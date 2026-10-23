#!/usr/bin/env python3
"""Chatterbox Multilingual (V3 T3 checkpoint) on MPS, cloning a reference clip.

Needs the GitHub version of chatterbox (PyPI 0.1.7 always loads the v2 checkpoint).
Every output carries Resemble's imperceptible Perth watermark.
"""

import argparse
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from huggingface_hub import snapshot_download
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

from common import OUTPUT, WARMUP, Measure, prompts, reference, save_results

DEFAULT_PROMPTS = ["nl-short", "nl-long", "nl-long-normalized", "en-short"]
FILES = ["ve.pt", "t3_mtl23ls_v3.safetensors", "s3gen.pt", "grapheme_mtl_merged_expanded_v1.json",
         "conds.pt", "Cangjie5_TC.json"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint-dir", help="local ResembleAI/chatterbox snapshot (downloaded if omitted)")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--reference", default="piper-female")
    ap.add_argument("--prefix", default="chatterbox")
    ap.add_argument("--prompts", nargs="*", default=DEFAULT_PROMPTS)
    args = ap.parse_args()

    ckpt = Path(args.checkpoint_dir or snapshot_download("ResembleAI/chatterbox", allow_patterns=FILES))
    model = ChatterboxMultilingualTTS.from_local(ckpt, args.device, t3_model="v3")
    rows = []
    for name, text in [("nl-warmup", WARMUP["nl"]), *prompts(args.prompts)]:
        lang = name[:2]
        torch.manual_seed(42)
        if args.device == "mps":
            torch.mps.manual_seed(42)
        with Measure() as m:
            wav = model.generate(text, language_id=lang,
                                 audio_prompt_path=str(reference(f"{args.reference}-{lang}")))
        audio = wav.squeeze(0).float().cpu().numpy()
        path = None
        if "warmup" not in name:
            path = OUTPUT / f"{args.prefix}-{name}.wav"
            path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(path, np.clip(audio, -1, 1), model.sr, subtype="PCM_16")
        rows.append(m.row(audio.size / model.sr, engine="chatterbox-mtl-v3", prompt=name,
                          file=str(path) if path else None))
        print(rows[-1], flush=True)
    save_results(args.prefix, rows)


if __name__ == "__main__":
    main()
