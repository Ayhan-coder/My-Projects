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

hop_length = 512
n_fft = 2048
D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
S_db = librosa.power_to_db(np.abs(D) ** 2, ref=np.max)
mag_spec = np.abs(D)

times = librosa.frames_to_time(np.arange(S_db.shape[1]), sr=sr, hop_length=hop_length)
freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

print("\n=== EXTRACTING FUNDAMENTAL FREQUENCIES (Cepstral Method) ===\n")

# Use cepstral analysis - better for finding fundamentals
def estimate_fundamental_cepstral(frame_mag, sr, n_fft, min_freq=80, max_freq=2000):
    """Estimate fundamental using cepstral analysis"""
    
    # Log magnitude spectrum
    spec_db = 20 * np.log10(frame_mag + 1e-8)
    
    # Compute cepstrum
    cepstrum = np.fft.irfft(spec_db)
    
    # Convert to quefrency axis (inverse frequency)
    min_quefrency = int(sr / max_freq)
    max_quefrency = int(sr / min_freq)
    
    if max_quefrency >= len(cepstrum):
        max_quefrency = len(cepstrum) - 1
    
    if min_quefrency < max_quefrency and max_quefrency > min_quefrency:
        valid_cepstrum = cepstrum[min_quefrency:max_quefrency]
        quefrency_idx = np.argmax(valid_cepstrum)
        quefrency = quefrency_idx + min_quefrency
        
        if quefrency > 0:
            freq = sr / quefrency
            strength = cepstrum[quefrency] / (np.max(cepstrum) + 1e-8)
            return freq, strength
    
    return None, 0

# Extract fundamental for each frame
fundamental_freqs = []
strengths = []
times_list = []

print("Processing frames with cepstral analysis...")
for i in range(S_db.shape[1]):
    frame = mag_spec[:, i]
    energy = np.sum(frame ** 2)
    
    # Process frames with good energy (lowered threshold)
    if energy > np.percentile(np.sum(mag_spec ** 2, axis=0), 5):
        freq, strength = estimate_fundamental_cepstral(frame, sr, n_fft, min_freq=100, max_freq=800)
        
        if freq is not None and 100 < freq < 800 and strength > 0.1:
            fundamental_freqs.append(freq)
            strengths.append(strength)
            times_list.append(times[i])

if len(fundamental_freqs) == 0:
    print("Cepstral method found no values. Trying spectral centroid-based approach...")
    
    # Alternative: use spectral centroid weighted by magnitude
    for i in range(S_db.shape[1]):
        frame = mag_spec[:, i]
        energy = np.sum(frame ** 2)
        
        if energy > np.percentile(np.sum(mag_spec ** 2, axis=0), 5):
            # Find local peaks in lower frequency range (100-800 Hz)
            freq_range_idx = np.where((freqs >= 100) & (freqs <= 800))[0]
            if len(freq_range_idx) > 0:
                frame_subset = frame[freq_range_idx]
                
                # Find the strongest peak
                peak_idx = np.argmax(frame_subset)
                peak_freq = freqs[freq_range_idx[peak_idx]]
                peak_mag = frame_subset[peak_idx]
                
                if peak_mag > np.percentile(frame_subset, 50):
                    fundamental_freqs.append(peak_freq)
                    strengths.append(peak_mag / np.max(frame))
                    times_list.append(times[i])

fundamental_freqs = np.array(fundamental_freqs)
strengths = np.array(strengths)
times_list = np.array(times_list)

print(f"Extracted {len(fundamental_freqs)} frames with valid fundamental frequency")

# Apply strong smoothing
if len(fundamental_freqs) > 1:
    smoothed_freqs = median_filter(fundamental_freqs, size=25)
    # Additional constraint: remove outliers
    std_dev = np.std(smoothed_freqs)
    mean_freq = np.mean(smoothed_freqs)
    smoothed_freqs = np.clip(smoothed_freqs, mean_freq - 2*std_dev, mean_freq + 2*std_dev)
else:
    smoothed_freqs = fundamental_freqs

# Group into notes
notes = []
current_freq = None
current_start_idx = 0
freq_tolerance = 50  # Hz
min_duration = 0.12  # seconds minimum note duration
min_frames = int(min_duration * sr / hop_length)

print(f"\nGrouping frames into notes (min duration: {min_duration}s, freq tolerance: {freq_tolerance} Hz)...\n")

i = 0
while i < len(smoothed_freqs):
    if current_freq is None:
        current_freq = smoothed_freqs[i]
        current_start_idx = i
    
    if i < len(smoothed_freqs) and abs(smoothed_freqs[i] - current_freq) > freq_tolerance:
        note_length = i - current_start_idx
        if note_length >= min_frames:
            duration = times_list[i - 1] - times_list[current_start_idx]
            avg_freq = np.median(smoothed_freqs[current_start_idx:i])
            notes.append({
                'frequency': avg_freq,
                'start_time': times_list[current_start_idx],
                'duration': duration,
                'strength': np.mean(strengths[current_start_idx:i])
            })
        
        current_freq = smoothed_freqs[i]
        current_start_idx = i
    
    i += 1

