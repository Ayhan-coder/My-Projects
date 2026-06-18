%% Method 7: Real-Time HPSS Source Separation
% Based on Real-Time-HPSS approach by Sevagh
% Uses sliding window STFT with median filtering for real-time separation

clear; clc; close all;

%% Load and Run Separation
mixFile = 'cafe_sample.wav';
if ~isfile(mixFile)
    error('Input file %s not found.', mixFile);
end

[mixedAudio, fs] = audioread(mixFile);
if size(mixedAudio, 2) > 1, mixedAudio = mean(mixedAudio, 2); end

fprintf('Running Real-Time HPSS on %s...\n', mixFile);
[music, speech] = realtime_hpss_separation(mixedAudio, fs);

%% Save Results
audiowrite('cafe_sample_realtime_hpss_music.wav', music, fs);
audiowrite('cafe_sample_realtime_hpss_speech.wav', speech, fs);
fprintf('Saved separated files (realtime_hpss_music and realtime_hpss_speech).\n');

%% Visualization
figure('Position', [100, 100, 1000, 600]);
subplot(3,1,1);
spectrogram(mixedAudio, hann(2048), 1024, 2048, fs, 'yaxis');
title('Original mixture'); ylim([0 8]); colormap hot;

subplot(3,1,2);
spectrogram(music, hann(2048), 1024, 2048, fs, 'yaxis');
title('Real-Time HPSS Music'); ylim([0 8]); colormap hot;

subplot(3,1,3);
spectrogram(speech, hann(2048), 1024, 2048, fs, 'yaxis');
title('Real-Time HPSS Speech'); ylim([0 8]); colormap hot;

saveas(gcf, 'realtime_hpss_separation_results.png');
fprintf('Saved visualization to realtime_hpss_separation_results.png\n');

