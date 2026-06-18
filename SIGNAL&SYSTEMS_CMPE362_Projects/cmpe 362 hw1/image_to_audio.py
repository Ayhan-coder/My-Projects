"""
Convert a drawn spectrogram PNG into audio using inverse STFT.
Input : drawed_complex_spectrogram.png
Output: complex_recreate.wav
"""
import numpy as np
from PIL import Image
from scipy.io import wavfile
from scipy.signal import resample

# ── parameters ────────────────────────────────────────────────────────────────
FS          = 48000
DURATION    = 6.0          # seconds of output audio
FMAX        = 8000         # Hz shown on image top → maps to this frequency
NFFT        = 2048         # FFT size  (freq resolution = FS/NFFT ≈ 23 Hz)
HOP         = 512          # hop size
N_FRAMES    = int((DURATION * FS - NFFT) / HOP) + 1
FMAX_BIN    = int(FMAX / (FS / 2) * (NFFT // 2 + 1)) + 1
GRIFFIN_LIM = 60           # Griffin-Lim iterations for better phase reconstruction

# ── load + preprocess image ───────────────────────────────────────────────────
img  = Image.open("drawed_complex_spectrogram.png").convert("RGB")
arr  = np.array(img, dtype=np.float32)   # shape: (H, W, 3)

# Convert RGB → perceived brightness
gray = 0.299*arr[:,:,0] + 0.587*arr[:,:,1] + 0.114*arr[:,:,2]  # (H, W)

# Normalize to [0, 1]
gray = gray / 255.0

# Background is black (0.0), drawn lines are bright (>0.0)
# Hard threshold: ignore faint background noise (< 5% energy)
gray[gray < 0.05] = 0.0

# Boost contrast: raise remaining values to make drawn lines stand out more
gray = np.clip(gray * 1.5, 0.0, 1.0)

# The image has freq on vertical axis:
#   row 0   = TOP    = HIGH freq
#   row H-1 = BOTTOM = LOW  freq   (standard spectrogram convention)
# We want canvas[freq_bin, time_frame] with freq_bin=0 = DC
# So flip vertically so row 0 = low freq
gray = np.flipud(gray)   # now row 0 = low freq, row H-1 = high freq

# Resize to [FMAX_BIN x N_FRAMES]
pil_resized = Image.fromarray((gray * 255).astype(np.uint8))
pil_resized = pil_resized.resize((N_FRAMES, FMAX_BIN), Image.LANCZOS)
canvas = np.array(pil_resized, dtype=np.float32) / 255.0  # (FMAX_BIN, N_FRAMES)

print(f"Canvas: {canvas.shape}  |  FMAX_BIN={FMAX_BIN}  N_FRAMES={N_FRAMES}")
print(f"Pixel energy range: {canvas.min():.3f} – {canvas.max():.3f}")

# ── build full (real-signal) magnitude spectrogram ───────────────────────────
n_bins    = NFFT // 2 + 1
full_mag  = np.zeros((n_bins, N_FRAMES), dtype=np.float32)
full_mag[:FMAX_BIN, :] = canvas

# ── Griffin-Lim phase reconstruction ─────────────────────────────────────────
def istft(S, hop, nfft):
    """Overlap-add inverse STFT."""
    win          = np.hanning(nfft)
    n_fr         = S.shape[1]
    total        = (n_fr - 1) * hop + nfft
    audio        = np.zeros(total)
    win_sq_sum   = np.zeros(total)
    for fr in range(n_fr):
        # Mirror for real output
        col      = S[:, fr]
        col_full = np.concatenate([col, np.conj(col[-2:0:-1])])
        frame    = np.real(np.fft.ifft(col_full))
        idx      = fr * hop
        audio   [idx:idx+nfft] += frame * win
        win_sq_sum[idx:idx+nfft] += win**2
    win_sq_sum = np.maximum(win_sq_sum, 1e-8)
    return audio / win_sq_sum

def stft(x, hop, nfft):
    """STFT of signal x."""
    win    = np.hanning(nfft)
    n_fr   = (len(x) - nfft) // hop + 1
    n_bins = nfft // 2 + 1
    S      = np.zeros((n_bins, n_fr), dtype=complex)
    for fr in range(n_fr):
        frame         = x[fr*hop : fr*hop+nfft] * win
        S[:, fr]      = np.fft.fft(frame, nfft)[:n_bins]
    return S

print(f"Running Griffin-Lim ({GRIFFIN_LIM} iterations)...")

# Initial random phase
angles = np.exp(1j * 2 * np.pi * np.random.rand(*full_mag.shape))
S      = full_mag * angles

for it in range(GRIFFIN_LIM):
    audio   = istft(S, HOP, NFFT)
    S       = stft(audio, HOP, NFFT)
    # Re-impose drawn magnitude
    angle   = np.angle(S)
    S       = full_mag * np.exp(1j * angle)
    if (it + 1) % 15 == 0:
        print(f"  iter {it+1}/{GRIFFIN_LIM}")

# Final inverse
audio = istft(S, HOP, NFFT)

# Trim edge artifacts and normalise
trim  = NFFT
audio = audio[trim:-trim]
peak  = np.max(np.abs(audio))
if peak > 0:
    audio = audio / peak * 0.85

# Save
audio_i16 = (audio * 32767).astype(np.int16)
wavfile.write("complex_recreate.wav", FS, audio_i16)

actual_dur = len(audio) / FS
print(f"\nSaved complex_recreate.wav  ({actual_dur:.2f} s  @ {FS} Hz)")
