#!/usr/bin/env python3
"""Client for a local pockettts.cpp `tts-server` (one server per language pack).

Registers a reference clip as a cloned voice, then streams raw 24 kHz PCM16 per prompt.
"""

import argparse
import base64
import json
import urllib.request

from common import OUTPUT, WARMUP, Measure, prompts, reference, save_results, write_wav

RATE = 24000


def post(url, body, timeout=600):
    req = urllib.request.Request(url, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req, timeout=timeout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["nl", "en"], required=True)
    ap.add_argument("--reference", default="piper-female", help="reference prefix in references/")
    ap.add_argument("--prefix", default="pocket-female")
    ap.add_argument("--url", default="http://127.0.0.1:8093")
    ap.add_argument("--server-pid", type=int, help="sample peak RSS of the server process")
    ap.add_argument("--prompts", nargs="*")
    args = ap.parse_args()

    wav_b64 = base64.b64encode(reference(f"{args.reference}-{args.lang}").read_bytes()).decode()
    post(f"{args.url}/v1/audio/voices", {"name": "clone", "wav_b64": wav_b64}).read()

    rows = []
    jobs = [(f"{args.lang}-warmup", WARMUP[args.lang])]
    jobs += [(k, v) for k, v in prompts(args.prompts) if k.startswith(args.lang)]
    for name, text in jobs:
        parts = []
        with Measure(args.server_pid) as m:
            body = {"input": text, "voice": "clone", "response_format": "pcm", "seed": 42}
            with post(f"{args.url}/v1/audio/speech", body) as resp:
                while data := resp.read1(4096):
                    m.chunk()
                    parts.append(data)
        pcm = b"".join(parts)
        path = None
        if "warmup" not in name:
            path = OUTPUT / f"{args.prefix}-{name}.wav"
            write_wav(path, pcm, RATE)
        rows.append(m.row(len(pcm) / (2 * RATE), engine="pockettts.cpp", prompt=name,
                          reference=args.reference, file=str(path) if path else None))
        print(rows[-1], flush=True)
    save_results(f"{args.prefix}-{args.lang}", rows)


if __name__ == "__main__":
    main()