%% Real-Time HPSS Separation Functions
function [music, speech] = realtime_hpss_separation(mixedAudio, fs)
    
    % Real-Time HPSS parameters (based on Sevagh's implementation)
    nfft = 2048;
    nwin = 1024;
    hop = 512;
    beta = 2; % Separation factor (Driedger et al. 2014)
    
    % Window function
    win = sqrt(hann(nwin, "periodic"));
    
    % Median filter parameters
    lHarm = 0.2/((nfft - hop)/fs);  % 200ms in samples (time domain)
    lPerc = 500/(fs/nfft);          % 500Hz in samples (frequency domain)
    
    % Preallocate sliding STFT buffer
    stftBuffer = zeros(nfft, ceil(lHarm/2));
    
    % Ring buffers for input and output
    xBuffer = zeros(nwin, 1);
    hBuffer = zeros(nwin, 1);
    pBuffer = zeros(nwin, 1);
    
    % Output buffers
    musicOutput = zeros(length(mixedAudio), 1);
    speechOutput = zeros(length(mixedAudio), 1);
    
    % Process audio in chunks (simulating real-time processing)
    totalSamples = length(mixedAudio);
    processedSamples = 0;
    
    fprintf('Processing audio with real-time HPSS...\n');
    
    while processedSamples + hop <= totalSamples
        % Get next hop of samples
        if processedSamples + hop <= totalSamples
            nextHop = mixedAudio(processedSamples + 1 : processedSamples + hop);
        else
            % Handle final chunk (pad with zeros if needed)
            remaining = totalSamples - processedSamples;
            nextHop = [mixedAudio(processedSamples + 1 : end); zeros(hop - remaining, 1)];
        end
        
        % Update input buffer (ring buffer style)
        xBuffer = [xBuffer(hop + 1 : end); nextHop];
        
        % Compute FFT of current frame
        frameWindowed = xBuffer .* win;
        X = fft(frameWindowed, nfft);
        Xhalf = X(1 : nfft/2);
        
        % Update STFT buffer (sliding window)
        stftBuffer = stftBuffer(:, 2 : end);
        stftBuffer(:, end + 1) = X;
        
        % Apply median filters to magnitude spectrogram
        Smag = abs(stftBuffer(1 : nfft/2, :));
        H = movmedian(Smag, lHarm, 2);  % Time domain median filter
        P = movmedian(Smag, lPerc, 1);  % Frequency domain median filter
        
        % Create binary masks with separation factor
        Mh = (H ./ (P + eps)) > beta;
        Mp = (P ./ (H + eps)) >= beta;
        
        % Apply masks to current frame
        Hmasked = Mh(:, end) .* Xhalf;
        Pmasked = Mp(:, end) .* Xhalf;
        
        % Reconstruct full spectrum
        Hfull = [Hmasked; flipud(conj(Hmasked))];
        Pfull = [Pmasked; flipud(conj(Pmasked))];
        
        % Inverse FFT
        hFrame = real(ifft(Hfull, nfft));
        pFrame = real(ifft(Pfull, nfft));
        
        % Weighted overlap-add
        weightFactor = nfft / sum(win.^2);
        hBuffer = hBuffer + hFrame(1 : nfft/2) .* weightFactor;
        pBuffer = pBuffer + pFrame(1 : nfft/2) .* weightFactor;
        
        % Output first hop samples (they're now finalized)
        outputStart = processedSamples + 1;
        outputEnd = min(processedSamples + hop, totalSamples);
        
        if outputEnd >= outputStart
            musicOutput(outputStart : outputEnd) = hBuffer(1 : outputEnd - outputStart + 1);
            speechOutput(outputStart : outputEnd) = pBuffer(1 : outputEnd - outputStart + 1);
        end
        
        % Shift buffers for next iteration
        hBuffer = [hBuffer(hop + 1 : end); zeros(hop, 1)];
        pBuffer = [pBuffer(hop + 1 : end); zeros(hop, 1)];
        
        processedSamples = processedSamples + hop;
        
        % Progress indicator
        if mod(processedSamples, fs*10) == 0 || processedSamples >= totalSamples - hop
            fprintf('Processed %d/%d samples (%.1f%%)\n', ...
                processedSamples, totalSamples, 100*processedSamples/totalSamples);
        end
    end
    
    % Trim output to original length
    musicOutput = musicOutput(1 : totalSamples);
    speechOutput = speechOutput(1 : totalSamples);
    
    % Classify harmonic and percussive as music and speech
    % Music is typically more harmonic, speech has more percussive elements
    music = musicOutput;
    speech = speechOutput;
    
    % Normalize outputs
    music = music / (max(abs(music)) + eps) * 0.9;
    speech = speech / (max(abs(speech)) + eps) * 0.9;
    
    fprintf('Real-time HPSS processing complete!\n');
end

%% Alternative Implementation: Batch Processing with Real-Time Algorithm
function [music, speech] = realtime_hpss_batch(mixedAudio, fs)
    % Alternative implementation that processes the entire signal at once
    % but uses the same algorithm as the real-time version
    
    % Parameters
    nfft = 2048;
    nwin = 1024;
    hop = 512;
    beta = 2;
    
    % Window function
    win = sqrt(hann(nwin, "periodic"));
    
    % Median filter parameters
    lHarm = 0.2/((nfft - hop)/fs);  % 200ms in samples
    lPerc = 500/(fs/nfft);          % 500Hz in samples
    
    % Compute full STFT
    [S, ~, ~] = spectrogram(mixedAudio, win, nwin - hop, nfft, fs);
    [nFreq, nFrames] = size(S);
    
    % Use magnitude for mask creation
    Smag = abs(S);
    
    % Apply median filters
    H = movmedian(Smag, lHarm, 2);
    P = movmedian(Smag, lPerc, 1);
    
    % Create binary masks
    Mh = (H ./ (P + eps)) > beta;
    Mp = (P ./ (H + eps)) >= beta;
    
    % Apply masks
    Hmasked = Mh .* S;
    Pmasked = Mp .* S;
    
    % Inverse STFT
    music = istft_custom_realtime(Hmasked, win, hop, nfft, length(mixedAudio));
    speech = istft_custom_realtime(Pmasked, win, hop, nfft, length(mixedAudio));
    
    % Normalize
    music = music / (max(abs(music)) + eps) * 0.9;
    speech = speech / (max(abs(speech)) + eps) * 0.9;
end

function x = istft_custom_realtime(S, window, hopSize, nfft, targetLength)
    % Custom inverse STFT function optimized for real-time HPSS
    
    [numBins, numFrames] = size(S);
    frameLength = length(window);
    
    % Output length
    outputLength = (numFrames - 1) * hopSize + frameLength;
    x = zeros(outputLength, 1);
    windowSum = zeros(outputLength, 1);
    
    for i = 1:numFrames
        % Inverse FFT
        frame = real(ifft(S(:, i), nfft));
        frame = frame(1:frameLength);
        
        % Apply window
        frame = frame .* window;
        
        % Overlap-add
        startIdx = (i - 1) * hopSize + 1;
        endIdx = startIdx + frameLength - 1;
        
        if endIdx <= outputLength
            x(startIdx:endIdx) = x(startIdx:endIdx) + frame;
            windowSum(startIdx:endIdx) = windowSum(startIdx:endIdx) + window.^2;
        end
    end
    
    % Normalize by window sum
    x = x ./ (windowSum + eps);
    
    % Trim to target length
    x = x(1:min(length(x), targetLength));
end

%% Performance Comparison Function
function compare_hpss_methods(mixedAudio, fs)
    % Compare original HPSS vs real-time HPSS
    
    fprintf('=== HPSS Methods Comparison ===\n');
    
    % Original HPSS
    tic;
    [music_orig, speech_orig] = hpss_separation(mixedAudio, fs);
    time_orig = toc;
    fprintf('Original HPSS: %.3f seconds\n', time_orig);
    
    % Real-time HPSS (batch version)
    tic;
    [music_rt, speech_rt] = realtime_hpss_batch(mixedAudio, fs);
    time_rt = toc;
    fprintf('Real-time HPSS: %.3f seconds\n', time_rt);
    
    % Real-time HPSS (chunked version)
    tic;
    [music_chunk, speech_chunk] = realtime_hpss_separation(mixedAudio, fs);
    time_chunk = toc;
    fprintf('Real-time HPSS (chunked): %.3f seconds\n', time_chunk);
    
    % Quality assessment
    quality_orig = assess_separation_quality(music_orig, speech_orig, mixedAudio);
    quality_rt = assess_separation_quality(music_rt, speech_rt, mixedAudio);
    quality_chunk = assess_separation_quality(music_chunk, speech_chunk, mixedAudio);
    
    fprintf('\nQuality Scores:\n');
    fprintf('Original HPSS: %.3f\n', quality_orig);
    fprintf('Real-time HPSS: %.3f\n', quality_rt);
    fprintf('Real-time HPSS (chunked): %.3f\n', quality_chunk);
    
    % Visualization
    figure('Position', [100, 100, 1200, 800]);
    
    subplot(3, 3, 1);
    spectrogram(mixedAudio, hann(2048), 1024, 2048, fs, 'yaxis');
    title('Original Mixture'); ylim([0 8]); colormap hot;
    
    subplot(3, 3, 2);
    spectrogram(music_orig, hann(2048), 1024, 2048, fs, 'yaxis');
    title('Original HPSS Music'); ylim([0 8]); colormap hot;
    
    subplot(3, 3, 3);
    spectrogram(music_rt, hann(2048), 1024, 2048, fs, 'yaxis');
    title('Real-time HPSS Music'); ylim([0 8]); colormap hot;
    
    subplot(3, 3, 4);
    spectrogram(mixedAudio, hann(2048), 1024, 2048, fs, 'yaxis');
    title('Original Mixture'); ylim([0 8]); colormap hot;
    
    subplot(3, 3, 5);
    spectrogram(speech_orig, hann(2048), 1024, 2048, fs, 'yaxis');
    title('Original HPSS Speech'); ylim([0 8]); colormap hot;
    
    subplot(3, 3, 6);
    spectrogram(speech_rt, hann(2048), 1024, 2048, fs, 'yaxis');
    title('Real-time HPSS Speech'); ylim([0 8]); colormap hot;
    
    % Waveforms comparison
    subplot(3, 3, 7);
    t = (0:length(mixedAudio)-1) / fs;
    plot(t, mixedAudio);
    title('Original Mixture'); xlabel('Time (s)');
    
    subplot(3, 3, 8);
    plot(t(1:length(music_orig)), music_orig, 'b', 'DisplayName', 'Original');
    hold on;
    plot(t(1:length(music_rt)), music_rt, 'r--', 'DisplayName', 'Real-time');
    title('Music Comparison'); xlabel('Time (s)'); legend;
    
    subplot(3, 3, 9);
    plot(t(1:length(speech_orig)), speech_orig, 'b', 'DisplayName', 'Original');
    hold on;
    plot(t(1:length(speech_rt)), speech_rt, 'r--', 'DisplayName', 'Real-time');
    title('Speech Comparison'); xlabel('Time (s)'); legend;
    
    sgtitle('HPSS Methods Comparison');
    saveas(gcf, 'hpss_methods_comparison.png');
    fprintf('Saved comparison to hpss_methods_comparison.png\n');
end

function quality = assess_separation_quality(music, speech, mixed)
    % Simple quality assessment metric
    reconstructed = music + speech;
    reconstructed = reconstructed(1:length(mixed));
    
    % Reconstruction error
    reconstruction_error = mean((mixed - reconstructed).^2);
    
    % Cross-correlation (lower is better for separation)
    correlation = abs(correlation(music, speech));
    
    % Energy balance
    music_energy = sum(music.^2);
    speech_energy = sum(speech.^2);
    energy_balance = abs(music_energy - speech_energy) / (music_energy + speech_energy + eps);
    
    % Combined quality score (higher is better)
    quality = 1 / (1 + reconstruction_error + correlation + energy_balance);
end

function [music, speech] = hpss_separation(mixedAudio, fs)
    % Original HPSS implementation for comparison
    
    % Parameters 
    frameLength = round(0.046 * fs);  
    hopLength = round(frameLength / 4); 
    nfft = 2^nextpow2(frameLength); 
    
    % Compute STFT 
    window = hann(frameLength); 
    [S, ~, ~] = spectrogram(mixedAudio, window, frameLength - hopLength, nfft, fs); 
    magnitude = abs(S); 
    phase = angle(S); 
    
    % Median filtering for HPSS 
    harmonicKernelSize = 17;  
    percussiveKernelSize = 17;  
    
    % Apply median filters 
    harmonicMag = medfilt2(magnitude, [1, harmonicKernelSize]); 
    percussiveMag = medfilt2(magnitude, [percussiveKernelSize, 1]); 
    
    % Create soft masks using Wiener-like filtering 
    epsilon = 1e-10; 
    harmonicMask = (harmonicMag.^2) ./ (harmonicMag.^2 + percussiveMag.^2 + epsilon); 
    percussiveMask = (percussiveMag.^2) ./ (harmonicMag.^2 + percussiveMag.^2 + epsilon); 
    
    % For music/speech: Music is more harmonic, Speech has percussive elements 
    musicMag = magnitude .* harmonicMask; 
    speechMag = magnitude .* percussiveMask; 
    
    % Reconstruct 
    musicSTFT = musicMag .* exp(1j * phase); 
    speechSTFT = speechMag .* exp(1j * phase); 
    
    % Inverse STFT 
    music = istft_overlap_add(musicSTFT, window, hopLength, nfft, length(mixedAudio)); 
    speech = istft_overlap_add(speechSTFT, window, hopLength, nfft, length(mixedAudio)); 
    
    % Normalize 
    music = music / (max(abs(music)) + eps) * 0.9; 
    speech = speech / (max(abs(speech)) + eps) * 0.9; 
end

function x = istft_overlap_add(S, window, hopLength, nfft, targetLength) 
    [~, numFrames] = size(S); 
    frameLength = length(window); 
    
    outputLength = (numFrames - 1) * hopLength + frameLength; 
    x = zeros(outputLength, 1); 
    windowSum = zeros(outputLength, 1); 
    
    for i = 1:numFrames 
        frame = real(ifft(S(:, i), nfft)); 
        frame = frame(1:frameLength) .* window; 
        
        startIdx = (i - 1) * hopLength + 1; 
        endIdx = startIdx + frameLength - 1; 
        
        x(startIdx:endIdx) = x(startIdx:endIdx) + frame; 
        windowSum(startIdx:endIdx) = windowSum(startIdx:endIdx) + window.^2; 
    end 
    
    x = x ./ (windowSum + eps); 
    x = x(1:min(length(x), targetLength)); 
end

%% Note on Real-Time HPSS Approach:
% This implementation is based on the Real-Time-HPSS framework by Sevagh,
% which modifies the traditional HPSS algorithm for real-time processing.
%
% Key innovations:
% 1. Sliding window STFT buffer for continuous processing
% 2. Ring buffers for efficient memory management
% 3. Weighted overlap-add for seamless reconstruction
% 4. Binary masks with separation factor (Driedger et al. 2014)
% 5. Chunk-based processing simulating real-time constraints
%
% The algorithm can process audio hop-by-hop, making it suitable for
% real-time applications while maintaining separation quality comparable
% to batch processing methods.
