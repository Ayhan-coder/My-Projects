#!/usr/bin/env python3
"""Run all CMPE476 experiments from one Python entrypoint.

This script runs:
1) Throughput experiments using ./client_flood.
2) Memory experiments by opening and holding many client connections.

Outputs:
- throughput_results.csv
- memory_results.csv
- experiment_results.md
"""

from __future__ import annotations

import argparse
import csv
import errno
import os
import platform
import resource
import selectors
import signal
import socket
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


SERVERS: Sequence[Tuple[str, int]] = (
    ("threadserv", 9090),
    ("epollserv", 9091),
)


@dataclass
class ThroughputResult:
    server: str
    clients: int
    requests_each: int
    established: int
    completed: int
    requests_completed: int
    elapsed_s: float
    rps: float
    avg_ms_per_req: float
    peak_rss_kb: int


@dataclass
class MemoryResult:
    server: str
    clients: int
    hold_seconds: int
    established: int
    failed: int
    peak_rss_kb: int
    peak_vmsize_kb: int
    peak_rss_mb: float
    peak_vmsize_mb: float


def parse_client_sizes(text: str) -> List[int]:
    vals: List[int] = []
    for token in text.split(","):
        token = token.strip()
        if not token:
            continue
        vals.append(int(token))
    if not vals:
        raise ValueError("client list cannot be empty")
    return vals


def ensure_linux() -> None:
    if platform.system() != "Linux":
        raise RuntimeError("Run this script inside WSL/Linux because servers are Linux binaries.")


def set_nofile_limit(required: int) -> None:
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    target = min(max(soft, required), hard)
    if soft < target:
        resource.setrlimit(resource.RLIMIT_NOFILE, (target, hard))


def run_cmd(cmd: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(cmd),
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=True,
    )


def tail_file(path: Path, max_lines: int = 30) -> str:
    if not path.exists():
        return "(log file not found)"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-max_lines:])


def wait_for_port(host: str, port: int, timeout_s: float, proc: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early with code {proc.returncode}")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(0.2)
            if s.connect_ex((host, port)) == 0:
                return
        finally:
            s.close()

        time.sleep(0.03)

    raise TimeoutError(f"timeout waiting for {host}:{port} to accept connections")


def read_proc_memory_kb(pid: int) -> Tuple[int, int]:
    status = Path(f"/proc/{pid}/status")
    if not status.exists():
        return (0, 0)

    rss = 0
    vmsize = 0
    try:
        with status.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    parts = line.split()
                    if len(parts) >= 2:
                        rss = int(parts[1])
                elif line.startswith("VmSize:"):
                    parts = line.split()
                    if len(parts) >= 2:
                        vmsize = int(parts[1])
    except OSError:
        return (0, 0)

    return (rss, vmsize)


def stop_process(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=3)


class MemorySampler:
    def __init__(self, pid: int, interval_s: float) -> None:
        self.pid = pid
        self.interval_s = interval_s
        self.peak_rss_kb = 0
        self.peak_vmsize_kb = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=2)

    def _run(self) -> None:
        while not self._stop.is_set():
            rss, vmsize = read_proc_memory_kb(self.pid)
            if rss > self.peak_rss_kb:
                self.peak_rss_kb = rss
            if vmsize > self.peak_vmsize_kb:
                self.peak_vmsize_kb = vmsize
            time.sleep(self.interval_s)


def start_server(root: Path, log_dir: Path, server_name: str, port: int, host: str) -> Tuple[subprocess.Popen[str], Path]:
    log_path = log_dir / f"{server_name}_{port}.log"
    log_file = log_path.open("w", encoding="utf-8")

    proc = subprocess.Popen(
        [str(root / server_name), str(port)],
        cwd=str(root),
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
        preexec_fn=os.setsid,
    )

    try:
        wait_for_port(host=host, port=port, timeout_s=10.0, proc=proc)
    except Exception:
        stop_process(proc)
        log_file.close()
        raise

    return proc, log_path


def parse_client_flood_output(output: str) -> Dict[str, float]:
    values: Dict[str, float] = {}
    for token in output.replace("\n", " ").split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        value = value.strip()
        if value.endswith("s") and key == "elapsed":
            value = value[:-1]
        try:
            if "." in value:
                values[key] = float(value)
            else:
                values[key] = float(int(value))
        except ValueError:
            continue
    required = ("clients_target", "established", "completed", "requests_completed", "elapsed", "rps")
    missing = [k for k in required if k not in values]
    if missing:
        raise ValueError(f"missing fields in client_flood output: {missing}\noutput was:\n{output}")
    return values


