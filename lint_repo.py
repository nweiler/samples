#!/usr/bin/env python3
"""Lint the sample library against the conventions in AGENTS.md.

Read-only: reports problems and exits non-zero when any check fails. Covers
top-level layout, file naming, directory depth, OS junk, provenance.json
consistency, strudel.json invariants (including freshness), the breaks BPM
ordering, .gitattributes coverage, and git index health.

Usage:
    python lint_repo.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter

# Importing build_strudel_json must not litter the repo with __pycache__.
sys.dont_write_bytecode = True
import build_strudel_json as bsj

ROOT = os.path.dirname(os.path.abspath(__file__))
PROVENANCE = os.path.join(ROOT, "provenance.json")
MAP = os.path.join(ROOT, "strudel.json")

CATEGORY_DIRS = [
    "bass", "bd", "breaks", "cp", "cym", "drum_fills", "drum_loops", "fx", "hh",
    "instruments", "midi", "perc", "sd", "spoken", "synth_chords", "synth_loops",
    "synth_one_shots", "toms", "vox",
]
LICENSES_DIR = "licenses"
CONTENT_DIRS = CATEGORY_DIRS + [LICENSES_DIR]

# Root files that are exempt from the content naming rules and from LFS.
ROOT_FILES = {
    ".gitattributes", ".gitignore", "AGENTS.md", "README.md",
    "build_strudel_json.py", "lint_repo.py", "provenance.json", "strudel.json",
    "strudel.local.json",
}

# a-z, 0-9, _, -, . only; must not start with a dot or hyphen (no hidden
# files, no leading separator).
NAME_RE = re.compile(r"^[a-z0-9_][a-z0-9_.-]*$")
# Underscores adjacent to hyphens are removed during normalization.
ADJACENCY_RE = re.compile(r"_-|-_")
KEY_RE = re.compile(r"^[a-z0-9_]+$")

JUNK_FILES = {
    ".ds_store", ".appledouble", ".lsoverride", ".localized", ".apdisk",
    ".volumicon.icns", ".com.apple.timemachine.donotpresent",
    "thumbs.db", "ehthumbs.db", "ehthumbs_vista.db", "desktop.ini",
}
JUNK_DIRS = {
    "__macosx", "_macosx", ".fseventsd", ".spotlight-v100", ".trashes",
    ".temporaryitems", ".documentrevisions-v100", "$recycle.bin",
}
JUNK_PREFIXES = ("._",)


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def is_junk(name: str, is_dir: bool) -> bool:
    lowered = name.lower()
    if lowered.startswith(JUNK_PREFIXES):
        return True
    return lowered in (JUNK_DIRS if is_dir else JUNK_FILES)


def check_name(path: str, name: str, is_dir: bool, problems: list[str]) -> None:
    if is_junk(name, is_dir):
        problems.append(f"OS junk: {path}")
    if not NAME_RE.match(name):
        problems.append(f"invalid name (uppercase/space/punctuation): {path}")
    elif ADJACENCY_RE.search(name):
        problems.append(f"underscore adjacent to hyphen: {path}")


def check_layout_and_naming() -> list[str]:
    problems: list[str] = []

    for entry in sorted(os.listdir(ROOT)):
        if entry == ".git":
            continue
        full = os.path.join(ROOT, entry)
        if os.path.isdir(full):
            if entry not in CONTENT_DIRS:
                problems.append(f"unexpected top-level directory: {entry}/")
        elif entry not in ROOT_FILES:
            problems.append(f"unexpected root file: {entry}")

    for top in CONTENT_DIRS:
        top_path = os.path.join(ROOT, top)
        if not os.path.isdir(top_path):
            problems.append(f"missing top-level directory: {top}/")
            continue
        for dirpath, dirnames, filenames in os.walk(top_path):
            rel_dir = rel(dirpath)
            for name in dirnames:
                path = f"{rel_dir}/{name}"
                check_name(path, name, is_dir=True, problems=problems)
                if not os.listdir(os.path.join(dirpath, name)):
                    problems.append(f"empty directory: {path}/")
                # Categories allow one level of nesting for BPM buckets and
                # vendor sub-packs; licenses allow licenses/<pack>/.
                if path.count("/") > 2:
                    problems.append(f"directory deeper than <category>/<subfolder>/: {path}/")
            for name in filenames:
                path = f"{rel_dir}/{name}"
                check_name(path, name, is_dir=False, problems=problems)
                if path.count("/") > 2:
                    problems.append(f"file deeper than <category>/<subfolder>/<file>: {path}")
    return problems


def check_provenance() -> list[str]:
    problems: list[str] = []
    with open(PROVENANCE, encoding="utf-8") as handle:
        prov = json.load(handle)
    packs: dict = prov["packs"]
    files: dict = prov["files"]

    disk: set[str] = set()
    for top in CONTENT_DIRS:
        for dirpath, _dirnames, filenames in os.walk(os.path.join(ROOT, top)):
            for name in filenames:
                disk.add(rel(os.path.join(dirpath, name)))

    mapped = set(files)
    for path in sorted(mapped - disk):
        problems.append(f"provenance maps a file that is gone: {path}")
    for path in sorted(disk - mapped):
        problems.append(f"file missing from provenance.json: {path}")

    sample_files: Counter = Counter()
    for path, meta in sorted(files.items()):
        pack = meta.get("pack")
        if pack not in packs:
            problems.append(f"{path}: unknown pack {pack!r}")
            continue
        if not isinstance(meta.get("original_path"), str) or not meta["original_path"]:
            problems.append(f"{path}: missing original_path")
        if path.startswith(f"{LICENSES_DIR}/"):
            continue
        sample_files[pack] += 1
        parent = path.split("/")[0]
        if parent not in packs[pack].get("categories", []):
            problems.append(f"{path}: lives in {parent}/ but that is not a category of pack {pack}")

    for code, meta in sorted(packs.items()):
        actual = sample_files.get(code, 0)
        if meta.get("sample_count") != actual:
            problems.append(f"pack {code}: sample_count={meta.get('sample_count')} but {actual} sample files are mapped")
    return problems


def check_map() -> tuple[list[str], dict]:
    problems: list[str] = []
    with open(MAP, encoding="utf-8") as handle:
        data = json.load(handle)

    if data.get("_base") != bsj.BASE:
        problems.append(f"_base is {data.get('_base')!r}, expected {bsj.BASE!r} (raw.github serves LFS pointers)")

    banks = {k for k in data if k.startswith("bank_")}
    pack_banks = {k for k in data if k.startswith("pack_")}
    aliases = {k for k in data if k != "_base" and k not in banks and k not in pack_banks}

    for key in data:
        if key != "_base" and not KEY_RE.match(key):
            problems.append(f"map key with invalid characters: {key!r}")
    for alias in sorted(aliases):
        if len(alias) < 3:
            problems.append(f"alias shorter than 3 chars: {alias}")
        elif alias.isdigit():
            problems.append(f"alias is purely numeric: {alias}")
        elif alias in bsj.RESERVED:
            problems.append(f"alias shadows a Strudel built-in: {alias}")

    for key, value in data.items():
        if key == "_base":
            continue
        paths = value if isinstance(value, list) else [value]
        for path in paths:
            if os.path.splitext(path)[1].lower() not in bsj.AUDIO_EXTENSIONS:
                problems.append(f"{key}: target is not audio: {path}")
            elif not os.path.exists(os.path.join(ROOT, path)):
                problems.append(f"{key}: target missing on disk: {path}")

    # Every directory that holds audio needs exactly one bank: one per
    # top-level category, one per nested subfolder, and one for loose audio at
    # the repository root.
    def holds_audio(directory: str) -> bool:
        try:
            names = os.listdir(directory)
        except OSError:
            return False
        return any(
            os.path.splitext(n)[1].lower() in bsj.AUDIO_EXTENSIONS for n in names
        )

    expected_banks: set[str] = set()
    for top in CATEGORY_DIRS:
        top_path = os.path.join(ROOT, top)
        if holds_audio(top_path):
            expected_banks.add("bank_" + bsj.keyify(top))
        try:
            subdirs = sorted(os.listdir(top_path))
        except OSError:
            continue
        for name in subdirs:
            sub = os.path.join(top_path, name)
            if os.path.isdir(sub) and holds_audio(sub):
                expected_banks.add("bank_" + bsj.keyify(f"{top}/{name}"))
    if holds_audio(ROOT):
        expected_banks.add("bank_root")
    if banks != expected_banks:
        problems.append(f"bank set mismatch: unexpected={sorted(banks - expected_banks)} missing={sorted(expected_banks - banks)}")

    with open(PROVENANCE, encoding="utf-8") as handle:
        prov = json.load(handle)
    packs_with_audio = {
        meta["pack"]
        for path, meta in prov["files"].items()
        if not path.startswith(f"{LICENSES_DIR}/")
        and os.path.splitext(path)[1].lower() in bsj.AUDIO_EXTENSIONS
    }
    expected_packs = {"pack_" + bsj.keyify(code) for code in packs_with_audio}
    if pack_banks != expected_packs:
        problems.append(f"pack bank set mismatch: unexpected={sorted(pack_banks - expected_packs)} missing={sorted(expected_packs - pack_banks)}")

    return problems, data


def check_breaks_order(data: dict) -> list[str]:
    problems: list[str] = []
    last: int | None = None
    # Breaks live in BPM buckets, so the BPM prefix comes after an optional
    # subfolder: breaks/<bucket>/<bpm>_<name>.wav.
    for entry in data.get("bank_breaks", []):
        match = re.match(r"^breaks/(?:[^/]+/)?(\d+)_", entry)
        if not match:
            problems.append(f"bank_breaks entry without BPM prefix: {entry}")
            continue
        bpm = int(match.group(1))
        if last is not None and bpm < last:
            problems.append(f"bank_breaks not sorted by BPM: {entry} ({bpm}) after {last}")
        last = bpm
    breaks_dir = os.path.join(ROOT, "breaks")
    for dirpath, _dirnames, filenames in os.walk(breaks_dir):
        for name in filenames:
            if not re.match(r"^\d+_", name):
                problems.append(f"breaks file without BPM prefix: {rel(os.path.join(dirpath, name))}")
    return problems


def check_gitattributes() -> list[str]:
    with open(os.path.join(ROOT, ".gitattributes"), encoding="utf-8") as handle:
        text = handle.read()
    problems: list[str] = []
    missing = [d for d in CONTENT_DIRS if f"{d}/**" not in text]
    problems += [f".gitattributes is missing the LFS rule for {d}/**" for d in missing]
    # A rule for a directory that no longer exists silently leaves its files
    # out of LFS, so flag stale entries too.
    declared = set(re.findall(r"^([A-Za-z0-9_.-]+)/\*\*\s", text, re.MULTILINE))
    problems += [
        f".gitattributes still maps a directory that does not exist: {d}/"
        for d in sorted(declared - set(CONTENT_DIRS))
    ]
    return problems


def check_map_freshness() -> list[str]:
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "build_strudel_json.py"), "--check"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [line for line in (result.stderr or result.stdout).splitlines() if line.strip()]
    return []


def check_git() -> list[str]:
    if shutil.which("git") is None or not os.path.isdir(os.path.join(ROOT, ".git")):
        return []
    problems: list[str] = []

    tracked = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True
    )
    for raw in tracked.stdout.split(b"\0"):
        path = raw.decode("utf-8", "replace")
        # Root metadata files (AGENTS.md, README.md) are exempt from the
        # lowercase naming rule; content paths are not.
        if path and path not in ROOT_FILES and re.search(r"[A-Z]", path):
            problems.append(f"uppercase path in git index: {path}")

    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True
    )
    for path in untracked.stdout.splitlines():
        if path.strip():
            problems.append(f"untracked file: {path}")
    return problems


def main() -> int:
    checks: list[tuple[str, list[str]]] = []

    checks.append(("layout & naming", check_layout_and_naming()))
    checks.append(("provenance.json", check_provenance()))
    map_problems, data = check_map()
    checks.append(("strudel.json invariants", map_problems))
    checks.append(("breaks BPM ordering", check_breaks_order(data)))
    checks.append((".gitattributes coverage", check_gitattributes()))
    checks.append(("strudel.json freshness", check_map_freshness()))
    checks.append(("git index", check_git()))

    failed = False
    for name, problems in checks:
        if problems:
            failed = True
            print(f"FAIL  {name}: {len(problems)} problem(s)")
            for problem in problems[:10]:
                print(f"      {problem}")
            if len(problems) > 10:
                print(f"      ... and {len(problems) - 10} more")
        else:
            print(f"PASS  {name}")

    if failed:
        print("lint: FAILED")
        return 1
    print("lint: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
