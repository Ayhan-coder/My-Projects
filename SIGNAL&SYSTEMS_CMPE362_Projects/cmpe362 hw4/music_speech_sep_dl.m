%% Method 3: Pre-trained Deep Learning Model (requires Audio Toolbox) 
 % This uses MATLAB's built-in audio separation capabilities 
 
 clear; clc; close all;

 %% Load and Run Separation
 inputFile = 'cafe_sample.wav';
 outputPath = pwd;

 if ~isfile(inputFile)
     error('Input file %s not found.', inputFile);
 end

 fprintf('Starting Deep Learning / VAD separation on %s...\n', inputFile);
 try
    separate_with_deep_learning(inputFile, outputPath);
    fprintf('Separation complete!\n');
 catch ME
    fprintf('Error during separation: %s\n', ME.message);
 end

 %% Separation Functions
 function separate_with_deep_learning(inputFile, outputPath) 
     % Check if Audio Toolbox is available 
     if ~license('test', 'Audio_Toolbox') 
         error('Audio Toolbox is required for this method'); 
     end 
     
     % Load audio 
     [audio, fs] = audioread(inputFile); 
     if size(audio, 2) > 1, audio = mean(audio, 2); end
     
     % Resample to 16kHz if needed (common for speech models) 
     targetFs = 16000; 
     if fs ~= targetFs 
         fprintf('Resampling to %d Hz...\n', targetFs);
         audio = resample(audio, targetFs, fs); 
         fs = targetFs; 
     end 
     
     % Use voice activity detection to identify speech regions 
     fprintf('Initializing Voice Activity Detector...\n');
     vadObj = voiceActivityDetector('SampleRate', fs); 
     
     frameLength = round(0.032 * fs); 
     hopLength = round(0.008 * fs); 
     
     numFrames = floor((length(audio) - frameLength) / hopLength) + 1; 
     speechProbability = zeros(numFrames, 1); 
     
     fprintf('Processing %d frames...\n', numFrames);
     for i = 1:numFrames 
         startIdx = (i-1) * hopLength + 1; 
         endIdx = startIdx + frameLength - 1; 
         frame = audio(startIdx:endIdx); 
         speechProbability(i) = vadObj(frame); 
     end 
     
     % Create masks based on VAD 
     speechMask = speechProbability > 0.5; 
     musicMask = ~speechMask; 
     
     % Smooth masks 
     speechMask = movmean(double(speechMask), 10) > 0.3; 
     musicMask = movmean(double(musicMask), 10) > 0.3; 
     
     % Apply masks in time domain with crossfade 
     crossfadeLength = round(0.01 * fs); 
     
     fprintf('Applying temporal masks...\n');
     speechAudio = apply_temporal_mask(audio, speechMask, hopLength, frameLength, crossfadeLength); 
     musicAudio = apply_temporal_mask(audio, musicMask, hopLength, frameLength, crossfadeLength); 
     
     % Save outputs 
     [~, name, ~] = fileparts(inputFile); 
     audiowrite(fullfile(outputPath, [name '_speech_dl.wav']), speechAudio, fs); 
     audiowrite(fullfile(outputPath, [name '_music_dl.wav']), musicAudio, fs); 
     fprintf('Saved: %s_speech_dl.wav and %s_music_dl.wav\n', name, name);
 end 
 
 function output = apply_temporal_mask(audio, frameMask, hopLength, frameLength, crossfadeLength) 
     output = zeros(size(audio)); 
     
     for i = 1:length(frameMask) 
         startIdx = (i-1) * hopLength + 1; 
         endIdx = min(startIdx + frameLength - 1, length(audio)); 
         
         if frameMask(i) 
             output(startIdx:endIdx) = audio(startIdx:endIdx); 
         end 
     end 
     
     % Apply smoothing to avoid clicks 
     output = smoothdata(output, 'gaussian', crossfadeLength); 
 end
