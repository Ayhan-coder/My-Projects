%% Low Frequency Watermark Test Suite
% Tests low-frequency bands because many watermarks are embedded in the
% lower part of the spectrum.

clear; close all; clc;

fprintf('=== LOW FREQUENCY WATERMARK TEST SUITE ===\n\n');

%% Load audio
audioFile = 'cafe_sample.wav';
if ~isfile(audioFile)
    error('Input file %s not found.', audioFile);
end

[audio, fs] = audioread(audioFile);
if size(audio, 2) > 1
    audio = mean(audio, 2);
end

audio = audio(:);
audio(~isfinite(audio)) = 0;
nyq = fs / 2;
fprintf('Loaded %s: %.2f seconds at %d Hz\n\n', audioFile, length(audio) / fs, fs);

%% Optional: Speech-band bandpass/bandstop (300-3400 Hz)
% 300-3400 Hz is the classic "telephone" speech band.
% - Bandpass 300-3400: isolates intelligibility band (useful for speech extraction).
% - Bandstop 300-3400: removes speech band while preserving <300 Hz (useful if a
%   low-frequency watermark lives below ~300 Hz and speech is masking it).
bp = [];
bs = [];
audioBandpass = [];
audioBandstop = [];

lowHz = 300;
highHz = 3400;

if nyq > lowHz + 10
    highHzUse = min(highHz, nyq - 1);
    if highHzUse > lowHz
        try
            [bp, ap] = butter(6, [lowHz highHzUse] / nyq, 'bandpass');
            audioBandpass = filtfilt(bp, ap, audio);
            [bs, as] = butter(6, [lowHz highHzUse] / nyq, 'stop');
            audioBandstop = filtfilt(bs, as, audio);
            fprintf('Prepared optional 300-%.0f Hz bandpass and bandstop versions.\n\n', highHzUse);
        catch
            fprintf('Skipping optional 300-3400 Hz filters (filter design failed).\n\n');
        end
    end
end

%% 1. Low-frequency band energy scan
fprintf('Step 1: Scanning low-frequency bands...\n');
bandEdges = [20 80; 80 150; 150 300; 300 500; 500 800; 800 1200; 1200 2000];
bandStats = analyze_low_frequency_bands(audio, fs, bandEdges);

fprintf('Low-frequency band summary:\n');
for i = 1:numel(bandStats)
    fprintf('  [%4d-%4d Hz] energy ratio = %.4f, crest factor = %.2f, rms = %.5f\n', ...
        bandStats(i).lowHz, bandStats(i).highHz, bandStats(i).energyRatio, ...
        bandStats(i).crestFactor, bandStats(i).rmsLevel);
end
fprintf('\n');

%% 2. Carrier sweep in the low-frequency domain
fprintf('Step 2: Searching for suspicious low-frequency carriers...\n');
carrierResults = scan_low_frequency_carriers(audio, fs, 20, 2000);

% If we computed a bandstop version, re-scan it too (often increases SNR for
% sub-300 Hz carriers by removing the speech band energy).
carrierResultsBandstop = struct([]);
if ~isempty(audioBandstop)
    fprintf('Step 2b: Re-scanning carriers after bandstop (300-3400 Hz)...\n');
    carrierResultsBandstop = scan_low_frequency_carriers(audioBandstop, fs, 20, 2000);
    if isempty(carrierResultsBandstop)
        fprintf('  No strong candidates found after bandstop.\n\n');
    else
        fprintf('Carrier candidates after bandstop:\n');
        for i = 1:numel(carrierResultsBandstop)
            decodedText = carrierResultsBandstop(i).decodedText;
            if isempty(decodedText)
                decodedText = '(no readable decode)';
            end
            fprintf('  #%d  %.1f Hz | peak SNR = %.1f dB | pulses = %d | decode = %s\n', ...
                i, carrierResultsBandstop(i).carrierHz, carrierResultsBandstop(i).peakSNRdB, ...
                carrierResultsBandstop(i).pulseCount, decodedText);
        end
        fprintf('\n');
    end
end

if isempty(carrierResults)
    fprintf('  No strong low-frequency carrier candidates found.\n\n');
else
    fprintf('Low-frequency carrier candidates:\n');
    for i = 1:numel(carrierResults)
        decodedText = carrierResults(i).decodedText;
        if isempty(decodedText)
            decodedText = '(no readable decode)';
        end
        fprintf('  #%d  %.1f Hz | peak SNR = %.1f dB | pulses = %d | decode = %s\n', ...
            i, carrierResults(i).carrierHz, carrierResults(i).peakSNRdB, ...
            carrierResults(i).pulseCount, decodedText);
    end
    fprintf('\n');
