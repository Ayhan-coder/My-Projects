from __future__ import annotations

import argparse
from pathlib import Path

from demucs_music_speech_common import add_common_args, separate_music_speech_with_demucs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Demucs-inspired Variant 2: speech=vocals+alpha*other, "
            "music=drums+bass+(1-alpha)*other. "
            "Install first with: pip install demucs soundfile"
        )
    )
    add_common_args(parser)
    parser.add_argument(
        "--other-in-speech",
        type=float,
        default=0.25,
        help="Blend ratio for Demucs 'other' stem into speech (0..1, default: 0.25)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    separate_music_speech_with_demucs(
        input_audio=Path(args.input),
        output_dir=Path(args.output_dir),
        variant="vocals_plus_other",
        model=args.model,
        device=args.device,
        other_in_speech=args.other_in_speech,
        keep_stems=args.keep_stems,
    )


if __name__ == "__main__":
    main()
