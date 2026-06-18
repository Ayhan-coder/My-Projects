%% CMPE362 HW5 - DSBAM (DSB-SC) Multi-Channel Demodulation
% Author: Ali Ayhan Günder
% Date: 2026-06-05
% Given: modulated.wav containing 3 DSB-SC AM channels.
% Each channel's message is bandlimited to |f| <= 3 kHz before modulation.
%
% Goal:
%   1) Estimate the 3 carrier frequencies.
%   2) Coherently demodulate each channel (multiply by cos(2*pi*fc*t)).
%   3) Low-pass filter to ~3 kHz and save the recovered audio as .wav.
%
% Outputs created in the current folder:
%   - channel1.wav, channel2.wav, channel3.wav
%   - spectrum_with_carriers.png
%   - extracted_channels_waveforms.png

clear; clc; close all;

% If running headless (e.g., matlab -batch), don't try to display figures.
if ~usejava('desktop')
	set(0, 'DefaultFigureVisible', 'off');
end

%% Parameters
% Input WAV (by default, expected next to this script). If you keep the
% file elsewhere, you can set filename to an absolute/relative path.
filename = 'modulated.wav';
numChannels = 3;

messageBW_Hz = 3000;          % message bandwidth (given in the homework)
lpfCutoff_Hz = 2800;          % slightly tighter than 3 kHz to reduce adjacent-channel bleed (set back to 3000 if you want max bandwidth)
bandGuard_Hz = 0;             % extra guard for bandpass during demod (Hz). Keep 0 when channels are tightly spaced.

% Filter tuning (helps reduce adjacent-channel bleed when carriers are close)
filterRp_dB = 0.2;            % passband ripple (dB) for elliptic filters
filterRs_dB = 80;             % stopband attenuation (dB) for elliptic filters
bpStopMargin_Hz = 50;         % margin to keep BP stopbands inside the inter-channel guard (Hz)
lpfStopMargin_Hz = 100;       % margin to keep LPF stopband before nearest interferer (Hz)
lpfTransitionTarget_Hz = 600; % preferred LPF transition width if spacing allows (Hz)

% Carrier refinement (DSB-SC has no carrier line; refine by sideband symmetry)
enableCarrierSymmetryRefine = true;
carrierRefineRange_Hz = 250;  % search range around initial fc (Hz)

% Optional audio denoising (post-demod). Uses STFT/ISTFT (Signal Processing Toolbox).
enableDenoise = true;
denoiseWinLen = 2048;
denoiseOverlapLen = 1536;
denoiseFftLen = 2048;
denoiseNoisePercentile = 10;  % lower = more aggressive noise estimate
denoiseBeta = 1.0;            % larger = more noise reduction
denoiseGainFloor = 0.05;      % prevent over-suppression (musical noise)

% If auto-detection misses a channel, try reducing this value.
peakSeparation_Hz = max(1000, 2*messageBW_Hz - 1000);

% Optional manual override (uncomment + fill to bypass auto carrier detection)
% manualCarriers_Hz = [4359 11338 16338];
manualCarriers_Hz = [];

psdWindowSeconds = 0.20;      % Welch window length (seconds)
psdOverlapFrac = 0.50;        % 50% overlap

outWavPattern = 'channel%d.wav';

%% Load modulated signal
scriptDir = fileparts(mfilename('fullpath'));

