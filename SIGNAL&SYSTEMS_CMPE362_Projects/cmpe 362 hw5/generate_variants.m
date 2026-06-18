% generate_variants.m
% Author: Ali Ayhan Günder
% Date: 2026-06-05
% Create 10 different voice-processing variants for each extracted channel
% Output files: channel{n}_v{01..10}_{label}.wav
% This script applies 10 audio effects to each input file to generate processed versions

clear; clc;  % Clear workspace and command window

% List of input audio files to process
files = {'channel1.wav','channel2.wav','channel3.wav'};

% Define the 10 audio effects to apply to each file
% Each effect will create a different output file
labels = { 'agc', 'softlim', 'compress_mild', 'compress_strong', 'bass_boost', 'treble_boost', 'telephone', 'pitch_up', 'pitch_down', 'reverb' };

% Check that we have exactly 10 effects
assert(numel(labels)==10,'Expect 10 variants');

% Process each audio file
for fi = 1:numel(files)
    fname = files{fi};
    
    % Check if the file exists, skip if not found
    if ~isfile(fname)
        warning('Missing %s, skipping.', fname);
        continue;
    end
    
    % Read the audio file and get the sample rate
    [x, Fs] = audioread(fname);
    
    % Convert stereo to mono by taking the average of all channels
    if size(x,2)>1, x = mean(x,2); end
    
    % Make sure the signal is a column vector
    x = x(:);

    % Apply each of the 10 effects to create 10 variants
    for vi = 1:10
        label = labels{vi};  % Get the name of the current effect
        y = x;  % Copy original signal to process it
        
        % Process the signal based on the effect type
        switch label
            % AGC: Automatic Gain Control - makes the signal louder or quieter to reach a target level
            case 'agc'
                % Set the desired loudness level (RMS value)
                target_rms = 0.07;
                % Calculate current loudness of the signal
                cur_rms = sqrt(mean(y.^2));
                % Calculate how much to multiply the signal to reach target loudness
                scale = target_rms/(cur_rms + eps);  % eps prevents division by zero
                % Apply the scaling to adjust loudness
                y = y * scale;

            % Soft Limiting: Limits loud peaks smoothly without hard clipping
            case 'softlim'
                % Normalize the signal to the range [-1, 1]
                if max(abs(y))>0, y = y / max(abs(y)); end
                % Apply soft limiting using tanh function (smooth clipping)
                y = tanh(3 * y);
                % Normalize output to safe level (0.95 prevents clipping)
                y = y / max(abs(y)+eps) * 0.95;

            % Mild Compression: Gently reduces loud parts of the signal
            case 'compress_mild'
                % Threshold: start compressing when signal exceeds 0.09
                % Ratio: reduce peaks by factor of 3 (3:1 ratio)
                th = 0.09; ratio = 3;
                y = simple_compressor(y, th, ratio);

            % Strong Compression: Reduces loud parts more aggressively
            case 'compress_strong'
                % Threshold: start compressing when signal exceeds 0.02
                % Ratio: reduce peaks by factor of 10 (10:1 ratio)
                th = 0.02; ratio = 10;
                y = simple_compressor(y, th, ratio);

            % Bass Boost: Emphasizes low frequencies (deep sounds)
            case 'bass_boost'
                % Create a filter to extract low frequencies (below 200 Hz)
                [b,a] = butter(4, 200/(Fs/2), 'low');
                % Extract the low-frequency part
                low = filtfilt(b,a,y);
                % Add the boosted low frequencies back to the original signal
                y = y + 0.7 * low;
                % Normalize to prevent clipping
                y = y / max(abs(y)+eps) * 0.95;

            % Treble Boost: Emphasizes high frequencies (bright sounds)
            case 'treble_boost'
                % Create a filter to extract high frequencies (above 3000 Hz)
                [b,a] = butter(4, 3000/(Fs/2), 'high');
                % Extract the high-frequency part
                hi = filtfilt(b,a,y);
                % Add the boosted high frequencies back to the original signal
                y = y + 0.7 * hi;
                % Normalize to prevent clipping
                y = y / max(abs(y)+eps) * 0.95;

            % Telephone Effect: Simulates low-quality telephone audio
            case 'telephone'
                % Reduce sample rate to 8000 Hz (telephone quality)
                y8 = resample(y, 8000, Fs);
                % Create bandpass filter for frequencies 300-3400 Hz (telephone range)
                [bb,aa] = butter(4, [300 3400]/(8000/2), 'bandpass');
                % Apply the filter to keep only telephone-band frequencies
                y8 = filtfilt(bb,aa,y8);
                % Restore original sample rate
                y = resample(y8, Fs, 8000);
                % Normalize to prevent clipping
                y = y / max(abs(y)+eps) * 0.95;

            % Pitch Up: Raises the pitch by playing audio faster
            case 'pitch_up'
                % Resample to increase speed: 53/50 = 1.06 (about 1 semitone higher)
                p = 53; q = 50;  % Numerator and denominator for resampling ratio
                y = resample(y, p, q);

            % Pitch Down: Lowers the pitch by playing audio slower
            case 'pitch_down'
                % Resample to decrease speed: 47/50 = 0.94 (about 1 semitone lower)
                p = 47; q = 50;  % Numerator and denominator for resampling ratio
                y = resample(y, p, q);

            % Reverb: Adds echo and space effect to make audio sound like a room
            case 'reverb'
                % Set reverb decay time in seconds
                rt = 0.35;  % seconds
                % Calculate how many samples the reverb lasts
                L = round(rt * Fs);
                % Create a decaying impulse response (each repeat gets quieter)
                h = (0.01) * (0.9 .^ (0:L-1));
                % Apply reverb by convolving with the impulse response
                y = conv(y, h, 'same');
                % Normalize to prevent clipping
                y = y / max(abs(y)+eps) * 0.95;

            otherwise
                % passthrough
        end

        % Clean up the processed signal
        % Replace any NaN values with silence (0)
        if any(isnan(y)), y(isnan(y))=0; end
        
        % Final normalization to ensure safe audio levels
        if max(abs(y))>0
            y = y / max(abs(y)) * 0.95;
        end

        % Create output filename with channel number, variant number, and effect name
        outname = sprintf('channel%d_v%02d_%s.wav', fi, vi, label);
        % Save the processed audio to a file
        audiowrite(outname, y, Fs);
        % Print message to confirm the file was saved
        fprintf('Wrote %s (len=%d samples)\n', outname, length(y));
    end
end

%% Helper Functions
%% SIMPLE_COMPRESSOR: Reduces loud parts of the audio signal
% Inputs:
%   x: audio signal
%   th: threshold level - only compress when signal exceeds this value
%   ratio: compression ratio - how much to reduce peaks (e.g., 3:1 ratio)
% Output:
%   y: compressed audio signal

function y = simple_compressor(x, th, ratio)
    % Start with the original signal
    y = x;
    
    % Get the absolute value (magnitude) of each sample
    a = abs(x);
    
    % Find which samples are above the threshold and need compression
    above = a > th;
    
    % Apply compression formula to samples above threshold:
    % new_value = sign(original) * (threshold + (magnitude - threshold) / ratio)
    % This reduces the peak while preserving the sign (positive/negative)
    y(above) = sign(x(above)).*( th + (a(above)-th)/ratio );
    
    % Normalize the output to safe level
    if max(abs(y))>0
        y = y / max(abs(y)) * 0.95;
    end
end
