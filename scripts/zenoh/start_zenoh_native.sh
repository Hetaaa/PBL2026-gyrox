#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ZENOH_BIN="${ZENOH_BIN:-zenoh-bridge-ros2dds}"
ZENOH_CONFIG="${ZENOH_CONFIG:-${WORKSPACE_DIR}/scripts/zenoh/robot.json5}"
LOG_DIR="${WORKSPACE_DIR}/.logs/zenoh"
PID_FILE="${LOG_DIR}/zenoh_bridge.pid"
LOG_FILE="${LOG_DIR}/zenoh_bridge.log"

mkdir -p "${LOG_DIR}"

if ! command -v "${ZENOH_BIN}" >/dev/null 2>&1; then
  if [[ "${ZENOH_BIN}" == "zenoh-bridge-ros2dds" ]] && command -v zenoh-bridge-dds >/dev/null 2>&1; then
    ZENOH_BIN="zenoh-bridge-dds"
  fi
fi

if ! command -v "${ZENOH_BIN}" >/dev/null 2>&1; then
  echo "Missing binary: ${ZENOH_BIN}"
  echo "Run: bash setup/scripts/07_install_zenoh.sh"
  exit 1
fi

if [[ -f "${PID_FILE}" ]]; then
  old_pid="$(cat "${PID_FILE}")"
  if ps -p "${old_pid}" >/dev/null 2>&1; then
    echo "Zenoh bridge already running (pid ${old_pid})"
    exit 0
  fi
  rm -f "${PID_FILE}"
fi

if [[ -f "${ZENOH_CONFIG}" ]]; then
  nohup "${ZENOH_BIN}" -c "${ZENOH_CONFIG}" >"${LOG_FILE}" 2>&1 &
else
  echo "Config not found: ${ZENOH_CONFIG}"
  echo "Starting Zenoh bridge with default settings."
  nohup "${ZENOH_BIN}" >"${LOG_FILE}" 2>&1 &
fi
new_pid=$!
echo "${new_pid}" > "${PID_FILE}"

echo "Zenoh bridge started (pid ${new_pid})"
echo "Config: ${ZENOH_CONFIG}"
echo "Logs: ${LOG_FILE}"
