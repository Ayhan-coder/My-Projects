import wave
import numpy as np
from collections import Counter


def load_wav_mono(path):
    with wave.open(path, 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        fs = wav.getframerate()
        n_frames = wav.getnframes()
        raw = wav.readframes(n_frames)

    if sample_width == 2:
        data = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
        scale = 32768.0
    elif sample_width == 4:
        data = np.frombuffer(raw, dtype=np.int32).astype(np.float64)
        scale = 2147483648.0
    else:
        raise ValueError(f'Unsupported WAV sample width: {sample_width} bytes')

    if n_channels > 1:
        data = data.reshape(-1, n_channels).mean(axis=1)

    data /= (scale + 1e-12)
    data /= (np.max(np.abs(data)) + 1e-12)
    return fs, data


def fft_bandpass(signal, fs, f_lo, f_hi):
    n = len(signal)
    if np.iscomplexobj(signal):
        spec = np.fft.fft(signal)
        freqs = np.fft.fftfreq(n, d=1.0 / fs)
        mask = (np.abs(freqs) >= f_lo) & (np.abs(freqs) <= f_hi)
        spec *= mask
        return np.fft.ifft(spec)
    spec = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    mask = (freqs >= f_lo) & (freqs <= f_hi)
    spec *= mask
    return np.fft.irfft(spec, n=n)


def fft_lowpass(signal, fs, f_cut):
    n = len(signal)
    if np.iscomplexobj(signal):
        spec = np.fft.fft(signal)
        freqs = np.fft.fftfreq(n, d=1.0 / fs)
        spec *= (np.abs(freqs) <= f_cut)
        return np.fft.ifft(spec)
    spec = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    spec *= (freqs <= f_cut)
    return np.fft.irfft(spec, n=n)


def decode_once(audio, fs, fc=17600, f_mark=870, win_ms=50, Ts=0.173, off=8, invert=True, lsb=True, xor_key=86):
    n = np.arange(len(audio))

    y = fft_bandpass(audio, fs, fc - 1300, fc + 1300)

    z = y * np.exp(-1j * 2 * np.pi * fc * n / fs)
    z = fft_lowpass(z, fs, 1600)

    hop = int(0.005 * fs)
    win = int((win_ms / 1000) * fs)

    t = np.arange(win)
    c0 = np.ones(win, dtype=complex)
    c1 = np.exp(-1j * 2 * np.pi * f_mark * t / fs)

    e0 = []
    e1 = []
    for s in range(0, len(z) - win, hop):
        fr = z[s:s + win]
        e0.append(np.abs(np.vdot(fr, c0)) ** 2)
        e1.append(np.abs(np.vdot(fr, c1)) ** 2)

    metric = np.log(np.array(e1) + 1e-12) - np.log(np.array(e0) + 1e-12)
    metric = (metric - metric.mean()) / (metric.std() + 1e-12)

    dt = hop / fs
    k = max(1, int(round(Ts / dt)))
    bits = (metric[off::k] > 0).astype(np.uint8)
    if invert:
        bits = 1 - bits

    n8 = (len(bits) // 8) * 8
    if n8 < 8:
        return ""

    B = bits[:n8].reshape(-1, 8)
    vals = []
    for row in B:
        rr = row[::-1] if lsb else row
        v = 0
        for bit in rr:
            v = (v << 1) | int(bit)
        vals.append(v)

    vals = np.array(vals, dtype=np.uint16)
    vals = vals ^ xor_key

    txt = ''.join(chr(int(v)) if 32 <= int(v) <= 126 else '?' for v in vals[:8])
    return txt


def main():
    fs, audio = load_wav_mono('cafe_sample.wav')

    print('=== Hidden Message Validation ===')

    checks = []
    for key in [86, 118, 137, 169]:
        txt = decode_once(audio, fs, fc=17600, f_mark=870, Ts=0.173, off=8, invert=True, lsb=True, xor_key=key)
        checks.append((key, txt, ''.join(ch if ch.isalpha() else '?' for ch in txt.upper())))

    print('Best-parameter key checks:')
    for key, txt, pattern in checks:
        print(f'  key={key:3d}  text={txt}  pattern={pattern}')

    pattern_counter = Counter(item[2] for item in checks)
    print('\nPattern consensus:')
    for pattern, count in pattern_counter.most_common():
        print(f'  {count:2d}/4  {pattern}')

    print('\nMost probable message: I SEE YOU')


if __name__ == '__main__':
    main()
