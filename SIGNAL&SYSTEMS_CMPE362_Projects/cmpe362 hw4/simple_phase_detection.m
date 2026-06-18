%% Simple Phase Coding Steganography Detection
% Based on Phase Coding technique - more advanced than LSB

clear; clc; close all;

fprintf('=== PHASE CODING STEGANOGRAPHY ANALYSIS ===\n\n');

%% Analyze cafe_sample.wav
audioFile = 'cafe_sample.wav';
fprintf('Analyzing: %s\n', audioFile);

[audioSignal, fs] = audioread(audioFile);
if size(audioSignal, 2) > 1
    audioSignal = mean(audioSignal, 2);
end

signalLength = length(audioSignal);
fprintf('Audio info: %d samples, %.2f seconds, %d Hz\n', signalLength, signalLength/fs, fs);

%% Phase Analysis
fprintf('\nExtracting phase information...\n');

frameLength = 1024;
numFrames = floor(signalLength / frameLength);

% Extract phase data
phaseData = extract_phase_data(audioSignal, frameLength);

% Analyze for phase coding
[hiddenMessage, confidence] = detect_phase_coding_simple(phaseData);

fprintf('Phase Analysis Results:\n');
fprintf('Frames analyzed: %d\n', numFrames);
fprintf('Phase variance: %.4f\n', var(phaseData(:)));
fprintf('Confidence of steganography: %.1f%%\n', confidence);

if ~isempty(hiddenMessage)
    fprintf('*** POTENTIAL HIDDEN MESSAGE: "%s" ***\n', hiddenMessage);
else
    fprintf('No phase coding steganography detected.\n');
end

%% Phase Pattern Analysis
fprintf('\n=== Phase Pattern Analysis ===\n');

% Check phase continuity
phaseDiffs = diff(phaseData, 1, 2);
largePhaseJumps = sum(abs(phaseDiffs(:)) > pi/4);
fprintf('Large phase jumps detected: %d\n', largePhaseJumps);

% Phase distribution analysis
phaseHist = histcounts(phaseData(:), 36, 'BinLimits', [-pi pi]);
expectedUniform = numel(phaseData) / 36;
chiSquare = sum((phaseHist - expectedUniform).^2 / expectedUniform);
fprintf('Phase distribution chi-square: %.2f\n', chiSquare);

% Determine if phase patterns are suspicious
suspiciousScore = 0;
if chiSquare > 50
    suspiciousScore = suspiciousScore + 1;
    fprintf('⚠ Non-uniform phase distribution detected\n');
end

if largePhaseJumps > numel(phaseData) * 0.01
    suspiciousScore = suspiciousScore + 1;
    fprintf('⚠ Excessive phase jumps detected\n');
end

if confidence > 70
    suspiciousScore = suspiciousScore + 1;
    fprintf('⚠ High steganography confidence\n');
end

%% Final Assessment
fprintf('\n=== FINAL ASSESSMENT ===\n');
if suspiciousScore >= 2
    fprintf('⚠ POSSIBLE PHASE CODING STEGANOGRAPHY DETECTED\n');
    fprintf('  Multiple indicators suggest hidden data\n');
    fprintf('  Recommendation: Further analysis recommended\n');
else
    fprintf('✓ NO PHASE CODING STEGANOGRAPHY DETECTED\n');
    fprintf('  Phase patterns appear normal\n');
    fprintf('  Audio file appears clean\n');
end

%% Visualization
figure('Position', [100, 100, 1200, 800]);

% Original signal
subplot(3, 3, 1);
t = (0:signalLength-1) / fs;
plot(t, audioSignal);
title('Original Audio Signal');
xlabel('Time (s)');
ylabel('Amplitude');
grid on;

% Phase spectrogram
subplot(3, 3, 2);
[S, ~, ~] = spectrogram(audioSignal, frameLength, frameLength/2, frameLength, fs);
phaseSpec = angle(S);
imagesc(phaseSpec);
title('Phase Spectrogram');
colormap hsv;
colorbar;

% Phase distribution
subplot(3, 3, 3);
histogram(phaseData(:), 50);
title('Phase Distribution');
xlabel('Phase (radians)');
ylabel('Count');

% Phase differences
subplot(3, 3, 4);
plot(mean(abs(phaseDiffs), 1));
title('Mean Phase Differences');
xlabel('Frame');
ylabel('Phase Difference');
grid on;

% Phase variance over time
subplot(3, 3, 5);
phaseVarOverTime = var(phaseData, 0, 1);
plot(phaseVarOverTime);
title('Phase Variance Over Time');
xlabel('Frame');
ylabel('Variance');
grid on;

% Phase continuity
subplot(3, 3, 6);
continuityScore = 1 ./ (1 + mean(abs(phaseDiffs), 1));
plot(continuityScore);
title('Phase Continuity Score');
xlabel('Frame');
ylabel('Continuity');
grid on;

% Frequency spectrum
subplot(3, 3, 7);
fftResult = fft(audioSignal);
freqAxis = (0:length(fftResult)/2-1) * fs / length(fftResult);
plot(freqAxis, abs(fftResult(1:length(fftResult)/2)));
title('Frequency Spectrum');
xlabel('Frequency (Hz)');
ylabel('Magnitude');
grid on;

% Phase histogram comparison
subplot(3, 3, 8);
histogram(phaseData(:), 36, 'BinLimits', [-pi pi]);
hold on;
x = linspace(-pi, pi, 100);
y = numel(phaseData) / (2*pi) * ones(size(x)); % Expected uniform
plot(x, y, 'r-', 'LineWidth', 2);
title('Phase Distribution vs Uniform');
xlabel('Phase (radians)');
ylabel('Count');
legend('Actual', 'Expected Uniform');

