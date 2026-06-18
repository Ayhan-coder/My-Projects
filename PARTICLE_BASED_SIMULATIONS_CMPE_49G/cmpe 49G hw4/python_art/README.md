## Python generative paintings

This folder contains a small script that generates high-res "paintings" as PNGs.

### Setup

From the workspace root:

- Install deps: `python -m pip install numpy pillow`

If you want to use the workspace virtualenv explicitly in PowerShell:

- `& .\.venv\Scripts\python.exe -m pip install numpy pillow`

### Generate images

- Starry night style:
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style starry --seed 1 --size 1920x1080`

- Dune ridges style:
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style dunes --seed 7 --size 2400x1600`

- Aurora / flow-field style:
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style aurora --seed 42 --size 1920x1080`

- Diffusion + flow-field style:
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style diffuse_flow --seed 203 --size 1920x1080 --vibe colorful`

- Field particles (Perlin-like flow field + layered particle sets + different brush shapes):
  - Rectangle “charcoal” brush:
    - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style field_particles --seed 11 --size 1920x1080 --vibe colorful --brush rect`
  - Arc brush:
    - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style field_particles --seed 12 --size 1920x1080 --vibe colorful --brush arc`
  - Triangle brush:
    - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style field_particles --seed 13 --size 1920x1080 --vibe colorful --brush tri`
  - Perpendicular hatch brush:
    - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style field_particles --seed 14 --size 1920x1080 --vibe colorful --brush perp`

- Confetti ribbons (dense flat-color boomerang/leaf shapes):
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style confetti --seed 5 --size 768x768`

- Confetti ribbons (chunky / fewer bigger pieces):
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style confetti_chunky --seed 5 --size 768x768`

- Marbled ribbons (warped rainbow stripes with contour + hatch texture):
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style marbled_ribbons --seed 7 --size 768x768 --vibe colorful`

- Neon currents (dark flow-field hairlines with glowing rivers):
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style neon_currents --seed 9 --size 1344x768 --vibe night`

- Reaction diffusion (Gray-Scott, noise-biased feed/kill):
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style reaction_diffusion --seed 21 --size 1920x1080 --vibe storm --grade pro`

- Topo contours (warped fBm heightfield with contour lines):
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style topo_contours --seed 22 --size 1920x1080 --vibe desert --grade pro`

- Kaleido noise (kaleidoscopic remap of a Perlin-like color field):
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style kaleido_noise --seed 23 --size 1920x1080 --vibe colorful --grade pro`

- Multi-style grid collage (3x2 mixed styles in one image):
  - `& .\.venv\Scripts\python.exe python_art\generate_paintings.py --style style_grid --seed 123 --size 1920x1080 --grade pro`

Outputs go to `./out`.

### Tips

- Change `--seed` to get a new painting with the same style.
- Try `--vibe night|desert|storm` to force a palette.
- The output filename includes `--vibe` (and `--brush` for `field_particles`) so variants don't overwrite each other.
- For a more polished look, add `--grade pro` (adds subtle filmic tone/contrast, vignette, grain; bloom on neon styles).
