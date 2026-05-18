#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ENV_NAME="${1:-senate}"
KEY_PATH="${2:-}"
SECRET_NAME="${3:-github-deploy-key}"

# Allow calling with either: [env] <key-path> [secret-name]
# or: <key-path> [secret-name] (env defaults to 'senate')
if [[ -z "$KEY_PATH" ]]; then
  if [[ -n "$ENV_NAME" && -f "$ENV_NAME" ]]; then
    KEY_PATH="$ENV_NAME"
    ENV_NAME=senate
  fi
fi

load_environment "$ENV_NAME" "$0"
require_oc
select_project

if [[ -z "$KEY_PATH" || ! -f "$KEY_PATH" ]]; then
  echo "Private deploy key file is required." >&2
  echo "Usage: $0 [senate] <private-key-path> [secret-name]" >&2
  exit 2
fi

oc create secret generic "$SECRET_NAME" \
  --type=kubernetes.io/ssh-auth \
  --from-file=ssh-privatekey="$KEY_PATH" \
  --dry-run=client \
  -o yaml \
  | oc apply -f -

oc secrets link builder "$SECRET_NAME"

echo "Applied deploy key secret '$SECRET_NAME' in project '$OPENSHIFT_PROJECT'."
echo "Use it with: GIT_SOURCE_SECRET=$SECRET_NAME deploy/cloudapps/scripts/apply-environment.sh $ENV_NAME"
