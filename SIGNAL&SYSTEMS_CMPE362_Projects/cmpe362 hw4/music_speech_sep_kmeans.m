%% Audio Source Separation: Music vs Speech 
 % This script separates a mixed WAV file into music and speech components 
 
 clear; clc; close all; 
 
 %% Load the mixed audio file 
 % Check if we are in non-interactive mode (e.g., Trae agent environment)
 if exist('cafe_sample.wav', 'file')
     filename = 'cafe_sample.wav';
     pathname = pwd;
 else
     [filename, pathname] = uigetfile('*.wav', 'Select the mixed WAV file'); 
     if isequal(filename, 0) 
         disp('User cancelled file selection'); 
         return; 
     end 
 end
 
 [mixedAudio, fs] = audioread(fullfile(pathname, filename)); 
 
 % Convert to mono if stereo 
 if size(mixedAudio, 2) > 1 
     mixedAudio = mean(mixedAudio, 2); 
 end 
 
 fprintf('Loaded audio file: %s\n', filename); 
 fprintf('Sample rate: %d Hz\n', fs); 
 fprintf('Duration: %.2f seconds\n', length(mixedAudio)/fs); 
 
 %% Parameters 
 frameLength = round(0.03 * fs);    % 30ms frame 
 hopLength = round(0.01 * fs);      % 10ms hop 
 nfft = 2^nextpow2(frameLength); 
 numMelBands = 40; 

