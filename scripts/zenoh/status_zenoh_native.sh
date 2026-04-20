#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PID_FILE="${WORKSPACE_DIR}/.logs/zenoh/zenoh_bridge.pid"
LOG_FILE="${WORKSPACE_DIR}/.logs/zenoh/zenoh_bridge.log"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "Zenoh bridge status: stopped"
  exit 0
fi

pid="$(cat "${PID_FILE}")"
if ps -p "${pid}" >/dev/null 2>&1; then
  echo "Zenoh bridge status: running (pid ${pid})"
  if [[ -f "${LOG_FILE}" ]]; then
    echo "Last log lines:"
    tail -n 20 "${LOG_FILE}" || true
  fi
else
  echo "Zenoh bridge status: stopped (stale pid ${pid})"
fi
