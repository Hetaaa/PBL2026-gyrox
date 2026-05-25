#!/usr/bin/env bash
# Zdejmujemy restrykcyjne flagi, które mogłyby ubić Twój główny terminal przy błędzie
set +e

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Lista wymaganych paczek
required_pkgs=(
  slam_bringup
  project_bringup
  robot_model
  scan_filter
  ultrasonic_driver
  zones_manager
  closest_element_info
)

# Sprawdzanie paczek (skorzysta dokładnie z tego, co masz w terminalu)
missing_pkgs=()
for pkg in "${required_pkgs[@]}"; do
  if ! ros2 pkg prefix "$pkg" >/dev/null 2>&1; then
    missing_pkgs+=("$pkg")
  fi
done

if (( ${#missing_pkgs[@]} > 0 )); then
  echo "Missing ROS packages: ${missing_pkgs[*]}"
  echo "Install native deps: bash scripts/install_native_deps.sh"
  # Używamy return zamiast exit, żeby nie zamknąć terminala użytkownika
  if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    return 1
  else
    exit 1
  fi
fi

# Odpalenie launchfile (BEZ exec, żeby nie ubić sesji terminala)
ros2 launch slam_bringup slam_bringup_launch.py "$@"