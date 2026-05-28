#!/usr/bin/env python3
"""Render Action Semantics Inference educational video per spec2.md."""

from __future__ import annotations

import json
import math
import re
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, VideoClip, concatenate_videoclips

ROOT = Path(__file__).resolve().parent
BUILD_DIR = ROOT / "_build"
OUT_MP4 = ROOT / "ASRA_Action_Semantics_Inference.mp4"
W, H = 1920, 1080
FPS = 24

BG = (6, 10, 18)
ACCENT = (0, 200, 220)
ACCENT2 = (60, 180, 120)
RED_HI = (220, 90, 90)
TEXT = (240, 245, 255)
MUTED = (130, 150, 175)

CELL_COLORS = {
    0: (22, 30, 48),
    1: (50, 110, 210),
    2: (210, 70, 70),
    3: (55, 175, 110),
}

Grid = Sequence[Sequence[int]]


@dataclass
class Slide:
    scene: str
    title: str
    subtitle: str
    narration: str
    painter: Callable[[Image.Image, float], None]


def load_font(size: int, bold: bool = False):
    for path in [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                pass
    return ImageFont.load_default()


TITLE_FONT = load_font(52, bold=True)
HEAD_FONT = load_font(34, bold=True)
BODY_FONT = load_font(26)
SMALL_FONT = load_font(20)
BIG_FONT = load_font(72, bold=True)


def base_canvas() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for i in range(0, W, 64):
        d.line([(i, 0), (i, H)], fill=(14, 22, 38), width=1)
    for j in range(0, H, 64):
        d.line([(0, j), (W, j)], fill=(14, 22, 38), width=1)
    return img


def draw_header(img: Image.Image, scene: str, title: str, subtitle: str = "") -> None:
    d = ImageDraw.Draw(img)
    d.text((80, 50), scene.upper(), font=SMALL_FONT, fill=ACCENT)
    d.text((80, 85), title, font=TITLE_FONT, fill=TEXT)
    if subtitle:
        d.text((82, 155), subtitle, font=HEAD_FONT, fill=MUTED)


def draw_grid(
    img: Image.Image,
    grid: Grid,
    ox: int,
    oy: int,
    cell: int = 90,
    highlight: Optional[Tuple[int, int]] = None,
    diff_cells: Optional[List[Tuple[int, int]]] = None,
    labels: bool = False,
) -> None:
    d = ImageDraw.Draw(img)
    diff_cells = diff_cells or []
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            x0, y0 = ox + x * cell, oy + y * cell
            x1, y1 = x0 + cell - 6, y0 + cell - 6
            fill = CELL_COLORS.get(val, (40, 50, 70))
            outline = MUTED
            width = 2
            if highlight == (y, x):
                outline = ACCENT
                width = 4
                pulse = 0.5 + 0.5 * math.sin(0.0)
                if (y, x) in diff_cells or highlight:
                    pass
            if (y, x) in diff_cells:
                outline = ACCENT
                width = 4
            d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=fill, outline=outline, width=width)
            d.text((x0 + cell // 2 - 8, y0 + cell // 2 - 12), str(val), font=BODY_FONT, fill=TEXT)
            if labels:
                d.text((x0 + 4, y0 - 22), f"({y},{x})", font=SMALL_FONT, fill=MUTED)


def paint_opening(img: Image.Image, t: float) -> None:
    draw_header(img, "Scene 1", "Action Semantics Inference", "Learning what actions mean from state transitions")
    d = ImageDraw.Draw(img)
    tokens = ["ACTION1", "ACTION2", "ACTION3"]
    for i, tok in enumerate(tokens):
        x = 1080 + i * 220
        y = 420 + int(30 * math.sin(t * 3 + i))
        on = i == int(t * 3) % 3
        d.text((x, y), tok, font=HEAD_FONT, fill=ACCENT if on else MUTED)
    if t < 0.45:
        d.text((1050, 300), "Most AI systems already know what their actions mean.", font=BODY_FONT, fill=MUTED)
    else:
        d.text((1050, 300), "But what if the meaning was never given?", font=BODY_FONT, fill=ACCENT)
    if t > 0.7:
        d.text((1050, 680), "The system is never told what ACTION1 means.", font=HEAD_FONT, fill=ACCENT)


def paint_grid_world(img: Image.Image, t: float) -> None:
    draw_header(img, "Scene 2", "Understanding States", "A state is a snapshot of the world")
    grid = [[0, 0, 0], [0, 2, 0], [0, 0, 0]]
    draw_grid(img, grid, 1100, 380, labels=t > 0.3)
    d = ImageDraw.Draw(img)
    legend = ["0 black", "1 blue", "2 red", "3 green"]
    for i, lab in enumerate(legend):
        on = i <= int(t * 4)
        d.text((1100, 760 + i * 32), lab, font=SMALL_FONT, fill=ACCENT if on else MUTED)
    if t > 0.5:
        d.text((1100, 340), "grid[0][1] = top-center", font=BODY_FONT, fill=ACCENT)
        d.text((1100, 680), "Coordinates: (y, x)", font=BODY_FONT, fill=MUTED)


def paint_before_state(img: Image.Image, t: float) -> None:
    draw_header(img, "Scene 3", "Before State", "Intelligence begins with comparison")
    grid = [[0, 0, 0], [0, 2, 0], [0, 0, 0]]
    draw_grid(img, grid, 1100, 380, highlight=(0, 1) if t > 0.2 else None)
    d = ImageDraw.Draw(img)
    if t > 0.35:
        d.text((1100, 680), "Before: position (0,1) = 0  ·  black", font=BODY_FONT, fill=ACCENT)
    if t > 0.55:
        d.text((1100, 730), "Before: position (1,1) = 2  ·  red (center)", font=BODY_FONT, fill=MUTED)


def paint_action_token(img: Image.Image, t: float) -> None:
    draw_header(img, "Scene 4", "The Unknown Action", "The token is known — the semantics are hidden")
    d = ImageDraw.Draw(img)
    cx, cy = 1350, 520
    d.text((cx - 120, cy - 40), "ACTION1", font=BIG_FONT, fill=ACCENT)
    for i in range(6):
        ang = t * 2 + i * math.pi / 3
        x = cx + int(200 * math.cos(ang))
        y = cy + int(120 * math.sin(ang))
        d.text((x - 10, y - 10), "?", font=HEAD_FONT, fill=MUTED)
    if t > 0.4:
        d.text((1050, 720), "The action meaning is never explicitly provided.", font=BODY_FONT, fill=ACCENT)


def paint_after_diff(img: Image.Image, t: float) -> None:
    draw_header(img, "Scene 5", "State Transition", "Before → ACTION1 → After")
    before = [[0, 0, 0], [0, 2, 0], [0, 0, 0]]
    after = [[0, 1, 0], [0, 2, 0], [0, 0, 0]]
    draw_grid(img, before, 980, 400, cell=70)
    draw_grid(img, after, 1380, 400, cell=70, diff_cells=[(0, 1)] if t > 0.4 else [])
    d = ImageDraw.Draw(img)
    d.text((1020, 350), "Before", font=SMALL_FONT, fill=MUTED)
    d.text((1420, 350), "After", font=SMALL_FONT, fill=ACCENT)
    d.text((1240, 520), "ACTION1", font=HEAD_FONT, fill=ACCENT2)
    if t > 0.55:
        d.text((980, 680), "Only (0,1) changed:  0 → 1", font=BODY_FONT, fill=ACCENT)
    if t > 0.75:
        d.text((980, 730), "No movement · no rotation · local color update", font=SMALL_FONT, fill=MUTED)


def paint_repeated(img: Image.Image, t: float) -> None:
    draw_header(img, "Scene 6", "Semantic Convergence", "Repeated transitions reveal hidden rules")
    cycle = [0, 1, 2, 3, 0]
    idx = min(4, int(t * 5))
    val = cycle[idx]
    grid = [[0, val, 0], [0, 2, 0], [0, 0, 0]]
    draw_grid(img, grid, 1100, 380, highlight=(0, 1))
    d = ImageDraw.Draw(img)
    chain = " → ".join(str(c) for c in cycle[: idx + 1])
    d.text((1100, 680), chain, font=HEAD_FONT, fill=ACCENT)
    if t > 0.75:
        d.text((1100, 760), "ACTION1 = increment color at top-center", font=BODY_FONT, fill=ACCENT2)


def paint_formula(img: Image.Image, t: float) -> None:
    draw_header(img, "Scene 7", "Compressed Semantics", "Rules emerge from repeated evidence")
    d = ImageDraw.Draw(img)
    d.text((1050, 380), "next[y][x] = (grid[y][x] + 1) % 4", font=HEAD_FONT, fill=ACCENT)
    parts = [
        "grid[y][x]  →  current value",
        "+ 1  →  increment",
        "% 4  →  wrap: 3 + 1 = 0",
    ]
    for i, p in enumerate(parts):
        on = i <= int(t * 3)
        d.text((1080, 500 + i * 55), p, font=BODY_FONT, fill=TEXT if on else MUTED)
    angles = [0, 1, 2, 3]
    cx, cy, r = 1500, 580, 80
    for i, v in enumerate(angles):
        ang = -math.pi / 2 + 2 * math.pi * i / 4
        x = cx + int(r * math.cos(ang))
        y = cy + int(r * math.sin(ang))
        on = i <= int(t * 4)
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=CELL_COLORS[v] if on else (40, 50, 70), outline=ACCENT if on else MUTED)
        d.text((x - 6, y - 10), str(v), font=SMALL_FONT, fill=TEXT)
    if t > 0.6:
        d.text((1050, 720), "The system compresses transitions into reusable rules.", font=BODY_FONT, fill=ACCENT)


def paint_science_bridge(img: Image.Image, t: float) -> None:
    draw_header(img, "Scene 8", "Beyond Grid Worlds", "Same mechanism · broader intelligence")
    d = ImageDraw.Draw(img)
    nodes = ["Grid world", "ARC reasoning", "Decision Biology", "World models", "Scientific AI"]
    for i, lab in enumerate(nodes):
        x = 1080 + (i % 3) * 220
        y = 380 + (i // 3) * 160
        on = i <= int(t * 5)
        d.rounded_rectangle([x, y, x + 200, y + 90], radius=10, outline=ACCENT if on else MUTED, width=2)
        d.text((x + 20, y + 32), lab, font=SMALL_FONT, fill=TEXT if on else MUTED)
        if i > 0 and on:
            px = 1080 + ((i - 1) % 3) * 220 + 100
            py = 380 + ((i - 1) // 3) * 160 + 45
            d.line([(px, py), (x + 100, y + 45)], fill=ACCENT2, width=2)
    if t > 0.6:
        d.text((1050, 720), "Infer intervention dynamics · hidden causal operators", font=BODY_FONT, fill=ACCENT)


def paint_asra_loop(img: Image.Image, t: float) -> None:
    draw_header(img, "Scene 9", "The ASRA Loop", "Adaptive scientific reasoning")
    steps = ["Observe", "Hypothesize", "Intervene", "Evaluate", "Update", "Abstract"]
    cx, cy, r = 1350, 540, 210
    d = ImageDraw.Draw(img)
    for i, label in enumerate(steps):
        ang = -math.pi / 2 + 2 * math.pi * i / len(steps)
        x = cx + int(r * math.cos(ang))
        y = cy + int(r * math.sin(ang))
        active = i == int(t * len(steps)) % len(steps)
        d.ellipse([x - 62, y - 22, x + 62, y + 22], outline=ACCENT if active else MUTED, width=3)
        d.text((x - 52, y - 10), label, font=SMALL_FONT, fill=TEXT if active else MUTED)
    d.text((cx - 30, cy - 10), "Repeat", font=SMALL_FONT, fill=MUTED)
    if t > 0.5:
        d.text((1050, 760), "Semantics feed planning · world models · discovery", font=BODY_FONT, fill=ACCENT)


def paint_closing(img: Image.Image, t: float) -> None:
    draw_header(img, "Scene 10", "Conclusion", "")
    grid = [[0, 1, 0], [0, 2, 0], [0, 0, 0]]
    draw_grid(img, grid, 1100, 360, cell=70, highlight=(0, 1))
    d = ImageDraw.Draw(img)
    lines = [
        "Before Grid  ·  Action Token  ·  After Grid",
        "Meaning emerged from interaction — never from labels.",
    ]
    for i, line in enumerate(lines):
        on = i <= int(t * 2)
        d.text((200, 520 + i * 60), line, font=BODY_FONT, fill=ACCENT if on else MUTED)
    if t > 0.55:
        d.text((200, 680), "The transition from 0 to 1 was not merely a color change.", font=HEAD_FONT, fill=TEXT)
        d.text((200, 740), "It was evidence.", font=HEAD_FONT, fill=ACCENT)
    if t > 0.75:
        d.text((200, 820), "Understanding state transitions is the beginning of understanding intelligence itself.",
               font=SMALL_FONT, fill=MUTED)
        d.text((200, 880), "ASRA · Decision Biology · Nature Foundation Models", font=SMALL_FONT, fill=ACCENT)


def paint_exercise(img: Image.Image, t: float) -> None:
    draw_header(img, "Exercise", "Infer the Action", "Compare Before and After cell by cell")
    before = [[1, 0, 0], [0, 2, 0], [0, 0, 0]]
    after = [[1, 0, 0], [0, 3, 0], [0, 0, 0]]
    draw_grid(img, before, 980, 400, cell=70)
    draw_grid(img, after, 1380, 400, cell=70, diff_cells=[(1, 1)] if t > 0.5 else [])
    d = ImageDraw.Draw(img)
    d.text((1020, 350), "Before", font=SMALL_FONT, fill=MUTED)
    d.text((1420, 350), "After", font=SMALL_FONT, fill=ACCENT)
    if t > 0.65:
        d.text((980, 680), "Center (1,1): 2 → 3  ·  increment at center cell", font=BODY_FONT, fill=ACCENT)


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


SLIDES: List[Slide] = [
    Slide(
        "Scene 1", "Opening",
        "",
        clean(
            "Most AI systems already know what their actions mean. When a game engine receives ACTION LEFT, "
            "the programmer defined exactly what happens. When a robot receives MOVE FORWARD, the motion planner "
            "knows the motor commands and expected outcome. The semantics are explicit — written into the system before it runs. "
            "But ASRA-style adaptive reasoning systems work differently. They receive abstract tokens: ACTION1, ACTION2, ACTION3. "
            "No definitions. No labels. No documentation. The system is never told what ACTION1 means. "
            "All it sees is Before Grid, Action Token, After Grid. From those observations alone, it must discover "
            "what each action actually does. This is action semantics inference — and it is one of the foundations of adaptive intelligence."
        ),
        paint_opening,
    ),
    Slide(
        "Scene 2", "States",
        "",
        clean(
            "Before we can talk about actions, we need a precise notion of state. "
            "A state is a complete snapshot of the environment at one moment in time. "
            "Consider a three-by-three grid. Zero is black. One is blue. Two is red. Three is green. "
            "One red cell sits at the center. The full grid configuration — every cell value together — is the current state. "
            "Grids use row-column indexing. Y is the row, top to bottom. X is the column, left to right. "
            "Position zero-comma-one is top-center. In code, grid zero-one refers to that cell. "
            "Understanding coordinates matters because action semantics are often local — "
            "the system must identify exactly where change occurred."
        ),
        paint_grid_world,
    ),
    Slide(
        "Scene 3", "Before State",
        "",
        clean(
            "The Before State is the environment immediately before an action is applied. "
            "Top-center position zero-comma-one equals zero — black. Center position one-comma-one equals two — red. "
            "Nothing has happened yet. This is the baseline the system will compare against. "
            "Why does the Before State matter? Because semantics inference is fundamentally comparative. "
            "The system cannot know what an action did unless it knows what the world looked like before. "
            "Without a Before State, an After State is meaningless in isolation. "
            "Seeing grid zero-one equals one tells you nothing unless you also know it was zero a moment ago. "
            "Intelligence begins with comparison."
        ),
        paint_before_state,
    ),
    Slide(
        "Scene 4", "Unknown Action",
        "",
        clean(
            "Now an action occurs: ACTION1. Here is the critical point. The system does NOT know what ACTION1 means. "
            "ACTION1 is only a token — a symbol, a label with no attached definition. "
            "It is not told ACTION1 equals increment top-center. It is not told ACTION1 equals move left, rotate, or change color. "
            "Nothing. The action meaning is never explicitly provided. "
            "What the system has instead is a symbolic action token, known only by name, "
            "and the expectation that applying it will produce a new state. "
            "The true meaning — the latent action semantics — is hidden. "
            "The token is known. The semantics are not. This mirrors ARC environments, scientific experiments, "
            "and biological perturbation responses where mechanisms are never labeled in advance."
        ),
        paint_action_token,
    ),
    Slide(
        "Scene 5", "Change Detection",
        "",
        clean(
            "After ACTION1 is applied, the grid changes. Before: top-center equals zero. After: top-center equals one. "
            "Compare cell by cell. Only one cell changed. The red center cell stayed at position one-comma-one. "
            "No movement occurred. No rotation. No translation. No sliding. "
            "Only a local color update: zero to one, black to blue. Everything else is identical. "
            "This is a state transition: Before State, down arrow ACTION1, down arrow After State. "
            "A transition describes how the environment changes when an action is applied. "
            "The system learns by analyzing differences — environment evolution, change detection, and transition dynamics."
        ),
        paint_after_diff,
    ),
    Slide(
        "Scene 6", "Convergence",
        "",
        clean(
            "One observation is evidence, not proof. The system localizes the change: ACTION1 probably affects only top-center. "
            "But it needs repeated transitions. Apply ACTION1 again. Zero becomes one. One becomes two. Two becomes three. Three becomes zero. "
            "The pattern repeats: zero, one, two, three, zero, one. "
            "The system accumulates evidence. Uncertainty shrinks. Competing hypotheses converge. "
            "After sufficient observations, the latent semantics emerge with confidence: "
            "ACTION1 equals increment color at top-center. "
            "This is action semantics inference — the process of discovering what an action does "
            "by analyzing state transitions, without ever receiving an explicit definition."
        ),
        paint_repeated,
    ),
    Slide(
        "Scene 7", "Formula",
        "",
        clean(
            "Repeated observations compress into a compact rule. "
            "Next at y,x equals grid at y,x plus one, modulo four — with only position zero-comma-one affected. "
            "Grid y x is the current value in the Before State. Plus one increments the color. "
            "Modulo four wraps the cycle. Three plus one equals four, and four mod four equals zero — green back to black. "
            "Without modulo, three would become four, which is not a valid color. Modulo creates cyclic state transitions. "
            "A formula is a compressed semantic hypothesis. Instead of storing thousands of transition pairs, "
            "the system stores a rule that predicts, tests, and abstracts. "
            "The system compresses repeated transitions into reusable rules — the bridge from raw data to world models."
        ),
        paint_formula,
    ),
    Slide(
        "Scene 8", "Scientific Intelligence",
        "",
        clean(
            "The grid example is simple. The principle is not. "
            "The same mechanism that infers a grid transformation can infer biological intervention dynamics. "
            "In ARC reasoning, action effects differ per environment — you discover them by playing, not from a manual. "
            "In Decision Biology, cells sense stimuli and infer hidden downstream effects from perturbation responses. "
            "In scientific experimentation, you apply an intervention and observe the outcome — the mechanism was not labeled. "
            "In every case the loop is the same: compare states, detect change, infer the operator, repeat until semantics converge. "
            "This feeds world models, causal inference, autonomous discovery, and Nature Foundation Models — "
            "unified scientific intelligence built on learning what interventions actually do."
        ),
        paint_science_bridge,
    ),
    Slide(
        "Scene 9", "ASRA Loop",
        "",
        clean(
            "In ASRA — the Adaptive Scientific Reasoning Architecture — discovered semantics feed a broader adaptive loop. "
            "Observe the environment. Generate competing hypotheses. Intervene with informative actions. "
            "Evaluate outcomes. Update the world model. Abstract reusable concepts. Repeat. "
            "Action semantics inference is not an isolated preprocessing step. "
            "It enables planning: which action maximally reduces uncertainty? "
            "It enables world modeling: what will the environment look like after I act? "
            "It enables memory: what have we learned about this environment's hidden mechanics? "
            "It enables autonomous discovery — systems that learn what to do by learning what actions are. "
            "Semantics discovered from interaction dynamics alone."
        ),
        paint_asra_loop,
    ),
    Slide(
        "Exercise", "Reader Challenge",
        "",
        clean(
            "Before you finish, try this yourself. Before grid: center cell equals two, red. "
            "After an unknown action, center cell equals three, green. Nothing else changed. "
            "Scan every cell. Ignore identical cells. Only center position one-comma-one changed: two to three. "
            "Same operator type — increment — at a different target cell. "
            "In a real ASRA environment, more examples would reveal whether the action always targets center "
            "or varies by context. That is the next layer of semantics inference."
        ),
        paint_exercise,
    ),
    Slide(
        "Scene 10", "Conclusion",
        "",
        clean(
            "Return to the central claim. The action meaning was never explicitly provided. "
            "The system only saw Before Grid, Action Token, After Grid — repeated many times. "
            "From those observations, it inferred what actions actually do. Not from a manual. Not from a label file. "
            "From state transitions. Meaning emerged from interaction. "
            "The transition from zero to one at top-center was not merely a color change. It was evidence. "
            "Understanding state transitions is the beginning of understanding intelligence itself. "
            "This is the foundation of ASRA, adaptive reasoning systems, world models, scientific intelligence, "
            "and autonomous discovery. Learning the semantics of intervention through state transitions."
        ),
        paint_closing,
    ),
]


def render_frame(slide: Slide, t: float) -> np.ndarray:
    img = base_canvas()
    slide.painter(img, min(1.0, t))
    return np.array(img)


def tts_to_wav(text: str, wav_path: Path) -> None:
    spoken = text.replace("A-S-R-A", "A S R A").replace("ACTION1", "ACTION 1")
    spoken = spoken.replace("ACTION2", "ACTION 2").replace("ACTION3", "ACTION 3")
    aiff = wav_path.with_suffix(".aiff")
    subprocess.run(["say", "-v", "Samantha", "-r", "155", "-o", str(aiff), spoken], check=True)
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", str(aiff), str(wav_path)], check=True)
    aiff.unlink(missing_ok=True)


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def build_video() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    clips = []
    total_d = 0.0
    for idx, slide in enumerate(SLIDES):
        wav = BUILD_DIR / f"slide_{idx:02d}.wav"
        print(f"TTS {idx + 1}/{len(SLIDES)}: {slide.scene} — {slide.title}")
        tts_to_wav(slide.narration, wav)
        duration = max(10.0, wav_duration(wav) + 1.0)
        total_d += duration

        def make_frame(t, s=slide, d=duration):
            return render_frame(s, t / max(d - 1.2, 1))

        clip = VideoClip(make_frame, duration=duration).with_audio(AudioFileClip(str(wav)))
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    print(f"Writing {OUT_MP4} (~{total_d / 60:.1f} min) ...")
    final.write_videofile(
        str(OUT_MP4),
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
    meta = {
        "slides": len(SLIDES),
        "output": OUT_MP4.name,
        "duration_seconds": round(total_d, 1),
        "duration_minutes": round(total_d / 60, 1),
        "spec": "asra_action_semantics/spec2.md",
        "article": "asra_action_semantics/article.md",
    }
    (ROOT / "video-render-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Done: {OUT_MP4}")


if __name__ == "__main__":
    build_video()
