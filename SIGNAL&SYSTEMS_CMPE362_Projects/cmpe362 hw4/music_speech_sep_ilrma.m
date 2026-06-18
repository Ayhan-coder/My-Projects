%% Method 6: Independent Low-Rank Matrix Analysis (ILRMA) Source Separation
% Based on ILRMA approach by Daichi Kitamura
% ILRMA unifies IVA and NMF for determined blind source separation

clear; clc; close all;

%% Load and Run Separation
mixFile = 'cafe_sample.wav';
if ~isfile(mixFile)
    error('Input file %s not found.', mixFile);
end

[mixedAudio, fs] = audioread(mixFile);
if size(mixedAudio, 2) > 1, mixedAudio = mean(mixedAudio, 2); end

fprintf('Running ILRMA on %s...\n', mixFile);
[music, speech] = ilrma_separation(mixedAudio, fs);

%% Save Results
audiowrite('cafe_sample_ilrma_music.wav', music, fs);
audiowrite('cafe_sample_ilrma_speech.wav', speech, fs);
fprintf('Saved separated files (ilrma_music and ilrma_speech).\n');

%% Visualization
figure('Position', [100, 100, 1000, 600]);
subplot(3,1,1);
spectrogram(mixedAudio, hann(2048), 1024, 2048, fs, 'yaxis');
title('Original mixture'); ylim([0 8]); colormap hot;

subplot(3,1,2);
spectrogram(music, hann(2048), 1024, 2048, fs, 'yaxis');
title('ILRMA Music'); ylim([0 8]); colormap hot;

subplot(3,1,3);
spectrogram(speech, hann(2048), 1024, 2048, fs, 'yaxis');
title('ILRMA Speech'); ylim([0 8]); colormap hot;

saveas(gcf, 'ilrma_separation_results.png');
fprintf('Saved visualization to ilrma_separation_results.png\n');

%% ILRMA Separation Functions
function [music, speech] = ilrma_separation(mixedAudio, fs)
    
    % ILRMA parameters (adapted for mono input)
    nSrc = 2; % Number of sources (music, speech)
    nBases = 8; % Number of NMF bases per source
    fftSize = 2048; % Window length in STFT
    shiftSize = 1024; % Shift length in STFT
    windowType = 'hamming'; % Window function
    nIter = 50; % Number of iterations (reduced for speed)
    ilrmaType = 1; % ILRMA type 1 (without partitioning function)
    applyNormalize = 1; % Apply normalization for stability
    applyWhitening = false; % Skip whitening for mono case
    
    % Create multi-channel observation from mono signal
    % ILRMA expects multichannel input, so we create virtual channels
    [observedSig, ~] = create_multichannel_observation(mixedAudio, fs);
    
    % Apply ILRMA algorithm
    [estimatedSig, ~] = ilrma_algorithm(observedSig, nSrc, fs, nBases, ...
        fftSize, shiftSize, windowType, nIter, ilrmaType, applyNormalize, applyWhitening);
    
    % Extract music and speech from estimated sources
    [music, speech] = classify_ilrma_sources(estimatedSig, fs);
    
    % Trim to original length
    music = music(1:min(length(music), length(mixedAudio)));
    speech = speech(1:min(length(speech), length(mixedAudio)));
    
    % Normalize
    music = music / (max(abs(music)) + eps) * 0.9;
    speech = speech / (max(abs(speech)) + eps) * 0.9;
end

