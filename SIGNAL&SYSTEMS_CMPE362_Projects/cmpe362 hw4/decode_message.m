% decode_message.m
% CMPE362 HW4 – Bonus: Advanced Decoder for Hidden Periodic Messages
%
% This improved script uses DSP forensics to automatically locate where
% the message is hidden, rather than guessing frequencies.
%
% Approach:
%   1. Unnatural Tone Detection (PSD vs. Local Median Baseline)
%   2. Precision Amplitude Demodulation / Morse Decoding on found carriers
%   3. High-Contrast "Steganography" Spectrogram to find visual text

clear; close all; clc;
fprintf('=== CMPE362 HW4 – Advanced Audio Forensics ===\n\n');

%% Load Audio
[audio, fs] = audioread('cafe_sample.wav');
if size(audio, 2) == 2, audio = mean(audio, 2); end
N = length(audio);
nyq = fs / 2;
fprintf('Loaded cafe_sample.wav (%.2f seconds, %d Hz)\n\n', N/fs, fs);

%% 1. AUTO-DETECT HIDDEN CARRIER FREQUENCIES
fprintf('Step 1: Automatically scanning spectrum for unnatural tonal peaks...\n');

% Compute high-resolution Power Spectral Density
nfft = 16384;
[pxx, f] = pwelch(audio, hann(nfft), nfft/2, nfft, fs);

% To find "hidden tones" buried in music, we compare the PSD to a heavily
% smoothed version of itself (the underlying "noise/music floor").
baseline = medfilt1(pxx, 200);   % 200-bin median filter
snr_db = 10 * log10(pxx ./ (baseline + 1e-12));

% Look for exceedingly sharp peaks that stand > 15 dB above the local floor
[pks, locs] = findpeaks(snr_db, 'MinPeakHeight', 12, 'MinPeakDistance', 50);
carriers = f(locs);

% Filter out extreme low frequencies (bass notes in music)
carriers = carriers(carriers > 500 & carriers < nyq - 100);

if isempty(carriers)
    fprintf('  No obvious continuous/repeating tones detected via PSD.\n');
    fprintf('  Falling back to standard candidate carriers...\n');
    carriers = [1000, 1500, 4000, 16000, 18000]; % common hiding spots
else
    fprintf('  Detected suspicious narrow-band tones at:\n');
    for i = 1:length(carriers)
        fprintf('    - %.1f Hz (SNR magnitude: %.1f dB)\n', carriers(i), pks(i));
    end
end
fprintf('\n');

%% 2. AMPLITUDE DEMODULATION (MORSE CODE SCAN)
fprintf('Step 2: Demodulating carriers and checking for Morse Code / OOK...\n');
bw = 50; % narrow bandpass half-width

