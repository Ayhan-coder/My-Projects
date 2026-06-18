from __future__ import annotations

import argparse
from pathlib import Path

from demucs_music_speech_common import add_common_args, separate_music_speech_with_demucs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Demucs-inspired Variant 1: speech=vocals, music=drums+bass+other. "
            "Install first with: pip install demucs soundfile"
        )
    )
    add_common_args(parser)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    separate_music_speech_with_demucs(
        input_audio=Path(args.input),
        output_dir=Path(args.output_dir),
        variant="vocals_only",
        model=args.model,
        device=args.device,
        other_in_speech=0.0,
        keep_stems=args.keep_stems,
    )


if __name__ == "__main__":
    main()