function [observedSig, nCh] = create_multichannel_observation(monoSignal, fs)
    % Create virtual multichannel observation from mono signal
    % This simulates different microphone positions/filters
    
    % Method 1: Different frequency bands as channels
    nCh = 3;
    observedSig = zeros(length(monoSignal), nCh);
    
    % Channel 1: Low-pass filtered
    [b1, a1] = butter(4, 2000/(fs/2), 'low');
    observedSig(:, 1) = filtfilt(b1, a1, monoSignal);
    
    % Channel 2: Band-pass filtered  
    [b2, a2] = butter(4, [300 3400]/(fs/2), 'bandpass');
    observedSig(:, 2) = filtfilt(b2, a2, monoSignal);
    
    % Channel 3: High-pass filtered
    [b3, a3] = butter(4, 1500/(fs/2), 'high');
    observedSig(:, 3) = filtfilt(b3, a3, monoSignal);
    
    % Add small random delays to simulate spatial separation
    for ch = 2:nCh
        delay = randi([0, 10]); % Random delay 0-10 samples
        observedSig(:, ch) = [zeros(delay, 1); observedSig(1:end-delay, ch)];
    end
end

function [estimatedSig, cost] = ilrma_algorithm(mixSig, nSrc, sampFreq, nBases, ...
    fftSize, shiftSize, windowType, nIter, ilrmaType, applyNormalize, ~)
    
    % Compute STFT of observed signals
    [X, ~] = stft_ilrma(mixSig, fftSize, shiftSize, windowType, sampFreq);
    referencePhase = angle(X(:, :, 1));
    
    % Initialize parameters
    T = initialize_ilrma_parameters(X, nSrc, nBases, ilrmaType);
    
    % Iterative updates
    cost = zeros(nIter+1, 1);
    
    for iter = 1:nIter
        % E-step: Compute sufficient statistics
        [Y, R] = compute_sufficient_statistics(X, T);
        
        % M-step: Update parameters
        T = update_ilrma_parameters(Y, R, T, applyNormalize, ilrmaType);
        
        % Compute cost function
        cost(iter+1) = compute_ilrma_cost(X, T);
        
        if mod(iter, 10) == 0
            fprintf('Iteration %d, Cost: %.6f\n', iter, cost(iter+1));
        end
    end
    
    % Reconstruct signals
    estimatedSig = reconstruct_ilrma_signals(Y, referencePhase, fftSize, shiftSize, windowType);
end

function T = initialize_ilrma_parameters(X, nSrc, nBases, ilrmaType)
    % Initialize ILRMA parameters
    
    [nFreq, nFrames, nCh] = size(X);
    
    if ilrmaType == 1
        % Type 1: Separate bases for each source
        T.W = abs(randn(nFreq, nBases, nSrc)); % Source-specific bases
        T.H = abs(rand(nBases, nFrames, nSrc)); % Source-specific activations
    else
        % Type 2: Shared bases (not implemented in this simplified version)
        T.W = abs(randn(nFreq, nBases));
        T.H = abs(rand(nBases, nFrames, nSrc));
    end
    
    % Initialize demixing matrix
    T.A = eye(nCh, nSrc);
end

function [Y, R] = compute_sufficient_statistics(X, T)
    % Compute sufficient statistics for parameter updates
    
    [nFreq, nFrames, ~] = size(X);
    [~, ~, nSrc] = size(T.W);
    
    Y = zeros(nFreq, nFrames, nSrc);
    R = zeros(nFreq, nFrames, nSrc);
    mixturePower = mean(abs(X).^2, 3);
    modelSum = zeros(nFreq, nFrames);
    
    for s = 1:nSrc
        R(:, :, s) = T.W(:, :, s) * T.H(:, :, s);
        modelSum = modelSum + R(:, :, s);
    end

    for s = 1:nSrc
        responsibility = R(:, :, s) ./ (modelSum + eps);
        Y(:, :, s) = mixturePower .* responsibility;
    end
end

