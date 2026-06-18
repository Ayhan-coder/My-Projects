"""
Synthesize complex_recreate.wav based on spectrogram analysis.
4 bursts with harmonic comb filter effect at ~1.2s intervals.
"""
import numpy as np
from scipy.io import wavfile

# Global parameters
SR = 48000
DURATION = 6.0
samples = int(SR * DURATION)
output = np.zeros(samples, dtype=np.float64)

# ADSR envelope (in seconds)
ATTACK = 0.010
DECAY = 0.200
SUSTAIN_LEVEL = 0.3
SUSTAIN_TIME = 0.100
RELEASE = 0.050
TOTAL_ENV = ATTACK + DECAY + SUSTAIN_TIME + RELEASE  # 0.36s

def make_adsr(duration_s):
    """Create ADSR envelope."""
    n = int(duration_s * SR)
    env = np.zeros(n)
    a = int(ATTACK * SR)
    d = int(DECAY * SR)
    s = int(SUSTAIN_TIME * SR)
    r = int(RELEASE * SR)
    
    idx = 0
    # Attack: 0 -> 1
    end = min(idx + a, n)
    env[idx:end] = np.linspace(0, 1, end - idx)
    idx = end
    # Decay: 1 -> sustain level
    end = min(idx + d, n)
    env[idx:end] = np.linspace(1, SUSTAIN_LEVEL, end - idx)
    idx = end
    # Sustain
    end = min(idx + s, n)
    env[idx:end] = SUSTAIN_LEVEL
    idx = end
    # Release: sustain -> 0
    end = min(idx + r, n)
    env[idx:end] = np.linspace(SUSTAIN_LEVEL, 0, end - idx)
    
    return env

def make_burst():
    """
    Create a single burst using additive synthesis of the harmonic bands
    plus a noise component, simulating the comb filter effect.
    """
    dur = TOTAL_ENV
    n = int(dur * SR)
    t = np.arange(n) / SR
    signal = np.zeros(n)
    
    # Hot points: freq (Hz), amplitude (dB), bandwidth (Hz)
    hot_points = [
        (150,   20,  300),
        (2500,  15,  400),
        (5000,  12,  400),
        (7500,   8,  500),
        (10000,  0,  500),
        (12500, -10, 600),
    ]
    
    # Reference level: 20 dB is max
    ref_db = 20.0
    
    for freq, amp_db, bw in hot_points:
        # Convert dB to linear amplitude (relative)
        amp = 10 ** ((amp_db - ref_db) / 20.0)
        
        if freq < 500:
            # Low end: square wave + noise for that "solid block" character
            # Square wave (odd harmonics up to ~500 Hz)
            for h in range(1, 8, 2):  # 1, 3, 5, 7
                f_h = freq * h
                if f_h > 500:
                    break
                signal += amp * (1.0 / h) * np.sin(2 * np.pi * f_h * t + np.random.uniform(0, 2*np.pi))
            
            # Add band-limited noise around fundamental
            noise = np.random.randn(n) * 0.3 * amp
            # Simple bandpass via modulation
            noise *= np.sin(2 * np.pi * freq * t)
            signal += noise
        else:
            # Higher harmonics: sine with slight noise to give texture
            signal += amp * np.sin(2 * np.pi * freq * t + np.random.uniform(0, 2*np.pi))
            # Add narrow-band noise for bandwidth
            noise = np.random.randn(n) * 0.15 * amp
            noise *= np.sin(2 * np.pi * freq * t)
            signal += noise
    
    # Apply comb filter for extra resonance (delay = 0.4ms = 1/2500 Hz)
    delay_samples = int(0.0004 * SR)  # ~19 samples
    feedback = 0.4
    filtered = np.copy(signal)
    for i in range(delay_samples, n):
        filtered[i] += feedback * filtered[i - delay_samples]
    
    # Apply ADSR envelope
    env = make_adsr(dur)
    filtered *= env
    
    return filtered

# Event timing (onset times)
events = [
    {"onset": 0.75, "peak": 0.95, "decay_end": 1.20},
    {"onset": 1.95, "peak": 2.15, "decay_end": 2.40},
    {"onset": 3.15, "peak": 3.35, "decay_end": 3.60},
    {"onset": 4.35, "peak": 4.55, "decay_end": 4.80},
]

# Generate and place each burst
for event in events:
    burst = make_burst()
    start_sample = int(event["onset"] * SR)
    end_sample = start_sample + len(burst)
    
    if end_sample > samples:
        burst = burst[:samples - start_sample]
        end_sample = samples
    
    output[start_sample:end_sample] += burst

# Normalize to prevent clipping
peak = np.max(np.abs(output))
if peak > 0:
    output = output / peak * 0.85

# Convert to 16-bit PCM
output_16 = np.int16(output * 32767)

# Save
wavfile.write("complex_recreate.wav", SR, output_16)

print(f"Created complex_recreate.wav")
print(f"  Sample rate: {SR} Hz")
print(f"  Duration: {DURATION} s")
print(f"  Samples: {len(output_16)}")
print(f"  4 bursts at t = {[e['onset'] for e in events]} s")
