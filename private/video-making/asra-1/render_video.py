#!/usr/bin/env python3
"""Render ASRA-1 presentation video from slides.md + voiceover-script.md content."""

from __future__ import annotations

import json
import math
import re
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, VideoClip, concatenate_videoclips

ROOT = Path(__file__).resolve().parent
BUILD_DIR = ROOT / "_build"
OUT_MP4 = ROOT / "ASRA_Decision_Biology_Nature_Foundation_Models.mp4"
W, H = 1920, 1080
FPS = 24

BG = (8, 12, 22)
ACCENT = (79, 209, 197)
ACCENT2 = (124, 92, 255)
TEXT = (235, 240, 255)
MUTED = (140, 155, 180)


@dataclass
class Slide:
    title: str
    subtitle: str
    bullets: List[str]
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


TITLE_FONT = load_font(58, bold=True)
HEAD_FONT = load_font(36, bold=True)
BODY_FONT = load_font(28)
SMALL_FONT = load_font(20)


def base_canvas() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for i in range(0, W, 80):
        d.line([(i, 0), (i, H)], fill=(20, 24, 34), width=1)
    for j in range(0, H, 80):
        d.line([(0, j), (W, j)], fill=(20, 24, 34), width=1)
    return img


def draw_slide_text(img: Image.Image, title: str, subtitle: str, bullets: List[str], y0: int = 220) -> None:
    d = ImageDraw.Draw(img)
    d.text((90, 60), title, font=TITLE_FONT, fill=TEXT)
    if subtitle:
        d.text((92, 130), subtitle, font=HEAD_FONT, fill=ACCENT)
    y = y0
    for b in bullets[:4]:
        d.text((100, y), f"• {b}", font=BODY_FONT, fill=MUTED)
        y += 46


def draw_nodes(img: Image.Image, centers: List[tuple], t: float, labels: List[str] | None = None) -> None:
    d = ImageDraw.Draw(img)
    for i, (x, y) in enumerate(centers):
        pulse = 0.6 + 0.4 * math.sin(t * 4 + i)
        r = int(22 + 8 * pulse)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(30, 45, 70), outline=ACCENT, width=2)
        if labels and i < len(labels):
            d.text((x - 30, y + r + 6), labels[i], font=SMALL_FONT, fill=MUTED)


def paint_opening(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Toward Adaptive Scientific Intelligence", "Science needs systems that reason, not only predict.", [])
    nodes = [(400, 400), (700, 300), (1000, 450), (1300, 350), (900, 650), (550, 600)]
    draw_nodes(img, nodes, t)
    d = ImageDraw.Draw(img)
    for i, (x1, y1) in enumerate(nodes):
        x2, y2 = nodes[(i + 1) % len(nodes)]
        d.line([(x1, y1), (x2, y2)], fill=(40, 60, 90), width=1)


def paint_static_vs(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Why Today's AI Falls Short of Discovery", "Static prediction ≠ scientific reasoning", [
        "Task-specific", "Benchmark-bound", "Weak on hidden rules", "Limited exploration",
    ])
    d = ImageDraw.Draw(img)
    d.rectangle([1050, 280, 1500, 750], outline=MUTED, width=2)
    d.rectangle([1550, 280, 1820, 750], outline=ACCENT, width=3)
    d.text((1100, 300), "Static AI", font=HEAD_FONT, fill=MUTED)
    d.text((1580, 300), "Adaptive", font=HEAD_FONT, fill=ACCENT)
    d.line([(1525, 280), (1525, 750)], fill=ACCENT2, width=2)


def paint_loop(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Science Is an Adaptive Loop", "", [
        "Observe → Hypothesize → Experiment",
        "Infer → Adapt → Discover",
    ])
    cx, cy, r = 1200, 520, 200
    steps = ["Observe", "Hypothesize", "Experiment", "Infer", "Adapt", "Discover"]
    d = ImageDraw.Draw(img)
    for i, label in enumerate(steps):
        ang = -math.pi / 2 + 2 * math.pi * i / len(steps)
        x = cx + int(r * math.cos(ang))
        y = cy + int(r * math.sin(ang))
        active = i == int(t * len(steps)) % len(steps)
        d.ellipse([x - 50, y - 22, x + 50, y + 22], outline=ACCENT if active else MUTED, width=3)
        d.text((x - 45, y - 12), label, font=SMALL_FONT, fill=TEXT if active else MUTED)


