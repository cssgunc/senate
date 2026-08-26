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

**The same CronJob run also triggers the OKD build**, immediately after a
push that actually moved `main` (a no-op push, when there's nothing new,
skips this). It does so by `curl`-ing the OKD generic webhook URLs itself
from inside the job, using the `${APP_NAME}-generic-webhook` token. This
is deliberate: earlier this triggered from `deploy.yml` on GitHub instead,
right after CI passed, but that raced the mirror — the webhook could fire
before the CronJob had synced that commit to sc.unc.edu yet, so OKD tried
to build a commit sc.unc.edu didn't have and failed with
`FetchSourceFailed`, with nothing to retry it once the mirror caught up.
Having the mirror job trigger the build itself, in the same run, right
after the push it just made, makes the ordering impossible to race.

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

GitHub Actions handles CI in [/.github/workflows/ci.yml](../../.github/workflows/ci.yml).
[/.github/workflows/deploy.yml](../../.github/workflows/deploy.yml) is
**manual-only** (`workflow_dispatch`) — a fallback for forcing OKD to
rebuild whatever sc.unc.edu currently has, without waiting for the mirror
CronJob's next run. It is *not* wired to fire automatically on push/CI
anymore, for the FetchSourceFailed race reason explained above.

The normal path is: push to `main` on GitHub → next `senate-github-mirror`
CronJob run (within 10 minutes) mirrors it to sc.unc.edu and triggers the
OKD build itself → OKD clones from sc.unc.edu with its read-only deploy
key, builds the backend and frontend images, and pushes them to the
`${APP_NAME}-backend`/`${APP_NAME}-frontend` ImageStreams.

The backend and frontend Deployments carry an
`image.openshift.io/triggers` annotation pointing at those
ImageStreamTags, which is what actually rolls the Deployment once a new
image lands — a plain `apps/v1` Deployment has no built-in equivalent of
DeploymentConfig's image trigger, and a Deployment's pod template
referencing `...:latest` does *not* restart on its own just because the
tag's underlying digest changed. Without this annotation, builds succeed
but the running pods keep serving the old image indefinitely. Verify it's
present with `oc get deployment ${APP_NAME}-backend -o jsonpath='{.metadata.annotations}'`
if a deploy ever silently doesn't show up.

The mirror CronJob's own webhook call (`curl`/`wget` from inside the pod)
uses `wget`, not `curl` — `alpine/git` doesn't ship `curl`, and installing
it at runtime with `apk add` fails under this project's restricted SCC
(the container runs as an arbitrary non-root UID with no write access to
`/etc/apk`). BusyBox's `wget` is already built into the base image and
needs no install.

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
5Gi storage, 10 pods, separate from `calebhan`'s) — a hard `ResourceQuota`
object only UNC IT can raise, the same as the `routes/custom-host`
permission described above. Storage is maxed outright: `requests.storage`
is 5Gi/5Gi (DB's 4Gi + uploads' 1Gi), so no new PVC — of any size — can be
created without freeing space first.

The `db` Deployment uses `strategy: type: Recreate`: it's a single-writer
stateful workload with a ReadWriteOnce PVC, so there's no meaningful way
to run two Postgres instances against the same data directory during a
rollout anyway — `Recreate` is the correct choice here, not a compromise.

The `backend` and `frontend` Deployments both use `RollingUpdate`
(`maxSurge: 1, maxUnavailable: 0`): the old pod keeps serving until the
new one passes its readiness probe, so a deploy has no window with zero
pods up. At the *original* `BACKEND_MEMORY_LIMIT`/`FRONTEND_MEMORY_LIMIT`
(512Mi/1Gi), a frontend surge pod didn't fit the quota at all (2Gi
steady-state + a 1Gi surge blows past the 2560Mi hard cap) — the honest
fix there would have been asking UNC IT for more quota, with no control
over the timeline.

Live usage checked with `oc adm top pods` told a different story, though:
actual memory use was ~85Mi for backend and ~94Mi for the DB against
512Mi limits each, and ~550Mi for frontend against its 1Gi limit — a lot
of committed-but-unused headroom. `BACKEND_MEMORY_LIMIT` was trimmed to
256Mi (still ~3x its measured usage) and `FRONTEND_MEMORY_LIMIT` to 896Mi
(~1.6x its measured peak), which frees just enough quota room for a
frontend surge pod to fit too, with **zero UNC IT dependency**:

```
steady-state:      512(db) + 256(backend) + 896(frontend) = 1664Mi
either surge pod:              + up to 896Mi              = 2560Mi  (exact cap)
```

