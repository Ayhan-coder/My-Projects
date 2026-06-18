%% Method 4: Independent Component Analysis (ICA) Source Separation
% Based on EliasKokkinis/audio-source-separation approach
% ICA assumes statistical independence of source signals

clear; clc; close all;

%% Load and Run Separation
mixFile = 'cafe_sample.wav';
if ~isfile(mixFile)
    error('Input file %s not found.', mixFile);
end

[mixedAudio, fs] = audioread(mixFile);
if size(mixedAudio, 2) > 1, mixedAudio = mean(mixedAudio, 2); end

fprintf('Running ICA on %s...\n', mixFile);
[music, speech] = ica_separation(mixedAudio, fs);

%% Save Results
audiowrite('cafe_sample_ica_music.wav', music, fs);
audiowrite('cafe_sample_ica_speech.wav', speech, fs);
fprintf('Saved separated files (ica_music and ica_speech).\n');

%% Visualization
figure('Position', [100, 100, 1000, 600]);
subplot(3,1,1);
spectrogram(mixedAudio, hann(2048), 1024, 2048, fs, 'yaxis');
title('Original mixture'); ylim([0 8]); colormap hot;

subplot(3,1,2);
spectrogram(music, hann(2048), 1024, 2048, fs, 'yaxis');
title('ICA Music'); ylim([0 8]); colormap hot;

subplot(3,1,3);
spectrogram(speech, hann(2048), 1024, 2048, fs, 'yaxis');
title('ICA Speech'); ylim([0 8]); colormap hot;

saveas(gcf, 'ica_separation_results.png');
fprintf('Saved visualization to ica_separation_results.png\n');

%% ICA Separation Functions
function [music, speech] = ica_separation(mixedAudio, fs)
    
    % Create multi-channel signal for ICA
    % ICA works best with multiple observations, so we create
    % different filtered versions of the mono signal
    numChannels = 3;
    
    % Create different frequency bands as separate "channels"
    X = create_multichannel_signal(mixedAudio, fs, numChannels);
    
    % Pre-processing
    % Extract dimensions
    [N, samples] = size(X);
    
    % Remove mean
    M = repmat(mean(X, 2), [1 samples]);
    Xn = X - M;
    
    % Covariance matrix
    C = cov(Xn');
    % EVD
    [E, D] = eig(C);
    % Calculate whitening matrix
    sqrtD = diag(sqrt(diag(D)));
    Tw = inv(sqrtD)*E';
    Td = E*sqrtD;
    
    % Whiten the data
    Z = Tw*Xn;
    
    % FastICA
    B = fastICA(Z, 'negentropy', 100, 1e-6);
    
    % Post-processing
    % Unmixing matrix
    W = B'*Tw;
    % Separated signals (don't forget to add back the mean!)
    Y = W*X + (W*M);
    
    % Classify components as music or speech
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

function X = create_multichannel_signal(monoSignal, fs, numChannels)
    % Create multiple "observations" from mono signal using different filters
    X = zeros(numChannels, length(monoSignal));
    
    % Channel 1: Original signal (low-pass filtered)
    [b1, a1] = butter(4, 2000/(fs/2), 'low');
    X(1, :) = filtfilt(b1, a1, monoSignal);
    
    % Channel 2: Band-pass filtered (mid frequencies)
    [b2, a2] = butter(4, [300 3400]/(fs/2), 'bandpass');
    X(2, :) = filtfilt(b2, a2, monoSignal);
    
    % Channel 3: High-pass filtered
    [b3, a3] = butter(4, 1000/(fs/2), 'high');
    X(3, :) = filtfilt(b3, a3, monoSignal);
    
    % Add small amount of noise to make channels more independent
    X = X + 0.01 * randn(size(X));
end

function componentTypes = classify_ica_components(Y, fs)
    % Classify ICA components as music or speech based on temporal characteristics
    numComponents = size(Y, 1);
    componentTypes = cell(numComponents, 1);
    
    for i = 1:numComponents
        component = Y(i, :);
        
        % Calculate temporal features
        % Zero crossing rate
        zcr = sum(abs(diff(sign(component)))) / (2 * length(component));
        
        % Short-term energy variance
        frameLength = round(0.02 * fs); % 20ms frames
        hopSize = round(0.01 * fs); % 10ms hop
        energy = zeros(1, floor((length(component) - frameLength) / hopSize) + 1);
        
        for j = 1:length(energy)
            startIdx = (j - 1) * hopSize + 1;
            endIdx = startIdx + frameLength - 1;
            if endIdx <= length(component)
                energy(j) = sum(component(startIdx:endIdx).^2);
            end
        end
        
        energyVariance = var(energy);
        
        % Speech typically has higher zero crossing rate and energy variance
        if zcr > 0.1 || energyVariance > 0.001
            componentTypes{i} = 'speech';
        else
            componentTypes{i} = 'music';
        end
    end
end

function W = fastICA(X, measure, maxIter, epsilon)
% This function implementes the FastICA method
%
% INPUTS
%   X       - The preprocessed input data (N x samples)
%   measure - The measure to maximize ('kurtosis' or 'negentropy')
%   maxIter - The maximum number of iterations
%   epsilon - The minimum change between iterations
%
% OUTPUTS
%   W       - The unmixing matrix. It needs post-processing

% Extract dimension
[N, samples] = size(X);
% Random initialization
W = randn(N);
% Previous estimation
W_old = zeros(size(W));

for i = 1 : maxIter
    % Symmetric orthogonalization.
    W = W * real(inv(W' * W)^(1/2));
    
    minAbsCos = min(abs(diag(W' * W_old)));
    if (1 - minAbsCos < epsilon)
        fprintf('FastICA converged after %d iterations!\n', i);
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

if i == maxIter
    fprintf('FastICA reached maximum number of iterations!\n');
end
end
