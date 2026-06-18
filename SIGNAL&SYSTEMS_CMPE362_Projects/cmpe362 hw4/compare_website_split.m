% compare_website_split.m
% Compare website-split stems (music/vocals) against our HW filter outputs.
%
% Inputs expected in current folder:
%   audio [music].mp3
%   audio [vocals].mp3
%   cafe_sample.wav (optional, for reference)
%   music_filtered.wav / speech_filtered.wav (optional)
%
% Outputs:
%   website_music.wav / website_vocals.wav
%   spectrogram_website_split.png
%   metrics printed in Command Window

clear; close all; clc;

musicMp3  = 'audio [music].mp3';
vocalsMp3 = 'audio [vocals].mp3';

mixFile   = 'cafe_sample.wav';
ourVocals = 'music_filtered.wav';   % bandpass (speech audible)
ourMusic  = 'speech_filtered.wav';  % bandstop (music audible)

fprintf('=== Website split comparison ===\n\n');

assert(exist(musicMp3,'file')==2,  'Missing file: %s', musicMp3);
assert(exist(vocalsMp3,'file')==2, 'Missing file: %s', vocalsMp3);

[webMusic,  fsMusic]  = audioread(musicMp3);
[webVocals, fsVocals] = audioread(vocalsMp3);

fprintf('Website music  : %s  | fs=%d Hz | ch=%d | N=%d\n', musicMp3,  fsMusic,  size(webMusic,2),  size(webMusic,1));
fprintf('Website vocals : %s  | fs=%d Hz | ch=%d | N=%d\n\n', vocalsMp3, fsVocals, size(webVocals,2), size(webVocals,1));

% Write WAV copies (easier for MATLAB / playback)
webMusicWav  = 'website_music.wav';
webVocalsWav = 'website_vocals.wav';
audiowrite(webMusicWav,  0.98 * webMusic  / (max(abs(webMusic(:)))  + 1e-12),  fsMusic);
audiowrite(webVocalsWav, 0.98 * webVocals / (max(abs(webVocals(:))) + 1e-12), fsVocals);

fprintf('Wrote: %s\n', webMusicWav);
fprintf('Wrote: %s\n\n', webVocalsWav);

% Load optional reference mixture and our filter outputs
haveMix = exist(mixFile,'file')==2;
haveOurVocals = exist(ourVocals,'file')==2;
haveOurMusic  = exist(ourMusic,'file')==2;

if haveMix
    [mix, fsMix] = audioread(mixFile);
    fprintf('Mixture        : %s | fs=%d Hz | ch=%d | N=%d\n', mixFile, fsMix, size(mix,2), size(mix,1));
else
    fsMix = [];
end

if haveOurVocals
    [oursV, fsOursV] = audioread(ourVocals);
    fprintf('Our vocals-ish : %s | fs=%d Hz | ch=%d | N=%d\n', ourVocals, fsOursV, size(oursV,2), size(oursV,1));
else
    fsOursV = [];
end

if haveOurMusic
    [oursM, fsOursM] = audioread(ourMusic);
    fprintf('Our music-ish  : %s | fs=%d Hz | ch=%d | N=%d\n', ourMusic, fsOursM, size(oursM,2), size(oursM,1));
else
    fsOursM = [];
end

fprintf('\n');

% Helper for basic loudness stats
rmsDb = @(x) 20*log10(sqrt(mean(x(:).^2)) + 1e-12);
peakDb = @(x) 20*log10(max(abs(x(:))) + 1e-12);

fprintf('Levels (RMS dBFS / Peak dBFS)\n');
fprintf('  Web music  : %7.2f / %7.2f\n', rmsDb(webMusic),  peakDb(webMusic));
fprintf('  Web vocals : %7.2f / %7.2f\n', rmsDb(webVocals), peakDb(webVocals));
if haveOurVocals
    fprintf('  Our vocals : %7.2f / %7.2f\n', rmsDb(oursV), peakDb(oursV));
end
if haveOurMusic
    fprintf('  Our music  : %7.2f / %7.2f\n', rmsDb(oursM), peakDb(oursM));
end
fprintf('\n');

% Similarity metrics (only if sample rates match)
if haveOurVocals && (fsOursV == fsVocals)
    a = mean(webVocals, 2);
    b = mean(oursV, 2);
    L = min(numel(a), numel(b));
    a = a(1:L); b = b(1:L);
    a = a - mean(a); b = b - mean(b);
    corrVocals = (a' * b) / ((norm(a) * norm(b)) + 1e-12);
    fprintf('Correlation(web vocals, our vocals-ish) = %.4f (1=very similar)\n', corrVocals);
else
    if haveOurVocals
        fprintf('Correlation(web vocals vs our vocals-ish) skipped: sample rate mismatch (%d vs %d).\n', fsVocals, fsOursV);
    end
end

if haveOurMusic && (fsOursM == fsMusic)
    a = mean(webMusic, 2);
    b = mean(oursM, 2);
    L = min(numel(a), numel(b));
    a = a(1:L); b = b(1:L);
    a = a - mean(a); b = b - mean(b);
    corrMusic = (a' * b) / ((norm(a) * norm(b)) + 1e-12);
    fprintf('Correlation(web music,  our music-ish)  = %.4f (1=very similar)\n', corrMusic);
else
    if haveOurMusic
        fprintf('Correlation(web music vs our music-ish) skipped: sample rate mismatch (%d vs %d).\n', fsMusic, fsOursM);
    end
end

fprintf('\n');

% Spectrogram montage (use mono for display)
figure('Name','Website split spectrograms','NumberTitle','off');

k = 1;
if haveMix
    subplot(2,2,k);
    spectrogram(mean(mix,2), hann(2048), 1024, 2048, fsMix, 'yaxis');
    title('Mixture: cafe\_sample.wav');
    ylim([0 12]); colorbar; k = k + 1;
end

subplot(2,2,k);
spectrogram(mean(webVocals,2), hann(2048), 1024, 2048, fsVocals, 'yaxis');
title('Website vocals (MP3)');
ylim([0 12]); colorbar; k = k + 1;

subplot(2,2,k);
spectrogram(mean(webMusic,2), hann(2048), 1024, 2048, fsMusic, 'yaxis');
title('Website music (MP3)');
ylim([0 12]); colorbar; k = k + 1;

if haveOurVocals
    subplot(2,2,k);
    spectrogram(mean(oursV,2), hann(2048), 1024, 2048, fsOursV, 'yaxis');
    title('Our bandpass (music\_filtered.wav)');
    ylim([0 12]); colorbar;
end

colormap hot;
saveas(gcf, 'spectrogram_website_split.png');

fprintf('Saved: spectrogram_website_split.png\n');
fprintf('=== Done ===\n');
