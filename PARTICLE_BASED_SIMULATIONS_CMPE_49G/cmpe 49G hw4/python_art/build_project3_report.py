r"""Build the CMPE49G Project 3 PDF report.

Creates:
- 2 intro pages (generative art + Perlin noise/flow field/diffusion/bias)
- 1 page per artwork (image + fancy name + short story)

Usage (PowerShell):
  & .\.venv\Scripts\python.exe python_art\build_project3_report.py --student-id 123456 --name John --surname Doe

Output:
  <stuID>_prj3_<name>_<surname>.pdf

Notes:
- This script uses only Pillow (no extra PDF deps).
- It expects the art images to exist in ./out. If missing, it will try to generate them.
"""

from __future__ import annotations

import argparse
import textwrap
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


A4_W = 1654  # ~A4 @ 200 DPI
A4_H = 2339


@dataclass(frozen=True)
class ArtPiece:
    title: str
    subtitle: str
    story: str
    image_path: Path
    generate_args: list[str]


def _load_font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    # Windows font fallback order
    candidates = []
    if bold:
        candidates += [
            Path("C:/Windows/Fonts/arialbd.ttf"),
            Path("C:/Windows/Fonts/calibrib.ttf"),
        ]
    candidates += [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
    ]

    for p in candidates:
        try:
            if p.exists():
                return ImageFont.truetype(str(p), size=size)
        except Exception:
            pass

    # Pillow default font
    return ImageFont.load_default()


def _wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            lines.append("")
            continue

        words = para.split()
        cur = ""
        for w in words:
            nxt = w if not cur else (cur + " " + w)
            w_box = draw.textbbox((0, 0), nxt, font=font)
            w_w = w_box[2] - w_box[0]
            if w_w <= max_width:
                cur = nxt
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    max_width: int,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    line_gap: int,
) -> int:
    for line in _wrap_lines(draw, text, font, max_width=max_width):
        if line == "":
            y += line_gap
            continue
        draw.text((x, y), line, font=font, fill=fill)
        y += (font.size + line_gap)
    return y


