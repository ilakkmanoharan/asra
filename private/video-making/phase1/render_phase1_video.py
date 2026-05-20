#!/usr/bin/env python3
"""
Render ASRA Phase 1 cinematic technical video (MP4) from slide spec.
Outputs to private/video-making/phase1/
"""

from __future__ import annotations

import json
import math
import subprocess
import textwrap
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, VideoClip, concatenate_videoclips

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT
BUILD_DIR = ROOT / "_build"
W, H = 1920, 1080
FPS = 24

BG = (8, 12, 22)
ACCENT = (79, 209, 197)
ACCENT2 = (124, 92, 255)
TEXT = (235, 240, 255)
MUTED = (140, 155, 180)
GRID_COLORS = [
    (20, 24, 36),
    (56, 189, 248),
    (244, 114, 182),
    (250, 204, 21),
    (74, 222, 128),
    (251, 146, 60),
]


@dataclass
class Slide:
    title: str
    bullets: List[str]
    narration: str
    painter: Callable[[Image.Image, float], None]  # image, t in [0,1]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


TITLE_FONT = load_font(64, bold=True)
HEAD_FONT = load_font(40, bold=True)
BODY_FONT = load_font(30)
SMALL_FONT = load_font(22)


def base_canvas() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    for i in range(0, W, 80):
        alpha = 18 + (i % 160) // 8
        draw.line([(i, 0), (i, H)], fill=(alpha, alpha + 6, alpha + 12), width=1)
    for j in range(0, H, 80):
        alpha = 18 + (j % 160) // 8
        draw.line([(0, j), (W, j)], fill=(alpha, alpha + 6, alpha + 12), width=1)
    return img


def draw_header(img: Image.Image, title: str, subtitle: str = "") -> None:
    d = ImageDraw.Draw(img)
    d.text((90, 70), title, font=TITLE_FONT, fill=TEXT)
    if subtitle:
        d.text((92, 150), subtitle, font=HEAD_FONT, fill=ACCENT)


def draw_bullets(img: Image.Image, bullets: List[str], y0: int = 240) -> None:
    d = ImageDraw.Draw(img)
    y = y0
    for b in bullets:
        d.text((100, y), f"• {b}", font=BODY_FONT, fill=MUTED)
        y += 52


def draw_arc_grid(
    img: Image.Image,
    grid: List[List[int]],
    origin: Tuple[int, int],
    cell: int = 56,
    highlight: List[Tuple[int, int]] | None = None,
    glow: float = 0.0,
) -> None:
    d = ImageDraw.Draw(img)
    highlight = highlight or []
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            px, py = origin[0] + x * cell, origin[1] + y * cell
            fill = GRID_COLORS[val % len(GRID_COLORS)]
            if (x, y) in highlight:
                fill = tuple(min(255, c + int(80 * glow)) for c in ACCENT)
            d.rounded_rectangle([px, py, px + cell - 6, py + cell - 6], radius=10, fill=fill, outline=(60, 70, 95))


def paint_intro(img: Image.Image, t: float) -> None:
    draw_header(img, "A-S-R-A Phase 1", "Adaptive Experimental Memory Formation")
    d = ImageDraw.Draw(img)
    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 2)
    cx, cy = W // 2, 560
    r = int(120 + 30 * pulse)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ACCENT, width=4)
    d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], outline=ACCENT2, width=2)
    d.text((cx - 280, cy - 20), "observe  →  act  →  compare  →  remember", font=HEAD_FONT, fill=TEXT)


def paint_static_vs_interactive(img: Image.Image, t: float) -> None:
    draw_header(img, "Beyond Static Benchmarks", "Interactive intelligence in unknown environments")
    draw_bullets(img, ["Static models predict fixed inputs", "Interactive agents learn through action", "Consequences shape memory and strategy"])
    d = ImageDraw.Draw(img)
    left = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]
    right = [[2, 0, 1], [0, 3, 0], [1, 0, 2]]
    draw_arc_grid(img, left, (220, 360), cell=48)
    draw_arc_grid(img, right, (1180, 360), cell=48, glow=t)
    d.text((250, 300), "STATIC", font=SMALL_FONT, fill=MUTED)
    d.text((1210, 300), "INTERACTIVE", font=SMALL_FONT, fill=ACCENT)
    d.line([(960, 340), (960, 720)], fill=(50, 60, 80), width=3)


