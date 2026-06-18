%%=========================================================================
%  SPEECH / MUSIC SEPARATION using REPET + HPSS + NMF + Wiener Masking
%
%  Input  : cafe_sample.wav
%  Output : speech_filtered.wav  → speech removed,   music audible
%           music_filtered.wav   → music  removed,   speech audible
%
%  Methods:
%    1) REPET  – Repeating Pattern Extraction Technique
%    2) HPSS   – Harmonic-Percussive Source Separation
%    3) NMF    – Non-negative Matrix Factorization
%    4) Wiener soft-masking to combine all three
%    5) Post-processing with IIR / FIR filters
%%=========================================================================
clear; clc; close all;

EPS = 1e-10;   % global small constant

%% ======================== 1. LOAD AUDIO ================================
[x_orig, fs] = audioread('cafe_sample.wav');
if size(x_orig,2) > 1                         % stereo → mono
    x = mean(x_orig, 2);
else
    x = x_orig;
end
N  = length(x);
Fn = fs / 2;
fprintf('Loaded: %d Hz | %.2f s | %d samples\n\n', fs, N/fs, N);

%% ======================== 2. STFT ======================================
win_len = 2048;                                % ~46 ms @ 44.1 kHz
hop_len = win_len / 4;                         % 75 % overlap (COLA)
nfft    = win_len * 2;                         % zero-pad
win     = hann(win_len, 'periodic');

S       = stft_forward(x, win, hop_len, nfft); % complex STFT
V       = abs(S);                               % magnitude
phi     = angle(S);                             % phase
[nBins, nFrames] = size(S);

freq_ax = (0:nBins-1)' * fs / nfft;            % Hz
time_ax = (0:nFrames-1)  * hop_len / fs;        % s

fprintf('STFT: %d bins × %d frames  (win=%d, hop=%d, nfft=%d)\n\n', ...
        nBins, nFrames, win_len, hop_len, nfft);

%% ======================== 3. REPET =====================================
%  Idea: Music repeats (beats, loops, chords).  Speech does NOT.
%        → Repeating part = music,  Residual = speech
%
%  Steps:
%   a. Beat spectrum via autocorrelation of the power spectrogram
%   b. Detect the repeating period
%   c. Build repeating model (median across aligned segments)
%   d. Soft Wiener mask
%  Reference: Rafii & Pardo, "REpeating Pattern Extraction Technique
%             (REPET)", ICASSP 2011 / TASLP 2013
%--------------------------------------------------------------------------
fprintf('--- [1/3] REPET ---\n');

P = V .^ 2;                                    % power spectrogram

%  Beat spectrum:  b(l) = Σ_f  autocorr{ P(f,:) }(l)
min_period = round(0.5 * fs / hop_len);         % 0.5 s
max_period = min(nFrames - 1, round(8 * fs / hop_len));  % 8 s

nfft_ac   = 2^nextpow2(2*nFrames);
P_fft     = fft(P, nfft_ac, 2);                % FFT along time
auto_mat  = real(ifft(P_fft .* conj(P_fft), [], 2));
beat_spec = sum(auto_mat(:, 1:max_period+1), 1);
beat_spec = beat_spec / beat_spec(1);           % normalise

%  Find the dominant repeating period
search   = beat_spec(min_period+1 : max_period+1);
[pks, locs] = findpeaks(search, 'SortStr','descend', 'NPeaks',5, ...
              'MinPeakDistance', round(0.3*fs/hop_len));

if ~isempty(pks)
    rep_period = locs(1) + min_period;          % frame index
else
    [~, idx] = max(search);
    rep_period = idx + min_period;
end
rep_sec = rep_period * hop_len / fs;
fprintf('  Repeating period: %d frames  (%.2f s)\n', rep_period, rep_sec);

%  Build repeating spectrogram model
nSeg = floor(nFrames / rep_period);

if nSeg >= 2
    %  Stack segments and take column-wise median
    V_stack = zeros(nBins, rep_period, nSeg);
    for s = 1:nSeg
        c1 = (s-1)*rep_period + 1;
        c2 = s * rep_period;
        V_stack(:,:,s) = V(:, c1:c2);
    end
    R_model = median(V_stack, 3);               % repeating template

    %  Tile to full length
    R_full = repmat(R_model, 1, nSeg);
    leftover = nFrames - nSeg*rep_period;
    if leftover > 0
        R_full = [R_full, R_model(:,1:leftover)];
    end
    R_full = min(R_full, V);                    % model ≤ observation

    %  Soft Wiener mask
    repet_mask_music  = (R_full.^2) ./ (V.^2 + EPS);
    repet_mask_music  = min(repet_mask_music, 1);
