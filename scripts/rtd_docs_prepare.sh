#!/usr/bin/env bash
set -euo pipefail

# Unless this is a stable or tagged build, use dev mode to grab unreleased changes
echo "READTHEDOCS=${READTHEDOCS:-}"
echo "READTHEDOCS_VERSION=${READTHEDOCS_VERSION:-}"
echo "READTHEDOCS_VERSION_TYPE=${READTHEDOCS_VERSION_TYPE:-}"
echo "READTHEDOCS_GIT_IDENTIFIER=${READTHEDOCS_GIT_IDENTIFIER:-}"

MODE="dev"

if [ "${READTHEDOCS_VERSION_TYPE:-}" = "tag" ]; then
  MODE="release"
elif [ "${READTHEDOCS_VERSION:-}" = "stable" ]; then
  MODE="release"
elif [ "${READTHEDOCS_GIT_IDENTIFIER:-}" = "main" ]; then
  MODE="release"
fi

echo "Preparing docs changelog in mode: ${MODE}"

if [ "${MODE}" = "dev" ]; then
  python scripts/docs_prepare.py --mode dev --title "Unreleased"
else
  python scripts/docs_prepare.py --mode release
fi
