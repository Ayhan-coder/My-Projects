% recreate.m
% CMPE 362 - Homework 1
% Recreate the melody in complex.wav using pure sinusoids and
% save it as complex_recreate.wav.

clear; close all;

fs = 48000;  % sampling rate (Hz)

% Frequencies and durations extracted from complex.wav
% (from Python spectral peak detection / visual inspection)
frequencies = [234, 164, 117, 164, 234, 176, 117, 234, 141, 164, 117, 234, 141];
durations  = [0.352, 0.235, 0.619, 0.256, 0.160, 0.267, 0.320, 0.117, 1.259, 0.331, 0.576, 0.171, 0.768];

assert(numel(frequencies) == numel(durations), 'freq and duration arrays must match');

% Build signal by concatenating sinusoids
segments = {};
for i = 1:numel(frequencies)
    f = frequencies(i);
    d = durations(i);
    N = round(d * fs);
    t = (0:N-1) / fs;

    if f > 0
        seg = sin(2*pi*f*t);
    else
        seg = zeros(size(t));
    end

    % Simple fade in/out to avoid clicks
    fadeLen = min(round(0.02*fs), floor(N/4));
    if fadeLen > 1
        fadeIn  = linspace(0, 1, fadeLen);
        fadeOut = linspace(1, 0, fadeLen);
        seg(1:fadeLen)       = seg(1:fadeLen)       .* fadeIn;
        seg(end-fadeLen+1:end) = seg(end-fadeLen+1:end) .* fadeOut;
    end

    segments{end+1} = seg(:); %#ok<SAGROW>
end

if isempty(segments)
    y = zeros(round(0.5*fs),1);
else
    y = vertcat(segments{:});
end

% Normalize to avoid clipping
y = y(:);
peak = max(abs(y));
if peak > 0
    y = 0.9 * y / peak;
end

% Save as WAV
audiowrite('complex_recreate.wav', y, fs);

fprintf('Saved complex_recreate.wav (duration = %.3f s)\n', numel(y)/fs);
