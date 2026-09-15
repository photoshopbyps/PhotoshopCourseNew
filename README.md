# ASMR Image Production Pipeline

`production_pipeline.py` creates 10 clip folders (`Clip_01` to `Clip_10`), each with S01–S32 metadata and, when enabled, PNG images saved as `Clip_01/S01.png`. It also writes `storyboard_index.json`, an interactive `dashboard.html`, and a sibling ZIP archive.

Install the SDK, then set `OPENAI_API_KEY` in your shell (never place a real key in this repository):

```bash
python3 -m pip install -r requirements.txt
export OPENAI_API_KEY="..."
```

Test the full folder/JSON/dashboard/ZIP structure without API calls:

```bash
python3 production_pipeline.py --metadata-only --no-llm
```

Generate metadata with the LLM and make one paid image smoke test:

```bash
python3 production_pipeline.py --max-images 1
```

Generate all 320 images:

```bash
python3 production_pipeline.py --skip-existing
```

Open ` ` in a browser. Missing images are dimmed; click a generated frame for an in-page preview. The script uses the official OpenAI Python SDK, Responses API for LLM metadata, and Images API for PNG generation. Configure `--llm-model`, `--image-model`, and `--image-size` for your account.
