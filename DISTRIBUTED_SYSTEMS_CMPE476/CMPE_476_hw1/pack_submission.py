#!/usr/bin/env python3
"""Create the required CMPE476 submission tarball.

Produces a .tar.gz named exactly:
  textCMPE476-C10k-<group_id>-<surname1>[_<surname2>].tar.gz

The archive contains (at the archive root):
  - all .c and .h files in the project root
  - Makefile
  - report.pdf
  - README.md (if present)

This script is intentionally cross-platform (no external `tar` needed).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tarfile
from pathlib import Path


_OPTIONAL_FILES = ["README.md"]


def _validate_token(value: str, *, label: str) -> str:
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError(f"{label} cannot be empty")

    # Keep filename-safe and predictable (letters/digits/underscore/hyphen only).
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", value):
        raise argparse.ArgumentTypeError(
            f"{label} must match [A-Za-z0-9][A-Za-z0-9_-]* (got {value!r})"
        )
    return value


def _collect_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []

    files.extend(sorted(source_dir.glob("*.c")))
    files.extend(sorted(source_dir.glob("*.h")))

    for name in _OPTIONAL_FILES:
        p = source_dir / name
        if p.exists():
            files.append(p)

    # De-dup while preserving order
    seen: set[Path] = set()
    out: list[Path] = []
    for p in files:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    return out


def _find_case_insensitive(path: Path, filename: str) -> Path | None:
    if not path.exists() or not path.is_dir():
        return None
    filename_lower = filename.lower()
    for child in path.iterdir():
        if child.is_file() and child.name.lower() == filename_lower:
            return child
    return None


def _find_required(root: Path, filename: str, *, fallbacks: list[Path]) -> Path:
    found = _find_case_insensitive(root, filename)
    if found is not None:
        return found

    for fb in fallbacks:
        found = _find_case_insensitive(fb, filename)
        if found is not None:
            return found

    raise FileNotFoundError(
        f"Missing required file: {filename}. "
        "(If this is the report, build `report.pdf` from `report.tex` before packaging.)"
    )


def _pick_source_dir(root: Path, requested: str) -> Path:
    submission_dir = root / "submission"
    if requested == "root":
        return root
    if requested == "submission":
        if not submission_dir.exists() or not submission_dir.is_dir():
            raise FileNotFoundError("Requested --source submission but submission/ does not exist")
        return submission_dir

    # auto
    if submission_dir.exists() and submission_dir.is_dir():
        # Treat submission/ as canonical if it looks staged.
        if any(submission_dir.glob("*.c")) and any(submission_dir.glob("*.h")):
            return submission_dir
        if (submission_dir / "Makefile").exists():
            return submission_dir
    return root


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create CMPE476 submission tar.gz")
    parser.add_argument(
        "--output-name",
        default="",
        help=(
            "Override the output filename exactly (must end with .tar.gz). "
            "If provided, --group-id/--surname1/--surname2 are ignored for naming."
        ),
    )
    parser.add_argument("--group-id", default="", type=lambda s: _validate_token(s, label="group_id") if s.strip() else "")
    parser.add_argument("--surname1", default="", type=lambda s: _validate_token(s, label="surname1") if s.strip() else "")
    parser.add_argument("--surname2", default="", type=lambda s: _validate_token(s, label="surname2") if s.strip() else "")
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent),
        help="Project root directory (defaults to this script's folder)",
    )
    parser.add_argument(
        "--source",
        choices=["auto", "root", "submission"],
        default="auto",
        help="Where to pick files from: auto (default), root, or submission/",
    )
    parser.add_argument(
        "--out-dir",
        default="",
        help="Output directory for the tarball (defaults to --root)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing tarball if present",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print intended archive name and file list without creating it",
    )

    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve() if args.out_dir else root

    if args.output_name:
        tar_name = args.output_name.strip()
        if not tar_name.endswith(".tar.gz"):
            print("--output-name must end with .tar.gz", file=sys.stderr)
            return 2
        if any(sep in tar_name for sep in ("/", "\\")):
            print("--output-name must be a filename, not a path", file=sys.stderr)
            return 2
    else:
        if not args.group_id or not args.surname1:
            print(
                "Provide either --output-name OR (--group-id and --surname1).",
                file=sys.stderr,
            )
            return 2
        surname_part = args.surname1 + (f"_{args.surname2}" if args.surname2 else "")
        tar_name = f"textCMPE476-C10k-{args.group_id}-{surname_part}.tar.gz"
    out_path = out_dir / tar_name

    try:
        source_dir = _pick_source_dir(root, args.source)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    # Search required files in source_dir first, then fall back to the other dir.
    fallback_dirs: list[Path] = []
    if source_dir != root:
        fallback_dirs.append(root)
    submission_dir = root / "submission"
    if source_dir != submission_dir and submission_dir.exists():
        fallback_dirs.append(submission_dir)

    files = _collect_files(source_dir)

    try:
        makefile_path = _find_required(source_dir, "Makefile", fallbacks=fallback_dirs)
        report_path = _find_required(source_dir, "report.pdf", fallbacks=fallback_dirs)
    except FileNotFoundError as e:
        print(f"Archive name: {tar_name}")
        print(f"Source directory: {source_dir}")
        print("Files that will be packed (archive root):")
        for p in files:
            print(f"  - {p.name}")
        print(str(e), file=sys.stderr)
        return 1

    print(f"Archive name: {tar_name}")
    print(f"Source directory: {source_dir}")
    print("Files that will be packed (archive root):")
    for p in files:
        print(f"  - {p.name}")
    # Show resolved required files (may come from submission/ or differ by case).
    print(f"  - Makefile  (from: {makefile_path})")
    print(f"  - report.pdf (from: {report_path})")

    if args.dry_run:
        return 0

    if out_path.exists() and not args.force:
        print(f"Refusing to overwrite existing: {out_path}", file=sys.stderr)
        print("Re-run with --force to overwrite.", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)

    # Avoid tarring the output into itself if out_dir == root.
    exclude_resolved = {out_path.resolve()}

    count = 0
    with tarfile.open(out_path, mode="w:gz") as tf:
        # Ensure required files are always present with the expected names.
        tf.add(makefile_path, arcname="Makefile")
        count += 1
        tf.add(report_path, arcname="report.pdf")
        count += 1
        for p in files:
            rp = p.resolve()
            if rp in exclude_resolved:
                continue
            if not p.exists():
                continue
            # Don't add duplicates of required files.
            if rp == makefile_path.resolve() or rp == report_path.resolve():
                continue
            # Store at archive root (no directories)
            tf.add(p, arcname=p.name)
            count += 1

    size_kb = os.path.getsize(out_path) / 1024.0
    print(f"Created: {out_path}")
    print(f"Files packed: {count}")
    print(f"Size: {size_kb:.1f} KiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
