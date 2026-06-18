% extract_speech_v4.m
% CMPE362 HW4 – Speech Extraction with Minimum-Statistics Noise Tracking
%
% Core problem with v2/v3:
%   The noise estimate was computed from a fixed segment (beginning/end).
%   Instruments that play continuously were never fully captured → subtraction
%   left them audible.
%
% KEY IMPROVEMENT: Minimum-Statistics noise tracking
%   → Continuously tracks the floor of the spectrum over time.
%   → Sustained instrument tones always appear near the floor → eliminated.
%   → Brief speech bursts sit above the floor → preserved.
%
% Additional improvements:
%   → Frequency-dependent alpha: bass & treble suppressed harder
%     (instruments dominate there; speech does not need those bands).
%   → Bias-corrected noise floor (min-stats overestimates → compensate).
%   → Temporal + spectral smoothing to avoid musical-noise artifacts.
%   → Expander gate for inter-word silence cleanup.
%
% Output:
%   speech_v4.wav            – clean speech, instruments suppressed
%   spectrogram_v4.png       – three-panel comparison

clear; close all; clc;
fprintf('=== CMPE362 HW4 – Speech Extraction v4 (Min-Stats) ===\n\n');

%% ─── PARAMETERS ─────────────────────────────────────────────────────────────
speech_lo_hz = 300;
speech_hi_hz = 3400;

% Over-subtraction per frequency zone
%   Outside speech band (bass/treble): much higher alpha → crush instruments
%   Inside speech band: moderate → preserve speech
alpha_speech = 2.5;   % 300 – 3400 Hz  (core speech band)
alpha_outer  = 6.0;   % < 300 Hz  and  > 3400 Hz  (music-only bands)

beta        = 0.02;   % spectral floor (lower = cleaner but more artefacts)
min_win_sec = 0.6;    % min-stats window length (seconds)
bias_corr   = 1.60;   % bias correction for minimum statistics method

% Expander (gentle gate between words)
exp_thresh_dB = -38;
exp_ratio     = 6;

%% ─── 1. LOAD ────────────────────────────────────────────────────────────────
[audio_raw, fs] = audioread('cafe_sample.wav');
if size(audio_raw,2)==2, audio = mean(audio_raw,2); else, audio = audio_raw(:); end
audio = double(audio);
N = length(audio); nyq = fs/2;
fprintf('Loaded: %.2f s @ %d Hz\n\n', N/fs, fs);

%% ─── 2. STFT ────────────────────────────────────────────────────────────────
nfft = 2048;
hop  = 256;   % 87.5% overlap → smooth reconstruction & fine time resolution
win  = sqrt(hann(nfft, 'periodic'));

pad_len  = ceil((N + nfft) / hop) * hop - N;
audio_p  = [audio; zeros(pad_len, 1)];
Np       = length(audio_p);
n_frames = floor((Np - nfft) / hop) + 1;
n_bins   = nfft / 2 + 1;

fprintf('STFT: hop=%d (%.0f%% overlap), computing %d frames... ', ...
        hop, 100*(1-hop/nfft), n_frames);
Smag = zeros(n_bins, n_frames);
Sph  = zeros(n_bins, n_frames);
for k = 1:n_frames
    idx = (k-1)*hop + (1:nfft);
    F = fft(audio_p(idx) .* win, nfft);
    Smag(:,k) = abs(F(1:n_bins));
    Sph(:,k)  = angle(F(1:n_bins));
end
fprintf('done\n');

%% ─── 3. MINIMUM-STATISTICS NOISE TRACKING ───────────────────────────────────
%
%  Classic approach: for each bin, track the minimum power in a sliding window.
%  A sustained tone (instrument) will always be near the minimum of that window.
%  A brief speech burst will raise the instantaneous value above the minimum.
%  → After subtraction: instruments vanish, speech survives.
%
%  Bias correction: in a window of L frames, the minimum of a random process
%  underestimates the true noise floor. Multiply by bias_corr (~1.6) to fix.

L_min = round(min_win_sec * fs / hop);   % window in frames
fprintf('Minimum-statistics tracking: window = %.0f ms (%d frames)...\n', ...
        min_win_sec*1000, L_min);

Spow = Smag .^ 2;  % power spectrogram

% Sliding minimum over time axis (vectorized via cummin approach)
noise_pow_track = zeros(n_bins, n_frames);

