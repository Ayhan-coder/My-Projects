import librosa
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter, label

# Load audio
y, sr = librosa.load('complex.wav', sr=None)

print(f"Loaded complex.wav at {sr} Hz")
print(f"Duration: {len(y) / sr:.2f}s\n")

# Compute STFT
hop_length = 512
n_fft = 2048
D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
mag_spec_full = np.abs(D)
S_db = librosa.power_to_db(mag_spec_full ** 2, ref=np.max)

times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sr, hop_length=hop_length)
freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

print("=== SPECTRAL PEAK DETECTION (100-800 Hz) ===\n")

# Focus on 100-800 Hz range
freq_mask = (freqs >= 100) & (freqs <= 800)
mag_spec = mag_spec_full[freq_mask, :]
freqs_range = freqs[freq_mask]

# Find peak frequencyfor each frame
peak_freqs = []
peak_mags = []
frame_times = []

print("Analyzing frames...")
for i in range(mag_spec.shape[1]):
    frame = mag_spec[:, i]
    energy = np.sum(frame ** 2)
    
    # Keep frames with reasonable energy
    if energy > 1e-6:
        peak_idx = np.argmax(frame)
        peak_freq = freqs_range[peak_idx]
        peak_mag = frame[peak_idx]
        
        peak_freqs.append(peak_freq)
        peak_mags.append(peak_mag)
        frame_times.append(times[i])

peak_freqs = np.array(peak_freqs)
peak_mags = np.array(peak_mags)
frame_times = np.array(frame_times)

print(f"Found {len(peak_freqs)} frames with peaks")

# Smooth the frequency contour
smoothed_freqs = median_filter(peak_freqs, size=21)

# Remove extreme outliers
q1 = np.percentile(smoothed_freqs, 25)
q3 = np.percentile(smoothed_freqs, 75)
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr
smoothed_freqs = np.clip(smoothed_freqs, max(100, lower), min(800, upper))

# Apply additional smoothing
smoothed_freqs = median_filter(smoothed_freqs, size=11)

# Segment into notes - group stable frequency regions
notes = []
current_freq = smoothed_freqs[0]
current_start = 0
freq_threshold = 40  # Hz

for i in range(1, len(smoothed_freqs)):
    # Check if frequency changed significantly
    if abs(smoothed_freqs[i] - current_freq) > freq_threshold:
        # Transition detected
        duration = frame_times[i-1] - frame_times[current_start]
        
        if duration >= 0.1:  # Minimum 100ms
            avg_freq = np.median(smoothed_freqs[current_start:i])
            notes.append({
                'frequency': avg_freq,
                'start_time': frame_times[current_start],
                'duration': duration
            })
        
        current_freq = smoothed_freqs[i]
        current_start = i

# Add final note
duration = frame_times[-1] - frame_times[current_start]
if duration >= 0.1:
    avg_freq = np.median(smoothed_freqs[current_start:])
    notes.append({
        'frequency': avg_freq,
        'start_time': frame_times[current_start],
        'duration': duration
    })

print(f"\n✓ Found {len(notes)} notes:\n")
print("Note | Frequency (Hz) | Duration (s) | Note Name")
print("-" * 60)

def freq_to_note(f):
    notes_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    h = 12 * np.log2(f / 440.0)
    octave = int(4 + np.round(h / 12))
    idx = int(np.round(h % 12)) % 12
    return f"{notes_list[idx]}{octave}"

for i, n in enumerate(notes):
    print(f"{i+1:3d}  | {n['frequency']:13.0f} | {n['duration']:12.3f} | {freq_to_note(n['frequency'])}")

print("\n" + "="*60)
print("MATLAB Code:")
print("="*60)
print("frequencies = [" + ", ".join([f"{n['frequency']:.0f}" for n in notes]) + "];")
print("durations = [" + ", ".join([f"{n['duration']:.3f}" for n in notes]) + "];")

# Save
with open('extracted_frequencies_final.txt', 'w') as f:
    f.write("=== Final Melody Extraction ===\n\n")
    f.write("frequencies = [" + ", ".join([f"{n['frequency']:.0f}" for n in notes]) + "];\n")
    f.write("durations = [" + ", ".join([f"{n['duration']:.3f}" for n in notes]) + "];\n\n")
    f.write("Details:\n")
    f.write("Note | Frequency (Hz) | Duration (s)\n")
    for i, n in enumerate(notes):
        f.write(f"{i+1:3d}  | {n['frequency']:13.0f} | {n['duration']:12.3f}\n")

print("\nSaved extracted_frequencies_final.txt")

# Visualization
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# Spectrogram
freq_mask_plot = (freqs >= 0) & (freqs <= 1500)
img = axes[0].pcolormesh(times, freqs[freq_mask_plot], S_db[freq_mask_plot, :], 
                          shading='auto', cmap='jet')
axes[0].set_ylabel('Frequency (Hz)')
axes[0].set_title('Spectrogram of complex.wav')
axes[0].set_ylim([0, 1500])
plt.colorbar(img, ax=axes[0], label='dB')

# Overlay detected notes
for i, n in enumerate(notes):
    t1 = n['start_time']
    t2 = t1 + n['duration']
    f = n['frequency']
    axes[0].plot([t1, t2], [f, f], 'lime', linewidth=4, marker='o')
    axes[0].text((t1 + t2) / 2, f + 60, f"{i+1}", color='white', fontsize=10, 
                weight='bold', ha='center', bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))

# Frequency contour
axes[1].plot(frame_times, peak_freqs, 'c-', linewidth=1, alpha=0.4, label='Raw')
axes[1].plot(frame_times, smoothed_freqs, 'r-', linewidth=2.5, label='Smoothed')
for i, n in enumerate(notes):
    t1 = n['start_time']
    t2 = t1 + n['duration']
    axes[1].axvspan(t1, t2, alpha=0.2, color=f'C{i}')
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Frequency (Hz)')
axes[1].set_title('Extracted Fundamental Frequency')
axes[1].set_ylim([100, 800])
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('final_melody_detection.png', dpi=150, bbox_inches='tight')
print("Saved final_melody_detection.png\n")
