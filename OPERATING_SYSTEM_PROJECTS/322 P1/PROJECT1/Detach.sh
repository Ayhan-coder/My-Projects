#!/usr/bin/env bash
set -euo pipefail

# Detach.sh
# Removes the kernel module and device created by Insert.sh

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root (or via sudo)." >&2
  exit 1
fi

DEVPATH="/dev/cmachine"
MODULE_NAME="machine"

echo "Attempting to remove device $DEVPATH and kernel module $MODULE_NAME"

# Remove device file if present
if [ -e "$DEVPATH" ]; then
  rm -f "$DEVPATH"
  echo "Removed $DEVPATH"
else
  echo "$DEVPATH not present"
fi

# Try to remove the kernel module if loaded
if lsmod | awk '{print $1}' | grep -q "^${MODULE_NAME}$"; then
  echo "Module ${MODULE_NAME} is loaded — attempting rmmod"
  if rmmod "$MODULE_NAME"; then
    echo "Module ${MODULE_NAME} removed"
  else
    echo "Failed to remove module ${MODULE_NAME}. It may be in use or require force." >&2
    exit 1
  fi
else
  echo "Module ${MODULE_NAME} not loaded"
fi

echo "Detach complete"
