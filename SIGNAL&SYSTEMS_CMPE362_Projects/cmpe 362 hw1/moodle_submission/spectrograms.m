% spectrograms.m
% CMPE 362 - Homework 1
% Name: Ali Ayhan Günder
% Date: February 22, 2026
% Draw spectrograms and autocorrelations

clear; close all;

files = {'low.wav', 'high.wav', 'whistle.wav', 'complex.wav'};

% Process each file
for k = 1:numel(files)
    currentFile = files{k};
    [y, fs] = audioread(currentFile);

    % Ensure mono
    if size(y,2) > 1
        y = mean(y, 2);
    end

    % Params for good resolution
    window   = hamming(2048);
    noverlap = 1536;   % 75% overlap
    nfft     = 4096;

    % 1. Spectrogram
    figure('Position',[100 100 800 600]);
    spectrogram(y, window, noverlap, nfft, fs, 'yaxis');
    colormap jet;
    title(['Spectrogram of ' strrep(currentFile,'_','\_')]);
    xlabel('Time (s)');
    ylabel('Frequency (Hz)');
    
    % Zoom in based on file content to show details
    if contains(currentFile, 'low')
        % Default zoom (no specific ylim for low/high unless requested)
    elseif contains(currentFile, 'high')
        % Default zoom
    elseif contains(currentFile, 'whistle')
        ylim([0 3000]); % Whistle is around 1200Hz
    elseif contains(currentFile, 'complex')
        ylim([0 2500]);
    end

    % Save spectrogram
    outSpec = [currentFile(1:end-4) '_spectrogram.png'];
    saveas(gcf, outSpec);

    % 2. Autocorrelation
    [c, lags] = xcorr(y, 'coeff');
    t_lags = lags / fs;

    figure('Position',[100 100 800 400]);
    plot(t_lags, c, 'LineWidth', 1.2);
    grid on;
    xlabel('Lag (s)');
    ylabel('Normalized autocorrelation');
    title(['Autocorrelation of ' strrep(currentFile,'_','\_')]);
    
    % Zoom near zero
    xlim([-0.05 0.05]); 

    % Save autocorr
    outAuto = [currentFile(1:end-4) '_autocorr.png'];
    saveas(gcf, outAuto);
end
