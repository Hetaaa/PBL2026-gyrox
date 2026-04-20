#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PID_FILE="${WORKSPACE_DIR}/.logs/zenoh/zenoh_bridge.pid"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "Zenoh bridge is not running (no pid file)"
  exit 0
fi

pid="$(cat "${PID_FILE}")"
if ps -p "${pid}" >/dev/null 2>&1; then
  kill "${pid}"
  sleep 1
  if ps -p "${pid}" >/dev/null 2>&1; then
    kill -9 "${pid}" || true
  fi
  echo "Zenoh bridge stopped (pid ${pid})"
else
  echo "Stale pid file removed (${pid})"
fi

rm -f "${PID_FILE}"