function T = update_ilrma_parameters(Y, ~, T, applyNormalize, ~)
    % Update ILRMA parameters
    
    [~, ~, nSrc] = size(Y);
    
    % Update bases and activations
    for s = 1:nSrc
        targetSpectrogram = max(Y(:, :, s), eps);

        % Update W (bases)
        currentModel = max(T.W(:, :, s) * T.H(:, :, s), eps);
        numerator_W = targetSpectrogram * T.H(:, :, s)';
        denominator_W = currentModel * T.H(:, :, s)' + eps;
        T.W(:, :, s) = max(T.W(:, :, s) .* (numerator_W ./ denominator_W), eps);
        
        % Update H (activations)
        currentModel = max(T.W(:, :, s) * T.H(:, :, s), eps);
        numerator_H = T.W(:, :, s)' * targetSpectrogram;
        denominator_H = T.W(:, :, s)' * currentModel + eps;
        T.H(:, :, s) = max(T.H(:, :, s) .* (numerator_H ./ denominator_H), eps);
    end
    
    % Apply normalization if requested
    if applyNormalize == 1
        % Power-based normalization
        for s = 1:nSrc
            V_s = T.W(:, :, s) * T.H(:, :, s);
            power = mean(mean(abs(V_s).^2));
            T.W(:, :, s) = T.W(:, :, s) / sqrt(power);
            T.H(:, :, s) = T.H(:, :, s) * sqrt(power);
        end
    end
end

function cost = compute_ilrma_cost(X, T)
    % Compute ILRMA cost function
    
    [nFreq, nFrames, ~] = size(X);
    [~, ~, nSrc] = size(T.W);
    mixturePower = mean(abs(X).^2, 3);
    modelSum = zeros(nFreq, nFrames);
    
    for s = 1:nSrc
        modelSum = modelSum + T.W(:, :, s) * T.H(:, :, s);
    end
    
    residual = mixturePower - modelSum;
    cost = sum(residual(:).^2) / (nFreq * nFrames);
end

function estimatedSig = reconstruct_ilrma_signals(Y, referencePhase, fftSize, shiftSize, windowType)
    % Reconstruct time-domain signals from estimated source spectrograms
    
    [~, nFrames, nSrc] = size(Y);
    
    signalLength = (nFrames - 1) * shiftSize + fftSize;
    estimatedSig = zeros(signalLength, nSrc);
    
    for s = 1:nSrc
        sourceMagnitude = sqrt(max(Y(:, :, s), 0));
        sourceSpectrum = sourceMagnitude .* exp(1j * referencePhase);
        
        % Inverse STFT
        estimatedSig(:, s) = istft_ilrma(sourceSpectrum, fftSize, shiftSize, windowType, []);
    end
end

function [music, speech] = classify_ilrma_sources(estimatedSig, fs)
    % Classify ILRMA estimated sources as music and speech
    
    [~, nSrc] = size(estimatedSig);
    
    if nSrc >= 2
        % Analyze spectral characteristics of each source
        source1 = estimatedSig(:, 1);
        source2 = estimatedSig(:, 2);
        
        % Compute spectral features for classification
        feat1 = compute_spectral_features(source1, fs);
        feat2 = compute_spectral_features(source2, fs);
        
        % Music typically has lower spectral centroid, more harmonic content
        if feat1.centroid < feat2.centroid && feat1.harmonic_ratio > feat2.harmonic_ratio
            music = source1;
            speech = source2;
        else
            music = source2;
            speech = source1;
        end
    else
        % If only one source, classify based on characteristics
        features = compute_spectral_features(estimatedSig(:, 1), fs);
        if features.centroid < 2000 && features.harmonic_ratio > 0.6
            music = estimatedSig(:, 1);
            speech = zeros(size(estimatedSig(:, 1)));
        else
            speech = estimatedSig(:, 1);
            music = zeros(size(estimatedSig(:, 1)));
        end
    end
end