speech_lo_hz = 300;
speech_hi_hz = 3400;
 
 %% Compute STFT 
 window = hamming(frameLength); 
 [S, F, T] = spectrogram(mixedAudio, window, frameLength - hopLength, nfft, fs); 
 magnitude = abs(S); 
 phase = angle(S); 
 
 %% Extract Features for Classification 
 fprintf('Extracting features...\n'); 
 
 numFrames = size(magnitude, 2); 
 features = zeros(numFrames, 6); 
 
 for i = 1:numFrames 
     frame_mag = magnitude(:, i); 
     
     % Spectral Centroid 
     features(i, 1) = sum(F .* frame_mag) / (sum(frame_mag) + eps); 
     
     % Spectral Rolloff (85%) 
     cumSum = cumsum(frame_mag); 
     rolloffThresh = 0.85 * cumSum(end); 
     rolloffIdx = find(cumSum >= rolloffThresh, 1, 'first'); 
     features(i, 2) = F(min(rolloffIdx, length(F))); 
     
     % Spectral Flux 
     if i > 1 
         features(i, 3) = sum((frame_mag - magnitude(:, i-1)).^2); 
     else 
         features(i, 3) = 0; 
     end 
     
     % Zero Crossing Rate (approximate from spectral domain) 
     features(i, 4) = sum(abs(diff(sign(frame_mag)))) / (2 * length(frame_mag)); 
     
     % Spectral Flatness 
     geometricMean = exp(mean(log(frame_mag + eps))); 
     arithmeticMean = mean(frame_mag); 
     features(i, 5) = geometricMean / (arithmeticMean + eps); 
     
     % High Frequency Content 
     highFreqIdx = F > speech_hi_hz; 
     features(i, 6) = sum(frame_mag(highFreqIdx)) / (sum(frame_mag) + eps); 
 end 
 
 %% Normalize features 
 features = (features - mean(features)) ./ (std(features) + eps); 
 
 %% Classification using K-means (2 clusters: music and speech) 
 fprintf('Classifying frames...\n'); 
 
 % Use custom k-means clustering (to avoid toolbox dependency)
 [clusterIdx, ~] = kmeans_custom(features, 2); 
 
 % Determine which cluster is speech (typically higher spectral centroid variance) 
 cluster1_var = var(features(clusterIdx == 1, 1)); 
 cluster2_var = var(features(clusterIdx == 2, 1)); 
 
 if cluster1_var > cluster2_var 
     speechCluster = 1; 
 else 
     speechCluster = 2; 
 end 
 
 speechMask = (clusterIdx == speechCluster); 
 musicMask = ~speechMask; 
 
 %% Create Time-Frequency Masks 
 fprintf('Creating separation masks...\n'); 
 
 % Smooth masks temporally 
 smoothingWindow = 5; 
 speechMaskSmooth = movmean(double(speechMask), smoothingWindow); 
 musicMaskSmooth = movmean(double(musicMask), smoothingWindow); 
 
 % Expand masks to full spectrogram size 
 speechMaskFull = repmat(speechMaskSmooth', size(magnitude, 1), 1); 
 musicMaskFull = repmat(musicMaskSmooth', size(magnitude, 1), 1); 
 
 %% Apply Soft Masking with Wiener Filter 
 % More sophisticated separation using spectral characteristics 
 
 % Estimate speech and music spectrograms 
 speechMag = magnitude .* speechMaskFull; 
 musicMag = magnitude .* musicMaskFull; 
 
 % Wiener filtering for better separation 
 epsilon = 1e-10; 
 speechWiener = (speechMag.^2) ./ (speechMag.^2 + musicMag.^2 + epsilon); 
 musicWiener = (musicMag.^2) ./ (speechMag.^2 + musicMag.^2 + epsilon); 
 
 % Apply Wiener masks 
 speechMagFinal = magnitude .* speechWiener; 
 musicMagFinal = magnitude .* musicWiener; 
 
 %% Reconstruct Audio Signals 
 fprintf('Reconstructing audio signals...\n'); 
 
 % Reconstruct with original phase 
 speechSTFT = speechMagFinal .* exp(1j * phase); 
 musicSTFT = musicMagFinal .* exp(1j * phase); 
 
 % Inverse STFT using overlap-add 
 speechAudio = istft_custom(speechSTFT, window, hopLength, nfft); 
 musicAudio = istft_custom(musicSTFT, window, hopLength, nfft); 
 
 % Trim to original length 
 speechAudio = speechAudio(1:min(length(speechAudio), length(mixedAudio))); 
 musicAudio = musicAudio(1:min(length(musicAudio), length(mixedAudio))); 

% Optional: constrain speech to telephone band (300–3400 Hz)
nyq = fs / 2;
bp_hi = min(speech_hi_hz, nyq - 1);
bp_lo = min(speech_lo_hz, bp_hi - 1);
if bp_lo > 0 && bp_hi > bp_lo
    [b_bp, a_bp] = butter(4, [bp_lo bp_hi] / nyq, 'bandpass');
    speechAudio = filtfilt(b_bp, a_bp, speechAudio);
end
 
 % Normalize outputs 
 speechAudio = speechAudio / max(abs(speechAudio) + eps) * 0.9; 
 musicAudio = musicAudio / max(abs(musicAudio) + eps) * 0.9; 
 
 %% Save separated audio files 
 [~, name, ~] = fileparts(filename); 
 speechFilename = fullfile(pathname, [name '_kmeans_speech.wav']); 
 musicFilename = fullfile(pathname, [name '_kmeans_music.wav']); 
 
 audiowrite(speechFilename, speechAudio, fs); 
 audiowrite(musicFilename, musicAudio, fs); 
 
 fprintf('Saved: %s\n', speechFilename); 
 fprintf('Saved: %s\n', musicFilename); 
 
 %% Visualization 
 figure('Position', [100, 100, 1200, 800]); 
 
 % Original spectrogram 
 subplot(3, 2, 1); 
 imagesc(T, F/1000, 20*log10(magnitude + eps)); 
 axis xy; 
 colorbar; 
 title('Original Mixed Audio Spectrogram'); 
 xlabel('Time (s)'); 
 ylabel('Frequency (kHz)'); 
 ylim([0 8]); 
 
 % Speech mask 
 subplot(3, 2, 2); 
 imagesc(T, F/1000, speechWiener); 
 axis xy; 
 colorbar; 
 title('Speech Mask'); 
 xlabel('Time (s)'); 
 ylabel('Frequency (kHz)'); 
 ylim([0 8]); 
 
 % Speech spectrogram 
 subplot(3, 2, 3); 
 imagesc(T, F/1000, 20*log10(speechMagFinal + eps)); 
 axis xy; 
 colorbar; 
 title('Separated Speech Spectrogram'); 
 xlabel('Time (s)'); 
 ylabel('Frequency (kHz)'); 
 ylim([0 8]); 
 
 % Music spectrogram 
 subplot(3, 2, 4); 
 imagesc(T, F/1000, 20*log10(musicMagFinal + eps)); 
 axis xy; 
 colorbar; 
 title('Separated Music Spectrogram'); 
 xlabel('Time (s)'); 
 ylabel('Frequency (kHz)'); 
 ylim([0 8]); 
 
 % Waveforms 
 subplot(3, 2, 5); 
 t = (0:length(mixedAudio)-1) / fs; 
 plot(t, mixedAudio); 
 title('Original Mixed Audio'); 
 xlabel('Time (s)'); 
 ylabel('Amplitude'); 
 xlim([0 t(end)]); 
 
 subplot(3, 2, 6); 
 hold on; 
 plot(t(1:length(speechAudio)), speechAudio, 'b', 'DisplayName', 'Speech'); 
 plot(t(1:length(musicAudio)), musicAudio, 'r', 'DisplayName', 'Music'); 
 title('Separated Audio'); 
 xlabel('Time (s)'); 
 ylabel('Amplitude'); 
 legend; 
 xlim([0 t(end)]); 
 hold off; 
 
 sgtitle('Music/Speech Separation Results'); 
 saveas(gcf, 'kmeans_separation_results.png');
 fprintf('Separation complete!\n'); 
 
 %% Helper Function: Inverse STFT 
 function x = istft_custom(S, window, hopLength, nfft) 
     [numBins, numFrames] = size(S); 
     frameLength = length(window); 
     
     % Output length 
     outputLength = (numFrames - 1) * hopLength + frameLength; 
     x = zeros(outputLength, 1); 
     windowSum = zeros(outputLength, 1); 
     
     for i = 1:numFrames 
         % Inverse FFT 
         frame = real(ifft(S(:, i), nfft)); 
         frame = frame(1:frameLength); 
         
         % Apply window 
         frame = frame .* window; 
         
         % Overlap-add 
         startIdx = (i - 1) * hopLength + 1; 
         endIdx = startIdx + frameLength - 1; 
         
         x(startIdx:endIdx) = x(startIdx:endIdx) + frame; 
         windowSum(startIdx:endIdx) = windowSum(startIdx:endIdx) + window.^2; 
     end 
     
     % Normalize by window sum 
     x = x ./ (windowSum + eps); 
 end

 function [idx, C] = kmeans_custom(X, k)
     % Simple K-means implementation
     % X: data matrix (frames x features)
     % k: number of clusters
     
     numFrames = size(X, 1);
     % Randomly initialize centroids
     C = X(randperm(numFrames, k), :);
     
     max_iters = 50;
     idx = zeros(numFrames, 1);
     
     for iter = 1:max_iters
         % Assign to nearest centroid
         for i = 1:numFrames
             dist = sum((C - X(i, :)).^2, 2);
             [~, idx(i)] = min(dist);
         end
         
         % Update centroids
         C_old = C;
         for j = 1:k
             if any(idx == j)
                 C(j, :) = mean(X(idx == j, :), 1);
             end
         end
         
         % Check for convergence
         if isequal(C, C_old)
             break;
         end
     end
 end
