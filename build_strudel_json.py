#!/usr/bin/env python3
"""Generate the Strudel sample map for this repository.

The default map points at GitHub's LFS media host, because
raw.githubusercontent.com serves Git LFS pointer files instead of audio.
Use ``--local`` to write a second map whose ``_base`` is the local sampler
server, so the same banks, packs, and aliases can be auditioned from disk.

The map contains these kinds of entries:
    _base             the media base URL
    bank_<category>   one array per top-level sample category (recursive)
    bank_<subfolder>  one array per nested folder with audio (for example a
                      BPM range or a zero-g sub-pack)
    pack_<pack-code>  one array per pack (from provenance.json), so a single
                      pack can be browsed with s("pack_<code>")
    <alias>           one short name per audio file

Usage:
    python build_strudel_json.py                  # writes strudel.json (GitHub)
    python build_strudel_json.py --local          # writes strudel.local.json
    python build_strudel_json.py --check          # verifies strudel.json
    python build_strudel_json.py --local --check  # verifies strudel.local.json
    python build_strudel_json.py --base URL       # custom _base
    python build_strudel_json.py --port 5555 --local
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
LOCAL_OUT = os.path.join(ROOT, "strudel.local.json")
PROVENANCE = os.path.join(ROOT, "provenance.json")
BASE = "https://media.githubusercontent.com/media/nweiler/samples/main/"
DEFAULT_PORT = 5432

# The library is organized by sample type, but a few categories were renamed
# to Strudel's short drum names. provenance.json predates that rename, so when
# a file has moved, prefer the old entry whose category maps to the new one.
CATEGORY_RENAMES = {
    "claps": "cp",
    "cymbals": "cym",
    "hats": "hh",
    "kicks": "bd",
    "percussion": "perc",
    "snares": "sd",
}

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


def load_pack_map() -> tuple[dict[str, str], dict[str, list[str]]]:
    """Map content file paths to pack codes, with a basename index.

    provenance.json records where a file lived when it was imported. The
    sample tree is periodically reorganized, so a moved audio file may not be
    at its recorded path. The basename index lets us keep its pack identity
    without silently dropping it from the pack banks.
    """
    with open(PROVENANCE, encoding="utf-8") as handle:
        provenance = json.load(handle)
    pack_of = {path: meta["pack"] for path, meta in provenance["files"].items()}
    by_basename: dict[str, list[str]] = defaultdict(list)
    for path in pack_of:
        by_basename[os.path.basename(path)].append(path)
    return pack_of, by_basename


def resolve_pack(
    path: str,
    pack_of: dict[str, str],
    by_basename: dict[str, list[str]],
) -> tuple[str | None, str]:
    """Return ``(pack, how)`` for an audio path.

    ``how`` is ``exact`` when provenance already knows the path, ``moved``
    when it was found by unique basename, and ``missing`` otherwise.
    """
    pack = pack_of.get(path)
    if pack is not None:
        return pack, "exact"

    candidates = by_basename.get(os.path.basename(path), [])
    if len(candidates) == 1:
        return pack_of[candidates[0]], "moved"
    if len(candidates) > 1:
        top = path.split("/")[0]
        renamed = [
            candidate
            for candidate in candidates
            if CATEGORY_RENAMES.get(candidate.split("/")[0], candidate.split("/")[0]) == top
        ]
        if len(renamed) == 1:
            return pack_of[renamed[0]], "moved"
    return None, "missing"


def build_map(
    files: list[str],
    pack_map: tuple[dict[str, str], dict[str, list[str]]],
    base: str = BASE,
) -> tuple[dict, dict[str, int]]:
    pack_of, by_basename = pack_map
    bank_map: dict[str, list[str]] = {}
    by_dir: dict[str, list[str]] = defaultdict(list)
    for path in files:
        by_dir[os.path.dirname(path)].append(path)

    def add_bank(name: str, paths: list[str]) -> None:
        candidate = name
        suffix = 2
        while candidate in bank_map:
            candidate = f"{name}_{suffix}"
            suffix += 1
        bank_map[candidate] = sorted(paths, key=natural_key)

    # A top-level bank covers every audio file in that category, including
    # files nested in subfolders such as breaks/090-099/ or bass/zero-g/.
    by_top: dict[str, list[str]] = defaultdict(list)
    for path in files:
        by_top[path.split("/")[0] if "/" in path else ""].append(path)
    for top in sorted(by_top, key=natural_key):
        if top:
            add_bank("bank_" + keyify(top), by_top[top])

    # Nested folders also get their own banks, so a BPM range or a sub-pack
    # can be auditioned on its own. Top-level folders are already covered.
    for directory in sorted(by_dir, key=natural_key):
        if directory and "/" in directory:
            add_bank("bank_" + keyify(directory), by_dir[directory])

    # Loose files at the repository root (format-neutral extras) stay playable.
    if "" in by_dir:
        add_bank("bank_root", by_dir[""])

    # Per-pack banks let one pack be auditioned at a time, e.g.
    # s("pack_cymatics_odyssey_edm"). Files are grouped by category
    # (the path prefix sorts that way) then natural order, so n() indices
    # are stable.
    by_pack: dict[str, list[str]] = defaultdict(list)
    unmapped: list[str] = []
    moved = 0
    for path in files:
        pack, how = resolve_pack(path, pack_of, by_basename)
        if pack is None:
            unmapped.append(path)
        else:
            by_pack[pack].append(path)
            moved += how == "moved"
    if unmapped:
        print(
            f"error: {len(unmapped)} audio files are missing from provenance.json, "
            "refusing to build incomplete pack banks:",
            file=sys.stderr,
        )
        for path in unmapped[:10]:
            print(f"  {path}", file=sys.stderr)
        raise SystemExit(1)

    pack_map: dict[str, list[str]] = {}
    for pack in sorted(by_pack, key=natural_key):
        bank = "pack_" + keyify(pack)
        candidate = bank
        suffix = 2
        while candidate in bank_map or candidate in pack_map:
            candidate = f"{bank}_{suffix}"
            suffix += 1
        pack_map[candidate] = sorted(by_pack[pack], key=natural_key)

    # Build every possible suffix alias, and count which files each alias can
    # refer to. A file gets the shortest suffix that is unambiguous.
    candidate_paths: dict[str, set[str]] = defaultdict(set)
    for path in files:
        for candidate in suffix_candidates(path):
            candidate_paths[keyify(candidate)].add(path)

    file_map: dict[str, str] = {}
    used: set[str] = set(bank_map) | set(pack_map)
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
            stem = chosen
            suffix = 2
            while chosen in used:
                chosen = f"{stem}_{suffix}"
                suffix += 1
        used.add(chosen)
        file_map[chosen] = path

    result: dict[str, object] = {"_base": base}
    result.update(bank_map)
    result.update(pack_map)
    result.update(file_map)
    return result, {"moved": moved}


def main() -> int:
    parser = argparse.ArgumentParser()
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--local", action="store_true", help="target strudel.local.json and a localhost base")
    target.add_argument("--out", help="write this file instead of strudel.json")
    parser.add_argument("--base", help="override the _base URL")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"localhost sampler port for --local (default {DEFAULT_PORT})")
    parser.add_argument("--check", action="store_true", help="exit non-zero if the target map is stale")
    args = parser.parse_args()

    if args.local:
        out = LOCAL_OUT
        base = args.base or f"http://localhost:{args.port}/"
    else:
        out = os.path.abspath(args.out) if args.out else OUT
        base = args.base or BASE
    if not base.endswith("/"):
        base += "/"

    files = collect_audio()
    sample_map, stats = build_map(files, load_pack_map(), base)
    text = json.dumps(sample_map, indent=2, ensure_ascii=True) + "\n"

    if stats["moved"]:
        print(
            f"note: {stats['moved']} audio files were matched to provenance.json "
            "by filename because their paths changed; refresh provenance.json "
            "when convenient",
            file=sys.stderr,
        )

    if args.check:
        if not os.path.exists(out):
            print(f"missing: {out}", file=sys.stderr)
            return 1
        with open(out, encoding="utf-8") as handle:
            current = handle.read()
        # A Windows checkout may have converted LF to CRLF; content is still current.
        if current.replace("\r\n", "\n") != text:
            print(f"stale: {out}", file=sys.stderr)
            return 1
        print(f"up to date: {out} ({len(files)} audio files, _base {base})")
        return 0

    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    banks = sum(1 for key in sample_map if key.startswith("bank_"))
    packs = sum(1 for key in sample_map if key.startswith("pack_"))
    aliases = len(sample_map) - 1 - banks - packs
    print(
        f"wrote {out}: {len(files)} audio files, "
        f"{banks} directory banks, {packs} pack banks, {aliases} file aliases, "
        f"_base {base}, {len(text) / 1024:.1f} KiB"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
