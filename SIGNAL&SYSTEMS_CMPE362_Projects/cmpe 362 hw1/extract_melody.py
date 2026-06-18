import librosa
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from scipy import signal
from scipy.ndimage import label, center_of_mass

# Load audio file
audio_file = 'complex.wav'
y, sr = librosa.load(audio_file, sr=None)

print(f"Loaded {audio_file}")
print(f"Sample rate: {sr} Hz")
print(f"Duration: {len(y) / sr:.2f} seconds")

# Compute STFT (Short-Time Fourier Transform)
D = librosa.stft(y)
S_db = librosa.power_to_db(np.abs(D) ** 2, ref=np.max)

# Create time and frequency axes
times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sr)
freqs = librosa.fft_frequencies(sr=sr, n_fft=2 * (D.shape[0] - 1))

# Plot original spectrogram
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# Plot 1: Full spectrogram
img = axes[0].pcolormesh(times, freqs, S_db, shading='auto', cmap='jet')
axes[0].set_ylabel('Frequency (Hz)')
axes[0].set_title('Full Spectrogram')
axes[0].set_ylim([0, 2000])
plt.colorbar(img, ax=axes[0])

# Extract dominant frequencies (peaks) over time
print("\n=== Extracting Dominant Frequencies ===\n")

# For each time frame, find the frequency with maximum energy
dominant_freqs = []
times_frames = []

for i in range(S_db.shape[1]):
    frame = S_db[:, i]
    
    # Find peaks (high-intensity frequencies)
    peaks, properties = signal.find_peaks(frame, height=-20, distance=5)
    
    if len(peaks) > 0:
        # Get the peak with highest magnitude
        peak_idx = peaks[np.argmax(frame[peaks])]
        freq = freqs[peak_idx]
        dominant_freqs.append(freq)
        times_frames.append(times[i])

# Plot 2: Spectrogram with extracted frequencies overlaid
axes[1].pcolormesh(times, freqs, S_db, shading='auto', cmap='jet')
axes[1].plot(times_frames, dominant_freqs, 'r-', linewidth=2, label='Extracted Fundamental')
axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Frequency (Hz)')
axes[1].set_title('Spectrogram with Extracted Fundamental Frequencies')
axes[1].set_ylim([0, 2000])
axes[1].legend()
axes[1].set_ylim([0, 2000])

plt.tight_layout()
plt.savefig('extracted_melody_plot.png', dpi=150, bbox_inches='tight')
print("Saved extracted_melody_plot.png")
# plt.show()  # Commented out for batch mode

# Smooth and group frequencies into discrete notes
print("\n=== Grouping into Discrete Notes ===\n")

# Smooth the frequency curve
from scipy.ndimage import median_filter
smoothed_freqs = median_filter(dominant_freqs, size=5)

# Group consecutive similar frequencies
notes = []
current_freq = None
current_start = 0
threshold = 20  # Hz threshold for grouping

for i, freq in enumerate(smoothed_freqs):
    if current_freq is None:
        current_freq = freq
        current_start = times_frames[i]
    elif abs(freq - current_freq) > threshold:
        # Note ended, save it
        duration = times_frames[i - 1] - current_start
        notes.append({
            'frequency': current_freq,
            'start_time': current_start,
            'duration': duration
        })
        current_freq = freq
        current_start = times_frames[i]

# Add the last note
if current_freq is not None:
    duration = times_frames[-1] - current_start
    notes.append({
        'frequency': current_freq,
        'start_time': current_start,
        'duration': duration
    })

# Print identified notes
print(f"Found {len(notes)} notes:\n")
print("Note | Frequency (Hz) | Duration (s) | Musical Note (approx)")
print("-" * 70)

# Musical note reference
def freq_to_note(freq):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    # A4 = 440 Hz
    h = 12 * np.log2(freq / 440.0)
    octave = int(4 + np.round(h / 12))
    note_idx = int(np.round(h % 12)) % 12
    return f"{note_names[note_idx]}{octave}"

for i, note in enumerate(notes):
    freq = note['frequency']
    duration = note['duration']
    note_name = freq_to_note(freq)
    print(f"{i+1:3d}  | {freq:13.1f} | {duration:12.3f} | {note_name}")

# Export as MATLAB-compatible format
print("\n=== MATLAB Code to Paste into helper.m ===\n")
print("frequencies = [", end="")
print(", ".join([f"{note['frequency']:.0f}" for note in notes]), end="")
print("];")
print("durations = [", end="")
print(", ".join([f"{note['duration']:.3f}" for note in notes]), end="")
print("];")

# Save to a text file for easy copying
with open('extracted_frequencies.txt', 'w') as f:
    f.write("=== Extracted Melody Parameters ===\n\n")
    f.write("Number of notes: " + str(len(notes)) + "\n\n")
    f.write("MATLAB Format:\n")
    f.write("frequencies = [" + ", ".join([f"{note['frequency']:.0f}" for note in notes]) + "];\n")
    f.write("durations = [" + ", ".join([f"{note['duration']:.3f}" for note in notes]) + "];\n\n")
    f.write("Detailed breakdown:\n")
    f.write("Note | Frequency (Hz) | Duration (s) | Musical Note\n")
    f.write("-" * 70 + "\n")
    for i, note in enumerate(notes):
        freq = note['frequency']
        duration = note['duration']
        note_name = freq_to_note(freq)
        f.write(f"{i+1:3d}  | {freq:13.1f} | {duration:12.3f} | {note_name}\n")

print("\nSaved extracted_frequencies.txt")
print("\nDone! Use the frequencies and durations above in helper.m")