else
    fprintf('  Warning: too few repetitions – REPET mask set to 0.5\n');
    repet_mask_music = 0.5 * ones(size(V));
end

repet_mask_speech = 1 - repet_mask_music;
fprintf('  REPET masks done.\n\n');

%% ======================== 4. HPSS =====================================
%  Idea: Harmonic content is smooth along TIME → horizontal median filter
%        Percussive content is smooth along FREQ → vertical median filter
%  Music tends to be more harmonic; speech consonants are percussive.
%  Reference: Fitzgerald, "Harmonic/Percussive Separation using Median
%             Filtering", DAFx 2010
%--------------------------------------------------------------------------
fprintf('--- [2/3] HPSS ---\n');

L_h = 31;                                       % harmonic median (time)
L_p = 31;                                       % percussive median (freq)

H_est = medfilt2(V, [1,   L_h], 'symmetric');   % harmonic estimate
P_est = medfilt2(V, [L_p, 1  ], 'symmetric');   % percussive estimate

hpss_mask_harm = (H_est.^2) ./ (H_est.^2 + P_est.^2 + EPS);
hpss_mask_perc = (P_est.^2) ./ (H_est.^2 + P_est.^2 + EPS);

fprintf('  HPSS masks done  (L_h=%d, L_p=%d).\n\n', L_h, L_p);

%% ======================== 5. NMF ======================================
%  Idea: V ≈ W·H   (W = spectral bases, H = temporal activations)
%        Cluster components into speech-like vs music-like using features.
%  Reference: Lee & Seung, "Algorithms for Non-negative Matrix
%             Factorization", NeurIPS 2001
%--------------------------------------------------------------------------
fprintf('--- [3/3] NMF ---\n');

K       = 30;                                    % NMF rank
maxIter = 300;
rng(42);                                         % reproducibility

W = rand(nBins, K) + EPS;
H = rand(K, nFrames) + EPS;

%  Multiplicative update rules (KL divergence)
fprintf('  Running %d iterations (K=%d) ...', maxIter, K);
for it = 1:maxIter
    % --- update H ---
    WtV  = W' * V;
    WtWH = W' * (W * H) + EPS;
    H    = H .* (WtV ./ WtWH);

    % --- update W ---
    VHt  = V  * H';
    WHHt = (W * H) * H' + EPS;
    W    = W .* (VHt ./ WHHt);

    if mod(it, 100) == 0, fprintf(' %d', it); end
end
fprintf(' done.\n');

%  Per-component reconstruction (soft NMF mask)
V_approx = W * H + EPS;
comp_specs = zeros(nBins, nFrames, K);
for k = 1:K
    comp_specs(:,:,k) = (W(:,k) * H(k,:)) ./ V_approx .* V;
end

%  Classify each component: speech vs music
%  Features: spectral centroid variance (speech → high),
%            temporal autocorrelation  (music → high)
scores = zeros(K, 1);
freqs  = (0:nBins-1)' * fs / nfft;

for k = 1:K
    Ck = comp_specs(:,:,k);

    %  spectral centroid per frame → high variance = speech-like
    centroids  = sum(bsxfun(@times, freqs, Ck), 1) ./ (sum(Ck,1) + EPS);
    cent_var   = var(centroids);

    %  temporal regularity (autocorrelation peak) → high = music-like
    energy_k   = sum(Ck, 1);
    ac_k       = xcorr(energy_k - mean(energy_k), max_period, 'normalized');
    ac_pos     = ac_k(max_period+1+min_period : end);
    regularity = max(ac_pos);

    %  spectral flatness (speech is less flat than music harmonics on average,
    %  but broadband noise is flat – combine with other cues)
    sf = exp(mean(log(Ck + EPS), 1));
    sf = mean(sf ./ (mean(Ck, 1) + EPS));

    %  combined score: positive = more speech-like
    scores(k) = cent_var / (regularity + 0.05) * (1 - sf);
end

%  Normalise scores to [0,1]
scores = (scores - min(scores)) ./ (max(scores) - min(scores) + EPS);

