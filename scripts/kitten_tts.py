#!/usr/bin/env python3
"""KittenTTS 2 with its named preset voices (MLX language model + MPS decoder)."""

import argparse
import os

import numpy as np
import soundfile as sf
from kittenml import KittenTTS

from common import MODELS, OUTPUT, WARMUP, Measure, prompts, save_results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", default=str(MODELS / "kitten"), help="local snapshot of KittenML/kitten-tts-2")
    ap.add_argument("--nl-voice", default="DutchWeatherPresenter")
    ap.add_argument("--en-voice", default="Maeve")
    ap.add_argument("--prefix", default="kitten")
    ap.add_argument("--prompts", nargs="*")
    args = ap.parse_args()

    model = KittenTTS(args.model_dir, backend="mlx", cache_dir=str(MODELS / "hf-cache"))
    sr = model.sample_rate
    rows = []
    for lang, voice in (("nl", args.nl_voice), ("en", args.en_voice)):
        selected = [(k, v) for k, v in prompts(args.prompts) if k.startswith(lang)]
        if not selected:
            continue
        # The built-in normaliser is English-only, so Dutch text is passed through unchanged.
        normalize = lang == "en"
        for name, text in [(f"{lang}-warmup", WARMUP[lang]), *selected]:
            parts = []
            with Measure() as m:
                for wav in model.generate_stream(text, voice=voice, normalize=normalize,
                                                 advanced={"seed": 42}):
                    m.chunk()
                    parts.append(np.asarray(wav, dtype=np.float32).reshape(-1))
            audio = np.concatenate(parts)
            path = None
            if "warmup" not in name:
                path = OUTPUT / f"{args.prefix}-{name}.wav"
                os.makedirs(path.parent, exist_ok=True)
                sf.write(path, audio, sr, subtype="PCM_16")
            rows.append(m.row(audio.size / sr, engine="kittentts2-mlx", voice=voice, prompt=name,
                              chunks=len(parts), file=str(path) if path else None))
            print(rows[-1], flush=True)
    save_results(args.prefix, rows)


if __name__ == "__main__":
    main()