end

%% 3. Low-frequency zoom spectrogram
fprintf('Step 3: Generating low-frequency spectrogram...\n');
figure('Name', 'Low Frequency Watermark Scan', 'NumberTitle', 'off', 'Position', [80 80 1400 800]);

subplot(2,2,1);
[pxx, f] = pwelch(audio, hann(8192), 4096, 8192, fs);
plot(f, 10 * log10(pxx + eps), 'k');
xlim([0 2000]);
grid on;
title('PSD Focused on Low Frequencies');
xlabel('Frequency (Hz)');
ylabel('Power (dB)');

subplot(2,2,2);
bandLabels = compose('%d-%d Hz', bandEdges(:,1), bandEdges(:,2));
barh(categorical(bandLabels), [bandStats.energyRatio], 'FaceColor', [0.2 0.5 0.8]);
title('Low-Frequency Band Energy Ratio');
xlabel('Energy ratio');

subplot(2,2,3);
spectrogram(audio, hann(2048), 1536, 4096, fs, 'yaxis');
title('Full Spectrogram');
ylim([0 2]);
colormap hot;

subplot(2,2,4);
if isempty(carrierResults)
    text(0.05, 0.5, 'No strong candidates found in 20-2000 Hz.', 'FontSize', 11);
    axis off;
else
    stem([carrierResults.carrierHz], [carrierResults.peakSNRdB], 'filled');
    grid on;
    title('Carrier Peaks Ranked by SNR');
    xlabel('Frequency (Hz)');
    ylabel('Peak SNR (dB)');
end

sgtitle('Low-Frequency Watermark Analysis');
saveas(gcf, 'low_frequency_watermark_scan.png');
fprintf('Saved low_frequency_watermark_scan.png\n\n');

%% 4. Synthetic validation test
fprintf('Step 4: Synthetic validation with a known low-frequency watermark...\n');
[testAudio, testFs, secretText, testCarrierHz] = create_low_frequency_ook_test('LOW FREQ', 240);
testResults = scan_low_frequency_carriers(testAudio, testFs, 100, 500);

normalizedSecret = normalize_text(secretText);
validated = false;

for i = 1:numel(testResults)
    if strcmp(normalize_text(testResults(i).decodedText), normalizedSecret)
        validated = true;
        fprintf('  PASS: recovered "%s" from synthetic %.1f Hz watermark.\n', ...
            testResults(i).decodedText, testResults(i).carrierHz);
        break;
    end
end

if ~validated
    fprintf('  FAIL: synthetic watermark at %.1f Hz did not decode cleanly.\n', testCarrierHz);
end

fprintf('\n=== CONCLUSION ===\n');
if isempty(carrierResults)
    fprintf('No strong low-frequency watermark was confirmed in the real audio.\n');
else
    topCandidate = carrierResults(1);
    fprintf('Top low-frequency candidate: %.1f Hz, decode = %s\n', ...
        topCandidate.carrierHz, fallback_text(topCandidate.decodedText, '(none)'));
end
fprintf('Synthetic test %s.\n', ternary(validated, 'passed', 'did not pass'));

%% Helper functions
function bandStats = analyze_low_frequency_bands(audio, fs, bandEdges)
    nBands = size(bandEdges, 1);
    bandStats = repmat(struct('lowHz', 0, 'highHz', 0, 'energyRatio', 0, ...
        'crestFactor', 0, 'rmsLevel', 0), nBands, 1);

    totalEnergy = sum(audio .^ 2) + eps;
    nyq = fs / 2;

    for idx = 1:nBands
        lowHz = bandEdges(idx, 1);
        highHz = bandEdges(idx, 2);
        highHz = min(highHz, nyq - 1);

        [b, a] = butter(4, [lowHz highHz] / nyq, 'bandpass');
        bandSignal = filtfilt(b, a, audio);

        bandEnergy = sum(bandSignal .^ 2);
        rmsLevel = sqrt(mean(bandSignal .^ 2) + eps);
        crestFactor = max(abs(bandSignal)) / (rmsLevel + eps);

        bandStats(idx).lowHz = lowHz;
        bandStats(idx).highHz = highHz;
        bandStats(idx).energyRatio = bandEnergy / totalEnergy;
        bandStats(idx).crestFactor = crestFactor;
        bandStats(idx).rmsLevel = rmsLevel;
    end
end

