%% Comprehensive Comparison of All Audio Source Separation Methods
% Including: HPSS, K-means, NMF, ICA (EliasKokkinis approaches), DRNN (DRNN4ASS-inspired)

clear; clc; close all;

%% Load Test Audio
mixFile = 'cafe_sample.wav';
if ~isfile(mixFile)
    error('Input file %s not found.', mixFile);
end

[mixedAudio, fs] = audioread(mixFile);
if size(mixedAudio, 2) > 1, mixedAudio = mean(mixedAudio, 2); end

fprintf('=== Audio Source Separation Methods Comparison ===\n');
fprintf('Input file: %s\n', mixFile);
fprintf('Sample rate: %d Hz\n', fs);
fprintf('Duration: %.2f seconds\n\n', length(mixedAudio)/fs);

%% Method 1: HPSS (Harmonic-Percussive Source Separation)
fprintf('1. Running HPSS method...\n');
try
    tic;
    [music_hpss, speech_hpss] = hpss_separation(mixedAudio, fs);
    time_hpss = toc;
    fprintf('   HPSS completed in %.2f seconds\n', time_hpss);
    audiowrite('comparison_hpss_music.wav', music_hpss, fs);
    audiowrite('comparison_hpss_speech.wav', speech_hpss, fs);
    success_hpss = true;
catch ME
    fprintf('   HPSS failed: %s\n', ME.message);
    success_hpss = false;
    time_hpss = NaN;
end

%% Method 2: K-means Clustering
fprintf('2. Running K-means method...\n');
try
    tic;
    [music_kmeans, speech_kmeans] = kmeans_separation(mixedAudio, fs);
    time_kmeans = toc;
    fprintf('   K-means completed in %.2f seconds\n', time_kmeans);
    audiowrite('comparison_kmeans_music.wav', music_kmeans, fs);
    audiowrite('comparison_kmeans_speech.wav', speech_kmeans, fs);
    success_kmeans = true;
catch ME
    fprintf('   K-means failed: %s\n', ME.message);
    success_kmeans = false;
    time_kmeans = NaN;
end

%% Method 3: NMF (Non-negative Matrix Factorization)
fprintf('3. Running NMF method...\n');
try
    tic;
    [music_nmf, speech_nmf] = nmf_separation(mixedAudio, fs);
    time_nmf = toc;
    fprintf('   NMF completed in %.2f seconds\n', time_nmf);
    audiowrite('comparison_nmf_music.wav', music_nmf, fs);
    audiowrite('comparison_nmf_speech.wav', speech_nmf, fs);
    success_nmf = true;
catch ME
    fprintf('   NMF failed: %s\n', ME.message);
    success_nmf = false;
    time_nmf = NaN;
end

%% Method 4: ICA (Independent Component Analysis)
fprintf('4. Running ICA method...\n');
try
    tic;
    [music_ica, speech_ica] = ica_separation(mixedAudio, fs);
    time_ica = toc;
    fprintf('   ICA completed in %.2f seconds\n', time_ica);
    audiowrite('comparison_ica_music.wav', music_ica, fs);
    audiowrite('comparison_ica_speech.wav', speech_ica, fs);
    success_ica = true;
catch ME
    fprintf('   ICA failed: %s\n', ME.message);
    success_ica = false;
    time_ica = NaN;
end

%% Method 5: DRNN (Deep Recurrent Neural Network)
fprintf('5. Running DRNN method...\n');
try
    tic;
    [music_drnn, speech_drnn] = drnn_separation(mixedAudio, fs);
    time_drnn = toc;
    fprintf('   DRNN completed in %.2f seconds\n', time_drnn);
    audiowrite('comparison_drnn_music.wav', music_drnn, fs);
    audiowrite('comparison_drnn_speech.wav', speech_drnn, fs);
    success_drnn = true;
catch ME
    fprintf('   DRNN failed: %s\n', ME.message);
    success_drnn = false;
    time_drnn = NaN;
end

%% Performance Comparison
fprintf('\n=== Performance Comparison ===\n');
methods = {};
times = [];
success = [];

if success_hpss
    methods{end+1} = 'HPSS';
    times(end+1) = time_hpss;
    success(end+1) = true;
