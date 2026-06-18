%% Audio Steganography Detection and Hidden Message Extraction
% Based on LSB (Least Significant Bit) steganography approach
% Can detect and extract hidden messages from audio files

clear; clc; close all;

%% Input Audio File
audioFile = 'cafe_sample.wav'; % Change this to test different files
if ~isfile(audioFile)
    error('Input file %s not found.', audioFile);
end

fprintf('Analyzing audio file for hidden messages: %s\n', audioFile);

%% Load Audio Signal
[audioSignal, fs] = audioread(audioFile);
if size(audioSignal, 2) > 1
    audioSignal = mean(audioSignal, 2); % Convert to mono if stereo
end

signalLength = length(audioSignal);
fprintf('Audio loaded: %d samples, %.2f seconds, %d Hz\n', ...
    signalLength, signalLength/fs, fs);

%% LSB Analysis and Hidden Message Detection
fprintf('\n=== LSB Steganography Analysis ===\n');

% Convert to 16-bit integer format for LSB extraction
audioInt16 = int16(audioSignal * (2^15 - 1));

% Extract LSB from all samples
lsbPattern = bitget(audioInt16, 1);

% Analyze LSB pattern for hidden messages
[hiddenMessage, confidence, messageLength] = extract_hidden_message(lsbPattern);

if ~isempty(hiddenMessage)
    fprintf('*** HIDDEN MESSAGE DETECTED ***\n');
    fprintf('Message: "%s"\n', hiddenMessage);
    fprintf('Confidence: %.2f%%\n', confidence);
    fprintf('Estimated message length: %d characters\n', messageLength);
else
    fprintf('No hidden message detected using LSB steganography.\n');
    fprintf('LSB pattern appears to be random noise.\n');
end

%% Advanced LSB Analysis
fprintf('\n=== Advanced LSB Analysis ===\n');

% Check for different bit depths and encoding schemes
results = comprehensive_lsb_analysis(audioInt16, fs);

% Display results
fprintf('Analysis Results:\n');
for i = 1:length(results)
    fprintf('Method %d: "%s" (Confidence: %.1f%%)\n', ...
        i, results(i).message, results(i).confidence);
end

%% Visual Analysis
figure('Position', [100, 100, 1200, 800]);

% Audio signal
subplot(4, 2, 1);
t = (0:signalLength-1) / fs;
plot(t, audioSignal);
title('Original Audio Signal');
xlabel('Time (s)');
ylabel('Amplitude');
grid on;

% LSB pattern
subplot(4, 2, 2);
plot(t, lsbPattern);
title('LSB Pattern');
xlabel('Time (s)');
ylabel('LSB Value');
ylim([0 1]);
grid on;

% LSB histogram
subplot(4, 2, 3);
histogram(lsbPattern, 2);
title('LSB Distribution');
xlabel('LSB Value');
ylabel('Count');
grid on;

% LSB autocorrelation (to detect patterns)
subplot(4, 2, 4);
[maxLag, autocorr] = compute_lsb_autocorrelation(lsbPattern);
plot(0:maxLag, autocorr);
title('LSB Autocorrelation');
xlabel('Lag');
ylabel('Correlation');
grid on;

% Spectrogram of original signal
subplot(4, 2, 5);
spectrogram(audioSignal, 1024, 512, 1024, fs, 'yaxis');
title('Spectrogram - Original Signal');
ylim([0 8]);

% Spectrogram with LSB emphasis
subplot(4, 2, 6);
lsbAudio = double(lsbPattern - 0.5) * 0.1; % Convert LSB to audio
spectrogram(lsbAudio, 256, 128, 256, fs, 'yaxis');
title('Spectrogram - LSB Emphasis');
ylim([0 8]);

% Binary pattern visualization
subplot(4, 2, 7);
visualize_binary_pattern(lsbPattern(1:min(1000, length(lsbPattern))));
title('LSB Binary Pattern (First 1000 samples)');
xlabel('Sample Index');
ylabel('Binary Value');

% Statistical analysis
subplot(4, 2, 8);
analyze_lsb_statistics(lsbPattern);
title('LSB Statistical Analysis');

sgtitle('Audio Steganography Detection Analysis');
saveas(gcf, 'steganography_analysis.png');
fprintf('Saved analysis plot to steganography_analysis.png\n');

%% Test with Different Audio Files
fprintf('\n=== Testing Multiple Audio Files ===\n');

testFiles = {'cafe_sample.wav'}; % Add more files to test
for i = 1:length(testFiles)
    if isfile(testFiles{i})
        fprintf('\nTesting file: %s\n', testFiles{i});
        test_file_for_steganography(testFiles{i});
    end
end

fprintf('\n=== Analysis Complete ===\n');