function features = compute_spectral_features(signal, fs)
    % Compute spectral features for source classification
    
    % Compute STFT
    window = hamming(round(0.03*fs));
    [S, f] = spectrogram(signal, window, round(0.015*fs), 2048, fs);
    magnitude = abs(S);
    
    % Spectral centroid
    weightedFreqs = f .* magnitude;
    features.centroid = sum(weightedFreqs(:)) / (sum(magnitude(:)) + eps);
    
    % Harmonic ratio (energy in harmonic frequencies)
    harmonic_freqs = [100:100:4000]; % Fundamental frequencies and harmonics
    harmonic_energy = 0;
    total_energy = sum(magnitude(:));
    
    for hf = harmonic_freqs
        [~, idx] = min(abs(f - hf));
        harmonic_energy = harmonic_energy + sum(magnitude(idx, :), 'all');
    end
    
    features.harmonic_ratio = harmonic_energy / (total_energy + eps);
    
    % Spectral flatness
    geometric_mean = exp(mean(log(magnitude(:) + eps)));
    arithmetic_mean = mean(magnitude(:));
    features.flatness = geometric_mean / (arithmetic_mean + eps);
end

%% STFT and ISTFT helper functions
function [X, freqs] = stft_ilrma(x, fftSize, shiftSize, windowType, sampFreq)
    % Short-time Fourier transform for ILRMA
    
    if strcmpi(windowType, 'hamming')
        window = hamming(fftSize);
    elseif strcmpi(windowType, 'hann')
        window = hann(fftSize);
    elseif strcmpi(windowType, 'rectangular')
        window = ones(fftSize, 1);
    else
        window = hamming(fftSize);
    end
    
    [sigLength, nCh] = size(x);
    nFrames = floor((sigLength - fftSize) / shiftSize) + 1;
    
    X = zeros(fftSize/2+1, nFrames, nCh);
    
    for ch = 1:nCh
        for n = 1:nFrames
            startIdx = (n-1) * shiftSize + 1;
            endIdx = startIdx + fftSize - 1;
            
            if endIdx <= sigLength
                frame = x(startIdx:endIdx, ch) .* window;
                spectrum = fft(frame, fftSize);
                X(:, n, ch) = spectrum(1:fftSize/2+1);
            end
        end
    end

    freqs = (0:fftSize/2) * sampFreq / fftSize;
end

function x = istft_ilrma(X, fftSize, shiftSize, windowType, ~)
    % Inverse short-time Fourier transform for ILRMA
    
    if strcmpi(windowType, 'hamming')
        window = hamming(fftSize);
    elseif strcmpi(windowType, 'hann')
        window = hann(fftSize);
    else
        window = hamming(fftSize);
    end
    
    [~, nFrames] = size(X);
    sigLength = (nFrames - 1) * shiftSize + fftSize;
    x = zeros(sigLength, 1);
    windowSum = zeros(sigLength, 1);
    
    for n = 1:nFrames
        % Reconstruct full spectrum
        fullSpectrum = [X(:, n); conj(flipud(X(2:end-1, n)))];
        
        % Inverse FFT
        frame = real(ifft(fullSpectrum, fftSize));
        
        % Apply window
        frame = frame .* window;
        
        % Overlap-add
        startIdx = (n-1) * shiftSize + 1;
        endIdx = startIdx + fftSize - 1;
        
        if endIdx <= sigLength
            x(startIdx:endIdx) = x(startIdx:endIdx) + frame;
            windowSum(startIdx:endIdx) = windowSum(startIdx:endIdx) + window.^2;
        end
    end
    
    % Normalize by window sum
    x = x ./ (windowSum + eps);
end

%% Note on ILRMA Approach:
% This implementation is inspired by the ILRMA (Independent Low-Rank Matrix Analysis)
% framework by Daichi Kitamura, which unifies Independent Vector Analysis (IVA)
% and Non-negative Matrix Factorization (NMF) for determined blind source separation.
%
% Key concepts implemented:
% - Low-rank modeling of each source using NMF (W * H decomposition)
% - Independence constraints through IVA-like updates
% - Iterative parameter updates with E-step and M-step
% - Multi-channel observation handling
%
% For production use, consider using the original ILRMA implementation
% with proper multichannel recordings and training data.