# Add last note
if current_freq is not None:
    note_length = len(smoothed_freqs) - current_start_idx
    if note_length >= min_frames:
        duration = times_list[-1] - times_list[current_start_idx]
        avg_freq = np.median(smoothed_freqs[current_start_idx:])
        notes.append({
            'frequency': avg_freq,
            'start_time': times_list[current_start_idx],
            'duration': duration,
            'strength': np.mean(strengths[current_start_idx:])
        })

notes = sorted(notes, key=lambda x: x['start_time'])

print(f"Found {len(notes)} discrete notes:\n")
print("Note | Frequency (Hz) | Duration (s) | Strength | Musical Note")
print("-" * 70)

def freq_to_note(freq):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    h = 12 * np.log2(freq / 440.0)
    octave = int(4 + np.round(h / 12))
    note_idx = int(np.round(h % 12)) % 12
    return f"{note_names[note_idx]}{octave}"

for i, note in enumerate(notes):
    freq = note['frequency']
    duration = note['duration']
    strength = note['strength']
    note_name = freq_to_note(freq)
    print(f"{i+1:3d}  | {freq:13.1f} | {duration:12.3f} | {strength:8.3f} | {note_name}")

print("\n=== MATLAB Code ===\n")
print("frequencies = [", end="")
print(", ".join([f"{note['frequency']:.0f}" for note in notes]), end="")
print("];")
print("durations = [", end="")
print(", ".join([f"{note['duration']:.3f}" for note in notes]), end="")
print("];")

# Save to file
with open('extracted_frequencies_best.txt', 'w') as f:
    f.write("=== BEST Melody Parameters ===\n\n")
    f.write(f"Number of notes: {len(notes)}\n")
    f.write(f"Total duration: {sum(n['duration'] for n in notes):.3f}s\n\n")
    f.write("MATLAB Format:\n")
    f.write("frequencies = [" + ", ".join([f"{note['frequency']:.0f}" for note in notes]) + "];\n")
    f.write("durations = [" + ", ".join([f"{note['duration']:.3f}" for note in notes]) + "];\n\n")
    f.write("Detailed breakdown:\n")
    f.write("Note | Frequency (Hz) | Duration (s) | Strength | Musical Note\n")
    f.write("-" * 70 + "\n")
    for i, note in enumerate(notes):
        freq = note['frequency']
        duration = note['duration']
        strength = note['strength']
        note_name = freq_to_note(freq)
        f.write(f"{i+1:3d}  | {freq:13.1f} | {duration:12.3f} | {strength:8.3f} | {note_name}\n")

print("\nSaved extracted_frequencies_best.txt")

# Visualization
fig, axes = plt.subplots(3, 1, figsize=(16, 12))

# Plot 1: Spectrogram focusing on 100-800 Hz range
img = axes[0].pcolormesh(times, freqs, S_db, shading='auto', cmap='jet')
axes[0].set_ylabel('Frequency (Hz)')
axes[0].set_title('Full Spectrogram')
axes[0].set_ylim([0, 2000])
plt.colorbar(img, ax=axes[0], label='dB')

# Plot 2: Fundamental frequency contour
axes[1].plot(times_list, fundamental_freqs, 'c.', markersize=2, alpha=0.5, label='Detected')
axes[1].plot(times_list, smoothed_freqs, 'r-', linewidth=2.5, label='Smoothed Fundamental')
axes[1].set_ylabel('Frequency (Hz)')
axes[1].set_title('Extracted Fundamental Frequency Contour')
axes[1].set_ylim([100, 800])
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Spectrogram with notes marked
axes[2].pcolormesh(times, freqs, S_db, shading='auto', cmap='jet')
for j, note in enumerate(notes):
    rect_start = note['start_time']
    rect_end = note['start_time'] + note['duration']
    freq = note['frequency']
    axes[2].hlines(freq, rect_start, rect_end, colors='lime', linewidth=5, label='Note' if j == 0 else '')
    mid_time = (rect_start + rect_end) / 2
    axes[2].text(mid_time, freq + 80, f"{j+1}", color='white', ha='center', fontsize=9, weight='bold',
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

axes[2].set_xlabel('Time (s)')
axes[2].set_ylabel('Frequency (Hz)')
axes[2].set_title('Detected Melodic Notes (Green Lines)')
axes[2].set_ylim([0, 2000])

plt.tight_layout()
plt.savefig('best_melody_detection.png', dpi=150, bbox_inches='tight')
print("Saved best_melody_detection.png")

print("\n✓ Copy the frequencies and durations above to helper.m")
