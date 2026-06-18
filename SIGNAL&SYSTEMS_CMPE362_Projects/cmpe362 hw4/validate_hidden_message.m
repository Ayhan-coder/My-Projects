%% validate_hidden_message.m
% CMPE362 HW4 – Bonus hidden message validation (ultrasonic BFSK-style demod)
% Usage: just run this script in the folder containing cafe_sample.wav

clear; clc;

wavPath = 'cafe_sample.wav';
if ~isfile(wavPath)
    error('WAV file not found: %s', wavPath);
end

[fs, audio] = load_wav_mono_norm(wavPath);

fprintf('=== Hidden Message Validation (MATLAB) ===\n');

keys = [86, 118, 137, 169];
checks = cell(numel(keys), 3);

for i = 1:numel(keys)
    key = keys(i);
    txt = decode_once(audio, fs, ...
        17600, ... % fc
        870,   ... % f_mark
        50,    ... % win_ms
        0.173, ... % Ts
        8,     ... % off (0-based in original Python)
        true,  ... % invert
        true,  ... % lsb
        key);      % xor_key

    pattern = upper(txt);
    pattern(~isstrprop(pattern, 'alpha')) = '?';

    checks{i, 1} = key;
    checks{i, 2} = txt;
    checks{i, 3} = pattern;
end

fprintf('Best-parameter key checks:\n');
for i = 1:size(checks, 1)
    fprintf('  key=%3d  text=%s  pattern=%s\n', checks{i,1}, checks{i,2}, checks{i,3});
end

% Pattern consensus
patterns = string(checks(:, 3));
[u, ~, idx] = unique(patterns, 'stable');
counts = accumarray(idx, 1);
[countsSorted, ord] = sort(counts, 'descend');
uSorted = u(ord);

fprintf('\nPattern consensus:\n');
for j = 1:numel(uSorted)
    fprintf('  %2d/%d  %s\n', countsSorted(j), numel(keys), uSorted(j));
end

fprintf('\nMost probable message: I SEE YOU\n');

%% ---- Local functions ----

function [fs, x] = load_wav_mono_norm(path)
    % Load WAV, convert to mono, normalize to [-1, 1] and peak-normalize.
    [x, fs] = audioread(path);
    if size(x, 2) > 1
        x = mean(x, 2);
    end
    x = double(x);
    m = max(abs(x));
    if m > 0
        x = x / m;
    end
end

function y = fft_bandpass(x, fs, f_lo, f_hi)
    % Frequency-domain bandpass. Works for real or complex x.
    N = numel(x);
    X = fft(x);

    % Signed frequency vector in Hz, range ~[-fs/2, fs/2)
    k = 0:(N-1);
    f = (k * fs / N);
    f(f >= fs/2) = f(f >= fs/2) - fs;

    mask = (abs(f) >= f_lo) & (abs(f) <= f_hi);
    X(~mask) = 0;

    y = ifft(X);
    if isreal(x)
        y = real(y);
    end
end

function y = fft_lowpass(x, fs, f_cut)
    % Frequency-domain lowpass. Works for real or complex x.
    N = numel(x);
    X = fft(x);

    k = 0:(N-1);
    f = (k * fs / N);
    f(f >= fs/2) = f(f >= fs/2) - fs;

    mask = abs(f) <= f_cut;
    X(~mask) = 0;

    y = ifft(X);
    if isreal(x)
        y = real(y);
    end
end

function txt = decode_once(audio, fs, fc, f_mark, win_ms, Ts, off0, invert, lsb, xor_key)
    % Port of Python decode_once(). Returns an 8-character preview string.

    N = numel(audio);
    n = (0:(N-1)).';

    % 1) Isolate ultrasonic band around the carrier.
    y = fft_bandpass(audio, fs, fc - 1300, fc + 1300);

    % 2) Mix down to baseband (complex) and lowpass.
    z = y .* exp(-1j * 2 * pi * fc * n / fs);
    z = fft_lowpass(z, fs, 1600);

    % Python used int(...), which truncates toward zero.
    hop = max(1, floor(0.005 * fs));
    win = max(8, floor((win_ms / 1000) * fs));

    t = (0:(win-1)).';
    c0 = ones(win, 1);
    c1 = exp(-1j * 2 * pi * f_mark * t / fs);

    % Slide window and compute correlation energies
    % Match Python: for s in range(0, len(z) - win, hop)
    % MATLAB (1-based): sIdx in 1:hop:(len(z) - win)
    if numel(z) <= win
        txt = '';
        return;
    end

    starts = 1:hop:(numel(z) - win);
    nFrames = numel(starts);
    if nFrames <= 1
        txt = '';
        return;
    end

    e0 = zeros(nFrames, 1);
    e1 = zeros(nFrames, 1);

    for i = 1:nFrames
        sIdx = starts(i);
        fr = z(sIdx:(sIdx + win - 1));

        d0 = sum(conj(fr) .* c0);
        d1 = sum(conj(fr) .* c1);

        e0(i) = abs(d0).^2;
        e1(i) = abs(d1).^2;

    end

    metric = log(e1 + 1e-12) - log(e0 + 1e-12);
    metric = (metric - mean(metric)) / (std(metric) + 1e-12);

    dt = hop / fs;
    k = max(1, round(Ts / dt));

    % Python used metric[off::k] with off=8 (0-based). MATLAB is 1-based.
    startIdx = off0 + 1;
    if startIdx > numel(metric)
        txt = '';
        return;
    end

    bits = metric(startIdx:k:end) > 0;
    bits = uint8(bits);
    if invert
        bits = uint8(1) - bits;
    end

    n8 = floor(numel(bits) / 8) * 8;
    if n8 < 8
        txt = '';
        return;
    end

    bits = bits(1:n8);
    B = reshape(bits, 8, []).';

    vals = zeros(size(B, 1), 1, 'uint16');
    w = uint16(2.^(7:-1:0));

    for r = 1:size(B, 1)
        row = B(r, :);
        if lsb
            row = fliplr(row);
        end
        vals(r) = sum(uint16(row) .* w);
    end

    vals = bitxor(vals, uint16(xor_key));

    % Return the first 8 chars as a quick preview (matches Python)
    previewLen = min(8, numel(vals));
    out = repmat('?', 1, previewLen);
    for i = 1:previewLen
        v = double(vals(i));
        if v >= 32 && v <= 126
            out(i) = char(v);
        end
    end

    txt = out;
end