%% Hidden Message Extraction Functions
function [message, confidence, estimatedLength] = extract_hidden_message(lsbPattern)
    % Extract hidden message from LSB pattern
    
    message = '';
    confidence = 0;
    estimatedLength = 0;
    
    % Method 1: Direct binary to ASCII conversion
    binaryMessage = num2str(lsbPattern');
    binaryMessage = binaryMessage(~isspace(binaryMessage));
    
    % Try different message lengths
    maxLength = min(length(lsbPattern) / 8, 500); % Max 500 characters
    bestMessage = '';
    bestScore = 0;
    
    for msgLen = 1:maxLength
        if msgLen * 8 <= length(lsbPattern)
            % Extract binary for this length
            msgBinary = lsbPattern(1:msgLen*8);
            
            % Convert to characters
            try
                binaryStr = num2str(msgBinary');
                binaryStr = binaryStr(~isspace(binaryStr));
                
                % Reshape to 8-bit groups
                if length(binaryStr) == msgLen * 8
                    binaryMatrix = reshape(binaryStr, 8, msgLen)';
                    decodedChars = char(bin2dec(binaryMatrix));
                    
                    % Check if result looks like readable text
                    score = evaluate_text_quality(decodedChars);
                    
                    if score > bestScore && score > 0.3
                        bestScore = score;
                        bestMessage = decodedChars;
                    end
                end
            catch
                % Skip invalid conversions
                continue;
            end
        end
    end
    
    if bestScore > 0.5
        message = bestMessage;
        confidence = bestScore * 100;
        estimatedLength = length(message);
    end
end

function score = evaluate_text_quality(text)
    % Evaluate if text looks like a readable message
    
    if isempty(text)
        score = 0;
        return;
    end
    
    % Check for printable ASCII characters
    printableChars = text >= 32 & text <= 126;
    printableRatio = sum(printableChars) / length(text);
    
    % Check for common English letters
    letters = isstrprop(text, 'alpha');
    letterRatio = sum(letters) / length(text);
    
    % Check for common words
    commonWords = {'the', 'and', 'is', 'this', 'that', 'for', 'are', 'with'};
    wordCount = 0;
    for i = 1:length(commonWords)
        if contains(lower(text), commonWords{i})
            wordCount = wordCount + 1;
        end
    end
    
    % Check for reasonable character distribution
    charFreq = histcounts(double(text), 32:127);
    entropy = -sum((charFreq/sum(charFreq)) .* log2(charFreq/sum(charFreq) + eps));
    entropyScore = min(entropy / 4, 1); % Normalize to 0-1
    
    % Combined score
    score = 0.4 * printableRatio + 0.3 * letterRatio + ...
            0.2 * (wordCount / length(commonWords)) + 0.1 * entropyScore;
end

function [maxLag, autocorr] = compute_lsb_autocorrelation(lsbPattern)
    % Compute autocorrelation of LSB pattern to detect hidden structures
    
    maxLag = min(100, length(lsbPattern) - 1);
    autocorr = zeros(1, maxLag + 1);
    
    for lag = 0:maxLag
        if lag == 0
            autocorr(lag + 1) = 1;
        else
            original = lsbPattern(1:end-lag);
            shifted = lsbPattern(1+lag:end);
            autocorr(lag + 1) = corr(original, shifted);
        end
    end
end

function visualize_binary_pattern(lsbPattern)
    % Visualize LSB pattern as binary image
    
    % Reshape for visualization
    samples = length(lsbPattern);
    cols = min(100, samples);
    rows = ceil(samples / cols);
    
    % Pad if necessary
    if samples < rows * cols
        lsbPattern = [lsbPattern; zeros(rows * cols - samples, 1)];
    end
    
    % Create binary image
    binaryImage = reshape(lsbPattern, cols, rows)';
    
    % Display as image
    imagesc(binaryImage);
    colormap([0 0 0; 1 1 1]); % Black and white
    axis equal tight;
end

function analyze_lsb_statistics(lsbPattern)
    % Analyze statistical properties of LSB pattern
    
    % Basic statistics
    zerosCount = sum(lsbPattern == 0);
    onesCount = sum(lsbPattern == 1);
    total = length(lsbPattern);
    
    % Create bar chart
    categories = {'Zeros', 'Ones'};
    counts = [zerosCount, onesCount];
    
    bar(counts);
    set(gca, 'XTickLabel', categories);
    ylabel('Count');
    
    % Add text annotations
    text(1, zerosCount + total*0.01, sprintf('%.1f%%', 100*zerosCount/total), ...
        'HorizontalAlignment', 'center');
    text(2, onesCount + total*0.01, sprintf('%.1f%%', 100*onesCount/total), ...
        'HorizontalAlignment', 'center');
    
    % Test for randomness (runs test)
    runs = detect_runs(lsbPattern);
    expectedRuns = (2 * zerosCount * onesCount) / total + 1;
    
    % Add title with randomness test
    title(sprintf('LSB Stats (Runs: %d, Expected: %.1f)', runs, expectedRuns));
end

function runs = detect_runs(sequence)
    % Count runs (consecutive same values) in binary sequence
    
    runs = 1;
    for i = 2:length(sequence)
        if sequence(i) ~= sequence(i-1)
            runs = runs + 1;
        end
    end
end

function results = comprehensive_lsb_analysis(audioInt16, fs)
    % Comprehensive analysis using different LSB extraction methods
    
    results = struct();
    
    % Method 1: Standard LSB (bit 1)
    lsb1 = bitget(audioInt16, 1);
    [msg1, conf1, len1] = extract_hidden_message(lsb1);
    results(1).message = msg1;
    results(1).confidence = conf1;
    results(1).method = 'LSB Bit 1';
    
    % Method 2: Multiple bits (bits 1-2)
    if length(audioInt16) >= 16
        lsb2 = bitget(audioInt16, 2);
        combined1_2 = lsb1 + 2 * lsb2;
        [msg2, conf2, len2] = extract_hidden_message(combined1_2);
        results(2).message = msg2;
        results(2).confidence = conf2;
        results(2).method = 'LSB Bits 1-2';
    else
        results(2).message = '';
        results(2).confidence = 0;
        results(2).method = 'LSB Bits 1-2';
    end
    
    % Method 3: Every Nth sample (skip encoding)
    skipFactor = 2;
    lsbSkip = lsb1(1:skipFactor:end);
    [msg3, conf3, len3] = extract_hidden_message(lsbSkip);
    results(3).message = msg3;
    results(3).confidence = conf3;
    results(3).method = sprintf('LSB Skip Factor %d', skipFactor);
    
    % Method 4: Reverse order
    lsbReverse = flip(lsb1);
    [msg4, conf4, len4] = extract_hidden_message(lsbReverse);
    results(4).message = msg4;
    results(4).confidence = conf4;
    results(4).method = 'LSB Reverse Order';
end

function test_file_for_steganography(filename)
    % Test a specific audio file for hidden messages
    
    try
        [audioSignal, fs] = audioread(filename);
        if size(audioSignal, 2) > 1
            audioSignal = mean(audioSignal, 2);
        end
        
        audioInt16 = int16(audioSignal * (2^15 - 1));
        lsbPattern = bitget(audioInt16, 1);
        
        [message, confidence, ~] = extract_hidden_message(lsbPattern);
        
        if ~isempty(message)
            fprintf('  HIDDEN MESSAGE FOUND: "%s" (%.1f%% confidence)\n', ...
                message, confidence);
        else
            fprintf('  No hidden message detected\n');
        end
        
        % Statistical analysis
        zerosRatio = sum(lsbPattern == 0) / length(lsbPattern);
        fprintf('  LSB distribution: %.1f%% zeros, %.1f%% ones\n', ...
            100*zerosRatio, 100*(1-zerosRatio));
        
    catch ME
        fprintf('  Error analyzing file: %s\n', ME.message);
    end
end

%% Create Test Audio with Hidden Message (for demonstration)
function create_test_steganography()
    % Create a test audio file with hidden message
    
    fprintf('\n=== Creating Test Audio with Hidden Message ===\n');
    
    % Generate test audio
    fs = 44100;
    duration = 5;
    t = 0:1/fs:duration-1/fs;
    
    % Create a more interesting test signal
    freq1 = 440; % A4
    freq2 = 880; % A5
    signal = 0.5 * sin(2*pi*freq1*t) + 0.3 * sin(2*pi*freq2*t) + ...
             0.1 * randn(size(t));
    
    % Normalize
    signal = signal / max(abs(signal));
    
    % Hidden message
    secretMessage = 'This is a secret hidden message in audio';
    secretMessageBinary = dec2bin(secretMessage, 8);
    secretMessageBinary = secretMessageBinary(:)';
    
    % Convert to 16-bit
    audioInt16 = int16(signal * (2^15 - 1));
    
    % Hide message in LSB
    numBits = min(length(secretMessageBinary), length(audioInt16));
    for i = 1:numBits
        audioInt16(i) = bitset(audioInt16(i), 1, secretMessageBinary(i));
    end
    
    % Save test file
    testFile = 'test_hidden_message.wav';
    audiowrite(testFile, double(audioInt16) / (2^15 - 1), fs, 'BitsPerSample', 16);
    
    fprintf('Created test file: %s\n', testFile);
    fprintf('Hidden message: "%s"\n', secretMessage);
    fprintf('Run this script again to detect the hidden message!\n');
end

%% Main execution options
% Uncomment to create a test file with hidden message
% create_test_steganography();

%% Note on Audio Steganography Detection:
% This script implements LSB (Least Significant Bit) steganography detection,
% which is one of the most common methods for hiding messages in audio.
%
% Detection techniques used:
% 1. Direct LSB extraction and binary-to-ASCII conversion
% 2. Statistical analysis of LSB patterns
% 3. Autocorrelation analysis to detect non-random patterns
% 4. Multiple extraction methods (different bit depths, skip patterns)
% 5. Text quality evaluation to distinguish real messages from noise
%
% Limitations:
% - Only detects LSB-based steganography
% - May miss messages encoded with more sophisticated methods
% - False positives possible for naturally patterned audio
%
% For production use, consider additional techniques like:
% - Wavelet domain analysis
% - Phase coding detection
% - Spread spectrum analysis
% - Machine learning-based detection