%  Build NMF soft masks
nmf_speech = zeros(nBins, nFrames);
nmf_music  = zeros(nBins, nFrames);
for k = 1:K
    nmf_speech = nmf_speech + scores(k)       * comp_specs(:,:,k);
    nmf_music  = nmf_music  + (1-scores(k))   * comp_specs(:,:,k);
end
nmf_mask_speech = nmf_speech ./ (nmf_speech + nmf_music + EPS);
nmf_mask_music  = 1 - nmf_mask_speech;

fprintf('  NMF masks done.\n\n');

%% ======================== 6. COMBINE MASKS =============================
%  Weighted fusion of all three methods, then Wiener normalisation.
%--------------------------------------------------------------------------
fprintf('--- Combining masks (Wiener fusion) ---\n');

w1 = 0.50;       % REPET  – best for repetitive music
w2 = 0.15;       % HPSS   – harmonic / percussive cue
w3 = 0.35;       % NMF    – data-driven basis decomposition

%  Music mask: REPET-music + HPSS-harmonic + NMF-music
comb_music  = w1*repet_mask_music  + w2*hpss_mask_harm + w3*nmf_mask_music;
%  Speech mask: REPET-speech + HPSS-percussive + NMF-speech
comb_speech = w1*repet_mask_speech + w2*hpss_mask_perc + w3*nmf_mask_speech;

%  Wiener normalisation (masks sum to 1 at every T-F bin)
M_sum       = comb_music + comb_speech + EPS;
mask_music  = comb_music  ./ M_sum;
mask_speech = comb_speech ./ M_sum;

%  Optional: sharpen masks (exponent > 1 pushes toward binary)
gamma       = 1.5;
mask_music  = mask_music  .^ gamma;
mask_speech = mask_speech .^ gamma;
M_sum2      = mask_music + mask_speech + EPS;
mask_music  = mask_music  ./ M_sum2;
mask_speech = mask_speech ./ M_sum2;

fprintf('  Final masks ready.\n\n');

%% ======================== 7. APPLY MASKS & ISTFT =======================
fprintf('--- Reconstructing separated signals ---\n');

S_speech = mask_speech .* V .* exp(1j * phi);
S_music  = mask_music  .* V .* exp(1j * phi);

y_speech = stft_inverse(S_speech, win, hop_len, nfft, N);
y_music  = stft_inverse(S_music,  win, hop_len, nfft, N);
y_speech = force_length(y_speech, N);
y_music  = force_length(y_music,  N);

fprintf('  ISTFT done.\n\n');

%% ======================== 8. POST-PROCESSING FILTERS ===================
%  Use classic IIR / FIR filter-design functions as required by homework.
%--------------------------------------------------------------------------
fprintf('--- Post-processing with designed filters ---\n');

% ---- 8a. Speech channel: bandpass 80–8000 Hz (Elliptic, sharpest cutoff)
[nord, Wn] = ellipord([80 8000]/Fn, [30 12000]/Fn, 0.5, 50);
nord = min(nord, 10);                                  % cap order
[z_bp, p_bp, k_bp] = ellip(nord, 0.5, 50, Wn, 'bandpass');
[sos_bp, g_bp]     = zp2sos(z_bp, p_bp, k_bp);        % SOS form
y_speech = sosfilt(sos_bp, y_speech) * g_bp;
y_speech = flipud(sosfilt(sos_bp, flipud(y_speech))) * g_bp;  % zero-phase
fprintf('  Speech: Elliptic bandpass 80–8000 Hz  (order %d)\n', 2*nord);

% ---- 8b. Speech channel: presence boost at 2–4 kHz  (FIR peaking)
bw_peak = 0.15;                                        % normalised BW
f_peak  = 3000 / Fn;
[b_pk, a_pk] = iirpeak(f_peak, bw_peak);
y_speech = filter(b_pk, a_pk, y_speech);
fprintf('  Speech: Peaking filter at 3 kHz\n');

% ---- 8c. Music channel: notch out main speech formant bands
formants = [500, 1500, 2500, 3500];
for fi = 1:length(formants)
    if formants(fi) < Fn
        wo = formants(fi) / Fn;
        bw = wo / 10;
        [b_n, a_n] = iirnotch(wo, bw);
        y_music = filtfilt(b_n, a_n, y_music);
    end
end
fprintf('  Music:  Notch filters at %s Hz\n', mat2str(formants));

