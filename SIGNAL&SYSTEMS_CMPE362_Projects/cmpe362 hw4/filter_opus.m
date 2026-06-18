%%=========================================================================
%  HOMEWORK – Separate Speech from Music/Background using Digital Filters
%
%  Input :  cafe_sample.wav
%  Output:  speech_filtered.wav  → speech removed,  music/background kept
%           music_filtered.wav   → music  removed,  human speech kept
%
%  Naming convention (as stated in the assignment):
%     speech_filtered.wav  = "Human speech is filtered OUT"
%     music_filtered.wav   = "Background noise and music is filtered OUT"
%%=========================================================================
clear; clc; close all;

%% ======================== 1. LOAD THE AUDIO ============================
[x_raw, Fs] = audioread('cafe_sample.wav');

% Convert to mono if stereo (keep original for reference)
if size(x_raw, 2) > 1
    x = mean(x_raw, 2);
    fprintf('Stereo → Mono conversion performed.\n');
else
    x = x_raw;
end

N  = length(x);
t  = (0:N-1) / Fs;          % time axis (s)
Fn = Fs / 2;                % Nyquist frequency (Hz)

fprintf('Sample rate   : %d Hz\n', Fs);
fprintf('Nyquist freq  : %d Hz\n', Fn);
fprintf('Duration      : %.2f s\n', N/Fs);
fprintf('Total samples : %d\n\n', N);

%% ==================== 2. SPECTRAL ANALYSIS =============================
%  Look at the audio in time, frequency and time-frequency domains
%  so we can decide where to place our filter cutoffs.

NFFT  = 2^nextpow2(N);
X     = fft(x, NFFT);
fHz   = (0:NFFT/2-1) * Fs / NFFT;   % one-sided frequency axis
Xmag  = 20*log10(abs(X(1:NFFT/2)) + eps);

figure('Name','Input Audio Analysis','Position',[50 50 1400 850]);

% --- 2a. Waveform ---
subplot(3,1,1);
plot(t, x, 'Color', [0 0.45 0.74]);
xlabel('Time (s)'); ylabel('Amplitude');
title('Time-Domain Waveform – Mixed Audio'); grid on; axis tight;

% --- 2b. Magnitude spectrum ---
subplot(3,1,2);
plot(fHz, Xmag, 'Color', [0 0.45 0.74]);
hold on;
xline(300,  '--r', '300 Hz',  'LabelOrientation','horizontal','FontSize',8);
xline(3500, '--r', '3500 Hz', 'LabelOrientation','horizontal','FontSize',8);
hold off;
xlabel('Frequency (Hz)'); ylabel('Magnitude (dB)');
title('Single-Sided Magnitude Spectrum (speech band marked in red)');
xlim([0 min(Fn, 20000)]); grid on;

% --- 2c. Spectrogram ---
subplot(3,1,3);
winLen  = round(0.030 * Fs);           % 30 ms analysis window
worLen  = round(winLen * 0.75);        % 75 % overlap
nfftSp  = 4096;
spectrogram(x, hamming(winLen), worLen, nfftSp, Fs, 'yaxis');
title('Spectrogram – Mixed Audio'); colormap jet; colorbar;

%% ========================================================================
%  3. FILTER DESIGN
%  ========================================================================
%
%  Human speech characteristics
%  ────────────────────────────
%  • Voiced fundamental (F0)  :   80 – 300 Hz
%  • Vowel formants  (F1–F3)  :  250 – 3500 Hz   ← main energy
%  • Fricatives / sibilants   : 4000 – 8000 Hz
%
%  Music / cafe background
%  ───────────────────────
%  • Bass / kick drum          :  20 – 250 Hz
%  • Mid-range instruments     : 250 – 4000 Hz   (overlaps with speech!)
%  • Hi-hats, cymbals, air     : 4000 – 20000 Hz
%
%  Because speech and music OVERLAP in the 250–4000 Hz region, a perfect
%  separation is impossible with linear filters alone.  We do our best
%  by choosing cutoffs that capture the *majority* of speech energy while
%  discarding as much music as we can.
%
%  Plan
%  ────
%  Speech extraction  → Bandpass   300 – 3500 Hz  → music_filtered.wav
%  Music  extraction  → Bandstop   300 – 3500 Hz  → speech_filtered.wav
%                       (+ combine LPF and HPF for better bass/treble)
%  ========================================================================

