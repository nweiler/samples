#!/usr/bin/env python3
"""Generate the Strudel sample map for this repository.

The map points at GitHub's LFS media host, because raw.githubusercontent.com
serves Git LFS pointer files instead of audio.

Usage:
    python build_strudel_json.py            # writes strudel.json
    python build_strudel_json.py --check    # verifies the map is current
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "strudel.json")
BASE = "https://media.githubusercontent.com/media/nweiler/samples/main/"

# WebAudio can decode these. .rx2 (Reason), .asd (Ableton), .mid and artwork are
# deliberately excluded: they are not playable samples.
AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aif", ".aiff"}

# Names that Strudel already uses for its built-in drum machine. A generated file
# alias must not silently replace one of them.
RESERVED = {
    "bd", "sd", "hh", "oh", "cp", "cr", "rd", "ht", "mt", "lt", "rim",
    "sh", "cb", "tb", "perc", "misc", "fx",
}


def keyify(value: str) -> str:
    """Turn a path fragment into a safe Strudel sample name."""
    value = value.lower().replace("-", "_").replace(".", "_")
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def natural_key(value: str):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value)]


def collect_audio() -> list[str]:
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d != ".git")
        rel = os.path.relpath(dirpath, ROOT)
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() in AUDIO_EXTENSIONS:
                path = filename if rel == "." else os.path.join(rel, filename)
                files.append(path.replace("\\", "/"))
    return sorted(files, key=natural_key)


def suffix_candidates(path: str):
    stem = os.path.splitext(path)[0]
    parts = stem.split("/")
    for depth in range(1, len(parts) + 1):
        yield "_".join(parts[-depth:])


def build_map(files: list[str]) -> dict:
    bank_map: dict[str, list[str]] = {}
    by_dir: dict[str, list[str]] = defaultdict(list)
    for path in files:
        by_dir[os.path.dirname(path)].append(path)

    for directory in sorted(by_dir, key=natural_key):
        bank = "bank_" + (keyify(directory) if directory else "root")
        candidate = bank
        suffix = 2
        while candidate in bank_map:
            candidate = f"{bank}_{suffix}"
            suffix += 1
        bank_map[candidate] = sorted(by_dir[directory], key=natural_key)

    # Build every possible suffix alias, and count which files each alias can
    # refer to. A file gets the shortest suffix that is unambiguous.
    candidate_paths: dict[str, set[str]] = defaultdict(set)
    for path in files:
        for candidate in suffix_candidates(path):
            candidate_paths[keyify(candidate)].add(path)

    file_map: dict[str, str] = {}
    used: set[str] = set(bank_map)
    for path in files:
        chosen = None
        for candidate in suffix_candidates(path):
            key = keyify(candidate)
            if len(key) < 3 or key.isdigit():
                continue
            if key in RESERVED or key.startswith(("bank_", "pack_")):
                continue
            if len(candidate_paths[key]) == 1 and key not in used:
                chosen = key
                break
        if chosen is None:
            chosen = keyify(os.path.splitext(path)[0]) or "sample"
            base = chosen
            suffix = 2
            while chosen in used:
                chosen = f"{base}_{suffix}"
                suffix += 1
        used.add(chosen)
        file_map[chosen] = path

    result: dict[str, object] = {"_base": BASE}
    result.update(bank_map)
    result.update(file_map)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="exit non-zero if strudel.json is stale")
    args = parser.parse_args()

    files = collect_audio()
    sample_map = build_map(files)
    text = json.dumps(sample_map, indent=2, ensure_ascii=True) + "\n"

    if args.check:
        if not os.path.exists(OUT):
            print(f"missing: {OUT}", file=sys.stderr)
            return 1
        with open(OUT, encoding="utf-8") as handle:
            current = handle.read()
        # A Windows checkout may have converted LF to CRLF; content is still current.
        if current.replace("\r\n", "\n") != text:
            print(f"stale: {OUT}", file=sys.stderr)
            return 1
        print(f"up to date: {OUT} ({len(files)} audio files)")
        return 0

    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    banks = sum(1 for key in sample_map if key.startswith("bank_"))
    aliases = len(sample_map) - 1 - banks
    print(
        f"wrote {OUT}: {len(files)} audio files, "
        f"{banks} directory banks, {aliases} file aliases, "
        f"{len(text) / 1024:.1f} KiB"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
