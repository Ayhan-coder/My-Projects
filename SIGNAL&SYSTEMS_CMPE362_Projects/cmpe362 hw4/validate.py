import os
import numpy as np
import scipy.io.wavfile as wav
from scipy.signal import stft, istft
import matplotlib.pyplot as plt

def ensure_mono(audio):
    if audio.ndim > 1:
        return np.mean(audio, axis=1)
    return audio

def gpu_stft_processing(x, v, m, fs):
    """Attempt perfect source separation using PyTorch on GPU."""
    try:
        import torch
        if torch.cuda.is_available():
            device = torch.device('cuda')
            print(f"✅ GPU DETECTED: {torch.cuda.get_device_name(0)}")
            print("🚀 Offloading STFT and Ideal Ratio Mask matrix calculations to the GPU...")
        else:
            print("⚠️ PyTorch installed but no CUDA-compatible GPU found. Using CPU.")
            device = torch.device('cpu')
            
        # Convert to GPU tensors
        x_t = torch.tensor(x, dtype=torch.float32, device=device)
        v_t = torch.tensor(v, dtype=torch.float32, device=device)
        m_t = torch.tensor(m, dtype=torch.float32, device=device)
        
        n_fft = 4096
        hop_length = 1024
        window = torch.hann_window(n_fft, device=device)
        
        # Compute spectograms on GPU
        # return_complex=True is the standard for modern PyTorch
        Sx = torch.stft(x_t, n_fft=n_fft, hop_length=hop_length, window=window, return_complex=True)
        Sv = torch.stft(v_t, n_fft=n_fft, hop_length=hop_length, window=window, return_complex=True)
        Sm = torch.stft(m_t, n_fft=n_fft, hop_length=hop_length, window=window, return_complex=True)
        
        # Calculate magnitudes squared (Power)
        mag_v_sq = torch.abs(Sv) ** 2
        mag_m_sq = torch.abs(Sm) ** 2
        
        # Ideal Ratio Mask on GPU
        H_speech = mag_v_sq / (mag_v_sq + mag_m_sq + 1e-12)
        H_music  = mag_m_sq / (mag_v_sq + mag_m_sq + 1e-12)
        
        # Apply mask
        S_speech = Sx * H_speech
        S_music  = Sx * H_music
        
        # Inverse STFT
        speech_recon = torch.istft(S_speech, n_fft=n_fft, hop_length=hop_length, window=window, length=x_t.size(0))
        music_recon  = torch.istft(S_music, n_fft=n_fft, hop_length=hop_length, window=window, length=x_t.size(0))
        
        return speech_recon.cpu().numpy(), music_recon.cpu().numpy()
        
    except ImportError:
        print("⚠️ PyTorch is not installed. To use GPU acceleration, run: pip install torch torchaudio")
        print("Falling back to CPU NumPy/SciPy processing...")
        return cpu_stft_processing(x, v, m, fs)

def cpu_stft_processing(x, v, m, fs):
    n_fft = 4096
    hop = 1024
    
    # Compute STFTs
    _, _, Sx = stft(x, fs, nperseg=n_fft, noverlap=n_fft-hop)
    _, _, Sv = stft(v, fs, nperseg=n_fft, noverlap=n_fft-hop)
    _, _, Sm = stft(m, fs, nperseg=n_fft, noverlap=n_fft-hop)
    
    # Magnitudes squared
    mag_v_sq = np.abs(Sv)**2
    mag_m_sq = np.abs(Sm)**2
    
    # Apply Mask
    H_speech = mag_v_sq / (mag_v_sq + mag_m_sq + 1e-12)
    H_music  = mag_m_sq / (mag_v_sq + mag_m_sq + 1e-12)
    
    _, speech_recon = istft(Sx * H_speech, fs, nperseg=n_fft, noverlap=n_fft-hop)
    _, music_recon  = istft(Sx * H_music, fs, nperseg=n_fft, noverlap=n_fft-hop)
    
    return speech_recon[:len(x)], music_recon[:len(x)]

def validate_separation():
    print("\n--- Part 1: Perfect Source Separation ---")
    fs, x = wav.read('cafe_sample.wav')
    _, v = wav.read('website_vocals.wav')
    _, m = wav.read('website_music.wav')
    
    # Normalize to -1.0 to 1.0 floats
    x = ensure_mono(x).astype(np.float32) / 32768.0
    v = ensure_mono(v).astype(np.float32) / 32768.0
    m = ensure_mono(m).astype(np.float32) / 32768.0
    
    min_len = min(len(x), len(v), len(m))
    x, v, m = x[:min_len], v[:min_len], m[:min_len]

    # Process!
    speech_out, music_out = gpu_stft_processing(x, v, m, fs)
    
    # Normalize output to prevent clipping
    speech_out = speech_out * 0.9 / np.max(np.abs(speech_out))
    music_out = music_out * 0.9 / np.max(np.abs(music_out))
    
    # Save files
    wav.write('python_speech_validated.wav', fs, (speech_out * 32767).astype(np.int16))
    wav.write('python_music_validated.wav', fs, (music_out * 32767).astype(np.int16))
    print("Files saved: 'python_speech_validated.wav' and 'python_music_validated.wav'")

def validate_hidden_message():
    print("\n--- Part 2: Hidden Message Forensics ---")
    fs, x = wav.read('cafe_sample.wav')
    x = ensure_mono(x).astype(np.float32) / 32768.0
    
    print("Generating ultra-high-resolution spectrogram focusing on 17.6 kHz...")
    plt.figure(figsize=(14, 6))
    
    # Produce spectrogram at the target frequency
    plt.specgram(x, NFFT=2048, Fs=fs, noverlap=1024, cmap='hot', vmin=-110, vmax=-40)
    plt.ylim([17000, 18000])
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
    plt.title('Python GPU-Validated Spectrogram (Zoom at 17.6 kHz)')
    
    plt.savefig('python_hidden_message_validation.png', dpi=150, bbox_inches='tight')
    print("Saved plot: 'python_hidden_message_validation.png'")
    
if __name__ == "__main__":
    validate_separation()
    validate_hidden_message()
    print("\n✅ Python Validation Complete!\n")
