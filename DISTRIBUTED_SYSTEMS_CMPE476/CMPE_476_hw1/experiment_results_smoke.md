# Experiment Results

Date: 2026-04-20 00:36:52
Host: 127.0.0.1

## Throughput

| server | clients | requests_each | established | completed | requests_completed | elapsed_s | rps | avg_ms_per_req | peak_rss_kb |
|---|---|---|---|---|---|---|---|---|---|
| threadserv | 50 | 2 | 50 | 50 | 100 | 0.004 | 27225 | 0.040000 | 1536 |
| epollserv | 50 | 2 | 50 | 50 | 100 | 0.001 | 100242 | 0.010000 | 1536 |

## Memory

| server | clients | hold_seconds | established | failed | peak_rss_kb | peak_vmsize_kb | peak_rss_mb | peak_vmsize_mb |
|---|---|---|---|---|---|---|---|---|
| threadserv | 50 | 1 | 50 | 0 | 1536 | 412484 | 1.50 | 402.82 |
| epollserv | 50 | 1 | 50 | 0 | 1536 | 2684 | 1.50 | 2.62 |

Note: thread-per-connection memory impact is better reflected by VmSize (reserved stacks) than VmRSS.
