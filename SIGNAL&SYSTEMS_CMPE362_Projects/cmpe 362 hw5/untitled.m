clc; clear; close all;

b = [2 2];
a = [1 -0.8];

figure;
zplane(b,a);
grid on;
title('Pole-Zero Plot of H(z)');