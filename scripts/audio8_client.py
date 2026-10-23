#!/usr/bin/env python3
"""Client for the Audio8 TTS ONNX runtime (`arktts_runtime.service:app`).

Registers a reference clip plus its exact transcript, then streams 44.1 kHz PCM chunks.
"""

import argparse
import base64
import json
import subprocess
import urllib.request

from common import OUTPUT, REFERENCES, WARMUP, Measure, prompts, reference, save_results, write_wav

RATE = 44100


def register(url, name, wav, text):
    subprocess.run(["curl", "-sf", f"{url}/api/voices/register", "-F", f"audio=@{wav}",
                    "-F", f"text={text}", "-F", f"name={name}", "-F", "overwrite=true"],
                   check=True, stdout=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", default="piper", help="reference prefix in references/")
    ap.add_argument("--prefix", default="audio8")
    ap.add_argument("--url", default="http://127.0.0.1:8024")
    ap.add_argument("--server-pid", type=int)
    ap.add_argument("--prompts", nargs="*")
    args = ap.parse_args()

    rows = []
    for lang in ("nl", "en"):
        selected = [(k, v) for k, v in prompts(args.prompts) if k.startswith(lang)]
        if not selected:
            continue
        voice = f"{args.reference}_{lang}"
        register(args.url, voice, reference(f"{args.reference}-{lang}"), REFERENCES[lang])
        for name, text in [(f"{lang}-warmup", WARMUP[lang]), *selected]:
            body = json.dumps({"text": text, "voice_name": voice, "seed": 42,
                               "max_new_tokens": 1024}).encode()
            req = urllib.request.Request(f"{args.url}/api/tts/stream", body,
                                         {"Content-Type": "application/json"}, method="POST")
            parts = []
            with Measure(args.server_pid) as m:
                with urllib.request.urlopen(req, timeout=600) as resp:
                    for line in resp:
                        if not line.strip():
                            continue
                        event = json.loads(line)
                        if event.get("event") == "audio_chunk":
                            m.chunk()
                            parts.append(base64.b64decode(event["pcm_b64"]))
            pcm = b"".join(parts)
            path = None
            if "warmup" not in name:
                path = OUTPUT / f"{args.prefix}-{name}.wav"
                write_wav(path, pcm, RATE)
            rows.append(m.row(len(pcm) / (2 * RATE), engine="audio8-onnx-int4", prompt=name,
                              voice=voice, file=str(path) if path else None))
            print(rows[-1], flush=True)
    save_results(args.prefix, rows)


if __name__ == "__main__":
    main()
