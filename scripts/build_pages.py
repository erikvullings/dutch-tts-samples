#!/usr/bin/env python3
"""Build the GitHub Pages player (index.html) and a README.md per sample folder.

Run after adding or renaming samples: python3 scripts/build_pages.py
"""
from html import escape
from pathlib import Path

from common import PROMPTS, REFERENCES

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/erikvullings/dutch-tts-samples"
PAGES = "https://erikvullings.github.io/dutch-tts-samples"
ORDER = ["nl-short", "nl-long", "nl-long-normalized", "en-short", "en-long"]

# folder -> (title, anchor, description)
COLLECTIONS = {
    "samples/pocket": ("Pocket TTS", "pocket",
        "Kyutai Pocket TTS via pockettts.cpp (Q8 GGUF, Metal). `pocket-*` clones the Ronnie/Kristin "
        "references, `pocket-female-*` the female references. Streams."),
    "samples/piper": ("Piper", "piper",
        "Piper with espeak-ng. `piper-*`: nl_NL Ronnie (male), en_US Kristin (female). "
        "`piper-female-*`: nl_NL-mls-medium speaker 12500 (id 10), en_US LJ Speech."),
    "samples/audio8": ("Audio8 TTS Preview 0.6B", "audio8",
        "Edge0 Audio8 0.6B, ONNX INT4 on CPU, cloning the Ronnie/Kristin references."),
    "samples/kittentts2": ("KittenTTS 2", "kittentts2",
        "KittenML KittenTTS 2 (MLX). `kitten-*`: DutchWeatherPresenter (nl), Maeve (en). "
        "`kitten-baker-*`: DutchBaker. Powered by KittenML."),
    "samples/omnivoice": ("OmniVoice", "omnivoice",
        "k2-fsa OmniVoice (mlx-community/OmniVoice-bf16), cloning the female references."),
    "samples/parkiet": ("Parkiet", "parkiet",
        "pevers/parkiet (Dutch Dia, MPS), cloning the Dutch female reference."),
    "samples/chatterbox": ("Chatterbox Multilingual V3", "chatterbox",
        "Resemble AI Chatterbox Multilingual V3 (MPS), cloning the female references. "
        "Outputs carry an inaudible Perth watermark."),
    "samples/vibevoice": ("VibeVoice-Realtime-0.5B (research only)", "vibevoice",
        "Microsoft VibeVoice-Realtime-0.5B demo presets `nl-Spk1_woman` and `en-Emma_woman`. "
        "**Research reference only; not covered by the CC BY grant.**"),
    "samples/piper/nl_NL-mls-medium-speakers": ("Piper nl_NL-mls-medium: all 52 speakers", "mls-speakers",
        "Every speaker of `nl_NL-mls-medium` saying nl-short. File name: `mls-<speaker id>-<MLS speaker>.wav`. "
        "Note: this voice handles short sentences poorly. For all 52 speakers the last word ('tien') is "
        "garbled, and about half garble 'Goedemorgen'. Adding a clause ('…, zoals we hadden afgesproken.') "
        "fixed 'half tien' for all speakers in a Whisper check. Likely cause: training on long LibriVox "
        "audiobook clips. Pad short replies or prefer a single-speaker voice such as Ronnie."),
    "references": ("Cloning references", "references",
        "Piper clips used as voice-cloning references (see the main README for how to regenerate them)."),
}


def split(stem):
    """Return (variant, prompt name) for a sample file stem."""
    for name in sorted(PROMPTS, key=len, reverse=True):
        if stem.endswith("-" + name):
            return stem[: -len(name) - 1], name
    if stem.endswith("-reference"):
        lang = stem.rsplit("-", 2)[-2]
        return stem, f"reference ({lang})"
    return stem, ""


def text_for(prompt):
    if prompt in PROMPTS:
        return PROMPTS[prompt]
    if prompt.startswith("reference"):
        return REFERENCES[prompt[-3:-1]]
    return PROMPTS["nl-short"]


def files(folder):
    return sorted((ROOT / folder).glob("*.wav"))


def md_inline(text):
    """Minimal Markdown to HTML for descriptions: `code` and **bold**."""
    out, parts = [], escape(text).split("`")
    for i, part in enumerate(parts):
        if i % 2:
            out.append(f"<code>{part}</code>")
        else:
            bold = part.split("**")
            out.append("".join(f"<strong>{b}</strong>" if j % 2 else b for j, b in enumerate(bold)))
    return "".join(out)


def audio(rel):
    return f'<audio controls preload="none" src="{escape(rel)}"></audio>'