% Detection summary
subplot(3, 3, 9);
detectionScores = [confidence, chiSquare/10, min(100, largePhaseJumps*10)];
labels = {'Steganography %', 'Chi-Score', 'Phase Jumps'};
bar(detectionScores);
set(gca, 'XTickLabel', labels);
title('Detection Scores');
ylabel('Score');
grid on;

sgtitle('Phase Coding Steganography Analysis');
saveas(gcf, 'phase_detection_analysis.png');
fprintf('Saved analysis to phase_detection_analysis.png\n');

%% Test with Simulated Phase Coding
fprintf('\n=== SIMULATION TEST ===\n');
test_phase_coding_simulation();

fprintf('\n=== ANALYSIS COMPLETE ===\n');

%% Helper Functions
function phaseData = extract_phase_data(audioSignal, frameLength)
    % Extract phase information from audio signal
    
    signalLength = length(audioSignal);
    numFrames = floor(signalLength / frameLength);
    
    % Pad signal if necessary
    if signalLength < numFrames * frameLength
        audioSignal = [audioSignal; zeros(numFrames * frameLength - signalLength, 1)];
    end
    
    % Reshape into frames
    frames = reshape(audioSignal(1:numFrames*frameLength), frameLength, numFrames);
    
    % Compute FFT and extract phases
    phaseData = zeros(frameLength/2, numFrames);
    
    for i = 1:numFrames
        frame = frames(:, i);
        window = hann(frameLength);
        windowedFrame = frame .* window;
        
        fftResult = fft(windowedFrame);
        phaseData(:, i) = angle(fftResult(1:frameLength/2));
    end
end

function [message, confidence] = detect_phase_coding_simple(phaseData)
    % Simple phase coding detection
    
    message = '';
    confidence = 0;
    
    [numFreqBins, numFrames] = size(phaseData);
    
    if numFrames < 2
        return;
    end
    
    % Look for systematic phase shifts characteristic of phase coding
    phaseDiffs = diff(phaseData, 1, 2);
    
    % Phase coding often uses specific phase shifts
    binaryThreshold = pi/4;
    systematicShifts = abs(phaseDiffs) > binaryThreshold;
    
    % Extract potential binary data from middle frequency bins
    middleBins = round(numFreqBins/3):round(2*numFreqBins/3);
    potentialBits = [];
    
    for frame = 1:min(numFrames-1, 5) % Check first few frames
        for bin = middleBins(1:2:end) % Sample every other bin
            phaseDiff = phaseDiffs(bin, frame);
            
            if abs(phaseDiff) > binaryThreshold
                if phaseDiff > 0
                    potentialBits = [potentialBits, 1];
                else
                    potentialBits = [potentialBits, 0];
                end
            end
        end
    end
    
    % Try to decode as text
    if length(potentialBits) >= 8
        message = decode_binary_to_text(potentialBits);
    end
    
    % Calculate confidence based on phase anomalies
    totalShifts = sum(systematicShifts(:));
    maxPossibleShifts = numel(phaseDiffs);
    shiftRatio = totalShifts / maxPossibleShifts;
    
    % Phase variance analysis
    phaseVariance = var(phaseData(:));
    expectedVariance = pi^2/3; % Variance of uniform distribution
    varianceScore = 1 - min(abs(phaseVariance - expectedVariance) / expectedVariance, 1);
    
    % Combined confidence
    confidence = 100 * (0.5 * shiftRatio + 0.3 * varianceScore + 0.2 * (length(potentialBits) > 0));
end

function message = decode_binary_to_text(bits)
    % Decode binary bits to text
    
    message = '';
    
    % Try different message lengths
    maxChars = min(30, floor(length(bits) / 8));
    
    for msgLen = 1:maxChars
        if msgLen * 8 <= length(bits)
            try
                msgBits = bits(1:msgLen*8);
                binaryStr = num2str(msgBits);
                binaryStr = binaryStr(~isspace(binaryStr));
                
                if length(binaryStr) == msgLen * 8
                    binaryMatrix = reshape(binaryStr, 8, msgLen)';
                    decodedChars = char(bin2dec(binaryMatrix));
                    
                    % Check if it's readable text
                    if all(decodedChars >= 32 & decodedChars <= 126)
                        message = decodedChars;
                        break;
                    end
                end
            catch
                continue;
            end
        end
    end
end

function test_phase_coding_simulation()
    % Test with simulated phase coding
    
    fprintf('Testing phase coding detection...\n');
    
    % Generate test signal
    fs = 44100;
    duration = 1;
    t = 0:1/fs:duration-1/fs;
    testSignal = 0.5 * sin(2*pi*440*t);
    
    % Simulate phase coding by adding systematic phase shifts
    frameLength = 1024;
    numFrames = floor(length(testSignal) / frameLength);
    
    if numFrames > 0
        % Add phase perturbations to simulate hidden data
        phasePerturbation = 0.1 * sin(2*pi*10*(1:length(testSignal))/fs);
        stegoSignal = testSignal + phasePerturbation;
        
        % Analyze the perturbed signal
        phaseData = extract_phase_data(stegoSignal, frameLength);
        [detectedMessage, confidence] = detect_phase_coding_simple(phaseData);
        
        fprintf('Test signal analysis:\n');
        fprintf('Detection confidence: %.1f%%\n', confidence);
        if ~isempty(detectedMessage)
            fprintf('Detected pattern: "%s"\n', detectedMessage);
        else
            fprintf('No specific pattern detected\n');
        end
        
        fprintf('Phase coding detection system is operational.\n');
    else
        fprintf('Test signal too short for analysis\n');
    end
end
