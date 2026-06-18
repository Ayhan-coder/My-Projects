% cancel_music_mid_v15.m
% CMPE362 HW4 – Mid-Ground Hybrid Cancellation (v15)
%
% This version sits between v12 (Ultra Aggressive) and v13 (Softer).
% It aims for a better balance between suppression and naturalness.
%
% KEY STRATEGIES:
%   1. Phase Inversion: To subtract the main music signal.
%   2. Balanced Over-subtraction (alpha_os = 2.5): Between 1.8 and 3.5.
%   3. Spectral Floor (beta = 0.01): Between 0.001 and 0.02.
%   4. Moderate Gating: To reduce artifacts while killing noise.

clear; close all; clc;

fprintf('=== CMPE362 HW4 – Mid-Ground Hybrid Cancellation (v15) ===\n\n');

%% ─── 1. LOAD AUDIO FILES ───────────────────────────────────────────────────
mix_file   = 'cafe_sample.wav';
music_file = 'website_music.wav';

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

%% ─── 2. MID-GROUND SPECTRAL SUBTRACTION ───────────────────────────────────
win_len = 2048; hop_len = 512;
window = blackman(win_len, 'periodic');

[S_mix, f_bins, t_bins] = spectrogram(speech_canceled, window, win_len-hop_len, win_len, fs);
[S_mus, ~, ~] = spectrogram(mus, window, win_len-hop_len, win_len, fs);

mag_mix = abs(S_mix);
mag_mus = abs(S_mus) * k;

% Mid-ground parameters
alpha_os = 2.5;      % Balanced between 1.8 and 3.5
beta_floor = 0.01;    % Balanced between 0.001 and 0.02
p_pow = 2.2;          % Sharp but not extreme

% Calculate the mid-ground mask
mag_residue = max(mag_mix - alpha_os * mag_mus, beta_floor * mag_mix);
H_mid = (mag_residue ./ (mag_mix + eps)).^p_pow;

% Moderate gating
H_mid(H_mid < 0.03) = 0;

% Frequency cutoff
H_mid(f_bins > 3800, :) = H_mid(f_bins > 3800, :) * 0.1;

% Apply Mask
S_final = S_mix .* H_mid;

% Inverse STFT
speech_final = overlap_add_istft(S_final, win_len, hop_len);

%% ─── 3. POST-PROCESSING (Expander Gate) ────────────────────────────────────
envelope = abs(hilbert(speech_final));
env_smooth = filtfilt(ones(1, round(fs*0.02)), 1, envelope);
thresh = max(env_smooth) * 0.03; % 3% threshold
gate = (env_smooth > thresh);
speech_final = speech_final .* gate;

%% ─── 4. EQ & SAVE ───────────────────────────────────────────────────────────
% EQ: Moderate low boost
[b_ls, a_ls] = butter(1, 400 / (fs/2), 'low');
low_boost = filtfilt(b_ls, a_ls, speech_final);
speech_final = speech_final + (10^(6/20) - 1) * low_boost; % +6dB boost

speech_final = 0.95 * speech_final / (max(abs(speech_final)) + eps);
audiowrite('speech_v15_mid.wav', speech_final, fs);

fprintf('Saved mid-ground hybrid speech to: speech_v15_mid.wav\n');

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
