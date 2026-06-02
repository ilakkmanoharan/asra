from __future__ import annotations

import argparse
from pathlib import Path

from asra.agent.baseline_agent import BaselineAgent
from asra.env.arc_agi3_runner import ArcAGI3Runner
from asra.env.backend_factory import create_backend
from asra.export.dataset_exporter import export_dataset
from asra.memory.state_graph import build_graph_from_transition_dir
from asra.viewer.replay_viewer import replay_episode


def _runner_from_args(args: argparse.Namespace) -> ArcAGI3Runner:
    backend = create_backend(
        mock=args.mock,
        replay_file=args.replay_file,
        live=args.live,
        terminal_demo=getattr(args, "terminal_demo", False),
    )
    data_dir = getattr(args, "data_dir", "data")
    return ArcAGI3Runner(backend=backend, game_id=args.game_id, level_id=args.level_id, data_dir=data_dir)


def _add_backend_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--mock", action="store_true", help="Use mock ARC environment (default for offline runs)")
    group.add_argument("--live", action="store_true", help="Use live ARC-AGI-3 API (requires env credentials)")
    parser.add_argument("--replay-file", default=None, help="Path to offline ARC-AGI-3 replay JSON")
    parser.add_argument("--terminal-demo", action="store_true", help="Mock scenario that reaches WIN quickly")


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m asra")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run-episode")
    run.add_argument("--game-id", default="mock-game")
    run.add_argument("--level-id", default="mock-level")
    run.add_argument("--max-steps", type=int, default=200)
    run.add_argument("--output-dir", default="data/episodes")
    run.add_argument("--data-dir", default="data")
    _add_backend_args(run)
    run.set_defaults(mock=True)

    batch = sub.add_parser("run-batch")
    batch.add_argument("--num-episodes", type=int, default=50)
    batch.add_argument("--max-steps", type=int, default=200)
    batch.add_argument("--data-dir", default="data")
    batch.add_argument("--game-id", default="mock-game")
    batch.add_argument("--level-id", default="mock-level")
    _add_backend_args(batch)
    batch.set_defaults(mock=True)

    export = sub.add_parser("export-dataset")
    export.add_argument("--input-dir", default="data/transitions")
    export.add_argument("--output-dir", default="data/exports")

    graph = sub.add_parser("build-graph")
    graph.add_argument("--input-dir", default="data/transitions")
    graph.add_argument("--output", default="data/graphs/state_graph.json")

    replay = sub.add_parser("replay")
    replay.add_argument("--episode-id", required=True)
    replay.add_argument("--data-dir", default="data")

    complete = sub.add_parser("complete-phase1")
    complete.add_argument("--data-dir", default="data")

    scale = sub.add_parser("run-scale")
    scale.add_argument("--num-episodes", type=int, default=10_000)
    scale.add_argument("--max-steps", type=int, default=50)
    scale.add_argument("--data-dir", default="data")
    scale.set_defaults(mock=True)

    viz = sub.add_parser("visualize-graph")
    viz.add_argument("--graph", default="data/graphs/state_graph.json")
    viz.add_argument("--out-dir", default="data/analysis/graph_viz")

    phase2 = sub.add_parser("run-phase2", help="Run Phase 2 perception on ARC tasks")
    phase2.add_argument("--arc-root", required=True, help="Directory of ARC task folders or JSON files")
    phase2.add_argument("--output-dir", default="data/analysis/phase2/reports")

    minigrid = sub.add_parser("run-minigrid", help="Run Phase 3 MiniGrid episodes with exploration v2")
    minigrid.add_argument("--env", default="MiniGrid-Empty-8x8-v0")
    minigrid.add_argument("--episodes", type=int, default=10)
    minigrid.add_argument("--max-steps", type=int, default=200)
    minigrid.add_argument("--data-dir", default="data/minigrid")
    minigrid.add_argument("--seed", type=int, default=42)
    minigrid.add_argument("--object-scenes", action="store_true")

    babyai = sub.add_parser("run-babyai", help="Run Phase 3 BabyAI episodes with subgoal tagging")
    babyai.add_argument("--env", default="BabyAI-GoToRedBallGrey-v0")
    babyai.add_argument("--episodes", type=int, default=10)
    babyai.add_argument("--max-steps", type=int, default=200)
    babyai.add_argument("--data-dir", default="data/babyai")
    babyai.add_argument("--seed", type=int, default=42)

    arc_exp = sub.add_parser("run-arc-exploration", help="Run ARC-AGI-3 episode with Phase 3 exploration engine")
    arc_exp.add_argument("--max-steps", type=int, default=200)
    arc_exp.add_argument("--data-dir", default="data/arc_exploration")
    arc_exp.add_argument("--game-id", default="mock-game")
    arc_exp.add_argument("--level-id", default="mock-level")
    _add_backend_args(arc_exp)
    arc_exp.set_defaults(mock=True)

    doorkey_bench = sub.add_parser("eval-doorkey", help="Benchmark DoorKey: Phase 3 v2 vs Phase 1 baseline")
    doorkey_bench.add_argument("--env", default="MiniGrid-DoorKey-8x8-v0")
    doorkey_bench.add_argument("--episodes", type=int, default=20)
    doorkey_bench.add_argument("--max-steps", type=int, default=300)
    doorkey_bench.add_argument("--seed", type=int, default=42)
    doorkey_bench.add_argument("--output", default="data/analysis/phase3/doorkey_benchmark.json")

    exp_graph = sub.add_parser("build-exploration-graph", help="Build Phase 3 exploration graph from transitions")
    exp_graph.add_argument("--input-dir", default="data/minigrid/transitions")
    exp_graph.add_argument("--output", default="data/minigrid/graphs/exploration_graph.json")

    args = parser.parse_args()

    if args.command == "run-episode":
        if not args.mock and not args.live and not args.replay_file:
            args.mock = True
        data_dir = str(Path(args.output_dir).parent) if Path(args.output_dir).name == "episodes" else args.data_dir
        args.data_dir = data_dir
        result = _runner_from_args(args).run_episode(BaselineAgent(), args.max_steps)
        print(result)
    elif args.command == "run-batch":
        if not args.mock and not args.live and not args.replay_file:
            args.mock = True
        for i in range(args.num_episodes):
            runner = _runner_from_args(args)
            print(f"episode {i + 1}/{args.num_episodes}", runner.run_episode(BaselineAgent(), args.max_steps))
    elif args.command == "export-dataset":
        print(export_dataset(args.input_dir, args.output_dir))
    elif args.command == "build-graph":
        graph_obj = build_graph_from_transition_dir(args.input_dir)
        graph_obj.save(args.output)
        print(args.output)
    elif args.command == "replay":
        replay_episode(args.episode_id, args.data_dir)
    elif args.command == "complete-phase1":
        import subprocess
        import sys

        script = Path(__file__).resolve().parents[2] / "scripts" / "complete_phase1.py"
        subprocess.run([sys.executable, str(script)], cwd=script.parent.parent, check=True)
    elif args.command == "run-scale":
        import subprocess
        import sys

        script = Path(__file__).resolve().parents[2] / "scripts" / "run_large_scale.py"
        cmd = [sys.executable, str(script), "--num-episodes", str(args.num_episodes), "--max-steps", str(args.max_steps), "--data-dir", args.data_dir]
        subprocess.run(cmd, cwd=script.parent.parent, check=True)
    elif args.command == "visualize-graph":
        import subprocess
        import sys

        script = Path(__file__).resolve().parents[2] / "scripts" / "visualize_state_graph.py"
        subprocess.run([sys.executable, str(script), "--graph", args.graph, "--out-dir", args.out_dir], cwd=script.parent.parent, check=True)
    elif args.command == "run-phase2":
        from asra.perception import run_phase2_batch

        paths = run_phase2_batch(args.arc_root, args.output_dir)
        print(f"Wrote {len(paths)} task reports to {args.output_dir}")
        for p in paths[:10]:
            print(p)
        if len(paths) > 10:
            print(f"... and {len(paths) - 10} more")
    elif args.command == "run-minigrid":
        from asra.exploration import run_minigrid_batch

        results = run_minigrid_batch(
            args.env,
            episodes=args.episodes,
            max_steps=args.max_steps,
            data_dir=args.data_dir,
            seed=args.seed,
        )
        for r in results:
            print(r)
        print(f"Completed {len(results)} episodes")
    elif args.command == "run-babyai":
        from asra.exploration import run_babyai_batch

        results = run_babyai_batch(
            args.env,
            episodes=args.episodes,
            max_steps=args.max_steps,
            data_dir=args.data_dir,
            seed=args.seed,
        )
        for r in results:
            print(r)
        print(f"Completed {len(results)} BabyAI episodes")
    elif args.command == "run-arc-exploration":
        from asra.exploration.arc_exploration import ArcExplorationRunner

        if not args.mock and not args.live and not args.replay_file:
            args.mock = True
        runner = ArcExplorationRunner(_runner_from_args(args), data_dir=args.data_dir)
        result = runner.run_episode(max_steps=args.max_steps)
        print(result)
    elif args.command == "eval-doorkey":
        import subprocess
        import sys

        script = Path(__file__).resolve().parents[2] / "scripts" / "eval_phase3_doorkey_benchmark.py"
        cmd = [
            sys.executable,
            str(script),
            "--env",
            args.env,
            "--episodes",
            str(args.episodes),
            "--max-steps",
            str(args.max_steps),
            "--seed",
            str(args.seed),
            "--output",
            args.output,
        ]
        subprocess.run(cmd, cwd=script.parent.parent, check=True)
    elif args.command == "build-exploration-graph":
        from asra.exploration import build_exploration_graph_from_transitions

        graph = build_exploration_graph_from_transitions(args.input_dir)
        graph.save(args.output)
        print(f"Wrote {args.output} ({graph.unique_nodes()} nodes)")


if __name__ == "__main__":
    main()
