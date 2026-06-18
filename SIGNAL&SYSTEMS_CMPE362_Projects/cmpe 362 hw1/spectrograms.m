% spectrograms.m
% CMPE 362 - Homework 1
% Draw spectrograms and autocorrelations for the 4 audio files:
%   low.wav, high.wav, whistle.wav, complex.wav

clear; close all;

filenames = {'low.wav', 'high.wav', 'whistle.wav', 'complex.wav'};

for k = 1:numel(filenames)
    fname = filenames{k};
    [y, fs] = audioread(fname);

    % Convert to mono if stereo
    if size(y,2) > 1
        y = mean(y, 2);
    end

    % Spectrogram parameters (same for all files)
    window   = hamming(2048);
    noverlap = 1536;   % 75%% overlap
    nfft     = 4096;

    figure('Position',[100 100 800 600]);
    spectrogram(y, window, noverlap, nfft, fs, 'yaxis');
    colormap jet;
    title(['Spectrogram of ' strrep(fname,'_','\_')]);
    xlabel('Time (s)');
    ylabel('Frequency (Hz)');

    % Save figure (optional, not required by Moodle)
    outSpec = [fname(1:end-4) '_spectrogram.png'];
    saveas(gcf, outSpec);

    % Autocorrelation
    [c, lags] = xcorr(y, 'coeff');
    t_lags = lags / fs;

    figure('Position',[100 100 800 400]);
    plot(t_lags, c, 'LineWidth', 1.2);
    grid on;
    xlabel('Lag (s)');
    ylabel('Normalized autocorrelation');
    title(['Autocorrelation of ' strrep(fname,'_','\_')]);
    xlim([-0.05 0.05]);   % zoom around zero

    outAuto = [fname(1:end-4) '_autocorr.png'];
    saveas(gcf, outAuto);
end