for t = 1:n_frames
    t_start = max(1, t - L_min + 1);
    noise_pow_track(:, t) = min(Spow(:, t_start:t), [], 2);
end

% Apply bias correction: min-stats min ≈ true_floor / bias_corr
noise_pow_track = noise_pow_track * bias_corr;

fprintf('  Bias correction: x%.2f\n', bias_corr);

%% ─── 4. FREQUENCY-DEPENDENT ALPHA MATRIX ────────────────────────────────────
freq_bins = linspace(0, nyq, n_bins)';

% Build per-bin alpha (column vector)
alpha_vec = alpha_speech * ones(n_bins, 1);
alpha_vec(freq_bins <  speech_lo_hz)  = alpha_outer;   % bass / sub-bass
alpha_vec(freq_bins >  speech_hi_hz)  = alpha_outer;   % treble / high instruments

% Smoothly taper transition edges (avoid clicks at boundary bins)
smooth_w = 20;  % bins
for b = 1:n_bins
    if freq_bins(b) >= 250 && freq_bins(b) <= 350
        t_val = (freq_bins(b) - 250) / 100;
        alpha_vec(b) = alpha_outer*(1-t_val) + alpha_speech*t_val;
    elseif freq_bins(b) >= 3300 && freq_bins(b) <= 3500
        t_val = (freq_bins(b) - 3300) / 200;
        alpha_vec(b) = alpha_speech*(1-t_val) + alpha_outer*t_val;
    end
end

fprintf('Frequency-dependent alpha: %.1f (speech band), %.1f (bass+treble)\n', ...
        alpha_speech, alpha_outer);

%% ─── 5. WIENER-STYLE GAIN WITH TRACKING NOISE ───────────────────────────────
fprintf('Computing gain function...\n');

% Expand alpha_vec to matrix
Alpha_mat = repmat(alpha_vec, 1, n_frames);

signal_power_est = max(Spow - Alpha_mat .* noise_pow_track, beta * Spow);
gain_raw = sqrt(signal_power_est ./ (Spow + 1e-10));
gain_raw = min(gain_raw, 1.0);

% ── Temporal exponential smoothing (reduces musical noise) ──
fprintf('  Temporal smoothing (tau=4)...\n');
tau_t = 4;
gain_smooth = gain_raw;
for t = 2:n_frames
    gain_smooth(:,t) = (1/tau_t)*gain_raw(:,t) + (1-1/tau_t)*gain_smooth(:,t-1);
end

% ── Spectral median smoothing (removes isolated freq spikes) ──
fprintf('  Spectral median smoothing (7-bin)...\n');
for t = 1:n_frames
    gain_smooth(:,t) = medfilt1(gain_smooth(:,t), 7);
end

%% ─── 6. INVERSE STFT ────────────────────────────────────────────────────────
fprintf('Inverse STFT (overlap-add)... ');
S_clean_mag = gain_smooth .* Smag;
S_noise_mag = (1 - gain_smooth) .* Smag;

clean_sig = zeros(Np,1);
noise_sig = zeros(Np,1);
win_acc   = zeros(Np,1);

for k = 1:n_frames
    idx = (k-1)*hop + (1:nfft);
    C = S_clean_mag(:,k) .* exp(1i * Sph(:,k));
    N_est = S_noise_mag(:,k) .* exp(1i * Sph(:,k));
    C_full = [C; conj(flipud(C(2:end-1)))];
    N_full = [N_est; conj(flipud(N_est(2:end-1)))];
    c_frame = real(ifft(C_full, 'symmetric')) .* win;
    n_frame = real(ifft(N_full, 'symmetric')) .* win;
    clean_sig(idx) = clean_sig(idx) + c_frame;
    noise_sig(idx) = noise_sig(idx) + n_frame;
    win_acc(idx)   = win_acc(idx) + win.^2;
end
win_acc   = max(win_acc, 1e-10);
clean_sig = (clean_sig ./ win_acc); clean_sig = clean_sig(1:N);
noise_sig = (noise_sig ./ win_acc); noise_sig = noise_sig(1:N);
fprintf('done\n');

%% ─── 7. POST-PROCESSING ─────────────────────────────────────────────────────
fprintf('Post-processing...\n');

