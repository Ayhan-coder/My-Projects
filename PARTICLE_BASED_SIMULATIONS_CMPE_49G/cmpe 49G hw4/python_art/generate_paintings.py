"""Generative "paintings" (PNG) using numpy + Pillow.

Usage examples:
  python generate_paintings.py --style starry --seed 1 --size 1920x1080
  python generate_paintings.py --style dunes --seed 7 --size 2400x1600
  python generate_paintings.py --style aurora --seed 42 --size 1920x1080

Output goes to ./out by default.

Note: This is intentionally self-contained (no external noise libs).
"""

from __future__ import annotations

import argparse
import colorsys
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def parse_size(value: str) -> tuple[int, int]:
    try:
        w_str, h_str = value.lower().split("x")
        w = int(w_str)
        h = int(h_str)
        if w <= 0 or h <= 0:
            raise ValueError
        return w, h
    except Exception as exc:  # noqa: BLE001
        raise argparse.ArgumentTypeError("Size must be like 1920x1080") from exc


def clamp01(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, 1.0)


def to_uint8(rgb01: np.ndarray) -> np.ndarray:
    return (clamp01(rgb01) * 255.0 + 0.5).astype(np.uint8)


def lerp(a: np.ndarray, b: np.ndarray, t: np.ndarray) -> np.ndarray:
    return a * (1.0 - t) + b * t


def smoothstep(t: np.ndarray) -> np.ndarray:
    t = clamp01(t)
    return t * t * (3.0 - 2.0 * t)


