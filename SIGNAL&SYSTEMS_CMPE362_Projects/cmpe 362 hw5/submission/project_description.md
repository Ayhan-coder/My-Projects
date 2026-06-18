# CMPE 362 HW5 Project Description

## Title Page

**Project:** Demodulation of Three DSB-SC Radio Channels  
**Course:** CMPE 362 HW5  
**Name:** Your Name Here  
**Student ID:** Your Student ID Here

## Waveforms of Extracted Radio Channels

The project produced three recovered audio files after demodulation:

- `channel1.wav`
- `channel2.wav`
- `channel3.wav`

Each waveform shows the time-domain audio recovered from one radio channel after carrier estimation, coherent demodulation, and low-pass filtering.

## Carrier Frequencies and Channel Information

The three carrier frequencies were estimated as:

- **Channel 1:** approximately **3.50 kHz**
- **Channel 2:** approximately **10.00 kHz**
- **Channel 3:** approximately **16.50 kHz**

### Relevant Information

- The input signal `modulated.wav` contains three DSB-SC AM channels.
- Each message signal is bandlimited to about **3 kHz** before modulation.
- Because this is **DSB-SC**, the carrier is suppressed, so the carrier frequency must be estimated from the sidebands rather than a visible carrier tone.
- The recovered channels were saved as separate WAV files after demodulation.

## Approach Used to Find the Carrier Frequencies

1. **Computed the power spectral density (PSD)** of the received signal using **Welch's method**.
2. **Identified strong energy regions** in the PSD that correspond to the three modulated channels.
3. **Estimated rough carrier locations** by finding peaks in a sliding band-power curve.
4. **Refined the carrier estimates** using PSD symmetry, since DSB-SC sidebands should be approximately symmetric around the true carrier frequency.
5. **Used the final carrier estimates** for coherent demodulation.

## Demodulation Method

For each channel:

1. Multiply the received signal by a cosine at the estimated carrier frequency.
2. Shift the desired message band back to baseband.
3. Apply a low-pass filter to keep only the audio message.
4. Normalize the output and save it as a WAV file.

## Figures to Include

If needed, include these figures in the slides:

- PSD of `modulated.wav` with the detected carrier bands marked
- Waveform of `channel1.wav`
- Waveform of `channel2.wav`
- Waveform of `channel3.wav`

## Summary

This project successfully separated three DSB-SC radio channels from a single composite signal by estimating the carrier frequencies from the spectrum, performing coherent demodulation, and filtering out unwanted frequencies to recover the audio for each channel.
