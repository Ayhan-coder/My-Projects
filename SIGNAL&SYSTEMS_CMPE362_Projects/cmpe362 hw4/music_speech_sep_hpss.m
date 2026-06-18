%% Method 2: Harmonic-Percussive Source Separation (HPSS) 
 % Music tends to be more harmonic, speech has more transients 
 
 clear; clc; close all;

 %% Load and Run Separation
 mixFile = 'cafe_sample.wav';
 if ~isfile(mixFile)
     error('Input file %s not found.', mixFile);
 end
 
 [mixedAudio, fs] = audioread(mixFile);
 if size(mixedAudio, 2) > 1, mixedAudio = mean(mixedAudio, 2); end
 
 fprintf('Running HPSS on %s...\n', mixFile);
 [music, speech] = hpss_separation(mixedAudio, fs);
 
 %% Save Results
 audiowrite('cafe_sample_hpss_music.wav', music, fs);
 audiowrite('cafe_sample_hpss_speech.wav', speech, fs);
 fprintf('Saved separated files (hpss_music and hpss_speech).\n');

 %% Visualization
 figure('Position', [100, 100, 1000, 600]);
 subplot(3,1,1);
 spectrogram(mixedAudio, hann(2048), 1024, 2048, fs, 'yaxis');
 title('Original mixture'); ylim([0 8]); colormap hot;
 
 subplot(3,1,2);
 spectrogram(music, hann(2048), 1024, 2048, fs, 'yaxis');
 title('HPSS Music (Harmonic)'); ylim([0 8]); colormap hot;
 
 subplot(3,1,3);
 spectrogram(speech, hann(2048), 1024, 2048, fs, 'yaxis');
 title('HPSS Speech (Percussive/Transient)'); ylim([0 8]); colormap hot;
 
 saveas(gcf, 'hpss_separation_results.png');
 fprintf('Saved visualization to hpss_separation_results.png\n');

 %% Separation Functions
 function [music, speech] = hpss_separation(mixedAudio, fs) 
     
     % Parameters 
     frameLength = round(0.046 * fs);  % ~46ms 
     hopLength = round(frameLength / 4); 
     nfft = 2^nextpow2(frameLength); 
     
     % Compute STFT 
     window = hann(frameLength); 
     [S, ~, ~] = spectrogram(mixedAudio, window, frameLength - hopLength, nfft, fs); 
     magnitude = abs(S); 
     phase = angle(S); 
     
     % Median filtering for HPSS 
     harmonicKernelSize = 17;  % Horizontal (time) for harmonic 
     percussiveKernelSize = 17;  % Vertical (frequency) for percussive 
     
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