`db`'s limit was deliberately left untouched even though it shows the
same slack — Postgres OOM-kills are a worse failure mode than a slow web
process (unclean termination mid-write, `Recreate` restart, connection
storm on recovery), so it isn't a lever to reach for casually.

This still leaves **zero slack** in the quota, with two consequences to
know about, neither of which causes an outage (both strategies keep
`maxUnavailable: 0`) but both of which can make a rollout stall:

- A stray pod needing memory during a deploy (`oc debug`, etc.) will hold
  up a surge pod in `Pending` until it clears.
- If a single commit changes both frontend and backend, their rollouts
  can overlap (the mirror CronJob triggers both BuildConfig webhooks
  back-to-back, and each Deployment rolls independently once its own
  image lands) and together need more than the 2560Mi available at once.
  Whichever surge pod loses the race just waits — `Pending` — until the
  other rollout finishes and releases its extra memory, then proceeds.

These numbers are a single live snapshot at low traffic, not a load test.
If `oc adm top pods` after a period of real traffic shows frontend
consistently closer to 896Mi than the ~550Mi seen here, that limit (or a
UNC IT quota increase) needs revisiting before it starts causing stalled
rollouts or OOM kills.

Both Deployments also set a `startupProbe` (polling every 2s, generous
`failureThreshold`) so a fast container start isn't hidden behind a flat
`initialDelaySeconds`, and a `preStop` hook (`sleep 5`) so the
Service/Route has time to stop routing to a pod before it receives
SIGTERM — general hardening independent of which rollout strategy is used.

### Zero-downtime backend deploys and the uploads PVC

`RollingUpdate` only works if the surge pod can actually start alongside
the old one. The `${APP_NAME}-uploads` PVC was `ReadWriteOnce`, and this
caused a real outage: during a backend rollout, the node hosting the new
pod hit `DiskPressure`, and while Kubernetes retried scheduling it
elsewhere, several attempts failed with `FailedAttachVolume: Multi-Attach
error ... already exclusively attached to one node` — the new pod
couldn't mount the same volume the old (still-terminating) pod held. That
combined with `Recreate` (no old pod left to fall back to) turned a
transient node problem into extended downtime, and left ~29 pods stuck in
`ContainerStatusUnknown` that had to be force-deleted afterward.

The fix is `ReadWriteMany`, which the backing `ontap-nas-economy`
(NetApp Trident NFS) storage class supports. `accessModes` is immutable on
an existing bound PVC, so this isn't a plain template change — run
`deploy/cloudapps/scripts/migrate-uploads-to-rwx.sh senate` once, which
backs up the uploads directory, deletes and recreates the PVC as RWX, and
restores the data. It takes the backend offline for the duration (seconds,
for the current ~5MB of uploads) and needs the same storage-quota headroom
problem kept in mind: deleting the old PVC first is what makes room for
the new one under the maxed-out 5Gi quota, so don't try to run it as a
create-alongside operation.

Run the migration script before applying a `template.yaml` that expects
`ReadWriteMany` — `apply-environment.sh` does a plain `oc apply`, which
will error on the PVC's immutable `accessModes` field if the live PVC is
still RWO.

### Schema changes and rolling deploys

`script/init_db.py` runs on every container start
(`python -m script.init_db && uvicorn ...`) and is deliberately
additive-only: it creates missing tables and adds missing nullable/
defaulted columns via `ALTER TABLE ... ADD COLUMN`, and silently skips any
`NOT NULL` column with no default (it can't backfill existing rows safely
on its own). It never drops or renames anything.

This happens to be exactly the right shape for zero-downtime rolling
deploys: during a `RollingUpdate`, the old pod (running the previous
commit's code) stays up and serving traffic while the new pod starts, so
briefly *both* code versions query the same database. Purely additive
changes are safe under that overlap — old code ignores columns/tables it
doesn't know about. Two things are not automatically safe, and need
manual handling regardless of rollout strategy:

- **Destructive or renaming changes** (drop/rename a column or table,
  change a column's type, add a `NOT NULL` column with no default): these
  need the standard expand/contract split across multiple deploys — add
  the new shape in one deploy, backfill, then remove the old shape in a
  later deploy once no running code references it anymore. Doing a rename
  in one shot will break the old pod for the duration of the rollout
  overlap.
- **A migration that gets silently skipped** (the `NOT NULL`-without-
  default case) doesn't fail the deploy — `init_db.py` logs and moves on,
  and the pod still passes its readiness probe (which only checks DB
  connectivity, not schema alignment). It'll surface as application
  errors on whatever code path touches that column, not as a stalled
  rollout. Check the `init_db` logs (`oc logs deploy/${APP_NAME}-backend`)
  after a deploy that adds a required column.

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
