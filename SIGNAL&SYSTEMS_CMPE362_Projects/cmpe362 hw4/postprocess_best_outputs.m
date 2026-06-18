% postprocess_best_outputs.m
% Single entry-point postprocessing for the “best” outputs.
%
% Includes:
%   A) Speech v12 ultra: generate 10% softer version (and optional louder copy)
%   B) Music v5 precise: suppress high-frequency transient clinks (fork/spoon)
%
% Run:
%   run('best/postprocess_best_outputs.m')

clear; clc;

%% ===================== Toggle What To Run =====================
run_speech_postprocess = true;
run_music_hfclean      = true;

%% ===================== A) Speech v12 Ultra =====================
soft_factor = 0.9;   % 10% softer (linear amplitude)
make_speech_louder = false;
speech_gain_db = 3;  % only used when make_speech_louder=true
speech_peak_target = 0.99;

%% ===================== B) Music v5 Precise HF Clean =====================
% Detect transient spikes in high-frequency bins vs local median, then attenuate.
hf_start_hz = 6000;
ratio_thresh = 3.0;
attenuation = 0.25;      % multiply detected spikes by this factor (0..1)
median_win_frames = 9;   % odd number; larger = more conservative

% Optional gentle lowpass to reduce ultra-high clink energy
apply_lowpass = false;
lowpass_hz = 12000;
lowpass_order = 6;

% STFT params
win_len = 2048;
hop_len = 512;

%% ===================== Path Setup =====================
this_file = mfilename('fullpath');
best_dir = fileparts(this_file);
root_dir = fileparts(best_dir);

window = blackman(win_len, 'periodic');

%% ===================== Run A) Speech =====================
if run_speech_postprocess
    in_speech = fullfile(root_dir, 'speech_v12_ultra.wav');
    out_soft  = fullfile(root_dir, 'speech_v12_ultra_10pct_softer.wav');
    out_loud  = fullfile(root_dir, 'speech_v12_ultra_10pct_softer_LOUD.wav');

    if ~isfile(in_speech)
        error('Input file not found: %s (run cancel_music_ultra_v12.m first)', in_speech);
    end

    [x, fs] = audioread(in_speech);

    x_soft = soft_factor * x;
    audiowrite(out_soft, x_soft, fs);
    fprintf('Wrote: %s (x%.3f)\n', out_soft, soft_factor);

    if make_speech_louder
        gain = 10^(speech_gain_db/20);
        y = x_soft * gain;

        peak = max(abs(y(:)));
        if peak > speech_peak_target
            y = y * (speech_peak_target / (peak + eps));
            fprintf('Speech peak limiting: %.4f -> %.4f\n', peak, speech_peak_target);
        end

        audiowrite(out_loud, y, fs);
        fprintf('Wrote: %s (gain %+g dB)\n', out_loud, speech_gain_db);
    end
end

%% ===================== Run B) Music =====================
if run_music_hfclean
    in_music  = fullfile(root_dir, 'music_v5_precise.wav');
    out_music = fullfile(root_dir, 'music_v5_precise_hfclean.wav');

    if ~isfile(in_music)
        error('Input file not found: %s (run filter_audio_v5_precise.m first)', in_music);
    end

    [m, fs_m] = audioread(in_music);

    if apply_lowpass
        Wn = min(lowpass_hz/(fs_m/2), 0.999);
        [b, a] = butter(lowpass_order, Wn, 'low');
        m = filtfilt(b, a, m);
    end

    [m_clean, stats] = process_all_channels(m, fs_m, window, win_len, hop_len, hf_start_hz, ratio_thresh, attenuation, median_win_frames);

    peak = max(abs(m_clean(:)));
    if peak > 0.99
        m_clean = m_clean * (0.99 / (peak + eps));
    end

    audiowrite(out_music, m_clean, fs_m);
    fprintf('Wrote: %s\n', out_music);
    fprintf('Suppressed spikes (approx): %d time-freq bins\n', stats.total_suppressed);
end

%% ===================== Helpers =====================
function [y, stats] = process_all_channels(x, fs, window, win_len, hop_len, hf_start_hz, ratio_thresh, attenuation, median_win_frames)
    if size(x, 2) == 1
        [y, stats] = process_one_channel(x, fs, window, win_len, hop_len, hf_start_hz, ratio_thresh, attenuation, median_win_frames);
    else
        y = zeros(size(x));
        stats.total_suppressed = 0;
        for ch = 1:size(x, 2)
            [y(:, ch), st] = process_one_channel(x(:, ch), fs, window, win_len, hop_len, hf_start_hz, ratio_thresh, attenuation, median_win_frames);
            stats.total_suppressed = stats.total_suppressed + st.total_suppressed;
        end
    end
end

function [y, stats] = process_one_channel(x, fs, window, win_len, hop_len, hf_start_hz, ratio_thresh, attenuation, median_win_frames)
    [Sx, f_bins, ~] = spectrogram(x, window, win_len-hop_len, win_len, fs);
    mag = abs(Sx);

    hf_mask = (f_bins >= hf_start_hz);

    % Robust local median over time for each frequency bin
    mag_med = movmedian(mag, median_win_frames, 2);

    % Spike detection only in HF region
    spike = false(size(mag));
    spike(hf_mask, :) = mag(hf_mask, :) > (ratio_thresh .* (mag_med(hf_mask, :) + eps));

    gain = ones(size(mag), 'like', mag);
    gain(spike) = attenuation;

    S_clean = Sx .* gain;

    y_full = overlap_add_istft(S_clean, win_len, hop_len);
    y = trim_pad(y_full, length(x));

    stats.total_suppressed = nnz(spike);
end

function recon = overlap_add_istft(S, win_len, hop_len)
    [nfreq, ntime] = size(S);
    nfft = (nfreq - 1) * 2;
    sig_len = (ntime - 1) * hop_len + win_len;
    recon = zeros(sig_len, 1);
    window = blackman(win_len, 'periodic');
    for frame = 1:ntime
        X = S(:, frame);
        X = [X; conj(X(end-1:-1:2))];
        x_frame = real(ifft(X, nfft));
        x_frame = x_frame(1:win_len) .* window;
        start_idx = (frame - 1) * hop_len + 1;
        recon(start_idx:start_idx+win_len-1) = recon(start_idx:start_idx+win_len-1) + x_frame;
    end
end

function out = trim_pad(in, target_len)
    if length(in) > target_len
        out = in(1:target_len);
    else
        out = zeros(target_len, 1);
        out(1:length(in)) = in;
    end
end
