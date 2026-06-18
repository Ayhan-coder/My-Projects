%% Method 3: Non-negative Matrix Factorization (NMF) Source Separation
% Based on EliasKokkinis/audio-source-separation approach
% NMF decomposes the spectrogram into basis spectra and activations

clear; clc; close all;

%% Load and Run Separation
mixFile = 'cafe_sample.wav';
if ~isfile(mixFile)
    error('Input file %s not found.', mixFile);
end

[mixedAudio, fs] = audioread(mixFile);
if size(mixedAudio, 2) > 1, mixedAudio = mean(mixedAudio, 2); end

fprintf('Running NMF on %s...\n', mixFile);
[music, speech] = nmf_separation(mixedAudio, fs);

%% Save Results
audiowrite('cafe_sample_nmf_music.wav', music, fs);
audiowrite('cafe_sample_nmf_speech.wav', speech, fs);
fprintf('Saved separated files (nmf_music and nmf_speech).\n');

%% Visualization
figure('Position', [100, 100, 1000, 600]);
subplot(3,1,1);
spectrogram(mixedAudio, hann(2048), 1024, 2048, fs, 'yaxis');
title('Original mixture'); ylim([0 8]); colormap hot;

subplot(3,1,2);
spectrogram(music, hann(2048), 1024, 2048, fs, 'yaxis');
title('NMF Music'); ylim([0 8]); colormap hot;

subplot(3,1,3);
spectrogram(speech, hann(2048), 1024, 2048, fs, 'yaxis');
title('NMF Speech'); ylim([0 8]); colormap hot;

saveas(gcf, 'nmf_separation_results.png');
fprintf('Saved visualization to nmf_separation_results.png\n');

%% NMF Separation Functions
function [music, speech] = nmf_separation(mixedAudio, fs)
    
    % STFT parameters
    windowLength = 1024;
    hopSize = 256;
    analysisWindow  = hamming(windowLength, 'periodic');
    synthesisWindow = hanning(windowLength, 'periodic')./hamming(windowLength, 'periodic');
    
    % Load data
    % Analyze into frames
    inputFrames = overlap_window_analysis(mixedAudio, windowLength, hopSize, analysisWindow);
    % Perform FFT
    X = fft(inputFrames);
    % Power spectrogram
    V = abs(X(1:end/2 + 1, :)).^2;
    % Ensure non-negative values
    V(V<=0) = 1e-12;
    
    % NMF parameters
    K = 2;  % Two components: music and speech
    beta = 1;  % Kullback-Leibler divergence
    lambda = 0.1;  % Sparsity parameter
    nIterations = 100;
    
    % Perform NMF
    [W, H, ~] = nmf(V, K, nIterations, 1e-6, beta, lambda, [], []);
    
    % Filter and reconstruct
    % Estimated spectrogram
    Vh = W*H;
    
    % Classify components as music or speech based on spectral characteristics
    componentTypes = classify_nmf_components(W, fs, windowLength);
    
    musicMag = zeros(size(V));
    speechMag = zeros(size(V));
    
    for k = 1 : K
        % Pseudo-Wiener mask
        mask = (W(:, k)*H(k, :))./Vh;
        
        % Add to appropriate component based on classification
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

function componentTypes = classify_nmf_components(W, fs, windowLength)
    % Classify NMF components as music or speech based on spectral characteristics
    K = size(W, 2);
    componentTypes = cell(K, 1);
    
    % Frequency bins
    freqBins = ((0:windowLength/2) * fs / windowLength).';
    
    for k = 1:K
        component = W(:, k);
        
        % Calculate spectral features
        % Spectral centroid
        spectralCentroid = sum(freqBins .* component) / (sum(component) + eps);
        
        % Harmonicity measure (energy in harmonic vs noise regions)
        lowFreqEnergy = sum(component(freqBins < 1000));
        highFreqEnergy = sum(component(freqBins >= 1000));
        harmonicRatio = lowFreqEnergy / (lowFreqEnergy + highFreqEnergy + eps);
        
        % Music typically has lower spectral centroid and higher harmonic ratio
        if spectralCentroid < 2000 && harmonicRatio > 0.6
            componentTypes{k} = 'music';
        else
            componentTypes{k} = 'speech';
        end
    end
end

function frames = overlap_window_analysis(x, frameLength, hopSize, window)
    % Overlap-window analysis
    numFrames = floor((length(x) - frameLength) / hopSize) + 1;
    frames = zeros(frameLength, numFrames);
    
    for i = 1:numFrames
        startIdx = (i - 1) * hopSize + 1;
        endIdx = startIdx + frameLength - 1;
        frames(:, i) = x(startIdx:endIdx) .* window;
    end
end

function x = overlap_window_synthesis(frames, hopSize, window)
    % Overlap-window synthesis
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

function [W, H, J] = nmf(V, K, nIterations, epsilon, beta, lambda, W0, H0)
% This function calculates the NMF of V with rank K based on the
% generalized beta divergence with sparsity parameter lambda.
%
% INPUTS:
%  V             - Input matrix (size FxN)
%  K             - Number of components/Rank of factorization
%  nIterations   - The number of iterations
%  epsilon       - The minimum value of change between iterations
%  beta          - Choose divergence (0 = Itakura-Saito, 1 = Kullback-Leibler, 2 = Euclidean)
%  lambda        - Sparsity parameter for H
%
% OUTPUTS:
%  W             - Spectral profile matrix (size FxK)
%  H             - Activation function matrix (size KxN)
%  J             - Cost function per iteration

% Extract data dimensions
[F, N] = size(V);

% Random initialization of matrices
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

% Estimate spectrogram
Vh = W*H;
% Initialize vector to hold values of cost function
J = zeros(nIterations, 1);
J(1) = beta_distance(V, Vh, beta);

for i = 2 : nIterations
    % 'Negative' gradient
    Hn = W'*(V.*(Vh.^(beta - 2)));
    % 'Positive' gradient
    Hp = W'*(Vh.^(beta - 1)) + lambda;
    % Multiplicative update rule for H
    H = H.*(Hn./(Hp + 1e-12));
    
    % Estimate spectrogram
    Vh = W*H;
    
    % 'Negative' gradient
    Wn = (V.*(Vh.^(beta - 2)))*H';
    % 'Positive' gradient
    Wp = (Vh.^(beta - 1))*H';
    % Multiplicative update rule for W
    W = W.*(Wn./(Wp + 1e-12));
    
    % Estimate spectrogram
    Vh = W*H;
    
    % Estimate distance and check for convergence
    J(i) = beta_distance(V, Vh, beta);
    if abs(J(i) - J(i - 1)) < epsilon
        break;
    end
end
end

function d = beta_distance(V, Vh, beta)
% Calculate beta divergence between V and Vh
if beta == 0
    % Itakura-Saito divergence
    d = sum(sum((V./Vh) - log(V./Vh + 1e-12) - 1));
elseif beta == 1
    % Kullback-Leibler divergence
    d = sum(sum(V.*log(V./(Vh + 1e-12) + 1e-12) - V + Vh));
else
    % General beta divergence
    d = sum(sum((V.^beta + (beta-1)*Vh.^beta - beta*V.*Vh.^(beta-1)) / (beta*(beta-1))));
end
end
