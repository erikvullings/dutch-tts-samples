#!/usr/bin/env python3
"""Generate comparable TTS samples with LiquidAI LFM3-Audio through MLX-VLM."""

import argparse
import subprocess
import sys
from pathlib import Path

from common import PROMPTS, ROOT, prompts as select_prompts

MODEL_ID = "LiquidAI/LFM3-Audio-2B-MLX-4bit"
DEFAULT_PROMPTS = ["nl-short", "nl-long", "nl-long-normalized", "en-short", "en-long"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL_ID)
    parser.add_argument("--prompts", nargs="*", choices=PROMPTS, default=DEFAULT_PROMPTS)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "samples" / "lfm3-audio")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, text in select_prompts(args.prompts):
        language = "Dutch" if name.startswith("nl-") else "American English"
        output = args.output_dir / f"lfm3-audio-{name}.wav"
        command = [
            sys.executable, "-m", "mlx_vlm.generate",
            "--model", args.model,
            "--system", f"Perform TTS in {language} using a female voice.",
            "--prompt", text,
            "--output-modality", "audio",
            "--output", str(output),
        ]
        subprocess.run(command, check=True)
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError(f"MLX-VLM did not create a non-empty WAV: {output}")
        print(f"Wrote {output}", flush=True)


if __name__ == "__main__":
    main()