def paint_asra_intro(img: Image.Image, t: float) -> None:
    draw_header(img, "Introducing A-S-R-A", "Adaptive Scientific Reasoning Architecture")
    draw_bullets(
        img,
        [
            "Intelligence as experimentation, not memorization",
            "Unknown environments, unknown action semantics",
            "Scientific loop: observe, act, compare, log, graph, replay",
        ],
    )
    d = ImageDraw.Draw(img)
    labels = ["Environment", "Agent", "Memory", "Graph", "Dataset"]
    xs = [int(200 + i * 320 + 40 * math.sin(t * 6.28 + i)) for i in range(5)]
    for i, (x, label) in enumerate(zip(xs, labels)):
        d.rounded_rectangle([x, 520, x + 220, 620], radius=16, outline=ACCENT if i == int(t * 5) % 5 else ACCENT2, width=3)
        d.text((x + 24, 555), label, font=BODY_FONT, fill=TEXT)


def paint_phase1(img: Image.Image, t: float) -> None:
    draw_header(img, "What Is Phase 1?", "Adaptive Experimental Memory Formation")
    steps = ["Observe frames", "Test actions", "Diff grids", "Hash states", "Log transitions", "Build graphs", "Replay & export"]
    d = ImageDraw.Draw(img)
    y = 260
    for i, s in enumerate(steps):
        active = i <= int(t * len(steps))
        col = ACCENT if active else MUTED
        d.text((120, y), f"{i+1}. {s}", font=BODY_FONT, fill=col)
        y += 48
    draw_arc_grid(img, [[0, 1, 0], [1, 2, 1], [0, 1, 0]], (1250, 300), cell=52, glow=t)


def paint_arc(img: Image.Image, t: float) -> None:
    draw_header(img, "ARC-AGI-3 Environments", "Grids, frames, actions — semantics unknown")
    draw_bullets(img, ["RESET + ACTION1…ACTION7", "Frame parser validates grid shape and colors", "Agent must infer effects through experimentation"])
    g1 = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    g2 = [[1, 0, 0], [0, 1, 0], [0, 0, 0]]
    hi = [(0, 0)] if t > 0.3 else []
    draw_arc_grid(img, g1 if t < 0.5 else g2, (1180, 360), cell=54, highlight=hi, glow=abs(math.sin(t * math.pi)))


def paint_architecture(img: Image.Image, t: float) -> None:
    draw_header(img, "Phase 1 Architecture", "End-to-end scientific observation pipeline")
    blocks = [
        "ARC Runner",
        "Frame Parser",
        "Exploration Policy",
        "Action Execution",
        "Grid Diff",
        "State Hash",
        "Episode Logger",
        "State Graph",
        "Replay Viewer",
        "Dataset Export",
    ]
    d = ImageDraw.Draw(img)
    x, y = 140, 260
    for i, b in enumerate(blocks):
        active = i <= int(t * len(blocks))
        col = ACCENT if active else (35, 45, 65)
        d.rounded_rectangle([x, y, x + 300, y + 56], radius=12, fill=col if active else (18, 24, 38), outline=ACCENT2, width=2)
        d.text((x + 16, y + 12), b, font=SMALL_FONT, fill=TEXT)
        if i < len(blocks) - 1:
            d.line([(x + 150, y + 56), (x + 150, y + 76)], fill=ACCENT, width=2)
        y += 76
        if y > 900:
            y = 260
            x += 360


