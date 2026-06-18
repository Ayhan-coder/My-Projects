import librosa
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal
from scipy.ndimage import median_filter

# Load audio file
audio_file = 'complex.wav'
y, sr = librosa.load(audio_file, sr=None)

print(f"Loaded {audio_file}")
print(f"Sample rate: {sr} Hz")
print(f"Duration: {len(y) / sr:.2f} seconds")

# Compute STFT with better parameters
hop_length = 512
n_fft = 2048
D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
S_db = librosa.power_to_db(np.abs(D) ** 2, ref=np.max)
mag_spec = np.abs(D)

times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sr, hop_length=hop_length)
freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

print("\n=== EXTRACTING FUNDAMENTAL FREQUENCIES (Filtering Harmonics) ===\n")

# Extract pitch using autocorrelation (more robust for fundamentals)
def estimate_fundamental(frame_mag, sr, n_fft, min_freq=80, max_freq=2000):
    """Estimate fundamental frequency using autocorrelation method"""
    
    # Apply Hann window
    frame = frame_mag * np.hanning(len(frame_mag))
    
    # Compute autocorrelation
    acf = np.correlate(frame, frame, mode='full')
    acf = acf[len(acf)//2:]
    acf = acf / acf[0]
    
    # Convert lag to frequency
    min_lag = int(sr / max_freq)
    max_lag = int(sr / min_freq)
    
    if max_lag >= len(acf):
        max_lag = len(acf) - 1
    
    # Find the peak in the valid range
    if min_lag < max_lag:
        valid_acf = acf[min_lag:max_lag]
        lag = np.argmax(valid_acf) + min_lag
        
        # Convert lag back to frequency
        if lag > 0:
            freq = sr / lag
            confidence = acf[lag]
            return freq, confidence
    
    return None, 0

# Extract fundamental for each frame
fundamental_freqs = []
confidence_scores = []
times_list = []

print("Processing frames...")
for i in range(S_db.shape[1]):
    frame = mag_spec[:, i]
    energy = np.sum(frame ** 2)
    
    # Only process frames with sufficient energy
    if energy > np.percentile(np.sum(mag_spec ** 2, axis=0), 20):
        freq, confidence = estimate_fundamental(frame, sr, n_fft)
        
        if freq is not None and 80 < freq < 2000 and confidence > 0.3:
            fundamental_freqs.append(freq)
            confidence_scores.append(confidence)
            times_list.append(times[i])

fundamental_freqs = np.array(fundamental_freqs)
confidence_scores = np.array(confidence_scores)
times_list = np.array(times_list)

print(f"Extracted {len(fundamental_freqs)} frames with valid fundamental frequency")

# Apply strong smoothing to get stable note frequencies
if len(fundamental_freqs) > 1:
    # Use median filter with larger window
    smoothed_freqs = median_filter(fundamental_freqs, size=31)
else:
    smoothed_freqs = fundamental_freqs

# Group into notes with higher thresholds
notes = []
current_freq = None
current_start_idx = 0
freq_tolerance = 40  # Hz - larger tolerance for stability
min_duration = 0.15  # seconds - minimum note length
min_frames = int(min_duration * sr / hop_length)

print(f"\nGrouping frames into notes (min duration: {min_duration}s)...")

i = 0
while i < len(smoothed_freqs):
    if current_freq is None:
        current_freq = smoothed_freqs[i]
        current_start_idx = i
    
    # Check if frequency is still in range
    if i < len(smoothed_freqs) and abs(smoothed_freqs[i] - current_freq) > freq_tolerance:
        # Frequency changed - save the note if long enough
        note_length = i - current_start_idx
        if note_length >= min_frames:
            duration = times_list[i - 1] - times_list[current_start_idx]
            avg_freq = np.mean(smoothed_freqs[current_start_idx:i])
            notes.append({
                'frequency': avg_freq,
                'start_time': times_list[current_start_idx],
                'duration': duration,
                'confidence': np.mean(confidence_scores[current_start_idx:i])
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
            'confidence': np.mean(confidence_scores[current_start_idx:])
        })

notes = sorted(notes, key=lambda x: x['start_time'])

# Print identified notes
print(f"\nFound {len(notes)} discrete notes:\n")
print("Note | Frequency (Hz) | Duration (s) | Confidence | Musical Note")
print("-" * 75)

def freq_to_note(freq):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    h = 12 * np.log2(freq / 440.0)
    octave = int(4 + np.round(h / 12))
    note_idx = int(np.round(h % 12)) % 12
    return f"{note_names[note_idx]}{octave}"

for i, note in enumerate(notes):
    freq = note['frequency']
    duration = note['duration']
    conf = note['confidence']
    note_name = freq_to_note(freq)
    print(f"{i+1:3d}  | {freq:13.1f} | {duration:12.3f} | {conf:10.3f} | {note_name}")

# Generate MATLAB code
print("\n=== MATLAB Code to Paste into helper.m ===\n")
print("frequencies = [", end="")
print(", ".join([f"{note['frequency']:.0f}" for note in notes]), end="")
print("];")
print("durations = [", end="")
print(", ".join([f"{note['duration']:.3f}" for note in notes]), end="")
print("];")

# Save to file
with open('extracted_frequencies_accurate.txt', 'w') as f:
    f.write("=== ACCURATE Melody Parameters (Fundamentals Only) ===\n\n")
    f.write(f"Number of notes: {len(notes)}\n")
    f.write(f"Total duration: {sum(n['duration'] for n in notes):.3f}s\n\n")
    f.write("MATLAB Format:\n")
    f.write("frequencies = [" + ", ".join([f"{note['frequency']:.0f}" for note in notes]) + "];\n")
    f.write("durations = [" + ", ".join([f"{note['duration']:.3f}" for note in notes]) + "];\n\n")
    f.write("Detailed breakdown:\n")
    f.write("Note | Frequency (Hz) | Duration (s) | Confidence | Musical Note\n")
    f.write("-" * 75 + "\n")
    for i, note in enumerate(notes):
        freq = note['frequency']
        duration = note['duration']
        conf = note['confidence']
        note_name = freq_to_note(freq)
        f.write(f"{i+1:3d}  | {freq:13.1f} | {duration:12.3f} | {conf:10.3f} | {note_name}\n")

print("\nSaved extracted_frequencies_accurate.txt")

# Plot results
fig, axes = plt.subplots(3, 1, figsize=(16, 12))

# Plot 1: Full spectrogram
img1 = axes[0].pcolormesh(times, freqs, S_db, shading='auto', cmap='jet')
axes[0].set_ylabel('Frequency (Hz)')
axes[0].set_title('Full Spectrogram (with Harmonics)')
axes[0].set_ylim([0, 2000])
plt.colorbar(img1, ax=axes[0], label='dB')

# Plot 2: Extracted fundamental frequency contour
axes[1].plot(times_list, fundamental_freqs, 'c-', linewidth=1, alpha=0.5, label='Raw Fundamental')
axes[1].plot(times_list, smoothed_freqs, 'r-', linewidth=2, label='Smoothed Fundamental')
axes[1].set_ylabel('Frequency (Hz)')
axes[1].set_title('Extracted Fundamental Frequency Contour')
axes[1].set_ylim([0, 2000])
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Spectrogram with detected notes marked
axes[2].pcolormesh(times, freqs, S_db, shading='auto', cmap='jet')
for j, note in enumerate(notes):
    rect_start = note['start_time']
    rect_end = note['start_time'] + note['duration']
    freq = note['frequency']
    axes[2].hlines(freq, rect_start, rect_end, colors='lime', linewidth=4)
    # Add note label
    mid_time = (rect_start + rect_end) / 2
    axes[2].text(mid_time, freq + 50, f"{j+1}", color='white', ha='center', fontsize=8, weight='bold')

axes[2].set_xlabel('Time (s)')
axes[2].set_ylabel('Frequency (Hz)')
axes[2].set_title('Detected Melodic Notes (Green Lines)')
axes[2].set_ylim([0, 2000])

plt.tight_layout()
plt.savefig('accurate_melody_detection.png', dpi=150, bbox_inches='tight')
print("Saved accurate_melody_detection.png")

print("\n✓ Done! Copy the frequencies and durations to helper.m")