def _paste_scaled(page: Image.Image, img: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    bw = max(1, x1 - x0)
    bh = max(1, y1 - y0)

    iw, ih = img.size
    scale = min(bw / iw, bh / ih)
    nw = max(1, int(iw * scale))
    nh = max(1, int(ih * scale))
    resized = img.resize((nw, nh), resample=Image.Resampling.LANCZOS)

    px = x0 + (bw - nw) // 2
    py = y0 + (bh - nh) // 2
    page.paste(resized, (px, py))


def _intro_pages(student_line: str) -> list[Image.Image]:
    pages: list[Image.Image] = []

    title_font = _load_font(52, bold=True)
    h_font = _load_font(28, bold=True)
    p_font = _load_font(22)

    margin_x = 120
    top = 110
    body_w = A4_W - 2 * margin_x

    # Page 1
    p1 = Image.new("RGB", (A4_W, A4_H), (255, 255, 255))
    d1 = ImageDraw.Draw(p1)

    d1.text((margin_x, top), "CMPE49G Project 3", font=title_font, fill=(15, 15, 15))
    d1.text((margin_x, top + 62), "Generative Art with Diffusion, Flow Fields, and Perlin Noise", font=h_font, fill=(15, 15, 15))
    d1.text((margin_x, top + 110), student_line, font=p_font, fill=(30, 30, 30))

    y = top + 170
    d1.text((margin_x, y), "Introduction", font=h_font, fill=(15, 15, 15))
    y += 48

    intro = (
        "Generative art is artwork produced with the help of an autonomous system: an algorithm that "
        "independently makes some of the visual decisions. The artist designs rules, constraints, and parameters "
        "(including randomness), then lets the program synthesize the final composition."
        "\n\n"
        "Coherent noise functions such as Perlin-like noise are popular building blocks because they vary smoothly "
        "across space. Sampling noise at each pixel (or at each particle position) gives motion and texture that "
        "feels organic rather than purely random."
    )
    y = _draw_wrapped(d1, intro, margin_x, y, body_w, p_font, (25, 25, 25), line_gap=10)

    y += 20
    d1.text((margin_x, y), "Project Summary", font=h_font, fill=(15, 15, 15))
    y += 48

    bullets = [
        "Tools: Python (NumPy + Pillow) / Processing.",
        "Core mechanisms: diffusion (random walk), flow-field advection, reaction-diffusion, Perlin-like coherent noise (fBm), and a bias structure for composition.",
        "Output: a portfolio of algorithmically generated images (one per page).",
    ]
    for b in bullets:
        y = _draw_wrapped(d1, "• " + b, margin_x, y, body_w, p_font, (25, 25, 25), line_gap=8)
        y += 2

    pages.append(p1)

    # Page 2
    p2 = Image.new("RGB", (A4_W, A4_H), (255, 255, 255))
    d2 = ImageDraw.Draw(p2)

    d2.text((margin_x, top), "Method (Noise + Flow + Diffusion + Bias)", font=h_font, fill=(15, 15, 15))
    y = top + 60

    method = (
        "1) Perlin-like noise field: Build N(x,y) ∈ [0,1] using multi-octave coherent noise (fBm) to create detail at multiple scales.\n\n"
        "2) Flow field: Convert noise into an angle field θ(x,y) and a local velocity v = (cos θ, sin θ).\n\n"
        "3) Particle motion (advection + diffusion): p(t+1) = p(t) + s·v(p(t)) + σ·η, where η is Gaussian noise.\n\n"
        "4) Bias structure: Bias the initial particle distribution (or introduce a void/attractor region) so the composition develops a focal area instead of being uniform.\n\n"
        "Finally, multiple passes are layered with different parameters (opacity, speed, brush shape) to build depth and texture. "
        "All pieces are reproducible by seed; changing the seed yields a new image with the same style."
    )
    y = _draw_wrapped(d2, method, margin_x, y, body_w, p_font, (25, 25, 25), line_gap=10)

    note = (
        "Implementation note: In code we use a self-contained Perlin-like noise implementation (value-noise + fBm) "
        "to achieve the same key property needed for this project: spatially smooth, coherent randomness."
    )
    y += 18
    y = _draw_wrapped(d2, note, margin_x, y, body_w, p_font, (25, 25, 25), line_gap=10)

    pages.append(p2)
    return pages


def _portfolio_page(piece: ArtPiece) -> Image.Image:
    page = Image.new("RGB", (A4_W, A4_H), (255, 255, 255))
    d = ImageDraw.Draw(page)

    title_font = _load_font(46, bold=True)
    sub_font = _load_font(22)
    body_font = _load_font(22)

    margin_x = 120
    top = 110
    body_w = A4_W - 2 * margin_x

    d.text((margin_x, top), piece.title, font=title_font, fill=(15, 15, 15))
    d.text((margin_x, top + 62), piece.subtitle, font=sub_font, fill=(35, 35, 35))

    # Image box: ~60-65% of page height
    img_top = top + 120
    img_bottom = int(A4_H * 0.73)
    img_box = (margin_x, img_top, A4_W - margin_x, img_bottom)

    img = Image.open(piece.image_path).convert("RGB")
    _paste_scaled(page, img, img_box)

    # Slight soft border
    border = Image.new("RGB", page.size, (0, 0, 0))
    border_draw = ImageDraw.Draw(border)
    border_draw.rectangle(img_box, outline=(220, 220, 220), width=2)
    page = Image.blend(page, border, alpha=0.08)
    d = ImageDraw.Draw(page)

    y = img_bottom + 25
    y = _draw_wrapped(d, piece.story, margin_x, y, body_w, body_font, (25, 25, 25), line_gap=10)

    return page


def _run(cmd: list[str]) -> None:
    import subprocess

    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-id", default="STUID")
    parser.add_argument("--name", default="Name")
    parser.add_argument("--surname", default="Surname")
    parser.add_argument("--out-dir", type=Path, default=Path("."))
    parser.add_argument("--images-dir", type=Path, default=Path("out"))
    args = parser.parse_args()

    student_line = f"Student: {args.student_id} — {args.name} {args.surname}"

    # Pick 4 visuals (different styles)
    pieces: list[ArtPiece] = [
        ArtPiece(
            title="Cellular Tempest",
            subtitle="reaction_diffusion — Gray-Scott diffusion with noise-biased feed/kill",
            story=(
                "A compact chemical seed evolves into branching membranes and cellular fronts. "
                "Reaction and diffusion compete over time, while coherent-noise feed/kill maps bias where activity "
                "intensifies. The composition feels like turbulent weather observed at microscopic scale."
            ),
            image_path=Path("report_images/reaction_diffusion_storm_pro_seed89_1920x1080.png"),
            generate_args=[
                "--style",
                "reaction_diffusion",
                "--seed",
                "89",
                "--size",
                "1920x1080",
                "--vibe",
                "storm",
                "--grade",
                "pro",
            ],
        ),
        ArtPiece(
            title="Prismatic Mandala",
            subtitle="kaleido_noise — coherent-noise color field with kaleidoscopic remap",
            story=(
                "A smooth noise-based color field is folded with kaleidoscopic symmetry. "
                "Mirrored wedges preserve coherence while creating radial rhythm and contrast. "
                "The result feels like a stained-glass mandala generated from controlled randomness."
            ),
            image_path=Path("report_images/kaleido_noise_colorful_pro_seed74_1920x1080.png"),
            generate_args=[
                "--style",
                "kaleido_noise",
                "--seed",
                "74",
                "--size",
                "1920x1080",
                "--vibe",
                "colorful",
                "--grade",
                "pro",
            ],
        ),
        ArtPiece(
            title="Festival Drift",
            subtitle="confetti — dense curved ribbons with stochastic spacing and curvature",
            story=(
                "Thousands of curved fragments scatter across the canvas like a frozen celebration. "
                "Randomized length, thickness, and curvature create variation without losing visual balance. "
                "The composition blends playful chaos with controlled color harmony."
            ),
            image_path=Path("report_images/confetti_colorful_pro_seed712_1920x1080.png"),
            generate_args=[
                "--style",
                "confetti",
                "--seed",
                "712",
                "--size",
                "1920x1080",
                "--vibe",
                "colorful",
                "--grade",
                "pro",
            ],
        ),
        ArtPiece(
            title="Arc Nocturne",
            subtitle="field_particles — layered flow particles with arc brush and spawn bias",
            story=(
                "Multiple particle layers launch from different biased regions and travel in the same coherent vector "
                "field. Arc-shaped marks accumulate into curved luminous fragments, creating depth through overlap and "
                "density changes. The result reads like painted wind trajectories at night."
            ),
            image_path=args.images_dir / "field_particles_arc_night_pro_seed907_1920x1080.png",
            generate_args=[
                "--style",
                "field_particles",
                "--seed",
                "907",
                "--size",
                "1920x1080",
                "--vibe",
                "night",
                "--brush",
                "arc",
                "--grade",
                "pro",
            ],
        ),
    ]

    # Generate images if missing
    gen_script = Path(__file__).with_name("generate_paintings.py")
    py = Path(".venv/Scripts/python.exe")
    if not py.exists():
        py = None

    for p in pieces:
        if p.image_path.exists():
            continue
        if py is None:
            raise SystemExit(f"Missing venv python; cannot auto-generate {p.image_path}")
        p.image_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [str(py), str(gen_script)] + p.generate_args + ["--out", str(p.image_path.parent)]
        _run(cmd)

    pages = []
    pages += _intro_pages(student_line)
    for piece in pieces:
        pages.append(_portfolio_page(piece))

    out_name = f"{args.student_id}_prj3_{args.name}_{args.surname}.pdf"
    out_path = args.out_dir / out_name

    # Save PDF. Some Pillow builds can miss JPEG support; fall back to paletted pages.
    first = pages[0]
    rest = pages[1:]
    try:
        first.save(out_path, save_all=True, append_images=rest)
    except KeyError as exc:
        if str(exc).strip("'") != "JPEG":
            raise
        adaptive = getattr(getattr(Image, "Palette", object()), "ADAPTIVE", None)
        if adaptive is None:
            adaptive = getattr(Image, "ADAPTIVE", None)
        if adaptive is None:
            raise

        fallback_pages = [
            p.convert("P", palette=adaptive, colors=256) for p in pages
        ]
        fallback_pages[0].save(out_path, save_all=True, append_images=fallback_pages[1:])

    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