% Common parameters
Flo   = 300;                 % lower passband edge (Hz)
Fhi   = 3500;                % upper passband edge (Hz)
Rp    = 1;                   % max passband ripple       (dB)
Rs    = 60;                  % min stopband attenuation   (dB)
Fstop_lo = 100;              % lower stopband edge (Hz)
Fstop_hi = 5000;             % upper stopband edge (Hz)

Wp = [Flo  Fhi ] / Fn;      % normalised passband edges
Ws = [Fstop_lo  Fstop_hi] / Fn;   % normalised stopband edges

%% ---------- 3a. ELLIPTIC IIR BANDPASS  (speech keeper) -----------------
%  Elliptic filters give the sharpest transition for a given order.
%  Use SOS (Second-Order Sections) for numerical stability.

[n_el, Wn_el] = ellipord(Wp, Ws, Rp, Rs);
[z, p, k] = ellip(n_el, Rp, Rs, Wn_el, 'bandpass');
[sos_el_bp, g_el_bp] = zp2sos(z, p, k);
fprintf('Elliptic bandpass  – order %d\n', 2*n_el);

% Verify stability
assert(all(abs(p) < 1), 'Bandpass filter is unstable!');

%% ---------- 3b. ELLIPTIC IIR BANDSTOP  (speech remover) ----------------
[z, p, k] = ellip(n_el, Rp, Rs, Wn_el, 'stop');
[sos_el_bs, g_el_bs] = zp2sos(z, p, k);
fprintf('Elliptic bandstop  – order %d\n', 2*n_el);

assert(all(abs(p) < 1), 'Bandstop filter is unstable!');

%% ---------- 3c. BUTTERWORTH LPF + HPF  (music, alternative) -----------
%  Keep bass (< 250 Hz)  and  treble (> 4000 Hz) separately,
%  then add them together.  Butterworth is maximally flat in passband.

ord_lp = 10;  ord_hp = 10;
[z, p, k] = butter(ord_lp, 250 / Fn, 'low');
[sos_lp, g_lp] = zp2sos(z, p, k);

[z, p, k] = butter(ord_hp, 4000 / Fn, 'high');
[sos_hp, g_hp] = zp2sos(z, p, k);

fprintf('Butterworth LPF    – order %d   (fc = 250 Hz)\n', ord_lp);
fprintf('Butterworth HPF    – order %d   (fc = 4000 Hz)\n', ord_hp);

%% ---------- 3d. CHEBYSHEV TYPE-II BANDSTOP (comparison) ----------------
%  Equiripple in the stop-band → flat passband, good for keeping music.

[z, p, k] = cheby2(8, Rs, [Flo Fhi]/Fn, 'stop');
[sos_c2, g_c2] = zp2sos(z, p, k);
fprintf('Chebyshev-II BS    – order %d\n', 16);

%% ---------- 3e. FIR BANDPASS  (linear-phase alternative) ---------------
%  Kaiser window FIR — linear phase, no group-delay distortion.

fir_order = 400;                   % high order → sharp transition
beta      = 7.8;                   % Kaiser β ≈ sidelobe control
b_fir_bp  = fir1(fir_order, [Flo Fhi]/Fn, 'bandpass', kaiser(fir_order+1, beta));
fprintf('FIR Kaiser BP      – order %d   (β = %.1f)\n', fir_order, beta);

%% ---------- 3f. FIR BANDSTOP (linear-phase alternative) ----------------
b_fir_bs = fir1(fir_order, [Flo Fhi]/Fn, 'stop', kaiser(fir_order+1, beta));
fprintf('FIR Kaiser BS      – order %d   (β = %.1f)\n\n', fir_order, beta);

%% ================ 4. VISUALISE FILTER RESPONSES =======================

figure('Name','Filter Frequency Responses','Position',[80 40 1400 800]);
nPts = 8192;

% (a) Elliptic bandpass
subplot(3,2,1);
[H1, f1] = freqz(sos_el_bp, nPts, Fs);
plot(f1, 20*log10(abs(H1)*g_el_bp + eps), 'b', 'LineWidth',1.3);
title(sprintf('Elliptic Bandpass (order %d)', 2*n_el));
xlabel('Hz'); ylabel('dB'); xlim([0 8000]); ylim([-80 5]); grid on;
hold on; xline(Flo,'--r'); xline(Fhi,'--r'); hold off;

