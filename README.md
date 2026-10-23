# Dutch TTS samples

Listen to and compare open text-to-speech (TTS) models speaking **Dutch** (and some English),
all generated locally on an Apple Silicon Mac. Few Dutch samples are published for most TTS
models, so this repository collects one fixed set of prompts rendered by several engines,
plus the scripts to reproduce them on your own machine.

> **All audio in this repository is AI-generated.** No real person's voice was cloned: the
> cloning references are themselves synthetic Piper voices trained on CC0, public-domain or
> CC BY 4.0 speech data (see [Licences](#licences-and-attribution)).

The samples come from an evaluation of local Dutch speech for a voice assistant. They are a
listening aid, not a benchmark.

**[▶ Listen to all samples in your browser](https://erikvullings.github.io/dutch-tts-samples/)**:
a player page with every engine side by side. Each sample folder also has a README that links
to its section of the player page.

## No performance numbers

**This repository deliberately publishes no timing, real-time-factor or memory figures.** Other
workloads shared the GPU during the original trials, so the numbers were not reliable. The
scripts still measure first-audio delay, real-time factor and peak memory, and write them to
`output/<name>-results.json`, so you can benchmark on your own hardware. Only qualitative
observations are given below (for example, whether an engine streams).

## Prompts

Every engine uses the same prompts (`scripts/common.py`):

| Name | Text |
| --- | --- |
| `nl-short` | Goedemorgen, uw afspraak is morgen om half tien. |
| `nl-long` | Goedemorgen, ik heb uw afspraak voor donderdag om half tien bevestigd. Het adres is Stationsstraat 24 in Utrecht. Laat het gerust weten als u liever een ander tijdstip kiest; dan bekijken we samen de mogelijkheden. |
| `nl-long-normalized` | Same as `nl-long`, with "24" written out as "vierentwintig". |
| `en-short` | Good morning, your appointment is tomorrow at nine thirty. |
| `en-long` | Good morning, I have confirmed your appointment for Thursday at nine thirty. The address is 24 Station Street in Utrecht. Please let me know if another time would suit you better, and we can look at the available options together. |

## Samples

| Folder | Engine | Voice or cloning reference | Streams? |
| --- | --- | --- | --- |
| [`samples/piper`](samples/piper) | [Piper](https://github.com/OHF-Voice/piper1-gpl) | `piper-*`: nl_NL Ronnie (male), en_US Kristin (female). `piper-female-*`: nl_NL MLS speaker 12500 (id 10), en_US LJ Speech | Yes |
| [`samples/piper/nl_NL-mls-medium-speakers`](samples/piper/nl_NL-mls-medium-speakers) | Piper `nl_NL-mls-medium` | All 52 speakers saying `nl-short` (`mls-<id>-<MLS speaker>.wav`) | Yes |
| [`samples/pocket`](samples/pocket) | [Pocket TTS](https://huggingface.co/kyutai/pocket-tts) via [pockettts.cpp](https://github.com/ServeurpersoCom/pockettts.cpp), Q8 GGUF on Metal | `pocket-*`: clones the Ronnie/Kristin references. `pocket-female-*`: clones the female references | Yes, very low first-audio delay |
| [`samples/audio8`](samples/audio8) | [Audio8 TTS Preview 0.6B](https://huggingface.co/Edge0/Audio8-TTS-Preview-0.6B-ONNX-INT4), ONNX INT4 on CPU | Clones the Ronnie/Kristin references | Yes, but much slower than real time on CPU |
| [`samples/kittentts2`](samples/kittentts2) | [KittenTTS 2](https://huggingface.co/KittenML/kitten-tts-2), MLX | `kitten-*`: DutchWeatherPresenter (nl), Maeve (en). `kitten-baker-*`: DutchBaker | No |
| [`samples/omnivoice`](samples/omnivoice) | [OmniVoice](https://huggingface.co/k2-fsa/OmniVoice) (`mlx-community/OmniVoice-bf16`, MLX) | Clones the female references | No |
| [`samples/parkiet`](samples/parkiet) | [Parkiet](https://huggingface.co/pevers/parkiet) (Dutch Dia, MPS) | Clones the Dutch female reference | No, slow |
| [`samples/chatterbox`](samples/chatterbox) | [Chatterbox Multilingual V3](https://huggingface.co/ResembleAI/chatterbox) (MPS) | Clones the female references | No, slow |
| [`samples/vibevoice`](samples/vibevoice) | [VibeVoice-Realtime-0.5B](https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B) (MPS) — **research only** | Demo presets `nl-Spk1_woman`, `en-Emma_woman` (no cloning) | Yes, but slower than real time |

The cloning references are in [`references/`](references).

### Observations (single listener, plus Whisper transcripts)

- **Normalise numbers before synthesis.** Pocket's Dutch pack and Audio8 garble raw digits:
  Whisper heard "Stationsstraat 24" as "Stationsstraat wauwer" (Pocket) and "Stassenstraat 64"
  (Audio8). Writing the number out (`nl-long-normalized`) fixed both. Piper (espeak-ng)
  expands digits itself; KittenTTS, OmniVoice, Parkiet and Chatterbox read the raw "24"
  correctly, although Kitten's DutchBaker voice said "44". VibeVoice read "24" correctly,
  but in the normalised run Whisper heard "Tassonstraat" instead of "Stationsstraat". Dates, times, amounts and
  abbreviations need the same treatment.
- **Pocket TTS** (cloning the female Dutch reference) was the preferred Dutch voice in this
  evaluation: natural, streaming, and light enough to run alongside other work. Single seeds
  still vary occasionally.
- **Piper** is fast and robust. The female `nl_NL-mls-medium` speakers append babble after the
  last word of the short prompt and are less intelligible than Ronnie.
- **OmniVoice, Parkiet and Chatterbox** all produced accurate Dutch, but none of them streams,
  so the whole reply is generated before playback.
- **Kitten's Dutch voices**: by pitch, DutchWeatherPresenter and DutchBaker sound female and
  GrandpaStory male. Whether they sound Netherlands Dutch or Flemish was not verified.
- Whisper writes a spoken "vierentwintig" back as "24", so transcripts confirm the words, not
  how natural they sound. Listen for yourself.

## Reproducing the samples

The scripts write to `output/` (set `TTS_OUTPUT_DIR` to change it) and look for weights under
`models/` (set `TTS_MODELS_DIR`). Both folders are ignored by git. Each engine needs its own
Python environment; [uv](https://docs.astral.sh/uv/) keeps them small and disposable.
Common options: `--prompts nl-short en` (prompt names or a language prefix), `--reference`
(a prefix in `references/`) and `--prefix` (output file prefix).

A warm-up sentence is synthesised first and discarded. Check your output with Whisper:

```sh
WHISPER_MODEL=~/models/ggml-large-v3-turbo-q8_0.bin scripts/transcribe.sh output/*.wav
```

After adding or renaming samples, run `python3 scripts/build_pages.py` to regenerate
`index.html` (the player page) and the folder READMEs.

### Piper

```sh
uv venv .venv-piper && uv pip install -p .venv-piper piper-tts==1.8.0
# Download <voice>.onnx and <voice>.onnx.json from rhasspy/piper-voices into models/piper/
.venv-piper/bin/python scripts/piper_tts.py --voice nl_NL-ronnie-medium --prompts nl
.venv-piper/bin/python scripts/piper_tts.py --voice nl_NL-mls-medium --speaker-id 10 --prefix piper-female --prompts nl
.venv-piper/bin/python scripts/mls_speakers.py   # all 52 MLS speakers, with median pitch
```

Piper does not seed its sampling, so repeated runs differ slightly.

### Regenerating the cloning references

The references are Piper outputs of the transcripts in `REFERENCES` (`scripts/common.py`):

| File | Piper voice | Command |
| --- | --- | --- |
| `piper-nl-reference.wav` | `nl_NL-ronnie-medium` | `piper_tts.py --voice nl_NL-ronnie-medium --prompts nl-short --reference` |
| `piper-en-reference.wav` | `en_US-kristin-medium` | `piper_tts.py --voice en_US-kristin-medium --prompts en-short --reference` |
| `piper-female-nl-reference.wav` | `nl_NL-mls-medium`, speaker id 10 (MLS speaker 12500) | `piper_tts.py --voice nl_NL-mls-medium --speaker-id 10 --prefix piper-female --prompts nl-short --reference` |
| `piper-female-en-reference.wav` | `en_US-ljspeech-medium` | `piper_tts.py --voice en_US-ljspeech-medium --prefix piper-female --prompts en-short --reference` |

Copy the result from `output/` to `references/`. Because Piper is unseeded, a regenerated
reference sounds the same but is not byte-identical.

### Pocket TTS (pockettts.cpp, Metal)

1. Accept the gate on [kyutai/pocket-tts](https://huggingface.co/kyutai/pocket-tts) and read
   its prohibited uses.
2. Build [pockettts.cpp](https://github.com/ServeurpersoCom/pockettts.cpp) with
   `cmake -B build -DGGML_METAL=ON && cmake --build build -j`.
3. Download a language pack, for example `pocket-tts-dutch-Q8_0.gguf`, from
   [Serveurperso/pocket-tts-GGUF](https://huggingface.co/Serveurperso/pocket-tts-GGUF).
4. Run one server per language, then the client (standard library only):

```sh
build/tts-server --model models/pocket/pocket-tts-dutch-Q8_0.gguf --device MTL0 --port 8093 &
python3 scripts/pocket_client.py --lang nl --server-pid $!
python3 scripts/pocket_client.py --lang nl --reference piper --prefix pocket
```

### Audio8 (ONNX, CPU)

Use the Python 3.11 ONNX runtime from the
[model repository](https://huggingface.co/Edge0/Audio8-TTS-Preview-0.6B-ONNX-INT4)
(`onnx_runtime/requirements.txt`, plus `tokenizers==0.22.2`) and start its server on port
8024. Check that the small `.onnx` graph files were downloaded: `hf download --include` can
fetch the `.data` files but miss the graphs. Then run `python3 scripts/audio8_client.py`.

### KittenTTS 2 (MLX)

```sh
uv venv .venv-kitten && uv pip install -p .venv-kitten kittenml
hf download KittenML/kitten-tts-2 --local-dir models/kitten
.venv-kitten/bin/python scripts/kitten_tts.py
```

Dutch runs with the built-in English text normaliser switched off.

### OmniVoice (MLX)

```sh
uv venv .venv-mlx && uv pip install -p .venv-mlx mlx-audio==0.6.1
.venv-mlx/bin/python scripts/mlx_clone.py
```

### Parkiet (MPS)

Needs `torch` and `transformers==4.57.6` (`DiaForConditionalGeneration`). The weights and the
`descript/dac_44khz` codec download on first use.
`python scripts/parkiet_tts.py`.

### Chatterbox Multilingual V3 (MPS)

The PyPI release (0.1.7) pins torch 2.6 and loads only the v2 model. Install the GitHub
version without its pins instead:

```sh
uv venv .venv-cb && uv pip install -p .venv-cb --no-deps git+https://github.com/resemble-ai/chatterbox@5de7a54a
uv pip install -p .venv-cb torch==2.11.0 torchaudio==2.11.0 transformers==5.2.0 librosa==0.11.0 \
  s3tokenizer diffusers==0.29.0 resemble-perth conformer==0.3.2 pyloudnorm omegaconf "numpy<2.4" \
  huggingface_hub safetensors
.venv-cb/bin/python scripts/chatterbox_tts.py
```

On MPS, memory use can grow very large; close other GPU workloads.

### VibeVoice-Realtime-0.5B (research only)

The model card limits
[microsoft/VibeVoice-Realtime-0.5B](https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B)
to research use, and calls Dutch an experimental, unsupported language. The samples in
`samples/vibevoice/` are shared only as a research reference for comparison. They are not
covered by this repository's CC BY grant, and must not be used in products or real-world
applications.

`scripts/vibevoice_tts.py` reproduces the listening trial with the upstream demo voices
(`nl-Spk1_woman`, `en-Emma_woman`). It needs `torch==2.7.1` (newer versions reject the voice
presets) and a checkout of [microsoft/VibeVoice](https://github.com/microsoft/VibeVoice).

The card says an audible AI disclaimer is embedded in every output. None is audible in these
files, and the open-source `vibevoice` package contains no disclaimer or watermark code. The
output was saved unmodified; nothing was removed.

## Licences and attribution

- **Code** (`scripts/`): [MIT](LICENSE).
- **Audio** (`samples/`, `references/`): [CC BY 4.0](SAMPLES-LICENSE.md), with the attribution
  and the per-model output terms listed there. In short:

| Engine | Code / runtime | Weights | Notes on outputs |
| --- | --- | --- | --- |
| Piper | `piper-tts` GPL-3.0-or-later (install it yourself) | Ronnie CC0; Kristin and LJ Speech public domain; `nl_NL-mls-medium` trained on MLS (CC BY 4.0) | MLS samples require attribution |
| Pocket TTS | pockettts.cpp MIT | CC BY 4.0, gated, with prohibited uses | No cloning without consent; don't present output as a genuine recording |
| Audio8 | Apache-2.0 | Apache-2.0 + NOTICE | — |
| KittenTTS 2 | Stellon Labs Community License | Same | Free for research and non-commercial use; commercial use needs registration and ends above $1M revenue or funding; outputs may not train other models; "Powered by KittenML" |
| OmniVoice | Apache-2.0 | No separate licence stated; audio tokenizer under the Boson Higgs Audio 2 Community License | Outputs may not be used to improve other LLMs |
| Parkiet | MIT; DAC codec MIT | RAIL-M (use restrictions) | — |
| Chatterbox | MIT | MIT | Carries an inaudible Perth watermark |
| VibeVoice | MIT | MIT metadata, but the card limits use to research | Samples are a research reference only; not CC BY |

Check each model's own card before using it: licences change, and this table is a summary,
not legal advice.
