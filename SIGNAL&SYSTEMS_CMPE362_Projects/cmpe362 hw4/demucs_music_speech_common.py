from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

try:
    import soundfile as sf
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency 'soundfile'. Install with: pip install soundfile"
    ) from exc


def run_demucs(input_audio: Path, work_dir: Path, model: str, device: str) -> Path:
    work_dir.mkdir(parents=True, exist_ok=True)
    demucs_input = prepare_input_for_demucs(input_audio, work_dir)

    command = [
        sys.executable,
        "-m",
        "demucs.separate",
        "--name",
        model,
        "--out",
        str(work_dir),
        "--device",
        device,
        str(demucs_input),
    ]
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise SystemExit(
            "Python executable not found while launching Demucs."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "Demucs separation failed. Ensure Demucs is installed: pip install demucs"
        ) from exc

    stem_dir = work_dir / model / demucs_input.stem
    if not stem_dir.exists():
        raise SystemExit(f"Expected Demucs output folder was not found: {stem_dir}")
    return stem_dir


def prepare_input_for_demucs(input_audio: Path, work_dir: Path) -> Path:
    data, sample_rate = sf.read(input_audio, always_2d=True)
    if data.shape[1] >= 2:
        return input_audio

    stereo_data = np.repeat(data, 2, axis=1)
    stereo_input = work_dir / f"{input_audio.stem}_stereo_for_demucs.wav"
    sf.write(stereo_input, stereo_data, sample_rate)
    return stereo_input


def _read_stem(path: Path) -> tuple[np.ndarray, int]:
    data, sample_rate = sf.read(path, always_2d=True)
    return data.astype(np.float32), sample_rate


def _trim_to_shortest(*signals: np.ndarray) -> list[np.ndarray]:
    min_len = min(signal.shape[0] for signal in signals)
    return [signal[:min_len] for signal in signals]


def _peak_normalize(signal: np.ndarray, target_peak: float = 0.95) -> np.ndarray:
    peak = float(np.max(np.abs(signal)))
    if peak <= 0:
        return signal
    scale = min(1.0, target_peak / peak)
    return signal * scale


def compose_music_speech(
    stem_dir: Path,
    output_dir: Path,
    base_name: str,
    variant: str,
    other_in_speech: float,
) -> tuple[Path, Path]:
    required = ["vocals.wav", "drums.wav", "bass.wav", "other.wav"]
    missing = [name for name in required if not (stem_dir / name).exists()]
    if missing:
        raise SystemExit(
            f"Demucs stems missing in {stem_dir}: {', '.join(missing)}"
        )

    vocals, sample_rate = _read_stem(stem_dir / "vocals.wav")
    drums, _ = _read_stem(stem_dir / "drums.wav")
    bass, _ = _read_stem(stem_dir / "bass.wav")
    other, _ = _read_stem(stem_dir / "other.wav")

    vocals, drums, bass, other = _trim_to_shortest(vocals, drums, bass, other)

    if variant == "vocals_only":
        speech = vocals
        music = drums + bass + other
    elif variant == "vocals_plus_other":
        blend = float(np.clip(other_in_speech, 0.0, 1.0))
        speech = vocals + blend * other
        music = drums + bass + (1.0 - blend) * other
    else:
        raise ValueError(f"Unsupported variant: {variant}")

    speech = _peak_normalize(speech)
    music = _peak_normalize(music)

    output_dir.mkdir(parents=True, exist_ok=True)
    music_path = output_dir / f"{base_name}_{variant}_music.wav"
    speech_path = output_dir / f"{base_name}_{variant}_speech.wav"
    sf.write(music_path, music, sample_rate)
    sf.write(speech_path, speech, sample_rate)
    return music_path, speech_path


def separate_music_speech_with_demucs(
    input_audio: Path,
    output_dir: Path,
    variant: str,
    model: str,
    device: str,
    other_in_speech: float,
    keep_stems: bool,
) -> tuple[Path, Path]:
    input_audio = input_audio.resolve()
    output_dir = output_dir.resolve()
    if not input_audio.exists():
        raise SystemExit(f"Input audio not found: {input_audio}")

    stems_root = output_dir / "demucs_stems"
    stem_dir = run_demucs(input_audio, stems_root, model, device)
    music_path, speech_path = compose_music_speech(
        stem_dir=stem_dir,
        output_dir=output_dir,
        base_name=input_audio.stem,
        variant=variant,
        other_in_speech=other_in_speech,
    )

    if not keep_stems:
        shutil.rmtree(stems_root, ignore_errors=True)

    print(f"Saved music track : {music_path}")
    print(f"Saved speech track: {speech_path}")
    print(f"Demucs stems path : {stem_dir}")
    return music_path, speech_path


def add_common_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--input", required=True, help="Path to input mix, e.g. cafe_sample.wav")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory for output files (default: current directory)",
    )
    parser.add_argument(
        "--model",
        default="htdemucs",
        help="Demucs model name (default: htdemucs)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda"],
        help="Inference device (default: cpu)",
    )
    parser.add_argument(
        "--keep-stems",
        action="store_true",
        help="Keep Demucs raw stem files in output-dir/demucs_stems",
    )
    return parser
