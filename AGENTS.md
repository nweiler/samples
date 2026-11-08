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
5. **Hyphens are preserved as word separators.**
6. **Only `a-z`, `0-9`, `_`, `-`, and `.` are allowed** in names. Dots are kept for
   extensions and vendor/version forms (`soundpacks.com`, `ver.1`); do not introduce new
   dots.
7. **Do not repeat the vendor or pack name in a file or directory name.** The enclosing
   pack directory already provides that context. Strip redundant prefixes such as
   `antidote_audio-`, `cymatics-`, `cymatics-odyssey_`, `cymatics-orchid_`, `minilogue-`,
   or `moonboy-`. Keep names that are otherwise meaningful, for example
   `antidote_audio-clap_6.wav` → `clap_6.wav` and
   `cymatics-orchid_808_cyclical_c.wav` → `808_cyclical_c.wav`.

Punctuation is normalized with these rules:

| Character | Rule | Example |
|---|---|---|
| `(` `)` `[` `]` | remove the bracket, keep the contents as a separator | `apollo_[long].wav` → `apollo_long.wav` |
| `#` | `_sharp` | `c#_min` → `c_sharp_min` |
| `'` and `’` | delete | `don't` → `dont` |
| `&` | `_and_` | `r&b` → `r_and_b` |
| `,` | `_` | `laugh,_laugh` → `laugh_laugh` |
| `+` | `_` | `moogone+subphatty` → `moogone_subphatty` |
| `=` | `_` | `5x5=55` → `5x5_55` |
| `!` | delete | `hustle!!!` → `hustle` |

If normalization would collide with an existing name, keep the existing name and append
`_2`, `_3`, … to the renamed item. Different assets must not be overwritten.

Examples:

```
Cymatics - Odyssey Open Hihat 4.wav  ->  cymatics-odyssey_open_hihat_4.wav
Antidote Audio -  Clap 6.wav         ->  antidote_audio-clap_6.wav
ZERO G - DISC 3/Drums/Kick 1.wav     ->  zero_g-disc_3/drums/kick_1.wav
```

Top-level pack directories use short, lowercase, hyphenated names, for example
`zero-g-sample-pack`, `cymatics-odyssey-edm`, and `antidote-dubstep`. When the vendor is
part of the pack identity, prefix it: `mode-audio-aerosol`,
`soundpacks-com-magical-chords-samples`.

Repository metadata files are exceptions to the content naming rule: `AGENTS.md`,
`.gitattributes`, `strudel.json`, `build_strudel_json.py`, and similar files keep their
conventional names.

## Directory layout

- **One top-level directory per pack.** Do not nest a pack inside a same-named vendor
  folder. A shape like `pack/pack/...` or `pack/vendor_pack/...` is a wrapper and should
  be collapsed.
- **Audio is grouped by category** below the pack root, for example `drum_loops/`,
  `drum_one_shots/`, `midi/`, `fx/`. Category names are reused across packs on purpose;
  they are not duplicates.
- **Metadata stays at the pack root**: `license.txt`, artwork, previews, and vendor
  `.url` files. Do not mix metadata into audio category folders.
- **Grouping folders are allowed when they add meaning**, for example
  `synth_loops/drop_loops/<track>_stems/` or `wav/1`, `wav/2`. Do not add a wrapper that
  holds only one child; fold it into the parent.
- **No duplicate pack trees.** Each pack has one canonical copy; byte-identical copies
  must be removed rather than kept side by side.
- **Keep differently-named assets** even when their bytes match (for example alternate
  MIDI presets, numbered one-shots, or per-context promo files). Only delete true copy
  artifacts such as timestamped download duplicates.
- Aim for **maximum path depth of 5** below the repo root.

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
- Empty files are not converted to pointers (for example `loopcult-future/icon` remains
  an empty blob).
- `.gitattributes` itself is stored as normal text.
- Current LFS rules cover all 18 top-level packs.
- Snapshot after the November 2026 structural cleanup: 7,271 tracked entries, 7,267 LFS
  pointers, about 6.86 GB.

## Strudel sample map

