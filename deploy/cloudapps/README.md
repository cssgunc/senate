# CloudApps Deployment

This directory configures two independent UNC CloudApps/OKD environments in the
`calebhan` project:

- `senate-dev`
- `senate-prod`

Each environment gets its own SQL Server deployment, database name, SQL Server
PVC, uploads PVC, backend, frontend, services, routes, image streams, build
configs, and OpenShift secret.

Secrets are not stored in git. The helper scripts create/update OpenShift
secrets directly and preserve existing generated values on reruns.

## GitHub CD

GitHub Actions handles CI in [/.github/workflows/ci.yml](../../.github/workflows/ci.yml)
and deployment in [/.github/workflows/deploy.yml](../../.github/workflows/deploy.yml).

The deploy workflow uses the existing OpenShift scripts so it stays aligned with
the current CloudApps setup:

- Pushes to `main` deploy `dev` automatically.
- Manual runs can target `dev` or `prod`.
- OpenShift remains the source of truth for runtime secrets once they exist.

Required GitHub secrets:

- `OC_SERVER`
- `OC_TOKEN`

Optional secret:

- `GIT_SOURCE_SECRET` if OpenShift needs a deploy key for the GitHub repo

If you want GitHub environment protection for production, configure the `prod`
environment in GitHub with reviewers and scoped secrets. The workflow already
labels jobs with `dev` or `prod` so that setup can be added without changing the
pipeline.

## First-Time GitHub Actions Dev Deploy

### Step 1: Get OpenShift Credentials from CloudApps

1. Open the UNC CloudApps console: https://cloudapps.unc.edu/
2. Log in with your UNC credentials.
3. Click your username in the top-right corner.
4. Select **Copy Login Command**.
5. You'll see a command like:
   ```
   oc login https://api.cloudapps.unc.edu:6443 --token=XXXXX
   ```
   The token expires after a period (typically hours), so generate a fresh one here each time you need it.
6. Save the server URL and token for the next step. They are:
   - `OC_SERVER`: the full URL like `https://api.cloudapps.unc.edu:6443`
   - `OC_TOKEN`: the token string like `sha256~XXXXX`

### Step 2: Add Secrets to GitHub

1. Go to your GitHub repository: https://github.com/cssgunc/senate
2. Click **Settings** (top-right menu).
3. On the left sidebar, click **Secrets and variables** → **Actions**.
4. Click **New repository secret**.
5. Add `OC_SERVER`:
   - Name: `OC_SERVER`
   - Secret: paste the full server URL from Step 1 (e.g., `https://api.cloudapps.unc.edu:6443`)
   - Click **Add secret**.
6. Click **New repository secret** again.
7. Add `OC_TOKEN`:
   - Name: `OC_TOKEN`
   - Secret: paste the token string from Step 1 (e.g., `sha256~XXXXX`)
   - Click **Add secret**.
