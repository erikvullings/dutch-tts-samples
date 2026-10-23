#!/usr/bin/env python3
"""VibeVoice-Realtime-0.5B on MPS with the upstream demo defaults. RESEARCH USE ONLY.

Microsoft limits this model to research; Dutch is outside its supported scope. Run it from a
checkout of microsoft/VibeVoice (for the demo voice presets) with torch==2.7.1. The output is
written unmodified; do not remove any disclaimer or watermark. The samples in
samples/vibevoice/ are a research reference only.
"""

import argparse
import copy
import json
import os
import threading
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from transformers.cache_utils import DynamicCache
from transformers.modeling_outputs import BaseModelOutputWithPast

from common import MODELS, OUTPUT, PROMPTS, WARMUP, rss, save_results
from vibevoice.modular.modeling_vibevoice_streaming_inference import (
    VibeVoiceStreamingForConditionalGenerationInference,
)
from vibevoice.modular.streamer import AudioStreamer
from vibevoice.processor.vibevoice_streaming_processor import VibeVoiceStreamingProcessor

SR = 24000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nl-voice", default="nl-Spk1_woman")
    ap.add_argument("--en-voice", default="en-Emma_woman")
    ap.add_argument("--model-dir", default=str(MODELS / "vibevoice"))
    ap.add_argument("--voices-dir", required=True,
                    help="<VibeVoice checkout>/demo/voices/streaming_model")
    args = ap.parse_args()
    MODEL, VOICES = Path(args.model_dir), Path(args.voices_dir)

    t = time.perf_counter()
    processor = VibeVoiceStreamingProcessor.from_pretrained(str(MODEL))
    model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
        str(MODEL), torch_dtype=torch.float32, attn_implementation="sdpa", device_map=None
    )
    model.to("mps").eval()
    model.set_ddpm_inference_steps(num_steps=5)
    print(f"load {time.perf_counter() - t:.1f}s", flush=True)

    pid = os.getpid()
    rows = []
    jobs = [("nl", args.nl_voice, "nl-warmup", WARMUP["nl"])]
    jobs += [("nl", args.nl_voice, k, v) for k, v in PROMPTS.items() if k.startswith("nl")]
    jobs += [("en", args.en_voice, "en-warmup", WARMUP["en"])]
    jobs += [("en", args.en_voice, k, v) for k, v in PROMPTS.items() if k.startswith("en")]

    cache = {}
    for _, voice, name, text in jobs:
        if voice not in cache:
            with torch.serialization.safe_globals([BaseModelOutputWithPast, DynamicCache]):
                cache[voice] = torch.load(VOICES / f"{voice}.pt", map_location="mps", weights_only=True)
        prefilled = cache[voice]
        inputs = processor.process_input_with_cached_prompt(
            text=text, cached_prompt=prefilled, padding=True,
            return_tensors="pt", return_attention_mask=True,
        )
        inputs = {k: v.to("mps") if torch.is_tensor(v) else v for k, v in inputs.items()}
        streamer = AudioStreamer(batch_size=1, stop_signal=None, timeout=None)
        errors = []
        peak = [rss(pid)]
        done = threading.Event()

        def sampler():
            while not done.wait(0.05):
                peak[0] = max(peak[0], rss(pid))

        def run():
            try:
                model.generate(
                    **inputs, max_new_tokens=None, cfg_scale=1.5,
                    tokenizer=processor.tokenizer,
                    generation_config={"do_sample": False},
                    audio_streamer=streamer, verbose=False, refresh_negative=True,
                    all_prefilled_outputs=copy.deepcopy(prefilled),
                )
            except Exception as exc:
                errors.append(exc)
                streamer.end()

        threading.Thread(target=sampler, daemon=True).start()
        start = time.perf_counter()
        th = threading.Thread(target=run, daemon=True)
        th.start()
        first = None
        chunks = []
        for chunk in streamer.get_stream(0):
            a = chunk.detach().cpu().to(torch.float32).numpy().reshape(-1)
            if first is None and a.size:
                first = time.perf_counter() - start
            chunks.append(a)
        th.join()
        total = time.perf_counter() - start
        done.set()
        if errors:
            raise errors[0]
        audio = np.concatenate(chunks) if chunks else np.zeros(0, np.float32)
        out = None
        if not name.endswith("warmup"):
            out = OUTPUT / f"vibevoice-{name}.wav"
            out.parent.mkdir(parents=True, exist_ok=True)
            # Same as the upstream processor.save_audio: write the raw float output, no post-processing.
            sf.write(out, np.clip(audio, -1, 1), SR, subtype="PCM_16")
        dur = audio.size / SR
        rows.append({
            "engine": "vibevoice-realtime-0.5b-mps", "voice": voice, "prompt": name,
            "chunks": len(chunks), "first_audio_s": first, "total_s": total,
            "audio_s": dur, "rtf": total / dur if dur else None,
            "rss_peak_bytes": peak[0], "file": str(out) if out else None,
        })
        print(json.dumps(rows[-1]), flush=True)
    save_results("vibevoice", rows)


if __name__ == "__main__":
    main()