% (b) Elliptic bandstop
subplot(3,2,2);
[H2, f2] = freqz(sos_el_bs, nPts, Fs);
plot(f2, 20*log10(abs(H2)*g_el_bs + eps), 'r', 'LineWidth',1.3);
title(sprintf('Elliptic Bandstop (order %d)', 2*n_el));
xlabel('Hz'); ylabel('dB'); xlim([0 8000]); ylim([-80 5]); grid on;
hold on; xline(Flo,'--r'); xline(Fhi,'--r'); hold off;

% (c) FIR bandpass
subplot(3,2,3);
[H3, f3] = freqz(b_fir_bp, 1, nPts, Fs);
plot(f3, 20*log10(abs(H3)+eps), 'Color',[0 0.6 0], 'LineWidth',1.3);
title(sprintf('FIR Kaiser Bandpass (order %d)', fir_order));
xlabel('Hz'); ylabel('dB'); xlim([0 8000]); ylim([-80 5]); grid on;
hold on; xline(Flo,'--r'); xline(Fhi,'--r'); hold off;

% (d) FIR bandstop
subplot(3,2,4);
[H4, f4] = freqz(b_fir_bs, 1, nPts, Fs);
plot(f4, 20*log10(abs(H4)+eps), 'm', 'LineWidth',1.3);
title(sprintf('FIR Kaiser Bandstop (order %d)', fir_order));
xlabel('Hz'); ylabel('dB'); xlim([0 8000]); ylim([-80 5]); grid on;
hold on; xline(Flo,'--r'); xline(Fhi,'--r'); hold off;

% (e) Butterworth LPF + HPF
subplot(3,2,5);
[Hlp, flp] = freqz(sos_lp, nPts, Fs);
[Hhp, fhp] = freqz(sos_hp, nPts, Fs);
plot(flp, 20*log10(abs(Hlp)*g_lp + eps), 'Color',[0.8 0.4 0], 'LineWidth',1.3); hold on;
plot(fhp, 20*log10(abs(Hhp)*g_hp + eps), 'Color',[0.5 0 0.8], 'LineWidth',1.3);
title('Butterworth LPF (250 Hz) + HPF (4 kHz)');
xlabel('Hz'); ylabel('dB'); xlim([0 8000]); ylim([-80 5]);
legend('LPF','HPF','Location','south'); grid on; hold off;

% (f) Chebyshev-II bandstop
subplot(3,2,6);
[H5, f5] = freqz(sos_c2, nPts, Fs);
plot(f5, 20*log10(abs(H5)*g_c2 + eps), 'Color',[0.6 0.3 0], 'LineWidth',1.3);
title('Chebyshev-II Bandstop (order 16)');
xlabel('Hz'); ylabel('dB'); xlim([0 8000]); ylim([-80 5]); grid on;
hold on; xline(Flo,'--r'); xline(Fhi,'--r'); hold off;

sgtitle('Designed Filter Frequency Responses');

%% =============== 5. POLE-ZERO PLOTS (educational) =====================

figure('Name','Pole-Zero Plots','Position',[150 100 1000 450]);

subplot(1,2,1);
zplane(sos_el_bp);
title('Elliptic Bandpass – Poles & Zeros');

subplot(1,2,2);
zplane(sos_el_bs);
title('Elliptic Bandstop – Poles & Zeros');

%% ======== 6. APPLY FILTERS (zero-phase via filtfilt) ==================
%  filtfilt applies the filter forward and backward → zero phase shift,
%  but effectively doubles the filter order.

fprintf('Applying filters...\n');

% ---------- Speech extraction (for music_filtered.wav) ------------------
%  IIR Elliptic bandpass
speech_iir  = filtfilt(sos_el_bp, g_el_bp, x);

%  FIR Kaiser bandpass
speech_fir  = filtfilt(b_fir_bp, 1, x);

% ---------- Music extraction (for speech_filtered.wav) ------------------
%  IIR Elliptic bandstop
music_iir   = filtfilt(sos_el_bs, g_el_bs, x);

%  Butterworth LPF + HPF combination
bass_part   = filtfilt(sos_lp, g_lp, x);
treble_part = filtfilt(sos_hp, g_hp, x);
music_lphp  = bass_part + treble_part;

