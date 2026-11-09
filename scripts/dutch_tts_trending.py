#!/usr/bin/env python3
"""Reproduce the 2026 trending Dutch TTS checks on Apple Silicon."""

import argparse

import numpy as np

from common import PROMPTS, ROOT, prompts as select_prompts

MODELS = {
    "audio8-realistic-air": {
        "repo": "groxaxo/Audio8-TTS-Realistic-Air-MLX8-Selective",
        "revision": "e37e231bd802c804c59b5ee25ef23f2d2195cba1",
        "kwargs": {"seed": 20261109, "max_tokens": 1024},
    },
    "higgs-tts3": {
        "repo": "whitelabel/mlx-q6-higgs-tts-3-4b",
        "revision": "7a91348cfaf6847e3969c00348b09d2c5fc36c06",
        "kwargs": {},
    },
    "voxcpm2": {
        "repo": "mlx-community/VoxCPM2-4bit",
        "revision": "dc9e5c187858da5f4a13dc4c247e297339216381",
        "kwargs": {
            "inference_timesteps": 7,
            "cfg_value": 2.0,
            "instruct": "A gentle female voice speaking in a natural, conversational tone.",
        },
    },
    "fish-s2-pro": {
        "repo": "mlx-community/fish-audio-s2-pro-8bit",
        "revision": "c8d4481b3f7cbfe64d855c8b7cda7739502fc3ff",
        "kwargs": {},
    },
}
PROMPT_NAMES = ["nl-short", "nl-long", "nl-long-normalized", "en-short", "en-long"]


def generate_mlx(engine, prompts):
    from mlx_audio.audio_io import write as audio_write
    from mlx_audio.tts.utils import load_model

    config = MODELS[engine]
    model_path = ROOT / "models" / engine
    if not (model_path / "config.json").is_file():
        raise FileNotFoundError(
            f"Download {config['repo']} at revision {config['revision']} into {model_path}"
        )
    model = load_model(str(model_path))
    for name, text in prompts:
        chunks = []
        sample_rate = None
        for result in model.generate(text=text, **config["kwargs"]):
            chunks.append(np.asarray(result.audio, dtype=np.float32).reshape(-1))
            sample_rate = result.sample_rate
        if not chunks or not sample_rate:
            raise RuntimeError(f"{engine} generated no audio for {name}")
        output = ROOT / "samples" / engine / f"{engine}-{name}.wav"
        output.parent.mkdir(parents=True, exist_ok=True)
        audio_write(str(output), np.concatenate(chunks), sample_rate)
        print(f"Wrote {output}", flush=True)


def generate_supertonic(prompts):
    from supertonic import TTS

    model_path = ROOT / "models" / "supertonic-3"
    tts = TTS(model_dir=model_path, auto_download=False)
    style = tts.get_voice_style("F1")
    for name, text in prompts:
        audio, _ = tts.synthesize(text, voice_style=style, lang="nl" if name.startswith("nl-") else "en")
        output = ROOT / "samples" / "supertonic3" / f"supertonic3-{name}.wav"
        output.parent.mkdir(parents=True, exist_ok=True)
        tts.save_audio(audio, str(output))
        print(f"Wrote {output}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=[*MODELS, "supertonic3"], action="append")
    parser.add_argument("--prompts", nargs="*", choices=PROMPT_NAMES, default=PROMPT_NAMES)
    args = parser.parse_args()
    selected = args.engine or [*MODELS, "supertonic3"]
    selected_prompts = select_prompts(args.prompts)
    for engine in selected:
        if engine == "supertonic3":
            generate_supertonic(selected_prompts)
        else:
            generate_mlx(engine, selected_prompts)


if __name__ == "__main__":
    main()
