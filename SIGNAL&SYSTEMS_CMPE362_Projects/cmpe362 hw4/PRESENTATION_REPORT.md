# CMPE362 HW4 – Presentation Draft

## Slide 1 — Title Page
- **Project:** Audio Speech/Music Separation and Hidden Message Analysis
- **Course:** CMPE362 – Homework 4
- **Name:** [Your Name]
- **Student ID:** [Your Student ID]
- **Date:** 16 March 2026

---

## Slide 2 — Spectrograms (Part 1)
**Title suggestion:** Spectrogram Analysis of Input and Speech Output

- **Top/Left:** `cafe_sample.wav` (original mixture)
  - Image: `spectrogram_original.png`
- **Bottom/Right:** `speech_filtered.wav`
  - Image: `spectrogram_speech_filtered.png`

**What to say (short):**
- The original contains overlapping speech + music energy across most of the spectrum.
- In `speech_filtered.wav`, speech-dominant bands are attenuated and repeating/harmonic background becomes more dominant.

---

## Slide 3 — Spectrograms (Part 2)
**Title suggestion:** Spectrogram of Music-Removed / Speech-Preserved Output

- **Main figure:** `music_filtered.wav`
  - Image: `spectrogram_music_filtered.png`

**What to say (short):**
- `music_filtered.wav` preserves speech-relevant content more strongly.
- Mid-band speech intelligibility is improved compared to the original mixture.
- Some residual overlap remains, which is expected for single-channel blind separation.

---

## Slide 4 — Method Journey: How We Found the Best Result
**Title suggestion:** From Baseline Filters to Hybrid Separation

### Methods we tried
- Baseline classical filtering (bandpass/bandstop)
- STFT mask-based filtering (IRM/ratio-mask style)
- Tuned variants for balance/quality (`filter_audio_v5_precise.m`, `filter_audio_v7_balanced.m`, etc.)
- Alternative source-separation families (HPSS, NMF, ICA, k-means, DRNN experiments)

### What we learned during comparison
- Frequency-only filtering was fast but insufficient where speech/music overlap strongly.
- Some aggressive methods reduced music more, but introduced robotic/metallic speech artifacts.
- Some mild methods preserved naturalness, but left too much background music.

### Why we selected the final method
- Best practical result came from combining complementary ideas instead of relying on one method.
- Final choice: hybrid REPET + HPSS + NMF with Wiener soft-mask fusion and post-filtering.
- This gave the strongest overall tradeoff between intelligibility, suppression, and listening quality.

---

## Slide 5 — Filters, Frequency Targets, Reasoning, Process
**Selected best method:** Hybrid pipeline in `filter_opus_extreme.m`

### Filters/Methods used
- STFT time-frequency masking (window 2048, hop 512, Hann window)
- REPET (repeating pattern extraction)
- HPSS (harmonic/percussive median filtering)
- NMF (rank-30 decomposition)
- Wiener-style soft mask fusion of REPET + HPSS + NMF
- Post IIR filters for cleanup and clarity

### Frequency ranges targeted
- **Speech enhancement path**
  - Elliptic bandpass: **80–8000 Hz**
  - Presence boost (peaking): around **3 kHz**
- **Music/background path**
  - Notch filters: **500, 1500, 2500, 3500 Hz** (speech formant zones)
  - Bass enhancement: below **200 Hz**
  - Treble enhancement: above **6 kHz**
  - Final low-pass smoothing: around **14 kHz**

### Reasoning and process
- Music in cafe recordings is more repetitive/harmonic; speech is less periodic and more transient.
- A single filter was not enough, so multiple complementary masks were fused.
- Soft (Wiener) masks reduce hard artifacts versus binary masks.
- Final frequency-domain cleanup was used to improve audibility and suppress leakage.
- Goal was not perfect source separation, but the best practical tradeoff between suppression and intelligibility.

---

## Slide 6 — Bonus: Hidden Message Decoding
**Decoded message (best interpretation):** **I SEE YOU**

### Process summary
- Focused ultrasonic BFSK-style demodulation around **17.6 kHz**.
- Performed stability sweeps over:
  - Carrier: 17580–17620 Hz
  - Symbol timing: 0.155–0.190 s
  - Window sizes: 40/50/60/80 ms
- Cross-checked with additional methods (DTMF/Morse/LSB scans), but none gave a clearer phrase.
- Turkish interpretation from noisy pattern `L?ISME?O`: probable key/message is **GÜLÜMSE** (“Smile”).

### Confidence statement
- Confidence is **medium-high** (repeatable core pattern), but not absolute due to sensitivity to timing/demod parameters.

---

## Quick Presenter Notes (optional)
- “Instructor emphasized best effort over perfect filtering; this is our strongest result.”
- “The hybrid method gave the most stable perceptual improvement among tested approaches.”
- “Residual bleed is expected because this is single-channel source separation.”