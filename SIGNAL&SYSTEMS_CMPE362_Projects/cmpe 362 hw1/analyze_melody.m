% Analyze complex.wav to identify melody notes
clear; close all;

% Load the audio file
filename = 'complex.wav';
[y, fs] = audioread(filename);

% Handle stereo to mono
if size(y, 2) > 1
    y = mean(y, 2);
end

% Create detailed spectrogram for analysis
figure('Position', [100, 100, 1200, 500]);

winLen = 1024;
overlap = floor(winLen / 2);
nfft = max(256, 2^nextpow2(winLen));

win = 0.54 - 0.46 * cos(2 * pi * (0:winLen-1)' / (winLen-1));
step = winLen - overlap;
numFrames = floor((length(y) - winLen) / step) + 1;
s = zeros(nfft, numFrames);

for i = 1:numFrames
    startIdx = (i-1)*step + 1;
    segment = y(startIdx : startIdx + winLen - 1) .* win;
    fft_seg = fft(segment, nfft);
    s(:, i) = fft_seg;
end

f = (0:nfft/2) * fs / nfft;
t = (0:numFrames-1) * step / fs;
s = s(1:nfft/2+1, :);

% Plot with better visualization
imagesc(t, f, 10*log10(abs(s).^2 + eps));
axis xy;
colormap jet;
colorbar;
xlabel('Time (s)');
ylabel('Frequency (Hz)');
title('Complex Melody Spectrogram - Zoom in on bright areas to identify note frequencies');
ylim([0 2000]);  % Focus on typical voice range

% Add grid for easier reading
grid on;

fprintf('\n=== INSTRUCTIONS FOR MANUAL FREQUENCY IDENTIFICATION ===\n');
fprintf('1. Look at the spectrogram image on screen\n');
fprintf('2. Identify bright horizontal lines - these are the notes (fundamental frequencies)\n');
fprintf('3. Note the approximate start and end times of each note\n');
fprintf('4. Note the frequency (Hz) of each bright line\n');
fprintf('5. Count approximately 4-8 notes for a typical melody\n');
fprintf('\nTYPICAL MUSIC NOTE FREQUENCIES (reference):\n');
fprintf('C4: 262 Hz, D4: 294 Hz, E4: 330 Hz, F4: 349 Hz\n');
fprintf('G4: 392 Hz, A4: 440 Hz, B4: 494 Hz\n');
fprintf('C5: 523 Hz, D5: 587 Hz, E5: 659 Hz, F5: 698 Hz\n');
fprintf('G5: 784 Hz, A5: 880 Hz, B5: 988 Hz\n\n');

% Save for reference
saveas(gcf, 'complex_analysis_spectrogram.png');
fprintf('Spectrogram saved as complex_analysis_spectrogram.png\n');