8. If the GitHub repo is private, also add `GIT_SOURCE_SECRET`:
   - Name: `GIT_SOURCE_SECRET`
   - Secret: `github-deploy-key` (or whatever you named it in OpenShift)
   - (You only need this if you've already created a deploy key secret in OpenShift.)

### Step 3: Verify Dev Environment Parameters

Check [params/dev.env](params/dev.env). It should have:

```
APP_NAME=senate-dev
OPENSHIFT_PROJECT=calebhan
GIT_REPO=git@github.com:cssgunc/senate.git
GIT_REF=main
RUNTIME_ENVIRONMENT=development
FRONTEND_HOST=senate-dev-frontend-calebhan.apps.unc.edu
BACKEND_HOST=senate-dev-backend-calebhan.apps.unc.edu
NEXT_PUBLIC_API_URL=https://senate-dev-backend-calebhan.apps.unc.edu
CORS_ORIGINS=https://senate-dev-frontend-calebhan.apps.unc.edu
DB_NAME=senate_dev
DB_STORAGE_SIZE=4Gi
UPLOAD_STORAGE_SIZE=1Gi
MSSQL_MEMORY_REQUEST=1Gi
MSSQL_MEMORY_LIMIT=2Gi
BACKEND_MEMORY_REQUEST=256Mi
BACKEND_MEMORY_LIMIT=512Mi
FRONTEND_MEMORY_REQUEST=256Mi
FRONTEND_MEMORY_LIMIT=512Mi
```

If CloudApps gave you different hostnames, update `FRONTEND_HOST`, `BACKEND_HOST`, `NEXT_PUBLIC_API_URL`, and `CORS_ORIGINS` here.

### Step 4: Trigger the Deploy

**Option A: Auto-deploy from main (recommended)**

Push a commit to `main`:

```bash
git checkout main
git push origin main
```

GitHub Actions will automatically run the Deploy workflow and deploy to `dev`.

**Option B: Manual dispatch**

1. Go to GitHub Actions: https://github.com/cssgunc/senate/actions
2. Click **Deploy** on the left (under Workflows).
3. Click **Run workflow**.
4. Select **dev** in the dropdown (default).
5. Click **Run workflow**.

### Step 5: Watch the Deploy

1. On the Actions tab, click the running **Deploy** job.
2. Watch the logs. Key milestones:
   - "Install OpenShift CLI" — GitHub is installing `oc`
   - "Log in to OpenShift" — GitHub is authenticating with your `OC_TOKEN`
   - "Apply environment" — The OpenShift template and builds are being applied
   - "oc start-build" — Builds are running (watch for Docker build output)
   - "Waiting briefly for deployments" — Pods are starting

If a step fails, read the error. Most common issues:

- Token expired: generate a fresh one from the CloudApps console and update the GitHub secret.
- "Project not found": confirm `OPENSHIFT_PROJECT=calebhan` and `OC_TOKEN` has access to it.
- "Build failed": check the backend or frontend Dockerfile, or look at the build logs in OpenShift.

### Step 6: Initialize the Database (First Time Only)

Once the Deploy job succeeds, the pods are running but the database is not yet initialized. Run this once:

```bash
oc project calebhan
deploy/cloudapps/scripts/init-db.sh dev
```

This connects to the running `senate-dev-backend` pod and runs `python -m script.init_db`, which creates the database and tables.

### Step 7: Create the First Admin User (First Time Only)

```bash
deploy/cloudapps/scripts/bootstrap-admin.sh dev
```

You'll be prompted for:

- **Initial admin email**: e.g., `admin@unc.edu`
- **Initial admin PID**: your 9-digit UNC PID
- **Initial admin first name**: your first name
- **Initial admin last name**: your last name

The script creates the admin user in the database, then cleans up the temporary secret.

### Step 8: Verify Dev is Running

Check the pods:

```bash
oc project calebhan
oc get pods -l app=senate-dev-backend
oc get pods -l app=senate-dev-frontend
oc get routes -l app=senate-dev-backend
```

You should see 3 pods running (backend, frontend, mssql). Check the health endpoints:

```bash
curl https://senate-dev-backend-calebhan.apps.unc.edu/health
curl https://senate-dev-backend-calebhan.apps.unc.edu/health/db
```

Both should return `{"status":"ok"}`. If the database health check fails, run Step 6 again.

Access the site:

- **Frontend**: https://senate-dev-frontend-calebhan.apps.unc.edu
- **Backend API**: https://senate-dev-backend-calebhan.apps.unc.edu/docs
- **Admin login**: use the email and PID from Step 7

## Prerequisites

Install `oc`, connect to UNC VPN or campus network if needed, then log in with
the command from the CloudApps console: user menu -> Copy Login Command ->
Display Token.

```bash
# Paste the generated oc login command here.
oc project calebhan
```

The scripts expect route hostnames under `apps.unc.edu`:

- Dev frontend: `https://senate-dev-frontend-calebhan.apps.unc.edu`
- Dev backend: `https://senate-dev-backend-calebhan.apps.unc.edu`
- Prod frontend: `https://senate-prod-frontend-calebhan.apps.unc.edu`
- Prod backend: `https://senate-prod-backend-calebhan.apps.unc.edu`

Edit [params/dev.env](params/dev.env) or [params/prod.env](params/prod.env) if
CloudApps gives you different hostnames.

## Private Git Repo

If the GitHub repo is private, create a deploy key secret in OpenShift. The key
file should stay local and is ignored by git.

```bash
deploy/cloudapps/scripts/create-deploy-key-secret.sh dev ./deploy_key github-deploy-key
deploy/cloudapps/scripts/create-deploy-key-secret.sh prod ./deploy_key github-deploy-key
```

Then pass that secret when applying either environment:

```bash
GIT_SOURCE_SECRET=github-deploy-key deploy/cloudapps/scripts/apply-environment.sh dev
GIT_SOURCE_SECRET=github-deploy-key deploy/cloudapps/scripts/apply-environment.sh prod
```

If the repo is public, omit `GIT_SOURCE_SECRET`.

## Apply Environments

Development:

```bash
deploy/cloudapps/scripts/apply-environment.sh dev
deploy/cloudapps/scripts/init-db.sh dev
deploy/cloudapps/scripts/bootstrap-admin.sh dev
```

Production:

```bash
deploy/cloudapps/scripts/apply-environment.sh prod
deploy/cloudapps/scripts/init-db.sh prod
deploy/cloudapps/scripts/bootstrap-admin.sh prod
```

`init-db.sh` runs `python -m script.init_db`, which creates the database and
missing tables without dropping or reseeding data.

`bootstrap-admin.sh` prompts for the first admin account, stores those values in
a temporary OpenShift secret, runs the initializer, then removes the temporary
secret and env vars.

Do not run `python -m script.reset_dev` or `python -m script.seed_data` against
production. `reset_dev` drops tables, and `seed_data` clears application data.

## SMTP Secrets

To configure SMTP without writing credentials to disk, pass values as environment
variables when applying secrets:

```bash
SMTP_HOST="smtp.example.edu" \
SMTP_PORT="587" \
SMTP_USER="smtp-user" \
SMTP_PASSWORD="smtp-password" \
SMTP_FROM="speaker@unc.edu" \
deploy/cloudapps/scripts/apply-secrets.sh prod
```

Then restart the backend:

```bash
oc rollout restart deployment/senate-prod-backend
```

## Custom Production DNS Later

When the production custom DNS is ready:

1. Update [params/prod.env](params/prod.env):
   - `FRONTEND_HOST`
   - `BACKEND_HOST`
   - `NEXT_PUBLIC_API_URL`
   - `CORS_ORIGINS`
2. Reapply prod:

```bash
GIT_SOURCE_SECRET=github-deploy-key deploy/cloudapps/scripts/apply-environment.sh prod
deploy/cloudapps/scripts/init-db.sh prod
```

The frontend build bakes in `NEXT_PUBLIC_API_URL`, so production must be rebuilt
after changing the backend hostname.

## Verify

```bash
oc get pods
oc get pvc
oc get routes
curl "https://senate-dev-backend-calebhan.apps.unc.edu/health"
curl "https://senate-dev-backend-calebhan.apps.unc.edu/health/db"
curl "https://senate-prod-backend-calebhan.apps.unc.edu/health"
curl "https://senate-prod-backend-calebhan.apps.unc.edu/health/db"
```

If SQL Server reports volume permission errors, check whether your CloudApps
project requires a particular storage class or supplemental group setting for
database containers.
