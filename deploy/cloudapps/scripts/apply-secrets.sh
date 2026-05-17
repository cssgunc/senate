#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ENV_NAME="${1:-}"
load_environment "$ENV_NAME" "$0"
require_oc
select_project

SECRET_NAME="${APP_NAME}-secrets"

existing_mssql="$(get_secret_value "$SECRET_NAME" MSSQL_SA_PASSWORD)"
existing_jwt="$(get_secret_value "$SECRET_NAME" JWT_SECRET)"
existing_smtp_host="$(get_secret_value "$SECRET_NAME" SMTP_HOST)"
existing_smtp_port="$(get_secret_value "$SECRET_NAME" SMTP_PORT)"
existing_smtp_user="$(get_secret_value "$SECRET_NAME" SMTP_USER)"
existing_smtp_password="$(get_secret_value "$SECRET_NAME" SMTP_PASSWORD)"
existing_smtp_from="$(get_secret_value "$SECRET_NAME" SMTP_FROM)"

MSSQL_SA_PASSWORD="${MSSQL_SA_PASSWORD:-${existing_mssql:-$(generate_sql_password)}}"
JWT_SECRET="${JWT_SECRET:-${existing_jwt:-$(generate_jwt_secret)}}"
SMTP_HOST="${SMTP_HOST:-${existing_smtp_host:-}}"
SMTP_PORT="${SMTP_PORT:-${existing_smtp_port:-587}}"
SMTP_USER="${SMTP_USER:-${existing_smtp_user:-}}"
SMTP_PASSWORD="${SMTP_PASSWORD:-${existing_smtp_password:-}}"
SMTP_FROM="${SMTP_FROM:-${existing_smtp_from:-speaker@unc.edu}}"

oc create secret generic "$SECRET_NAME" \
  --from-literal=MSSQL_SA_PASSWORD="$MSSQL_SA_PASSWORD" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --from-literal=SMTP_HOST="$SMTP_HOST" \
  --from-literal=SMTP_PORT="$SMTP_PORT" \
  --from-literal=SMTP_USER="$SMTP_USER" \
  --from-literal=SMTP_PASSWORD="$SMTP_PASSWORD" \
  --from-literal=SMTP_FROM="$SMTP_FROM" \
  --dry-run=client \
  -o yaml \
  | oc apply -f -

echo "Applied OpenShift secret '$SECRET_NAME' in project '$OPENSHIFT_PROJECT'."
echo "Secret values were not written to the repository."