def run_throughput_case(
    root: Path,
    log_dir: Path,
    host: str,
    server_name: str,
    port: int,
    clients: int,
    requests_each: int,
    sample_interval_s: float,
) -> ThroughputResult:
    proc, log_path = start_server(root, log_dir, server_name, port, host)

    peak_rss = 0
    cmd = [str(root / "client_flood"), host, str(port), str(clients), str(requests_each)]
    client = subprocess.Popen(cmd, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    try:
        while client.poll() is None:
            rss, _ = read_proc_memory_kb(proc.pid)
            if rss > peak_rss:
                peak_rss = rss
            time.sleep(sample_interval_s)

        out, _ = client.communicate(timeout=2)
        final_rss, _ = read_proc_memory_kb(proc.pid)
        peak_rss = max(peak_rss, final_rss)
    finally:
        stop_process(proc)

    if client.returncode != 0:
        raise RuntimeError(f"client_flood failed for {server_name} {clients} clients:\n{out}")

    parsed = parse_client_flood_output(out)
    req = int(parsed["requests_completed"])
    elapsed = float(parsed["elapsed"])
    avg_ms = (elapsed / req) * 1000.0 if req > 0 else 0.0

    return ThroughputResult(
        server=server_name,
        clients=clients,
        requests_each=requests_each,
        established=int(parsed["established"]),
        completed=int(parsed["completed"]),
        requests_completed=req,
        elapsed_s=elapsed,
        rps=float(parsed["rps"]),
        avg_ms_per_req=avg_ms,
        peak_rss_kb=peak_rss,
    )


def establish_nonblocking_connections(host: str, port: int, total_clients: int, timeout_s: float) -> Tuple[List[socket.socket], int, int]:
    selector = selectors.DefaultSelector()
    sockets: List[socket.socket] = []
    established = 0
    failed = 0

    progress_errors = {errno.EINPROGRESS, errno.EALREADY, errno.EWOULDBLOCK}

    for _ in range(total_clients):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        err = s.connect_ex((host, port))
        if err == 0:
            sockets.append(s)
            established += 1
        elif err in progress_errors:
            selector.register(s, selectors.EVENT_WRITE)
        else:
            s.close()
            failed += 1

    deadline = time.monotonic() + timeout_s
    while selector.get_map() and time.monotonic() < deadline:
        events = selector.select(timeout=0.2)
        if not events:
            continue

        for key, _ in events:
            sock = key.fileobj
            assert isinstance(sock, socket.socket)
            try:
                selector.unregister(sock)
            except Exception:
                pass

            err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if err == 0:
                sockets.append(sock)
                established += 1
            else:
                sock.close()
                failed += 1

    for key in list(selector.get_map().values()):
        sock = key.fileobj
        assert isinstance(sock, socket.socket)
        try:
            selector.unregister(sock)
        except Exception:
            pass
        sock.close()
        failed += 1

    selector.close()
    return sockets, established, failed


def close_sockets(sockets: Iterable[socket.socket]) -> None:
    for s in sockets:
        try:
            s.close()
        except OSError:
            pass


def run_memory_case(
    root: Path,
    log_dir: Path,
    host: str,
    server_name: str,
    port: int,
    clients: int,
    hold_seconds: int,
    connect_timeout_s: float,
    sample_interval_s: float,
) -> MemoryResult:
    proc, log_path = start_server(root, log_dir, server_name, port, host)

    sampler = MemorySampler(pid=proc.pid, interval_s=sample_interval_s)
    sampler.start()

    sockets: List[socket.socket] = []
    established = 0
    failed = clients

    try:
        sockets, established, failed = establish_nonblocking_connections(
            host=host,
            port=port,
            total_clients=clients,
            timeout_s=connect_timeout_s,
        )

        if established > 0 and hold_seconds > 0:
            time.sleep(hold_seconds)
    finally:
        close_sockets(sockets)
        time.sleep(0.2)
        sampler.stop()
        stop_process(proc)

    peak_rss_kb = sampler.peak_rss_kb
    peak_vmsize_kb = sampler.peak_vmsize_kb

    return MemoryResult(
        server=server_name,
        clients=clients,
        hold_seconds=hold_seconds,
        established=established,
        failed=failed,
        peak_rss_kb=peak_rss_kb,
        peak_vmsize_kb=peak_vmsize_kb,
        peak_rss_mb=peak_rss_kb / 1024.0,
        peak_vmsize_mb=peak_vmsize_kb / 1024.0,
    )


def write_csv(path: Path, rows: Sequence[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "|" + "|".join(["---"] * len(headers)) + "|"
    body = ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def write_markdown(
    path: Path,
    throughput: Sequence[ThroughputResult],
    memory: Sequence[MemoryResult],
    args: argparse.Namespace,
) -> None:
    lines: List[str] = []
    lines.append("# Experiment Results")
    lines.append("")
    lines.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Host: {args.host}")
    lines.append("")

    if throughput:
        lines.append("## Throughput")
        lines.append("")
        lines.append(
            markdown_table(
                headers=[
                    "server",
                    "clients",
                    "requests_each",
                    "established",
                    "completed",
                    "requests_completed",
                    "elapsed_s",
                    "rps",
                    "avg_ms_per_req",
                    "peak_rss_kb",
                ],
                rows=[
                    [
                        r.server,
                        str(r.clients),
                        str(r.requests_each),
                        str(r.established),
                        str(r.completed),
                        str(r.requests_completed),
                        f"{r.elapsed_s:.3f}",
                        f"{r.rps:.0f}",
                        f"{r.avg_ms_per_req:.6f}",
                        str(r.peak_rss_kb),
                    ]
                    for r in throughput
                ],
            )
        )
        lines.append("")

    if memory:
        lines.append("## Memory")
        lines.append("")
        lines.append(
            markdown_table(
                headers=[
                    "server",
                    "clients",
                    "hold_seconds",
                    "established",
                    "failed",
                    "peak_rss_kb",
                    "peak_vmsize_kb",
                    "peak_rss_mb",
                    "peak_vmsize_mb",
                ],
                rows=[
                    [
                        r.server,
                        str(r.clients),
                        str(r.hold_seconds),
                        str(r.established),
                        str(r.failed),
                        str(r.peak_rss_kb),
                        str(r.peak_vmsize_kb),
                        f"{r.peak_rss_mb:.2f}",
                        f"{r.peak_vmsize_mb:.2f}",
                    ]
                    for r in memory
                ],
            )
        )
        lines.append("")
        lines.append("Note: thread-per-connection memory impact is better reflected by VmSize (reserved stacks) than VmRSS.")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_binaries(root: Path) -> None:
    run_cmd(["make"], cwd=root)
    run_cmd(["make", "client_flood"], cwd=root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run throughput and memory experiments from one Python file.")
    parser.add_argument("--host", default="127.0.0.1", help="target host for clients")
    parser.add_argument("--clients", default="1000,5000,10000", help="comma-separated client counts")
    parser.add_argument("--requests-each", type=int, default=20, help="requests per client for throughput tests")
    parser.add_argument("--hold-seconds", type=int, default=12, help="hold duration for memory tests")
    parser.add_argument("--connect-timeout", type=float, default=45.0, help="connection timeout for memory tests")
    parser.add_argument("--sample-interval", type=float, default=0.01, help="memory sampling interval in seconds")
    parser.add_argument("--skip-throughput", action="store_true", help="skip throughput experiments")
    parser.add_argument("--skip-memory", action="store_true", help="skip memory experiments")
    parser.add_argument("--output-md", default="experiment_results.md", help="output markdown file")
    parser.add_argument("--throughput-csv", default="throughput_results.csv", help="throughput CSV output")
    parser.add_argument("--memory-csv", default="memory_results.csv", help="memory CSV output")
    parser.add_argument("--log-dir", default="experiment_logs", help="directory for server logs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_linux()

    root = Path(__file__).resolve().parent
    log_dir = root / args.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    client_sizes = parse_client_sizes(args.clients)
    if args.requests_each <= 0:
        raise ValueError("--requests-each must be > 0")
    if args.hold_seconds < 0:
        raise ValueError("--hold-seconds must be >= 0")

    # Reserve enough descriptors for high-connection client runs.
    required_fds = max(client_sizes) * 2 + 512
    set_nofile_limit(required_fds)

    build_binaries(root)

    throughput_results: List[ThroughputResult] = []
    memory_results: List[MemoryResult] = []

    for server_name, port in SERVERS:
        if not args.skip_throughput:
            for n in client_sizes:
                result = run_throughput_case(
                    root=root,
                    log_dir=log_dir,
                    host=args.host,
                    server_name=server_name,
                    port=port,
                    clients=n,
                    requests_each=args.requests_each,
                    sample_interval_s=args.sample_interval,
                )
                throughput_results.append(result)
                print(asdict(result))
                sys.stdout.flush()

        if not args.skip_memory:
            for n in client_sizes:
                result = run_memory_case(
                    root=root,
                    log_dir=log_dir,
                    host=args.host,
                    server_name=server_name,
                    port=port,
                    clients=n,
                    hold_seconds=args.hold_seconds,
                    connect_timeout_s=args.connect_timeout,
                    sample_interval_s=args.sample_interval,
                )
                memory_results.append(result)
                print(asdict(result))
                sys.stdout.flush()

    throughput_dicts = [asdict(r) for r in throughput_results]
    memory_dicts = [asdict(r) for r in memory_results]

    write_csv(root / args.throughput_csv, throughput_dicts)
    write_csv(root / args.memory_csv, memory_dicts)
    write_markdown(root / args.output_md, throughput_results, memory_results, args)

    print("Done.")
    print(f"Throughput CSV: {root / args.throughput_csv}")
    print(f"Memory CSV: {root / args.memory_csv}")
    print(f"Markdown: {root / args.output_md}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        msg = ["Command failed:", " ".join(exc.cmd)]
        if exc.stdout:
            msg.append("\nstdout:\n" + exc.stdout.strip())
        if exc.stderr:
            msg.append("\nstderr:\n" + exc.stderr.strip())
        print("\n".join(msg), file=sys.stderr)
        raise
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise
