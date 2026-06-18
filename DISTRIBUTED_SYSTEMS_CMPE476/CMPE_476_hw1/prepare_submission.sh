#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dst="$root/submission"

mkdir -p "$dst"

# Stage the required files into submission/ (useful for quick inspection).
cp -f \
  "$root"/*.c \
  "$root"/*.h \
  "$root"/Makefile \
  "$dst"/

# Stage the report if it exists either in the project root or already in submission/.
if [[ -f "$root/report.pdf" ]]; then
  cp -f "$root/report.pdf" "$dst/report.pdf"
elif [[ -f "$dst/report.pdf" ]]; then
  :
elif [[ -f "$dst/Report.pdf" ]]; then
  cp -f "$dst/Report.pdf" "$dst/report.pdf"
fi

if [[ -f "$root/README.md" ]]; then
  cp -f "$root/README.md" "$dst/"
fi

printf 'Staged submission contents (submission/):\n'
ls -1 "$dst"

# If naming parameters are provided, also create the required tar.gz.
# Usage:
#   ./prepare_submission.sh <group_id> <surname1> [surname2]
if [[ ${1:-} != "" && ${2:-} != "" ]]; then
  group_id="$1"
  surname1="$2"
  surname2="${3:-}"

  if [[ "$surname2" != "" ]]; then
    python3 "$root/pack_submission.py" --group-id "$group_id" --surname1 "$surname1" --surname2 "$surname2" --root "$root" --force
  else
    python3 "$root/pack_submission.py" --group-id "$group_id" --surname1 "$surname1" --root "$root" --force
  fi
fi
