# AGENTS.md

Guidance for AI agents and contributors working in this repository.

## Purpose

This repo is a local library of third-party sample packs. Each top-level directory is one
pack; audio and MIDI content is stored with Git LFS. Keep the tree tidy and consistent, but
do not delete or merge content without explicit approval.

## Naming conventions

Applies to files and directories inside the sample packs:

1. **Lowercase everything**, including extensions.
2. **Whitespace runs become a single underscore** (`_`).
3. **Underscores adjacent to hyphens are removed**, keeping the hyphen as a separator.
4. **Repeated underscores collapse to one.**
5. **Hyphens are preserved** as word separators.
6. **Other punctuation is currently preserved** — `()`, `#`, `'`, `&`, `,`, `=`, `[]`, etc.
   Do not strip or replace it without approval.

Examples:

```
Cymatics - Odyssey Open Hihat 4.wav  ->  cymatics-odyssey_open_hihat_4.wav
Antidote Audio -  Clap 6.wav         ->  antidote_audio-clap_6.wav
ZERO G - DISC 3/Drums/Kick 1.wav     ->  zero_g-disc_3/drums/kick_1.wav
```

Top-level pack directories use short, lowercase, hyphenated names, for example
`zero-g-sample-pack`, `cymatics-odyssey-edm`, and `samples-and-loops`.

Repository metadata files are exceptions to the content naming rule: `AGENTS.md`,
`.gitattributes`, and similar files keep their conventional names.

## Bulk rename procedure

Before renaming many files or directories:

1. Enumerate the tree excluding `.git`.
2. Compute every new name and check for sibling collisions after normalization.
3. Save an undo mapping (previous bulk runs wrote `$env:TEMP\opencode\rename_undo_*.tsv`).
4. Rename deepest paths first so parent directories can be renamed last.
5. Handle case-only renames through a temporary name when needed.
6. Verify afterwards that no names still contain uppercase or spaces and that the item
   count is unchanged.

## Git on Windows

- The working copy uses `core.ignorecase=true` and `core.autocrlf=true`.
- Case-only renames are unreliable with a plain `git add -A`: Git can keep the old casing
  in the index and can skip files that are already tracked. After a bulk rename, rebuild
  the index from the working tree:

  ```powershell
  git read-tree --empty
  git add -A
  ```

- Then verify the index itself, not just the working tree:

  ```powershell
  git ls-files | Where-Object { $_ -cmatch '[A-Z]' }   # should be empty
  git lfs fsck                                         # should pass
  ```

## Git LFS

- `.gitattributes` at the repo root is authoritative.
- Patterns use the recursive form `pack-name/**`. A bare directory name such as `hits`
  only matches the directory path itself and does **not** apply attributes to files inside.
- LFS currently applies to **all files inside each pack directory**, not only audio. This
  matches the original intent, but it means text files and artwork are also stored as LFS
  pointers.
- Empty files are not converted to pointers (for example `loopcult-future/icon_` remains
  an empty blob).
- `.gitattributes` itself is stored as normal text.
- Current LFS rules cover all 21 top-level packs.
- Snapshot after the November 2026 cleanup: 7,904 tracked entries, 7,902 LFS pointers,
  about 7.15 GB.

## Known issues and deferred work

Do **not** fix these without explicit approval:

- **Duplicate nested directories** are still present, for example
  `samples-extra/samples-extra`, `mode-audio-aerosol/__macosx/...`, and repeated
  `Drum Loops` / `Loop Stems` folders.
- **macOS junk** such as `_macosx/` directories and `.ds_store` files is still present.
- **Punctuation cleanup** is unfinished; roughly 1,700 names still contain characters
  such as `()`, `#`, `'`, `&`, `,`, or `=`.
- **Duplicate audio content** may exist across and within packs; deduplication has not
  been attempted.
- LFS currently covers whole pack directories; narrowing it to audio/MIDI extensions is
  an open option.

## Future organization spec

> **Add future repository organization rules and decisions in this section.**
>
> When a new convention is agreed (folder layout, duplicate handling, punctuation policy,
> LFS scope, metadata, etc.), document it here so the conventions stay in one place.

## Change log

- **2026-11** — Normalized all file and directory names (7,929 items: 218 directories and
  7,711 files), rebuilt the Git index to fix path casing, converted 7,902 files to LFS,
  and committed as `1aeb390`.
