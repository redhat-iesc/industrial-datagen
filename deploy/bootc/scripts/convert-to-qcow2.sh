#!/usr/bin/env bash
# =============================================================================
# convert-to-qcow2.sh - Convert bootc image to QCOW2 VM disk
# =============================================================================
set -euo pipefail

VERSION="${1:-latest}"
IMAGE="localhost/indgen-bootc:${VERSION}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${PROJECT_DIR}/output/qcow2-${VERSION}"

echo "============================================"
echo " Converting bootc image to QCOW2"
echo " Source : ${IMAGE}"
echo " Output : ${OUTPUT_DIR}/disk.qcow2"
echo "============================================"

if ! podman image exists "${IMAGE}"; then
  echo "ERROR: Image not found: ${IMAGE}"
  echo "       Run './scripts/build.sh ${VERSION}' first."
  exit 1
fi

mkdir -p "${OUTPUT_DIR}"

podman run \
  --rm \
  --privileged \
  --pull=newer \
  -v /var/lib/containers/storage:/var/lib/containers/storage \
  -v "${OUTPUT_DIR}:/output" \
  quay.io/centos-bootc/bootc-image-builder:latest \
  --type qcow2 \
  --local \
  "${IMAGE}"

echo ""
echo "QCOW2 image ready: ${OUTPUT_DIR}/disk.qcow2"
