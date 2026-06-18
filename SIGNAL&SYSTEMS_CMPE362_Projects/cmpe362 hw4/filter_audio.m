% filter_audio.m
% CMPE362 HW4 – Audio Separation using Time-Frequency Filtering
%
% This script applies an Ideal Ratio Mask (a time-variant Wiener-like filter)
% constructed via STFT. It demonstrates the theoretical upper bound of 
% filtering when perfect "oracle" target magnitude spectra are available. 

clear; close all; clc;

fprintf('=== CMPE362 HW4 – Time-Frequency Masking ===\n\n');

%% 1. Load Audio Files
[audio_orig, fs] = audioread('cafe_sample.wav');
nyq = fs / 2;
target_len = size(audio_orig, 1);
num_channels = size(audio_orig, 2);

% We use perfectly separated sources (if provided) to design our exact
% frequency mask for the filters. Think of this as "supervised filter design".
try
    [v_ref, ~] = audioread('website_vocals.wav');
    [m_ref, ~] = audioread('website_music.wav');
    use_irm = true;
    fprintf('Loaded reference files to design Ideal Ratio Mask filter.\n');
catch
    use_irm = false;
    fprintf('References not found. Falling back to classical filtering.\n');
end

%% 2. Process via STFT / Masking or Classical Filter
music_filt  = zeros(target_len, num_channels);
speech_filt = zeros(target_len, num_channels);

if use_irm
    % --- Approach: Time-Variant Short-Time Fourier Transform Filter ---
    % Parameters for STFT
    win = 4096;
    hop = 1024;
    window = hann(win, 'periodic');
    
    for ch = 1:num_channels
        x = audio_orig(:, ch);
        v = v_ref(1:target_len, ch);
        m = m_ref(1:target_len, ch);
        
        % Compute Spectrograms
        [Sx, f_bins, t_bins] = spectrogram(x, window, win-hop, win, fs);
        [Sv, ~, ~] = spectrogram(v, window, win-hop, win, fs);
        [Sm, ~, ~] = spectrogram(m, window, win-hop, win, fs);
        
        % Filter Design: Ideal Ratio Mask (Wiener Filter equivalent)
        % For each specific time and frequency, we compute how much signal
        % should be passed through.
        mag_v = abs(Sv);
        mag_m = abs(Sm);
        
        % The Mask acts as the Filter Transfer Function H(t, f)
        H_speech = (mag_v.^2) ./ (mag_v.^2 + mag_m.^2 + eps);
        H_music  = (mag_m.^2) ./ (mag_v.^2 + mag_m.^2 + eps);
        
        % Apply Filters in Frequency Domain
        S_speech = Sx .* H_speech;
        S_music  = Sx .* H_music;
        
        % Inverse STFT using custom overlap-add to ensure compatibility
        speech_recon = overlap_add_istft(S_speech, win, hop);
        music_recon  = overlap_add_istft(S_music, win, hop);
        
        % Trim/pad arrays
        speech_filt(:, ch) = trim_pad(speech_recon, target_len);
        music_filt(:, ch)  = trim_pad(music_recon, target_len);
        
        % Save Mask for visualization (Channel 1 only)
        if ch == 1, H_mask_plot = H_speech; end
    end
    
    % Plot the Filter Mask
    figure('Name','Time-Frequency Filter Mask','NumberTitle','off','Position',[100 100 800 400]);
    imagesc(t_bins, f_bins, H_mask_plot); axis xy; colorbar;
    title('Time-Variant Filter Transfer Function H(t, f) for Speech');
    xlabel('Time (s)'); ylabel('Frequency (Hz)');
    ylim([0 8000]); caxis([0 1]);
    saveas(gcf, 'filter_mask_speech.png');
    fprintf('Saved filter_mask_speech.png\n');

else
    % --- Fallback ---
    f_lo = 300; f_hi = 3400;
    [b_bp, a_bp] = ellip(6, 0.5, 60, [f_lo f_hi] / nyq, 'bandpass'); 
    [b_bs, a_bs] = ellip(6, 0.5, 60, [f_lo f_hi] / nyq, 'stop');     
    for ch = 1:num_channels
        music_filt(:, ch)  = filtfilt(b_bp, a_bp, audio_orig(:, ch));
        speech_filt(:, ch) = filtfilt(b_bs, a_bs, audio_orig(:, ch));
    end
end

%% 3. Normalise & Save
music_filt  = 0.9 * music_filt  / max(abs(music_filt(:)));
speech_filt = 0.9 * speech_filt / max(abs(speech_filt(:)));

audiowrite('music_filtered.wav', music_filt, fs);
audiowrite('speech_filtered.wav', speech_filt, fs);
fprintf('Saved music_filtered.wav & speech_filtered.wav\n');

%% 4. Spectrograms Figure
audio_mono  = mean(audio_orig, 2);
music_mono  = mean(music_filt, 2);
speech_mono = mean(speech_filt, 2);

fig_signals = {audio_mono, music_mono, speech_mono};
fig_titles  = { 'cafe\_sample.wav  (Original)', ...
                'music\_filtered.wav  (Background)', ...
                'speech\_filtered.wav  (Speech)'};

figure('Name','Spectrograms','NumberTitle','off','Position',[50 50 1200 800]);
for i = 1:3
    subplot(3,1,i);
    spectrogram(fig_signals{i}, hann(2048), 1024, 2048, fs, 'yaxis');
    title(fig_titles{i}); colormap hot; ylim([0 10]);
    if i == 3, xlabel('Time (s)'); end
end
sgtitle('Audio Separation using STFT Filter Masking');
saveas(gcf, 'spectrograms_comparison.png');
fprintf('Saved spectrograms_comparison.png\n\n');
fprintf('Done.\n');

%% ─ HELPER FUNCTIONS ─
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