% ---- 8d. Music channel: bass shelf boost (Butterworth LPF additive)
[b_bass, a_bass] = butter(4, 200/Fn, 'low');
y_music = y_music + 0.25 * filtfilt(b_bass, a_bass, y_music);
fprintf('  Music:  Bass boost < 200 Hz  (Butterworth order 4)\n');

% ---- 8e. Music channel: treble boost (Chebyshev Type-I HPF)
[b_tr, a_tr] = cheby1(4, 0.5, 6000/Fn, 'high');
y_music = y_music + 0.15 * filtfilt(b_tr, a_tr, y_music);
fprintf('  Music:  Treble boost > 6 kHz  (Chebyshev-I order 4)\n');

% ---- 8f. Music channel: gentle Butterworth LPF to tame artefacts
[b_lp, a_lp] = butter(6, min(14000, Fn-100)/Fn, 'low');
y_music = filtfilt(b_lp, a_lp, y_music);
fprintf('  Music:  Butterworth LPF at 14 kHz  (order 6)\n\n');

%% ======================== 9. NORMALISE & SAVE ==========================
y_speech = loudness_boost(y_speech, -16, 0.99);
y_music  = loudness_boost(y_music,  -16, 0.99);

audiowrite('speech_filtered.wav', y_music,  fs);   % speech removed
audiowrite('music_filtered.wav',  y_speech, fs);   % music  removed

fprintf('✓  speech_filtered.wav  (speech REMOVED, music audible)\n');
fprintf('✓  music_filtered.wav   (music  REMOVED, speech audible)\n\n');

%% ======================== 10. VISUALISATION ============================
figure('Position',[40 20 1700 1000], 'Color','w', ...
       'Name','Source Separation Results');

t_audio = (0:N-1)/fs;

% --- Row 1 : Waveforms ---
subplot(4,3,1);
plot(t_audio, x, 'Color',[.2 .2 .7]); axis tight; grid on;
title('Original Mix'); xlabel('s'); ylabel('Amp');

subplot(4,3,2);
plot(t_audio, y_speech, 'Color',[0 .6 0]); axis tight; grid on;
title('Extracted Speech  →  music\_filtered.wav'); xlabel('s');

subplot(4,3,3);
plot(t_audio, y_music, 'Color',[.8 .15 0]); axis tight; grid on;
title('Extracted Music  →  speech\_filtered.wav'); xlabel('s');

% --- Row 2 : Spectrograms ---
subplot(4,3,4);
imagesc(time_ax, freq_ax/1000, 20*log10(V+EPS));
axis xy; ylim([0 min(10,Fn/1000)]); colorbar; colormap jet;
title('Original Spectrogram'); xlabel('s'); ylabel('kHz');

subplot(4,3,5);
V_sp = abs(stft_forward(y_speech, win, hop_len, nfft));
imagesc(time_ax, freq_ax/1000, 20*log10(V_sp+EPS));
axis xy; ylim([0 min(10,Fn/1000)]); colorbar; colormap jet;
title('Speech Spectrogram'); xlabel('s'); ylabel('kHz');

subplot(4,3,6);
V_mu = abs(stft_forward(y_music, win, hop_len, nfft));
imagesc(time_ax, freq_ax/1000, 20*log10(V_mu+EPS));
axis xy; ylim([0 min(10,Fn/1000)]); colorbar; colormap jet;
title('Music Spectrogram'); xlabel('s'); ylabel('kHz');

% --- Row 3 : Individual masks ---
subplot(4,3,7);
imagesc(time_ax, freq_ax/1000, repet_mask_speech);
axis xy; ylim([0 min(10,Fn/1000)]); colorbar;
title('REPET Speech Mask'); xlabel('s'); ylabel('kHz');

subplot(4,3,8);
imagesc(time_ax, freq_ax/1000, hpss_mask_perc);
axis xy; ylim([0 min(10,Fn/1000)]); colorbar;
title('HPSS Percussive Mask'); xlabel('s'); ylabel('kHz');

subplot(4,3,9);
imagesc(time_ax, freq_ax/1000, nmf_mask_speech);
axis xy; ylim([0 min(10,Fn/1000)]); colorbar;
title('NMF Speech Mask'); xlabel('s'); ylabel('kHz');

% --- Row 4 : Beat spectrum, NMF scores, filter response ---
subplot(4,3,10);
lag_sec = (0:max_period) * hop_len / fs;
plot(lag_sec, beat_spec, 'b', 'LineWidth',1.2); grid on;
hold on; xline(rep_sec, '--r','LineWidth',1.5); hold off;
xlabel('Lag (s)'); ylabel('Normalised');
title(sprintf('Beat Spectrum  (period = %.2f s)', rep_sec));

