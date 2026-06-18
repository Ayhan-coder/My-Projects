import numpy as np
from scipy.io import wavfile

# Sample rate
FS = 48000

# Detected melody from extract_melody_final.py
frequencies = [234, 164, 117, 164, 234, 176, 117, 234, 141, 164, 117, 234, 141]
durations  = [0.352, 0.235, 0.619, 0.256, 0.160, 0.267, 0.320, 0.117, 1.259, 0.331, 0.576, 0.171, 0.768]

assert len(frequencies) == len(durations)

segments = []
for f, d in zip(frequencies, durations):
    n = int(np.round(d * FS))
    t = np.arange(n) / FS
    if f > 0:
        seg = np.sin(2 * np.pi * f * t)
    else:
        seg = np.zeros_like(t)
    # Apply simple fade in/out to reduce clicks
    if n > 20:
        fade_len = min( int(0.02 * FS), n // 4 )
        fade_in = np.linspace(0, 1, fade_len)
        fade_out = np.linspace(1, 0, fade_len)
        seg[:fade_len] *= fade_in
        seg[-fade_len:] *= fade_out
    segments.append(seg)

# Concatenate all segments
y = np.concatenate(segments) if segments else np.zeros(int(0.5 * FS))

# Normalize
peak = np.max(np.abs(y)) if y.size > 0 else 0
if peak > 0:
    y = y / peak * 0.9

# Convert to 16-bit PCM
y_int16 = np.int16(y * 32767)

wavfile.write("complex_recreate.wav", FS, y_int16)

print("Saved complex_recreate.wav")
print(f"  Duration: {len(y_int16) / FS:.3f} s")