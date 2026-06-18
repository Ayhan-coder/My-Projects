"""
Analyze complex.wav to extract accurate pitch segments for recreation.
Uses librosa's pyin for robust pitch tracking of speech.
"""
import librosa
import numpy as np
import matplotlib.pyplot as plt

# Load audio
y, sr = librosa.load(r"complex.wav", sr=None)
print(f"Sample rate: {sr}, Duration: {len(y)/sr:.3f}s")

# Use pyin for pitch tracking (good for speech)
f0, voiced_flag, voiced_probs = librosa.pyin(
    y, fmin=50, fmax=500, sr=sr, frame_length=2048, hop_length=256
)
times = librosa.times_like(f0, sr=sr, hop_length=256)

# Replace NaN with 0 for unvoiced
f0_clean = np.copy(f0)
f0_clean[np.isnan(f0_clean)] = 0

# Plot the pitch contour
fig, axes = plt.subplots(2, 1, figsize=(14, 8))

# Waveform
axes[0].plot(np.arange(len(y)) / sr, y, alpha=0.6)
axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("Amplitude")
axes[0].set_title("Waveform")

# Pitch contour
axes[1].plot(times, f0_clean, 'b.', markersize=2)
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Frequency (Hz)")
axes[1].set_title("Pitch Contour (pyin)")
axes[1].set_ylim(0, 500)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("pitch_contour.png", dpi=150)
plt.close()

# --- Segment the pitch into stable regions ---
# Group consecutive voiced frames into segments
segments = []
in_segment = False
seg_start = 0
seg_freqs = []

MIN_DURATION = 0.03  # minimum 30ms segment

for i in range(len(f0_clean)):
    if f0_clean[i] > 0:
        if not in_segment:
            seg_start = i
            seg_freqs = []
            in_segment = True
        seg_freqs.append(f0_clean[i])
    else:
        if in_segment:
            duration = (i - seg_start) * 256 / sr
            if duration >= MIN_DURATION:
                median_f = np.median(seg_freqs)
                segments.append({
                    'start_time': seg_start * 256 / sr,
                    'end_time': i * 256 / sr,
                    'duration': duration,
                    'freq': median_f,
                    'start_idx': seg_start,
                    'end_idx': i
                })
            in_segment = False

# Handle last segment
if in_segment:
    duration = (len(f0_clean) - seg_start) * 256 / sr
    if duration >= MIN_DURATION:
        median_f = np.median(seg_freqs)
        segments.append({
            'start_time': seg_start * 256 / sr,
            'end_time': len(f0_clean) * 256 / sr,
            'duration': duration,
            'freq': median_f,
            'start_idx': seg_start,
            'end_idx': len(f0_clean)
        })

# Now further split segments where pitch changes significantly
refined_segments = []
PITCH_CHANGE_THRESHOLD = 20  # Hz

for seg in segments:
    start = seg['start_idx']
    end = seg['end_idx']
    freqs = f0_clean[start:end]
    
    # Find split points where pitch jumps
    sub_start = 0
    sub_freqs = [freqs[0]]
    
    for j in range(1, len(freqs)):
        if abs(freqs[j] - np.median(sub_freqs)) > PITCH_CHANGE_THRESHOLD:
            # Split here
            dur = (j - sub_start) * 256 / sr
            if dur >= MIN_DURATION:
                refined_segments.append({
                    'start_time': (start + sub_start) * 256 / sr,
                    'duration': dur,
                    'freq': np.median(sub_freqs)
                })
            sub_start = j
            sub_freqs = [freqs[j]]
        else:
            sub_freqs.append(freqs[j])
    
    # Last sub-segment
    dur = (len(freqs) - sub_start) * 256 / sr
    if dur >= MIN_DURATION:
        refined_segments.append({
            'start_time': (start + sub_start) * 256 / sr,
            'duration': dur,
            'freq': np.median(sub_freqs)
        })

# Include silences between segments
full_sequence = []
prev_end = 0.0

for seg in refined_segments:
    gap = seg['start_time'] - prev_end
    if gap > 0.01:  # silence gap > 10ms
        full_sequence.append({'freq': 0, 'duration': gap, 'type': 'silence'})
    full_sequence.append({'freq': seg['freq'], 'duration': seg['duration'], 'type': 'voiced'})
    prev_end = seg['start_time'] + seg['duration']

# Add trailing silence if any
total_dur = len(y) / sr
if prev_end < total_dur:
    full_sequence.append({'freq': 0, 'duration': total_dur - prev_end, 'type': 'silence'})

print(f"\nFound {len(refined_segments)} voiced segments, {len(full_sequence)} total (with silences)")
print(f"\n{'#':>3}  {'Type':>8}  {'Freq (Hz)':>10}  {'Duration (s)':>12}  {'Start (s)':>10}")
print("-" * 55)
running_time = 0
for i, s in enumerate(full_sequence):
    print(f"{i+1:3d}  {s['type']:>8}  {s['freq']:10.1f}  {s['duration']:12.4f}  {running_time:10.3f}")
    running_time += s['duration']

# Output as MATLAB arrays
voiced_freqs = [s['freq'] for s in full_sequence]
voiced_durs = [s['duration'] for s in full_sequence]

print("\n\n% --- MATLAB arrays (copy to helper.m) ---")
print(f"frequencies = [{', '.join(f'{f:.1f}' for f in voiced_freqs)}];")
print(f"durations = [{', '.join(f'{d:.4f}' for d in voiced_durs)}];")
print(f"% Total duration: {sum(voiced_durs):.3f}s (original: {total_dur:.3f}s)")
