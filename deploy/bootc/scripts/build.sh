#!/usr/bin/env bash
# =============================================================================
# build.sh - Build the industrial-datagen bootc container image
# =============================================================================
set -euo pipefail

VERSION="${1:-latest}"
IMAGE="localhost/indgen-bootc:${VERSION}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo " industrial-datagen bootc image build"
echo " Image : ${IMAGE}"
echo "============================================"

if [[ ! -d "${PROJECT_DIR}/indgen-src/static" ]] || [[ ! -d "${PROJECT_DIR}/indgen-src/backend/app" ]]; then
  echo "ERROR: Source files not found. Run './scripts/prepare-src.sh' first."
  exit 1
fi

podman build \
  --tag "${IMAGE}" \
  --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --label "org.opencontainers.image.version=${VERSION}" \
  "${PROJECT_DIR}"

echo ""
echo "Build complete: ${IMAGE}"
echo "Next: ./scripts/convert-to-qcow2.sh ${VERSION}"
