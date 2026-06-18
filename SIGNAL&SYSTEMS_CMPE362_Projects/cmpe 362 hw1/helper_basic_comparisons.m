% helper_basic_comparisons.m
% Create spectrogram + autocorrelation comparison figures
% for low_pitch.wav, high_pitch.wav, and whiskle.wav.

clear; close all;

filenames = {'low_pitch.wav', 'high_pitch.wav', 'whistle.wav'};

for k = 1:numel(filenames)
    fname = filenames{k};
    [y, fs] = audioread(fname);
    if size(y,2) > 1
        y = mean(y,2); % mono
    end

    % Spectrogram settings (same as main.m)
    window   = hamming(2048);
    noverlap = 1536;
    nfft     = 4096;

    [S, F, T] = spectrogram(y, window, noverlap, nfft, fs);
    S_db = 10*log10(abs(S).^2 + eps);

    % Autocorrelation
    [c, lags] = xcorr(y, 'coeff');
    t_lags = lags / fs;

    % Figure: left = spectrogram, right = autocorr
    figure('Position',[100 100 1000 400]);

    subplot(1,2,1);
    imagesc(T, F, S_db); axis xy;
    colormap jet;
    xlabel('Time (s)'); ylabel('Frequency (Hz)');
    title(['Spectrogram of ' strrep(fname,'_','\_')]);

    subplot(1,2,2);
    plot(t_lags, c, 'LineWidth', 1.0);
    grid on;
    xlabel('Lag (s)'); ylabel('Normalized Autocorr');
    title(['Autocorrelation of ' strrep(fname,'_','\_')]);
    xlim([-0.05 0.05]);

    outname = [fname(1:end-4) '_comparison.png'];
    saveas(gcf, outname);
end
