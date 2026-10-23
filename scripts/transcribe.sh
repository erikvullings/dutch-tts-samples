#!/usr/bin/env bash
# Transcribe WAVs with whisper.cpp (large-v3-turbo) to spot misread words and numbers.
# Usage: WHISPER_MODEL=/path/ggml-large-v3-turbo-q8_0.bin scripts/transcribe.sh samples/pocket/*.wav
set -euo pipefail
: "${WHISPER_MODEL:?set WHISPER_MODEL to a ggml Whisper model}"
for f in "$@"; do
  lang=nl
  [[ "$(basename "$f")" == *-en-* ]] && lang=en
  text=$(whisper-cli -m "$WHISPER_MODEL" -l "$lang" -nt -np -f "$f" 2>/dev/null | tr -s ' \n' ' ')
  printf '%s:%s\n' "$f" "$text"
done
