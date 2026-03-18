import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class Row:
    idx: int
    size: int
    pred_accept: float
    accept_rate: float


def _parse_float(s: str) -> float:
    try:
        return float(s)
    except Exception:
        return 0.0


def _parse_int(s: str) -> int:
    try:
        return int(s)
    except Exception:
        return 0


def read_best_rows(results_path: str) -> Dict[int, Row]:
    best: Dict[int, Row] = {}
    if not os.path.exists(results_path):
        raise FileNotFoundError(results_path)

    with open(results_path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    # Skip header if present
    if lines and lines[0].lower().startswith("id"):
        lines = lines[1:]

    for ln in lines:
        parts = re.split(r"\s+", ln)
        if len(parts) < 11:
            continue
        idx = _parse_int(parts[0])
        size = _parse_int(parts[1])
        pred_accept = _parse_float(parts[9])
        accept_rate = _parse_float(parts[10])
        row = Row(idx=idx, size=size, pred_accept=pred_accept, accept_rate=accept_rate)
        cur = best.get(idx)
        if cur is None or row.accept_rate > cur.accept_rate:
            best[idx] = row

    return best


def main() -> int:
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Ensure we use the more stable (non-FAST) measurement unless the caller opted into FAST.
    os.environ.setdefault("Q3_FAST", "0")

    topk = int(os.environ.get("Q3_TOPK", "5"))
    trials = int(os.environ.get("Q3_TRIALS", "50"))
    timeout_s = int(os.environ.get("Q3_TRIAL_TIMEOUT_S", "20"))

    # Force these settings for the in-process calls into solve_q3.
    os.environ["Q3_TRIALS"] = str(trials)
    os.environ["Q3_TRIAL_TIMEOUT_S"] = str(timeout_s)

    results_path = os.path.join(base_dir, "results.txt")
    best = read_best_rows(results_path)
    if not best:
        print("No rows found in results.txt")
        return 2

    rows: List[Row] = sorted(best.values(), key=lambda r: (r.accept_rate, r.pred_accept), reverse=True)
    rows = rows[: max(1, topk)]

    # Import after env defaults so solve_q3 picks them up.
    import solve_q3  # type: ignore

    print(
        f"Re-testing top {len(rows)} graphs with Q3_TRIALS={trials} and Q3_TRIAL_TIMEOUT_S={timeout_s} ...",
        flush=True,
    )

    for r in rows:
        graph_path = os.path.join(base_dir, "graphs", f"G_{r.idx}.txt")
        coloring_path = os.path.join(base_dir, "colorings", f"coloring_{r.idx}.txt")

        if not os.path.exists(graph_path):
            print(f"[ID {r.idx}] missing graph: {graph_path}")
            continue
        if not os.path.exists(coloring_path):
            print(f"[ID {r.idx}] missing coloring: {coloring_path}")
            continue

        print(f"[ID {r.idx:2d}] running verifier trials...", flush=True)
        measured, completed = solve_q3.run_experiment(graph_path=graph_path, coloring_path=coloring_path)
        print(
            f"[ID {r.idx:2d}] size_param={r.size:4d} | prev_accept={r.accept_rate*100:5.1f}% | "
            f"prev_pred={r.pred_accept*100:5.1f}% | retest={measured*100:5.1f}% (completed={completed})",
            flush=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
