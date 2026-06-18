import librosa
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal

# Load audio file
audio_file = 'complex.wav'
y, sr = librosa.load(audio_file, sr=None)

print(f"Loaded {audio_file}")
print(f"Sample rate: {sr} Hz")
print(f"Duration: {len(y) / sr:.2f} seconds")

# Use librosa's pitch detection (pyin - more robust)
print("\nExtracting pitch using librosa's built-in method...")

# Compute constant-Q transform for better pitch resolution
D = librosa.stft(y)
S_db = librosa.power_to_db(np.abs(D) ** 2, ref=np.max)

# Use spectral centroid and other features
times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sr)
freqs = librosa.fft_frequencies(sr=sr, n_fft=2 * (D.shape[0] - 1))

# Better approach: Extract pitch contour
print("Computing pitch contour with filtering...")

# Get magnitude spectrogram
mag_spec = np.abs(D)

# For each frame, find the peak frequency (fundamental)
fundamental_freqs = []
times_list = []
energies = []

for i in range(S_db.shape[1]):
    frame = S_db[:, i]
    energy = np.sum(mag_spec[:, i] ** 2)
    
    if energy > 0.001:  # Only process frames with sufficient energy
        # Find the strongest peak
        peak_idx = np.argmax(frame)
        freq = freqs[peak_idx]
        
        # Only include if frequency is reasonable (40-2000 Hz for voice/whistle)
        if 40 < freq < 2000:
            fundamental_freqs.append(freq)
            times_list.append(times[i])
            energies.append(energy)

fundamental_freqs = np.array(fundamental_freqs)
times_list = np.array(times_list)
energies = np.array(energies)

print(f"Found {len(fundamental_freqs)} frames with valid pitch")

# Smooth the frequency contour
from scipy.ndimage import median_filter
if len(fundamental_freqs) > 1:
    smoothed_freqs = median_filter(fundamental_freqs, size=11)
else:
    smoothed_freqs = fundamental_freqs

# Group consecutive similar frequencies into notes
# A note is a stable frequency for at least 100ms
notes = []
current_freq = None
current_start_idx = 0
freq_tolerance = 30  # Hz
min_duration = 0.1  # seconds
min_frames = int(min_duration * (sr / 512))  # ~4 frames at 512 hop

i = 0
while i < len(smoothed_freqs):
    if current_freq is None:
        current_freq = smoothed_freqs[i]
        current_start_idx = i
    
    # Check if frequency is similar (within tolerance)
    if abs(smoothed_freqs[i] - current_freq) > freq_tolerance:
        # Frequency changed - save the note if long enough
        note_length = i - current_start_idx
        if note_length >= min_frames:
            duration = times_list[i - 1] - times_list[current_start_idx]
            avg_freq = np.mean(smoothed_freqs[current_start_idx:i])
            notes.append({
                'frequency': avg_freq,
                'start_time': times_list[current_start_idx],
                'duration': duration,
                'num_frames': note_length
            })
        
        current_freq = smoothed_freqs[i]
        current_start_idx = i
    
    i += 1

# Add last note
if current_freq is not None:
    note_length = len(smoothed_freqs) - current_start_idx
    if note_length >= min_frames:
        duration = times_list[-1] - times_list[current_start_idx]
        avg_freq = np.mean(smoothed_freqs[current_start_idx:])
        notes.append({
            'frequency': avg_freq,
            'start_time': times_list[current_start_idx],
            'duration': duration,
            'num_frames': note_length
        })

# Sort by start time
notes = sorted(notes, key=lambda x: x['start_time'])

# Merge very close notes that might be the same
merged_notes = []
for note in notes:
    if merged_notes and abs(note['frequency'] - merged_notes[-1]['frequency']) < 20 and \
       (note['start_time'] - (merged_notes[-1]['start_time'] + merged_notes[-1]['duration'])) < 0.1:
        # Merge with previous note
        merged_notes[-1]['duration'] += note['duration']
    else:
        merged_notes.append(note)

notes = merged_notes

# Print identified notes
print(f"\nFound {len(notes)} melodic notes:\n")
print("Note | Frequency (Hz) | Duration (s) | Musical Note")
print("-" * 65)

def freq_to_note(freq):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    h = 12 * np.log2(freq / 440.0)
    octave = int(4 + np.round(h / 12))
    note_idx = int(np.round(h % 12)) % 12
    return f"{note_names[note_idx]}{octave}"

for i, note in enumerate(notes):
    freq = note['frequency']
    duration = note['duration']
    note_name = freq_to_note(freq)
    print(f"{i+1:3d}  | {freq:13.1f} | {duration:12.3f} | {note_name}")

# Generate MATLAB code
print("\n=== MATLAB Code to Paste into helper.m ===\n")
print("frequencies = [", end="")
print(", ".join([f"{note['frequency']:.0f}" for note in notes]), end="")
print("];")
print("durations = [", end="")
print(", ".join([f"{note['duration']:.3f}" for note in notes]), end="")
print("];")

# Save to file
with open('extracted_frequencies_cleaned.txt', 'w') as f:
    f.write("=== Cleaned Melody Parameters ===\n\n")
    f.write(f"Number of notes: {len(notes)}\n\n")
    f.write("MATLAB Format:\n")
    f.write("frequencies = [" + ", ".join([f"{note['frequency']:.0f}" for note in notes]) + "];\n")
    f.write("durations = [" + ", ".join([f"{note['duration']:.3f}" for note in notes]) + "];\n\n")
    f.write("Detailed breakdown:\n")
    f.write("Note | Frequency (Hz) | Duration (s) | Musical Note\n")
    f.write("-" * 65 + "\n")
    for i, note in enumerate(notes):
        freq = note['frequency']
        duration = note['duration']
        note_name = freq_to_note(freq)
        f.write(f"{i+1:3d}  | {freq:13.1f} | {duration:12.3f} | {note_name}\n")

print("\nSaved extracted_frequencies_cleaned.txt")

# Plot comparison
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# Full spectrogram
img1 = axes[0].pcolormesh(times, freqs, S_db, shading='auto', cmap='jet')
axes[0].set_ylabel('Frequency (Hz)')
axes[0].set_title('Original Spectrogram')
axes[0].set_ylim([0, 2000])
plt.colorbar(img1, ax=axes[0])

# Spectrogram with detected notes
axes[1].pcolormesh(times, freqs, S_db, shading='auto', cmap='jet')
for note in notes:
    rect_start = note['start_time']
    rect_end = note['start_time'] + note['duration']
    freq = note['frequency']
    axes[1].hlines(freq, rect_start, rect_end, colors='lime', linewidth=3, label='Detected' if note == notes[0] else '')

axes[1].set_xlabel('Time (s)')
axes[1].set_ylabel('Frequency (Hz)')
axes[1].set_title('Detected Melodic Notes')
axes[1].set_ylim([0, 2000])

plt.tight_layout()
plt.savefig('cleaned_melody_detection.png', dpi=150, bbox_inches='tight')
print("Saved cleaned_melody_detection.png")

print("\nDone! Copy the frequencies and durations to helper.m and run it.")
