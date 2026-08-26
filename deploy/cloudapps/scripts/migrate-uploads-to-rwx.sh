#!/usr/bin/env bash
set -euo pipefail

# One-time migration: swap the ${APP_NAME}-uploads PVC from ReadWriteOnce to
# ReadWriteMany so the backend Deployment can use a RollingUpdate strategy
# (a surge pod mounting a ReadWriteOnce volume while the old pod still holds
# it fails with a Multi-Attach error - see deploy/cloudapps/README.md).
#
# accessModes is immutable on an existing PVC, so this can't be a plain
# `oc apply` of the updated template: it backs up the (small) uploads
# directory, deletes the old PVC, recreates it as ReadWriteMany, and
# restores the data. This takes the backend offline for the duration of the
# swap (typically well under a minute for a small uploads directory) - run
# it in a maintenance window, not as part of a routine deploy.
#
# Run once, before applying a template.yaml that sets the uploads PVC to
# ReadWriteMany. After this completes, run apply-environment.sh to pick up
# the RollingUpdate strategy change on the backend Deployment.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ENV_NAME="${1:-}"
load_environment "$ENV_NAME" "$0"
require_oc
select_project

PVC_NAME="${APP_NAME}-uploads"
DEPLOYMENT_NAME="${APP_NAME}-backend"
BACKUP_DIR="$(mktemp -d)"
trap 'rm -rf "$BACKUP_DIR"' EXIT

echo "== ${APP_NAME}-uploads: ReadWriteOnce -> ReadWriteMany migration =="
echo "Project:      ${OPENSHIFT_PROJECT}"
echo "PVC:          ${PVC_NAME} (size: ${UPLOAD_STORAGE_SIZE})"
echo "Local backup: ${BACKUP_DIR}"
echo
echo "This will scale ${DEPLOYMENT_NAME} to 0 replicas and delete/recreate"
echo "${PVC_NAME}. The backend will be unavailable for the duration."
echo
read -r -p "Type 'yes' to proceed: " confirm
if [[ "$confirm" != "yes" ]]; then
  echo "Aborted."
  exit 1
fi

existing_phase="$(oc get pvc "$PVC_NAME" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
if [[ -z "$existing_phase" ]]; then
  echo "PVC ${PVC_NAME} not found; nothing to migrate." >&2
  exit 1
fi

current_access_modes="$(oc get pvc "$PVC_NAME" -o jsonpath='{.spec.accessModes[*]}' 2>/dev/null || true)"
if [[ "$current_access_modes" == "ReadWriteMany" ]]; then
  echo "PVC ${PVC_NAME} is already ReadWriteMany. Nothing to do."
  exit 0
fi

echo
echo "-- Backing up current uploads data --"
backup_pod="$(wait_for_pod_running "app=${APP_NAME}-backend")"
if oc exec "$backup_pod" -- sh -c 'command -v tar >/dev/null'; then
  oc cp "${OPENSHIFT_PROJECT}/${backup_pod}:/app/uploads" "$BACKUP_DIR/uploads"
else
  echo "tar not found in ${backup_pod}; cannot back up via oc cp." >&2
  exit 1
fi
backup_size="$(du -sh "$BACKUP_DIR/uploads" 2>/dev/null | cut -f1)"
echo "Backed up ${backup_size:-unknown size} to ${BACKUP_DIR}/uploads"

echo
echo "-- Scaling ${DEPLOYMENT_NAME} to 0 (releases the PVC) --"
oc scale "deployment/${DEPLOYMENT_NAME}" --replicas=0
oc wait --for=delete "pod/${backup_pod}" --timeout=120s 2>/dev/null || true
# Recreate strategy pods can take a moment to fully terminate after scale-down.
for _ in {1..30}; do
  remaining="$(oc get pods -l "app=${APP_NAME}-backend" --field-selector=status.phase=Running -o name 2>/dev/null | wc -l)"
  [[ "$remaining" -eq 0 ]] && break
  sleep 2
done

echo
echo "-- Deleting old ReadWriteOnce PVC --"
oc delete pvc "$PVC_NAME" --wait=true

echo
echo "-- Creating new ReadWriteMany PVC --"
cat <<EOF | oc apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ${PVC_NAME}
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: ${UPLOAD_STORAGE_SIZE}
EOF

for _ in {1..30}; do
  phase="$(oc get pvc "$PVC_NAME" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  [[ "$phase" == "Bound" ]] && break
  sleep 2
done
if [[ "$phase" != "Bound" ]]; then
  echo "PVC ${PVC_NAME} did not reach Bound in time (phase: ${phase:-unknown})." >&2
  echo "Uploads backup is preserved at ${BACKUP_DIR}/uploads - inspect before retrying." >&2
  exit 1
fi
echo "PVC ${PVC_NAME} is Bound (ReadWriteMany)."

echo
echo "-- Scaling ${DEPLOYMENT_NAME} back to 1 --"
oc scale "deployment/${DEPLOYMENT_NAME}" --replicas=1
restore_pod="$(wait_for_pod_running "app=${APP_NAME}-backend")"

echo
echo "-- Restoring uploads data --"
oc cp "$BACKUP_DIR/uploads/." "${OPENSHIFT_PROJECT}/${restore_pod}:/app/uploads"
echo "Restored $(oc exec "$restore_pod" -- du -sh /app/uploads 2>/dev/null | cut -f1) into ${restore_pod}:/app/uploads"

echo
echo "Migration complete. ${PVC_NAME} is now ReadWriteMany."
echo "Next: apply the updated template.yaml (RollingUpdate strategy for"
echo "${DEPLOYMENT_NAME}) with apply-environment.sh so future deploys use it."