`strudel.json` at the repo root is a generated sample map for
[Strudel](https://strudel.cc). It is committed as normal text and is **not** covered by
Git LFS; only the pack directories are.

Load it in a live set with:

```js
samples('github:nweiler/samples');
```

`_base` in the map points at `https://media.githubusercontent.com/media/nweiler/samples/main/`,
not `raw.githubusercontent.com`. Raw GitHub serves the 130-byte LFS pointer files, so audio
would fail to decode. Do not change `_base` to a raw URL.

Map structure:

- `bank_<flattened-directory>` — one array per directory that contains audio, for example
  `bank_breaks` or `bank_zero_g_sample_pack_zero_g_disc_3_vocals`. Arrays are in natural
  sort order, so `n` indexes are stable.
- One alias per audio file — the shortest path suffix that is globally unique, sanitized
  to `[a-z0-9_]`, at least three characters, never purely numeric, and never a Strudel
  built-in name (`bd`, `sd`, `hh`, …). For example `erupt_170` and `cymatics_orchid_hihat_loop_93_bpm`.
- Only WebAudio-decodable files are included (`.wav`, `.mp3`, and similar). `.rx2`, `.asd`,
  `.mid`, and artwork are intentionally absent.

The file is pretty-printed with one entry per line — `_base`, then banks, then file
aliases — so additions and renames produce readable diffs. Regenerate it rather than
hand-editing.

Examples:

```js
s("erupt_170")                    // file alias
s("bank_breaks:3")                // fourth file in the bank
s("bank_breaks").n(3)             // same thing
```

Regenerate the map after adding, renaming, or removing audio, and commit it with the
change:

```powershell
python build_strudel_json.py           # writes strudel.json
python build_strudel_json.py --check   # fails if the map is stale
```

The generator defaults to the repo root (the script's directory). Browsers may cache the
map; when testing an update, load the JSON directly with a cache-busting query:

```js
samples('https://raw.githubusercontent.com/nweiler/samples/main/strudel.json?version=2');
```

## Repository hygiene

- `.gitignore` at the repo root excludes OS metadata. Do not commit these files or
  remove their patterns without approval:
  - macOS: `.ds_store`, `._*` (AppleDouble), `_macosx/`, `__macosx/`, `.appleDouble`,
    `.lsOverride`, `.localized`, `.apdisk`, `.fseventsd/`, `.spotlight-v100/`,
    `.trashes/`, `.temporaryitems/`, `.documentrevisions-v100/`, `.volumeicon.icns`
  - Windows: `thumbs.db`, `ehthumbs.db`, `ehthumbs_vista.db`, `desktop.ini`,
    `$recycle.bin/`
- If junk appears in the tree, delete it and stage the deletion in the same commit;
  tracked junk is not ignored by `.gitignore` until it has been removed.
- Root metadata files (`.gitignore`, `.gitattributes`, `strudel.json`,
  `build_strudel_json.py`) are exempt from the content naming rules.

## Known issues and deferred work

Do **not** fix these without explicit approval:

- **Intentional overlaps** remain, for example the free ModeAudio tasters vs the full
  pack. Do not dedupe across packs without approval.
- LFS currently covers whole pack directories; narrowing it to audio/MIDI extensions is
  an open option.

## Future organization spec

> **Add future repository organization rules and decisions in this section.**
>
> When a new convention is agreed (folder layout, duplicate handling, punctuation policy,
> LFS scope, metadata, etc.), document it here so the conventions stay in one place.

## Change log

- **2026-11** — Removed redundant vendor/pack prefixes from 807 files and 35 `_stems`
  directories in `antidote-dubstep`, `cymatics-chaos`, `cymatics-odyssey-edm`,
  `cymatics-orchid`, `minilogue`, and `moonboy-bass`; regenerated `strudel.json`. No
  content changed and file count stayed at 7,273.
- **2026-11** — Added the generated Strudel sample map (`strudel.json`) and its generator
  (`build_strudel_json.py`): 197 directory banks and a short alias for all 6,220 playable
  audio files, pointed at the GitHub LFS media host and pretty-printed one entry per line.
- **2026-11** — Relocated the 90-file `samples-extra/snare/` set to
  `zero-g-sample-pack/zero_g-disc_2/hits/snare/` (working-tree move found at commit
  time). No content changed and no duplicates introduced.
- **2026-11** — Removed the timestamped duplicate of `sl_troopers-movement.wav` from
  `samples-extra/break/` (byte-identical to the rhythm-lab original). 7,272 → 7,271
  files.
- **2026-11** — Punctuation cleanup: normalized all remaining special characters in
  1,556 file/directory renames (`()` `[]` `#` `'` `&` `,` `+` `=` `!`). No content
  changed; the two genuine `don't`/`dont` collisions were resolved with `_2`. File count
  unchanged at 7,272.
- **2026-11** — Layout cleanup: moved rhythm-lab's 877 loose wavs into `wav/` and
  collapsed `rhythm-lab.com_breakbeats_collection/`; removed both `loop_stems/` grouping
  levels and the lone `no_sidechain/` wrapper in `cymatics-odyssey-edm`; removed one
  timestamped samples-extra download duplicate. Max depth 6 → 5. 7,273 → 7,272 files.
- **2026-11** — Structural cleanup: collapsed 6 redundant wrapper directories, removed
  duplicate Antidote packs (`hits`, `samples-and-loops`), merged the two Magical Chords
  packs into `soundpacks-com-magical-chords-samples`, and removed duplicate Cymatics
  promo folders. 21 → 18 packs, 7,487 → 7,273 files, 7.15 → 6.86 GB.
- **2026-11** — Added `.gitignore` for OS metadata and removed all tracked junk:
  419 files (72 `.ds_store`, 347 AppleDouble `._*`) and 4 `_macosx/` directories,
  about 0.59 MB total.
- **2026-11** — Normalized all file and directory names (7,929 items: 218 directories and
  7,711 files), rebuilt the Git index to fix path casing, converted 7,902 files to LFS,
  and committed as `1aeb390`.
