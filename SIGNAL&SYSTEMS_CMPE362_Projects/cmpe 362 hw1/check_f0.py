from scipy.io import wavfile
import numpy as np

files = {'low_pitch.wav': (50, 500), 'high_pitch.wav': (100, 1000)}

for fname, (fmin, fmax) in files.items():
    fs, y = wavfile.read(fname)
    if y.ndim == 2:
        y = y.mean(axis=1)
    y = y.astype(np.float64)
    N = len(y)
    seg = y[N//4:3*N//4]
    seg -= seg.mean()

    fft_size = 65536
    spec = np.fft.rfft(seg, n=fft_size)
    freqs = np.fft.rfftfreq(fft_size, 1.0/fs)
    mag = np.abs(spec)
    band = (freqs >= fmin) & (freqs <= fmax)
    fft_f0 = freqs[band][np.argmax(mag[band])]

    r = np.correlate(seg, seg, mode='full')
    mid = len(r)//2
    r_pos = r[mid:]
    min_lag = int(fs / fmax)
    max_lag = int(fs / fmin)
    sub = r_pos[min_lag:max_lag]
    lag = min_lag + np.argmax(sub)
    ac_f0 = fs / lag

    print(f'{fname}: FFT={fft_f0:.1f} Hz, AutoCorr={ac_f0:.1f} Hz')
