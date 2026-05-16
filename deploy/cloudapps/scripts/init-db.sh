#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ENV_NAME="${1:-}"
load_environment "$ENV_NAME" "$0"
require_oc
select_project

pod="$(wait_for_pod_running "app=${APP_NAME}-backend")"
oc exec "$pod" -- python -m script.init_db

echo "Database initialized for ${APP_NAME}."