%  Chebyshev-II bandstop
music_cheby = filtfilt(sos_c2, g_c2, x);

%  FIR Kaiser bandstop
music_fir   = filtfilt(b_fir_bs, 1, x);

%% ======= 7. PICK THE BEST COMBINATION & REFINE ========================
%  The elliptic filters provide the sharpest roll-off with the lowest
%  order, so they tend to give the cleanest separation.

% ----- Final speech signal -----
speech_final = speech_iir;

% Optional: slight pre-emphasis to brighten consonants
pre_emph_coeff = 0.97;
speech_final = filter([1, -pre_emph_coeff], 1, speech_final);

% ----- Final music signal -----
%  Combine IIR bandstop with Butterworth LPF+HPF for a fuller result
%  (bandstop keeps a bit of residual near the edges; LPF+HPF is cleaner)
alpha = 0.6;   % blending weight
music_final = alpha * music_iir + (1 - alpha) * music_lphp;

%% ======= 8. NORMALISE ==================================================
% Ensure no NaNs before normalization
speech_final(isnan(speech_final)) = 0;
music_final(isnan(music_final)) = 0;

speech_final = 0.95 * speech_final / (max(abs(speech_final)) + eps);
music_final  = 0.95 * music_final  / (max(abs(music_final))  + eps);

%% ======= 9. VISUALISE RESULTS ==========================================
figure('Name','Separation Results','Position',[60 20 1500 900]);

% --- Waveforms ---
subplot(3,2,1);
plot(t, x); axis tight; grid on;
xlabel('Time (s)'); ylabel('Amp');
title('Original Mixed Audio');

subplot(3,2,3);
plot(t, speech_final, 'b'); axis tight; grid on;
xlabel('Time (s)'); ylabel('Amp');
title('Extracted Speech → music\_filtered.wav');

subplot(3,2,5);
plot(t, music_final, 'r'); axis tight; grid on;
xlabel('Time (s)'); ylabel('Amp');
title('Extracted Music → speech\_filtered.wav');

% --- Spectrograms ---
subplot(3,2,2);
spectrogram(x, hamming(winLen), worLen, nfftSp, Fs, 'yaxis');
title('Spectrogram – Original'); colormap jet;

subplot(3,2,4);
spectrogram(speech_final, hamming(winLen), worLen, nfftSp, Fs, 'yaxis');
title('Spectrogram – Speech Extracted'); colormap jet;

subplot(3,2,6);
spectrogram(music_final, hamming(winLen), worLen, nfftSp, Fs, 'yaxis');
title('Spectrogram – Music Extracted'); colormap jet;

sgtitle('Speech / Music Separation Results');

%% ======= 10. SAVE OUTPUT FILES =========================================
%  speech_filtered.wav  →  speech is REMOVED,  music is audible
%  music_filtered.wav   →  music  is REMOVED,  speech is audible

audiowrite('speech_filtered.wav', music_final,  Fs);
audiowrite('music_filtered.wav',  speech_final, Fs);

fprintf('\n✓ speech_filtered.wav saved (speech removed, music audible)\n');
fprintf('✓ music_filtered.wav  saved (music removed, speech audible)\n');

% Uncomment below to listen in MATLAB:
% fprintf('\nPlaying extracted speech...\n');
% sound(speech_final, Fs); pause(N/Fs + 1);
% fprintf('Playing extracted music...\n');
% sound(music_final, Fs);

%% ========================================================================
%  11. COMPARISON OF ALL FILTER METHODS (supplementary figure)
%  ========================================================================

figure('Name','Method Comparison','Position',[100 50 1500 700]);

subplot(2,3,1);
spectrogram(speech_iir, hamming(winLen), worLen, nfftSp, Fs, 'yaxis');
title('Speech – Elliptic BP'); colormap jet;

subplot(2,3,2);
spectrogram(speech_fir, hamming(winLen), worLen, nfftSp, Fs, 'yaxis');
title('Speech – FIR Kaiser BP'); colormap jet;

subplot(2,3,3);
spectrogram(speech_final, hamming(winLen), worLen, nfftSp, Fs, 'yaxis');
title('Speech – Final (chosen)'); colormap jet;

subplot(2,3,4);
spectrogram(music_iir, hamming(winLen), worLen, nfftSp, Fs, 'yaxis');
title('Music – Elliptic BS'); colormap jet;

