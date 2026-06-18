import numpy as np
from scipy.io import wavfile

fs, y = wavfile.read('whistle.wav')

if y.ndim == 2:
    y = y.mean(axis=1)

# Use a centered segment to avoid possible fade-in/out noise
N = len(y)
start = N // 4
end = 3 * N // 4
seg = y[start:end].astype(np.float64)
seg -= seg.mean()

# FFT-based estimate (spectrogram-style)
fft_size = 65536
spec = np.fft.rfft(seg, n=fft_size)
mag = np.abs(spec)
freqs = np.fft.rfftfreq(fft_size, 1.0/fs)

# Search in a reasonable whistle band (500 Hz .. 4000 Hz)
band = (freqs >= 500) & (freqs <= 4000)
peak_idx = np.argmax(mag[band])
fft_f0 = freqs[band][peak_idx]

# Autocorrelation-based estimate
r = np.correlate(seg, seg, mode='full')
mid = len(r)//2
r_pos = r[mid:]

# Ignore very small lags; search between 0.2 ms and 10 ms
min_lag = int(0.0002 * fs)
max_lag = int(0.010 * fs)
sub = r_pos[min_lag:max_lag]
sub_idx = np.argmax(sub)
lag_samples = min_lag + sub_idx
ac_f0 = fs / lag_samples

print(f"fs = {fs} Hz")
print(f"Whistle duration: {N/fs:.3f} s")
print(f"FFT-based f0  ≈ {fft_f0:.1f} Hz")
print(f"Autocorr f0   ≈ {ac_f0:.1f} Hz")
