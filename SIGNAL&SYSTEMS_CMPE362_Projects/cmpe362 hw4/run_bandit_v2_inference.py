"""Run Bandit v2 inference (from kwatcharasupat/bandit-v2) on a local WAV.

This script is intentionally lightweight:
- It imports the model + chunked inference handler directly.
- It does NOT use Hydra configs, Ray, or Netflix-internal dependencies.

Prereqs (CPU-only is fine):
  pip install torch torchaudio pytorch-lightning tqdm

You must download a Bandit v2 checkpoint (.ckpt) yourself from the repo's Zenodo link:
  https://github.com/kwatcharasupat/bandit-v2 (see README)

Example:
  python run_bandit_v2_inference.py --ckpt path\\to\\bandit.ckpt --input cafe_sample.wav --outdir bandit_out

Outputs (in outdir):
  speech_bandit.wav, music_bandit.wav, sfx_bandit.wav (if present)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _workspace_root() -> Path:
    return Path(__file__).resolve().parent


def _add_bandit_repo_to_path() -> Path:
    repo_dir = _workspace_root() / "bandit-v2"
    if not repo_dir.exists():
        raise FileNotFoundError(
            f"Expected {repo_dir} (git clone the repo into the workspace first)."
        )
    sys.path.insert(0, str(repo_dir))
    return repo_dir


def _pick_device(force_cpu: bool) -> str:
    import torch

    if force_cpu:
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def _load_checkpoint_state_dict(ckpt_path: Path, device: str) -> dict:
    import torch

    ckpt = torch.load(str(ckpt_path), map_location=device)
    if isinstance(ckpt, dict) and "state_dict" in ckpt:
        return ckpt["state_dict"]
    if isinstance(ckpt, dict):
        return ckpt
    raise ValueError("Unsupported checkpoint format (expected dict or dict with state_dict).")


def _strip_prefix(state_dict: dict, prefix: str) -> dict:
    out: dict = {}
    for k, v in state_dict.items():
        if k.startswith(prefix):
            out[k[len(prefix) :]] = v
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", required=True, type=Path, help="Path to .ckpt file")
    parser.add_argument(
        "--input", default="cafe_sample.wav", type=Path, help="Input mixture WAV"
    )
    parser.add_argument(
        "--outdir", default=Path("bandit_out"), type=Path, help="Output directory"
    )
    parser.add_argument("--fs", default=48000, type=int, help="Model sample rate")
    parser.add_argument(
        "--chunk", default=8.0, type=float, help="Chunk size (seconds)"
    )
    parser.add_argument("--hop", default=1.0, type=float, help="Hop size (seconds)")
    parser.add_argument(
        "--batch",
        default=None,
        type=int,
        help="Inference batch size (chunks per forward). Default: 1 on CPU, 16 on CUDA",
    )
    parser.add_argument(
        "--force-cpu", action="store_true", help="Force CPU even if CUDA exists"
    )

    args = parser.parse_args()

    _add_bandit_repo_to_path()

    import torch
    import torchaudio as ta

    device = _pick_device(args.force_cpu)

    if args.batch is None:
        inference_batch_size = 16 if device == "cuda" else 1
    else:
        inference_batch_size = args.batch

    args.outdir.mkdir(parents=True, exist_ok=True)

    if not args.input.exists():
        raise FileNotFoundError(f"Missing input file: {args.input}")
    if not args.ckpt.exists():
        raise FileNotFoundError(f"Missing checkpoint: {args.ckpt}")

    # Import model + inference handler
    from src.models.bandit.bandit import Bandit
    from src.system.inference_handler import StandardTensorChunkedInferenceHandler

    # Construct model matching configs/models/bandit-mus64.yaml + stems from dnr-v3 config
    stems = ["speech", "music", "sfx"]

    model = Bandit(
        fs=args.fs,
        stems=stems,
        in_channels=1,
        band_type="musical",
        n_bands=64,
        normalize_channel_independently=False,
        treat_channel_as_feature=True,
        n_sqm_modules=8,
        emb_dim=128,
        rnn_dim=256,
        bidirectional=True,
        rnn_type="GRU",
        mlp_dim=512,
        hidden_activation="Tanh",
        hidden_activation_kwargs=None,
        complex_mask=True,
        use_freq_weights=True,
        n_fft=2048,
        win_length=2048,
        hop_length=512,
        window_fn="hann_window",
        wkwargs=None,
        power=None,
        center=True,
        normalized=True,
        pad_mode="reflect",
        onesided=True,
    )

    state_dict = _load_checkpoint_state_dict(args.ckpt, device=device)

    # Try common Lightning prefix pattern: "model." (System.model)
    if any(k.startswith("model.") for k in state_dict.keys()):
        model_state = _strip_prefix(state_dict, "model.")
    else:
        model_state = state_dict

    missing, unexpected = model.load_state_dict(model_state, strict=False)

    model.to(device)
    model.eval()

    # Load mixture and resample to model fs
    audio, fs_in = ta.load(str(args.input))  # (channels, samples)
    if audio.ndim != 2:
        raise ValueError(f"Unexpected audio shape: {tuple(audio.shape)}")

    # Downmix to mono (model expects in_channels=1)
    if audio.shape[0] > 1:
        audio = audio.mean(dim=0, keepdim=True)

    if fs_in != args.fs:
        audio = ta.functional.resample(audio, fs_in, args.fs)

    mixture = audio[None, :, :].to(device)  # (1, 1, n_samples)

    inference = StandardTensorChunkedInferenceHandler(
        chunk_size_seconds=float(args.chunk),
        hop_size_seconds=float(args.hop),
        inference_batch_size=int(inference_batch_size),
        fs=int(args.fs),
        window_fn="hann_window",
        wkwargs=None,
        pad_mode="reflect",
        rank=0,
    )
    inference.to(device)

    with torch.inference_mode():
        out = inference(mixture, model)

    # Save stems
    estimates = out["estimates"]

    for stem, payload in estimates.items():
        stem_audio = payload["audio"][0].detach().cpu()  # (1, n_samples)
        # Safety normalization
        stem_audio = 0.98 * stem_audio / (stem_audio.abs().max() + 1e-12)

        out_path = args.outdir / f"{stem}_bandit.wav"
        ta.save(str(out_path), stem_audio, args.fs)
        print(f"Wrote {out_path}")

    # Also write convenience copies if present
    if "speech" in estimates:
        (args.outdir / "vocals_bandit.wav").write_bytes(
            (args.outdir / "speech_bandit.wav").read_bytes()
        )
    print("\nLoad-state-dict summary:")
    print(f"  missing keys   : {len(missing)}")
    print(f"  unexpected keys: {len(unexpected)}")
    print(f"Device: {device} | inference_batch_size={inference_batch_size}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