def paint_transition(img: Image.Image, t: float) -> None:
    draw_header(img, "State Transitions", "state → action → next_state → reward → terminal → metadata")
    g_before = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    g_after = [[1, 0, 0], [0, 1, 0], [0, 0, 0]]
    draw_arc_grid(img, g_before, (260, 380), cell=58)
    draw_arc_grid(img, g_after, (1180, 380), cell=58, highlight=[(0, 0)], glow=t)
    d = ImageDraw.Draw(img)
    d.text((820, 500), "ACTION1", font=HEAD_FONT, fill=ACCENT)
    d.text((300, 320), "state", font=SMALL_FONT, fill=MUTED)
    d.text((1220, 320), "next_state", font=SMALL_FONT, fill=MUTED)


def paint_diff(img: Image.Image, t: float) -> None:
    draw_header(img, "Grid Differencing", "Visible causality from local cell changes")
    draw_bullets(img, ["changed_cells", "change_ratio", "added / removed colors", "unchanged_ratio"])
    g = [[0, 1, 0], [1, 2, 1], [0, 1, 0]]
    hi = [(1, 0), (0, 1), (1, 1)] if t > 0.2 else []
    draw_arc_grid(img, g, (1150, 360), cell=54, highlight=hi, glow=min(1.0, t * 1.5))


def paint_hash(img: Image.Image, t: float) -> None:
    draw_header(img, "State Hashing", "Same grid → same SHA-256 identity")
    draw_bullets(img, ["Includes grid values and shape", "Excludes timestamps and episode metadata", "Powers graph nodes, replay, and cycle detection"])
    d = ImageDraw.Draw(img)
    h = "d4665b97…9420fa8"
    d.rounded_rectangle([1100, 380, 1700, 520], radius=18, outline=ACCENT, width=3)
    d.text((1140, 430), h, font=HEAD_FONT, fill=ACCENT)
    draw_arc_grid(img, [[0, 0, 0], [0, 1, 0], [0, 0, 0]], (280, 380), cell=58)
    draw_arc_grid(img, [[0, 0, 0], [0, 1, 0], [0, 0, 0]], (280, 620), cell=58)
    if t > 0.4:
        d.line([(600, 500), (1080, 450)], fill=ACCENT2, width=4)


def paint_graph(img: Image.Image, t: float) -> None:
    draw_header(img, "State Graph", "Nodes = state hashes, edges = actions + outcomes")
    d = ImageDraw.Draw(img)
    nodes = [(400, 500), (700, 350), (1000, 520), (1300, 380), (1550, 550), (850, 700)]
    n_show = max(2, int(t * len(nodes)))
    for i in range(n_show):
        x, y = nodes[i]
        d.ellipse([x - 28, y - 28, x + 28, y + 28], fill=(30, 40, 60), outline=ACCENT, width=3)
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (1, 5), (5, 2)]
    for a, b in edges:
        if a < n_show and b < n_show:
            x1, y1 = nodes[a]
            x2, y2 = nodes[b]
            d.line([(x1, y1), (x2, y2)], fill=ACCENT2, width=3)


def paint_policy(img: Image.Image, t: float) -> None:
    draw_header(img, "Exploration Policy", "simple_exploration — novelty without assumed semantics")
    draw_bullets(img, ["Prefer untested actions", "Reward grid change and new state hashes", "Penalize cycles and GAME_OVER", "RESET on high dead-end score"])
    d = ImageDraw.Draw(img)
    actions = ["RESET", "A1", "A2", "A3", "A4", "A5", "A6", "A7"]
    for i, a in enumerate(actions):
        score = abs(math.sin(t * 4 + i)) * (1 if i == 3 else 0.4)
        w = int(40 + score * 120)
        d.rectangle([1120, 280 + i * 70, 1120 + w, 330 + i * 70], fill=ACCENT if i == 3 else (40, 50, 70))
        d.text((1240, 292 + i * 70), a, font=SMALL_FONT, fill=TEXT)


def paint_dead_end(img: Image.Image, t: float) -> None:
    draw_header(img, "Dead-End Detection", "Heuristic escape from unproductive loops")
    draw_bullets(img, ["All actions return same state", "No meaningful grid change", "Cycles among visited hashes", "GAME_OVER and low novelty"])
    d = ImageDraw.Draw(img)
    pts = [(500, 500), (650, 400), (800, 500), (650, 600)]
    for i in range(4):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % 4]
        d.line([(x1, y1), (x2, y2)], fill=(220, 80, 100), width=4)
    d.text((620, 470), "cycle", font=HEAD_FONT, fill=(255, 120, 140))


