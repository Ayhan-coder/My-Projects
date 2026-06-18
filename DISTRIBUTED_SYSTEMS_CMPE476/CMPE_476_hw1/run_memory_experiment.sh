#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
ulimit -n 200000 || true

gcc -std=c11 -D_GNU_SOURCE -O2 -Wall -Wextra -Wpedantic -o client_hold client_hold.c

echo "server,clients,hold_seconds,established,failed,peak_rss_kb,peak_vmsize_kb,peak_rss_mb,peak_vmsize_mb"

wait_for_listen() {
    local srvpid="$1"
    local port="$2"
    local hex_port
    local i

    hex_port=$(printf '%04X' "$port")

    for i in $(seq 1 200000); do
        if ! kill -0 "$srvpid" 2>/dev/null; then
            return 1
        fi

        if awk -v hp="$hex_port" 'BEGIN {IGNORECASE=1} $2 ~ ":" hp "$" && $4 == "0A" {found=1} END {exit(found ? 0 : 1)}' /proc/net/tcp >/dev/null 2>&1; then
            return 0
        fi
    done

    return 1
}

sample_case() {
    local srvname="$1"
    local port="$2"
    local n="$3"
    local hold_s=12

    local srvpid clipid peak_rss peak_vmsize rss vms out line est fail

    "./${srvname}" "$port" >/tmp/${srvname}_${n}_mem.log 2>&1 &
    srvpid=$!

    if ! wait_for_listen "$srvpid" "$port"; then
        echo "${srvname},${n},${hold_s},0,${n},0,0,0.00,0.00"
        kill "$srvpid" 2>/dev/null || true
        wait "$srvpid" 2>/dev/null || true
        return
    fi

    ./client_hold 127.0.0.1 "$port" "$n" "$hold_s" >/tmp/client_hold_${srvname}_${n}.out 2>&1 &
    clipid=$!

    peak_rss=0
    peak_vmsize=0

    while kill -0 "$clipid" 2>/dev/null; do
        rss=$(awk '/VmRSS:/ {print $2}' "/proc/${srvpid}/status" 2>/dev/null || true)
        vms=$(awk '/VmSize:/ {print $2}' "/proc/${srvpid}/status" 2>/dev/null || true)

        rss=${rss:-0}
        vms=${vms:-0}

        if [ "$rss" -gt "$peak_rss" ] 2>/dev/null; then
            peak_rss="$rss"
        fi
        if [ "$vms" -gt "$peak_vmsize" ] 2>/dev/null; then
            peak_vmsize="$vms"
        fi
    done

    wait "$clipid" || true

    rss=$(awk '/VmRSS:/ {print $2}' "/proc/${srvpid}/status" 2>/dev/null || true)
    vms=$(awk '/VmSize:/ {print $2}' "/proc/${srvpid}/status" 2>/dev/null || true)
    rss=${rss:-0}
    vms=${vms:-0}

    if [ "$rss" -gt "$peak_rss" ] 2>/dev/null; then
        peak_rss="$rss"
    fi
    if [ "$vms" -gt "$peak_vmsize" ] 2>/dev/null; then
        peak_vmsize="$vms"
    fi

    kill "$srvpid" 2>/dev/null || true
    wait "$srvpid" 2>/dev/null || true

    out="/tmp/client_hold_${srvname}_${n}.out"
    line=$(grep -E '^clients_target=' "$out" | tail -n1 || true)

    est=$(echo "$line" | sed -n 's/.*established=\([0-9][0-9]*\).*/\1/p')
    fail=$(echo "$line" | sed -n 's/.*failed=\([0-9][0-9]*\).*/\1/p')

    est=${est:-0}
    fail=${fail:-0}

    local peak_rss_mb peak_vmsize_mb
    peak_rss_mb=$(awk -v x="$peak_rss" 'BEGIN { printf "%.2f", x / 1024.0 }')
    peak_vmsize_mb=$(awk -v x="$peak_vmsize" 'BEGIN { printf "%.2f", x / 1024.0 }')

    echo "${srvname},${n},${hold_s},${est},${fail},${peak_rss},${peak_vmsize},${peak_rss_mb},${peak_vmsize_mb}"
}

for n in 1000 5000 10000; do
    sample_case threadserv 9090 "$n"
done

for n in 1000 5000 10000; do
    sample_case epollserv 9091 "$n"
done
