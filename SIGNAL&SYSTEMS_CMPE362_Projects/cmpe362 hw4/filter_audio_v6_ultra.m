% filter_audio_v6_ultra.m
% CMPE362 HW4 – Ultra-Precise Speech Extraction (Harmonic-Sustained Suppression)
%
% This script is specifically designed to eliminate "stubborn" background 
% music like accordion melodies that leak through standard masks.
%
% KEY STRATEGIES:
%   1. Over-subtraction (OS): Subtract more of the music reference than is 
%      actually present to ensure the mask fully zeroes out those bins.
%   2. Spectral Floor (beta): A lower floor for cleaner output, though it
%      might introduce some artifacts.
%   3. Minimum-Statistics Noise Tracking (on top of mask): To find any 
%      sustained accordion notes that weren't captured by the music reference.
%   4. Adaptive Scaling: Ensures the music reference magnitude is normalized
%      to the local energy of the mixture.

clear; close all; clc;

fprintf('=== CMPE362 HW4 – Ultra-Precise Accordion Suppression ===\n\n');

speech_lo_hz = 300;
speech_hi_hz = 3400;

%% ─── 1. LOAD AUDIO FILES ───────────────────────────────────────────────────
[audio_orig, fs] = audioread('cafe_sample.wav');
target_len = size(audio_orig, 1);
num_channels = size(audio_orig, 2);

% Use reference files for "noise profile"
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
window = blackman(win_len, 'periodic');

% Extraction Parameters
alpha_os = 2.5;      % Over-subtraction factor (1.0 = standard, >1.0 = aggressive)
beta_floor = 0.005;  % Spectral floor (very low to mute music)
p_val = 2.0;         % Power parameter for mask

% Min-Stats tracking on residual (to catch remaining accordion)
min_win_sec = 0.5;   % Time window (sec) to find sustained music tones
L_min = round(min_win_sec * fs / hop_len);

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
    
    % ─── Step A: Adaptive Scaling of Music Reference ───
    % Scale music magnitude so its peaks don't exceed the mixture
    % This handles cases where the music reference is louder than the cafe mix.
    mag_m_scaled = min(mag_m, mag_x);
    
    % ─── Step B: Multi-target Masking with Over-subtraction ───
    % Compute how much of the original signal is "not music/vocals"
    % Use over-subtraction factor (alpha_os) specifically on the music component
    % to crush the accordion.
    mag_residue = max(mag_x - alpha_os * mag_m_scaled - mag_v, beta_floor * mag_x);
    
    % Wiener Mask for the residue
    H_s = (mag_residue.^p_val) ./ (mag_x.^p_val + eps);
    H_s = min(H_s, 1.0);
    
    % ─── Step C: Min-Stats on the Residue ───
    % Any sustained notes (accordion) that leaked into the residue will be 
    % constant over time. Speech is transient.
    % Track the floor of the residual spectrum and subtract it.
    S_res = Sx .* H_s;
    mag_res = abs(S_res);
    
    noise_floor = zeros(size(mag_res));
    for t = 1:size(mag_res, 2)
        t_start = max(1, t - L_min + 1);
        noise_floor(:, t) = min(mag_res(:, t_start:t), [], 2);
    end
    
    % Subtract sustained noise floor (with 1.5x bias)
    mag_res_clean = max(mag_res - 1.5 * noise_floor, beta_floor * mag_res);
    
    % Refined mask for reconstruction
    H_final = mag_res_clean ./ (mag_res + eps);
    S_final = S_res .* H_final;
    
    % ─── Step D: Frequency-dependent Filtering ───
    % Speech fundamentals rarely go above ~3.4 kHz. Mute higher bands where
    % accordion harmonics are very strong.
    f_mute_idx = f_bins > speech_hi_hz;
    S_final(f_mute_idx, :) = S_final(f_mute_idx, :) * 0.1; % -20dB suppression
    
    % Inverse STFT
    speech_recon = overlap_add_istft(S_final, win_len, hop_len);
    speech_filt(:, ch) = trim_pad(speech_recon, target_len);
end

%% ─── 4. RE-APPLY USER EQ (Low Boost / High Mute) ───────────────────────────
% Cutoff high (3500 Hz) and boost low (fundamentals)
nyq = fs / 2;
lpf_cut = min(speech_hi_hz, nyq - 1);
[b_lpf, a_lpf] = butter(4, lpf_cut / nyq, 'low');
[b_ls, a_ls]   = butter(1, 400 / (fs/2), 'low');

speech_out = filtfilt(b_lpf, a_lpf, speech_filt);
low_boost = filtfilt(b_ls, a_ls, speech_out);
speech_out = speech_out + (10^(8/20) - 1) * low_boost;

%% ─── 5. NORMALIZE & SAVE ───────────────────────────────────────────────────
speech_out = 0.95 * speech_out / (max(abs(speech_out(:))) + eps);
audiowrite('speech_v6_ultra.wav', speech_out, fs);

fprintf('Saved ultra-clean speech to: speech_v6_ultra.wav\n');
fprintf('This version uses aggressive over-subtraction and min-stats noise tracking.\n');

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

function out = trim_pad(in, target_len)
    if length(in) > target_len
        out = in(1:target_len);
    else
        out = zeros(target_len, 1);
        out(1:length(in)) = in;
    end
end
