% analyze_perfect.m
% Analyzes the perfect separation files to design optimal FIR filters

clear; close all; clc;

[x, fs] = audioread('cafe_sample.wav');
[v, fs_v] = audioread('website_vocals.wav');
[m, fs_m] = audioread('website_music.wav');

% Ensure same length and mono
x = mean(x, 2);
v = mean(v, 2);
m = mean(m, 2);
mindur = min([length(x), length(v), length(m)]);
x = x(1:mindur);
v = v(1:mindur);
m = m(1:mindur);

% Compute Power Spectral Density (Welch's method)
nfft = 4096;
[Pxx, f] = pwelch(x, hann(nfft), nfft/2, nfft, fs);
[Pvv, ~] = pwelch(v, hann(nfft), nfft/2, nfft, fs);
[Pmm, ~] = pwelch(m, hann(nfft), nfft/2, nfft, fs);

% Compute ideal Wiener filter amplitude response
% H_vocals(f) = Pvv / (Pvv + Pmm)
% H_music(f)  = Pmm / (Pvv + Pmm)
H_voc = Pvv ./ (Pvv + Pmm + 1e-12);
H_mus = Pmm ./ (Pvv + Pmm + 1e-12);

% Smooth the responses
kernel = ones(50,1)/50;
H_voc_sm = filtfilt(kernel, 1, H_voc);
H_mus_sm = filtfilt(kernel, 1, H_mus);

% Design FIR filters from these ideal responses
N_order = 1000;
f_norm = f / (fs/2);
f_norm(end) = 1; % ensure ends at Nyquist exactly

b_voc = fir2(N_order, f_norm, H_voc_sm);
b_mus = fir2(N_order, f_norm, H_mus_sm);

% Apply filters to original
speech_filt = filtfilt(b_voc, 1, x);
music_filt = filtfilt(b_mus, 1, x);

audiowrite('speech_v4.wav', speech_filt / max(abs(speech_filt)), fs);
audiowrite('music_v4.wav', music_filt / max(abs(music_filt)), fs);

disp('Wrote ideal FIR output to speech_v4.wav and music_v4.wav');

figure;
plot(f, H_voc_sm, 'r', 'LineWidth', 1.5); hold on;
plot(f, H_mus_sm, 'b', 'LineWidth', 1.5);
xlim([0, 5000]); title('Ideal FIR Filter Responses derived from perfect audio');
legend('Speech Filter', 'Music Filter');
xlabel('Hz'); ylabel('Magnitude');
saveas(gcf, 'ideal_fir_responses.png');
