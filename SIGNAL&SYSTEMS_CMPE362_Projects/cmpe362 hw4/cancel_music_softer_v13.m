% cancel_music_softer_v13.m
% CMPE362 HW4 – Softer Hybrid Cancellation (v13)
%
% This version aims for a "softer" result, balancing music suppression 
% with speech naturalness. It uses:
%   1. Phase Inversion: To subtract the main music signal.
%   2. Moderate Over-subtraction: To remove residue without heavy artifacts.
%   3. Gentle Spectral Gating: To preserve speech while muting noise.
%   4. Relaxed EQ: For a more open and detailed vocal sound.

clear; close all; clc;

fprintf('=== CMPE362 HW4 – Softer Hybrid Cancellation (v13) ===\n\n');

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

%% ─── 2. MODERATE SPECTRAL SUBTRACTION ─────────────────────────────────────
win_len = 2048; hop_len = 512;
window = hann(win_len, 'periodic'); % Hann is smoother than Blackman

[S_mix, f_bins, t_bins] = spectrogram(speech_canceled, window, win_len-hop_len, win_len, fs);
[S_mus, ~, ~] = spectrogram(mus, window, win_len-hop_len, win_len, fs);

mag_mix = abs(S_mix);
mag_mus = abs(S_mus) * k;

% Moderate parameters for a "softer" feel
alpha_os = 1.8;      % Significantly reduced from 3.5
beta_floor = 0.02;    % Increased from 0.001 to maintain naturalness
p_pow = 1.8;          % Smoother mask power

% Calculate the moderate mask
mag_residue = max(mag_mix - alpha_os * mag_mus, beta_floor * mag_mix);
H_softer = (mag_residue ./ (mag_mix + eps)).^p_pow;

% Gentle gate: if residue is less than 2% of original mix, kill it
H_softer(H_softer < 0.02) = 0;

% More relaxed frequency cutoff (higher limit for clearer consonants)
H_softer(f_bins > 4200, :) = H_softer(f_bins > 4200, :) * 0.2; % 80% suppression instead of 100%

% Apply Mask
S_final = S_mix .* H_softer;

% Inverse STFT
speech_final = overlap_add_istft(S_final, win_len, hop_len);

%% ─── 3. POST-PROCESSING (Gentle Gate) ──────────────────────────────────────
envelope = abs(hilbert(speech_final));
env_smooth = filtfilt(ones(1, round(fs*0.03)), 1, envelope); % Smoother (30ms)
thresh = max(env_smooth) * 0.02; % 2% threshold (gentler)
gate = (env_smooth > thresh);
speech_final = speech_final .* gate;

%% ─── 4. BALANCED EQ & SAVE ──────────────────────────────────────────────────
% EQ: Balanced low boost
[b_ls, a_ls] = butter(1, 400 / (fs/2), 'low');
low_boost = filtfilt(b_ls, a_ls, speech_final);
speech_final = speech_final + (10^(5/20) - 1) * low_boost; % +5dB (moderate)

speech_final = 0.95 * speech_final / (max(abs(speech_final)) + eps);
audiowrite('speech_v13_softer.wav', speech_final, fs);

fprintf('Saved softer hybrid speech to: speech_v13_softer.wav\n');

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