for fc = carriers'
    % If a detected frequency is too close to Nyquist, it breaks the filter design
    if (fc + bw) >= nyq
        fprintf('  Skipping %.1f Hz (too close to Nyquist)\n', fc);
        continue; 
    end
    
    % Precision bandpass filter around the target frequency
    try
        [b, a] = butter(6, [(fc-bw) (fc+bw)] / nyq, 'bandpass');
        iso_sig = filtfilt(b, a, audio);
    catch
        fprintf('  Failed to design filter for %.1f Hz, skipping.\n', fc);
        continue;
    end
    
    % Enveloping via abs() + low-pass (Hilberts on noise can blow up)
    % A simple rectifier + lowpass is safer than hilbert() for high frequencies
    env = abs(iso_sig);
    
    % Low-pass the envelope to remove high-frequency flutter natively
    [b_lp, a_lp] = butter(4, 20 / nyq, 'low'); % Limit to 20 Hz max keying rate
    
    % Ensure no NaNs or Infs from mathematical anomalies
    env(isnan(env) | isinf(env)) = 0;
    
    env_smooth = filtfilt(b_lp, a_lp, env);
    
    % Normalize envelope for easier thresholding
    max_env = max(abs(env_smooth));
    if max_env < 1e-12, continue; end
    
    thresh = 0.4 * max_env;
    is_on = diff([0; env_smooth > thresh; 0]);
    rises = find(is_on == 1);
    falls = find(is_on == -1);
    
    np = min(length(rises), length(falls));
    if np < 5, continue; end % Need at least a few pulses to be a message
    
    % Durations of marks (tones) and spaces (silence)
    durs = (falls(1:np) - rises(1:np)) / fs;
    valid_pulses = durs > 0.02; % ignore sub-20ms ultra-glitches
    durs = durs(valid_pulses);
    if length(durs) < 5, continue; end
    
    % Group durations into dots and dashes using K-Means or basic logic
    dot_est = median(durs(durs < median(durs)*1.8)); % estimate of "1 unit"
    if isnan(dot_est) || dot_est == 0, continue; end
    
    syms = repmat('.', 1, length(durs));
    syms(durs >= dot_est * 2) = '-'; % dash is typically 3x a dot
    
    % Evaluate gaps
    gaps = (rises(2:np) - falls(1:np-1)) / fs;
    gaps = gaps(valid_pulses(1:end-1));
    
    % Construct Morse String
    mstr = '';
    for k = 1:length(syms)
        mstr(end+1) = syms(k); %#ok<AGROW>
        if k <= length(gaps)
            if gaps(k) > dot_est * 4
                mstr = [mstr, '   ']; %#ok<AGROW> % Word gap
            elseif gaps(k) > dot_est * 1.5
                mstr = [mstr, ' '];   %#ok<AGROW> % Letter gap
            end
        end
    end
    
    decoded = morse_decode(mstr);
    
    fprintf('► Analyzing %.1f Hz:\n', fc);
    fprintf('  Pulses : %d  | Base unit ≈ %.3f s\n', length(durs), dot_est);
    fprintf('  Raw    : %s\n', mstr);
    if ~isempty(strrep(decoded, '[]', '')) && length(decoded) > 2
        fprintf('  Decoded: %s\n\n', decoded);
    else
        fprintf('  Decoded: (No intelligible alphanumeric characters found)\n\n');
    end
end

%% 3. HIGH-CONTRAST VISUAL SPECTROGRAM (Look for Drawn Text)
% Sometimes messages are literal text drawn into the spectrogram at frequencies
% perfectly above the music (e.g., 15k - 20kHz).
fprintf('Step 3: Generating precision high-contrast visual spectrograms...\n');

figure('Name','Steganography / Hidden Text Scan','NumberTitle','off','Position',[50 50 1400 800]);

% Plot 1: Full Range up to Nyquist (Boosted Contrast)
subplot(2,1,1);
spectrogram(audio, hann(2048), 1536, 4096, fs, 'yaxis');
title('Full Frequency Spectrum (Boosted Contrast)');
colormap hot; colorbar;
caxis([-100 -20]); % Push background noise to black to highlight hidden structures

% Plot 2: High Frequency Zoom (12kHz - 22kHz)
% Many acoustic watermarks exist above human hearing
subplot(2,1,2);
spectrogram(audio, hann(1024), 768, 2048, fs, 'yaxis');
title('High-Frequency Zoom (Look here for visual text or FSK lines)');
ylim([12, 22]); % Zoom in on 12kHz to 22kHz
colormap hot; colorbar;
caxis([-110 -30]); 

saveas(gcf, 'hidden_message_visual_scan.png');
fprintf('  Saved hidden_message_visual_scan.png\n');
fprintf('  --> Manually open this image and look for literal text or distinct dashed lines.\n\n');

%% HELPER FUNCTION: Morse-to-ASCII
function txt = morse_decode(morse_str)
    table = containers.Map( ...
        {'.-','-...','-.-.','-..','.','..-.','--.','....','..','.---', ...
         '-.-','.-..','--','-.','---','.--.','--.-','.-.','...','-', ...
         '..-','...-','.--','-..-','-.--','--..', ...
         '-----','.----','..---','...--','....-','.....','-....','--...','---..','----.'}, ...
        {'A','B','C','D','E','F','G','H','I','J', ...
         'K','L','M','N','O','P','Q','R','S','T', ...
         'U','V','W','X','Y','Z', ...
         '0','1','2','3','4','5','6','7','8','9'});
    words = strsplit(strtrim(morse_str), '   ');
    txt = '';
    for w = 1:length(words)
        for letter = strsplit(strtrim(words{w}), ' ')
            c = strtrim(letter{1});
            if isKey(table, c)
                txt(end+1) = table(c);  %#ok<AGROW>
            elseif ~isempty(c)
                txt = [txt '[' c ']'];   %#ok<AGROW>
            end
        end
        if w < length(words), txt(end+1) = ' '; end  %#ok<AGROW>
    end
end
