#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ENV_NAME="${1:-senate}"
KEY_DIR="${2:-$CLOUDAPPS_DIR/secrets/${ENV_NAME:-}}"

load_environment "$ENV_NAME" "$0"
require_oc
select_project

if [[ -z "$KEY_DIR" ]]; then
  KEY_DIR="$CLOUDAPPS_DIR/secrets/$APP_NAME"
fi

mkdir -p "$KEY_DIR"

PRIVATE_KEY_PATH="$KEY_DIR/github-deploy-key"
PUBLIC_KEY_PATH="$PRIVATE_KEY_PATH.pub"
DEPLOY_SECRET_NAME="${APP_NAME}-git-source"
WEBHOOK_SECRET_NAME="${APP_NAME}-generic-webhook"

if [[ ! -f "$PRIVATE_KEY_PATH" ]]; then
  ssh-keygen -t ed25519 -N "" -C "${APP_NAME}-deploy-key" -f "$PRIVATE_KEY_PATH"
fi

"$SCRIPT_DIR/create-deploy-key-secret.sh" "$ENV_NAME" "$PRIVATE_KEY_PATH" "$DEPLOY_SECRET_NAME"

WEBHOOK_TOKEN="$(get_secret_value "$WEBHOOK_SECRET_NAME" WebHookSecretKey || true)"
if [[ -z "$WEBHOOK_TOKEN" ]]; then
  WEBHOOK_TOKEN="$(generate_webhook_secret)"
fi
oc create secret generic "$WEBHOOK_SECRET_NAME" \
  --from-literal=WebHookSecretKey="$WEBHOOK_TOKEN" \
  --dry-run=client \
  -o yaml \
  | oc apply -f -

oc apply -f "$CLOUDAPPS_DIR/manifests/webhook-rbac.yaml"

SKIP_BUILD=1 GIT_SOURCE_SECRET="$DEPLOY_SECRET_NAME" "$SCRIPT_DIR/apply-environment.sh" "$ENV_NAME"

SERVER_URL="$(oc whoami --show-server)"
BACKEND_WEBHOOK_URL="${SERVER_URL}/apis/build.openshift.io/v1/namespaces/${OPENSHIFT_PROJECT}/buildconfigs/${APP_NAME}-backend/webhooks/${WEBHOOK_TOKEN}/generic"
FRONTEND_WEBHOOK_URL="${SERVER_URL}/apis/build.openshift.io/v1/namespaces/${OPENSHIFT_PROJECT}/buildconfigs/${APP_NAME}-frontend/webhooks/${WEBHOOK_TOKEN}/generic"

echo ""
echo "GitHub deploy key public key:"
cat "$PUBLIC_KEY_PATH"
echo ""
echo "Add the public key above to GitHub as a read-only deploy key."
echo ""
  echo "Store these GitHub Actions secrets:"
  echo "  OKD_BACKEND_WEBHOOK_URL=$BACKEND_WEBHOOK_URL"
  echo "  OKD_FRONTEND_WEBHOOK_URL=$FRONTEND_WEBHOOK_URL"
echo ""
echo "Webhook secret secret name in OpenShift: $WEBHOOK_SECRET_NAME"