function carrierResults = scan_low_frequency_carriers(audio, fs, fmin, fmax)
    nyq = fs / 2;
    nfft = 16384;
    [pxx, f] = pwelch(audio, hann(nfft), nfft / 2, nfft, fs);
    baseline = medfilt1(pxx, 41, 'truncate');
    snrDb = 10 * log10((pxx + eps) ./ (baseline + eps));

    searchMask = f >= fmin & f <= min(fmax, nyq - 1);
    if ~any(searchMask)
        carrierResults = struct([]);
        return;
    end

    searchFreq = f(searchMask);
    searchSNR = snrDb(searchMask);
    [peakVals, peakLocs] = findpeaks(searchSNR, searchFreq, 'MinPeakHeight', 6, 'MinPeakDistance', 20);

    if isempty(peakLocs)
        carrierResults = struct([]);
        return;
    end

    [peakVals, order] = sort(peakVals, 'descend');
    peakLocs = peakLocs(order);

    carrierResults = repmat(struct('carrierHz', 0, 'peakSNRdB', 0, 'pulseCount', 0, ...
        'rawMorse', '', 'decodedText', '', 'confidence', 0), numel(peakLocs), 1);

    for idx = 1:numel(peakLocs)
        fc = peakLocs(idx);
        bw = max(10, min(40, round(fc * 0.08)));
        lowCut = max(2, fc - bw);
        highCut = min(nyq - 1, fc + bw);

        if lowCut >= highCut
            continue;
        end

        try
            [b, a] = butter(6, [lowCut highCut] / nyq, 'bandpass');
            isoSig = filtfilt(b, a, audio);
        catch
            continue;
        end

        isoSig(~isfinite(isoSig)) = 0;
        env = abs(hilbert(isoSig));
        env(~isfinite(env)) = 0;
        lpCut = min(20, max(5, fc / 6));
        [bLp, aLp] = butter(4, lpCut / nyq, 'low');
        env = filtfilt(bLp, aLp, env);

        [rawMorse, decodedText, pulseCount, confidence] = decode_morse_envelope(env, fs);

        carrierResults(idx).carrierHz = fc;
        carrierResults(idx).peakSNRdB = peakVals(idx);
        carrierResults(idx).pulseCount = pulseCount;
        carrierResults(idx).rawMorse = rawMorse;
        carrierResults(idx).decodedText = decodedText;
        carrierResults(idx).confidence = confidence;
    end

    carrierResults = carrierResults([carrierResults.carrierHz] > 0);
end

function [rawMorse, decodedText, pulseCount, confidence] = decode_morse_envelope(env, fs)
    rawMorse = '';
    decodedText = '';
    pulseCount = 0;
    confidence = 0;

    env = env(:);
    env(isnan(env) | isinf(env)) = 0;

    maxEnv = max(abs(env));
    if maxEnv < 1e-12
        return;
    end

    thresh = 0.45 * maxEnv;
    transitions = diff([0; env > thresh; 0]);
    rises = find(transitions == 1);
    falls = find(transitions == -1);
    pulseCount = min(numel(rises), numel(falls));

    if pulseCount < 4
        return;
    end

    durs = (falls(1:pulseCount) - rises(1:pulseCount)) / fs;
    validPulse = durs > 0.02;
    durs = durs(validPulse);
    if numel(durs) < 4
        return;
    end

    pulseCount = numel(durs);
    baseUnit = median(durs(durs < median(durs) * 1.8));
    if isnan(baseUnit) || baseUnit <= 0
        return;
    end

    symbols = repmat('.', 1, pulseCount);
    symbols(durs >= baseUnit * 2) = '-';

    gapCount = min(numel(rises), numel(falls)) - 1;
    if gapCount > 0
        gaps = (rises(2:gapCount + 1) - falls(1:gapCount)) / fs;
        gaps = gaps(validPulse(1:gapCount));
    else
        gaps = [];
    end

    if isempty(symbols)
        return;
    end

    for k = 1:numel(symbols)
        rawMorse(end + 1) = symbols(k); %#ok<AGROW>
        if k <= numel(gaps)
            if gaps(k) > baseUnit * 4
                rawMorse = [rawMorse '   ']; %#ok<AGROW>
            elseif gaps(k) > baseUnit * 1.5
                rawMorse = [rawMorse ' ']; %#ok<AGROW>
            end
        end
    end

    decodedText = morse_decode(rawMorse);
    confidence = text_quality_score(decodedText);
end

