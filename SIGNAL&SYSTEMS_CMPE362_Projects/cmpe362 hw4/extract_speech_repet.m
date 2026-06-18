% extract_speech_repet.m
% CMPE362 HW4 – Speech/Music Separation using REPET-Matlab (zafarrafii)
%
% This script uses the REPET methods from:
%   https://github.com/zafarrafii/REPET-Matlab
%
% REPET assumption:
%   Background (music/ambience) is more repeating/consistent.
%   Foreground (speech) is more varying.
%
% Outputs:
%   music_repet.wav        – estimated repeating background
%   speech_repet.wav       – foreground = mixture - background
%   spectrogram_repet.png  – spectrogram comparison

clear; close all; clc;
fprintf('=== CMPE362 HW4 – REPET Speech/Music Separation ===\n\n');

%% ─── 0. ADD REPET TO PATH ───────────────────────────────────────────────────
repet_dir = fullfile(pwd, 'REPET-Matlab');
assert(isfile(fullfile(repet_dir, 'repet.m')), 'Missing REPET-Matlab/repet.m');
addpath(repet_dir);

%% ─── 1. LOAD AUDIO ─────────────────────────────────────────────────────────
[audio_signal, fs] = audioread('cafe_sample.wav');
if size(audio_signal,2) == 2
    audio_signal = mean(audio_signal,2);
end

audio_signal = double(audio_signal);

fprintf('Loaded cafe_sample.wav: %.2f s @ %d Hz\n\n', length(audio_signal)/fs, fs);

%% ─── 2. RUN REPET (choose method) ──────────────────────────────────────────
% Recommended to try:
%   - repet.sim      : works even when repetition is not strictly periodic
%   - repet.adaptive : works when repetition varies over time
%
% For cafe_sample.wav, background music is not perfectly periodic → SIM tends
% to be more robust.

method = 'sim';   % 'original' | 'extended' | 'adaptive' | 'sim' | 'simonline'

fprintf('Running repet.%s(...) ...\n', method);

switch lower(method)
    case 'original'
        bg = repet.original(audio_signal, fs);
    case 'extended'
        bg = repet.extended(audio_signal, fs);
    case 'adaptive'
        bg = repet.adaptive(audio_signal, fs);
    case 'sim'
        bg = repet.sim(audio_signal, fs);
    case 'simonline'
        bg = repet.simonline(audio_signal, fs);
    otherwise
        error('Unknown method: %s', method);
end

fg = audio_signal - bg;

%% ─── 3. NORMALIZE & SAVE ───────────────────────────────────────────────────
% Keep levels safe; normalization is per-channel (mono here).

bg_out = 0.95 * bg / (max(abs(bg)) + 1e-10);
fg_out = 0.95 * fg / (max(abs(fg)) + 1e-10);

audiowrite('music_repet.wav',  bg_out, fs);
audiowrite('speech_repet.wav', fg_out, fs);

fprintf('Saved:\n');
fprintf('  music_repet.wav   (background/music estimate)\n');
fprintf('  speech_repet.wav  (foreground/speech estimate)\n\n');

%% ─── 4. SPECTROGRAM COMPARISON ─────────────────────────────────────────────
window_length = 2048;
overlap = 1536;

figure('Name','REPET Separation','NumberTitle','off', 'Position',[50 50 1400 900]);

subplot(3,1,1);
spectrogram(audio_signal, hann(window_length), overlap, window_length, fs, 'yaxis');
title('Original');
colormap hot; colorbar; ylim([0 8]); caxis([-80 -20]);

subplot(3,1,2);
spectrogram(bg_out, hann(window_length), overlap, window_length, fs, 'yaxis');
title(sprintf('REPET background (music) – method: %s', method));
colormap hot; colorbar; ylim([0 8]); caxis([-80 -20]);

subplot(3,1,3);
spectrogram(fg_out, hann(window_length), overlap, window_length, fs, 'yaxis');
title('REPET foreground (speech) = mixture - background');
colormap hot; colorbar; ylim([0 8]); caxis([-80 -20]);

sgtitle('REPET-Matlab Separation – CMPE362 HW4', 'FontSize', 14, 'FontWeight', 'bold');

saveas(gcf, 'spectrogram_repet.png');
fprintf('Saved spectrogram_repet.png\n\n');

%% ─── 5. QUICK METRICS ──────────────────────────────────────────────────────
fprintf('=== RMS Metrics ===\n');
fprintf('Original RMS:  %.4f\n', rms(audio_signal));
fprintf('Music RMS:     %.4f\n', rms(bg_out));
fprintf('Speech RMS:    %.4f\n', rms(fg_out));

fprintf('\nTip: If speech still contains music, try method=''adaptive'' or ''simonline''.\n');
fprintf('=== Done ===\n');
