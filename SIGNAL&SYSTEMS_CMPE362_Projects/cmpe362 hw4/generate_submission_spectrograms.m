% generate_submission_spectrograms.m
% Generates spectrogram PNGs required by PRESENTATION_REPORT.tex.
% Writes images into best/ so you can compile the PDF inside best/.

clear; close all; clc;

% Resolve output dir relative to this file
this_file = mfilename('fullpath');
root_dir = fileparts(this_file);
best_dir = fullfile(root_dir, 'best');

in_original = fullfile(best_dir, 'cafe_sample.wav');
in_speech   = fullfile(best_dir, 'speech_filtered.wav');
in_music    = fullfile(best_dir, 'music_filtered.wav');

if ~isfile(in_original)
    error('Missing %s', in_original);
end
if ~isfile(in_speech)
    error('Missing %s', in_speech);
end
if ~isfile(in_music)
    error('Missing %s', in_music);
end

make_spec(in_original, fullfile(best_dir, 'spectrogram_original.png'), 'cafe\_sample.wav');
make_spec(in_speech,   fullfile(best_dir, 'spectrogram_speech_filtered.png'), 'speech\_filtered.wav');
make_spec(in_music,    fullfile(best_dir, 'spectrogram_music_filtered.png'), 'music\_filtered.wav');

fprintf('Saved spectrogram PNGs into: %s\n', best_dir);

function make_spec(wav_path, png_path, plot_title)
    [x, fs] = audioread(wav_path);
    if size(x, 2) > 1
        x = mean(x, 2);
    end

    win_len = 2048;
    hop_len = 512;
    window = blackman(win_len, 'periodic');

    fig = figure('Visible','off','Color','w','Position',[50 50 1200 500]);
    spectrogram(x, window, win_len-hop_len, win_len, fs, 'yaxis');
    title(plot_title);
    ylim([0 10]);
    colormap hot;
    set(gca, 'FontSize', 12);

    exportgraphics(fig, png_path, 'Resolution', 200);
    close(fig);
end