def html_section(folder, title, anchor, desc):
    rows = []
    wavs = files(folder)
    if folder in ("references", "samples/piper/nl_NL-mls-medium-speakers"):
        for f in wavs:
            variant, prompt = split(f.stem)
            rows.append(f"<tr><td><code>{escape(f.name)}</code></td><td>{escape(text_for(prompt))}</td>"
                        f"<td>{audio(f.relative_to(ROOT).as_posix())}</td></tr>")
        head = "<tr><th>File</th><th>Text</th><th>Listen</th></tr>"
    else:
        grid = {}
        for f in wavs:
            variant, prompt = split(f.stem)
            grid.setdefault(variant, {})[prompt] = f
        cols = [p for p in ORDER if any(p in v for v in grid.values())]
        head = "<tr><th>Voice</th>" + "".join(f'<th><abbr title="{escape(PROMPTS[p])}">{p}</abbr></th>' for p in cols) + "</tr>"
        for variant, cells in grid.items():
            tds = "".join(f"<td>{audio(cells[p].relative_to(ROOT).as_posix())}</td>" if p in cells else "<td></td>"
                          for p in cols)
            rows.append(f"<tr><th scope=\"row\"><code>{escape(variant)}</code></th>{tds}</tr>")
    return (f'<section id="{anchor}"><h2>{escape(title)} <a href="#{anchor}">#</a></h2>'
            f"<p>{md_inline(desc)}</p><div class=\"scroll\"><table>{head}{''.join(rows)}</table></div></section>")


def build_html():
    prompts = "".join(f"<tr><th><code>{p}</code></th><td>{escape(PROMPTS[p])}</td></tr>" for p in ORDER)
    toc = "".join(f'<li><a href="#{a}">{escape(t)}</a></li>' for t, a, _ in COLLECTIONS.values())
    sections = "".join(html_section(f, *meta) for f, meta in COLLECTIONS.items())
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dutch TTS samples</title>
<style>
body {{ font: 16px/1.5 system-ui, sans-serif; max-width: 1200px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
table {{ border-collapse: collapse; margin: .5rem 0 1.5rem; }}
th, td {{ border: 1px solid #ddd; padding: .35rem .5rem; text-align: left; vertical-align: middle; }}
thead th, tr:first-child th {{ background: #f5f5f5; }}
audio {{ width: 220px; height: 36px; }}
.scroll {{ overflow-x: auto; }}
.note {{ background: #fff8e1; border-left: 4px solid #f0b400; padding: .5rem 1rem; }}
h2 a {{ text-decoration: none; color: #bbb; font-size: .8em; }}
@media (prefers-color-scheme: dark) {{
  body {{ background: #111; color: #ddd; }} th, td {{ border-color: #333; }}
  thead th, tr:first-child th {{ background: #1c1c1c; }} .note {{ background: #2a2410; }} a {{ color: #8ab4f8; }}
}}
</style>
</head>
<body>
<h1>Dutch TTS samples</h1>
<p class="note"><strong>All audio is AI-generated.</strong> No real person's voice was cloned. These are listening
samples, not benchmarks. Licences, attribution and setup: see the <a href="{REPO}">repository README</a>.
VibeVoice samples are a research reference only.</p>
<h2>Prompts</h2>
<table>{prompts}</table>
<h2>Collections</h2>
<ul>{toc}</ul>
{sections}
<p><small>Generated by <code>scripts/build_pages.py</code>.</small></p>
</body>
</html>
"""


def build_readme(folder, title, anchor, desc):
    lines = [f"# {title}", "", desc, "",
             f"**[▶ Play these samples in your browser]({PAGES}/#{anchor})**", "",
             "GitHub cannot play audio in its file view. Use the player page above, or click a file "
             "below to open it in your browser's built-in player.", "",
             "| File | Text |", "| --- | --- |"]
    for f in files(folder):
        _, prompt = split(f.stem)
        url = f"{PAGES}/{f.relative_to(ROOT).as_posix()}"
        lines.append(f"| [{f.name}]({url}) | {text_for(prompt)} |")
    lines += ["", "All audio is AI-generated. See [SAMPLES-LICENSE.md]"
              f"({'../' * len(Path(folder).parts)}SAMPLES-LICENSE.md) for licence and attribution.", ""]
    (ROOT / folder / "README.md").write_text("\n".join(lines))


if __name__ == "__main__":
    (ROOT / "index.html").write_text(build_html())
    for folder, meta in COLLECTIONS.items():
        build_readme(folder, *meta)
    print("wrote index.html and", len(COLLECTIONS), "folder READMEs")
