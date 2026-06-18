#!/usr/bin/env bash
set -euo pipefail

# Insert.sh
# Usage: sudo ./Insert.sh <studentID>

DEFAULT_ID="2021400219"

if [ "$#" -eq 0 ]; then
  echo "No studentID provided; using default: $DEFAULT_ID"
  ID="$DEFAULT_ID"
elif [ "$#" -eq 1 ]; then
  ID="$1"
else
  echo "Usage: $0 [studentID]" >&2
  exit 1
fi

if ! [[ "$ID" =~ ^[0-9]+$ ]]; then
  echo "studentID must be numeric" >&2
  exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root (or via sudo)." >&2
  exit 1
fi

# compute char_key: sum of digits of ID
char_key=0
for ((i=0; i<${#ID}; i++)); do
  digit=${ID:i:1}
  char_key=$((char_key + digit))
done

# compute short_key: ID modulo 32767
short_key=$((ID % 32767))

# find machine.ko (prefer local path)
KO=""
if [ -f ./machine.ko ]; then
  KO="./machine.ko"
elif [ -f ./amd64/machine.ko ]; then
  KO="./amd64/machine.ko"
elif [ -f "$(pwd)/machine.ko" ]; then
  KO="$(pwd)/machine.ko"
fi

if [ -z "$KO" ]; then
  echo "Error: machine.ko not found in current directory or ./amd64" >&2
  exit 1
fi

echo "Inserting kernel module $KO with parameters:" \
     "char_key=$char_key short_key=$short_key user_string_key=$ID"

# Insert module (use insmod to ensure local .ko used)
if lsmod | grep -q '^machine\b'; then
  echo "machine module already loaded; attempting to remove first"
  rmmod machine || true
fi

insmod "$KO" char_key="$char_key" short_key="$short_key" user_string_key="$ID"

sleep 1

# create character device /dev/cmachine major 444 minor 4
DEVPATH="/dev/cmachine"
if [ ! -e "$DEVPATH" ]; then
  echo "Creating character device $DEVPATH (major 444 minor 4)"
  mknod "$DEVPATH" c 444 4
fi

# Set permissions to read-write, not execute for all users
chmod 666 "$DEVPATH"

echo "Module inserted and device $DEVPATH created with permissions $(stat -c '%A' $DEVPATH)"
echo "To remove, run Detach.sh or use: sudo rmmod machine && sudo rm -f /dev/cmachine"
