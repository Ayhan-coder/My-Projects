%% Phase Coding Steganography Detection and Analysis
% Based on Phase Coding technique by Bender et al. (1996)
% More advanced than LSB - hides data in phase information

clear; clc; close all;

%% Input Audio File
audioFile = 'cafe_sample.wav'; % Change to test different files
if ~isfile(audioFile)
    error('Input file %s not found.', audioFile);
end

fprintf('=== PHASE CODING STEGANOGRAPHY ANALYSIS ===\n');
fprintf('Analyzing audio file for phase coding steganography: %s\n', audioFile);

%% Load Audio Signal
[audioSignal, fs] = audioread(audioFile);
if size(audioSignal, 2) > 1
    audioSignal = mean(audioSignal, 2); % Convert to mono if stereo
end

signalLength = length(audioSignal);
fprintf('Audio loaded: %d samples, %.2f seconds, %d Hz\n', ...
    signalLength, signalLength/fs, fs);

%% Phase Coding Analysis
fprintf('\n=== Phase Coding Detection ===\n');

% Parameters for phase coding analysis
frameLength = 1024; % Standard frame length
numFrames = floor(signalLength / frameLength);

if numFrames < 2
    fprintf('Audio too short for phase coding analysis\n');
    return;
end

% Extract phase information
phaseData = extract_phase_information(audioSignal, frameLength);

% Analyze phase patterns for hidden data
[hiddenMessage, confidence, phaseAnomalies] = detect_phase_coding(phaseData, frameLength);

% Display results
if ~isempty(hiddenMessage)
    fprintf('*** PHASE CODING DETECTED ***\n');
    fprintf('Hidden message: "%s"\n', hiddenMessage);
    fprintf('Confidence: %.2f%%\n', confidence);
    fprintf('Phase anomalies detected: %d\n', phaseAnomalies);
else
    fprintf('No phase coding steganography detected.\n');
    fprintf('Phase patterns appear normal.\n');
end

%% Advanced Phase Analysis
fprintf('\n=== Advanced Phase Analysis ===\n');

% Multiple detection methods
results = comprehensive_phase_analysis(audioSignal, fs, frameLength);

% Display comprehensive results
fprintf('Phase Analysis Results:\n');
for i = 1:length(results)
    fprintf('Method %d: "%s" (Confidence: %.1f%%)\n', ...
        i, results(i).message, results(i).confidence);
end

%% Phase Visualization
figure('Position', [100, 100, 1400, 900]);

% Original signal
subplot(4, 3, 1);
t = (0:signalLength-1) / fs;
plot(t, audioSignal);
title('Original Audio Signal');
xlabel('Time (s)');
ylabel('Amplitude');
grid on;

% Phase spectrogram
subplot(4, 3, 2);
phase_spectrogram(audioSignal, frameLength, fs);
title('Phase Spectrogram');
colorbar;

% Phase distribution
subplot(4, 3, 3);
plot_phase_distribution(phaseData);
title('Phase Distribution');
xlabel('Phase (radians)');
ylabel('Frequency');

% Phase differences
subplot(4, 3, 4);
plot_phase_differences(phaseData);
title('Phase Differences Between Frames');
xlabel('Frame');
ylabel('Phase Difference');

% Phase anomaly detection
subplot(4, 3, 5);
detect_phase_anomalies_plot(phaseData);
title('Phase Anomaly Detection');
xlabel('Frame Index');
ylabel('Anomaly Score');

% Histogram of phase values
subplot(4, 3, 6);
histogram(phaseData(:), 50);
title('Phase Value Histogram');
xlabel('Phase (radians)');
ylabel('Count');

% Phase continuity analysis
subplot(4, 3, 7);
analyze_phase_continuity(phaseData);
title('Phase Continuity Analysis');
xlabel('Frame');
ylabel('Continuity Score');

% Frequency domain analysis
subplot(4, 3, 8);
analyze_frequency_domain(audioSignal, fs);
title('Frequency Domain Analysis');
xlabel('Frequency (Hz)');
ylabel('Magnitude');

% Phase coding simulation
subplot(4, 3, 9);
simulate_phase_coding();
title('Phase Coding Pattern Example');
xlabel('Sample');
ylabel('Phase');

% Statistical analysis
subplot(4, 3, 10);
phase_statistical_analysis(phaseData);
title('Phase Statistical Analysis');

% Time-frequency phase analysis
subplot(4, 3, 11);
time_frequency_phase_analysis(audioSignal, fs);
title('Time-Frequency Phase Analysis');

