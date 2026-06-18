import numpy as np
from scipy.io import wavfile

# Target fundamental frequencies from report (autocorr-based where possible)
F0_MAP = {
    'low_pitch.wav': 120.0,   # Hz
    'high_pitch.wav': 323.0,  # Hz
    'whistle.wav':   1211.0,  # Hz  (measured from re-recorded whistle)
}

FADE_SEC = 0.02  # 20 ms fade in/out to avoid clicks
PEAK_LEVEL = 0.9

for fname, f0 in F0_MAP.items():
    fs, y_orig = wavfile.read(fname)

    # Ensure mono
    if y_orig.ndim == 2:
        y_orig = y_orig.mean(axis=1).astype(y_orig.dtype)

    duration = len(y_orig) / fs
    n = len(y_orig)
    t = np.arange(n) / fs

    # Generate pure sinusoid at f0
    y = np.sin(2 * np.pi * f0 * t).astype(np.float64)

    # Apply fade in/out
    fade_len = int(FADE_SEC * fs)
    fade_len = max(1, min(fade_len, n // 4))
    fade_in = np.linspace(0.0, 1.0, fade_len)
    fade_out = np.linspace(1.0, 0.0, fade_len)
    y[:fade_len] *= fade_in
    y[-fade_len:] *= fade_out

    # Normalize
    peak = np.max(np.abs(y))
    if peak > 0:
        y = y / peak * PEAK_LEVEL

    y_int16 = np.int16(np.clip(y, -1.0, 1.0) * 32767)

    out_name = fname.replace('.wav', '_recreate.wav')
    wavfile.write(out_name, fs, y_int16)

    print(f"Saved {out_name}: f0={f0} Hz, duration={duration:.3f} s, fs={fs}")
