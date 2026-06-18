function varargout = spectrogram(x, window, noverlap, nfft, fs, varargin)
    % Polyfill for MATLAB's inbuilt spectrogram function
    % Used when Signal Processing Toolbox is not installed.
    
    if isscalar(window)
        winLen = window;
        win = 0.54 - 0.46 * cos(2 * pi * (0:winLen-1)' / (winLen-1)); % Hamming
    else
        winLen = length(window);
        win = window;
    end
    
    step = winLen - noverlap;
    numFrames = floor((length(x) - winLen) / step) + 1;
    
    s = zeros(nfft/2+1, numFrames);
    for i = 1:numFrames
        startIdx = (i-1)*step + 1;
        segment = x(startIdx : startIdx + winLen - 1) .* win;
        fft_seg = fft(segment, nfft);
        s(:, i) = fft_seg(1:nfft/2+1);
    end
    
    f = (0:nfft/2) * fs / nfft;
    t = (0:numFrames-1) * step / fs;
    
    if nargout == 0
        imagesc(t, f, 10*log10(abs(s).^2 + eps));
        axis xy;
        xlabel('Time (s)');
        ylabel('Frequency (Hz)');
        colorbar;
    else
        varargout{1} = s;
        varargout{2} = f;
        varargout{3} = t;
    end
end