def paint_asra_hub(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "A-S-R-A", "Adaptive Scientific Reasoning Architecture", [
        "Hidden-mechanics inference",
        "Exploration-driven learning",
        "Strategy invention",
        "Memory from interaction",
    ])
    d = ImageDraw.Draw(img)
    cx, cy = 1250, 560
    d.polygon(
        [(cx, cy - 90), (cx + 78, cy - 45), (cx + 78, cy + 45), (cx, cy + 90), (cx - 78, cy + 45), (cx - 78, cy - 45)],
        outline=ACCENT,
        width=3,
    )
    d.text((cx - 42, cy - 18), "A-S-R-A", font=HEAD_FONT, fill=ACCENT)
    for i, (label, ang) in enumerate(
        zip(["Environment", "Memory", "Policies", "Observations", "Simulations", "Abstractions"], range(6))
    ):
        a = ang * math.pi / 3 + t
        x = cx + int(200 * math.cos(a))
        y = cy + int(140 * math.sin(a))
        d.line([(cx, cy), (x, y)], fill=ACCENT2, width=2)
        d.text((x - 40, y - 10), label, font=SMALL_FONT, fill=MUTED)


def paint_hidden(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Inferring What You Cannot See", "Unknown rules → inferred structure", [])
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1100, 320, 1750, 820], radius=20, outline=ACCENT2, width=3)
    d.text((1280, 350), "hidden mechanics", font=HEAD_FONT, fill=MUTED)
    opacity = int(40 + 180 * t)
    for i in range(5):
        d.text((1150 + i * 110, 500), "?", font=TITLE_FONT, fill=(opacity, opacity, opacity + 40))
    if t > 0.5:
        d.line([(1200, 600), (1400, 550), (1600, 650)], fill=ACCENT, width=3)


