# Experiment Results

Date: 2026-05-08 01:19:49
Host: 127.0.0.1

## Throughput

| server | clients | requests_each | established | completed | requests_completed | elapsed_s | rps | avg_ms_per_req | peak_rss_kb |
|---|---|---|---|---|---|---|---|---|---|
| threadserv | 1000 | 20 | 1000 | 1000 | 20000 | 0.102 | 197038 | 0.005100 | 2112 |
| threadserv | 5000 | 20 | 5000 | 5000 | 100000 | 1.131 | 88422 | 0.011310 | 23180 |
| threadserv | 10000 | 20 | 10000 | 10000 | 200000 | 4.233 | 47253 | 0.021165 | 33792 |
| epollserv | 1000 | 20 | 1000 | 1000 | 20000 | 0.103 | 193761 | 0.005150 | 3264 |
| epollserv | 5000 | 20 | 5000 | 5000 | 100000 | 0.266 | 376147 | 0.002660 | 11520 |
| epollserv | 10000 | 20 | 10000 | 10000 | 200000 | 0.537 | 372427 | 0.002685 | 21696 |

## Memory

| server | clients | hold_seconds | established | failed | peak_rss_kb | peak_vmsize_kb | peak_rss_mb | peak_vmsize_mb |
|---|---|---|---|---|---|---|---|---|
| threadserv | 1000 | 12 | 1000 | 0 | 16320 | 8198948 | 15.94 | 8006.79 |
| threadserv | 5000 | 12 | 5000 | 0 | 81600 | 40984004 | 79.69 | 40023.44 |
| threadserv | 10000 | 12 | 10000 | 0 | 162624 | 81965456 | 158.81 | 80044.39 |
| epollserv | 1000 | 12 | 1000 | 0 | 3456 | 4664 | 3.38 | 4.55 |
| epollserv | 5000 | 12 | 5000 | 0 | 11328 | 12716 | 11.06 | 12.42 |
| epollserv | 10000 | 12 | 10000 | 0 | 21504 | 22880 | 21.00 | 22.34 |

Note: thread-per-connection memory impact is better reflected by VmSize (reserved stacks) than VmRSS.
