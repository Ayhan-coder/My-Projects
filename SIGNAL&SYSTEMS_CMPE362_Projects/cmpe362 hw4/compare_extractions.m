% compare_extractions.m
% CMPE362 HW4 – Compare All Speech Extraction Methods
%
% Generates a side-by-side comparison of all extraction attempts:
%   - Original (cafe_sample.wav)
%   - Simple bandpass (filter_audio.m → music_filtered.wav)
%   - Spectral subtraction v2 (extract_speech_v2.m → speech_clean.wav)
%   - Enhanced v3 (extract_speech_v3.m → speech_enhanced.wav)
%
% Output: comparison_all_methods.png

clear; close all; clc;
fprintf('=== Comparing All Speech Extraction Methods ===\n\n');

%% ─── LOAD ALL FILES ─────────────────────────────────────────────────────────
files = {};
labels = {};

% Original
if isfile('cafe_sample.wav')
    files{end+1} = 'cafe_sample.wav';
    labels{end+1} = 'Original (Cafe Recording)';
end

% Simple bandpass (from filter_audio.m)
if isfile('music_filtered.wav')
    files{end+1} = 'music_filtered.wav';
    labels{end+1} = 'Simple Bandpass (300–3400 Hz)';
end

% Spectral subtraction v2
if isfile('speech_clean.wav')
    files{end+1} = 'speech_clean.wav';
    labels{end+1} = 'Spectral Subtraction (v2)';
end

% Enhanced v3
if isfile('speech_enhanced.wav')
    files{end+1} = 'speech_enhanced.wav';
    labels{end+1} = 'Enhanced (v3 – moderate)';
end

% Min-stats tracking v4
if isfile('speech_v4.wav')
    files{end+1} = 'speech_v4.wav';
    labels{end+1} = 'Min-Stats Tracking (v4)';
end

% Precise 3-way split (v5)
if isfile('speech_v5_precise.wav')
    files{end+1} = 'speech_v5_precise.wav';
    labels{end+1} = 'Precise 3-Way Split (v5)';
end

% Final selected output (copied from preferred method)
if isfile('speech_best.wav')
    files{end+1} = 'speech_best.wav';
    labels{end+1} = 'Final Selected (best)';
end

% REPET-Matlab separation (foreground estimate)
if isfile('speech_repet.wav')
    files{end+1} = 'speech_repet.wav';
    labels{end+1} = 'REPET foreground (speech)';
end

n_files = length(files);
if n_files == 0
    error('No audio files found. Run extraction scripts first.');
end

fprintf('Found %d files to compare:\n', n_files);
signals = cell(1, n_files);
fs_val = 0;

for i = 1:n_files
    [x, fs] = audioread(files{i});
    if size(x,2) == 2, x = mean(x,2); end
    signals{i} = x;
    if fs_val == 0, fs_val = fs; end
    fprintf('  %d. %s\n', i, files{i});
end
fprintf('\n');

%% ─── SIDE-BY-SIDE SPECTROGRAMS ─────────────────────────────────────────────
fprintf('Generating comparison spectrograms...\n');

fig = figure('Name', 'Speech Extraction Method Comparison', ...
             'NumberTitle', 'off', 'Position', [50 50 1600 900]);

for i = 1:n_files
    subplot(n_files, 1, i);
    spectrogram(signals{i}, hann(2048), 1536, 2048, fs_val, 'yaxis');
    title(labels{i}, 'FontSize', 11, 'Interpreter', 'none');
    colormap hot;
    ylim([0 8]);  % focus on speech-relevant band
    colorbar;
    caxis([-80 -20]);
    if i == n_files, xlabel('Time (s)'); end
end

sgtitle('Speech Extraction Methods – Spectrogram Comparison', ...
        'FontSize', 14, 'FontWeight', 'bold');

saveas(fig, 'comparison_all_methods.png');
fprintf('  Saved comparison_all_methods.png\n\n');

%% ─── RMS ENERGY COMPARISON ──────────────────────────────────────────────────
fprintf('=== RMS Energy Comparison ===\n');
fprintf('%-40s  %8s  %8s\n', 'File', 'RMS', '% Orig');
fprintf('%s\n', repmat('-', 1, 60));

rms_orig = rms(signals{1});
for i = 1:n_files
    r = rms(signals{i});
    pct = 100 * r / rms_orig;
    fprintf('%-40s  %8.4f  %7.1f%%\n', files{i}, r, pct);
end
fprintf('\n');

%% ─── SPEECH BAND ENERGY (300-3400 Hz) ───────────────────────────────────────
fprintf('=== Speech Band Energy (300–3400 Hz) ===\n');
fprintf('%-40s  %8s  %8s\n', 'File', 'Band RMS', '% Orig');
fprintf('%s\n', repmat('-', 1, 60));

[b, a] = butter(4, [300 3400]/(fs_val/2), 'bandpass');
sb_orig = rms(filtfilt(b, a, signals{1}));

for i = 1:n_files
    sb = rms(filtfilt(b, a, signals{i}));
    pct = 100 * sb / sb_orig;
    fprintf('%-40s  %8.4f  %7.1f%%\n', files{i}, sb, pct);
end
fprintf('\n');

%% ─── FREQUENCY DISTRIBUTION ──────────────────────────────────────────────────
fprintf('=== Frequency Band Distribution ===\n');
bands = [100 300; 300 1000; 1000 2000; 2000 3400; 3400 8000];
band_names = {'Sub-speech (100–300 Hz)', ...
              'Low speech (300–1k Hz)', ...
              'Mid speech (1–2 kHz)', ...
              'High speech (2–3.4 kHz)', ...
              'Music/noise (3.4–8 kHz)'};

for b_idx = 1:length(band_names)
    fprintf('\n%s:\n', band_names{b_idx});
    [b_filt, a_filt] = butter(3, bands(b_idx,:)/(fs_val/2), 'bandpass');
    
    for i = 1:n_files
        e_band = rms(filtfilt(b_filt, a_filt, signals{i}));
        fprintf('  %-35s  %.4f\n', strrep(files{i}, '.wav', ''), e_band);
    end
end

fprintf('\n=== Done ===\n');
fprintf('Review comparison_all_methods.png for visual comparison.\n');
fprintf('Listen to each file to judge speech clarity vs background suppression.\n\n');

fprintf('RECOMMENDATION:\n');
fprintf('  • speech_enhanced.wav (v3) – best balance of clarity + naturalness\n');
fprintf('  • Adjust v3 preset (mild/moderate/aggressive) in extract_speech_v3.m line 18\n\n');
