% cancel_music_phase.m
% CMPE362 HW4 – Phase Inversion Cancellation
%
% This script implements "Phase Inversion" by subtracting the separated 
% music estimate from the original mixture.
%
% $Speech = Mixture - (k * Music_{separated})$
%
% Where 'k' is an adaptively calculated gain factor to ensure perfect 
% cancellation of the music signal.

clear; close all; clc;

fprintf('=== CMPE362 HW4 – Phase Inversion Cancellation ===\n\n');

%% ─── 1. LOAD AUDIO FILES ───────────────────────────────────────────────────
mix_file   = 'cafe_sample.wav';
music_file = 'website_music.wav'; % Using the most successful music separation

if ~isfile(mix_file) || ~isfile(music_file)
    error('Required files not found. Run compare_website_split.m first.');
end

[mix_raw, fs_mix] = audioread(mix_file);
[mus_raw, fs_mus] = audioread(music_file);

% Ensure same sample rate
if fs_mix ~= fs_mus
    fprintf('Resampling music from %d to %d Hz...\n', fs_mus, fs_mix);
    mus_raw = resample(mus_raw, fs_mix, fs_mus);
end

% Convert to mono for alignment and subtraction
mix = mean(mix_raw, 2);
mus = mean(mus_raw, 2);

% Match lengths
len = min(length(mix), length(mus));
mix = mix(1:len);
mus = mus(1:len);

fprintf('Loaded mixture and music reference (%.2f seconds).\n', len/fs_mix);

%% ─── 2. ADAPTIVE ALIGNMENT & SCALING ───────────────────────────────────────
% Find the optimal time-alignment (lag) using cross-correlation
fprintf('Aligning signals... ');
[c, lags] = xcorr(mix, mus, round(0.1 * fs_mix)); % 100ms max lag
[~, idx] = max(abs(c));
best_lag = lags(idx);
fprintf('Best lag: %d samples.\n', best_lag);

% Shift music to match mixture
if best_lag > 0
    mus = [zeros(best_lag, 1); mus(1:end-best_lag)];
elseif best_lag < 0
    mus = [mus(-best_lag+1:end); zeros(-best_lag, 1)];
end

% Find optimal gain 'k' using Least Squares (minimizes (mix - k*mus)^2)
% k = (mus' * mix) / (mus' * mus)
k = (mus' * mix) / (mus' * mus + eps);
fprintf('Calculated optimal cancellation gain: k = %.4f\n', k);

%% ─── 3. SUBTRACTION (Phase Inversion) ──────────────────────────────────────
% Perform the subtraction: Mixture - (Scaled Music)
% This is equivalent to "Multiplying by reverse phase and adding"
speech_raw = mix - (k * mus);

%% ─── 4. REFINEMENT (EQ) ────────────────────────────────────────────────────
% Apply the previously requested EQ: LPF for highs, Boost for lows
nyq = fs_mix / 2;
[b_lpf, a_lpf] = butter(4, 3500 / nyq, 'low');
[b_ls, a_ls]   = butter(1, 400 / nyq, 'low');

speech_filt = filtfilt(b_lpf, a_lpf, speech_raw);
low_boost   = filtfilt(b_ls, a_ls, speech_filt);
speech_out  = speech_filt + (10^(8/20) - 1) * low_boost; % +8dB boost

%% ─── 5. NORMALIZE & SAVE ───────────────────────────────────────────────────
speech_out = 0.95 * speech_out / (max(abs(speech_out)) + eps);
audiowrite('speech_cancellation.wav', speech_out, fs_mix);

fprintf('Saved result to: speech_cancellation.wav\n');

%% ─── 6. VISUALIZATION ──────────────────────────────────────────────────────
figure('Name','Phase Inversion Cancellation','NumberTitle','off');

subplot(3,1,1);
spectrogram(mix, hann(2048), 1024, 2048, fs_mix, 'yaxis');
title('Original Mixture (Cafe Sample)');
ylim([0 10]); colormap hot; colorbar;

subplot(3,1,2);
spectrogram(mus * k, hann(2048), 1024, 2048, fs_mix, 'yaxis');
title('Scaled Music Estimate (Subtrahend)');
ylim([0 10]); colormap hot; colorbar;

subplot(3,1,3);
spectrogram(speech_out, hann(2048), 1024, 2048, fs_mix, 'yaxis');
title('Resulting Speech (Cancellation Result)');
ylim([0 10]); colormap hot; colorbar;

saveas(gcf, 'phase_cancellation_spectrogram.png');
fprintf('Saved phase_cancellation_spectrogram.png\n');
fprintf('\nDone.\n');