def paint_explore(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Intelligence Through Interaction", "Probe · Compare · Update", [])
    d = ImageDraw.Draw(img)
    root = (1200, 750)
    d.ellipse([root[0] - 20, root[1] - 20, root[0] + 20, root[1] + 20], fill=ACCENT)
    branches = [(1100, 600), (1300, 600), (1150, 450), (1250, 450), (1200, 350)]
    for i, (x, y) in enumerate(branches):
        if i <= int(t * len(branches)):
            d.line([root, (x, y)], fill=ACCENT2, width=3)
            d.ellipse([x - 14, y - 14, x + 14, y + 14], outline=ACCENT, width=2)


def paint_strategy(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Strategy Is Invented, Not Memorized", "Fluid pathways through unknown space", [])
    d = ImageDraw.Draw(img)
    pts = [(1100, 700), (1250, 550), (1400, 650), (1550, 480), (1700, 600)]
    for i in range(len(pts) - 1):
        if i <= int(t * (len(pts) - 1)):
            d.line([pts[i], pts[i + 1]], fill=ACCENT, width=4)
    d.text((1280, 780), "emergent strategy", font=SMALL_FONT, fill=MUTED)


def paint_cell(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Cells as Information Processors", "Decision-making under uncertainty", [])
    d = ImageDraw.Draw(img)
    d.ellipse([1150, 380, 1650, 780], outline=ACCENT, width=4)
    for i in range(6):
        x = 1120 + i * 40
        y = 450 + int(20 * math.sin(t * 8 + i))
        d.line([(x, y), (1150, 520)], fill=(200, 100, 120), width=2)
    d.line([(1650, 520), (1720, 500)], fill=ACCENT, width=3)


def paint_pathway(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Decision Biology", "Signaling · Uncertainty · Adaptation · Inference", [])
    d = ImageDraw.Draw(img)
    xs = [1100, 1250, 1400, 1550, 1700]
    for i, x in enumerate(xs):
        d.ellipse([x - 30, 500, x + 30, 560], outline=ACCENT if i <= int(t * 5) else MUTED, width=2)
        if i < len(xs) - 1:
            d.line([(x + 30, 530), (xs[i + 1] - 30, 530)], fill=ACCENT2, width=2)
    labels = ["Receptor", "Cascade", "Signal", "Gene", "Phenotype"]
    for x, lab in zip(xs, labels):
        d.text((x - 35, 570), lab, font=SMALL_FONT, fill=MUTED)


def paint_cellular_net(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Cellular Intelligence", "Local decisions · Collective coordination", [])
    d = ImageDraw.Draw(img)
    for row in range(3):
        for col in range(5):
            x = 1080 + col * 130
            y = 420 + row * 100
            on = (col + row) <= int(t * 8)
            d.ellipse([x, y, x + 50, y + 50], outline=ACCENT if on else MUTED, width=2)


def paint_channel(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Information Theory Meets Biology", "Entropy · Mutual information · Channel fidelity", [])
    d = ImageDraw.Draw(img)
    boxes = [(1100, 500, "Ligand"), (1300, 500, "Pathway"), (1550, 500, "Phenotype")]
    for x, y, lab in boxes:
        d.rounded_rectangle([x, y, x + 140, y + 70], radius=10, outline=ACCENT, width=2)
        d.text((x + 20, y + 20), lab, font=SMALL_FONT, fill=TEXT)
    d.line([(1240, 535), (1300, 535)], fill=ACCENT2, width=3)
    d.line([(1440, 535), (1550, 535)], fill=ACCENT2, width=3)
    d.text((1320, 450), "noisy channel", font=SMALL_FONT, fill=MUTED)


def paint_domains(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Nature Foundation Models", "Biology · Chemistry · Physics · Materials · Environment", [])
    d = ImageDraw.Draw(img)
    cx, cy = 1350, 550
    domains = ["Biology", "Chemistry", "Physics", "Materials", "Environment"]
    for i, name in enumerate(domains):
        ang = -math.pi / 2 + 2 * math.pi * i / len(domains)
        x = cx + int(220 * math.cos(ang))
        y = cy + int(160 * math.sin(ang))
        on = i <= int(t * len(domains))
        d.ellipse([x - 55, y - 28, x + 55, y + 28], outline=ACCENT if on else MUTED, width=2)
        d.text((x - 40, y - 10), name, font=SMALL_FONT, fill=TEXT if on else MUTED)
        if on:
            d.line([(cx, cy), (x, y)], fill=ACCENT2, width=1)
    d.text((cx - 50, cy - 15), "Nature FM", font=HEAD_FONT, fill=ACCENT)


def paint_hierarchy(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "The Architecture Hierarchy", "", [])
    d = ImageDraw.Draw(img)
    layers = [
        (1100, 720, 1720, 820, "A-S-R-A — adaptive reasoning engine"),
        (1100, 580, 1720, 680, "Decision Biology — first domain"),
        (1100, 440, 1720, 540, "Nature Foundation Models — ecosystem"),
    ]
    for i, (x1, y1, x2, y2, label) in enumerate(layers):
        if i <= int(t * 3):
            d.rounded_rectangle([x1, y1, x2, y2], radius=14, outline=ACCENT, width=3)
            d.text((x1 + 24, y1 + 28), label, font=BODY_FONT, fill=TEXT)


def paint_agents(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Scientific Agents", "Reason · Experiment · Simulate · Collaborate", [])
    d = ImageDraw.Draw(img)
    for i, x in enumerate([1120, 1320, 1520, 1720]):
        y = 480 + (i % 2) * 120
        d.rounded_rectangle([x, y, x + 100, y + 80], radius=12, outline=ACCENT if i == int(t * 4) % 4 else MUTED, width=2)


def paint_ecosystem(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Scientific Operating Systems", "Discovery engines · Collaborative reasoning", [])
    d = ImageDraw.Draw(img)
    labels = ["Labs", "Data", "Sim", "Agents", "Graph", "Export"]
    for i, lab in enumerate(labels):
        x = 1100 + (i % 3) * 200
        y = 420 + (i // 3) * 150
        d.rounded_rectangle([x, y, x + 160, y + 90], radius=10, outline=ACCENT2, width=2)
        d.text((x + 40, y + 32), lab, font=SMALL_FONT, fill=TEXT)


def paint_impact(img: Image.Image, t: float) -> None:
    draw_slide_text(img, "Why This Matters", "Medicine · Climate · Materials · Bioengineering", [])
    d = ImageDraw.Draw(img)
    quads = ["Medicine", "Climate", "Materials", "Bioengineering"]
    for i, q in enumerate(quads):
        x = 1100 + (i % 2) * 320
        y = 400 + (i // 2) * 200
        hi = i == int(t * 4) % 4
        d.rectangle([x, y, x + 280, y + 160], outline=ACCENT if hi else MUTED, width=3)
        d.text((x + 60, y + 65), q, font=HEAD_FONT, fill=TEXT if hi else MUTED)


def paint_closing(img: Image.Image, t: float) -> None:
    d = ImageDraw.Draw(img)
    stages = ["Tools", "Models", "Agents", "Scientific intelligence systems"]
    for i, s in enumerate(stages):
        x = 200 + i * 420
        on = i <= int(t * 4)
        d.rounded_rectangle([x, 480, x + 360, 580], radius=12, outline=ACCENT if on else MUTED, width=3)
        d.text((x + 40, 520), s, font=BODY_FONT, fill=TEXT if on else MUTED)
    d.text((90, 60), "From Narrow Models → Adaptive Scientific Intelligence", font=TITLE_FONT, fill=TEXT)
    d.text((500, 720), "Toward adaptive scientific intelligence", font=HEAD_FONT, fill=ACCENT)


def clean_narration(text: str) -> str:
    text = re.sub(r"\[pause\]|\[beat\]", " ", text, flags=re.I)
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


SLIDES: List[Slide] = [
    Slide(
        "Opening Vision",
        "",
        [],
        clean_narration(
            "Modern artificial intelligence has achieved remarkable results on fixed tasks and curated benchmarks. "
            "Yet scientific discovery does not happen inside a frozen dataset. It happens in unfamiliar worlds—where rules are hidden, "
            "experiments change what you see, and the right move is rarely obvious in advance. "
            "This presentation is about a different goal: not another narrow model, but adaptive scientific intelligence—systems built to explore, "
            "infer, and adapt when the environment itself is unknown."
        ),
        paint_opening,
    ),
    Slide(
        "Static vs Interactive",
        "",
        [],
        clean_narration(
            "Much of today's AI is optimized for static prediction: given inputs, produce outputs. "
            "That works when the task is fixed and the world does not fight back. Scientific discovery breaks those assumptions. "
            "You rarely know the full mechanism upfront. Benchmarks reward pattern matching, not mechanism discovery. "
            "Exploration is treated as an afterthought. Hidden structure stays hidden. "
            "The gap is not raw compute—it is architecture: we need systems that infer what they cannot see and adapt when the world responds to action."
        ),
        paint_static_vs,
    ),
    Slide(
        "Science Loop",
        "",
        [],
        clean_narration(
            "At its core, science is not a single forward pass. It is a loop. You observe a phenomenon. You form a hypothesis. "
            "You design an experiment. You infer from what changed—and what did not. You adapt your model of the world. "
            "Only then does discovery become possible. Framing science this way defines what we should build: not passive predictors, "
            "but interactive reasoners that treat experimentation as first-class intelligence."
        ),
        paint_loop,
    ),
    Slide(
        "Introducing A-S-R-A",
        "",
        [],
        clean_narration(
            "A-S-R-A—the Adaptive Scientific Reasoning Architecture—is not positioned as another task-specific model. "
            "It is a reasoning substrate: an engine meant to operate in environments where rules are unfamiliar, actions have unknown semantics, "
            "and understanding must be earned through interaction. It connects observation, experimentation, memory, and abstraction into one adaptive loop. "
            "Think of it as the layer beneath domain science—the machinery that lets scientific intelligence stay coherent when the world is not fully specified."
        ),
        paint_asra_hub,
    ),
    Slide(
        "Hidden Mechanics",
        "",
        [],
        clean_narration(
            "A central capability is hidden-mechanics inference: reasoning under uncertainty about how the world actually works. "
            "The agent does not receive a complete specification of action semantics or environmental dynamics. "
            "It must infer latent structure from consequences—what changed when an action was taken, what stayed invariant, what patterns repeat. "
            "This is the difference between answering questions in a closed world and learning the rules of an open one."
        ),
        paint_hidden,
    ),
    Slide(
        "Exploration",
        "",
        [],
        clean_narration(
            "A-S-R-A learns by interacting. It probes the environment, compares outcomes, and updates beliefs. "
            "Exploration is not random wandering—it is structured uncertainty reduction. Policies adapt as evidence accumulates. "
            "World models sharpen where data is rich and stay cautious where it is sparse. "
            "In this view, intelligence is inseparable from the quality of experimentation: the system must choose actions that reveal structure, "
            "not merely actions that score well on a known metric."
        ),
        paint_explore,
    ),
    Slide(
        "Strategy",
        "",
        [],
        clean_narration(
            "Memorization solves yesterday's tasks. Adaptive strategy invention solves tomorrow's environments. "
            "When conditions shift, a rigid playbook fails. A-S-R-A is designed so strategies can be formed and revised as structure becomes visible—"
            "new pathways through state space, new action sequences, new abstractions. "
            "This is closer to fluid intelligence than to pattern replay: behavior composed from what the system has learned about the world, not from a fixed script."
        ),
        paint_strategy,
    ),
    Slide(
        "Why Biology",
        "",
        [],
        clean_narration(
            "Why biology first? Because the cell is already an adaptive information-processing system. "
            "It receives noisy signals from an uncertain environment. It must decide how to respond—often before full information arrives. "
            "Survival depends on inference, not on perfect sensors. Decision Biology begins here: treating biological systems as computational agents "
            "operating under noise, constraint, and feedback."
        ),
        paint_cell,
    ),
    Slide(
        "Decision Biology",
        "",
        [],
        clean_narration(
            "Decision Biology is the first scientific domain mounted on A-S-R-A. It models signaling, uncertainty, adaptation, and cellular inference "
            "as a unified information-flow problem. Pathways are not just chemistry—they are communication channels with fidelity limits, feedback, and failure modes. "
            "State transitions are probabilistic. The goal is to reason about how cells interpret their world and how collective behavior emerges from local decisions."
        ),
        paint_pathway,
    ),
    Slide(
        "Cellular Intelligence",
        "",
        [],
        clean_narration(
            "Cells process information, make probabilistic decisions, and adapt to changing conditions. "
            "No single cell sees the whole organism—but coordination still emerges. Cellular intelligence is distributed: local rules, global outcomes. "
            "Bridging A-S-R-A and Decision Biology lets us ask systems-level questions—how inference at one scale constrains behavior at another—without reducing biology to metaphor."
        ),
        paint_cellular_net,
    ),
    Slide(
        "Information Theory",
        "",
        [],
        clean_narration(
            "Decision Biology connects naturally to information theory. Entropy measures uncertainty. Mutual information measures what one variable tells us about another. "
            "Biological channels are noisy—ligands, receptors, cascades, phenotypes each add distortion and delay. "
            "Reasoning about fidelity and capacity is how we formalize when a cell can trust a signal and when it must hedge. "
            "This grounds adaptive reasoning in measurable science."
        ),
        paint_channel,
    ),
    Slide(
        "Nature FM",
        "",
        [],
        clean_narration(
            "Nature Foundation Models widen the aperture. Biology is the first domain—not the only one. "
            "The same scientific intelligence stack must eventually speak to chemistry, physics, materials, and environmental systems—because nature is not siloed. "
            "Interactions cross domains: molecular structure affects function; physical constraints shape biological possibility. "
            "A foundation model for nature is a bet on shared structure beneath diverse phenomena."
        ),
        paint_domains,
    ),
    Slide(
        "Hierarchy",
        "",
        [],
        clean_narration(
            "Here is the hierarchy to remember. A-S-R-A is the adaptive reasoning engine—the substrate. "
            "Decision Biology is the first scientific domain where that engine meets real biological structure. "
            "Nature Foundation Models is the broader ecosystem: unified capability for reasoning, simulation, experimentation, and abstraction across scientific fields. "
            "One engine. Deepening domains. Expanding scope. That is the architectural story."
        ),
        paint_hierarchy,
    ),
    Slide(
        "Scientific Agents",
        "",
        [],
        clean_narration(
            "The next layer is agency. Future scientific systems will not only answer queries—they will propose hypotheses, design experiments, "
            "run simulations, collaborate with other agents, and validate claims against evidence. "
            "Scientific agents are collaborators in discovery, operating inside shared reasoning environments. "
            "A-S-R-A supplies the adaptive core; domains like Decision Biology supply grounding; Nature Foundation Models supply breadth."
        ),
        paint_agents,
    ),
    Slide(
        "Ecosystem",
        "",
        [],
        clean_narration(
            "At scale, these pieces become infrastructure: scientific operating systems where discovery is continuous, auditable, and shared. "
            "Not a single model in a notebook—a collaborative reasoning environment. Memory persists across experiments. "
            "Graphs capture what was tried. Replay makes science inspectable. Export makes experience reusable. "
            "This is how adaptive intelligence becomes institutional, not anecdotal."
        ),
        paint_ecosystem,
    ),
    Slide(
        "Why This Matters",
        "",
        [],
        clean_narration(
            "The stakes are practical. Adaptive scientific intelligence could accelerate medicine by improving how we model cellular decision-making under disease. "
            "It could sharpen climate and environmental models where systems are coupled and nonlinear. "
            "It could aid materials discovery where experiments are costly and mechanisms are partial. "
            "The through-line is the same: fewer brittle pipelines, more systems that learn how nature works by interacting with it carefully and remembering what they found."
        ),
        paint_impact,
    ),
    Slide(
        "Final Vision",
        "",
        [],
        clean_narration(
            "We are moving from narrow models to adaptive scientific intelligence systems. "
            "From tools that answer prompts to architectures that observe, experiment, infer, and remember. "
            "A-S-R-A provides the reasoning engine. Decision Biology grounds it in life. Nature Foundation Models extend it across science. "
            "The invitation is not hype—it is engineering discipline applied to the hardest problem we have: "
            "understanding a world that does not reveal its rules on the first try. That is the future worth building."
        ),
        paint_closing,
    ),
]


def render_frame(slide: Slide, t: float) -> np.ndarray:
    img = base_canvas()
    slide.painter(img, min(1.0, t))
    return np.array(img)


def tts_to_wav(text: str, wav_path: Path) -> None:
    spoken = text.replace("A-S-R-A", "A S R A")
    aiff = wav_path.with_suffix(".aiff")
    subprocess.run(["say", "-v", "Samantha", "-r", "165", "-o", str(aiff), spoken], check=True)
    subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", str(aiff), str(wav_path)], check=True)
    aiff.unlink(missing_ok=True)


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def build_video() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    clips = []
    for idx, slide in enumerate(SLIDES):
        wav = BUILD_DIR / f"slide_{idx:02d}.wav"
        print(f"TTS {idx + 1}/{len(SLIDES)}: {slide.title}")
        tts_to_wav(slide.narration, wav)
        duration = max(8.0, wav_duration(wav) + 0.8)

        def make_frame(t, s=slide, d=duration):
            return render_frame(s, t / max(d - 1.0, 1))

        clip = VideoClip(make_frame, duration=duration).with_audio(AudioFileClip(str(wav)))
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    print(f"Writing {OUT_MP4} ...")
    final.write_videofile(str(OUT_MP4), fps=FPS, codec="libx264", audio_codec="aac", preset="medium", threads=4, logger=None)
    for c in clips:
        c.close()
    final.close()
    meta = {"slides": len(SLIDES), "output": str(OUT_MP4), "duration_target": "15-18 min"}
    (ROOT / "video-render-meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build_video()
