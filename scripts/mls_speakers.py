#!/usr/bin/env python3
"""Render nl-short for every speaker in Piper's nl_NL-mls-medium and estimate median F0.

Used to shortlist female speakers; F0 is a rough gender hint, not a verified label.
"""

import json

import numpy as np
from piper.config import SynthesisConfig
from piper.voice import PiperVoice

from common import MODELS, OUTPUT, PROMPTS, write_wav

VOICE = MODELS / "piper" / "nl_NL-mls-medium.onnx"


def median_f0(x, sr):
    x = x.astype(np.float32) / 32768
    n, hop, values = int(0.04 * sr), int(0.01 * sr), []
    for i in range(0, len(x) - n, hop):
        frame = x[i:i + n]
        if np.sqrt((frame ** 2).mean()) < 0.02:
            continue
        frame = frame - frame.mean()
        corr = np.correlate(frame, frame, "full")[n - 1:]
        lo, hi = int(sr / 400), int(sr / 70)
        k = lo + np.argmax(corr[lo:hi])
        if corr[k] > 0.5 * corr[0]:
            values.append(sr / k)
    return float(np.median(values)) if values else 0.0


def main():
    voice = PiperVoice.load(str(VOICE))
    sr = voice.config.sample_rate
    ids = json.loads(VOICE.with_suffix(".onnx.json").read_text())["speaker_id_map"]
    rows = []
    for mls_id, sid in ids.items():
        pcm = b"".join(c.audio_int16_bytes for c in voice.synthesize(
            PROMPTS["nl-short"], syn_config=SynthesisConfig(speaker_id=sid)))
        write_wav(OUTPUT / "nl_NL-mls-medium-speakers" / f"mls-{sid:02d}-{mls_id}.wav", pcm, sr)
        rows.append((median_f0(np.frombuffer(pcm, np.int16), sr), sid, mls_id))
    for f0, sid, mls_id in sorted(rows):
        print(f"{f0:6.1f} Hz  id={sid:2d}  mls={mls_id}")


if __name__ == "__main__":
    main()
