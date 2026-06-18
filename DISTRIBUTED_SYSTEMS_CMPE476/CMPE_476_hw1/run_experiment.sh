#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
ulimit -n 200000 || true

make >/tmp/make_exp.log 2>&1
make client_flood >/tmp/make_client_exp.log 2>&1 || true

echo "server,clients,requests_each,established,completed,requests_completed,elapsed_s,rps,avg_ms_per_req,peak_rss_kb"

run_case() {
    local srvname="$1"
    local port="$2"

    local n m srvpid clipid peak rss out line1 line2
    local est comp req elapsed rps avg_ms

    for n in 1000 5000 10000; do
        m=20

        "./${srvname}" "$port" >/tmp/${srvname}_${n}.log 2>&1 &
        srvpid=$!

        ./client_flood 127.0.0.1 "$port" "$n" "$m" >/tmp/client_${srvname}_${n}.out 2>&1 &
        clipid=$!

        peak=$(ps -o rss= -p "$srvpid" 2>/dev/null | tr -d ' ' || true)
        peak=${peak:-0}
        while kill -0 "$clipid" 2>/dev/null; do
            rss=$(ps -o rss= -p "$srvpid" 2>/dev/null | tr -d ' ' || true)
            rss=${rss:-0}
            if [ "$rss" -gt "$peak" ] 2>/dev/null; then
                peak="$rss"
            fi
        done

        wait "$clipid" || true

        # Take one final sample before stopping the server to avoid 0 KB peaks on very fast runs.
        rss=$(ps -o rss= -p "$srvpid" 2>/dev/null | tr -d ' ' || true)
        rss=${rss:-0}
        if [ "$rss" -gt "$peak" ] 2>/dev/null; then
            peak="$rss"
        fi

        kill "$srvpid" 2>/dev/null || true
        wait "$srvpid" 2>/dev/null || true

        out=/tmp/client_${srvname}_${n}.out
        line1=$(grep -E '^clients_target=' "$out" | tail -n1 || true)
        line2=$(grep -E '^requests_completed=' "$out" | tail -n1 || true)

        est=$(echo "$line1" | sed -n 's/.*established=\([0-9][0-9]*\).*/\1/p')
        comp=$(echo "$line1" | sed -n 's/.*completed=\([0-9][0-9]*\).*/\1/p')
        req=$(echo "$line2" | sed -n 's/.*requests_completed=\([0-9][0-9]*\).*/\1/p')
        elapsed=$(echo "$line2" | sed -n 's/.*elapsed=\([0-9.][0-9.]*\).*/\1/p')
        rps=$(echo "$line2" | sed -n 's/.*rps=\([0-9.][0-9.]*\).*/\1/p')

        est=${est:-0}
        comp=${comp:-0}
        req=${req:-0}
        elapsed=${elapsed:-nan}
        rps=${rps:-nan}

        avg_ms=$(awk -v e="$elapsed" -v r="$req" 'BEGIN { if (r+0 > 0) printf "%.6f", (e/r)*1000; else printf "nan" }')

        echo "${srvname},${n},${m},${est},${comp},${req},${elapsed},${rps},${avg_ms},${peak}"
    done
}

run_case threadserv 9090
run_case epollserv 9091
