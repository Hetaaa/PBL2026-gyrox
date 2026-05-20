#!/bin/bash
# Stop Zenoh Router on Robot

set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="${WORKSPACE_DIR}/.logs/zenoh"
PID_FILE="${LOG_DIR}/zenoh_router.pid"

if [[ ! -f "${PID_FILE}" ]]; then
    echo "Zenoh router not running (no pid file)"
    exit 0
fi

pid="$(cat "${PID_FILE}")"
if ps -p "${pid}" >/dev/null 2>&1; then
    kill "${pid}"
    sleep 1
    if ps -p "${pid}" >/dev/null 2>&1; then
        kill -9 "${pid}" || true
    fi
    echo "✅ Zenoh router stopped (PID: ${pid})"
else
    echo "⚠️  Stale PID file removed (${pid})"
fi

rm -f "${PID_FILE}"