% Summary plot
subplot(4, 3, 12);
plot_detection_summary(results);
title('Detection Summary');

sgtitle('Phase Coding Steganography Analysis');
saveas(gcf, 'phase_coding_analysis.png');
fprintf('Saved phase analysis to phase_coding_analysis.png\n');

%% Test with Phase Coding (Demonstration)
fprintf('\n=== Phase Coding Demonstration ===\n');
test_phase_coding();

fprintf('\n=== Analysis Complete ===\n');

%% Phase Coding Detection Functions
function phaseData = extract_phase_information(audioSignal, frameLength)
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
    phaseData = zeros(frameLength/2, numFrames); % Only need positive frequencies
    
    for i = 1:numFrames
        frame = frames(:, i);
        window = hann(frameLength);
        windowedFrame = frame .* window;
        
        fftResult = fft(windowedFrame);
        phaseData(:, i) = angle(fftResult(1:frameLength/2));
    end
end

function [message, confidence, anomalies] = detect_phase_coding(phaseData, frameLength)
    % Detect phase coding patterns in phase data
    
    message = '';
    confidence = 0;
    anomalies = 0;
    
    [numFreqBins, numFrames] = size(phaseData);
    
    if numFrames < 2
        return;
    end
    
    % Method 1: Look for binary patterns in phase differences
    phaseDiffs = diff(phaseData, 1, 2); % Differences between adjacent frames
    
    % Check for characteristic phase coding patterns
    % Phase coding often uses ±π/2 phase shifts
    binaryThreshold = pi/4; % Threshold for detecting binary phase shifts
    
    % Extract potential binary data from middle frequency bins
    middleBins = round(numFreqBins/4):round(3*numFreqBins/4);
    potentialBits = [];
    
    for frame = 1:min(numFrames-1, 10) % Check first few frames
        for bin = middleBins
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
        message = decode_phase_bits(potentialBits);
        confidence = calculate_phase_confidence(phaseData, potentialBits);
    end
    
    % Count phase anomalies
    anomalies = sum(abs(phaseDiffs(:)) > binaryThreshold);
end

function message = decode_phase_bits(bits)
    % Decode bits to text message
    
    message = '';
    
    % Try different message lengths
    maxChars = min(50, floor(length(bits) / 8));
    
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

function confidence = calculate_phase_confidence(phaseData, extractedBits)
    % Calculate confidence score for phase coding detection
    
    confidence = 0;
    
    % Check for non-random phase patterns
    [numFreqBins, numFrames] = size(phaseData);
    
    % Phase variance analysis
    phaseVariance = var(phaseData(:));
    expectedVariance = pi^2/3; % Variance of uniform distribution
    
    varianceScore = 1 - min(abs(phaseVariance - expectedVariance) / expectedVariance, 1);
    
    % Phase continuity analysis
    phaseDiffs = diff(phaseData, 1, 2);
    continuityScore = 1 - mean(abs(phaseDiffs(:)) > pi/2);
    
    % Binary pattern analysis
    if length(extractedBits) > 0
        binaryScore = min(length(extractedBits) / 64, 1); % More bits = higher confidence
    else
        binaryScore = 0;
    end
    
    % Combined confidence
    confidence = 100 * (0.3 * varianceScore + 0.3 * continuityScore + 0.4 * binaryScore);
end

function results = comprehensive_phase_analysis(audioSignal, fs, frameLength)
    % Comprehensive analysis using multiple phase coding detection methods
    
    results = struct();
    
    % Method 1: Standard phase coding detection
    phaseData = extract_phase_information(audioSignal, frameLength);
    [msg1, conf1, ~] = detect_phase_coding(phaseData, frameLength);
    results(1).message = msg1;
    results(1).confidence = conf1;
    results(1).method = 'Standard Phase Coding';
    
    % Method 2: Phase difference analysis
    [msg2, conf2] = analyze_phase_differences_method(phaseData);
    results(2).message = msg2;
    results(2).confidence = conf2;
    results(2).method = 'Phase Difference Analysis';
    
    % Method 3: Frequency-specific phase analysis
    [msg3, conf3] = frequency_phase_analysis(audioSignal, fs);
    results(3).message = msg3;
    results(3).confidence = conf3;
    results(3).method = 'Frequency-Specific Analysis';
    
    % Method 4: Statistical phase analysis
    [msg4, conf4] = statistical_phase_analysis(phaseData);
    results(4).message = msg4;
    results(4).confidence = conf4;
    results(4).method = 'Statistical Phase Analysis';