subplot(4,3,11);
bar(1:K, scores, 'FaceColor',[.3 .6 .9]); grid on;
xlabel('Component'); ylabel('Speech score');
title('NMF Component Classification');

subplot(4,3,12);
nPts = 8192;
[Hbp, fbp] = freqz(sos_bp(1,1:3), sos_bp(1,4:6), nPts, fs);
for si = 2:size(sos_bp,1)
    Hbp = Hbp .* freqz(sos_bp(si,1:3), sos_bp(si,4:6), nPts, fs);
end
Hbp = Hbp * g_bp^2;                   % account for double pass
[Hn, fn] = freqz(b_n, a_n, nPts, fs); % last notch
plot(fbp, 20*log10(abs(Hbp)+EPS), 'b', 'LineWidth',1.5); hold on;
plot(fn,  20*log10(abs(Hn)+EPS),  'r', 'LineWidth',1.2); hold off;
legend('Speech Elliptic BP','Music Notch (3.5 kHz)');
xlabel('Hz'); ylabel('dB'); xlim([0 10000]); ylim([-70 5]); grid on;
title('Post-Processing Filter Responses');

sgtitle('Speech / Music Separation — REPET + HPSS + NMF', 'FontSize',15);

%% --- Pole-Zero plot ---
figure('Name','Pole-Zero: Elliptic Bandpass','Position',[800 400 500 450]);
zplane(z_bp, p_bp); title('Elliptic Bandpass – Poles & Zeros');

%% ======================== 11. BONUS: HIDDEN MESSAGE ====================
fprintf('\n============ BONUS : Hidden Message Detection ============\n');

figure('Position',[60 40 1600 850], 'Color','w', ...
       'Name','Hidden Message Hunt');

% (a) Wideband spectrogram – look for visual patterns / text
subplot(2,3,1);
spectrogram(x, hann(256,'periodic'), 250, 2048, fs, 'yaxis');
colormap jet; title('Short-Window Spectrogram'); colorbar;

% (b) Narrowband spectrogram – reveals tonal patterns
subplot(2,3,2);
spectrogram(x, hann(4096,'periodic'), 4000, 8192, fs, 'yaxis');
colormap jet; title('Long-Window Spectrogram'); colorbar;

% (c) High-frequency spectrogram (> 10 kHz) – ultrasonic hiding
subplot(2,3,3);
if Fn > 10000
    [b_hf, a_hf] = cheby2(8, 60, 10000/Fn, 'high');
    x_hf = filtfilt(b_hf, a_hf, x);
    spectrogram(x_hf, hann(512,'periodic'), 504, 2048, fs, 'yaxis');
    colormap jet; title('Content > 10 kHz');
else
    title('Fs too low for ultrasonic check');
end

