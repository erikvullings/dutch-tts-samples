#!/usr/bin/env python3
"""Piper (espeak-ng phonemes, ONNX) baseline and reference-clip generator.

Examples:
  python scripts/piper_tts.py --voice nl_NL-ronnie-medium --prefix piper --prompts nl
  python scripts/piper_tts.py --voice nl_NL-mls-medium --speaker-id 10 --prefix piper-female --prompts nl --reference
"""

import argparse

from piper.config import SynthesisConfig
from piper.voice import PiperVoice

from common import MODELS, OUTPUT, REFERENCES, WARMUP, Measure, prompts, save_results, write_wav


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True, help="Piper voice name; expects MODELS/piper/<voice>.onnx(.json)")
    ap.add_argument("--speaker-id", type=int, help="speaker id for multi-speaker voices")
    ap.add_argument("--prefix", default="piper")
    ap.add_argument("--prompts", nargs="*", help="prompt names or language prefixes (nl, en)")
    ap.add_argument("--reference", action="store_true", help="also write <prefix>-<lang>-reference.wav for cloning")
    args = ap.parse_args()

    voice = PiperVoice.load(str(MODELS / "piper" / f"{args.voice}.onnx"))
    rate = voice.config.sample_rate
    lang = args.voice[:2]
    cfg = SynthesisConfig(speaker_id=args.speaker_id) if args.speaker_id is not None else None
    jobs = [(f"{lang}-warmup", WARMUP[lang])]
    if args.reference:
        jobs.append((f"{lang}-reference", REFERENCES[lang]))
    jobs += [(k, v) for k, v in prompts(args.prompts) if k.startswith(lang)]

    rows = []
    for name, text in jobs:
        parts = []
        with Measure() as m:
            for chunk in voice.synthesize(text, syn_config=cfg):
                m.chunk()
                parts.append(chunk.audio_int16_bytes)
        pcm = b"".join(parts)
        path = None
        if "warmup" not in name:
            path = OUTPUT / f"{args.prefix}-{name}.wav"
            write_wav(path, pcm, rate)
        rows.append(m.row(len(pcm) / (2 * rate), engine="piper", voice=args.voice,
                          speaker_id=args.speaker_id, prompt=name, file=str(path) if path else None))
        print(rows[-1], flush=True)
    save_results(f"{args.prefix}-{lang}", rows)


if __name__ == "__main__":
    main()