end

function [message, confidence] = analyze_phase_differences_method(phaseData)
    % Analyze phase differences for hidden patterns
    
    message = '';
    confidence = 0;
    
    phaseDiffs = diff(phaseData, 1, 2);
    
    % Look for systematic phase shifts
    systematicShifts = abs(phaseDiffs) > pi/4;
    
    if sum(systematicShifts(:)) > 100 % Significant number of shifts
        % Extract binary pattern
        binaryPattern = phaseDiffs(systematicShifts) > 0;
        
        if length(binaryPattern) >= 8
            message = decode_phase_bits(binaryPattern);
            confidence = min(100 * sum(systematicShifts(:)) / numel(phaseDiffs), 95);
        end
    end
end

function [message, confidence] = frequency_phase_analysis(audioSignal, fs)
    % Frequency-specific phase analysis
    
    message = '';
    confidence = 0;
    
    % Focus on specific frequency bands where phase coding is often applied
    freqBands = [1000 2000; 2000 4000; 4000 8000]; % Hz
    
    for band = 1:size(freqBands, 1)
        bandSignal = filter_frequency_band(audioSignal, fs, freqBands(band, :));
        
        if length(bandSignal) > 1024
            phaseData = extract_phase_information(bandSignal, 512);
            [msg, conf] = detect_phase_coding(phaseData, 512);
            
            if conf > confidence
                message = msg;
                confidence = conf;
            end
        end
    end
end

function [message, confidence] = statistical_phase_analysis(phaseData)
    % Statistical analysis of phase patterns
    
    message = '';
    confidence = 0;
    
    % Check for non-uniform phase distribution
    phaseHistogram = histogram(phaseData(:), 36, 'BinLimits', [-pi pi]);
    binCounts = phaseHistogram.Values;
    
    expectedUniform = numel(phaseData) / 36;
    chiSquareStat = sum((binCounts - expectedUniform).^2 / expectedUniform);
    
    % Significant deviation from uniform distribution
    if chiSquareStat > 50
        confidence = min(100 * chiSquareStat / 100, 90);
        
        % Try to extract message from anomalous bins
        anomalousBins = find(abs(binCounts - expectedUniform) > 2*sqrt(expectedUniform));
        
        if length(anomalousBins) >= 8
            binaryPattern = binCounts(anomalousBins) > expectedUniform;
            message = decode_phase_bits(binaryPattern);
        end
    end
end

function filteredSignal = filter_frequency_band(signal, fs, freqRange)
    % Filter signal to specific frequency band
    
    [b, a] = butter(4, freqRange/(fs/2), 'bandpass');
    filteredSignal = filtfilt(b, a, signal);
end

%% Visualization Functions
function phase_spectrogram(audioSignal, frameLength, fs)
    % Create phase spectrogram
    
    [S, F, T] = spectrogram(audioSignal, frameLength, frameLength/2, frameLength, fs);
    phaseData = angle(S);
    
    imagesc(T, F, phaseData);
    axis xy;
    colorbar;
    colormap hsv;
end

function plot_phase_distribution(phaseData)
    % Plot phase distribution
    
    plot(phaseData(:), 'b.', 'MarkerSize', 1);
    xlim([-pi pi]);
    ylim([-pi pi]);
    grid on;
end

function plot_phase_differences(phaseData)
    % Plot phase differences between frames
    
    phaseDiffs = diff(phaseData, 1, 2);
    plot(mean(abs(phaseDiffs), 1));
    grid on;
end

function detect_phase_anomalies_plot(phaseData)
    % Detect and plot phase anomalies
    
    phaseDiffs = diff(phaseData, 1, 2);
    anomalyScores = mean(abs(phaseDiffs), 1);
    
    plot(anomalyScores);
    grid on;
    hold on;
    plot([1 length(anomalyScores)], [mean(anomalyScores) mean(anomalyScores)], 'r--');
    legend('Anomaly Score', 'Mean');
end

function analyze_phase_continuity(phaseData)
    % Analyze phase continuity
    
    phaseDiffs = diff(phaseData, 1, 2);
    continuityScores = 1 ./ (1 + mean(abs(phaseDiffs), 1));
    
    plot(continuityScores);
    grid on;
end

function analyze_frequency_domain(audioSignal, fs)
    % Frequency domain analysis
    
    fftResult = fft(audioSignal);
    freqAxis = (0:length(fftResult)-1) * fs / length(fftResult);
    
    plot(freqAxis(1:length(fftResult)/2), abs(fftResult(1:length(fftResult)/2)));
    grid on;
    xlim([0 fs/2]);
