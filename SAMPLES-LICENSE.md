# Audio licence and attribution

The audio in `samples/` and `references/` is **AI-generated**. It is released under the
[Creative Commons Attribution 4.0 International licence (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/),
to the extent the generating models allow, and subject to the output terms below.
Attribute it as: "Dutch TTS samples, Erik Vullings (github.com/erikvullings/dutch-tts-samples), CC BY 4.0",
plus the attributions below for the files they apply to.

Do not present these files as recordings of a real person.

## Source voices

| Files | Source | Licence / attribution |
| --- | --- | --- |
| `piper-nl-*`, `references/piper-nl-reference.wav`, `pocket-nl-*`, `pocket-en-*`, `audio8-*` | Piper `nl_NL-ronnie-medium` (NabuCasa voice dataset), `en_US-kristin-medium` (LibriVox) | CC0 / public domain |
| `piper-female-en-*`, `references/piper-female-en-reference.wav` | Piper `en_US-ljspeech-medium` (LJ Speech) | Public domain |
| `piper-female-nl-*`, `piper/nl_NL-mls-medium-speakers/*`, `references/piper-female-nl-reference.wav`, and every sample cloned from that reference (`pocket-female-nl-*`, `omnivoice-nl-*`, `parkiet-*`, `chatterbox-nl-*`) | Piper `nl_NL-mls-medium`, trained on Multilingual LibriSpeech | **Attribution required:** "Multilingual LibriSpeech (MLS)", V. Pratap et al., 2020, [OpenSLR 94](https://www.openslr.org/94/), CC BY 4.0; source recordings from [LibriVox](https://librivox.org/) |

## Output terms of the generating models

- **Pocket TTS** ([kyutai/pocket-tts](https://huggingface.co/kyutai/pocket-tts), CC BY 4.0):
  its terms prohibit cloning a voice without consent and presenting generated audio as a
  genuine recording.
- **KittenTTS 2** ([KittenML/kitten-tts-2](https://huggingface.co/KittenML/kitten-tts-2),
  Stellon Labs Community License): Powered by KittenML. Outputs may not be used to train or
  improve other models.
- **OmniVoice** ([k2-fsa/OmniVoice](https://huggingface.co/k2-fsa/OmniVoice)): its audio
  tokenizer falls under the Boson Higgs Audio 2 Community License, which bars using outputs
  to improve other large language models.
- **Parkiet** ([pevers/parkiet](https://huggingface.co/pevers/parkiet), RAIL-M): the use
  restrictions in its licence apply.
- **Chatterbox** ([ResembleAI/chatterbox](https://huggingface.co/ResembleAI/chatterbox), MIT):
  outputs carry an inaudible Perth watermark.
- **Audio8** ([Edge0](https://huggingface.co/Edge0/Audio8-TTS-Preview-0.6B-ONNX-INT4), Apache-2.0)
  and **Piper** voices: no additional output terms.

VibeVoice output is research-only and is therefore not included.