% Resolve filename robustly (MATLAB's current folder may differ from the
% script's folder when you run it from the editor).
if isfile(filename)
	inputPath = filename;
elseif isfile(fullfile(scriptDir, filename))
	inputPath = fullfile(scriptDir, filename);
else
	% Try recursive search under the project folder for the expected name.
	hits = dir(fullfile(scriptDir, '**', filename));
	hits = hits(~[hits.isdir]);
	if numel(hits) == 1
		inputPath = fullfile(hits(1).folder, hits(1).name);
	elseif numel(hits) > 1
		error('Found multiple files named %s under %s. Please set filename to the correct path.', filename, scriptDir);
	else
		% As a last resort, prompt for a WAV file (desktop only).
		if usejava('desktop')
			[fPick, pPick] = uigetfile({'*.wav','WAV files (*.wav)'}, 'Select modulated.wav');
			if isequal(fPick, 0)
				error('Input WAV not selected. Place %s next to this script or set filename to its path.', filename);
			end
			inputPath = fullfile(pPick, fPick);
		else
			error('File not found: %s (looked in current folder and under %s). Place it next to this script or set filename to its path.', filename, scriptDir);
		end
	end
end

[y, Fs] = audioread(inputPath);
if size(y,2) > 1
	y = mean(y,2);
end
y = y(:);
y = y - mean(y);              % remove DC

N = length(y);
t = (0:N-1)'/Fs;

fprintf('Loaded %s | Fs = %d Hz | Duration = %.2f s\n', filename, Fs, N/Fs);

%% PSD (Welch)
[f, pxx] = compute_psd_welch(y, Fs, psdWindowSeconds, psdOverlapFrac);
pxxDb = 10*log10(pxx + eps);

%% Estimate carrier frequencies of the 3 channels
if ~isempty(manualCarriers_Hz)
	if numel(manualCarriers_Hz) ~= numChannels
		error('manualCarriers_Hz must have exactly %d values.', numChannels);
	end
	fc = sort(manualCarriers_Hz(:));
else
	fc = estimate_carriers_from_psd(f, pxx, numChannels, messageBW_Hz, peakSeparation_Hz);
end

if enableCarrierSymmetryRefine
	fcRefined = refine_carriers_by_psd_symmetry(f, pxx, fc, messageBW_Hz, carrierRefineRange_Hz);
	fprintf('\nCarrier refinement (PSD symmetry):\n');
	for k = 1:numChannels
		fprintf('  Ch %d: %.2f Hz  ->  %.2f Hz  (%.2f Hz)\n', k, fc(k), fcRefined(k), fcRefined(k)-fc(k));
	end
	fc = fcRefined;
end

fprintf('\nEstimated carrier frequencies (Hz):\n');
for k = 1:numChannels
	fprintf('  Channel %d: fc = %.2f Hz\n', k, fc(k));
end

%% Plot PSD with detected carrier bands (useful for slides)
figure('Name','PSD + Detected Carriers');
plot(f, pxxDb, 'b'); grid on; hold on;
xlabel('Frequency (Hz)');
ylabel('PSD (dB/Hz)');
title('modulated.wav PSD (Welch) with detected carrier bands');
xlim([0 Fs/2]);

for k = 1:numChannels
	xline(fc(k), 'r', 'LineWidth', 1.2);
	xline(fc(k) - messageBW_Hz, 'r--');
	xline(fc(k) + messageBW_Hz, 'r--');
end

saveas(gcf, 'spectrum_with_carriers.png');

%% Demodulate each channel using the reference repo style
% Coherent multiplication followed by an ideal frequency-domain LPF.
channels = zeros(N, numChannels);
for k = 1:numChannels
	lo = cos(2*pi*fc(k)*t);
	xMix = 2 * y .* lo;

	% Keep only the message band, just like the repo's fftshift -> zero -> ifftshift flow.
	xHat = ideal_lowpass_fft(xMix, Fs, lpfCutoff_Hz);

	% Remove residual DC and normalize for listening.
	xHat = xHat - mean(xHat);
	peak = max(abs(xHat));
	if peak > 0
		xHat = xHat / peak * 0.95;
	end
	channels(:,k) = xHat;

	outName = sprintf(outWavPattern, k);
	audiowrite(outName, xHat, Fs);
	fprintf('Wrote %s\n', outName);
end

%% Plot extracted channel waveforms (required in slides)
figure('Name','Extracted Channels (Waveforms)');
for k = 1:numChannels
	subplot(numChannels,1,k);
	plot(t, channels(:,k));
	grid on;
	xlim([0 t(end)]);
	ylabel(sprintf('Ch %d', k));
	if k == 1
		title('Extracted audio waveforms');
	end
	if k == numChannels
		xlabel('Time (s)');
	end
end
saveas(gcf, 'extracted_channels_waveforms.png');

fprintf('\nDone. Play channel1.wav / channel2.wav / channel3.wav to hear the songs.\n');

%% --- Local functions ----------------------------------------------------
function [f, pxx] = compute_psd_welch(y, Fs, winSeconds, overlapFrac)
	N = length(y);

	winLen = max(1024, round(winSeconds * Fs));
	winLen = min(winLen, N);
	if mod(winLen,2) == 1
		winLen = winLen - 1;
	end
	if winLen < 8
		error('Signal too short for PSD.');
	end

	noverlap = round(overlapFrac * winLen);

	% Hann window (explicit formula keeps the script self-contained)
	n = (0:winLen-1)';
	w = 0.5 - 0.5*cos(2*pi*n/(winLen-1));

	% Cap NFFT for speed, but keep it >= window length
	nfft = 2^nextpow2(min(N, 2^18));
	nfft = max(nfft, 2^nextpow2(winLen));

	[pxx, f] = pwelch(y, w, noverlap, nfft, Fs, 'onesided');
end

function fc = estimate_carriers_from_psd(f, pxx, numChannels, messageBW_Hz, minSep_Hz)
	df = mean(diff(f));

	% Sliding-window integrated power over a 2*BW band.
	% Peaks of this curve are good estimates of the carrier centers.
	bandBins = max(3, round((2*messageBW_Hz)/df));
	kernel = ones(bandBins, 1);
	bandPower = conv(pxx, kernel, 'same');
	bandPowerDb = 10*log10(bandPower + eps);

	minDistBins = max(1, round(minSep_Hz/df));
	[~, locs] = findpeaks(bandPowerDb, 'MinPeakDistance', minDistBins, 'SortStr', 'descend');

	% Discard peaks too close to DC or Nyquist (band would clip)
	validMask = f > (messageBW_Hz + 100) & f < (max(f) - (messageBW_Hz + 100));
	locs = locs(validMask(locs));

	% If findpeaks misses channels (e.g., channels are closer than expected),
	% fall back to greedy selection on the sliding band-power curve.
	if numel(locs) < numChannels
		warning('findpeaks detected %d/%d channels; using greedy selection instead.', numel(locs), numChannels);
		bp = bandPower;
		bp(~validMask) = 0;

		locsGreedy = zeros(numChannels,1);
		bpWork = bp;
		for k = 1:numChannels
			[maxVal, i] = max(bpWork);
			if maxVal <= 0
				error('Carrier auto-detection failed. Try lowering peakSeparation_Hz or set manualCarriers_Hz.');
			end
			locsGreedy(k) = i;
			lo = max(1, i - minDistBins);
			hi = min(length(bpWork), i + minDistBins);
			bpWork(lo:hi) = 0;
		end
		locs = locsGreedy;
	else
		locs = locs(1:numChannels);
	end

	fcRough = f(locs);

	% Refine each carrier by PSD centroid inside +/- BW
	fc = zeros(numChannels,1);
	for k = 1:numChannels
		idx = f >= (fcRough(k) - messageBW_Hz) & f <= (fcRough(k) + messageBW_Hz);
		fc(k) = sum(f(idx).*pxx(idx)) / (sum(pxx(idx)) + eps);
	end

	fc = sort(fc(:));
end

function fcRefined = refine_carriers_by_psd_symmetry(f, pxx, fcInit, messageBW_Hz, searchRange_Hz)
	% For DSB-SC, the PSD within a channel should be approximately symmetric
	% around the true carrier center. Refine each initial estimate by choosing
	% the center frequency that minimizes left/right mismatch inside +/-BW.
	%
	% This is a *PSD-only* refinement (fast) and is typically more reliable
	% than snapping to any single PSD peak (since the carrier is suppressed).
	df = mean(diff(f));
	m = max(3, round(messageBW_Hz/df));
	searchBins = max(1, round(searchRange_Hz/df));

	fcRefined = fcInit(:);
	for k = 1:numel(fcInit)
		i0 = round(fcInit(k)/df) + 1;
		bestErr = inf;
		bestI = i0;
		for ii = (i0 - searchBins):(i0 + searchBins)
			if ii - m < 2 || ii + m > (numel(pxx) - 1)
				continue;
			end
			left = pxx(ii-m:ii-1);
			right = pxx(ii+1:ii+m);
			err = sum((left - flipud(right)).^2);
			if err < bestErr
				bestErr = err;
				bestI = ii;
			end
		end
		fcRefined(k) = f(bestI);
	end

	fcRefined = sort(fcRefined(:));
end

function yOut = ideal_lowpass_fft(yIn, Fs, cutoff_Hz)
	% Repo-style ideal low-pass filter implemented in the frequency domain.
	Nloc = length(yIn);
	Y = fftshift(fft(yIn));
	fvec = linspace(-Fs/2, Fs/2, Nloc).';
	Y(abs(fvec) > cutoff_Hz) = 0;
	yOut = real(ifft(ifftshift(Y)));
end