end
if success_kmeans
    methods{end+1} = 'K-means';
    times(end+1) = time_kmeans;
    success(end+1) = true;
end
if success_nmf
    methods{end+1} = 'NMF';
    times(end+1) = time_nmf;
    success(end+1) = true;
end
if success_ica
    methods{end+1} = 'ICA';
    times(end+1) = time_ica;
    success(end+1) = true;
end
if success_drnn
    methods{end+1} = 'DRNN';
    times(end+1) = time_drnn;
    success(end+1) = true;
end

if ~isempty(methods)
    [~, idx] = sort(times);
    fprintf('Method ranking by speed:\n');
    for i = 1:length(idx)
        fprintf('   %d. %s: %.2f seconds\n', i, methods{idx(i)}, times(idx(i)));
    end
end

%% Quality Assessment (Simple Metrics)
fprintf('\n=== Quality Assessment ===\n');
if success_hpss
    quality_hpss = assess_separation_quality(music_hpss, speech_hpss, mixedAudio);
    fprintf('HPSS Quality Score: %.3f\n', quality_hpss);
end
if success_kmeans
    quality_kmeans = assess_separation_quality(music_kmeans, speech_kmeans, mixedAudio);
    fprintf('K-means Quality Score: %.3f\n', quality_kmeans);
end
if success_nmf
    quality_nmf = assess_separation_quality(music_nmf, speech_nmf, mixedAudio);
    fprintf('NMF Quality Score: %.3f\n', quality_nmf);
end
if success_ica
    quality_ica = assess_separation_quality(music_ica, speech_ica, mixedAudio);
    fprintf('ICA Quality Score: %.3f\n', quality_ica);
end
if success_drnn
    quality_drnn = assess_separation_quality(music_drnn, speech_drnn, mixedAudio);
    fprintf('DRNN Quality Score: %.3f\n', quality_drnn);
end

%% Comprehensive Visualization
fprintf('\nGenerating comprehensive visualization...\n');

% Determine grid layout
num_methods = sum(success);
if num_methods <= 2
    rows = 3; cols = 2;
elseif num_methods <= 4
    rows = 3; cols = 4;
else
    rows = 4; cols = 6;
end

figure('Position', [50, 50, 1200, 800]);

% Original mixture
subplot(rows, cols, 1);
spectrogram(mixedAudio, hann(2048), 1024, 2048, fs, 'yaxis');
title('Original Mixture'); ylim([0 8]); colormap hot;

plot_idx = 2;

% Plot each successful method
if success_hpss
    subplot(rows, cols, plot_idx);
    spectrogram(music_hpss, hann(2048), 1024, 2048, fs, 'yaxis');
    title('HPSS Music'); ylim([0 8]); colormap hot;
    
    subplot(rows, cols, plot_idx + cols);
    spectrogram(speech_hpss, hann(2048), 1024, 2048, fs, 'yaxis');
    title('HPSS Speech'); ylim([0 8]); colormap hot;
    plot_idx = plot_idx + 1;
end

if success_kmeans
    subplot(rows, cols, plot_idx);
    spectrogram(music_kmeans, hann(2048), 1024, 2048, fs, 'yaxis');
    title('K-means Music'); ylim([0 8]); colormap hot;
    
    subplot(rows, cols, plot_idx + cols);
    spectrogram(speech_kmeans, hann(2048), 1024, 2048, fs, 'yaxis');
    title('K-means Speech'); ylim([0 8]); colormap hot;
    plot_idx = plot_idx + 1;
end

if success_nmf
    subplot(rows, cols, plot_idx);
    spectrogram(music_nmf, hann(2048), 1024, 2048, fs, 'yaxis');
    title('NMF Music'); ylim([0 8]); colormap hot;
    
    subplot(rows, cols, plot_idx + cols);
    spectrogram(speech_nmf, hann(2048), 1024, 2048, fs, 'yaxis');
    title('NMF Speech'); ylim([0 8]); colormap hot;
    plot_idx = plot_idx + 1;
end

