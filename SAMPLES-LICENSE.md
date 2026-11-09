# Audio licence and attribution

The audio in `samples/` and `references/` is **AI-generated**. Except for `samples/vibevoice/` (see below), it is released under the
[Creative Commons Attribution 4.0 International licence (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/),
to the extent the generating models allow, and subject to the output terms below.
Attribute it as: "Dutch TTS samples, Erik Vullings (github.com/erikvullings/dutch-tts-samples), CC BY 4.0",
plus the attributions below for the files they apply to.

Do not present these files as recordings of a real person.

## Source voices

| Files | Source | Licence / attribution |
| --- | --- | --- |
| `piper-nl-*`, `references/piper-nl-reference.wav`, `pocket-nl-*`, `pocket-en-*`, `audio8-*` | Piper `nl_NL-ronnie-medium` (NabuCasa voice dataset), `en_US-kristin-medium` (LibriVox) | CC0 / public domain |
| `piper-female-en-*`, `references/piper-female-en-reference.wav`, `kugelaudio-en-*`, `fish-drama3-en-*` | Piper `en_US-ljspeech-medium` (LJ Speech) | Public domain |
| `piper-female-nl-*`, `piper/nl_NL-mls-medium-speakers/*`, `references/piper-female-nl-reference.wav`, and every sample cloned from that reference (`pocket-female-nl-*`, `omnivoice-nl-*`, `parkiet-*`, `chatterbox-nl-*`, `kugelaudio-nl-*`, `fish-drama3-nl-*`) | Piper `nl_NL-mls-medium`, trained on Multilingual LibriSpeech | **Attribution required:** "Multilingual LibriSpeech (MLS)", V. Pratap et al., 2020, [OpenSLR 94](https://www.openslr.org/94/), CC BY 4.0; source recordings from [LibriVox](https://librivox.org/) |

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
- **KugelAudio** ([kugelaudio/kugelaudio-0-open](https://huggingface.co/kugelaudio/kugelaudio-0-open), MIT):
  the card prohibits deepfakes, misleading content and impersonation without consent.
  Outputs carry an inaudible AudioSeal watermark.
- **LFM3-Audio-2B** ([LiquidAI/LFM3-Audio-2B](https://huggingface.co/LiquidAI/LFM3-Audio-2B),
  via [LiquidAI/LFM3-Audio-2B-MLX-4bit](https://huggingface.co/LiquidAI/LFM3-Audio-2B-MLX-4bit)):
  the model is under the [LFM Open License v1.0](https://huggingface.co/LiquidAI/LFM3-Audio-2B-MLX-4bit/blob/221ddc778422af5354d689b450f1a5e21d2b5616/LICENSE).
  In brief, it grants use, modification and redistribution subject to its terms, including a
  USD 10 million annual-revenue threshold for commercial use. The license text does not state
  separate audio-output terms; check the full license for the applicable use.
- **Audio8 TTS Realistic Air** ([Edge0/Audio8-TTS-Realistic-Air](https://huggingface.co/Edge0/Audio8-TTS-Realistic-Air),
  via [the MLX 8-bit conversion](https://huggingface.co/groxaxo/Audio8-TTS-Realistic-Air-MLX8-Selective)):
  Apache-2.0; the conversion is community-provided and retains upstream terms.
- **Higgs TTS 3** ([Boson AI model](https://huggingface.co/bosonai/higgs-tts-3-4b),
  via [the MLX 6-bit conversion](https://huggingface.co/whitelabel/mlx-q6-higgs-tts-3-4b)):
  [Research and Non-Commercial License](https://huggingface.co/bosonai/higgs-tts-3-4b/blob/main/LICENSE).
  Public non-commercial demonstrations are permitted; commercial/production uses need a separate license.
  Attribution: "Built with Higgs TTS 3 licensed from Boson AI USA, Inc." The full agreement and
  conversion notice are included in `samples/higgs-tts3/LICENSE` and `samples/higgs-tts3/NOTICE`.
- **VoxCPM2** ([OpenBMB model](https://huggingface.co/openbmb/VoxCPM2), via
  [the MLX 4-bit conversion](https://huggingface.co/mlx-community/VoxCPM2-4bit)): Apache-2.0.
  Its card prohibits impersonation, fraud and disinformation.
- **Fish Audio S2 Pro** ([Fish Audio model](https://huggingface.co/fishaudio/s2-pro), via
  [the MLX 8-bit conversion](https://huggingface.co/mlx-community/fish-audio-s2-pro-8bit)):
  [Fish Audio Research License](https://huggingface.co/fishaudio/s2-pro/blob/main/LICENSE.md).
  Research and non-commercial use only; commercial use requires a separate license. Outputs may not
  be used to create or improve foundational generative AI models. Attribution: "Built with Fish Audio."
- **Supertonic 3** ([Supertone/supertonic-3](https://huggingface.co/Supertone/supertonic-3)):
  [OpenRAIL-M License](https://huggingface.co/Supertone/supertonic-3/blob/main/LICENSE), which grants
  use subject to its restrictions, including non-consensual impersonation and deceptive content;
  it also requires disclosure of synthetic content in applicable contexts.
- **Fish Audio Drama 3** ([fishaudio/drama-3](https://huggingface.co/fishaudio/drama-3), via
  [mlx-community/fish-audio-drama-3-4bit](https://huggingface.co/mlx-community/fish-audio-drama-3-4bit)):
  **Built with Fish Audio.** These Fish Audio Materials are licensed under the Fish Audio
  Community License, Version 1.0. Copyright © 39 AI, INC. All Rights Reserved. The licence
  forbids using outputs to imitate an identifiable person without consent, to impersonate or
  deceive, or to create, train, distil or improve speech, audio, voice or foundational
  generative models (training detectors of synthetic audio is allowed).
- **Audio8** ([Edge0](https://huggingface.co/Edge0/Audio8-TTS-Preview-0.6B-ONNX-INT4), Apache-2.0)
  and **Piper** voices: no additional output terms.

## Excluded from the CC BY grant: VibeVoice

The files in `samples/vibevoice/` were generated with
[microsoft/VibeVoice-Realtime-0.5B](https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B),
whose model card limits use to research. They are **not** licensed under CC BY 4.0. They are
shared only as a research reference for listening comparisons, and must not be used in
products or real-world applications. They use the upstream demo voice presets, whose source
speakers are not documented. The output was saved unmodified.