function txt = morse_decode(morseStr)
    table = containers.Map( ...
        {'.-','-...','-.-.','-..','.','..-.','--.','....','..','.---', ...
         '-.-','.-..','--','-.','---','.--.','--.-','.-.','...','-', ...
         '..-','...-','.--','-..-','-.--','--..', ...
         '-----','.----','..---','...--','....-','.....','-....','--...','---..','----.'}, ...
        {'A','B','C','D','E','F','G','H','I','J', ...
         'K','L','M','N','O','P','Q','R','S','T', ...
         'U','V','W','X','Y','Z', ...
         '0','1','2','3','4','5','6','7','8','9'});

    words = strsplit(strtrim(morseStr), '   ');
    txt = '';

    for w = 1:numel(words)
        letters = strsplit(strtrim(words{w}), ' ');
        for l = 1:numel(letters)
            code = strtrim(letters{l});
            if isempty(code)
                continue;
            end

            if isKey(table, code)
                txt(end + 1) = table(code); %#ok<AGROW>
            else
                txt = [txt '[' code ']']; %#ok<AGROW>
            end
        end

        if w < numel(words)
            txt(end + 1) = ' '; %#ok<AGROW>
        end
    end
end

function score = text_quality_score(text)
    if isempty(text)
        score = 0;
        return;
    end

    printable = sum(text >= 32 & text <= 126) / length(text);
    letters = sum(isstrprop(text, 'alpha')) / length(text);
    commonWords = {'the', 'and', 'is', 'this', 'you', 'low', 'freq', 'watermark'};
    wordHits = 0;

    lowerText = lower(text);
    for i = 1:numel(commonWords)
        if contains(lowerText, commonWords{i})
            wordHits = wordHits + 1;
        end
    end

    score = min(1, 0.45 * printable + 0.35 * letters + 0.20 * (wordHits / numel(commonWords)));
end

function [signalOut, fsOut, secretText, carrierHz] = create_low_frequency_ook_test(secretTextIn, carrierHzIn)
    fsOut = 8000;
    carrierHz = carrierHzIn;
    secretText = secretTextIn;

    dot = 0.08;
    dash = 3 * dot;
    intraGap = dot;
    letterGap = 3 * dot;
    wordGap = 7 * dot;

    morseMap = containers.Map( ...
        {'A','B','C','D','E','F','G','H','I','J', ...
         'K','L','M','N','O','P','Q','R','S','T', ...
         'U','V','W','X','Y','Z', ...
         '0','1','2','3','4','5','6','7','8','9'}, ...
        {'.-','-...','-.-.','-..','.','..-.','--.','....','..','.---', ...
         '-.-','.-..','--','-.','---','.--.','--.-','.-.','...','-', ...
         '..-','...-','.--','-..-','-.--','--..', ...
         '-----','.----','..---','...--','....-','.....','--...','---..','----.',' '});

    morseString = '';
    normalized = upper(secretText);
    for i = 1:length(normalized)
        ch = normalized(i);
        if ch == ' '
            morseString = [morseString, repmat('0', 1, round(wordGap * fsOut))]; %#ok<AGROW>
            continue;
        end

        if ~isKey(morseMap, ch)
            continue;
        end

        code = morseMap(ch);
        for j = 1:length(code)
            if code(j) == '.'
                morseString = [morseString, repmat('1', 1, round(dot * fsOut))]; %#ok<AGROW>
            elseif code(j) == '-'
                morseString = [morseString, repmat('1', 1, round(dash * fsOut))]; %#ok<AGROW>
            end

            if j < length(code)
                morseString = [morseString, repmat('0', 1, round(intraGap * fsOut))]; %#ok<AGROW>
            end
        end

        if i < length(normalized)
            morseString = [morseString, repmat('0', 1, round(letterGap * fsOut))]; %#ok<AGROW>
        end
    end

    if isempty(morseString)
        error('Failed to generate synthetic watermark test signal.');
    end

    env = double(morseString(:) == '1');
    t = (0:length(env) - 1)' / fsOut;
    carrier = sin(2 * pi * carrierHz * t);
    signalOut = 0.35 * env .* carrier + 0.02 * sin(2 * pi * 60 * t);
    signalOut = signalOut / (max(abs(signalOut)) + eps);
end

function out = normalize_text(text)
    out = upper(regexprep(text, '[^A-Z0-9]', ''));
end

function text = fallback_text(value, fallback)
    if isempty(value)
        text = fallback;
    else
        text = value;
    end
end

function out = ternary(condition, trueText, falseText)
    if condition
        out = trueText;
    else
        out = falseText;
    end
end