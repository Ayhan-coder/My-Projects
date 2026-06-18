% speech_filter.m
% CMPE362 HW4 – Speech Filter (Ultra-Aggressive Hybrid Cancellation)
%
% This is the ultimate "music killer". It combines:
%   1. Phase Inversion: To subtract the main music signal.
%   2. Over-subtraction: To aggressively remove music residue.
%   3. Spectral Gating: To zero out non-speech frequencies.
%   4. Downward Expander: To mute the silence between words.

clear; close all; clc;

fprintf('=== CMPE362 HW4 – Speech Filter (Ultra-Aggressive) ===\n\n');

% Resolve paths relative to this script so it works from any MATLAB cwd.
this_file = mfilename('fullpath');
best_dir = fileparts(this_file);
root_dir = fileparts(best_dir);

%% ─── 1. LOAD AUDIO FILES ───────────────────────────────────────────────────
mix_file   = fullfile(root_dir, 'cafe_sample.wav');
music_file = fullfile(root_dir, 'website_music.wav');

if ~isfile(mix_file) || ~isfile(music_file)
    error('Required files not found. Run compare_website_split.m first.');
end

[mix_raw, fs] = audioread(mix_file);
[mus_raw, ~]  = audioread(music_file);

% Convert to mono
mix = mean(mix_raw, 2);
mus = mean(mus_raw, 2);

% Alignment and Scaling (Phase Inversion)
len = min(length(mix), length(mus));
mix = mix(1:len); mus = mus(1:len);

[c, lags] = xcorr(mix, mus, round(0.1 * fs));
[~, idx] = max(abs(c));
best_lag = lags(idx);

if best_lag > 0
    mus = [zeros(best_lag, 1); mus(1:end-best_lag)];
elseif best_lag < 0
    mus = [mus(-best_lag+1:end); zeros(-best_lag, 1)];
end

k = (mus' * mix) / (mus' * mus + eps);
speech_canceled = mix - (k * mus);

fprintf('Phase cancellation complete (lag: %d, k: %.4f).\n', best_lag, k);

%% ─── 2. AGGRESSIVE SPECTRAL SUBTRACTION ─────────────────────────────────────
% Treat the phase-canceled signal as a "noisy" speech signal.
% Treat the scaled music as the "noise" to be over-subtracted.

win_len = 2048; hop_len = 512;
window = blackman(win_len, 'periodic');

[S_mix, f_bins, t_bins] = spectrogram(speech_canceled, window, win_len-hop_len, win_len, fs);
[S_mus, ~, ~] = spectrogram(mus, window, win_len-hop_len, win_len, fs);

mag_mix = abs(S_mix);
mag_mus = abs(S_mus) * k; % Use the scaled music magnitude

% Over-subtraction parameters
alpha_os = 3.5; % Ultra aggressive subtraction
beta_floor = 0.001; % Very low floor

% Calculate the ultra-aggressive mask
mag_residue = max(mag_mix - alpha_os * mag_mus, beta_floor * mag_mix);
H_ultra = (mag_residue ./ (mag_mix + eps)).^2.5; % High power for sharp cut

% Hard gate: if residue is less than 5% of original mix, kill it
H_ultra(H_ultra < 0.05) = 0;

% Mute highs above 3.2kHz where accordion is piercing
H_ultra(f_bins > 3200, :) = 0;

% Apply Mask
S_final = S_mix .* H_ultra;

% Inverse STFT
speech_final = overlap_add_istft(S_final, win_len, hop_len);

%% ─── 3. POST-PROCESSING (Expander Gate) ────────────────────────────────────
% Apply a temporal downward expander to mute gaps between speech
envelope = abs(hilbert(speech_final));
env_smooth = filtfilt(ones(1, round(fs*0.02)), 1, envelope); % 20ms smoothing
thresh = max(env_smooth) * 0.05; % 5% threshold
gate = (env_smooth > thresh);
speech_final = speech_final .* gate;

%% ─── 4. EQ & SAVE ───────────────────────────────────────────────────────────
% EQ: Low boost for speech body
[b_ls, a_ls] = butter(1, 400 / (fs/2), 'low');
low_boost = filtfilt(b_ls, a_ls, speech_final);
speech_final = speech_final + (10^(8/20) - 1) * low_boost;

speech_final = 0.95 * speech_final / (max(abs(speech_final)) + eps);

out_file = fullfile(best_dir, 'speech_filtered.wav');
audiowrite(out_file, speech_final, fs);

fprintf('Saved ultra-aggressive speech to: %s\n', out_file);

%% ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────
function recon = overlap_add_istft(S, win_len, hop_len)
    [nfreq, ntime] = size(S);
    nfft = (nfreq - 1) * 2;
    sig_len = (ntime - 1) * hop_len + win_len;
    recon = zeros(sig_len, 1);
    window = blackman(win_len, 'periodic'); 
    for frame = 1:ntime
        X = S(:, frame);
        X = [X; conj(X(end-1:-1:2))];
        x_frame = real(ifft(X, nfft));
        x_frame = x_frame(1:win_len) .* window;
        start_idx = (frame - 1) * hop_len + 1;
        end_idx = start_idx + win_len - 1;
        recon(start_idx:end_idx) = recon(start_idx:end_idx) + x_frame;
    end
end
