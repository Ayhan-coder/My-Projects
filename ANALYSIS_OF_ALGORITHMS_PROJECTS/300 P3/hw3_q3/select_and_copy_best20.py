import os
import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BestRow:
    idx: int
    size: int
    pred_accept: float
    accept_rate: float


def _parse_int(s: str) -> int:
    try:
        return int(s)
    except Exception:
        return 0


def _parse_float(s: str) -> float:
    try:
        return float(s)
    except Exception:
        return 0.0


def pick_best_per_id(results_path: str) -> Dict[int, BestRow]:
    best: Dict[int, BestRow] = {}

    with open(results_path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    if lines and lines[0].lower().startswith("id"):
        lines = lines[1:]

    for ln in lines:
        # results.txt sometimes renders with spaces depending on environment; accept any whitespace.
        parts = re.split(r"\s+", ln)
        if len(parts) < 11:
            continue
        idx = _parse_int(parts[0])
        size = _parse_int(parts[1])
        pred_accept = _parse_float(parts[9])
        accept_rate = _parse_float(parts[10])
        row = BestRow(idx=idx, size=size, pred_accept=pred_accept, accept_rate=accept_rate)

        cur = best.get(idx)
        if cur is None:
            best[idx] = row
            continue

        # Primary: higher measured accept_rate. Secondary: higher pred_accept.
        if (row.accept_rate > cur.accept_rate) or (
            abs(row.accept_rate - cur.accept_rate) < 1e-12 and row.pred_accept > cur.pred_accept
        ):
            best[idx] = row

    return best


def main() -> int:
    base = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(base, "results.txt")
    best = pick_best_per_id(results_path)

    rows: List[BestRow] = sorted(best.values(), key=lambda r: (r.accept_rate, r.pred_accept), reverse=True)

    topk = int(os.environ.get("Q3_TOPK", "20"))
    rows = rows[: max(1, topk)]

    out_dir = os.path.join(base, "best_20")
    out_g = os.path.join(out_dir, "graphs")
    out_c = os.path.join(out_dir, "colorings")
    os.makedirs(out_g, exist_ok=True)
    os.makedirs(out_c, exist_ok=True)

    summary_lines: List[str] = []
    summary_lines.append(f"Copied top {len(rows)} pairs from results.txt")
    summary_lines.append("Rank\tID\tSizeParam\tAcceptRate\tPredAccept")

    for rank, r in enumerate(rows, start=1):
        g_src = os.path.join(base, "graphs", f"G_{r.idx}.txt")
        c_src = os.path.join(base, "colorings", f"coloring_{r.idx}.txt")
        if not os.path.exists(g_src):
            raise FileNotFoundError(g_src)
        if not os.path.exists(c_src):
            raise FileNotFoundError(c_src)

        g_dst = os.path.join(out_g, f"G_{r.idx}.txt")
        c_dst = os.path.join(out_c, f"coloring_{r.idx}.txt")

        # Copy bytes
        with open(g_src, "rb") as fsrc, open(g_dst, "wb") as fdst:
            fdst.write(fsrc.read())
        with open(c_src, "rb") as fsrc, open(c_dst, "wb") as fdst:
            fdst.write(fsrc.read())

        summary_lines.append(
            f"{rank}\t{r.idx}\t{r.size}\t{r.accept_rate*100:.1f}%\t{r.pred_accept*100:.1f}%"
        )

    with open(os.path.join(out_dir, "SUMMARY.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines) + "\n")

    print(os.path.join(out_dir, "SUMMARY.txt"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
