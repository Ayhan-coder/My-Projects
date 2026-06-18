% draw_spectrogram.m
% Draw a spectrogram with your mouse and synthesize audio.
%
% HOW TO USE:
%   Left-click + drag  : Paint energy
%   Right-click + drag : Erase
%   Press ENTER        : Synthesize and save drawn_audio.wav
%
% Run with:  run('draw_spectrogram.m')

clear; close all;

%% --- Parameters ---
fs       = 48000;
duration = 4.0;
fmax     = 8000;
nfft     = 1024;
hop      = 256;
brush_r  = 4;

n_frames = floor((duration * fs - nfft) / hop) + 1;
n_freqs  = nfft / 2 + 1;
fmax_bin = min(round(fmax / (fs/2) * (n_freqs-1)) + 1, n_freqs);

time_axis = (0:n_frames-1) * hop / fs;
freq_axis = linspace(0, fmax/1000, fmax_bin);   % kHz

canvas = zeros(fmax_bin, n_frames);

%% --- Figure setup ---
fig = figure('Name','Draw Spectrogram | LClick=Paint  RClick=Erase  Enter=Synth', ...
             'NumberTitle','off','Color','k','Units','normalized',...
             'Position',[0.05 0.1 0.85 0.75]);

ax = axes('Parent',fig,'Color','k','Position',[0.08 0.12 0.86 0.78]);
img = imagesc(ax, time_axis, freq_axis, canvas);
axis(ax,'xy');
colormap(ax, hot);
clim(ax,[0 1]);
xlim(ax,[time_axis(1) time_axis(end)]);
ylim(ax,[freq_axis(1) freq_axis(end)]);
xlabel(ax,'Time (s)','Color','w','FontSize',12);
ylabel(ax,'Frequency (kHz)','Color','w','FontSize',12);
title(ax,'Left-drag = Paint  |  Right-drag = Erase  |  ENTER = Synthesize','Color','w','FontSize',11);
ax.XColor='w'; ax.YColor='w';
cb = colorbar(ax); cb.Color='w';

%% --- Store all state in figure appdata ---
setappdata(fig,'canvas',  canvas);
setappdata(fig,'drawing', false);
setappdata(fig,'erasing', false);
setappdata(fig,'img',     img);
setappdata(fig,'ax',      ax);
setappdata(fig,'n_frames',n_frames);
setappdata(fig,'fmax_bin',fmax_bin);
setappdata(fig,'brush_r', brush_r);
setappdata(fig,'duration',duration);
setappdata(fig,'fmax',    fmax);
setappdata(fig,'fs',      fs);
setappdata(fig,'nfft',    nfft);
setappdata(fig,'hop',     hop);

%% --- Attach callbacks ---
set(fig,'WindowButtonDownFcn',   @cb_down);
set(fig,'WindowButtonUpFcn',     @cb_up);
set(fig,'WindowButtonMotionFcn', @cb_move);
set(fig,'KeyPressFcn',           @cb_key);

disp('=== SPECTROGRAM PAINTER READY ===');
disp('Left-click + drag  : Paint');
disp('Right-click + drag : Erase');
disp('Press ENTER        : Synthesize -> drawn_audio.wav');

%% =========================================================
%% LOCAL FUNCTIONS  (use setappdata/getappdata for state)
%% =========================================================

function cb_down(fig, ~)
    if strcmp(get(fig,'SelectionType'),'normal')
        setappdata(fig,'drawing',true);
        setappdata(fig,'erasing',false);
    else
        setappdata(fig,'drawing',false);
        setappdata(fig,'erasing',true);
    end
    do_paint(fig);
end

function cb_up(fig, ~)
    setappdata(fig,'drawing',false);
    setappdata(fig,'erasing',false);
end

function cb_move(fig, ~)
    if ~getappdata(fig,'drawing') && ~getappdata(fig,'erasing')
        return;
    end
    do_paint(fig);
end

function do_paint(fig)
    ax       = getappdata(fig,'ax');
    canvas   = getappdata(fig,'canvas');
    img      = getappdata(fig,'img');
    n_frames = getappdata(fig,'n_frames');
    fmax_bin = getappdata(fig,'fmax_bin');
    brush_r  = getappdata(fig,'brush_r');
    duration = getappdata(fig,'duration');
    fmax     = getappdata(fig,'fmax');
    drawing  = getappdata(fig,'drawing');
    erasing  = getappdata(fig,'erasing');

    pt = get(ax,'CurrentPoint');
    t  = pt(1,1);          % seconds
    f  = pt(1,2) * 1000;   % Hz (axis was in kHz)

    % Map to canvas pixel indices
    t_idx = round((t / duration) * n_frames);
    f_idx = round((f / fmax) * fmax_bin);
    t_idx = max(1, min(n_frames, t_idx));
    f_idx = max(1, min(fmax_bin, f_idx));

    % Paint with circular soft brush
    for ti = max(1,t_idx-brush_r):min(n_frames,t_idx+brush_r)
        for fi = max(1,f_idx-brush_r):min(fmax_bin,f_idx+brush_r)
            d = sqrt((ti-t_idx)^2 + (fi-f_idx)^2);
            if d <= brush_r
                w = (1 - d/brush_r) * 0.6;
                if drawing
                    canvas(fi,ti) = min(1, canvas(fi,ti) + w);
                elseif erasing
                    canvas(fi,ti) = max(0, canvas(fi,ti) - w);
                end
            end
        end
    end

    setappdata(fig,'canvas',canvas);
    set(img,'CData',canvas);
    drawnow limitrate;
end

function cb_key(fig, evt)
    if strcmp(evt.Key,'return')
        do_synthesize(fig);
    end
end

function do_synthesize(fig)
    canvas = getappdata(fig,'canvas');
    fs     = getappdata(fig,'fs');
    nfft   = getappdata(fig,'nfft');
    hop    = getappdata(fig,'hop');

    n_frames = size(canvas,2);
    fmax_bin = size(canvas,1);

    disp('Synthesizing...');

    % Build full STFT magnitude (mirror for real signal)
    full_mag = zeros(nfft, n_frames);
    full_mag(1:fmax_bin, :) = canvas;
    full_mag(nfft/2+2:end,:) = flipud(full_mag(2:nfft/2,:));

    % Random phase
    phase = exp(1j * 2*pi * rand(nfft, n_frames));
    S = full_mag .* phase;

    % Overlap-add inverse STFT
    win = hann(nfft);
    total_samples = (n_frames-1)*hop + nfft;
    audio   = zeros(total_samples,1);
    win_sum = zeros(total_samples,1);

    for fr = 1:n_frames
        frame = real(ifft(S(:,fr)));
        idx   = (fr-1)*hop + (1:nfft);
        audio(idx)   = audio(idx)   + frame .* win;
        win_sum(idx) = win_sum(idx) + win.^2;
    end

    win_sum(win_sum < 1e-8) = 1;
    audio = audio ./ win_sum;

    % Trim edges and normalize
    trim  = nfft/2;
    audio = audio(trim+1:end-trim);
    peak  = max(abs(audio));
    if peak > 0
        audio = audio / peak * 0.85;
    end

    audiowrite('drawn_audio.wav', audio, fs);
    fprintf('Saved drawn_audio.wav  (%.2f sec)\n', length(audio)/fs);
    sound(audio, fs);
    disp('Playing...');
end