% (A) Speech bandpass
bp_hi = min(speech_hi_hz, nyq - 1);
bp_lo = min(speech_lo_hz, bp_hi - 1);
if bp_lo > 0 && bp_hi > bp_lo
    [b_bp, a_bp] = butter(4, [bp_lo bp_hi]/nyq, 'bandpass');
    speech_filt = filtfilt(b_bp, a_bp, clean_sig);
else
    speech_filt = clean_sig;
end

% (B) Downward expander (smooth gate)
envelope   = abs(hilbert(speech_filt));
env_smooth = filtfilt(ones(1, round(fs*0.015)), round(fs*0.015), envelope);
thresh_lin = max(abs(speech_filt)) * 10^(exp_thresh_dB/20);
exp_gain   = ones(size(env_smooth));
below      = env_smooth < thresh_lin;
exp_gain(below) = (env_smooth(below) / thresh_lin) .^ (1 - 1/exp_ratio);
speech_out = speech_filt .* exp_gain;

% (C) Sub-bass roll-off
[b_hp, a_hp] = butter(2, 80/nyq, 'high');
speech_out = filtfilt(b_hp, a_hp, speech_out);

fprintf('  Bandpass %.0f–%.0f Hz, expander %.0f dB/%d:1, HP 80 Hz\n', ...
    bp_lo, bp_hi, ...
        exp_thresh_dB, exp_ratio);

%% ─── 8. SAVE ─────────────────────────────────────────────────────────────────
speech_out = speech_out / (max(abs(speech_out)) + 1e-10) * 0.95;
noise_out  = noise_sig  / (max(abs(noise_sig))  + 1e-10) * 0.95;

audiowrite('speech_v4.wav',      speech_out, fs);
audiowrite('music_v4.wav',       noise_out,  fs);

fprintf('\n✓ Saved:\n');
fprintf('  speech_v4.wav   – instruments suppressed (min-stats tracking)\n');
fprintf('  music_v4.wav    – extracted background\n\n');

%% ─── 9. SPECTROGRAMS ─────────────────────────────────────────────────────────
fprintf('Generating spectrograms...\n');

figure('Name','Speech Extraction v4 (Min-Stats)','NumberTitle','off', ...
       'Position',[50 50 1400 900]);

subplot(3,1,1);
spectrogram(audio,      hann(2048),1536,2048,fs,'yaxis');
title('Original'); colormap hot; ylim([0 8]); colorbar; caxis([-80 -20]);

subplot(3,1,2);
spectrogram(speech_out, hann(2048),1536,2048,fs,'yaxis');
title('v4 – Min-Stats + Freq-Dependent Suppression'); 
colormap hot; ylim([0 8]); colorbar; caxis([-80 -20]);

subplot(3,1,3);
spectrogram(noise_out,  hann(2048),1536,2048,fs,'yaxis');
title('Suppressed Background (Music/Instruments)');
colormap hot; ylim([0 8]); colorbar; caxis([-80 -20]);

sgtitle('Speech Extraction v4 – CMPE362 HW4','FontSize',14,'FontWeight','bold');
saveas(gcf, 'spectrogram_v4.png');
fprintf('  Saved spectrogram_v4.png\n\n');

%% ─── 10. METRICS ─────────────────────────────────────────────────────────────
fprintf('=== Metrics ===\n');
fprintf('  Original:       RMS = %.4f\n', rms(audio));
fprintf('  speech_v4.wav:  RMS = %.4f  (%.0f%% of original)\n', ...
        rms(speech_out), 100*rms(speech_out)/rms(audio));
fprintf('  music_v4.wav:   RMS = %.4f  (%.0f%% of original)\n', ...
        rms(noise_out), 100*rms(noise_out)/rms(audio));

% Instrument suppression: check 500-2000 Hz in music channel vs original
[b_ins, a_ins] = butter(4, [500 2000]/nyq, 'bandpass');
ins_orig = rms(filtfilt(b_ins, a_ins, audio));
ins_out  = rms(filtfilt(b_ins, a_ins, speech_out));
fprintf('\n  Instrument-band suppression (500–2000 Hz): %.1f dB\n', ...
        20*log10(ins_out/ins_orig));
fprintf('  (negative = instruments suppressed relative to original)\n\n');

fprintf('=== Done ===\n');
fprintf('Listen to speech_v4.wav — instruments should be much less audible.\n');
fprintf('If still too prominent: decrease min_win_sec (line 27) or increase alpha_outer (line 25).\n\n');
