from __future__ import annotations

import argparse
from pathlib import Path

from asra.agent.baseline_agent import BaselineAgent
from asra.env.arc_agi3_runner import ArcAGI3Runner
from asra.export.dataset_exporter import export_dataset
from asra.memory.state_graph import build_graph_from_transition_dir
from asra.viewer.replay_viewer import replay_episode


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m asra")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run-episode")
    run.add_argument("--game-id", default="mock-game")
    run.add_argument("--level-id", default="mock-level")
    run.add_argument("--max-steps", type=int, default=200)
    run.add_argument("--output-dir", default="data/episodes")

    batch = sub.add_parser("run-batch")
    batch.add_argument("--num-episodes", type=int, default=50)
    batch.add_argument("--max-steps", type=int, default=200)
    batch.add_argument("--data-dir", default="data")

    export = sub.add_parser("export-dataset")
    export.add_argument("--input-dir", default="data/transitions")
    export.add_argument("--output-dir", default="data/exports")

    graph = sub.add_parser("build-graph")
    graph.add_argument("--input-dir", default="data/transitions")
    graph.add_argument("--output", default="data/graphs/state_graph.json")

    replay = sub.add_parser("replay")
    replay.add_argument("--episode-id", required=True)
    replay.add_argument("--data-dir", default="data")

    args = parser.parse_args()
    if args.command == "run-episode":
        data_dir = str(Path(args.output_dir).parent) if Path(args.output_dir).name == "episodes" else args.output_dir
        result = ArcAGI3Runner(game_id=args.game_id, level_id=args.level_id, data_dir=data_dir).run_episode(BaselineAgent(), args.max_steps)
        print(result)
    elif args.command == "run-batch":
        for _ in range(args.num_episodes):
            print(ArcAGI3Runner(data_dir=args.data_dir).run_episode(BaselineAgent(), args.max_steps))
    elif args.command == "export-dataset":
        print(export_dataset(args.input_dir, args.output_dir))
    elif args.command == "build-graph":
        graph_obj = build_graph_from_transition_dir(args.input_dir)
        graph_obj.save(args.output)
        print(args.output)
    elif args.command == "replay":
        replay_episode(args.episode_id, args.data_dir)


if __name__ == "__main__":
    main()
