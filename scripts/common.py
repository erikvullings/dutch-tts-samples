"""Shared prompts, paths and helpers for every engine script."""

import json
import os
import subprocess
import threading
import time
import wave
from pathlib import Path

ROOT = Path(os.environ.get("TTS_TRIALS_DIR", Path(__file__).resolve().parent.parent))
OUTPUT = Path(os.environ.get("TTS_OUTPUT_DIR", ROOT / "output"))
MODELS = Path(os.environ.get("TTS_MODELS_DIR", ROOT / "models"))
REFERENCE_DIR = ROOT / "references"

PROMPTS = {
    "nl-short": "Goedemorgen, uw afspraak is morgen om half tien.",
    "nl-long": (
        "Goedemorgen, ik heb uw afspraak voor donderdag om half tien bevestigd. "
        "Het adres is Stationsstraat 24 in Utrecht. Laat het gerust weten als u "
        "liever een ander tijdstip kiest; dan bekijken we samen de mogelijkheden."
    ),
    "nl-long-normalized": (
        "Goedemorgen, ik heb uw afspraak voor donderdag om half tien bevestigd. "
        "Het adres is Stationsstraat vierentwintig in Utrecht. Laat het gerust weten als u "
        "liever een ander tijdstip kiest; dan bekijken we samen de mogelijkheden."
    ),
    "en-short": "Good morning, your appointment is tomorrow at nine thirty.",
    "en-long": (
        "Good morning, I have confirmed your appointment for Thursday at nine thirty. "
        "The address is 24 Station Street in Utrecht. Please let me know if another "
        "time would suit you better, and we can look at the available options together."
    ),
}

# Exact transcripts of the Piper-generated reference clips in references/.
REFERENCES = {
    "nl": "Hallo, ik spreek vandaag een paar zinnen in het Nederlands voor deze stemtest.",
    "en": "Hello, I am reading a few English sentences today for this voice test.",
}

WARMUP = {"nl": "Een korte test.", "en": "A short test."}


def prompts(selection=None):
    """Return (name, text) pairs, optionally limited to the given names or language prefixes."""
    if not selection:
        return list(PROMPTS.items())
    return [(k, v) for k, v in PROMPTS.items() if k in selection or k[:2] in selection]


def reference(name):
    """Path to a reference clip, e.g. reference('piper-female-nl')."""
    return REFERENCE_DIR / f"{name}-reference.wav"


def rss(pid):
    value = subprocess.check_output(["ps", "-o", "rss=", "-p", str(pid)], text=True).strip()
    return int(value) * 1024 if value else 0


def write_wav(path, pcm16, rate):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(pcm16)


class Measure:
    """Times one synthesis and samples peak RSS of a process (default: this one)."""

    def __init__(self, pid=None):
        self.pid = pid or os.getpid()
        self.first = None

    def __enter__(self):
        self.peak = rss(self.pid)
        self._done = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()
        self.start = time.perf_counter()
        return self

    def _sample(self):
        while not self._done.wait(0.05):
            self.peak = max(self.peak, rss(self.pid))

    def chunk(self):
        if self.first is None:
            self.first = time.perf_counter() - self.start

    def __exit__(self, *exc):
        self.total = time.perf_counter() - self.start
        self._done.set()
        self._thread.join()
        if self.first is None:
            self.first = self.total
        return False

    def row(self, audio_seconds, **extra):
        return {
            **extra,
            "first_audio_s": self.first,
            "total_s": self.total,
            "audio_s": audio_seconds,
            "rtf": self.total / audio_seconds if audio_seconds else None,
            "rss_peak_bytes": self.peak,
        }


def save_results(name, rows):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / f"{name}-results.json"
    path.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"wrote {path}")
