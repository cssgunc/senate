# CloudApps Deployment

This directory configures a single UNC CloudApps/OKD environment in the
`dept-undergraduate-senate` project: `senate`

Each environment gets its own Postgres deployment, database name, DB PVC,
uploads PVC, backend, frontend, services, routes, image streams, build
configs, and OpenShift secrets.

Secrets are not stored in git. The helper scripts create/update OpenShift
secrets directly and preserve existing generated values on reruns.

## Source of truth and the sc.unc.edu mirror

GitHub (`cssgunc/senate`) is canonical for development: PRs, CI, branch
protection all happen there. OKD's BuildConfigs pull source from the
department's campus Git service instead of GitHub directly
(`https://sc.unc.edu/dept-undergraduate-senate`), because that's the git
host CloudApps is meant to build from for department-owned projects.

GitHub and sc.unc.edu are kept in sync by a **one-way mirror**, not
bidirectional sync — bidirectional mirroring risks silently clobbering
commits on whichever side last synced. The mirror direction only goes
GitHub `main` → sc.unc.edu `main`.

### Why a CronJob instead of a GitHub Action

The obvious design — a GitHub Action that pushes to sc.unc.edu on every
push to `main` — does not work. `sc.unc.edu` is only reachable from the
UNC campus network/VPN, and GitHub-hosted Actions runners live on the
public internet, so the push always times out (`Connection timed out` on
port 22). A self-hosted Actions runner on campus would fix that but adds a
persistent process someone has to maintain.

