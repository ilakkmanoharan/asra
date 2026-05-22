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


if __name__ == "__main__":
    main()
