#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() {
  bash "${WORKSPACE_DIR}/scripts/zenoh/stop_zenoh_native.sh" || true
}

trap cleanup EXIT INT TERM

bash "${WORKSPACE_DIR}/scripts/zenoh/start_zenoh_native.sh"
exec bash "${WORKSPACE_DIR}/scripts/run_native.sh" "$@"
