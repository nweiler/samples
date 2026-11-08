# AGENTS.md

Guidance for AI agents and contributors working in this repository.

## Purpose

This repo is a local library of third-party sample packs, organized at the top level into
12 flat sample-type directories (`bass/`, `breaks/`, `drum_fills/`, `drum_loops/`,
`drum_one_shots/`, `fx/`, `instruments/`, `midi/`, `synth_chords/`, `synth_loops/`,
`synth_one_shots/`, `vocals/`) so every leaf directory name is globally unique (for
`npx @strudel/sampler` compatibility), with pack provenance and original paths recorded
in `provenance.json` and per-pack documentation under `licenses/<pack>/`. Audio, MIDI,
and pack metadata are stored with Git LFS. Keep the tree tidy and consistent, but do not
delete or merge content without explicit approval.

## Naming conventions

Applies to files and directories inside the library:

1. **Lowercase everything**, including extensions.
2. **Whitespace runs become a single underscore** (`_`).
3. **Underscores adjacent to hyphens are removed**, keeping the hyphen as a separator.
4. **Repeated underscores collapse to one** (except the `__<pack-code>` disambiguation
   separator described in rule 7).
5. **Hyphens are preserved as word separators.**
6. **Only `a-z`, `0-9`, `_`, `-`, and `.` are allowed** in names. Dots are kept for
   extensions and vendor/version forms (`soundpacks.com`, `ver.1`); do not introduce new
   dots.
7. **Do not repeat the vendor or pack name in a file name unless disambiguating a
   collision.** Strip redundant vendor prefixes such as `antidote_audio-`, `cymatics-`,
   `cymatics-odyssey_`, `cymatics-orchid_`, `minilogue-`, or `moonboy-`. When two files
   from different packs (or sub-packs/discs) would collide in the same type folder,
   keep the first name as-is and suffix subsequent colliding files with `__<pack-code>`
   (for example `kick_1.wav`, `kick_1__zero-g-d2.wav`, `kick_1__zero-g-d3.wav`). Every
   file's pack identity and original path are tracked in `provenance.json`.

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

If normalization would collide with an existing name within the same pack/code, keep the
existing name and append `_2`, `_3`, … to the renamed item. Different assets must not be
overwritten.

Examples:

```
Cymatics - Odyssey Open Hihat 4.wav  ->  open_hihat_4.wav
Antidote Audio -  Clap 6.wav         ->  clap_6.wav
ZERO G - DISC 3/Drums/Kick 1.wav     ->  drum_one_shots/kick_1__zero-g-d3.wav
```

Repository metadata files are exceptions to the content naming rule: `AGENTS.md`,
`.gitattributes`, `strudel.json`, `provenance.json`, `build_strudel_json.py`, and similar
files keep their conventional names.

## Directory layout

- **Type-first 1-level flat hierarchy (max depth 1 for samples).** Every sample category is
  a single top-level directory so leaf folder names are 100% unique (avoiding collisions in
  tools like `npx @strudel/sampler` that index by leaf folder name):
  - `drum_loops/`, `drum_one_shots/`, `drum_fills/`
  - `synth_loops/`, `synth_one_shots/`, `synth_chords/`
  - `bass/`
  - `vocals/`
  - `fx/`
  - `instruments/`
  - `breaks/`
  - `midi/`
- **Provenance and licenses**:
  - `provenance.json` at the repo root records every pack's metadata (`code`, `vendor`,
    `source`, `license`, `license_files`, `categories`, `sample_count`, `notes`) and maps
    every file path back to its `pack` and `original_path`.
  - `licenses/<pack>/` holds all non-sample pack documentation (`license.txt`, `.pdf`,
    `.rtf`, `.url`, artwork `.jpg`, and `.vst` files). Do not mix metadata into sample
    category folders.
- **No duplicate packs.** Each pack has one canonical copy; byte-identical copies
  must be removed rather than kept side by side.
- **Keep differently-named assets** even when their bytes match (for example alternate
  MIDI presets, numbered one-shots, or per-context promo files). Only delete true copy
  artifacts such as timestamped download duplicates.
- Aim for **maximum path depth of 2** for samples (`<category>/<file>`) and 3 for
  `licenses/<pack>/<file>`.

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
- Patterns use the recursive form `<category>/**` across the 13 top-level content folders
  (`bass/**`, `breaks/**`, `drum_fills/**`, `drum_loops/**`, `drum_one_shots/**`, `fx/**`,
  `instruments/**`, `licenses/**`, `midi/**`, `synth_chords/**`, `synth_loops/**`,
  `synth_one_shots/**`, `vocals/**`). A bare directory name such as `hits` only matches
  the directory path itself and does **not** apply attributes to files inside.
- LFS applies to **all files inside each category and license directory**, not only audio.
  This means text files and artwork under `licenses/` are also stored as LFS pointers.
- `.gitattributes`, `.gitignore`, `AGENTS.md`, `build_strudel_json.py`, `strudel.json`,
  and `provenance.json` are stored as normal text.
- Snapshot after the November 2026 type-first flattening and `provenance.json` rollout:
  7,559 tracked entries, 7,553 LFS pointers (across 22 packs), and 6 non-LFS root
  metadata files (`.gitattributes`, `.gitignore`, `AGENTS.md`, `build_strudel_json.py`,
  `provenance.json`, `strudel.json`).

