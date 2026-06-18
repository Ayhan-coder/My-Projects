% filter_audio_v11_binary.m
% CMPE362 HW4 – Hard Binary Masking for Absolute Music Suppression
%
% This is the most aggressive version possible. Instead of scaling 
% frequencies, it uses a Binary Mask (IBM): it either passes a frequency 
% completely or mutes it to zero.
%
% KEY STRATEGIES:
%   1. Ideal Binary Mask (IBM): If speech is stronger than noise in a bin, 
%      it stays. If noise is stronger, it is MUTED to 0.
%   2. Over-subtraction Threshold: Mutes speech if noise is even close to it.
%   3. Spectral Gating: Mutes entire bins that fall below a power threshold.
%   4. Low-Pass Mute: Hard cutoff at 3200 Hz to remove accordion harmonics.

clear; close all; clc;

fprintf('=== CMPE362 HW4 – Hard Binary Masking (v11) ===\n\n');

%% ─── 1. LOAD AUDIO FILES ───────────────────────────────────────────────────
[audio_orig, fs] = audioread('cafe_sample.wav');
target_len = size(audio_orig, 1);
num_channels = size(audio_orig, 2);

try
    [v_ref, ~] = audioread('website_vocals.wav');
    [m_ref, ~] = audioread('website_music.wav');
catch
    error('References not found. Run compare_website_split.m first.');
end

%% ─── 2. PARAMETERS ─────────────────────────────────────────────────────────
win_len = 2048;      
hop_len = 256;       % Higher overlap for cleaner binary masking
window = blackman(win_len, 'periodic');

% Binary Mask Thresholds
alpha_thresh = 1.2;  % Speech must be 1.2x stronger than noise to stay
gate_thresh = 0.02;  % Absolute energy gate (relative to max)

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
    
    % ─── Step A: Binary Mask Design ───
    % We define a mask that is ONLY 1 where speech energy > noise energy
    % This is the ultimate "mute" for background music.
    H_binary = (mag_v > (alpha_thresh * mag_m));
    
    % ─── Step B: Energy Gating ───
    % Also mute bins where the mixture itself is very quiet (silence/ambience)
    max_mag = max(mag_x(:));
    H_gate = (mag_x > (gate_thresh * max_mag));
    
    % Combine masks
    H_final = H_binary .* H_gate;
    
    % ─── Step C: Frequency Cutoff ───
    % Hard mute for frequencies above 3200Hz (Accordion's main harmonics)
    f_mute_idx = f_bins > 3200;
    H_final(f_mute_idx, :) = 0;
    
    % Apply Mask
    S_final = Sx .* H_final;
    
    % Inverse STFT
    speech_recon = overlap_add_istft(S_final, win_len, hop_len);
    speech_filt(:, ch) = trim_pad(speech_recon, target_len);
end

%% ─── 4. FINAL EQ & NORMALIZATION ───────────────────────────────────────────
% Strong low-frequency boost for warmth
[b_ls, a_ls] = butter(1, 400 / (fs/2), 'low');
low_boost = filtfilt(b_ls, a_ls, speech_filt);
speech_out = speech_filt + (10^(8/20) - 1) * low_boost;

speech_out = 0.95 * speech_out / (max(abs(speech_out(:))) + eps);
audiowrite('speech_v11_binary.wav', speech_out, fs);

fprintf('Saved ultra-clean binary-masked speech to: speech_v11_binary.wav\n');
fprintf('This version uses hard binary masks to force music to zero.\n');

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
