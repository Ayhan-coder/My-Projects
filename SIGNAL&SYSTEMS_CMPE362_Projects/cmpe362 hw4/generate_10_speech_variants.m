% generate_10_speech_variants.m
% CMPE362 HW4 – Multiple Speech Extraction Presets
%
% This script generates 10 different versions of speech extraction by 
% varying parameters such as over-subtraction, smoothing, and EQ.
%
% Outputs: speech_variant_1.wav to speech_variant_10.wav

clear; close all; clc;

fprintf('=== CMPE362 HW4 – Generating 10 Speech Variants ===\n\n');

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

%% ─── 2. DEFINE 10 PRESETS ──────────────────────────────────────────────────
% Columns: [alpha_os, beta_floor, tau_t, p_val, f_lpf, low_boost_db]
presets = [
    1.6, 0.03,  4, 2.0, 4500, 4;  % 1. Balanced (Natural)
    1.2, 0.08,  3, 1.5, 5500, 2;  % 2. Minimal Artifacts (Very light)
    2.5, 0.005, 5, 2.5, 3200, 6;  % 3. Ultra Clean (Aggressive mute)
    1.8, 0.04,  8, 2.0, 4000, 5;  % 4. Smooth (Heavy temporal smoothing)
    1.5, 0.02,  2, 2.0, 5000, 8;  % 5. Warm & Bright (High boost + High cutoff)
    2.0, 0.01,  1, 2.0, 3800, 3;  % 6. Sharp (No smoothing, aggressive)
    1.7, 0.05,  4, 1.0, 4200, 10; % 7. Deep (Extreme low-frequency boost)
    2.2, 0.002, 6, 2.5, 3000, 0;  % 8. Radio (Muted highs, no boost, very clean)
    1.4, 0.06,  5, 1.8, 4800, 4;  % 9. Ambient (High floor, natural room sound)
    2.0, 0.02,  4, 2.2, 3500, 7;  % 10. The Hybrid (Balanced aggressive)
];

labels = {
    'Balanced (Natural)', ...
    'Minimal Artifacts (Lightest)', ...
    'Ultra Clean (Aggressive)', ...
    'Smooth (No fluctuations)', ...
    'Warm & Bright', ...
    'Sharp (Fast transients)', ...
    'Deep (Heavy Bass)', ...
    'Radio (Compressed highs)', ...
    'Ambient (Natural room)', ...
    'The Hybrid (Best overall)'
};

%% ─── 3. CORE PROCESSING LOOP ────────────────────────────────────────────────
win_len = 2048;      
hop_len = 512;       
window = hann(win_len, 'periodic');

for v_idx = 1:10
    fprintf('Generating Variant %d: %s...\n', v_idx, labels{v_idx});
    
    % Unpack parameters
    p_alpha = presets(v_idx, 1);
    p_beta  = presets(v_idx, 2);
    p_tau   = presets(v_idx, 3);
    p_pow   = presets(v_idx, 4);
    p_lpf   = presets(v_idx, 5);
    p_boost = presets(v_idx, 6);
    
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
        
        % Mask Design
        mag_noise = p_alpha * mag_m + mag_v;
        mag_residue = max(mag_x - mag_noise, p_beta * mag_x);
        
        H_raw = (mag_residue.^p_pow) ./ (mag_x.^p_pow + eps);
        H_raw = min(H_raw, 1.0);
        
        % Smoothing
        H_smooth = H_raw;
        if p_tau > 1
            for t = 2:size(H_raw, 2)
                H_smooth(:, t) = (1/p_tau) * H_raw(:, t) + (1 - 1/p_tau) * H_smooth(:, t-1);
            end
        end
        
        % Apply Mask
        S_final = Sx .* H_smooth;
        
        % Inverse STFT
        speech_recon = overlap_add_istft(S_final, win_len, hop_len);
        speech_filt(:, ch) = trim_pad(speech_recon, target_len);
    end
    
    % Post-processing EQ
    [b_lpf, a_lpf] = butter(4, p_lpf / (fs/2), 'low');
    [b_ls, a_ls]   = butter(1, 400 / (fs/2), 'low');
    
    speech_out = filtfilt(b_lpf, a_lpf, speech_filt);
    if p_boost > 0
        low_boost = filtfilt(b_ls, a_ls, speech_out);
        speech_out = speech_out + (10^(p_boost/20) - 1) * low_boost;
    end
    
    % Normalize
    speech_out = 0.95 * speech_out / (max(abs(speech_out(:))) + eps);
    
    % Save
    audiowrite(sprintf('speech_variant_%d.wav', v_idx), speech_out, fs);
end

fprintf('\nDone! Generated 10 speech variants.\n');

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
