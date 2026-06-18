% Clear workspace and close figures
clear; close all;

% Process all audio files
filenames = {'low_pitch.wav', 'high_pitch.wav', 'whistle.wav', 'complex.wav', 'complex_recreate.wav'};

for file_idx = 1:length(filenames)
    filename = filenames{file_idx};
    
    % Step 1: Load audio file
    [y, fs] = audioread(filename);  % y = audio data, fs = sampling rate (Hz)

    % Handle stereo to mono (if your recording has 2 channels)
    if size(y, 2) > 1
        y = mean(y, 2);  % Average channels to make mono
    end

    % Step 2: Plot Spectrogram using inbuilt function
    figure('Position', [100, 100, 800, 600]);
    
    % Parameters for a nice and smooth spectrogram
    window = hamming(2048); % 2048-point Hamming window for good frequency resolution
    noverlap = 1536;        % 75% overlap for smooth time resolution
    nfft = 4096;            % 4096-point FFT for smooth frequency interpolation
    
    % Draw spectrogram
    spectrogram(y, window, noverlap, nfft, fs, 'yaxis');
    
    % Formatting
    colormap jet;
    title(['Spectrogram of ', strrep(filename, '_', '\_')]);
    xlabel('Time (seconds)');
    ylabel('Frequency (Hz)');
    
    % Save as image
    saveas(gcf, [filename(1:end-4) '_spectrogram.png']);

    % Step 3: Plot Autocorrelation
    [c, lags] = xcorr(y, 'coeff');  % 'coeff' normalizes so zero lag is 1.0
    time_lags = lags / fs;  % Convert to seconds

    figure('Position', [100, 100, 800, 400]);
    plot(time_lags, c, 'LineWidth', 1.2);
    xlabel('Time (seconds)');
    ylabel('Normalized Autocorrelation');
    title(['Autocorrelation of ', strrep(filename, '_', '\_')]);
    grid on;
    
    % Zoom in to see the periodic peaks clearly (e.g., +/- 50 ms)
    xlim([-0.05 0.05]);  
    
    % Save as image
    saveas(gcf, [filename(1:end-4) '_autocorr.png']);
    
    close all;  % Close figures after saving
end