def paint_replay(img: Image.Image, t: float) -> None:
    draw_header(img, "Replay Viewer", "CLI and Streamlit inspection of every transition")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([180, 280, 1740, 900], radius=24, outline=ACCENT2, width=3, fill=(14, 18, 30))
    step = int(t * 9)
    d.text((220, 320), f"Episode · Step {step}", font=HEAD_FONT, fill=TEXT)
    draw_arc_grid(img, [[0, 1, 0], [1, 2, 1], [0, 1, 0]], (260, 430), cell=44)
    draw_arc_grid(img, [[1, 1, 0], [1, 2, 1], [0, 1, 0]], (900, 430), cell=44, highlight=[(0, 0), (1, 0)], glow=t)
    d.text((260, 380), "before", font=SMALL_FONT, fill=MUTED)
    d.text((900, 380), "after", font=SMALL_FONT, fill=MUTED)


def paint_exports(img: Image.Image, t: float) -> None:
    draw_header(img, "Dataset Outputs", "Structured experiential memory for Phase 2+")
    files = [
        "asra_v0_1_transitions.jsonl",
        "asra_v0_1_transitions.parquet",
        "asra_v0_1_episode_summary.csv",
        "asra_v0_1_state_graph.json",
    ]
    d = ImageDraw.Draw(img)
    y = 300
    for i, f in enumerate(files):
        on = i <= int(t * len(files))
        d.text((120, y), f"{'▸' if on else '○'} {f}", font=BODY_FONT, fill=ACCENT if on else MUTED)
        y += 56


def paint_accomplished(img: Image.Image, t: float) -> None:
    draw_header(img, "What Phase 1 Accomplished", "A-S-R-A now possesses experiential memory")
    caps = ["interact", "observe", "compare", "remember", "replay", "graph", "export"]
    d = ImageDraw.Draw(img)
    cx, cy = 1050, 560
    for i, c in enumerate(caps):
        ang = 2 * math.pi * i / len(caps) + t * 0.8
        x = int(cx + 260 * math.cos(ang))
        y = int(cy + 180 * math.sin(ang))
        d.ellipse([x - 70, y - 28, x + 70, y + 28], outline=ACCENT, width=2)
        d.text((x - 48, y - 14), c, font=SMALL_FONT, fill=TEXT)


def paint_future(img: Image.Image, t: float) -> None:
    draw_header(img, "Beyond Phase 1", "Foundation for adaptive reasoning")
    phases = [
        "Phase 2 — Action semantics inference",
        "Phase 3 — World models",
        "Phase 4 — Adaptive strategy invention",
        "Phase 5 — Scientific reasoning",
    ]
    d = ImageDraw.Draw(img)
    y = 280
    for i, p in enumerate(phases):
        if i <= int(t * len(phases)):
            d.text((120, y), p, font=BODY_FONT, fill=ACCENT if i == int(t * 4) % 4 else TEXT)
        y += 58


