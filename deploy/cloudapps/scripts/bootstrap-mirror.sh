#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ENV_NAME="${1:-senate}"
load_environment "$ENV_NAME" "$0"
require_oc
select_project

KEY_DIR="$CLOUDAPPS_DIR/secrets/$APP_NAME"
mkdir -p "$KEY_DIR"

PRIVATE_KEY_PATH="$KEY_DIR/mirror-key"
PUBLIC_KEY_PATH="$PRIVATE_KEY_PATH.pub"
MIRROR_SECRET_NAME="${APP_NAME}-mirror-key"
GIT_HOST="$(echo "$GIT_REPO" | sed -E 's#^[^@]+@([^:/]+).*#\1#')"

if [[ ! -f "$PRIVATE_KEY_PATH" ]]; then
  ssh-keygen -t ed25519 -N "" -C "${APP_NAME}-mirror-key" -f "$PRIVATE_KEY_PATH"
fi

KNOWN_HOSTS="$(ssh-keyscan -t ed25519,rsa "$GIT_HOST" 2>/dev/null)"
if [[ -z "$KNOWN_HOSTS" ]]; then
  echo "Could not ssh-keyscan '$GIT_HOST'. Are you on the campus network/VPN?" >&2
  exit 1
fi

oc create secret generic "$MIRROR_SECRET_NAME" \
  --from-file=ssh-privatekey="$PRIVATE_KEY_PATH" \
  --from-literal=known_hosts="$KNOWN_HOSTS" \
  --dry-run=client \
  -o yaml \
  | oc apply -f -

echo ""
echo "Mirror deploy key public key (add as a WRITE-capable deploy key on $GIT_HOST):"
cat "$PUBLIC_KEY_PATH"
echo ""
echo "Applied secret '$MIRROR_SECRET_NAME' in project '$OPENSHIFT_PROJECT'."
echo "Run apply-environment.sh (or 'oc process ... | oc apply -f -') to (re)create the ${APP_NAME}-github-mirror CronJob so it can mount this secret."
