%% Method 4: Simple Energy-based VAD (No Toolbox Required)
 % This script performs speech/music separation using basic energy 
 % and spectral flatness thresholds.
 
 clear; clc; close all;

 %% 1. Load Audio
 inputFile = 'cafe_sample.wav';
 if ~isfile(inputFile)
     error('Input file %s not found.', inputFile);
 end
 
 [audio, fs] = audioread(inputFile);
 if size(audio, 2) > 1, audio = mean(audio, 2); end
 
 fprintf('Running Simple VAD (No Toolbox) on %s...\n', inputFile);

 %% 2. Feature Extraction (Energy + ZCR)
 frameLen = round(0.03 * fs);
 hopLen = round(0.01 * fs);
 
 numFrames = floor((length(audio) - frameLen) / hopLen) + 1;
 energy = zeros(numFrames, 1);
 zcr = zeros(numFrames, 1);
 
 for i = 1:numFrames
     startIdx = (i-1) * hopLen + 1;
     endIdx = startIdx + frameLen - 1;
     frame = audio(startIdx:endIdx);
     
     % Short-time Energy
     energy(i) = sum(frame.^2);
     
     % Zero Crossing Rate
     zcr(i) = sum(abs(diff(sign(frame)))) / (2 * frameLen);
 end
 
 % Normalize features
 energy = energy / max(energy + eps);
 
 %% 3. VAD Logic
 % Speech typically has higher energy and moderate ZCR compared to background
 % We'll use a combined threshold.
 vad_mask = (energy > 0.1) & (zcr < 0.2); 
 
 % Smooth the mask to avoid rapid flickering
 vad_mask = movmean(double(vad_mask), 15) > 0.4;
 
 %% 4. Separation & Reconstruction
 fprintf('Applying separation masks...\n');
 
 % Create time-domain signals
 speechAudio = zeros(size(audio));
 musicAudio = zeros(size(audio));
 
 for i = 1:numFrames
     startIdx = (i-1) * hopLen + 1;
     endIdx = startIdx + frameLen - 1;
     
     if vad_mask(i)
         speechAudio(startIdx:endIdx) = audio(startIdx:endIdx);
     else
         musicAudio(startIdx:endIdx) = audio(startIdx:endIdx);
     end
 end
 
 % Normalize outputs individually to maximize volume
 speechAudio = speechAudio / (max(abs(speechAudio)) + eps) * 0.95;
 musicAudio = musicAudio / (max(abs(musicAudio)) + eps) * 0.95;
 
 %% 5. Save Results
 [~, name, ~] = fileparts(inputFile);
 audiowrite([name '_simple_vad_speech.wav'], speechAudio, fs);
 audiowrite([name '_simple_vad_music.wav'], musicAudio, fs);
 
 fprintf('Saved separated files with boosted volume: %s_simple_vad_speech.wav and %s_simple_vad_music.wav\n', name, name);

 %% 6. Visualization
 figure('Position', [100, 100, 1000, 400]);
 t = (0:length(audio)-1)/fs;
 plot(t, audio, 'k', 'DisplayName', 'Original'); hold on;
 plot(t, speechAudio, 'b', 'DisplayName', 'Speech (VAD)');
 title('Simple Energy-based VAD Separation');
 xlabel('Time (s)'); ylabel('Amplitude');
 legend; grid on;
 saveas(gcf, 'simple_vad_results.png');
 fprintf('Separation complete!\n');
