---
name: tts-sample-upkeep
description: Use when adding or refreshing a text-to-speech (TTS) engine or audio samples in this repository, or updating its generated GitHub Pages player.
---

# TTS sample upkeep

1. Read `scripts/common.py` for the canonical prompts and `scripts/build_pages.py` for the player conventions. Keep prompt wording unchanged when the engine supports it.
2. Choose a checkpoint and quantization supported by the current machine. On Apple Silicon, prefer an upstream MLX checkpoint when available. Check free disk and memory before downloading.
3. Read the model card and the full license text, including any separate output terms. Record the exact checkpoint, runtime version, license URL, and a concise plain-language summary. Ask before proceeding if permission to publish the generated audio is unclear.
4. Create an isolated runtime and download weights only into one dedicated directory under ignored `models/`. Keep a runnable script in `scripts/` that records the model, prompts, generation settings, and output filenames; generate the comparable canonical prompts where supported.
5. Save generated WAVs under `samples/<engine>/`. Check each file is valid and non-empty, listen to the outputs, and report audible issues rather than treating generation success as a quality check.
6. Add the engine to `scripts/build_pages.py`, the main README sample table and reproduction instructions, and `SAMPLES-LICENSE.md`. Run `python3 scripts/build_pages.py`, then verify the generated page and sample README link every committed WAV.
7. Remove the exact downloaded model directory after generation when requested, and verify it is absent while the reproduction script and generated samples remain.