subplot(2,3,5);
spectrogram(music_lphp, hamming(winLen), worLen, nfftSp, Fs, 'yaxis');
title('Music – Butter LPF+HPF'); colormap jet;

subplot(2,3,6);
spectrogram(music_fir, hamming(winLen), worLen, nfftSp, Fs, 'yaxis');
title('Music – FIR Kaiser BS'); colormap jet;

sgtitle('Comparison of Different Filter Designs');

%% ========================================================================
%  12. BONUS: HIDDEN TEXT MESSAGE DETECTION
%  ========================================================================
%
%  The assignment says a text message is "periodically hidden" in the audio.
%  Common hiding methods:
%    (a) High-frequency tones (above ~15 kHz)
%    (b) LSB steganography in audio samples
%    (c) Visual pattern in spectrogram
%    (d) DTMF-style tones
%    (e) Morse-code-like ON/OFF keying of a carrier
%
%  We investigate all of these.

fprintf('\n========== BONUS: Hidden Message Analysis ==========\n');

% --- 12a. High-frequency spectrogram (look for patterns above 8 kHz) ---
figure('Name','Hidden Message Hunt','Position',[80 30 1500 900]);

subplot(3,2,1);
spectrogram(x, hamming(512), 480, 4096, Fs, 'yaxis');
title('Full Spectrogram (fine resolution)');
colormap jet; colorbar;

if Fn > 8000
    % Isolate high-frequency content
    [z, p, k] = butter(6, 8000/Fn, 'high');
    [sos_hf, g_hf] = zp2sos(z, p, k);
    x_hf = filtfilt(sos_hf, g_hf, x);
    
    subplot(3,2,2);
    spectrogram(x_hf, hamming(256), 240, 2048, Fs, 'yaxis');
    title('High-Freq Content > 8 kHz');
    colormap jet; colorbar;
end

% --- 12b. Very-high-frequency check (>15 kHz, near-ultrasonic) ---
if Fn > 15000
    [z, p, k] = butter(4, 15000/Fn, 'high');
    [sos_uf, g_uf] = zp2sos(z, p, k);
    x_uf = filtfilt(sos_uf, g_uf, x);
    
    subplot(3,2,3);
    spectrogram(x_uf, hamming(256), 240, 2048, Fs, 'yaxis');
    title('Near-Ultrasonic Content > 15 kHz');
    colormap jet; colorbar;
    
    % Energy over time in this band
    subplot(3,2,4);
    frame_sz = round(0.05 * Fs);   % 50 ms
    n_frames = floor(N / frame_sz);
    energy_hf = zeros(1, n_frames);
    for k = 1:n_frames
        seg = x_uf((k-1)*frame_sz+1 : k*frame_sz);
        energy_hf(k) = sum(seg.^2);
    end
    t_frames = ((1:n_frames) - 0.5) * frame_sz / Fs;
    plot(t_frames, energy_hf, 'b'); grid on;
    xlabel('Time (s)'); ylabel('Energy');
    title('High-Freq Energy Envelope (possible OOK signal)');
end