sc.unc.edu's own GitLab-style mirroring only supports **push** mirrors
(push mirroring requires a paid tier we don't have), and push mirrors send
sc.unc.edu's content *out*, which is the wrong direction for what we need.

Instead, `template.yaml` defines a Kubernetes `CronJob`
(`senate-github-mirror`) that runs *inside* `dept-undergraduate-senate`
every 10 minutes. That project's pods already sit on campus-network
infrastructure, so they can reach sc.unc.edu fine. Each run does an
anonymous `git clone` of the public GitHub repo (no GitHub auth needed —
it's a public repo) and pushes `main` to sc.unc.edu with a dedicated,
write-scoped deploy key.

Bootstrap it with:

```bash
deploy/cloudapps/scripts/bootstrap-mirror.sh senate
```

This creates/reuses an ed25519 keypair under `deploy/cloudapps/secrets/senate/`
(git-ignored) and stores it as the `${APP_NAME}-mirror-key` OpenShift
secret. Add the printed public key to the sc.unc.edu repo as a
**write-capable** deploy key (Settings → Repository → Deploy Keys, check
the write-access box — some GitLab-style UIs only show that option when
you first create the key, so delete and re-add if you can't find it after
the fact).

### When maintainership transfers

Once GitHub is no longer maintained by whoever has push access today,
flip the source of truth: disable/delete the `senate-github-mirror`
CronJob and start pushing directly to sc.unc.edu (which already has full
history from the mirror). Update `GIT_REPO` in `params/senate.env` if the
clone URL changes.

## GitHub CI/CD

GitHub Actions handles CI in [/.github/workflows/ci.yml](../../.github/workflows/ci.yml)
and deployment in [/.github/workflows/deploy.yml](../../.github/workflows/deploy.yml).

The deployment workflow does not log into OpenShift. Instead, it posts a
JSON payload to OKD generic webhook URLs stored in GitHub Secrets. OKD then
clones the repo from sc.unc.edu with its own SSH deploy key, builds the
backend and frontend images, and rolls the deployments when the image
streams change. The mirror CronJob above is what keeps sc.unc.edu current
enough for this to pick up recent commits (with up to ~10 minutes of lag).

### Secret locations

GitHub Secrets:

- `OKD_BACKEND_WEBHOOK_URL`
- `OKD_FRONTEND_WEBHOOK_URL`

OpenShift secrets:

- `${APP_NAME}-git-source` - SSH private key OKD uses to clone from sc.unc.edu (read-only)
- `${APP_NAME}-mirror-key` - SSH private key the mirror CronJob uses to push to sc.unc.edu (write-capable)
- `${APP_NAME}-generic-webhook` - token used by the generic webhook trigger
- `${APP_NAME}-secrets` - runtime app config: DB password, JWT secret, SMTP credentials

### Bootstrap once from a VPN-connected machine

You only need local `oc login` for the one-time bootstrap. Run the command
from the CloudApps console on a machine that can reach CloudApps, then
bootstrap each environment:

```bash
deploy/cloudapps/scripts/bootstrap-webhook.sh senate
deploy/cloudapps/scripts/bootstrap-mirror.sh senate
```

`bootstrap-webhook.sh`:

1. Generates an ed25519 SSH deploy key if needed.
2. Creates the OKD SSH auth secret (read-only) and links it to the builder service account.
3. Generates the generic webhook token secret in OpenShift.
4. Applies the unauthenticated webhook RBAC binding.
5. Applies the CloudApps resources without starting local builds.
6. Prints the public SSH key to add to sc.unc.edu as a **read-only** deploy key.
7. Prints the backend and frontend webhook URLs to paste into GitHub Secrets.

`bootstrap-mirror.sh` does the equivalent for the write-capable mirror key
(see "Why a CronJob instead of a GitHub Action" above).

### Add the GitHub secrets

After the bootstrap script prints the webhook URLs, add them at
**Settings** → **Secrets and variables** → **Actions**:

- `OKD_BACKEND_WEBHOOK_URL` and `OKD_FRONTEND_WEBHOOK_URL`.

## Custom hostnames (senate.unc.edu) and the route "permission" gotcha

`FRONTEND_HOST=senate.unc.edu` in `params/senate.env` is a **custom
hostname**, not one of the auto-generated `*.apps.cloudapps.unc.edu` ones.
OpenShift gates *claiming a brand-new, currently-unclaimed custom hostname*
behind a `routes/custom-host` permission that this project does not have
by default — only specific projects get it granted (however UNC IT
provisions that; ask them the way you'd ask for anything else CloudApps-side).

This has a sharp edge: if you delete the existing `senate-frontend` Route
that holds `senate.unc.edu` before a replacement exists, the host becomes
briefly *unclaimed*, and creating a new Route object with that host then
requires the permission — which will fail with `you do not have permission
to set the host field of the route` if the project doesn't have it. This
is an outage: the host has no working Route until you either get the
permission or move it back.

**Safe way to move `senate.unc.edu` between projects without that
permission**: OpenShift does *not* gate creating a new Route object whose
host is already claimed and admitted by an *older* Route somewhere else —
it just sits there `Admitted: False` / `HostAlreadyClaimed` until the
older one goes away, at which point the router promotes it automatically
(observed to happen in well under a second). So the sequence that works
without the special permission is:

1. Create the new Route (e.g. via `oc create route edge ... --hostname=senate.unc.edu`,
   *not* `oc apply`/`oc process` if a same-named Route already exists in
   the target project pointing at the temporary hostname — updating an
   *existing* Route object's `spec.host` to a custom value hits the
   permission check even when a brand-new Route object with the same host
   wouldn't. Delete-then-recreate the Route object if you're changing an
   already-applied one.) while the old Route still exists. It'll sit
   pending/unclaimed — this is not disruptive.
2. Confirm the new Route was actually created and shows `HostAlreadyClaimed`
   (not a permission error) before touching the old one.
3. Delete the old Route. The new one gets admitted automatically.
4. Verify: `curl -o /dev/null -w '%{http_code}\n' https://senate.unc.edu/`.

If step 1 itself fails with the permission error, the host is genuinely
unclaimed somewhere (or you're on a codepath that updates rather than
creates) — stop and get the `routes/custom-host` permission from UNC IT,
or recreate the old Route to restore service before investigating further.

## Storage and quota

`dept-undergraduate-senate` has its own project quota (2.5Gi memory limit,
5Gi storage, 10 pods, separate from `calebhan`'s). The frontend Deployment
uses `strategy: type: Recreate` (matching backend/db) rather than the
Kubernetes default `RollingUpdate` — with a tight memory quota,
`RollingUpdate` needs headroom to run old and new pods simultaneously
during rollout, which this project's quota often doesn't have. `Recreate`
avoids that by stopping the old pod before starting the new one.

## First deploy and database initialization

After the first webhook-triggered deploy completes, run the database and
admin bootstrap locally once:

```bash
deploy/cloudapps/scripts/init-db.sh senate
deploy/cloudapps/scripts/bootstrap-admin.sh senate
```

(Not needed if you're migrating data from an existing environment via
`pg_dump`/`pg_restore` instead — see the migration history for that
procedure.)

## Verify

```bash
oc get pods -n dept-undergraduate-senate
oc get pvc -n dept-undergraduate-senate
oc get routes -n dept-undergraduate-senate
curl "https://senate-backend-dept-undergraduate-senate.apps.cloudapps.unc.edu/health"
curl "https://senate-backend-dept-undergraduate-senate.apps.cloudapps.unc.edu/health/db"
curl "https://senate.unc.edu/"
```

If Postgres reports volume permission errors, check whether your
CloudApps project requires a particular storage class or supplemental
group setting for database containers.
