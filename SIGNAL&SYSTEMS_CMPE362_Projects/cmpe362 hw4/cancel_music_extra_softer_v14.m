% cancel_music_extra_softer_v14.m
% CMPE362 HW4 – Extra Softer Hybrid Cancellation (v14)
%
% This version is designed for maximum speech naturalness and clarity.
% It prioritizes the vocal quality over complete music removal.
%
% KEY STRATEGIES:
%   1. Light Over-subtraction (alpha_os = 1.3): Minimal interference.
%   2. Higher Spectral Floor (beta = 0.05): Preserves "air" and texture.
%   3. Smooth STFT Window (Hann): Reduces processing artifacts.
%   4. Minimal Gating: To prevent word-clipping and robotic silence.

clear; close all; clc;

fprintf('=== CMPE362 HW4 – Extra Softer Hybrid Cancellation (v14) ===\n\n');

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

%% ─── 2. GENTLE SPECTRAL SUBTRACTION ───────────────────────────────────────
win_len = 2048; hop_len = 512;
window = hann(win_len, 'periodic');

[S_mix, f_bins, t_bins] = spectrogram(speech_canceled, window, win_len-hop_len, win_len, fs);
[S_mus, ~, ~] = spectrogram(mus, window, win_len-hop_len, win_len, fs);

mag_mix = abs(S_mix);
mag_mus = abs(S_mus) * k;

% "Extra Soft" parameters
alpha_os = 1.3;      % Reduced from 1.8 (very light)
beta_floor = 0.05;    % Increased from 0.02 (preserves natural texture)
p_pow = 1.2;          % Very smooth mask curvature

% Calculate the gentle mask
mag_residue = max(mag_mix - alpha_os * mag_mus, beta_floor * mag_mix);
H_extra_soft = (mag_residue ./ (mag_mix + eps)).^p_pow;

% Very light gating
H_extra_soft(H_extra_soft < 0.01) = 0.01; 

% Relaxed high frequency handling
H_extra_soft(f_bins > 5000, :) = H_extra_soft(f_bins > 5000, :) * 0.5;

% Apply Mask
S_final = S_mix .* H_extra_soft;

% Inverse STFT
speech_final = overlap_add_istft(S_final, win_len, hop_len);

%% ─── 3. BALANCED POST-PROCESSING ──────────────────────────────────────────
% No hard temporal gate (to preserve breaths and word endings)
% Minimal EQ adjustment
[b_ls, a_ls] = butter(1, 400 / (fs/2), 'low');
low_boost = filtfilt(b_ls, a_ls, speech_final);
speech_final = speech_final + (10^(3/20) - 1) * low_boost; % +3dB (very light)

speech_final = 0.95 * speech_final / (max(abs(speech_final)) + eps);
audiowrite('speech_v14_extra_softer.wav', speech_final, fs);

fprintf('Saved extra softer hybrid speech to: speech_v14_extra_softer.wav\n');

%% ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────
function recon = overlap_add_istft(S, win_len, hop_len)
    [nfreq, ntime] = size(S);
    nfft = (nfreq - 1) * 2;
    sig_len = (ntime - 1) * hop_len + win_len;
    recon = zeros(sig_len, 1);
    window = hann(win_len, 'periodic'); 
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
