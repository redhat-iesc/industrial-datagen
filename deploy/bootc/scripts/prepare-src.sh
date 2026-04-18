#!/usr/bin/env bash
# =============================================================================
# prepare-src.sh - Build frontend and copy backend for bootc image build
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="${PROJECT_DIR}/../.."

echo "Building frontend..."
cd "${REPO_ROOT}/frontend"
npm ci
npm run build

echo "Copying artifacts..."
mkdir -p "${PROJECT_DIR}/indgen-src/static"
mkdir -p "${PROJECT_DIR}/indgen-src/backend"

cp -r "${REPO_ROOT}/frontend/dist/"* "${PROJECT_DIR}/indgen-src/static/"
cp -r "${REPO_ROOT}/backend/app" "${PROJECT_DIR}/indgen-src/backend/app"
cp "${REPO_ROOT}/backend/pyproject.toml" "${PROJECT_DIR}/indgen-src/backend/"

echo "Source prepared in ${PROJECT_DIR}/indgen-src/"
