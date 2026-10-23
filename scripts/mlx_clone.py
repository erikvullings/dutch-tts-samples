#!/usr/bin/env python3
"""Voice cloning through mlx-audio (used for mlx-community/OmniVoice-bf16)."""

import argparse
import json

import mlx.core as mx
import numpy as np
from mlx_audio.audio_io import write as audio_write
from mlx_audio.tts.utils import load_model

from common import OUTPUT, REFERENCES, WARMUP, Measure, prompts, reference, save_results

DEFAULT_PROMPTS = ["nl-short", "nl-long", "nl-long-normalized", "en-short"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mlx-community/OmniVoice-bf16")
    ap.add_argument("--prefix", default="omnivoice")
    ap.add_argument("--reference", default="piper-female")
    ap.add_argument("--extra", default="{}", help="JSON kwargs passed to generate()")
    ap.add_argument("--prompts", nargs="*", default=DEFAULT_PROMPTS)
    args = ap.parse_args()
    extra = json.loads(args.extra)

    model = load_model(args.model)
    rows = []
    jobs = [("nl-warmup", WARMUP["nl"]), *prompts(args.prompts)]
    for name, text in jobs:
        lang = name[:2]
        mx.reset_peak_memory()
        chunks, sr = [], None
        with Measure() as m:
            for res in model.generate(text=text, ref_audio=str(reference(f"{args.reference}-{lang}")),
                                      ref_text=REFERENCES[lang], language=lang, **extra):
                m.chunk()
                chunks.append(np.asarray(res.audio, dtype=np.float32).reshape(-1))
                sr = res.sample_rate
        audio = np.concatenate(chunks)
        path = None
        if "warmup" not in name:
            path = OUTPUT / f"{args.prefix}-{name}.wav"
            path.parent.mkdir(parents=True, exist_ok=True)
            audio_write(str(path), audio, sr)
        rows.append(m.row(audio.size / sr, engine=args.prefix, model=args.model, prompt=name,
                          metal_peak_bytes=mx.get_peak_memory(), file=str(path) if path else None))
        print(rows[-1], flush=True)
    save_results(args.prefix, rows)


if __name__ == "__main__":
    main()