% (d) LSB steganography check
subplot(2,3,4);
[x_native, ~] = audioread('cafe_sample.wav', 'native');
if isa(x_native, 'int16')
    lsb = bitand(abs(x_native(:,1)), int16(1));
    nBitsTotal = length(lsb);
    nChars = floor(nBitsTotal / 8);

    % Try both bit-orderings
    for order = ["MSB-first", "LSB-first"]
        bm = reshape(double(lsb(1:nChars*8)), 8, nChars)';
        if order == "LSB-first", bm = fliplr(bm); end
        cv = bm * (2.^(7:-1:0))';
        printable = sum(cv>=32 & cv<=126) / nChars;
        fprintf('  %s : %.1f%% printable ASCII\n', order, printable*100);
        if printable > 0.6
            msg = char(cv');
            fprintf('  → Message: %s\n', msg(1:min(300,end)));
        end
    end

    % Try every Nth sample (hidden periodically)
    for skip = [2 4 8 16 32 100 fs]
        lsb_skip = lsb(1:skip:end);
        nc = floor(length(lsb_skip)/8);
        if nc < 5, continue; end
        bm = reshape(double(lsb_skip(1:nc*8)), 8, nc)';
        cv = bm * (2.^(7:-1:0))';
        pr = sum(cv>=32 & cv<=126) / nc;
        if pr > 0.65
            fprintf('  LSB skip=%d : %s\n', skip, char(cv(1:min(200,end))'));
        end
    end
    plot(double(lsb(1:min(10000,end))), '.', 'MarkerSize',1);
    title('LSB Stream'); xlabel('Sample');
else
    text(0.3, 0.5, 'Not 16-bit PCM'); title('LSB Check');
end

% (e) Autocorrelation of amplitude envelope (periodic hiding?)
subplot(2,3,5);
env_frame = round(0.01*fs);
nEnv = floor(N/env_frame);
env  = zeros(1,nEnv);
for k = 1:nEnv
    seg = x((k-1)*env_frame+1 : k*env_frame);
    env(k) = sqrt(mean(seg.^2));
end
[acf, lag] = xcorr(env - mean(env), 'normalized');
acf = acf(nEnv:end); lag = lag(nEnv:end);
plot(lag*env_frame/fs, acf, 'b'); grid on;
xlabel('Lag (s)'); title('Envelope Autocorrelation');

% (f) Scan narrow bands for on-off keyed tones
subplot(2,3,6);
scan_lo = 5000; scan_hi = min(Fn-200, 20000); scan_step = 200;
scan_f  = scan_lo : scan_step : scan_hi;
tone_map = zeros(length(scan_f), nEnv);
for fi = 1:length(scan_f)
    fc = scan_f(fi);
    [b_nb, a_nb] = butter(4, [(fc-80)/Fn, min((fc+80)/Fn, 0.99)], 'bandpass');
    xn = filter(b_nb, a_nb, x);
    for k = 1:nEnv
        seg = xn((k-1)*env_frame+1 : k*env_frame);
        tone_map(fi,k) = sum(seg.^2);
    end
end
t_env = ((1:nEnv)-0.5)*env_frame/fs;
imagesc(t_env, scan_f/1000, 10*log10(tone_map+EPS)); axis xy;
colorbar; colormap jet;
xlabel('Time (s)'); ylabel('kHz');
title('Narrowband Energy Map (tone search)');

sgtitle('Hidden Message Analysis', 'FontSize',14);

fprintf('\n>> Inspect figures for visual text, tonal patterns, or LSB data.\n');
fprintf('============ Done ============\n');

%% ========================================================================
%  LOCAL FUNCTIONS  (must be at the end of a MATLAB script)
%% ========================================================================

function S = stft_forward(x, win, hop, nfft)
%STFT_FORWARD  One-sided Short-Time Fourier Transform.
    x = x(:);  win = win(:);
    wlen    = length(win);
    nFrames = floor((length(x) - wlen) / hop) + 1;
    nBins   = nfft/2 + 1;
    S       = zeros(nBins, nFrames);
    for m = 1:nFrames
        i1 = (m-1)*hop + 1;
        frame = x(i1 : i1+wlen-1) .* win;
        X = fft(frame, nfft);
        S(:,m) = X(1:nBins);
    end
end

function x = stft_inverse(S, win, hop, nfft, origLen)
%STFT_INVERSE  Overlap-add inverse STFT from one-sided spectrum.
    win = win(:);
    wlen = length(win);
    [~, nFrames] = size(S);

    % Mirror to full spectrum
    S_full = [S; conj(S(end-1:-1:2, :))];

    outLen = (nFrames-1)*hop + wlen;
    x    = zeros(outLen, 1);
    wsum = zeros(outLen, 1);

    for m = 1:nFrames
        frame = real(ifft(S_full(:,m), nfft));
        frame = frame(1:wlen) .* win;
        i1 = (m-1)*hop + 1;
        i2 = i1 + wlen - 1;
        x(i1:i2)    = x(i1:i2)    + frame;
        wsum(i1:i2) = wsum(i1:i2) + win.^2;
    end
    x = x ./ (wsum + 1e-10);
    x = x(1:min(end, origLen));
end

function y = force_length(y, targetLen)
    y = y(:);
    if length(y) < targetLen
        y(end+1:targetLen,1) = 0;
    elseif length(y) > targetLen
        y = y(1:targetLen);
    end
end

function y = loudness_boost(y, targetRmsDb, peakTarget)
    y = y(:);
    y = y - mean(y);
    targetRms = 10^(targetRmsDb/20);
    rmsNow = sqrt(mean(y.^2) + 1e-12);
    y = y * (targetRms / (rmsNow + 1e-12));
    y = tanh(2.3 * y);
    y = y * (peakTarget / (max(abs(y)) + 1e-12));
end
