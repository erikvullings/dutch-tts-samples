#!/usr/bin/env python3
"""Parkiet (Dutch fine-tune of Dia-1.6B) via transformers on MPS, cloning a reference clip."""

import argparse

import numpy as np
import soundfile as sf
import torch
from scipy.signal import resample_poly
from transformers import AutoProcessor, DiaForConditionalGeneration

from common import OUTPUT, REFERENCES, WARMUP, Measure, prompts, reference, save_results

DEFAULT_PROMPTS = ["nl-short", "nl-long", "nl-long-normalized", "en-short"]
SR = 44100


def load_reference(path):
    pcm, sr = sf.read(path, dtype="float32")
    assert sr == 22050, f"expected a 22.05 kHz Piper reference, got {sr}"
    return resample_poly(pcm, 2, 1).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="pevers/parkiet")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--reference", default="piper-female")
    ap.add_argument("--prefix", default="parkiet")
    ap.add_argument("--prompts", nargs="*", default=DEFAULT_PROMPTS)
    args = ap.parse_args()

    processor = AutoProcessor.from_pretrained(args.repo)
    model = DiaForConditionalGeneration.from_pretrained(args.repo).to(args.device).eval()
    refs = {lang: load_reference(reference(f"{args.reference}-{lang}")) for lang in ("nl", "en")}

    rows = []
    for name, text in [("nl-warmup", WARMUP["nl"]), *prompts(args.prompts)]:
        lang = name[:2]
        # Dia continues the reference: prepend its transcript, then decode only the new audio.
        inputs = processor(text=[f"[S1] {REFERENCES[lang]} {text}"], audio=[refs[lang]],
                           padding=True, return_tensors="pt").to(args.device)
        prompt_len = processor.get_audio_prompt_len(inputs["decoder_attention_mask"])
        torch.manual_seed(42)
        if args.device == "mps":
            torch.mps.manual_seed(42)
        with Measure() as m, torch.inference_mode():
            out = model.generate(**inputs, max_new_tokens=3072, guidance_scale=3.0,
                                 temperature=1.8, top_p=0.90, top_k=50)
        audio = processor.batch_decode(out, audio_prompt_len=prompt_len)[0]
        audio = np.asarray(audio.float().cpu() if torch.is_tensor(audio) else audio, np.float32).reshape(-1)
        path = None
        if "warmup" not in name:
            path = OUTPUT / f"{args.prefix}-{name}.wav"
            path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(path, np.clip(audio, -1, 1), SR, subtype="PCM_16")
        rows.append(m.row(audio.size / SR, engine="parkiet", prompt=name, file=str(path) if path else None))
        print(rows[-1], flush=True)
    save_results(args.prefix, rows)


if __name__ == "__main__":
    main()
