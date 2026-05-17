#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOUDAPPS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$CLOUDAPPS_DIR/../.." && pwd)"

usage_env() {
  echo "Usage: $1 <dev|prod>" >&2
  exit 2
}

require_oc() {
  if ! command -v oc >/dev/null 2>&1; then
    echo "The OpenShift CLI 'oc' is not installed or not on PATH." >&2
    echo "Install it, connect to UNC VPN/campus if needed, then run 'oc login'." >&2
    exit 1
  fi
}

load_environment() {
  local env_name="${1:-}"
  if [[ "$env_name" != "dev" && "$env_name" != "prod" ]]; then
    usage_env "${2:-$0}"
  fi

  PARAM_FILE="$CLOUDAPPS_DIR/params/${env_name}.env"
  if [[ ! -f "$PARAM_FILE" ]]; then
    echo "Missing parameter file: $PARAM_FILE" >&2
    exit 1
  fi

  set -a
  # shellcheck disable=SC1090
  source "$PARAM_FILE"
  set +a

  if [[ -z "${APP_NAME:-}" || -z "${OPENSHIFT_PROJECT:-}" ]]; then
    echo "APP_NAME and OPENSHIFT_PROJECT are required in $PARAM_FILE" >&2
    exit 1
  fi
}

select_project() {
  oc project "$OPENSHIFT_PROJECT" >/dev/null
}

generate_sql_password() {
  python3 - <<'PY'
import secrets
print("A1!" + secrets.token_urlsafe(29))
PY
}

generate_jwt_secret() {
  python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
}

get_secret_value() {
  local secret_name="$1"
  local key="$2"
  local encoded

  encoded="$(oc get secret "$secret_name" -o "jsonpath={.data.${key}}" 2>/dev/null || true)"
  if [[ -n "$encoded" ]]; then
    printf "%s" "$encoded" | base64 -d 2>/dev/null || true
  fi
}

wait_for_pod_running() {
  local selector="$1"
  local pod=""

  for _ in {1..60}; do
    pod="$(oc get pods -l "$selector" \
      -o jsonpath='{range .items[?(@.status.phase=="Running")]}{.metadata.name}{"\n"}{end}' \
      2>/dev/null | head -n 1)"
    if [[ -n "$pod" ]]; then
      echo "$pod"
      return 0
    fi
    sleep 2
  done

  echo "Timed out waiting for pod with selector '$selector' to be Running" >&2
  exit 1
}