def make_rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def value_noise_2d(
    rng: np.random.Generator,
    width: int,
    height: int,
    grid: int,
) -> np.ndarray:
    """Value noise via random grid + smooth bilinear interpolation."""
    gx = max(2, width // grid + 2)
    gy = max(2, height // grid + 2)
    grid_values = rng.random((gy, gx), dtype=np.float32)

    xs = np.linspace(0, gx - 2, width, dtype=np.float32)
    ys = np.linspace(0, gy - 2, height, dtype=np.float32)
    x0 = np.floor(xs).astype(np.int32)
    y0 = np.floor(ys).astype(np.int32)
    tx = smoothstep(xs - x0)
    ty = smoothstep(ys - y0)

    x1 = x0 + 1
    y1 = y0 + 1

    # Broadcast to image grid
    v00 = grid_values[y0[:, None], x0[None, :]]
    v10 = grid_values[y0[:, None], x1[None, :]]
    v01 = grid_values[y1[:, None], x0[None, :]]
    v11 = grid_values[y1[:, None], x1[None, :]]

    a = lerp(v00, v10, tx[None, :])
    b = lerp(v01, v11, tx[None, :])
    return lerp(a, b, ty[:, None])


def fbm(
    rng: np.random.Generator,
    width: int,
    height: int,
    base_grid: int,
    octaves: int = 6,
    lacunarity: float = 2.0,
    gain: float = 0.5,
) -> np.ndarray:
    amp = 1.0
    freq = 1.0
    total = np.zeros((height, width), dtype=np.float32)
    norm = 0.0
    for _ in range(octaves):
        grid = max(4, int(base_grid / freq))
        total += amp * value_noise_2d(rng, width, height, grid=grid)
        norm += amp
        amp *= gain
        freq *= lacunarity
    return total / max(1e-6, norm)


@dataclass(frozen=True)
class Palette:
    bg: tuple[float, float, float]
    a: tuple[float, float, float]
    b: tuple[float, float, float]
    c: tuple[float, float, float]


def hsv(h: float, s: float, v: float) -> tuple[float, float, float]:
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, clamp01(np.array([s]))[0], clamp01(np.array([v]))[0])
    return float(r), float(g), float(b)


def golden_ratio_palette(rng: np.random.Generator, n: int) -> list[tuple[float, float, float]]:
    """Generate visually spaced colors in HSV using golden ratio increments."""
    phi = 0.618033988749895  # golden ratio conjugate
    h0 = float(rng.random())
    colors: list[tuple[float, float, float]] = []
    for i in range(n):
        h = (h0 + phi * i) % 1.0
        s = float(rng.uniform(0.55, 0.95))
        v = float(rng.uniform(0.65, 1.00))
        colors.append(hsv(h, s, v))
    return colors


def hsv_to_rgb_np(h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Vectorized HSV->RGB. Inputs/outputs in [0,1]."""
    h = np.mod(h, 1.0).astype(np.float32)
    s = clamp01(s.astype(np.float32))
    v = clamp01(v.astype(np.float32))

    i = np.floor(h * 6.0).astype(np.int32)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)

    i_mod = np.mod(i, 6)

    r = np.empty_like(h, dtype=np.float32)
    g = np.empty_like(h, dtype=np.float32)
    b = np.empty_like(h, dtype=np.float32)

    m0 = i_mod == 0
    m1 = i_mod == 1
    m2 = i_mod == 2
    m3 = i_mod == 3
    m4 = i_mod == 4
    m5 = i_mod == 5

    r[m0], g[m0], b[m0] = v[m0], t[m0], p[m0]
    r[m1], g[m1], b[m1] = q[m1], v[m1], p[m1]
    r[m2], g[m2], b[m2] = p[m2], v[m2], t[m2]
    r[m3], g[m3], b[m3] = p[m3], q[m3], v[m3]
    r[m4], g[m4], b[m4] = t[m4], p[m4], v[m4]
    r[m5], g[m5], b[m5] = v[m5], p[m5], q[m5]

    return np.stack([r, g, b], axis=-1)


def choose_palette(rng: np.random.Generator, vibe: str) -> Palette:
    vibe = vibe.lower()
    if vibe == "night":
        return Palette(
            bg=hsv(0.62, 0.70, 0.08),
            a=hsv(0.58, 0.60, 0.30),
            b=hsv(0.12, 0.70, 0.95),
            c=hsv(0.82, 0.45, 0.70),
        )
    if vibe == "desert":
        return Palette(
            bg=hsv(0.08, 0.65, 0.10),
            a=hsv(0.08, 0.55, 0.40),
            b=hsv(0.10, 0.65, 0.85),
            c=hsv(0.12, 0.25, 0.95),
        )
    if vibe == "storm":
        return Palette(
            bg=hsv(0.60, 0.60, 0.05),
            a=hsv(0.52, 0.75, 0.45),
            b=hsv(0.33, 0.80, 0.85),
            c=hsv(0.83, 0.45, 0.80),
        )

    if vibe == "colorful":
        # High saturation, high contrast, "poster-like" palette.
        h0 = rng.random()
        return Palette(
            bg=hsv(h0 + 0.55, 0.85, 0.10),
            a=hsv(h0 + 0.15, 0.95, 0.55),
            b=hsv(h0 + 0.00, 1.00, 1.00),
            c=hsv(h0 + 0.65, 0.95, 0.90),
        )

    # Random but coherent
    h0 = rng.random()
    return Palette(
        bg=hsv(h0 + 0.50, 0.75, 0.08),
        a=hsv(h0 + 0.10, 0.55, 0.35),
        b=hsv(h0 + 0.00, 0.75, 0.95),
        c=hsv(h0 + 0.75, 0.45, 0.75),
    )


def paint_starry(rng: np.random.Generator, w: int, h: int, palette: Palette) -> Image.Image:
    n = fbm(rng, w, h, base_grid=220, octaves=6)
    n2 = fbm(rng, w, h, base_grid=90, octaves=5)
    v = clamp01(0.15 + 0.85 * (0.6 * n + 0.4 * (n2**1.8)))

    # Background gradient (top->bottom)
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    grad_line = lerp(
        np.array(palette.bg, dtype=np.float32),
        np.array(palette.a, dtype=np.float32),
        y[..., None],
    )
    grad = np.repeat(grad_line, w, axis=1)

    # Nebula tint
    tint = lerp(np.array(palette.c, dtype=np.float32), np.array(palette.b, dtype=np.float32), (n2**1.2)[..., None])
    img = grad + (v[..., None] ** 2.2) * 0.65 * tint

    # Stars
    img8 = to_uint8(img)
    im = Image.fromarray(img8, mode="RGB")
    draw = ImageDraw.Draw(im)

    star_count = int((w * h) / 2200)
    for _ in range(star_count):
        x = int(rng.integers(0, w))
        y0 = int(rng.integers(0, h))
        r = float(rng.random() ** 2.2) * 1.8 + 0.2
        b = float(rng.random() ** 1.5)
        col = (255, 255, 255) if b < 0.85 else (255, 240, 190)
        draw.ellipse((x - r, y0 - r, x + r, y0 + r), fill=col)

    im = im.filter(ImageFilter.GaussianBlur(radius=0.6))
    # Re-add sharp stars
    draw = ImageDraw.Draw(im)
    for _ in range(star_count // 3):
        x = int(rng.integers(0, w))
        y0 = int(rng.integers(0, h))
        draw.point((x, y0), fill=(255, 255, 255))

    # Vignette
    xx = (np.linspace(-1, 1, w, dtype=np.float32)[None, :])
    yy = (np.linspace(-1, 1, h, dtype=np.float32)[:, None])
    rr = np.sqrt(xx * xx + yy * yy)
    vig = clamp01(1.0 - (rr**2.2) * 0.55)
    arr = np.asarray(im).astype(np.float32) / 255.0
    arr *= vig[..., None]
    return Image.fromarray(to_uint8(arr), mode="RGB")


def paint_dunes(rng: np.random.Generator, w: int, h: int, palette: Palette) -> Image.Image:
    base = fbm(rng, w, h, base_grid=180, octaves=7)
    ridge = fbm(rng, w, h, base_grid=60, octaves=6)

    # Make ridges by folding noise
    dunes = 1.0 - np.abs(2.0 * ridge - 1.0)
    dunes = dunes**2.6

    # Lighting direction
    lx, ly = 0.8, -0.6
    gx = np.gradient(base, axis=1)
    gy = np.gradient(base, axis=0)
    light = clamp01(0.55 + 0.9 * (lx * (-gx) + ly * (-gy)))

    sand = lerp(np.array(palette.a, dtype=np.float32), np.array(palette.b, dtype=np.float32), dunes[..., None])

    # Sky
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    sky_line = lerp(
        np.array(palette.c, dtype=np.float32),
        np.array(palette.bg, dtype=np.float32),
        (y**1.8)[..., None],
    )
    sky = np.repeat(sky_line, w, axis=1)

    horizon = int(h * 0.42)
    img = np.zeros((h, w, 3), dtype=np.float32)
    img[:horizon] = sky[:horizon]

    # Dunes below horizon with atmospheric fade
    fade = clamp01((np.linspace(0, 1, h - horizon, dtype=np.float32)[:, None]) ** 0.6)
    dune_rgb = sand[horizon:] * (0.55 + 0.45 * light[horizon:][..., None])
    dune_rgb = lerp(sky[horizon:], dune_rgb, fade[..., None])
    img[horizon:] = dune_rgb

    # Add fine grain
    grain = rng.normal(0.0, 0.02, size=(h, w, 1)).astype(np.float32)
    img = clamp01(img + grain)

    # Slight blur then sharpen-ish
    im = Image.fromarray(to_uint8(img), mode="RGB")
    im = im.filter(ImageFilter.GaussianBlur(radius=0.7))
    return im


def _flow_field(rng: np.random.Generator, w: int, h: int) -> tuple[np.ndarray, np.ndarray]:
    ang = fbm(rng, w, h, base_grid=140, octaves=6)
    ang = (ang * 2.0 - 1.0) * math.pi * 1.2
    u = np.cos(ang).astype(np.float32)
    v = np.sin(ang).astype(np.float32)
    return u, v


def paint_aurora(rng: np.random.Generator, w: int, h: int, palette: Palette) -> Image.Image:
    # Base background
    bg = paint_starry(make_rng(int(rng.integers(0, 2**31 - 1))), w, h, palette)
    canvas = bg.convert("RGBA")

    u, v = _flow_field(rng, w, h)

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    # Seed points near top-ish
    trails = int((w * h) / 9000)
    steps = 220

    c1 = np.array(palette.b, dtype=np.float32)
    c2 = np.array(palette.c, dtype=np.float32)

    for _ in range(trails):
        x = float(rng.uniform(0, w - 1))
        y = float(rng.uniform(0.05 * h, 0.55 * h))
        width0 = float(rng.uniform(0.8, 2.2))
        alpha0 = float(rng.uniform(0.06, 0.18))

        for i in range(steps):
            xi = int(x)
            yi = int(y)
            if xi < 0 or xi >= w or yi < 0 or yi >= h:
                break
            fx = float(u[yi, xi])
            fy = float(v[yi, xi])

            t = i / max(1, steps - 1)
            col = lerp(c1, c2, t)
            # Fade with altitude and time
            alt = 1.0 - (y / h)
            a = alpha0 * (0.35 + 0.65 * alt) * (1.0 - 0.7 * t)
            rgb = tuple(int(255 * c) for c in col)
            aa = int(255 * clamp01(np.array([a], dtype=np.float32))[0])

            r = width0 * (0.7 + 0.6 * alt) * (0.7 + 0.6 * (1.0 - t))
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(rgb[0], rgb[1], rgb[2], aa))

            # Step with a little turbulence
            x += fx * 2.2 + float(rng.normal(0.0, 0.25))
            y += fy * 1.7 + float(rng.normal(0.0, 0.15))

    layer = layer.filter(ImageFilter.GaussianBlur(radius=2.2))
    canvas = Image.alpha_composite(canvas, layer)

    # Gentle color grading
    arr = np.asarray(canvas.convert("RGB")).astype(np.float32) / 255.0
    arr = clamp01(arr ** 0.95)
    return Image.fromarray(to_uint8(arr), mode="RGB")


def paint_diffuse_flow(rng: np.random.Generator, w: int, h: int, palette: Palette) -> Image.Image:
    """Diffusing particles in a biased Perlin-like flow field.

    - Perlin-like noise (fbm/value noise) defines the flow direction.
    - Diffusion is modeled by random walk jitter.
    - Bias structure: particles spawn from an off-center source region.
    """

    # Flow field from noise
    ang = fbm(rng, w, h, base_grid=160, octaves=6)
    ang2 = fbm(rng, w, h, base_grid=55, octaves=5)
    angle = (ang * 2.0 - 1.0) * math.pi * (1.2 + 0.8 * ang2)
    u = np.cos(angle).astype(np.float32)
    v = np.sin(angle).astype(np.float32)

    # Biased source region (left-ish, slightly above center)
    sx = int(w * (0.18 + 0.07 * float(rng.random())))
    sy = int(h * (0.45 + 0.10 * float(rng.random())))
    sr = int(min(w, h) * 0.11)

    # Accumulation buffer
    acc = np.zeros((h, w), dtype=np.float32)

    # Particle simulation (vectorized)
    n_particles = int((w * h) / 220)  # ~9k for 1080p
    steps = 260

    # Initialize particles in a disk around (sx, sy)
    theta = rng.random(n_particles, dtype=np.float32) * (2.0 * math.pi)
    rad = (rng.random(n_particles, dtype=np.float32) ** 0.6) * sr
    px = (sx + rad * np.cos(theta)).astype(np.float32)
    py = (sy + rad * np.sin(theta)).astype(np.float32)

    # Color mapping noise (for later)
    color_n = fbm(rng, w, h, base_grid=95, octaves=5)

    for i in range(steps):
        xi = np.clip(px.astype(np.int32), 0, w - 1)
        yi = np.clip(py.astype(np.int32), 0, h - 1)

        # Deposit (heavier early for brighter core)
        t = 1.0 - (i / max(1, steps - 1))
        np.add.at(acc, (yi, xi), 0.45 * t + 0.08)

        # Advection + diffusion
        fx = u[yi, xi]
        fy = v[yi, xi]

        # Bias: gently pull towards a curved "spine" across the canvas
        spine_y = (0.52 + 0.12 * np.sin((xi / max(1, w - 1)) * 2.0 * math.pi)).astype(np.float32) * h
        pull = (spine_y - py) * 0.0035

        px += fx * 2.0 + rng.normal(0.0, 0.9, size=n_particles).astype(np.float32)
        py += fy * 1.7 + pull + rng.normal(0.0, 0.9, size=n_particles).astype(np.float32)

        # Wrap edges for continuity
        px = np.mod(px, w).astype(np.float32)
        py = np.mod(py, h).astype(np.float32)

    # Normalize and diffuse (blur) the ink
    acc = acc / max(1e-6, float(np.percentile(acc, 99.6)))
    acc = clamp01(acc)

    # Pillow blur for diffusion look
    ink = Image.fromarray(to_uint8(acc[..., None].repeat(3, axis=2)), mode="RGB")
    ink = ink.filter(ImageFilter.GaussianBlur(radius=2.4))
    ink_arr = np.asarray(ink).astype(np.float32) / 255.0

    # Colorize: map ink amount + noise to palette
    p_bg = np.array(palette.bg, dtype=np.float32)
    p_a = np.array(palette.a, dtype=np.float32)
    p_b = np.array(palette.b, dtype=np.float32)
    p_c = np.array(palette.c, dtype=np.float32)

    m = (ink_arr[..., 0] ** 1.15).astype(np.float32)
    hue_t = clamp01(0.15 + 0.85 * color_n)
    col1 = lerp(p_a, p_b, hue_t[..., None])
    col2 = lerp(p_c, p_b, (color_n**1.6)[..., None])
    paint = lerp(col1, col2, (m**0.9)[..., None])
    out = lerp(p_bg, paint, (m**1.05)[..., None])

    # Gentle contrast
    out = clamp01(out ** 0.92)
    return Image.fromarray(to_uint8(out), mode="RGB")


def paint_flow_lines(rng: np.random.Generator, w: int, h: int, palette: Palette) -> Image.Image:
    """Streamlines in a Perlin-like flow field (classic flow-field art)."""

    ang = fbm(rng, w, h, base_grid=140, octaves=6)
    ang2 = fbm(rng, w, h, base_grid=45, octaves=5)
    angle = (ang * 2.0 - 1.0) * math.pi * (1.0 + 1.2 * ang2)
    u = np.cos(angle).astype(np.float32)
    v = np.sin(angle).astype(np.float32)

    # Base background
    bg = np.zeros((h, w, 3), dtype=np.float32)
    p_bg = np.array(palette.bg, dtype=np.float32)
    p_a = np.array(palette.a, dtype=np.float32)
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    grad_line = lerp(p_bg, p_a, (y**1.4)[..., None])
    bg = np.repeat(grad_line, w, axis=1)

    base = Image.fromarray(to_uint8(bg), mode="RGB").convert("RGBA")
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    p_b = np.array(palette.b, dtype=np.float32)
    p_c = np.array(palette.c, dtype=np.float32)
    color_n = fbm(rng, w, h, base_grid=110, octaves=5)

    n_lines = int((w * h) / 7000)  # ~300 for 1080p
    steps = 380

    for _ in range(n_lines):
        x = float(rng.uniform(0, w - 1))
        y0 = float(rng.uniform(0, h - 1))
        thickness = float(rng.uniform(0.8, 2.2))
        alpha = int(rng.uniform(18, 40))

        for i in range(steps):
            xi = int(x) % w
            yi = int(y0) % h

            # Color along the line
            t = i / max(1, steps - 1)
            cn = float(color_n[yi, xi])
            col = lerp(p_b, p_c, cn)
            col = lerp(col, p_a, (t**1.3))
            rgba = (int(255 * col[0]), int(255 * col[1]), int(255 * col[2]), alpha)

            # Small segment
            fx = float(u[yi, xi])
            fy = float(v[yi, xi])
            x2 = x + fx * 3.0
            y2 = y0 + fy * 3.0
            draw.line((x, y0, x2, y2), fill=rgba, width=int(round(thickness)))

            # Step with a hint of diffusion
            x = x2 + float(rng.normal(0.0, 0.25))
            y0 = y2 + float(rng.normal(0.0, 0.25))

            if x < -5 or x > w + 5 or y0 < -5 or y0 > h + 5:
                break

    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.6))
    out = Image.alpha_composite(base, layer).convert("RGB")
    return out


def paint_noisy_circles(rng: np.random.Generator, w: int, h: int, palette: Palette) -> Image.Image:
    """Geometric pattern: circles with radii/colors modulated by Perlin-like noise + a bias."""

    p_bg = np.array(palette.bg, dtype=np.float32)
    p_a = np.array(palette.a, dtype=np.float32)
    p_b = np.array(palette.b, dtype=np.float32)
    p_c = np.array(palette.c, dtype=np.float32)

    # Background
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    grad_line = lerp(p_bg, p_a, (y**1.6)[..., None])
    bg = np.repeat(grad_line, w, axis=1)
    im = Image.fromarray(to_uint8(bg), mode="RGB").convert("RGBA")
    draw = ImageDraw.Draw(im, "RGBA")

    n = fbm(rng, w, h, base_grid=120, octaves=6)
    n2 = fbm(rng, w, h, base_grid=50, octaves=5)

    # Bias: push circles away from a "void" area
    void_x = w * (0.72 + 0.06 * float(rng.random()))
    void_y = h * (0.36 + 0.10 * float(rng.random()))
    void_r = min(w, h) * (0.22 + 0.04 * float(rng.random()))

    spacing = int(max(16, min(w, h) / 45))
    jitter = spacing * 0.35

    for y0 in range(0, h, spacing):
        for x0 in range(0, w, spacing):
            x = float(x0 + rng.normal(0.0, jitter))
            y_ = float(y0 + rng.normal(0.0, jitter))
            if x < 0 or x >= w or y_ < 0 or y_ >= h:
                continue

            d = math.hypot(x - void_x, y_ - void_y)
            bias = clamp01(np.array([(d - void_r) / max(1.0, void_r)], dtype=np.float32))[0]

            xi = int(x)
            yi = int(y_)
            t = float(n[yi, xi])
            t2 = float(n2[yi, xi])

            r = (2.0 + 16.0 * (t**1.6)) * (0.25 + 0.75 * bias)
            if r < 1.2:
                continue

            col = p_b * (1.0 - t2) + p_c * t2
            col = col * bias + p_a * (1.0 - bias)
            alpha = int(40 + 140 * (t**1.4) * (0.3 + 0.7 * bias))
            alpha = int(max(0, min(255, alpha)))

            draw.ellipse(
                (x - r, y_ - r, x + r, y_ + r),
                fill=(int(255 * col[0]), int(255 * col[1]), int(255 * col[2]), alpha),
            )

    im = im.filter(ImageFilter.GaussianBlur(radius=0.9))
    return im.convert("RGB")


def _draw_brush(
    draw: ImageDraw.ImageDraw,
    brush: str,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    rgba: tuple[int, int, int, int],
    width: float,
    rng: np.random.Generator,
) -> None:
    brush = brush.lower()
    w_int = max(1, int(round(width)))

    if brush == "dot":
        r = max(0.8, width * 0.7)
        draw.ellipse((x2 - r, y2 - r, x2 + r, y2 + r), fill=rgba)
        return

    dx = x2 - x1
    dy = y2 - y1
    mag = math.hypot(dx, dy)
    if mag < 1e-6:
        return

    ux = dx / mag
    uy = dy / mag
    px = -uy
    py = ux

    if brush == "line":
        draw.line((x1, y1, x2, y2), fill=rgba, width=w_int)
        return

    if brush == "perp":
        half = (3.5 + 7.0 * float(rng.random())) * width * 0.35
        ax = x2 - px * half
        ay = y2 - py * half
        bx = x2 + px * half
        by = y2 + py * half
        draw.line((ax, ay, bx, by), fill=rgba, width=w_int)
        return

    if brush == "arc":
        r = max(2.0, width * (3.0 + 6.0 * float(rng.random())))
        start = float(rng.uniform(0, 360))
        extent = float(rng.uniform(40, 160))
        bbox = (x2 - r, y2 - r, x2 + r, y2 + r)
        draw.arc(bbox, start=start, end=start + extent, fill=rgba, width=w_int)
        return

    if brush == "tri":
        mx = (x1 + x2) * 0.5
        my = (y1 + y2) * 0.5
        lift = (1.5 + 6.0 * float(rng.random())) * width
        cx = mx + px * lift
        cy = my + py * lift
        draw.polygon([(x1, y1), (x2, y2), (cx, cy)], fill=rgba)
        return

    # "rect" (also mimics square stroke caps / charcoal texture)
    half_len = max(1.0, mag * 0.55)
    half_w = max(0.8, width * 0.9)
    c1 = (x2 - ux * half_len - px * half_w, y2 - uy * half_len - py * half_w)
    c2 = (x2 - ux * half_len + px * half_w, y2 - uy * half_len + py * half_w)
    c3 = (x2 + ux * half_len + px * half_w, y2 + uy * half_len + py * half_w)
    c4 = (x2 + ux * half_len - px * half_w, y2 + uy * half_len - py * half_w)
    draw.polygon([c1, c2, c3, c4], fill=rgba)


def paint_field_particles(
    rng: np.random.Generator,
    w: int,
    h: int,
    palette: Palette,
    *,
    brush: str,
) -> Image.Image:
    """Layered particles in a Perlin-like flow field with configurable brush."""

    # Smooth flow field
    ang = fbm(rng, w, h, base_grid=170, octaves=6)
    ang2 = fbm(rng, w, h, base_grid=55, octaves=5)
    angle = (ang * 2.0 - 1.0) * math.pi * (1.1 + 1.3 * ang2)
    u = np.cos(angle).astype(np.float32)
    v = np.sin(angle).astype(np.float32)

    # Background (slightly textured)
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    grad_line = lerp(np.array(palette.bg, dtype=np.float32), np.array(palette.a, dtype=np.float32), (y**1.4)[..., None])
    bg = np.repeat(grad_line, w, axis=1)
    bg = clamp01(bg + rng.normal(0.0, 0.012, size=(h, w, 3)).astype(np.float32))
    base = Image.fromarray(to_uint8(bg), mode="RGB").convert("RGBA")
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    # Golden-ratio colors per layer
    layer_colors = golden_ratio_palette(rng, n=9)

    layers = 9
    particles_per_layer = int((w * h) / 28000) + 260  # ~330 for 1080p
    steps = 170

    for li in range(layers):
        col = layer_colors[li % len(layer_colors)]
        base_rgb = (int(255 * col[0]), int(255 * col[1]), int(255 * col[2]))

        # Spawn bias: each layer favors a different region (composition)
        bx = float(rng.uniform(0.05, 0.95))
        by = float(rng.uniform(0.10, 0.90))
        sx = w * bx
        sy = h * by
        sr = min(w, h) * float(rng.uniform(0.08, 0.20))

        theta = rng.random(particles_per_layer, dtype=np.float32) * (2.0 * math.pi)
        rad = (rng.random(particles_per_layer, dtype=np.float32) ** 0.7) * sr
        px = (sx + rad * np.cos(theta)).astype(np.float32)
        py = (sy + rad * np.sin(theta)).astype(np.float32)

        width0 = float(rng.uniform(1.0, 3.4))
        alpha0 = int(rng.integers(10, 26))

        for si in range(steps):
            t = si / max(1, steps - 1)
            # Fade to white + thinner ("flame/comet" feel)
            fade = (t**1.4)
            rgb = (
                int(base_rgb[0] * (1.0 - 0.55 * fade) + 255 * 0.55 * fade),
                int(base_rgb[1] * (1.0 - 0.55 * fade) + 255 * 0.55 * fade),
                int(base_rgb[2] * (1.0 - 0.55 * fade) + 255 * 0.55 * fade),
            )
            alpha = int(alpha0 * (1.0 - 0.75 * t))
            width = width0 * (1.0 - 0.70 * t)

            x1 = px.copy()
            y1 = py.copy()

            xi = np.mod(px.astype(np.int32), w)
            yi = np.mod(py.astype(np.int32), h)
            fx = u[yi, xi]
            fy = v[yi, xi]

            # Move: strong advection + slight diffusion
            px = (px + fx * 3.2 + rng.normal(0.0, 0.22, size=particles_per_layer).astype(np.float32))
            py = (py + fy * 2.6 + rng.normal(0.0, 0.22, size=particles_per_layer).astype(np.float32))

            # Wrap edges
            px = np.mod(px, w).astype(np.float32)
            py = np.mod(py, h).astype(np.float32)

            rgba = (rgb[0], rgb[1], rgb[2], max(0, min(255, alpha)))

            # Draw a subset each step for speed, but keep density via many steps
            stride = 2
            for k in range(0, particles_per_layer, stride):
                _draw_brush(
                    draw,
                    brush,
                    float(x1[k]),
                    float(y1[k]),
                    float(px[k]),
                    float(py[k]),
                    rgba,
                    width,
                    rng,
                )

    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.6))
    out = Image.alpha_composite(base, layer).convert("RGB")
    return out


def paint_confetti(
    rng: np.random.Generator,
    w: int,
    h: int,
    *,
    count_div: float = 520.0,
    length_min_frac: float = 0.020,
    length_max_frac: float = 0.160,
) -> Image.Image:
    """Dense, flat-color curved ribbons (boomerang/leaf confetti)."""

    def quad_bezier(p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float], t: float) -> tuple[float, float]:
        omt = 1.0 - t
        x = omt * omt * p0[0] + 2.0 * omt * t * p1[0] + t * t * p2[0]
        y = omt * omt * p0[1] + 2.0 * omt * t * p1[1] + t * t * p2[1]
        return x, y

    def quad_bezier_deriv(
        p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float], t: float
    ) -> tuple[float, float]:
        # d/dt of quadratic Bezier
        x = 2.0 * (1.0 - t) * (p1[0] - p0[0]) + 2.0 * t * (p2[0] - p1[0])
        y = 2.0 * (1.0 - t) * (p1[1] - p0[1]) + 2.0 * t * (p2[1] - p1[1])
        return x, y

    # Oversample for smoother edges, then downsample.
    scale = 2
    W = w * scale
    H = h * scale

    # Pale background (aqua-ish)
    bg_h = float(rng.random())
    bg = hsv(bg_h + 0.52, 0.16, 0.98)
    im = Image.new("RGB", (W, H), (int(bg[0] * 255), int(bg[1] * 255), int(bg[2] * 255)))
    draw = ImageDraw.Draw(im)

    # Bright flat colors
    colors = golden_ratio_palette(rng, n=96)
    rgb_colors = [(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)) for c in colors]

    area = W * H
    count = int(area / max(1.0, float(count_div)))
    count = max(900, min(7500, count))

    size_min = min(W, H)
    Lmin = float(length_min_frac) * size_min
    Lmax = float(length_max_frac) * size_min

    shapes: list[tuple[float, tuple[float, float, float, float, float, float, int]]] = []
    # params: (cx, cy, length, thick, curvature, angle, color_idx)
    for _ in range(count):
        cx = float(rng.uniform(-0.05 * W, 1.05 * W))
        cy = float(rng.uniform(-0.05 * H, 1.05 * H))
        u = float(rng.random())
        length = Lmin * math.exp((u**1.9) * math.log(Lmax / Lmin))
        thick = length * float(rng.uniform(0.18, 0.44))
        curvature = float(rng.uniform(-0.95, 0.95))
        angle = float(rng.uniform(0.0, 2.0 * math.pi))
        color_idx = int(rng.integers(0, len(rgb_colors)))
        shapes.append((length, (cx, cy, length, thick, curvature, angle, color_idx)))

    # Draw large first, then smaller to fill gaps
    shapes.sort(key=lambda x: x[0], reverse=True)

    samples = 18
    for _, (cx, cy, length, thick, curvature, angle, color_idx) in shapes:
        p0 = (-0.5 * length, 0.0)
        p2 = (0.5 * length, 0.0)
        p1 = (0.0, curvature * length * 0.85)

        ca = math.cos(angle)
        sa = math.sin(angle)

        left: list[tuple[float, float]] = []
        right: list[tuple[float, float]] = []
        for i in range(samples + 1):
            t = i / samples
            x, y = quad_bezier(p0, p1, p2, t)
            dx, dy = quad_bezier_deriv(p0, p1, p2, t)
            mag = math.hypot(dx, dy)
            if mag < 1e-6:
                continue
            nx = -dy / mag
            ny = dx / mag

            # Leaf-like thickness (fatter mid) with slight randomness
            prof = math.sin(math.pi * t)
            prof = max(0.0, prof) ** 0.75
            t_w = thick * (0.28 + 0.72 * prof) * float(rng.uniform(0.92, 1.08))

            lx = x + nx * t_w
            ly = y + ny * t_w
            rx = x - nx * t_w
            ry = y - ny * t_w

            # Rotate + translate
            lxr = lx * ca - ly * sa + cx
            lyr = lx * sa + ly * ca + cy
            rxr = rx * ca - ry * sa + cx
            ryr = rx * sa + ry * ca + cy
            left.append((lxr, lyr))
            right.append((rxr, ryr))

        if len(left) < 3 or len(right) < 3:
            continue

        poly = left + right[::-1]
        draw.polygon(poly, fill=rgb_colors[color_idx])

    if scale != 1:
        im = im.resize((w, h), resample=Image.Resampling.LANCZOS)
    return im


def paint_confetti_chunky(rng: np.random.Generator, w: int, h: int) -> Image.Image:
    """Fewer, bigger pieces than `confetti` (chunkier look)."""
    return paint_confetti(
        rng,
        w,
        h,
        count_div=1400.0,
        length_min_frac=0.045,
        length_max_frac=0.280,
    )


def paint_marbled_ribbons(rng: np.random.Generator, w: int, h: int) -> Image.Image:
    """Marbled rainbow ribbons: warped stripes + contour lines + subtle hatch texture."""

    # Coordinate grid
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    X = (xx / max(1, w - 1) - 0.5) * 2.0
    Y = (yy / max(1, h - 1) - 0.5) * 2.0

    # Smooth warps
    n1 = fbm(rng, w, h, base_grid=240, octaves=6)
    n2 = fbm(rng, w, h, base_grid=120, octaves=6)
    n3 = fbm(rng, w, h, base_grid=70, octaves=5)

    # Flow-ish angle field to give a marbled direction
    ang = (fbm(rng, w, h, base_grid=180, octaves=5) * 2.0 - 1.0) * math.pi
    ca = np.cos(ang).astype(np.float32)
    sa = np.sin(ang).astype(np.float32)

    warp = 0.55 + 0.50 * n2
    dx = (n1 * 2.0 - 1.0) * warp
    dy = (n2 * 2.0 - 1.0) * warp
    # rotate displacement by angle field
    Xw = X + (dx * ca - dy * sa) * 0.85
    Yw = Y + (dx * sa + dy * ca) * 0.85

    # Stripe coordinate: a blend of axes + extra wobble
    freq = 6.0 + 7.0 * float(rng.random())
    t = (
        Xw * freq
        + 0.65 * Yw * (freq * 0.65)
        + 1.55 * np.sin(Yw * (2.5 + 2.0 * n3))
        + (n3 - 0.5) * 3.6
    )
    # Extra local warp
    t = t + (fbm(rng, w, h, base_grid=45, octaves=4) - 0.5) * 1.8

    # Rainbow mapping
    phase = float(rng.random())
    hue = phase + 0.14 * t + 0.20 * (n1 - 0.5)
    sat = 0.90 + 0.10 * (n2 - 0.5)
    val = 0.92 + 0.10 * (n3 - 0.5)
    rgb = hsv_to_rgb_np(hue, sat, val)

    # Contour lines between bands
    bands = 18.0 + 10.0 * float(rng.random())
    band_pos = np.mod(t * bands, 1.0)
    dist = np.abs(band_pos - 0.5)
    line = np.exp(-((dist / 0.05) ** 2)).astype(np.float32)
    rgb = clamp01(rgb * (1.0 - 0.24 * line[..., None]))

    # Hatch texture (two rotated sine patterns) modulated by noise
    g = fbm(rng, w, h, base_grid=28, octaves=3)
    a1 = float(rng.uniform(0.3, 1.4))
    a2 = a1 + float(rng.uniform(0.9, 1.6))
    f1 = 40.0 + 25.0 * float(rng.random())
    f2 = 58.0 + 28.0 * float(rng.random())
    p1 = np.sin((Xw * math.cos(a1) + Yw * math.sin(a1)) * f1 * math.pi)
    p2 = np.sin((Xw * math.cos(a2) + Yw * math.sin(a2)) * f2 * math.pi)
    hatch = (np.abs(p1) < 0.08).astype(np.float32) + (np.abs(p2) < 0.07).astype(np.float32)
    hatch = clamp01(hatch * (0.25 + 0.85 * (g**1.1))).astype(np.float32)
    rgb = clamp01(rgb * (1.0 - 0.10 * hatch[..., None]))

    # Subtle grain
    grain = rng.normal(0.0, 0.018, size=(h, w, 3)).astype(np.float32)
    rgb = clamp01(rgb + grain)

    im = Image.fromarray(to_uint8(rgb), mode="RGB")
    im = im.filter(ImageFilter.GaussianBlur(radius=0.35))
    return im


def paint_neon_currents(rng: np.random.Generator, w: int, h: int, palette: Palette) -> Image.Image:
    """Dark flow-field hairlines with neon highlight rivers (additive glow)."""

    # Flow field
    ang = fbm(rng, w, h, base_grid=190, octaves=6)
    ang2 = fbm(rng, w, h, base_grid=70, octaves=5)
    angle = (ang * 2.0 - 1.0) * math.pi * (0.9 + 1.6 * ang2)
    u = np.cos(angle).astype(np.float32)
    v = np.sin(angle).astype(np.float32)

    # Dark background gradient
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    bg_line = lerp(
        np.array(palette.bg, dtype=np.float32),
        np.array(palette.a, dtype=np.float32),
        (y**1.25)[..., None],
    )
    bg = np.repeat(bg_line, w, axis=1)
    bg = clamp01(bg + rng.normal(0.0, 0.006, size=(h, w, 3)).astype(np.float32))

    # Hairline layer
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    area = w * h
    layers = 6
    particles = max(700, min(2400, int(area / 1100)))
    steps = 240
    stride = 3
    speed = 2.4
    jitter = 0.18

    # Base colors: deep violet/blue hairs
    base_cols = [
        hsv(0.69, 0.65, 0.35),
        hsv(0.62, 0.75, 0.42),
        hsv(0.78, 0.55, 0.32),
    ]

    for li in range(layers):
        col = base_cols[li % len(base_cols)]
        rgb = (int(col[0] * 255), int(col[1] * 255), int(col[2] * 255))
        alpha = int(rng.integers(10, 18))

        px = rng.random(particles, dtype=np.float32) * w
        py = rng.random(particles, dtype=np.float32) * h

        for _ in range(steps):
            x1 = px.copy()
            y1 = py.copy()

            xi = np.mod(px.astype(np.int32), w)
            yi = np.mod(py.astype(np.int32), h)
            fx = u[yi, xi]
            fy = v[yi, xi]

            px = px + fx * speed + rng.normal(0.0, jitter, size=particles).astype(np.float32)
            py = py + fy * speed + rng.normal(0.0, jitter, size=particles).astype(np.float32)
            px = np.mod(px, w).astype(np.float32)
            py = np.mod(py, h).astype(np.float32)

            rgba = (rgb[0], rgb[1], rgb[2], alpha)
            for k in range(0, particles, stride):
                draw.line((float(x1[k]), float(y1[k]), float(px[k]), float(py[k])), fill=rgba, width=1)

    # Neon river highlights (few thick, bright streaks)
    hi = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hi_draw = ImageDraw.Draw(hi, "RGBA")
    river_cols = [hsv(0.93, 0.90, 0.98), hsv(0.86, 0.80, 0.90), hsv(0.97, 0.65, 0.98)]
    river_rgb = [(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)) for c in river_cols]

    river_sets = 3
    river_particles = max(260, min(900, int(area / 5200)))
    river_steps = 320
    river_stride = 2
    river_speed = 2.9
    river_jitter = 0.10

    for si in range(river_sets):
        y0 = float(rng.uniform(0.25, 0.75)) * h
        amp = float(rng.uniform(0.06, 0.16)) * h
        freq = float(rng.uniform(0.8, 1.7))
        phase = float(rng.uniform(0.0, 2.0 * math.pi))

        t = rng.random(river_particles, dtype=np.float32)
        px = (t * 1.2 - 0.1).astype(np.float32) * w
        py = (y0 + amp * np.sin((t * freq * 2.0 * math.pi) + phase)).astype(np.float32)
        px = px + rng.normal(0.0, 0.020 * w, size=river_particles).astype(np.float32)
        py = py + rng.normal(0.0, 0.025 * h, size=river_particles).astype(np.float32)
        px = np.mod(px, w).astype(np.float32)
        py = np.mod(py, h).astype(np.float32)

        col = river_rgb[si % len(river_rgb)]
        width0 = float(rng.uniform(2.0, 4.0))
        alpha0 = int(rng.integers(28, 52))

        for step_i in range(river_steps):
            x1 = px.copy()
            y1 = py.copy()

            xi = np.mod(px.astype(np.int32), w)
            yi = np.mod(py.astype(np.int32), h)
            fx = u[yi, xi]
            fy = v[yi, xi]

            px = px + fx * river_speed + rng.normal(0.0, river_jitter, size=river_particles).astype(np.float32)
            py = py + fy * river_speed + rng.normal(0.0, river_jitter, size=river_particles).astype(np.float32)
            px = np.mod(px, w).astype(np.float32)
            py = np.mod(py, h).astype(np.float32)

            tlife = step_i / max(1, river_steps - 1)
            width = max(1.0, width0 * (1.0 - 0.70 * tlife))
            alpha = int(alpha0 * (1.0 - 0.60 * tlife))
            rgba = (col[0], col[1], col[2], alpha)
            w_int = max(1, int(round(width)))
            for k in range(0, river_particles, river_stride):
                hi_draw.line((float(x1[k]), float(y1[k]), float(px[k]), float(py[k])), fill=rgba, width=w_int)

    # Additive composite: bg + hair + glow(hi)
    hair = np.asarray(layer.convert("RGBA"), dtype=np.float32) / 255.0
    hil = np.asarray(hi.convert("RGBA"), dtype=np.float32) / 255.0
    glow = np.asarray(hi.filter(ImageFilter.GaussianBlur(radius=4.0)).convert("RGBA"), dtype=np.float32) / 255.0

    out = bg.copy()
    out += hair[..., :3] * hair[..., 3:4] * 1.10
    out += hil[..., :3] * hil[..., 3:4] * 1.25
    out += glow[..., :3] * glow[..., 3:4] * 2.10

    # Gentle vignette
    xv = (np.linspace(-1, 1, w, dtype=np.float32)[None, :])
    yv = (np.linspace(-1, 1, h, dtype=np.float32)[:, None])
    r2 = xv * xv + yv * yv
    vig = np.clip(1.0 - 0.30 * (r2**0.85), 0.55, 1.0)
    out *= vig[..., None]

    out = clamp01(out)
    im = Image.fromarray(to_uint8(out), mode="RGB")
    im = im.filter(ImageFilter.GaussianBlur(radius=0.35))
    return im


def paint_reaction_diffusion(rng: np.random.Generator, w: int, h: int, palette: Palette) -> Image.Image:
    """Gray-Scott reaction–diffusion with spatially biased feed/kill (noise-modulated)."""

    # Simulate on a smaller grid, then upscale.
    scale = 4 if max(w, h) >= 1600 else (3 if max(w, h) >= 1000 else 2)
    gw = max(240, w // scale)
    gh = max(180, h // scale)

    # Fields
    u = np.ones((gh, gw), dtype=np.float32)
    v = np.zeros((gh, gw), dtype=np.float32)

    # Spatially varying parameters (Perlin-like bias)
    nF = fbm(rng, gw, gh, base_grid=90, octaves=5)
    nK = fbm(rng, gw, gh, base_grid=55, octaves=5)
    x = np.linspace(0, 1, gw, dtype=np.float32)[None, :]
    y = np.linspace(0, 1, gh, dtype=np.float32)[:, None]
    # Bias: more activity near a diagonal band
    diag = np.exp(-(((x - (0.25 + 0.55 * y)) / 0.18) ** 2)).astype(np.float32)

    F = 0.030 + 0.020 * (nF - 0.5) + 0.010 * diag
    K = 0.055 + 0.020 * (nK - 0.5) + 0.006 * (1.0 - y)
    F = np.clip(F, 0.010, 0.080).astype(np.float32)
    K = np.clip(K, 0.030, 0.090).astype(np.float32)

    # Seed V in a biased region + droplets
    cx = float(rng.uniform(0.20, 0.55)) * gw
    cy = float(rng.uniform(0.35, 0.75)) * gh
    rr = float(rng.uniform(0.055, 0.090)) * min(gw, gh)
    yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
    mask = ((xx - cx) ** 2 + (yy - cy) ** 2) <= rr * rr
    v[mask] = 1.0
    u[mask] = 0.0

    for _ in range(int(rng.integers(5, 10))):
        dx = float(rng.uniform(0.05, 0.95)) * gw
        dy = float(rng.uniform(0.05, 0.95)) * gh
        r2 = float(rng.uniform(0.010, 0.028)) * min(gw, gh)
        m = ((xx - dx) ** 2 + (yy - dy) ** 2) <= r2 * r2
        v[m] = np.maximum(v[m], 1.0)
        u[m] = np.minimum(u[m], 0.0)

    Du = 0.16
    Dv = 0.08
    dt = 1.0

    cells = gw * gh
    steps = 1200 if cells <= 150_000 else (900 if cells <= 260_000 else 700)

    def lap(a: np.ndarray) -> np.ndarray:
        n = np.roll(a, -1, axis=0)
        s = np.roll(a, 1, axis=0)
        e = np.roll(a, -1, axis=1)
        w_ = np.roll(a, 1, axis=1)
        ne = np.roll(n, -1, axis=1)
        nw = np.roll(n, 1, axis=1)
        se = np.roll(s, -1, axis=1)
        sw = np.roll(s, 1, axis=1)
        return (-a + 0.20 * (n + s + e + w_) + 0.05 * (ne + nw + se + sw)).astype(np.float32)

    for _ in range(steps):
        lu = lap(u)
        lv = lap(v)
        uvv = u * v * v
        u = u + (Du * lu - uvv + F * (1.0 - u)) * dt
        v = v + (Dv * lv + uvv - (F + K) * v) * dt
        u = np.clip(u, 0.0, 1.0)
        v = np.clip(v, 0.0, 1.0)

    # Normalize V robustly
    lo = float(np.quantile(v, 0.02))
    hi = float(np.quantile(v, 0.98))
    v01 = np.clip((v - lo) / max(1e-6, (hi - lo)), 0.0, 1.0).astype(np.float32)

    # Edge emphasis
    edge = np.abs(np.roll(v01, -1, axis=0) - v01) + np.abs(np.roll(v01, -1, axis=1) - v01)
    edge = np.clip(edge * 3.6, 0.0, 1.0).astype(np.float32)

    bg = np.array(palette.bg, dtype=np.float32)
    a = np.array(palette.a, dtype=np.float32)
    b = np.array(palette.b, dtype=np.float32)
    c = np.array(palette.c, dtype=np.float32)

    t = v01**0.70
    rgb = lerp(bg, a, (0.25 + 0.55 * (1.0 - t))[..., None])
    rgb = lerp(rgb, b, t[..., None])
    rgb = lerp(rgb, c, (t**2.2)[..., None] * 0.75)
    rgb *= (1.0 - 0.30 * edge[..., None])
    rgb = clamp01(rgb)

    im = Image.fromarray(to_uint8(rgb), mode="RGB")
    im = im.resize((w, h), resample=Image.Resampling.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(radius=0.45))
    return im


def paint_topo_contours(rng: np.random.Generator, w: int, h: int, palette: Palette) -> Image.Image:
    """Topographic contour map from warped fBm with slope shading."""

    n1 = fbm(rng, w, h, base_grid=420, octaves=6)
    n2 = fbm(rng, w, h, base_grid=140, octaves=6)
    n3 = fbm(rng, w, h, base_grid=55, octaves=5)
    w1 = fbm(rng, w, h, base_grid=85, octaves=4)

    z = 0.55 * n1 + 0.35 * n2 + 0.10 * (n3**1.35)
    z = z + 0.22 * (w1 - 0.5) + 0.12 * np.sin((w1 - 0.5) * math.pi * 4.0 + n2 * math.pi * 2.0)

    # Bias: tilt terrain to create compositional asymmetry
    x = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    z = z + (x - 0.5) * float(rng.uniform(-0.28, 0.28))

    z = (z - float(z.min())) / max(1e-6, float(z.max() - z.min()))
    z = z.astype(np.float32)

    # Slope shading
    zx = np.roll(z, -1, axis=1) - np.roll(z, 1, axis=1)
    zy = np.roll(z, -1, axis=0) - np.roll(z, 1, axis=0)
    slope = np.clip(np.sqrt(zx * zx + zy * zy) * 2.4, 0.0, 1.0).astype(np.float32)
    shade = (1.0 - 0.55 * slope).astype(np.float32)

    # Contours
    levels = 22.0 + 10.0 * float(rng.random())
    band = np.mod(z * levels, 1.0)
    dist = np.abs(band - 0.5)
    line = np.exp(-((dist / 0.055) ** 2)).astype(np.float32)

    bg = np.array(palette.bg, dtype=np.float32)
    a = np.array(palette.a, dtype=np.float32)
    b = np.array(palette.b, dtype=np.float32)
    c = np.array(palette.c, dtype=np.float32)

    t = smoothstep((z**1.10)[..., None])
    rgb = lerp(bg, a, t)
    rgb = lerp(rgb, b, smoothstep(((z - 0.35) / 0.45).clip(0, 1))[..., None])
    rgb = lerp(rgb, c, smoothstep(((z - 0.78) / 0.22).clip(0, 1))[..., None] * 0.85)

    rgb *= shade[..., None]
    rgb *= (1.0 - 0.22 * line[..., None])

    # Paper grain
    rgb = clamp01(rgb + rng.normal(0.0, 0.010, size=(h, w, 3)).astype(np.float32))

    im = Image.fromarray(to_uint8(rgb), mode="RGB")
    im = im.filter(ImageFilter.GaussianBlur(radius=0.30))
    return im


def paint_kaleido_noise(rng: np.random.Generator, w: int, h: int, palette: Palette) -> Image.Image:
    """Kaleidoscopic remap of a Perlin-like color field (symmetry + noise warp)."""

    n1 = fbm(rng, w, h, base_grid=260, octaves=6)
    n2 = fbm(rng, w, h, base_grid=85, octaves=5)
    phase = float(rng.random())

    hue = phase + 0.80 * n1 + 0.30 * (n2 - 0.5)
    sat = 0.82 + 0.16 * (n2 - 0.5)
    val = 0.82 + 0.25 * (n1 - 0.5)
    base = hsv_to_rgb_np(hue.astype(np.float32), sat.astype(np.float32), val.astype(np.float32))

    # Kaleidoscope mapping
    cy = (h - 1) * 0.5
    cx = (w - 1) * 0.5
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = xx - cx
    dy = yy - cy
    r = np.sqrt(dx * dx + dy * dy)
    ang = np.arctan2(dy, dx)
    ang = np.mod(ang + 2.0 * math.pi, 2.0 * math.pi)

    k = int(rng.integers(6, 13))
    wedge = (2.0 * math.pi) / float(k)
    a = np.mod(ang, wedge)
    a = np.where(a > wedge * 0.5, wedge - a, a)  # fold
    rot = float(rng.uniform(0.0, wedge))

    # Radial warp from noise
    rw = r * (1.0 + 0.12 * (n2 - 0.5))
    xm = cx + rw * np.cos(a + rot)
    ym = cy + rw * np.sin(a + rot)

    xi = np.clip(xm.astype(np.int32), 0, w - 1)
    yi = np.clip(ym.astype(np.int32), 0, h - 1)
    rgb = base[yi, xi]

    # Light contour to emphasize symmetry
    edge = np.abs(np.roll(n1, -1, axis=0) - n1) + np.abs(np.roll(n1, -1, axis=1) - n1)
    edge = np.clip(edge * 2.5, 0.0, 1.0).astype(np.float32)
    rgb = clamp01(rgb * (1.0 - 0.10 * edge[..., None]))

    # Subtle background tint toward palette.bg
    tint = np.array(palette.bg, dtype=np.float32)
    rgb = lerp(rgb, tint, (0.10 + 0.10 * (1.0 - n2))[..., None])
    rgb = clamp01(rgb)

    im = Image.fromarray(to_uint8(rgb), mode="RGB")
    im = im.filter(ImageFilter.GaussianBlur(radius=0.25))
    return im


def _grade_pro(img: Image.Image, rng: np.random.Generator, *, bloom: bool) -> Image.Image:
    arr = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    h, w, _ = arr.shape

    # Filmic-ish highlight compression
    arr = arr / (arr + 0.38)
    arr = clamp01(arr)

    # Gentle S-curve contrast
    arr = lerp(arr, smoothstep(arr), np.array(0.55, dtype=np.float32))

    # Slight saturation boost (luma-based)
    luma = arr[..., 0] * 0.2126 + arr[..., 1] * 0.7152 + arr[..., 2] * 0.0722
    sat = 1.10
    arr = luma[..., None] + (arr - luma[..., None]) * sat
    arr = clamp01(arr)

    if bloom:
        bright = np.clip(arr - 0.72, 0.0, 1.0)
        bright_img = Image.fromarray(to_uint8(bright), mode="RGB").filter(ImageFilter.GaussianBlur(radius=7.0))
        bright_arr = np.asarray(bright_img, dtype=np.float32) / 255.0
        arr = clamp01(arr + bright_arr * 0.22)

    # Subtle vignette
    xv = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    yv = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    r2 = xv * xv + yv * yv
    vig = np.clip(1.0 - 0.16 * (r2**0.75), 0.78, 1.0)
    arr *= vig[..., None]

    # Fine grain
    arr = clamp01(arr + rng.normal(0.0, 0.0075, size=arr.shape).astype(np.float32))

    # Unsharp mask (small)
    base = Image.fromarray(to_uint8(arr), mode="RGB")
    blur = base.filter(ImageFilter.GaussianBlur(radius=1.25))
    base_arr = np.asarray(base, dtype=np.float32) / 255.0
    blur_arr = np.asarray(blur, dtype=np.float32) / 255.0
    arr = clamp01(base_arr + (base_arr - blur_arr) * 0.55)

    return Image.fromarray(to_uint8(arr), mode="RGB")


def apply_grade(img: Image.Image, *, style: str, seed: int, grade: str) -> Image.Image:
    grade = grade.lower()
    if grade in {"none", "off", "0"}:
        return img

    if grade != "pro":
        raise ValueError(f"Unknown grade: {grade}")

    # Deterministic grade RNG that doesn't depend on style internals
    grade_seed = (int(seed) ^ 0xC0FFEE) & 0xFFFFFFFF
    rng = make_rng(grade_seed)
    bloom = style.lower() in {"neon_currents"}
    return _grade_pro(img, rng, bloom=bloom)


def paint_style_grid(
    seed: int,
    size: tuple[int, int],
    *,
    brush: str,
    grade: str,
) -> Image.Image:
    """Compose a multi-style collage image in a 3x2 grid."""

    w, h = size
    cols, rows = 3, 2

    margin = max(10, int(min(w, h) * 0.015))
    gap = max(6, int(min(w, h) * 0.010))

    inner_w = w - 2 * margin - (cols - 1) * gap
    inner_h = h - 2 * margin - (rows - 1) * gap
    tile_w = max(40, inner_w // cols)
    tile_h = max(40, inner_h // rows)

    styles = [
        "kaleido_noise",
        "reaction_diffusion",
        "confetti",
        "marbled_ribbons",
        "topo_contours",
        "neon_currents",
    ]
    vibes = {
        "kaleido_noise": "colorful",
        "reaction_diffusion": "storm",
        "confetti": "colorful",
        "marbled_ribbons": "colorful",
        "topo_contours": "desert",
        "neon_currents": "night",
    }

    canvas = Image.new("RGB", (w, h), (245, 245, 245))
    draw = ImageDraw.Draw(canvas)
    label_font = ImageFont.load_default()

    for idx, style_name in enumerate(styles):
        r = idx // cols
        c = idx % cols
        x = margin + c * (tile_w + gap)
        y = margin + r * (tile_h + gap)

        tile_seed = int(seed + 37 * (idx + 1))
        tile = generate(
            style_name,
            tile_seed,
            (tile_w, tile_h),
            vibes.get(style_name, "auto"),
            brush=brush,
            grade=grade,
        )
        canvas.paste(tile, (x, y))

        label = style_name.replace("_", " ")
        tb = draw.textbbox((0, 0), label, font=label_font)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
        pad = 5

        lx0 = x + 6
        ly0 = y + tile_h - th - pad * 2 - 6
        lx1 = lx0 + tw + pad * 2
        ly1 = ly0 + th + pad * 2
        draw.rectangle((lx0, ly0, lx1, ly1), fill=(0, 0, 0))
        draw.text((lx0 + pad, ly0 + pad), label, font=label_font, fill=(255, 255, 255))

    return canvas


def generate(
    style: str,
    seed: int,
    size: tuple[int, int],
    vibe: str,
    *,
    brush: str = "rect",
    grade: str = "none",
) -> Image.Image:
    w, h = size
    style = style.lower()

    if style == "style_grid":
        return paint_style_grid(seed, size, brush=brush, grade=grade)

    rng = make_rng(seed)
    if vibe == "auto":
        vibe = {
            "starry": "night",
            "dunes": "desert",
            "aurora": "storm",
            "reaction_diffusion": "storm",
            "topo_contours": "desert",
            "kaleido_noise": "colorful",
            "style_grid": "colorful",
        }.get(style, "night")
    pal = choose_palette(rng, vibe)

    if style == "starry":
        img = paint_starry(rng, w, h, pal)
    elif style == "dunes":
        img = paint_dunes(rng, w, h, pal)
    elif style == "aurora":
        img = paint_aurora(rng, w, h, pal)
    elif style == "diffuse_flow":
        img = paint_diffuse_flow(rng, w, h, pal)
    elif style == "flow_lines":
        img = paint_flow_lines(rng, w, h, pal)
    elif style == "noisy_circles":
        img = paint_noisy_circles(rng, w, h, pal)
    elif style == "field_particles":
        img = paint_field_particles(rng, w, h, pal, brush=brush)
    elif style == "confetti":
        img = paint_confetti(rng, w, h)
    elif style == "confetti_chunky":
        img = paint_confetti_chunky(rng, w, h)
    elif style == "marbled_ribbons":
        img = paint_marbled_ribbons(rng, w, h)
    elif style == "neon_currents":
        img = paint_neon_currents(rng, w, h, pal)
    elif style == "reaction_diffusion":
        img = paint_reaction_diffusion(rng, w, h, pal)
    elif style == "topo_contours":
        img = paint_topo_contours(rng, w, h, pal)
    elif style == "kaleido_noise":
        img = paint_kaleido_noise(rng, w, h, pal)
    else:
        raise ValueError(f"Unknown style: {style}")

    return apply_grade(img, style=style, seed=seed, grade=grade)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--style",
        choices=[
            "starry",
            "dunes",
            "aurora",
            "diffuse_flow",
            "flow_lines",
            "noisy_circles",
            "field_particles",
            "confetti",
            "confetti_chunky",
            "marbled_ribbons",
            "neon_currents",
            "reaction_diffusion",
            "topo_contours",
            "kaleido_noise",
            "style_grid",
        ],
        required=True,
    )
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--size", type=parse_size, default=parse_size("1920x1080"))
    parser.add_argument("--vibe", type=str, default="auto", help="night|desert|storm|colorful|auto")
    parser.add_argument(
        "--grade",
        type=str,
        default="none",
        choices=["none", "pro"],
        help="Optional post-processing for a more polished look",
    )
    parser.add_argument(
        "--brush",
        type=str,
        default="rect",
        choices=["rect", "line", "dot", "arc", "tri", "perp"],
        help="Used only when --style field_particles",
    )
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args()

    img = generate(args.style, args.seed, args.size, args.vibe, brush=args.brush, grade=args.grade)

    args.out.mkdir(parents=True, exist_ok=True)
    vibe_tag = args.vibe.lower().replace(" ", "_")
    grade_tag = "" if args.grade == "none" else f"_{args.grade}"
    extra = f"_{args.brush}" if args.style == "field_particles" else ""
    out_path = args.out / f"{args.style}{extra}_{vibe_tag}{grade_tag}_seed{args.seed}_{args.size[0]}x{args.size[1]}.png"
    img.save(out_path)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
