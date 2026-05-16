#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ENV_NAME="${1:-}"
load_environment "$ENV_NAME" "$0"
require_oc
select_project

"$SCRIPT_DIR/apply-secrets.sh" "$ENV_NAME"

oc process -f "$CLOUDAPPS_DIR/template.yaml" --param-file "$PARAM_FILE" | oc apply -f -

if [[ -n "${GIT_SOURCE_SECRET:-}" ]]; then
  oc set build-secret --source "bc/${APP_NAME}-backend" "$GIT_SOURCE_SECRET"
  oc set build-secret --source "bc/${APP_NAME}-frontend" "$GIT_SOURCE_SECRET"
  echo "Attached Git source secret '$GIT_SOURCE_SECRET' to ${APP_NAME} BuildConfigs."
fi

if [[ "${SKIP_BUILD:-0}" == "1" ]]; then
  echo "Applied ${ENV_NAME} resources without starting builds because SKIP_BUILD=1."
  exit 0
fi

oc start-build "${APP_NAME}-backend" --follow
oc start-build "${APP_NAME}-frontend" --follow

oc rollout restart "deployment/${APP_NAME}-backend"
oc rollout restart "deployment/${APP_NAME}-frontend"

echo "Waiting briefly for ${APP_NAME} deployments. The backend may remain unready until init-db runs."
oc rollout status "deployment/${APP_NAME}-frontend" --timeout=180s
oc rollout status "deployment/${APP_NAME}-backend" --timeout=60s || true

echo "Applied ${ENV_NAME} environment:"
echo "  frontend: https://${FRONTEND_HOST}"
echo "  backend:  https://${BACKEND_HOST}"
