% helper_basic_recreate_comparisons.m
% Side-by-side spectrogram comparison for low/high/whiskle and their
% pure-tone recreate versions.

clear; close all;

pairs = {
    'low_pitch.wav',    'low_pitch_recreate.wav';
    'high_pitch.wav',   'high_pitch_recreate.wav';
    'whistle.wav',      'whistle_recreate.wav';
};

for k = 1:size(pairs,1)
    orig_name = pairs{k,1};
    rec_name  = pairs{k,2};

    [y_orig, fs_o] = audioread(orig_name);
    [y_rec,  fs_r] = audioread(rec_name);

    if size(y_orig,2) > 1, y_orig = mean(y_orig,2); end
    if size(y_rec,2)  > 1, y_rec  = mean(y_rec,2);  end

    % Use same fs (all are 48 kHz in this homework)
    fs = fs_o;

    % Spectrogram settings (same as main.m)
    window   = hamming(2048);
    noverlap = 1536;
    nfft     = 4096;

    [S1, F1, T1] = spectrogram(y_orig, window, noverlap, nfft, fs);
    [S2, F2, T2] = spectrogram(y_rec,  window, noverlap, nfft, fs);

    S1_db = 10*log10(abs(S1).^2 + eps);
    S2_db = 10*log10(abs(S2).^2 + eps);

    clim = [min([S1_db(:); S2_db(:)]), max([S1_db(:); S2_db(:)])];

    figure('Position',[100 100 1000 400]);

    subplot(1,2,1);
    imagesc(T1, F1, S1_db); axis xy;
    title(['Original ' strrep(orig_name,'_','\_')]);
    xlabel('Time (s)'); ylabel('Frequency (Hz)');
    caxis(clim);

    subplot(1,2,2);
    imagesc(T2, F2, S2_db); axis xy;
    title(['Recreate ' strrep(rec_name,'_','\_')]);
    xlabel('Time (s)'); ylabel('Frequency (Hz)');
    caxis(clim);

    colormap jet;
    colorbar('Position',[0.92 0.11 0.015 0.815]);

    outname = [orig_name(1:end-4) '_recreate_comparison.png'];
    saveas(gcf, outname);
end