end

function simulate_phase_coding()
    % Simulate phase coding pattern
    
    % Generate example phase pattern with hidden data
    frameLength = 1024;
    phasePattern = linspace(-pi, pi, frameLength/2);
    
    % Add phase coding signature
    middleStart = frameLength/4;
    middleEnd = 3*frameLength/4;
    
    % Simulate binary data in phase
    binaryData = [1 0 1 1 0 0 1 0]; % Example
    phaseShifts = (binaryData - 0.5) * pi; % Convert to phase shifts
    
    for i = 1:length(binaryData)
        idx = middleStart + i - 1;
        if idx <= middleEnd
            phasePattern(idx) = phasePattern(idx) + phaseShifts(i);
        end
    end
    
    plot(phasePattern);
    grid on;
end

function phase_statistical_analysis(phaseData)
    % Statistical analysis of phase data
    
    phaseMean = mean(phaseData(:));
    phaseStd = std(phaseData(:));
    phaseSkewness = skewness(phaseData(:));
    phaseKurtosis = kurtosis(phaseData(:));
    
    stats = [phaseMean, phaseStd, phaseSkewness, phaseKurtosis];
    labels = {'Mean', 'Std', 'Skewness', 'Kurtosis'};
    
    bar(stats);
    set(gca, 'XTickLabel', labels);
    grid on;
end

function time_frequency_phase_analysis(audioSignal, fs)
    % Time-frequency phase analysis
    
    [S, F, T] = spectrogram(audioSignal, 512, 256, 512, fs);
    phaseData = angle(S);
    
    % Plot phase variance over time
    phaseVariance = var(phaseData, 0, 1);
    plot(T, phaseVariance);
    grid on;
end

function plot_detection_summary(results)
    % Plot detection summary
    
    confidences = [results.confidence];
    methods = {results.method};
    
    bar(confidences);
    set(gca, 'XTickLabel', methods, 'XTickLabelRotation', 45);
    ylabel('Confidence (%)');
    grid on;
end

function test_phase_coding()
    % Test phase coding with known message
    
    fprintf('Testing phase coding detection...\n');
    
    % Generate test signal
    fs = 44100;
    duration = 2;
    t = 0:1/fs:duration-1/fs;
    testSignal = 0.5 * sin(2*pi*440*t) + 0.3 * sin(2*pi*880*t);
    
    % Hide message using phase coding
    secretMessage = 'TEST';
    stegoSignal = phase_enc_simulation(testSignal, secretMessage);
    
    % Try to detect
    phaseData = extract_phase_information(stegoSignal, 1024);
    [detectedMessage, confidence, ~] = detect_phase_coding(phaseData, 1024);
    
    fprintf('Original message: "%s"\n', secretMessage);
    fprintf('Detected message: "%s"\n', detectedMessage);
    fprintf('Detection confidence: %.1f%%\n', confidence);
    
    if strcmp(detectedMessage, secretMessage)
        fprintf('✓ Phase coding detection working correctly!\n');
    else
        fprintf('⚠ Phase coding detection needs refinement.\n');
    end
end

function stegoSignal = phase_enc_simulation(signal, text)
    % Simulate phase encoding (simplified version)
    
    % This is a simplified simulation for demonstration
    % In practice, you'd use the full phase encoding algorithm
    
    stegoSignal = signal; % Placeholder - full implementation would be complex
    
    % Add small phase perturbations to simulate hidden data
    phasePerturbation = 0.01 * sin(2*pi*1000*(1:length(signal))/44100);
    stegoSignal = stegoSignal + phasePerturbation;
end

%% Note on Phase Coding Steganography:
% Phase coding is a more advanced steganography technique than LSB.
% It hides data in the phase information of the audio signal's Fourier transform.
%
% Advantages over LSB:
% - More robust to signal processing
% - Less perceptible to human hearing
% - Higher capacity in some cases
%
% Detection challenges:
% - Phase information is less intuitive to analyze
% - Requires sophisticated statistical methods
% - Natural audio already has complex phase patterns
%
% This script implements multiple detection approaches:
% 1. Phase difference analysis
% 2. Statistical phase distribution analysis
% 3. Frequency-specific phase analysis
% 4. Phase continuity analysis
%
% For production use, consider additional techniques like:
% - Machine learning-based phase pattern recognition
% - Advanced statistical hypothesis testing
% - Multi-resolution phase analysis
