% refine_speech_eq.m
% CMPE362 HW4 – Post-processing of speech extraction
%
% This script refines the extracted speech by:
%   1. Muting high-frequency voices (Low-Pass Filter @ 3500 Hz)
%   2. Boosting low-frequency voices (+6 dB Low-Shelf @ 400 Hz)

clear; close all; clc;

input_file = 'speech_v5_precise.wav';
output_file = 'speech_refined.wav';

if ~isfile(input_file)
    error('Input file %s not found. Run filter_audio_v5_precise.m first.', input_file);
end

[x, fs] = audioread(input_file);
nyq = fs / 2;

fprintf('Processing: %s (fs = %d Hz)\n', input_file, fs);

%% 1. Mute High Frequency Voices (LPF)
% Cutoff at 3500 Hz (approx. upper bound for clean speech intelligibility)
f_cut_high = 3500;
[b_lpf, a_lpf] = butter(4, f_cut_high / nyq, 'low');
x_lowpassed = filtfilt(b_lpf, a_lpf, x);

%% 2. Volume Up Low Frequency Voices (Low Shelf)
% Boost below 400 Hz (where fundamental frequencies of voices are)
f_cut_low = 400;
gain_db = 8; % Significant boost as requested
gain_lin = 10^(gain_db/20);

% Simple low-shelf filter design
% Using a first-order shelf for natural sound
theta = 2 * pi * f_cut_low / fs;
mu = gain_lin;
beta_s = (1 - (mu-1)/2 * sin(theta)) / (1 + (mu-1)/2 * sin(theta));
gamma = (1 + beta_s) / 2;
alpha = (1 - beta_s) / 2;

% Low shelf filter coefficients (b, a)
% H(z) = (gamma + alpha*z^-1) / (1 - beta_s*z^-1) -- This is a simple shelf
% But for simplicity and robustness, we can use built-in shelf or design it
% Let's use a 2nd order shelf approximation or just a 1st order boost.
% Or more simply: boost = x + (gain-1) * lowpass(x)
[b_ls, a_ls] = butter(1, f_cut_low / nyq, 'low');
x_low_only = filtfilt(b_ls, a_ls, x_lowpassed);
x_refined = x_lowpassed + (gain_lin - 1) * x_low_only;

%% 3. Normalize & Save
% Ensure no clipping and normalize to -1dB peak
x_refined = x_refined / (max(abs(x_refined)) + eps) * 0.89;

audiowrite(output_file, x_refined, fs);
fprintf('Saved refined speech to: %s\n', output_file);

%% 4. Visualization
figure('Name','Speech Refinement (EQ)','NumberTitle','off');
subplot(2,1,1);
spectrogram(x, hann(2048), 1024, 2048, fs, 'yaxis');
title('Before Refinement (speech\_v5\_precise.wav)');
ylim([0 10]); colormap hot; colorbar;

subplot(2,1,2);
spectrogram(x_refined, hann(2048), 1024, 2048, fs, 'yaxis');
title('After Refinement (Mute > 3.5k, Boost < 400 Hz)');
ylim([0 10]); colormap hot; colorbar;

saveas(gcf, 'refine_speech_spectrogram.png');
fprintf('Saved refine_speech_spectrogram.png\n');