def paint_closing(img: Image.Image, t: float) -> None:
    d = ImageDraw.Draw(img)
    msg = "Before intelligence can reason,\nit must first learn to observe,\nexperiment, and remember."
    for i, line in enumerate(msg.split("\n")):
        alpha = min(1.0, max(0, t * 2 - i * 0.2))
        col = tuple(int(c * alpha) for c in TEXT)
        d.text((W // 2 - 520, 360 + i * 72), line, font=TITLE_FONT if i == 0 else HEAD_FONT, fill=col)
    d.text((W // 2 - 160, 820), "A-S-R-A", font=TITLE_FONT, fill=ACCENT)


SLIDES: List[Slide] = [
    Slide(
        "Cinematic Intro",
        ["Adaptive Scientific Reasoning Architecture", "Phase 1 — memory from interaction"],
        "A-S-R-A Phase 1 is about adaptive experimental memory formation. "
        "Before an agent can reason scientifically, it must learn to observe unknown worlds, "
        "act without assumed semantics, and remember what happened.",
        paint_intro,
    ),
    Slide(
        "Static vs Interactive",
        ["Benchmark prediction is not enough", "Interactive agents learn from consequences"],
        "Traditional AI often excels at static benchmarks. "
        "But real intelligence unfolds inside environments that change when we act. "
        "A-S-R-A treats intelligence as adaptive experimentation in unknown environments.",
        paint_static_vs_interactive,
    ),
    Slide(
        "Introducing A-S-R-A",
        ["Scientific observation layer", "Not a hardcoded solver"],
        "A-S-R-A, the Adaptive Scientific Reasoning Architecture, is built for interactive scientific learning. "
        "Phase one does not memorize tasks. It builds the infrastructure to observe, experiment, and remember.",
        paint_asra_intro,
    ),
    Slide(
        "What Is Phase 1",
        ["Memory formation through experience", "Observe, act, compare, log, graph, replay"],
        "Phase one is adaptive experimental memory formation. "
        "The agent watches frames, tests actions, compares states, logs transitions, "
        "builds a state graph, replays episodes, and exports datasets.",
        paint_phase1,
    ),
    Slide(
        "ARC-AGI-3",
        ["Interactive grid environments", "Unknown action meaning"],
        "ARC AGI three provides interactive grid worlds. "
        "Each frame is parsed into a normalized grid. Actions are available, but their semantics are not given. "
        "The agent must discover effects through experimentation.",
        paint_arc,
    ),
    Slide(
        "Architecture",
        ["Runner through export", "Modular and reproducible"],
        "The Phase one pipeline connects an environment runner, frame parser, exploration policy, "
        "action execution, grid differencing, state hashing, episode logger, state graph, replay viewer, "
        "and dataset exporter into one reproducible system.",
        paint_architecture,
    ),
    Slide(
        "Transitions",
        ["Every step is a scientific record", "state, action, next_state, reward, terminal, metadata"],
        "Every step becomes a transition: state, action, next state, reward, terminal flag, and metadata. "
        "This is the atomic unit of experiential memory.",
        paint_transition,
    ),
    Slide(
        "Grid Diff",
        ["Visible change is evidence", "Local causality from pixels"],
        "Grid differencing highlights which cells changed, how much of the grid changed, "
        "and which colors appeared or disappeared. This is how A-S-R-A sees action consequences.",
        paint_diff,
    ),
    Slide(
        "State Hash",
        ["Deterministic identity", "Foundation of memory"],
        "Identical grids always receive the same SHA-256 state hash. "
        "That stable identity powers the state graph, replay, and cycle detection.",
        paint_hash,
    ),
    Slide(
        "State Graph",
        ["Topology of experience", "Cycles, hubs, dead ends"],
        "Transitions accumulate into a state graph. Nodes are unique states. "
        "Edges are actions with counts, rewards, and diff summaries. Exploration topology becomes visible.",
        paint_graph,
    ),
    Slide(
        "Exploration Policy",
        ["simple_exploration", "Novelty without cheating"],
        "The baseline simple exploration policy prefers untested actions and new state hashes, "
        "avoids game over and cycles, and resets when dead-end scores grow high.",
        paint_policy,
    ),
    Slide(
        "Dead Ends",
        ["Detect traps early", "Heuristic, not oracle"],
        "Dead-end detection flags states where every action fails to escape, "
        "where grids stop changing, or where the agent loops among known states.",
        paint_dead_end,
    ),
    Slide(
        "Replay",
        ["Scientific playback", "Inspect every decision"],
        "The replay viewer walks step by step through episodes, showing grids before and after, "
        "diffs, rewards, and metadata. Memory becomes inspectable science.",
        paint_replay,
    ),
    Slide(
        "Exports",
        ["JSONL, Parquet, CSV, graph JSON", "Ready for analysis and Phase 2"],
        "Phase one exports transitions as JSONL and Parquet, episode summaries as CSV, "
        "and the state graph as JSON for analysis, visualization, and future learning.",
        paint_exports,
    ),
    Slide(
        "Accomplished",
        ["Experiential memory exists", "Infrastructure is real"],
        "A-S-R-A can now interact, observe, compare, remember, replay, graph, and export. "
        "This is not hypothetical. Phase one built the memory layer.",
        paint_accomplished,
    ),
    Slide(
        "Future Phases",
        ["Semantics, world models, strategy, reasoning"],
        "Phase two will infer action semantics. Phase three builds world models. "
        "Phase four invents strategies. Phase five pursues scientific reasoning. "
        "But all of it stands on Phase one's memory.",
        paint_future,
    ),
    Slide(
        "Closing",
        ["Observe. Experiment. Remember.", "The beginning of adaptive intelligence"],
        "Before intelligence can reason, it must first learn to observe, experiment, and remember. "
        "A-S-R-A Phase one is that foundation. This is the beginning of adaptive experimental intelligence.",
        paint_closing,
    ),
]


def render_slide_frame(slide: Slide, t: float) -> np.ndarray:
    img = base_canvas()
    # Each slide painter owns its own text layout. Avoid drawing a second
    # global bullet layer, which makes text overlap and unreadable.
    slide.painter(img, t)
    return np.array(img)


def tts_to_wav(text: str, wav_path: Path) -> None:
    aiff = wav_path.with_suffix(".aiff")
    spoken_text = text.replace("A-S-R-A", "A S R A")
    subprocess.run(["say", "-v", "Samantha", "-r", "168", "-o", str(aiff), spoken_text], check=True)
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", str(aiff), str(wav_path)], check=True)
    aiff.unlink(missing_ok=True)


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def build_video(slides: List[Slide], out_mp4: Path) -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    clips = []
    for idx, slide in enumerate(slides):
        wav = BUILD_DIR / f"slide_{idx:02d}.wav"
        print(f"TTS slide {idx+1}/{len(slides)}: {slide.title}")
        tts_to_wav(slide.narration, wav)
        duration = max(6.0, wav_duration(wav) + 0.6)

        def make_frame(t, s=slide, d=duration):
            return render_slide_frame(s, min(1.0, t / max(d - 0.5, 1)))

        clip = VideoClip(make_frame, duration=duration)
        audio = AudioFileClip(str(wav))
        clip = clip.with_audio(audio)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    print(f"Writing {out_mp4} ...")
    final.write_videofile(
        str(out_mp4),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        logger=None,
    )
    for c in clips:
        c.close()
    final.close()


def write_production_package(slides: List[Slide], path: Path) -> None:
  lines = ["# A-S-R-A Phase 1 — Video Production Package\n"]
  for i, s in enumerate(slides, 1):
    lines += [
      f"\n## Slide {i}: {s.title}\n",
      f"**On-screen bullets:** " + "; ".join(s.bullets) + "\n",
      f"**Voice-over:** {s.narration}\n",
      "**Motion:** slow zoom-in, 0.4s ease-out transitions, glowing grid highlights.\n",
      "**Sound:** ambient scientific pad, soft whoosh between slides.\n",
    ]
  path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    out_mp4 = OUT_DIR / "ASRA_Phase1_Adaptive_Experimental_Memory.mp4"
    write_production_package(SLIDES, OUT_DIR / "phase1-video-production-package.md")
    (OUT_DIR / "phase1-video-voiceover-script.md").write_text(
        "\n\n".join(f"### Slide {i+1}: {s.title}\n\n{s.narration}" for i, s in enumerate(SLIDES)),
        encoding="utf-8",
    )
    build_video(SLIDES, out_mp4)
    meta = {
      "slides": len(SLIDES),
      "output": str(out_mp4),
      "resolution": [W, H],
      "fps": FPS,
    }
    (OUT_DIR / "phase1-video-render-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("Done:", out_mp4)


if __name__ == "__main__":
    main()
