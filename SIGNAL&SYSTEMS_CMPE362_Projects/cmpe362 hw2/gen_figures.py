import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fs = 10000
T  = 2
t  = np.arange(-1.5*T, 1.5*T + 1/fs, 1/fs)
w0 = 2*np.pi / T
harmonics = [5, 20, 100]
colors    = ['#e74c3c', '#27ae60', '#2980b9']  # red, green, blue

FIG_W, FIG_H = 10, 4.5   # inches for a 16:9 slide image

def save(fig, name):
    fig.savefig(name, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'saved {name}')

# ── helpers ────────────────────────────────────────────────────────────────
def sq_wave(t):
    return np.sign(np.sin(w0 * t))

def sq_series(t, N):
    s = np.zeros_like(t)
    for n in range(1, 2*N, 2):
        s += (4/np.pi) * (1/n) * np.sin(n * w0 * t)
    return s

def tri_wave(t):
    return (2/np.pi) * np.arcsin(np.sin(w0 * t))

def tri_series(t, N):
    s = np.zeros_like(t)
    for k, n in enumerate(range(1, 2*N, 2)):
        s += ((-1)**k) / (n**2) * np.sin(n * w0 * t)
    return s * (8/np.pi**2)

def rect_wave(t):
    return np.abs(np.sin(w0/2 * t))

def rect_series(t, N):
    s = np.full_like(t, 2/np.pi)
    for n in range(1, N+1):
        s -= (4/np.pi) * (1/(4*n**2 - 1)) * np.cos(n * w0 * t)
    return s

# ── plotting helper ─────────────────────────────────────────────────────────
def make_fig(target, series_fn, harmonics, colors,
             xlim=(-0.5*T, 1.5*T), ylim=None, title=''):
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    ax.plot(t, target, color=[0.78, 0.78, 0.78], linewidth=2.5,
            label='Target', zorder=1)
    for N, c in zip(harmonics, colors):
        ax.plot(t, series_fn(t, N), color=c, linewidth=1.4,
                label=f'$N={N}$', zorder=2)
    ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('Amplitude', fontsize=12)
    ax.set_title(title, fontsize=13)
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig

# ═══════════════════════════════════════════════════════════════════════════
# 1.  SQUARE WAVE
# ═══════════════════════════════════════════════════════════════════════════
target_sq = sq_wave(t)

fig = make_fig(target_sq, sq_series, harmonics, colors,
               xlim=(-0.5*T, 1.5*T),
               title='Square Wave — Fourier Approximations ($N=5,20,100$)')
save(fig, 'sq_full.png')

fig = make_fig(target_sq, sq_series, harmonics, colors,
               xlim=(-0.05*T, 0.05*T), ylim=(-1.25, 1.25),
               title='Square Wave — Zoomed at Discontinuity (Gibbs Phenomenon)')
save(fig, 'sq_zoom.png')

# ═══════════════════════════════════════════════════════════════════════════
# 2.  TRIANGULAR WAVE
# ═══════════════════════════════════════════════════════════════════════════
target_tri = tri_wave(t)

fig = make_fig(target_tri, tri_series, harmonics, colors,
               xlim=(-0.5*T, 1.5*T),
               title='Triangular Wave — Fourier Approximations ($N=5,20,100$)')
save(fig, 'tri_full.png')

fig = make_fig(target_tri, tri_series, harmonics, colors,
               xlim=(T/4 - 0.06*T, T/4 + 0.06*T), ylim=(0.75, 1.05),
               title='Triangular Wave — Zoomed at Peak')
save(fig, 'tri_zoom.png')

# ═══════════════════════════════════════════════════════════════════════════
# 3.  FULL-WAVE RECTIFIED SINE
# ═══════════════════════════════════════════════════════════════════════════
target_rect = rect_wave(t)

fig = make_fig(target_rect, rect_series, harmonics, colors,
               xlim=(-0.5*T, 1.5*T),
               title='Full-Wave Rectified Sine — Fourier Approximations ($N=5,20,100$)')
save(fig, 'rect_full.png')

fig = make_fig(target_rect, rect_series, harmonics, colors,
               xlim=(-0.06*T, 0.06*T), ylim=(-0.05, 0.35),
               title='Full-Wave Rectified Sine — Zoomed at Cusp')
save(fig, 'rect_zoom.png')

print('\nAll 6 figures saved.')
