#!/usr/bin/env python3
"""KugelAudio-0-Open (MIT) with a voice encoded from a Piper reference clip.

Run inside an environment with the `kugelaudio-open` package installed
(https://github.com/Kugelaudio/kugelaudio-open). The first run downloads
about 19 GB of weights from kugelaudio/kugelaudio-0-open.
"""

import argparse

import torch
from kugelaudio_open import KugelAudioForConditionalGenerationInference, KugelAudioProcessor

from common import OUTPUT, WARMUP, Measure, prompts, reference, save_results

MODEL_ID = "kugelaudio/kugelaudio-0-open"
SPEECH_END_TOKEN = 151653
DEFAULT_PROMPTS = ["nl-short", "nl-long", "nl-long-normalized", "en-short"]


def penalise_early_end(model, strength=5.0):
    """Discourage the speech-end token, which otherwise cuts sentences short."""
    original = model.forward

    def forward(*args, **kwargs):
        out = original(*args, **kwargs)
        logits = getattr(out, "logits", None)
        if isinstance(logits, torch.Tensor) and logits.shape[-1] > SPEECH_END_TOKEN:
            logits[..., SPEECH_END_TOKEN] -= strength
        return out

    model.forward = forward


def encode_voice(model, processor, wav):
    audio = processor.audio_processor(str(wav), return_tensors="pt")["audio"]
    with torch.no_grad():
        enc = model.acoustic_tokenizer.encode(audio)
    return {"acoustic_mean": enc.mean.cpu(), "acoustic_std": enc.std}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="kugelaudio")
    ap.add_argument("--reference", default="piper-female")
    ap.add_argument("--prompts", nargs="*", default=DEFAULT_PROMPTS)
    ap.add_argument("--cfg-scale", type=float, default=3.0)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    processor = KugelAudioProcessor.from_pretrained(MODEL_ID)
    model = KugelAudioForConditionalGenerationInference.from_pretrained(MODEL_ID, dtype=torch.float32)
    model.eval()
    penalise_early_end(model)
    voices = {lang: encode_voice(model, processor, reference(f"{args.reference}-{lang}")) for lang in ("nl", "en")}
    model.model.strip_encoders()

    rows = []
    for name, text in [("nl-warmup", WARMUP["nl"]), *prompts(args.prompts)]:
        lang = name[:2]
        torch.manual_seed(args.seed)
        inputs = processor(text=text, voice_cache=voices[lang], return_tensors="pt")
        with Measure() as m, torch.no_grad():
            out = model.generate(**inputs, cfg_scale=args.cfg_scale, max_new_tokens=2048, show_progress=False)
        speech = out.speech_outputs[0]
        seconds = speech.shape[-1] / processor.audio_processor.sampling_rate
        path = None
        if "warmup" not in name:
            path = OUTPUT / f"{args.prefix}-{name}.wav"
            path.parent.mkdir(parents=True, exist_ok=True)
            processor.save_audio(speech, str(path))
        rows.append(m.row(seconds, engine=args.prefix, model=MODEL_ID, prompt=name, file=str(path) if path else None))
        print(rows[-1], flush=True)
    save_results(args.prefix, rows)


if __name__ == "__main__":
    main()