if success_ica
    subplot(rows, cols, plot_idx);
    spectrogram(music_ica, hann(2048), 1024, 2048, fs, 'yaxis');
    title('ICA Music'); ylim([0 8]); colormap hot;
    
    subplot(rows, cols, plot_idx + cols);
    spectrogram(speech_ica, hann(2048), 1024, 2048, fs, 'yaxis');
    title('ICA Speech'); ylim([0 8]); colormap hot;
    plot_idx = plot_idx + 1;
end

if success_drnn
    subplot(rows, cols, plot_idx);
    spectrogram(music_drnn, hann(2048), 1024, 2048, fs, 'yaxis');
    title('DRNN Music'); ylim([0 8]); colormap hot;
    
    subplot(rows, cols, plot_idx + cols);
    spectrogram(speech_drnn, hann(2048), 1024, 2048, fs, 'yaxis');
    title('DRNN Speech'); ylim([0 8]); colormap hot;
end

sgtitle('Audio Source Separation Methods Comparison');
saveas(gcf, 'comparison_all_methods.png');
fprintf('Saved comprehensive comparison to comparison_all_methods.png\n');

fprintf('\n=== Comparison Complete ===\n');

%% Helper Functions
function [music, speech] = hpss_separation(mixedAudio, fs)
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

function [music, speech] = kmeans_separation(mixedAudio, fs)
    % Parameters 
    frameLength = round(0.03 * fs);    
    hopLength = round(0.01 * fs);      
    nfft = 2^nextpow2(frameLength); 
    
    % Compute STFT 
    window = hamming(frameLength); 
    [S, F, T] = spectrogram(mixedAudio, window, frameLength - hopLength, nfft, fs); 
    magnitude = abs(S); 
    phase = angle(S); 
    
    % Extract Features for Classification 
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
        highFreqIdx = F > 4000; 
        features(i, 6) = sum(frame_mag(highFreqIdx)) / (sum(frame_mag) + eps); 
    end 
    
    % Normalize features 
    features = (features - mean(features)) ./ (std(features) + eps); 
    
    % Classification using K-means (2 clusters: music and speech) 
    [clusterIdx, ~] = kmeans_custom(features, 2); 
    
    % Determine which cluster is speech 
    cluster1_var = var(features(clusterIdx == 1, 1)); 
    cluster2_var = var(features(clusterIdx == 2, 1)); 
    
    if cluster1_var > cluster2_var 
        speechCluster = 1; 
    else 
        speechCluster = 2; 
    end 
    
    speechMask = (clusterIdx == speechCluster); 
    musicMask = ~speechMask; 
    
    % Create Time-Frequency Masks 
    smoothingWindow = 5; 
    speechMaskSmooth = movmean(double(speechMask), smoothingWindow); 
    musicMaskSmooth = movmean(double(musicMask), smoothingWindow); 
    
    % Expand masks to full spectrogram size 
    speechMaskFull = repmat(speechMaskSmooth', size(magnitude, 1), 1); 
    musicMaskFull = repmat(musicMaskSmooth', size(magnitude, 1), 1); 
    
    % Apply Soft Masking with Wiener Filter 
    speechMag = magnitude .* speechMaskFull; 
    musicMag = magnitude .* musicMaskFull; 
    
    epsilon = 1e-10; 
    speechWiener = (speechMag.^2) ./ (speechMag.^2 + musicMag.^2 + epsilon); 
    musicWiener = (musicMag.^2) ./ (speechMag.^2 + musicMag.^2 + epsilon); 
    
    % Apply Wiener masks 
    speechMagFinal = magnitude .* speechWiener; 
    musicMagFinal = magnitude .* musicWiener; 
    
    % Reconstruct Audio Signals 
    speechSTFT = speechMagFinal .* exp(1j * phase); 
    musicSTFT = musicMagFinal .* exp(1j * phase); 
    
    % Inverse STFT using overlap-add 
    speechAudio = istft_custom(speechSTFT, window, hopLength, nfft); 
    musicAudio = istft_custom(musicSTFT, window, hopLength, nfft); 
    
    % Trim to original length 
    speechAudio = speechAudio(1:min(length(speechAudio), length(mixedAudio))); 
    musicAudio = musicAudio(1:min(length(musicAudio), length(mixedAudio))); 
    
    % Normalize outputs 
    speech = speechAudio / max(abs(speechAudio) + eps) * 0.9; 
    music = musicAudio / max(abs(musicAudio) + eps) * 0.9; 
end

function [music, speech] = nmf_separation(mixedAudio, fs)
    % STFT parameters
    windowLength = 1024;
    hopSize = 256;
    analysisWindow  = hamming(windowLength, 'periodic');
    synthesisWindow = hanning(windowLength, 'periodic')./hamming(windowLength, 'periodic');
    
    % Load data
    inputFrames = overlap_window_analysis(mixedAudio, windowLength, hopSize, analysisWindow);
    X = fft(inputFrames);
    V = abs(X(1:end/2 + 1, :)).^2;
    V(V<=0) = 1e-12;
    
    % NMF parameters
    K = 2;
    beta = 1;
    lambda = 0.1;
    nIterations = 50; % Reduced for speed
    
    % Perform NMF
    [W, H, ~] = nmf(V, K, nIterations, 1e-6, beta, lambda, [], []);
    
    % Filter and reconstruct
    Vh = W*H;
    
    % Classify components
    componentTypes = classify_nmf_components(W, fs, windowLength);
    
    musicMag = zeros(size(V));
    speechMag = zeros(size(V));
    
    for k = 1 : K
        mask = (W(:, k)*H(k, :))./Vh;
        if strcmp(componentTypes{k}, 'music')
            musicMag = musicMag + mask;
        else
            speechMag = speechMag + mask;
        end
    end
    
    % Apply masks to original magnitude spectrum
    originalMag = sqrt(V);
    musicMag = musicMag .* originalMag;
    speechMag = speechMag .* originalMag;
    
    % Reconstruct with original phase
    musicSTFT = [musicMag; musicMag(end-1:-1:2, :)] .* exp(1j * angle(X));
    speechSTFT = [speechMag; speechMag(end-1:-1:2, :)] .* exp(1j * angle(X));
    
    % Apply IFFT and synthesize
    musicFrames = real(ifft(musicSTFT));
    speechFrames = real(ifft(speechSTFT));
    
    music = overlap_window_synthesis(musicFrames, hopSize, synthesisWindow);
    speech = overlap_window_synthesis(speechFrames, hopSize, synthesisWindow);
    
    % Trim to original length
    music = music(1:min(length(music), length(mixedAudio)));
    speech = speech(1:min(length(speech), length(mixedAudio)));
    
    % Normalize
    music = music / (max(abs(music)) + eps) * 0.9;
    speech = speech / (max(abs(speech)) + eps) * 0.9;
end

function [music, speech] = ica_separation(mixedAudio, fs)
    % Create multi-channel signal for ICA
    numChannels = 3;
    X = create_multichannel_signal(mixedAudio, fs, numChannels);
    
    % Pre-processing
    [N, samples] = size(X);
    M = repmat(mean(X, 2), [1 samples]);
    Xn = X - M;
    
    % Covariance matrix and whitening
    C = cov(Xn');
    [E, D] = eig(C);
    sqrtD = diag(sqrt(diag(D)));
    Tw = inv(sqrtD)*E';
    
    % Whiten the data
    Z = Tw*Xn;
    
    % FastICA
    B = fastICA(Z, 'negentropy', 50, 1e-6); % Reduced iterations for speed
    
    % Post-processing
    W = B'*Tw;
    Y = W*X + (W*M);
    
    % Classify components
    componentTypes = classify_ica_components(Y, fs);
    
    % Extract music and speech components
    musicComponent = zeros(size(mixedAudio));
    speechComponent = zeros(size(mixedAudio));
    
    for i = 1:size(Y, 1)
        component = Y(i, 1:length(mixedAudio))';
        if strcmp(componentTypes{i}, 'music')
            musicComponent = musicComponent + component;
        else
            speechComponent = speechComponent + component;
        end
    end
    
    % Normalize
    music = musicComponent / (max(abs(musicComponent)) + eps) * 0.9;
    speech = speechComponent / (max(abs(speechComponent)) + eps) * 0.9;
end

function quality = assess_separation_quality(music, speech, mixed)
    % Simple quality assessment based on:
    % 1. Reconstruction error
    % 2. Cross-correlation between components
    % 3. Energy distribution
    
    % Reconstruction error
    reconstructed = music + speech;
    reconstructed = reconstructed(1:length(mixed));
    reconstruction_error = mean((mixed - reconstructed).^2);
    
    % Cross-correlation (lower is better)
    correlation = abs(correlation(music, speech));
    
    % Energy balance
    music_energy = sum(music.^2);
    speech_energy = sum(speech.^2);
    energy_balance = abs(music_energy - speech_energy) / (music_energy + speech_energy + eps);
    
    % Combined quality score (higher is better)
    quality = 1 / (1 + reconstruction_error + correlation + energy_balance);
end

% Include all necessary helper functions from previous implementations
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

function x = istft_custom(S, window, hopLength, nfft) 
    [numBins, numFrames] = size(S); 
    frameLength = length(window); 
    
    outputLength = (numFrames - 1) * hopLength + frameLength; 
    x = zeros(outputLength, 1); 
    windowSum = zeros(outputLength, 1); 
    
    for i = 1:numFrames 
        frame = real(ifft(S(:, i), nfft)); 
        frame = frame(1:frameLength); 
        frame = frame .* window; 
        
        startIdx = (i - 1) * hopLength + 1; 
        endIdx = startIdx + frameLength - 1; 
        
        x(startIdx:endIdx) = x(startIdx:endIdx) + frame; 
        windowSum(startIdx:endIdx) = windowSum(startIdx:endIdx) + window.^2; 
    end 
    
    x = x ./ (windowSum + eps); 
end

function [idx, C] = kmeans_custom(X, k)
    numFrames = size(X, 1);
    C = X(randperm(numFrames, k), :);
    max_iters = 50;
    idx = zeros(numFrames, 1);
    
    for iter = 1:max_iters
        for i = 1:numFrames
            dist = sum((C - X(i, :)).^2, 2);
            [~, idx(i)] = min(dist);
        end
        
        C_old = C;
        for j = 1:k
            if any(idx == j)
                C(j, :) = mean(X(idx == j, :), 1);
            end
        end
        
        if isequal(C, C_old)
            break;
        end
    end
end

% Include NMF, ICA, and other helper functions...

function frames = overlap_window_analysis(x, frameLength, hopSize, window)
    numFrames = floor((length(x) - frameLength) / hopSize) + 1;
    frames = zeros(frameLength, numFrames);
    
    for i = 1:numFrames
        startIdx = (i - 1) * hopSize + 1;
        endIdx = startIdx + frameLength - 1;
        frames(:, i) = x(startIdx:endIdx) .* window;
    end
end

function x = overlap_window_synthesis(frames, hopSize, window)
    [frameLength, numFrames] = size(frames);
    outputLength = (numFrames - 1) * hopSize + frameLength;
    x = zeros(outputLength, 1);
    windowSum = zeros(outputLength, 1);
    
    for i = 1:numFrames
        startIdx = (i - 1) * hopSize + 1;
        endIdx = startIdx + frameLength - 1;
        
        frame = frames(:, i) .* window;
        x(startIdx:endIdx) = x(startIdx:endIdx) + frame;
        windowSum(startIdx:endIdx) = windowSum(startIdx:endIdx) + window.^2;
    end
    
    x = x ./ (windowSum + eps);
end

function componentTypes = classify_nmf_components(W, fs, windowLength)
    K = size(W, 2);
    componentTypes = cell(K, 1);
    freqBins = (0:windowLength/2) * fs / windowLength;
    
    for k = 1:K
        component = W(:, k);
        spectralCentroid = sum(freqBins .* component) / (sum(component) + eps);
        lowFreqEnergy = sum(component(freqBins < 1000));
        highFreqEnergy = sum(component(freqBins >= 1000));
        harmonicRatio = lowFreqEnergy / (lowFreqEnergy + highFreqEnergy + eps);
        
        if spectralCentroid < 2000 && harmonicRatio > 0.6
            componentTypes{k} = 'music';
        else
            componentTypes{k} = 'speech';
        end
    end
end

function X = create_multichannel_signal(monoSignal, fs, numChannels)
    X = zeros(numChannels, length(monoSignal));
    
    [b1, a1] = butter(4, 2000/(fs/2), 'low');
    X(1, :) = filtfilt(b1, a1, monoSignal);
    
    [b2, a2] = butter(4, [1000 4000]/(fs/2), 'bandpass');
    X(2, :) = filtfilt(b2, a2, monoSignal);
    
    [b3, a3] = butter(4, 1000/(fs/2), 'high');
    X(3, :) = filtfilt(b3, a3, monoSignal);
    
    X = X + 0.01 * randn(size(X));
end

function componentTypes = classify_ica_components(Y, fs)
    numComponents = size(Y, 1);
    componentTypes = cell(numComponents, 1);
    
    for i = 1:numComponents
        component = Y(i, :);
        zcr = sum(abs(diff(sign(component)))) / (2 * length(component));
        
        frameLength = round(0.02 * fs);
        hopSize = round(0.01 * fs);
        energy = zeros(1, floor((length(component) - frameLength) / hopSize) + 1);
        
        for j = 1:length(energy)
            startIdx = (j - 1) * hopSize + 1;
            endIdx = startIdx + frameLength - 1;
            if endIdx <= length(component)
                energy(j) = sum(component(startIdx:endIdx).^2);
            end
        end
        
        energyVariance = var(energy);
        
        if zcr > 0.1 || energyVariance > 0.001
            componentTypes{i} = 'speech';
        else
            componentTypes{i} = 'music';
        end
    end
end

function W = fastICA(X, measure, maxIter, epsilon)
    [N, samples] = size(X);
    W = randn(N);
    W_old = zeros(size(W));

    for i = 1 : maxIter
        W = W * real(inv(W' * W)^(1/2));
        
        minAbsCos = min(abs(diag(W' * W_old)));
        if (1 - minAbsCos < epsilon)
            break;
        end
        
        W_old = W;
        
        switch measure
            case 'kurtosis'
                W = X*(X'*W).^3 - 3*(ones(N, 1)*mean((X'*W).^2))*W;
            case 'negentropy'
                hypTan = tanh(X'*W);
                W = X*hypTan/samples - ones(N, 1)*sum(1 - hypTan.^2).*W/samples;
            otherwise
                error('Unsupported non-linearity');
        end
    end
end

function [W, H, J] = nmf(V, K, nIterations, epsilon, beta, lambda, W0, H0)
    [F, N] = size(V);

    if isempty(W0)
        W = abs(randn(F, K));
    else
        W = W0;
    end

    if isempty(H0)
        H = abs(randn(K, N));
    else
        H = H0;
    end

    Vh = W*H;
    J = zeros(nIterations, 1);
    J(1) = beta_distance(V, Vh, beta);

    for i = 2 : nIterations
        Hn = W'*(V.*(Vh.^(beta - 2)));
        Hp = W'*(Vh.^(beta - 1)) + lambda;
        H = H.*(Hn./(Hp + 1e-12));
        
        Vh = W*H;
        
        Wn = (V.*(Vh.^(beta - 2)))*H';
        Wp = (Vh.^(beta - 1))*H';
        W = W.*(Wn./(Wp + 1e-12));
        
        Vh = W*H;
        
        J(i) = beta_distance(V, Vh, beta);
        if abs(J(i) - J(i - 1)) < epsilon
            break;
        end
    end
end

function d = beta_distance(V, Vh, beta)
    if beta == 0
        d = sum(sum((V./Vh) - log(V./Vh + 1e-12) - 1));
    elseif beta == 1
        d = sum(sum(V.*log(V./(Vh + 1e-12) + 1e-12) - V + Vh));
    else
        d = sum(sum((V.^beta + (beta-1)*Vh.^beta - beta*V.*Vh.^(beta-1)) / (beta*(beta-1))));
    end
end

function [music, speech] = drnn_separation(mixedAudio, fs)
    % DRNN separation function (simplified version)
    
    % STFT parameters
    windowLength = 1024;
    hopSize = 256;
    nFFT = 1024;
    window = sin(0:pi/windowLength:pi-pi/windowLength)'; % Sine window
    
    % Compute STFT
    [S, ~, ~] = spectrogram(mixedAudio, window, windowLength - hopSize, nFFT, fs);
    magnitude = abs(S);
    phase = angle(S);
    
    % Log-magnitude features
    logMagnitude = log(magnitude.^2 + eps);
    
    % Initialize simplified DRNN parameters
    networkParams = initialize_drnn_parameters(size(logMagnitude, 1), fs);
    
    % Forward pass through simplified DRNN
    [musicMask, speechMask] = drnn_forward_pass(logMagnitude, networkParams);
    
    % Apply masks to original magnitude spectrum
    musicMag = magnitude .* musicMask;
    speechMag = magnitude .* speechMask;
    
    % Reconstruct with original phase
    musicSTFT = musicMag .* exp(1j * phase);
    speechSTFT = speechMag .* exp(1j * phase);
    
    % Inverse STFT
    music = istft_custom(musicSTFT, window, hopSize, nFFT);
    speech = istft_custom(speechSTFT, window, hopSize, nFFT);
    
    % Trim to original length
    music = music(1:min(length(music), length(mixedAudio)));
    speech = speech(1:min(length(speech), length(mixedAudio)));
    
    % Normalize
    music = music / (max(abs(music)) + eps) * 0.9;
    speech = speech / (max(abs(speech)) + eps) * 0.9;
end

function params = initialize_drnn_parameters(freqBins, fs)
    % Initialize simplified DRNN parameters
    params.inputDim = freqBins;
    params.hiddenDim = min(128, freqBins);
    params.outputDim = freqBins;
    
    % Frequency-dependent weights
    freqVector = (0:freqBins-1)' * fs / (2 * freqBins);
    
    % Music tends to have energy in lower frequencies
    params.musicWeights = exp(-((freqVector - 500).^2) / (2 * 1000^2));
    % Speech tends to have more energy in mid-high frequencies
    params.speechWeights = exp(-((freqVector - 2000).^2) / (2 * 1500^2));
    
    % Temporal recurrence weights
    params.musicRecurrence = 0.8;
    params.speechRecurrence = 0.6;
    
    % Masking parameters
    params.maskSharpness = 2.0;
    params.gain = 1.0;
end

function [musicMask, speechMask] = drnn_forward_pass(logMagnitude, params)
    % Simplified forward pass through DRNN
    
    [freqBins, numFrames] = size(logMagnitude);
    musicMask = zeros(freqBins, numFrames);
    speechMask = zeros(freqBins, numFrames);
    
    % Initialize hidden states
    musicHidden = zeros(params.hiddenDim, 1);
    speechHidden = zeros(params.hiddenDim, 1);
    
    for t = 1:numFrames
        % Current frame features
        currentFrame = logMagnitude(:, t);
        
        % Music pathway (with recurrence)
        musicInput = params.musicWeights .* currentFrame;
        musicHidden = params.musicRecurrence * musicHidden + musicInput;
        musicHidden = tanh(musicHidden);
        
        % Speech pathway (with recurrence)
        speechInput = params.speechWeights .* currentFrame;
        speechHidden = params.speechRecurrence * speechHidden + speechInput;
        speechHidden = tanh(speechHidden);
        
        % Generate masks
        musicActivation = params.musicWeights' * musicHidden;
        speechActivation = params.speechWeights' * speechHidden;
        
        % Soft masking
        combined = exp(musicActivation) + params.gain * exp(speechActivation) + eps;
        musicMask(:, t) = exp(musicActivation) ./ combined;
        speechMask(:, t) = params.gain * exp(speechActivation) ./ combined;
        
        % Apply mask sharpening
        musicMask(:, t) = musicMask(:, t) .^ params.maskSharpness;
        speechMask(:, t) = speechMask(:, t) .^ params.maskSharpness;
        
        % Renormalize
        totalMask = musicMask(:, t) + speechMask(:, t) + eps;
        musicMask(:, t) = musicMask(:, t) ./ totalMask;
        speechMask(:, t) = speechMask(:, t) ./ totalMask;
    end
    
    % Temporal smoothing
    smoothWindow = 3;
    musicMask = movmean(musicMask, smoothWindow, 2);
    speechMask = movmean(speechMask, smoothWindow, 2);
    
    % Ensure masks sum to 1
    totalMask = musicMask + speechMask + eps;
    musicMask = musicMask ./ totalMask;
    speechMask = speechMask ./ totalMask;
end
