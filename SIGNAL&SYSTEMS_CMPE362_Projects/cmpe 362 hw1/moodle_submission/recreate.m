% recreate.m
% CMPE 362 - Homework 1
% Name: Ali Ayhan Günder
% Date: February 22, 2026
% Recreate melody from frequencies

clear; close all;

fs = 48000; % Sampling rate

% Frequencies and durations from inspection
frequencies = [234, 164, 117, 164, 234, 176, 117, 234, 141, 164, 117, 234, 141];
durations  = [0.352, 0.235, 0.619, 0.256, 0.160, 0.267, 0.320, 0.117, 1.259, 0.331, 0.576, 0.171, 0.768];

if numel(frequencies) ~= numel(durations)
    error('Mismatch in notes data');
end

% Synthesize melody loop
segments = {};
for i = 1:numel(frequencies)
    f = frequencies(i);
    d = durations(i);
    
    N = round(d * fs);  % num samples
    t = (0:N-1) / fs;   % time vector

    if f > 0
        seg = sin(2*pi*f*t); % sine wave
    else
        seg = zeros(size(t));
    end

    % Apply fading to prevent clicks
    fadeLen = min(round(0.02*fs), floor(N/4));
    if fadeLen > 1
        fadeIn  = linspace(0, 1, fadeLen);
        fadeOut = linspace(1, 0, fadeLen);
        seg(1:fadeLen)       = seg(1:fadeLen)       .* fadeIn;
        seg(end-fadeLen+1:end) = seg(end-fadeLen+1:end) .* fadeOut;
    end

    segments{end+1} = seg(:); %#ok<SAGROW>
end

% Concatenate all segments
if isempty(segments)
    y = zeros(round(0.5*fs),1);
else
    y = vertcat(segments{:});
end

% Normalize
y = y(:);
peak = max(abs(y));
if peak > 0
    y = 0.9 * y / peak;
end

audiowrite('complex_recreate.wav', y, fs);
fprintf('Saved complex_recreate.wav\n');

%% Comparison Plot
[y_orig, fs_orig] = audioread('complex.wav');
if size(y_orig,2) > 1, y_orig = mean(y_orig, 2); end

figure('Position', [100, 100, 1200, 500]);

% Left: Original
subplot(1, 2, 1);
spectrogram(y_orig, hamming(2048), 1536, 4096, fs_orig, 'yaxis');
title('Original');
colormap jet;
ylim([0 2500]); % Zoom to see melody detail

% Right: Recreated
subplot(1, 2, 2);
spectrogram(y, hamming(2048), 1536, 4096, fs, 'yaxis');
title('Recreated');
colormap jet;
ylim([0 2500]); % Zoom to match scale

saveas(gcf, 'complex_comparison.png');
fprintf('Saved complex_comparison.png\n');