% --- 12c. LSB steganography check ---
subplot(3,2,5);
% Read the file as int16 to inspect least significant bits
info = audioinfo('cafe_sample.wav');
[x_int, ~] = audioread('cafe_sample.wav', 'native');
if isa(x_int, 'int16')
    lsb_bits = bitand(uint16(abs(x_int(:,1))), uint16(1));
    
    % Try to interpret as 8-bit ASCII (group every 8 LSBs)
    nBits   = length(lsb_bits);
    nChars  = floor(nBits / 8);
    bitMat  = double(reshape(lsb_bits(1:nChars*8), 8, nChars)');
    powers  = 2.^(7:-1:0);
    charVals = bitMat * powers';
    decoded_text = char(charVals');
    
    % Look for printable ASCII sequences
    printable = (charVals >= 32 & charVals <= 126);
    frac_print = sum(printable) / length(printable);
    
    fprintf('LSB analysis: %.1f%% printable ASCII chars\n', frac_print*100);
    if frac_print > 0.7
        fprintf('Possible LSB message (first 200 chars):\n');
        fprintf('  %s\n', decoded_text(1:min(200, length(decoded_text))));
    else
        fprintf('LSB data does not look like plain ASCII text.\n');
    end
    
    % Plot LSB bit-stream (look for periodicity)
    plot(lsb_bits(1:min(5000,nBits)), '.', 'MarkerSize', 1);
    title('LSB Bit Stream (first 5000 samples)');
    xlabel('Sample'); ylabel('LSB');
else
    text(0.3, 0.5, 'Not int16 format', 'FontSize', 14);
    title('LSB Analysis');
    fprintf('Audio is not 16-bit integer format.\n');
end

% --- 12d. Search for periodic narrow-band tones ---
subplot(3,2,6);
seg_len    = round(0.5 * Fs);           % 500 ms segments
n_seg      = floor(N / seg_len);
peak_freqs = [];

for k = 1:n_seg
    seg  = x((k-1)*seg_len+1 : k*seg_len);
    Seg  = abs(fft(seg));
    fSeg = (0:length(seg)-1) * Fs / length(seg);
    half = 1:floor(length(seg)/2);
    
    % Find prominent peaks
    [pks, locs] = findpeaks(Seg(half), 'MinPeakProminence', ...
                  5 * median(Seg(half)), 'NPeaks', 10);
    if ~isempty(locs)
        peak_freqs = [peak_freqs; k*ones(length(locs),1), fSeg(locs)'];
    end
end

if ~isempty(peak_freqs)
    plot(peak_freqs(:,1)*0.5, peak_freqs(:,2), '.', 'MarkerSize', 6);
    xlabel('Time (s)'); ylabel('Frequency (Hz)');
    title('Detected Tonal Peaks vs Time');
    grid on;
    
    % Look for frequencies that appear periodically
    unique_freqs = unique(round(peak_freqs(:,2) / 50) * 50);
    fprintf('\nPeriodic tonal peaks found at ~: ');
    fprintf('%g Hz  ', unique_freqs(unique_freqs > 100)');
    fprintf('\n');
else
    text(0.2, 0.5, 'No prominent periodic tones found', 'FontSize', 12);
    title('Periodic Tone Detection');
end

sgtitle('Hidden Message Analysis');

% --- 12e. DTMF detection attempt ---
fprintf('\n--- DTMF Tone Check ---\n');
dtmf_low  = [697 770 852 941];
dtmf_high = [1209 1336 1477 1633];
dtmf_chars = ['1','2','3','A'; '4','5','6','B'; ...
              '7','8','9','C'; '*','0','#','D'];

seg_dur = 0.08;   % 80 ms per DTMF symbol (minimum)
seg_samps = round(seg_dur * Fs);
n_dtmf_seg = floor(N / seg_samps);
dtmf_msg = '';

for k = 1:n_dtmf_seg
    seg = x((k-1)*seg_samps+1 : k*seg_samps);
    S_seg = abs(fft(seg));
    f_seg = (0:length(seg)-1) * Fs / length(seg);
    
    % Check each DTMF frequency pair
    best_score = 0;
    best_char  = ' ';
    for r = 1:4
        for c = 1:4
            idx_lo = find(abs(f_seg - dtmf_low(r)) < 20, 1);
            idx_hi = find(abs(f_seg - dtmf_high(c)) < 20, 1);
            if ~isempty(idx_lo) && ~isempty(idx_hi)
                score = S_seg(idx_lo) * S_seg(idx_hi);
                if score > best_score
                    best_score = score;
                    best_char  = dtmf_chars(r, c);
                end
            end
        end
    end
    
    median_energy = median(S_seg(2:end/2));
    if best_score > (50 * median_energy^2)
        dtmf_msg = [dtmf_msg, best_char];
    end
end

% Remove consecutive duplicates
dtmf_clean = dtmf_msg;
if length(dtmf_clean) > 1
    keep = [true, diff(dtmf_clean) ~= 0];
    dtmf_clean = dtmf_clean(keep);
end

if ~isempty(dtmf_clean)
    fprintf('Possible DTMF sequence: %s\n', dtmf_clean);
    
    % Attempt to decode as hex (A-D used as 10-13), ignoring * and #
    dtmf_hex = upper(regexprep(dtmf_clean, '[^0-9A-D]', ''));
    % If odd length, drop last nibble
    if mod(length(dtmf_hex),2) == 1
        dtmf_hex = dtmf_hex(1:end-1);
    end
    decoded_chars = [];
    for i = 1:2:length(dtmf_hex)
        byte_str = dtmf_hex(i:i+1);
        val = hex2dec(strrep(strrep(strrep(strrep(byte_str, 'A','A'), 'B','B'), 'C','C'), 'D','D'));
        if val >= 32 && val <= 126
            decoded_chars(end+1) = char(val); %#ok<AGROW>
        else
            decoded_chars(end+1) = '.'; %#ok<AGROW>
        end
    end
    decoded_text_hex = char(decoded_chars);
    fprintf('DTMF hex-decode (printables): %s\n', decoded_text_hex);
    
    keys = [0 32 48 85 170 255];
    best_score = -Inf; best_text = '';
    for offset = 0:1
        s = dtmf_hex(1+offset:end);
        if mod(length(s),2) == 1
            s = s(1:end-1);
        end
        if isempty(s)
            continue
        end
        bytes = zeros(1, length(s)/2);
        idx = 1;
        for ii = 1:2:length(s)
            bytes(idx) = hex2dec(s(ii:ii+1));
            idx = idx + 1;
        end
        for kk = 1:length(keys)
            dec = bitxor(uint8(bytes), uint8(keys(kk)));
            str = char(dec);
            printable = (dec >= 32 & dec <= 126);
            score = sum(printable) / numel(dec);
            if contains(str,'CMPE','IgnoreCase',true), score = score + 0.1; end
            if contains(str,'HW','IgnoreCase',true), score = score + 0.05; end
            if contains(str,'HIDDEN','IgnoreCase',true), score = score + 0.2; end
            if contains(str,'MESSAGE','IgnoreCase',true), score = score + 0.2; end
            if contains(str,'MERHABA','IgnoreCase',true) || contains(str,'GIZLI','IgnoreCase',true) || contains(str,'MESAJ','IgnoreCase',true) || contains(str,'ODEV','IgnoreCase',true)
                score = score + 0.2;
            end
            if score > best_score
                best_score = score; best_text = str;
            end
        end
    end
    if ~isempty(best_text)
        fprintf('DTMF best candidate: %s\n', best_text);
    end
    
    m = containers.Map({'2','3','4','5','6','7','8','9'}, ...
        {{'A','B','C'},{'D','E','F'},{'G','H','I'},{'J','K','L'}, ...
         {'M','N','O'},{'P','Q','R','S'},{'T','U','V'},{'W','X','Y','Z'}});
    s2 = dtmf_clean;
    res = '';
    i = 1;
    while i <= length(s2)
        d = s2(i);
        if isKey(m, d)
            j = i;
            while j <= length(s2) && s2(j) == d
                j = j + 1;
            end
            reps = j - i;
            vals = m(d);
            idx = mod(reps - 1, numel(vals)) + 1;
            res = [res vals{idx}];
            i = j;
        elseif d == '0' || d == '*' || d == '#'
            res = [res ' '];
            i = i + 1;
        else
            i = i + 1;
        end
    end
    if ~isempty(strtrim(res))
        fprintf('DTMF T9 candidate: %s\n', res);
    end
else
    fprintf('No DTMF tones detected.\n');
end

% --- 12f. Display spectrogram as image (visual steganography) ---
hImg = figure('Name','Spectrogram Image (Visual Message?)','Position',[200 150 1200 500]);

% Use different window sizes to reveal possible hidden images
subplot(1,2,1);
spectrogram(x, hamming(256), 250, 1024, Fs, 'yaxis');
title('Short Window (256 samples) – look for text/image');
colormap jet; colorbar; ylim([0 Fn/1000]);

subplot(1,2,2);
spectrogram(x, hamming(2048), 2000, 4096, Fs, 'yaxis');
title('Long Window (2048 samples) – look for text/image');
colormap jet; colorbar; ylim([0 Fn/1000]);

sgtitle('Visual Inspection: Is the message drawn in the spectrogram?');

fprintf('\n========== Analysis Complete ==========\n');
fprintf('Inspect all figures for the hidden message.\n');
fprintf('Look especially for patterns in the high-frequency spectrogram.\n');
try
    exportgraphics(hImg, 'hidden_message_spectrogram.png', 'Resolution', 300);
    fprintf('Saved spectrogram image: hidden_message_spectrogram.png\n');
catch
end
