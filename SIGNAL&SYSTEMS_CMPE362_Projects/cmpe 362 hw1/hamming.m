function w = hamming(L)
    % Polyfill for MATLAB's inbuilt hamming function
    w = 0.54 - 0.46 * cos(2 * pi * (0:L-1)' / (L-1));
end