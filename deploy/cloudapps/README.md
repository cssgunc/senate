# CloudApps Deployment

This directory configures a single UNC CloudApps/OKD environment in the
`calebhan` project: `senate`

Each environment gets its own SQL Server deployment, database name, SQL Server
PVC, uploads PVC, backend, frontend, services, routes, image streams, build
configs, and OpenShift secret.

Secrets are not stored in git. The helper scripts create/update OpenShift
secrets directly and preserve existing generated values on reruns.

## GitHub CD

GitHub Actions handles CI in [/.github/workflows/ci.yml](../../.github/workflows/ci.yml)
and deployment in [/.github/workflows/deploy.yml](../../.github/workflows/deploy.yml).

This repository currently prioritizes dev only. The deployment workflow does
not log into OpenShift. Instead, it posts a JSON payload to OKD generic webhook
URLs stored in GitHub Secrets. OKD then clones the repo with its own SSH deploy
key, builds the backend and frontend images, and rolls the deployments when the
image streams change.

### Secret locations

GitHub Secrets:

- `OKD_BACKEND_WEBHOOK_URL`
- `OKD_FRONTEND_WEBHOOK_URL`

OpenShift secrets:

- `${APP_NAME}-git-source` - SSH private key used by OKD to clone the GitHub repo
- `${APP_NAME}-generic-webhook` - token used by the generic webhook trigger
- `${APP_NAME}-secrets` - runtime app config, database password, JWT secret, SMTP credentials

### Bootstrap once from a VPN-connected machine

You only need local `oc login` for the one-time bootstrap. Run the command from
the CloudApps console on a machine that can reach CloudApps, then bootstrap each
environment:

```bash
deploy/cloudapps/scripts/bootstrap-webhook.sh
```

The bootstrap script:

1. Generates an ed25519 SSH deploy key if needed.
2. Creates the OKD SSH auth secret and links it to the builder service account.
3. Generates the generic webhook token secret in OpenShift.
4. Applies the unauthenticated webhook RBAC binding.
5. Applies the CloudApps resources without starting local builds.
6. Prints the public SSH key to add to GitHub as a read-only deploy key.
7. Prints the backend and frontend webhook URLs to paste into GitHub Secrets.

The generated private key is stored under `deploy/cloudapps/secrets/`, which is
already ignored by git.

### Add the GitHub secrets

After the bootstrap script prints the webhook URLs, add them at
**Settings** → **Secrets and variables** → **Actions**:

1. Add `OKD_BACKEND_WEBHOOK_URL` and `OKD_FRONTEND_WEBHOOK_URL`.
2. If you want to protect the deploy button, configure a GitHub `dev`
   environment with reviewers and scoped secrets.

Then add the public SSH key shown by the bootstrap script to
**Repository Settings** → **Deploy keys** → **Add deploy key**.

### How deployment works

- CI runs in GitHub on pushes and pull requests through `ci.yml`.
- When CI succeeds on `main`, `deploy.yml` runs on a GitHub-hosted runner.
- The workflow sends the commit SHA and branch name to the backend and frontend
  OKD webhook URLs.
- OKD receives the anonymous webhook POST because `webhook-rbac.yaml` grants
  `system:unauthenticated` access to the webhook trigger.
- OKD clones the repo with the deploy key, builds the backend and frontend
  images, and updates the image streams.
- The image stream trigger on the Deployments rolls out the new pods.

### Storage and quota warning

The default CloudApps project name in this repo is still `calebhan` for both
environments. That means dev and prod share the same namespace quota unless you
change `OPENSHIFT_PROJECT` in one of the parameter files.

With the default 5Gi project quota, dev already uses the full 4Gi + 1Gi PVC
budget. Prod therefore needs either:

1. Its own separate OpenShift project with its own quota, or
2. A larger project quota than the combined storage requested by both envs.

The prod PVC sizes have been reduced to 4Gi and 1Gi so they stay under the
per-PVC limit. They will still fail in the same project until prod gets its own
namespace or quota increase.

### First deploy and database initialization

After the first webhook-triggered deploy completes, run the database and admin
bootstrap locally once:

```bash
deploy/cloudapps/scripts/init-db.sh dev
deploy/cloudapps/scripts/bootstrap-admin.sh dev
```

## Verify

```bash
oc get pods
oc get pvc
oc get routes
curl "https://senate-backend-calebhan.apps.unc.edu/health"
curl "https://senate-backend-calebhan.apps.unc.edu/health/db"
```

If SQL Server reports volume permission errors, check whether your CloudApps
project requires a particular storage class or supplemental group setting for
database containers.
