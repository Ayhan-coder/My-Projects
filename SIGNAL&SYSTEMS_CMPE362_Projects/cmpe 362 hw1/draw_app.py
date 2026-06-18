import tkinter as tk
from PIL import Image, ImageDraw
import numpy as np
from scipy.io import wavfile
import threading
import winsound
import os

class SpectrogramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spectrogram Painter -> complex_recreate.wav")
        self.root.configure(bg="#2b2b2b")
        
        # Canvas size
        self.width = 1000
        self.height = 400
        
        # Title
        title = tk.Label(root, text="Draw Your Audio", font=("Helvetica", 16, "bold"), bg="#2b2b2b", fg="white")
        title.pack(pady=10)
        
        # Canvas
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg='black', cursor="crosshair")
        self.canvas.pack(pady=5, padx=20)
        
        # PIL Image for saving and processing
        self.image = Image.new("RGB", (self.width, self.height), "black")
        self.draw = ImageDraw.Draw(self.image)
        
        # Bindings
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Button-1>", self.paint)
        self.canvas.bind("<B3-Motion>", self.erase)
        self.canvas.bind("<Button-3>", self.erase)
        
        # Controls
        self.btn_frame = tk.Frame(root, bg="#2b2b2b")
        self.btn_frame.pack(pady=10)
        
        self.clear_btn = tk.Button(self.btn_frame, text="🗑 Clear Canvas", font=("Helvetica", 12), command=self.clear, width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=10)
        
        self.synth_btn = tk.Button(self.btn_frame, text="⚙️ Synthesize Audio", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", command=self.synthesize_thread, width=20)
        self.synth_btn.pack(side=tk.LEFT, padx=10)
        
        self.play_btn = tk.Button(self.btn_frame, text="▶️ Play Audio", font=("Helvetica", 12), command=self.play_audio, state=tk.DISABLED, width=15)
        self.play_btn.pack(side=tk.LEFT, padx=10)
        
        self.status = tk.Label(root, text="Left Click: Draw  |  Right Click: Erase", font=("Helvetica", 11), bg="#2b2b2b", fg="#aaaaaa")
        self.status.pack(pady=10)
        
        self.brush_size = 6

    def paint(self, event):
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
        self.canvas.create_oval(x1, y1, x2, y2, fill="white", outline="white")
        self.draw.ellipse([x1, y1, x2, y2], fill="white")

    def erase(self, event):
        x1, y1 = (event.x - self.brush_size*2), (event.y - self.brush_size*2)
        x2, y2 = (event.x + self.brush_size*2), (event.y + self.brush_size*2)
        self.canvas.create_oval(x1, y1, x2, y2, fill="black", outline="black")
        self.draw.ellipse([x1, y1, x2, y2], fill="black")

    def clear(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (self.width, self.height), "black")
        self.draw = ImageDraw.Draw(self.image)
        self.status.config(text="Canvas cleared.", fg="#aaaaaa")
        self.play_btn.config(state=tk.DISABLED)

    def play_audio(self):
        if os.path.exists("complex_recreate.wav"):
            winsound.PlaySound("complex_recreate.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            self.status.config(text="Playing complex_recreate.wav...", fg="#4CAF50")

    def synthesize_thread(self):
        self.status.config(text="Synthesizing audio... Please wait (this takes ~5-10 seconds).", fg="#FFC107")
        self.synth_btn.config(state=tk.DISABLED, text="Synthesizing...")
        self.clear_btn.config(state=tk.DISABLED)
        self.play_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.synthesize, daemon=True).start()

    def synthesize(self):
        try:
            # Audio parameters
            FS = 48000
            DURATION = 6.0
            FMAX = 8000
            NFFT = 2048
            HOP = 512
            N_FRAMES = int((DURATION * FS - NFFT) / HOP) + 1
            FMAX_BIN = int(FMAX / (FS / 2) * (NFFT // 2 + 1)) + 1
            GRIFFIN_LIM = 50
            
            # Convert image to numpy array
            arr = np.array(self.image, dtype=np.float32)
            gray = 0.299*arr[:,:,0] + 0.587*arr[:,:,1] + 0.114*arr[:,:,2]
            gray = gray / 255.0
            gray[gray < 0.05] = 0.0
            gray = np.clip(gray * 1.5, 0.0, 1.0)
            
            # Flip vertically (row 0 = low freq)
            gray = np.flipud(gray)
            
            # Resize to match STFT bins and frames
            pil_resized = Image.fromarray((gray * 255).astype(np.uint8))
            pil_resized = pil_resized.resize((N_FRAMES, FMAX_BIN), Image.LANCZOS)
            canvas_arr = np.array(pil_resized, dtype=np.float32) / 255.0
            
            n_bins = NFFT // 2 + 1
            full_mag = np.zeros((n_bins, N_FRAMES), dtype=np.float32)
            full_mag[:FMAX_BIN, :] = canvas_arr
            
            # Griffin-Lim Algorithm
            def istft(S, hop, nfft):
                win = np.hanning(nfft)
                n_fr = S.shape[1]
                total = (n_fr - 1) * hop + nfft
                audio = np.zeros(total)
                win_sq_sum = np.zeros(total)
                for fr in range(n_fr):
                    col = S[:, fr]
                    col_full = np.concatenate([col, np.conj(col[-2:0:-1])])
                    frame = np.real(np.fft.ifft(col_full))
                    idx = fr * hop
                    audio[idx:idx+nfft] += frame * win
                    win_sq_sum[idx:idx+nfft] += win**2
                win_sq_sum = np.maximum(win_sq_sum, 1e-8)
                return audio / win_sq_sum

            def stft(x, hop, nfft):
                win = np.hanning(nfft)
                n_fr = (len(x) - nfft) // hop + 1
                S = np.zeros((n_bins, n_fr), dtype=complex)
                for fr in range(n_fr):
                    frame = x[fr*hop : fr*hop+nfft] * win
                    S[:, fr] = np.fft.fft(frame, nfft)[:n_bins]
                return S

            angles = np.exp(1j * 2 * np.pi * np.random.rand(*full_mag.shape))
            S = full_mag * angles
            
            for it in range(GRIFFIN_LIM):
                audio = istft(S, HOP, NFFT)
                S = stft(audio, HOP, NFFT)
                angle = np.angle(S)
                S = full_mag * np.exp(1j * angle)
                
            audio = istft(S, HOP, NFFT)
            
            # Trim and normalize
            audio = audio[NFFT:-NFFT]
            peak = np.max(np.abs(audio))
            if peak > 0:
                audio = audio / peak * 0.85
                
            # Save to file
            audio_i16 = (audio * 32767).astype(np.int16)
            wavfile.write("complex_recreate.wav", FS, audio_i16)
            
            # Update UI
            self.root.after(0, self.synthesis_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.status.config(text=f"Error: {str(e)}", fg="#F44336"))
            self.root.after(0, lambda: self.synth_btn.config(state=tk.NORMAL, text="⚙️ Synthesize Audio"))
            self.root.after(0, lambda: self.clear_btn.config(state=tk.NORMAL))

    def synthesis_complete(self):
        self.status.config(text="✅ Successfully saved as complex_recreate.wav!", fg="#4CAF50")
        self.synth_btn.config(state=tk.NORMAL, text="⚙️ Synthesize Audio")
        self.clear_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.NORMAL)
        self.play_audio()

if __name__ == "__main__":
    root = tk.Tk()
    # Center the window
    window_width = 1050
    window_height = 550
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
    
    app = SpectrogramApp(root)
    root.mainloop()