## Strudel sample map

`strudel.json` at the repo root is a generated sample map for
[Strudel](https://strudel.cc). It is committed as normal text and is **not** covered by
Git LFS; only the sample and license directories are.

Load it in a live set with:

```js
samples('github:nweiler/samples');
```

`_base` in the map points at `https://media.githubusercontent.com/media/nweiler/samples/main/`,
not `raw.githubusercontent.com`. Raw GitHub serves the 130-byte LFS pointer files, so audio
would fail to decode. Do not change `_base` to a raw URL.

Map structure:

- `bank_<flattened-directory>` — one array per directory that contains audio (11 banks:
  `bank_bass`, `bank_breaks`, `bank_drum_fills`, `bank_drum_loops`,
  `bank_drum_one_shots`, `bank_fx`, `bank_instruments`, `bank_synth_chords`,
  `bank_synth_loops`, `bank_synth_one_shots`, `bank_vocals`). Arrays are in natural sort
  order, so `n` indexes are stable.
- One alias per audio file — the shortest path suffix that is globally unique, sanitized
  to `[a-z0-9_]`, at least three characters, never purely numeric, and never a Strudel
  built-in name (`bd`, `sd`, `hh`, …). For example `170_erupt_drumloop_1` and
  `hihat_loop_93_bpm`.
- Only WebAudio-decodable files are included (`.wav`, `.mp3`, and similar). `.rx2`, `.asd`,
  `.mid`, and artwork are intentionally absent.

The file is pretty-printed with one entry per line — `_base`, then banks, then file
aliases — so additions and renames produce readable diffs. Regenerate it rather than
hand-editing.

Examples:

```js
s("170_erupt_drumloop_1")         // file alias
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
- Root metadata files (`.gitignore`, `.gitattributes`, `strudel.json`, `provenance.json`,
  `build_strudel_json.py`) are exempt from the content naming rules.

## Known issues and deferred work

Do **not** fix these without explicit approval:

- **Intentional overlaps** remain, for example the free ModeAudio tasters vs the full
  pack. Do not dedupe across packs without approval.
- LFS currently covers whole category directories; narrowing it to audio/MIDI extensions is
  an open option.

## Future organization spec

> **Add future repository organization rules and decisions in this section.**
>
> When a new convention is agreed (folder layout, duplicate handling, punctuation policy,
> LFS scope, metadata, etc.), document it here so the conventions stay in one place.

## Change log

- **2026-11** — Flattened the 23 pack trees into a type-first 1-level hierarchy (`bass/`,
  `breaks/`, `drum_fills/`, `drum_loops/`, `drum_one_shots/`, `fx/`, `instruments/`,
  `midi/`, `synth_chords/`, `synth_loops/`, `synth_one_shots/`, `vocals/`) so all leaf
  directory names are globally unique for `npx @strudel/sampler`, and consolidated pack
  documentation under `licenses/<pack>/` (max depth 5 → 2 for samples). Added
  `provenance.json` at the repo root recording vendor/source/license metadata for all 22
  packs and mapping all 7,553 content files back to their source pack and original path.
  Removed the duplicate 12-file `bass/` pack (byte-identical to `moonboy-bass`) and the
  empty `loopcult-future/icon` file. Disambiguated 1,580 colliding basenames with
  `__<pack-code>` suffixes while leaving 5,973 filenames unchanged. Updated
  `.gitattributes` (23 pack rules → 13 category rules) and regenerated `strudel.json`
  (215 → 11 directory banks, 6,517 → 6,505 audio files/aliases).

- **2026-11** — Normalised `focusrite-drum-pack`, `breaks`, `bass`, `foley`, and
  `bt-vintage-modernized-kicks-volume-1` under the naming rules: 263 files and 14
  directories renamed (lowercased, spaces to `_`, `#` to `_sharp`, `(1)` suffix dropped,
  `MOONBOY -` vendor prefix stripped). De-duplicated `breaks/`, which held a
  byte-identical pre-normalized twin for every messy name: removed the 38 twins, keeping
  the descriptive names, and dropped the duplicate `foley` download. 7,610 → 7,571
  tracked entries. Rebuilt the index for the case-only renames and regenerated
  `strudel.json` (6,556 → 6,517 aliases, banks unchanged at 215).
- **2026-11** — Cleaned `vox/`: renamed 21 YouTube-style files by dropping the
  `[video-id]` hashes and normalizing punctuation, then split the 52 flat files into
  `music/` (29), `speech/` (11), `percussion/` (7), and `phrases/` (4). Removed
  `locked.wav`, byte-identical to `all.wav`. 52 → 51 files, no content changed.
- **2026-11** — Extended LFS to the five packs that were missing rules (`bass`,
  `bt-vintage-modernized-kicks-volume-1`, `focusrite-drum-pack`, `foley`, `vox`),
  18 → 23 packs, renormalising their existing blobs into pointers. Those five packs had
  never been mapped, so they also account for the `strudel.json` growth: 197 → 215 banks,
  6,219 → 6,517 aliases.
- **2026-11** — Removed one break sample from `breaks/` at the owner's request and
  regenerated `strudel.json`. File count 7,273 → 7,272.
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
