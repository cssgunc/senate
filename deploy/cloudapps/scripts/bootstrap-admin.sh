#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ENV_NAME="${1:-}"
load_environment "$ENV_NAME" "$0"
require_oc
select_project

read_prompt() {
  local var_name="$1"
  local prompt="$2"
  local secret="${3:-0}"

  if [[ -n "${!var_name:-}" ]]; then
    return
  fi

  if [[ "$secret" == "1" ]]; then
    read -r -s -p "$prompt" "$var_name"
    echo
  else
    read -r -p "$prompt" "$var_name"
  fi
  export "$var_name"
}

read_prompt INITIAL_ADMIN_EMAIL "Initial admin email: "
read_prompt INITIAL_ADMIN_PID "Initial admin PID (9 digits): " 1
read_prompt INITIAL_ADMIN_FIRST_NAME "Initial admin first name: "
read_prompt INITIAL_ADMIN_LAST_NAME "Initial admin last name: "
INITIAL_ADMIN_ROLE="${INITIAL_ADMIN_ROLE:-admin}"

TEMP_SECRET="${APP_NAME}-initial-admin"

oc create secret generic "$TEMP_SECRET" \
  --from-literal=INITIAL_ADMIN_EMAIL="$INITIAL_ADMIN_EMAIL" \
  --from-literal=INITIAL_ADMIN_PID="$INITIAL_ADMIN_PID" \
  --from-literal=INITIAL_ADMIN_FIRST_NAME="$INITIAL_ADMIN_FIRST_NAME" \
  --from-literal=INITIAL_ADMIN_LAST_NAME="$INITIAL_ADMIN_LAST_NAME" \
  --from-literal=INITIAL_ADMIN_ROLE="$INITIAL_ADMIN_ROLE" \
  --dry-run=client \
  -o yaml \
  | oc apply -f -

cleanup() {
  oc set env "deployment/${APP_NAME}-backend" \
    INITIAL_ADMIN_EMAIL- INITIAL_ADMIN_PID- INITIAL_ADMIN_FIRST_NAME- \
    INITIAL_ADMIN_LAST_NAME- INITIAL_ADMIN_ROLE- >/dev/null 2>&1 || true
  oc delete secret "$TEMP_SECRET" --ignore-not-found >/dev/null 2>&1 || true
}
trap cleanup EXIT

oc set env "deployment/${APP_NAME}-backend" --from="secret/${TEMP_SECRET}"
oc rollout status "deployment/${APP_NAME}-backend" --timeout=60s || true

pod="$(wait_for_pod_running "app=${APP_NAME}-backend")"
oc exec "$pod" -- python -m script.init_db

echo "Initial admin bootstrap complete for ${APP_NAME}."
echo "Temporary bootstrap secret has been removed from OpenShift."
