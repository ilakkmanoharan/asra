One-time setup

cd /Users/ilakkmanoharan2026/Projects/asra/asra-arc
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev,viewer,graph]'
Run one episode (mock ARC environment)

cd /Users/ilakkmanoharan2026/Projects/asra/asra-arc
source .venv/bin/activate
python -m asra run-episode --game-id GAME_ID --level-id LEVEL_ID --max-steps 200 --output-dir data/episodes
Optional: replay that episode (use the episode_id printed in the output, or from data/transitions/*.jsonl filenames)

python -m asra replay --episode-id EPISODE_ID
Optional: Streamlit viewer


streamlit run src/asra/viewer/streamlit_app.py






_______
__________


Here is what ran successfully on your machine:

Setup — python3 -m venv .venv, activated it, upgraded pip, and ran pip install -e '.[dev,viewer,graph]' (finished without errors).

Episode — This command completed with exit code 0:

cd /Users/ilakkmanoharan2026/Projects/asra/asra-arc
source .venv/bin/activate
python -m asra run-episode --game-id GAME_ID --level-id LEVEL_ID --max-steps 200 --output-dir data/episodes
This run’s episode id: 5830e744-ad91-4cbb-93be-f38949366c7e

Logs are under:

asra-arc/data/transitions/5830e744-ad91-4cbb-93be-f38949366c7e.jsonl
asra-arc/data/episodes/5830e744-ad91-4cbb-93be-f38949366c7e.json
Replay that episode:

cd /Users/ilakkmanoharan2026/Projects/asra/asra-arc
source .venv/bin/activate
python -m asra replay --episode-id 5830e744-ad91-4cbb-93be-f38949366c7e
Note: the CLI prints the full EpisodeResult (one very long line). For a shorter view, use replay or open the JSONL file in an editor.