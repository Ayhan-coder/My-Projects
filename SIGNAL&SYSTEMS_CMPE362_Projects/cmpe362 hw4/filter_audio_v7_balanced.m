% filter_audio_v7_balanced.m
% CMPE362 HW4 – Balanced Speech Extraction (Suppression vs Quality)
%
% This script aims for a middle-ground: keeping the accordion suppressed 
% without introducing robotic/metallic "spectral holes" in the speech.
%
% KEY STRATEGIES:
%   1. Moderate Over-subtraction (alpha_os = 1.6): Enough to mute the 
%      accordion, but not so much that it eats into the speech spectrum.
%   2. Temporal Gain Smoothing (tau = 4 frames): Prevents rapid fluctuations 
%      in the frequency mask, which is the main cause of robotic artifacts.
%   3. Spectral Floor (beta = 0.03): Maintains a low-level background ambience 
%      instead of absolute silence, making the result sound more natural.
%   4. Frequency-Dependent Masking: Aggressive suppression above 3kHz (accordion)
%      and gentle suppression below 500Hz (speech fundamentals).

clear; close all; clc;

fprintf('=== CMPE362 HW4 – Balanced Speech Extraction (v7) ===\n\n');

speech_lo_hz = 300;
speech_hi_hz = 3400;

%% ─── 1. LOAD AUDIO FILES ───────────────────────────────────────────────────
[audio_orig, fs] = audioread('cafe_sample.wav');
target_len = size(audio_orig, 1);
num_channels = size(audio_orig, 2);

try
    [v_ref, ~] = audioread('website_vocals.wav');
    [m_ref, ~] = audioread('website_music.wav');
    use_refs = true;
catch
    error('References not found. Run compare_website_split.m first.');
end

%% ─── 2. PARAMETERS ─────────────────────────────────────────────────────────
win_len = 2048;      
hop_len = 512;       
window = hann(win_len, 'periodic'); % Hann is smoother for quality than Blackman

% Balanced Extraction Parameters
alpha_os_base = 1.6;  % Moderate over-subtraction
beta_floor = 0.03;    % Natural-sounding floor
p_val = 2.0;          % Power parameter (IRM)

% Smoothing
tau_t = 4;            % Time-constant in frames for gain smoothing

%% ─── 3. PROCESS PER CHANNEL ────────────────────────────────────────────────
speech_filt = zeros(target_len, num_channels);

for ch = 1:num_channels
    x = audio_orig(:, ch);
    v = v_ref(1:target_len, ch);
    m = m_ref(1:target_len, ch);
    
    % STFTs
    [Sx, f_bins, t_bins] = spectrogram(x, window, win_len-hop_len, win_len, fs);
    [Sv, ~, ~] = spectrogram(v, window, win_len-hop_len, win_len, fs);
    [Sm, ~, ~] = spectrogram(m, window, win_len-hop_len, win_len, fs);
    
    mag_x = abs(Sx);
    mag_v = abs(Sv);
    mag_m = abs(Sm);
    
    % ─── Step A: Frequency-dependent Alpha ───
    % Be more aggressive where accordion is strong (mid-high)
    alpha_vec = ones(size(f_bins)) * alpha_os_base;
    alpha_vec(f_bins > 3000) = alpha_os_base * 1.5; % Stronger for high harmonics
    alpha_vec(f_bins < 500)  = alpha_os_base * 0.7; % Gentler for speech fundamentals
    Alpha_mat = repmat(alpha_vec, 1, size(mag_x, 2));
    
    % ─── Step B: Mask Design ───
    % Estimate speech residue (mixture - scaled noise)
    mag_noise = Alpha_mat .* mag_m + mag_v;
    mag_residue = max(mag_x - mag_noise, beta_floor * mag_x);
    
    % Gain Function (H)
    H_raw = (mag_residue.^p_val) ./ (mag_x.^p_val + eps);
    H_raw = min(H_raw, 1.0);
    
    % ─── Step C: Temporal Smoothing ───
    % This is the most critical step to avoid speech corruption.
    % It filters the mask coefficients over time.
    H_smooth = H_raw;
    for t = 2:size(H_raw, 2)
        H_smooth(:, t) = (1/tau_t) * H_raw(:, t) + (1 - 1/tau_t) * H_smooth(:, t-1);
    end
    
    % ─── Step D: Frequency Muting (Post-mask) ───
    % Soft roll-off above ~3.4 kHz to catch remaining accordion harmonics
    for b = 1:length(f_bins)
        if f_bins(b) > speech_hi_hz
            H_smooth(b, :) = H_smooth(b, :) * 0.5;
        end
    end
    
    % Apply Smoothed Mask
    S_final = Sx .* H_smooth;
    
    % Inverse STFT
    speech_recon = overlap_add_istft(S_final, win_len, hop_len);
    speech_filt(:, ch) = trim_pad(speech_recon, target_len);
end

%% ─── 4. FINAL EQ & NORMALIZATION ───────────────────────────────────────────
% Gentle EQ (Less extreme than previous)
nyq = fs / 2;
lpf_cut = min(speech_hi_hz, nyq - 1);
[b_lpf, a_lpf] = butter(4, lpf_cut / nyq, 'low');
[b_ls, a_ls]   = butter(1, 400 / (fs/2), 'low');

speech_out = filtfilt(b_lpf, a_lpf, speech_filt);
low_boost = filtfilt(b_ls, a_ls, speech_out);
speech_out = speech_out + (10^(4/20) - 1) * low_boost; % +4dB boost (moderate)

speech_out = 0.95 * speech_out / (max(abs(speech_out(:))) + eps);
audiowrite('speech_v7_balanced.wav', speech_out, fs);

fprintf('Saved balanced speech to: speech_v7_balanced.wav\n');
fprintf('This version balances accordion suppression with speech quality.\n');

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

function out = trim_pad(in, target_len)
    if length(in) > target_len
        out = in(1:target_len);
    else
        out = zeros(target_len, 1);
        out(1:length(in)) = in;
    end
end
