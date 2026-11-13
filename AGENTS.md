# AGENTS.md

Guidance for AI agents and contributors working in this repository.

## Purpose

This repo is a local library of third-party sample packs, organized at the top level into
18 flat sample-type directories (`bass/`, `breaks/`, `claps/`, `cymbals/`, `drum_fills/`,
`drum_loops/`, `fx/`, `hats/`, `instruments/`, `kicks/`, `midi/`, `percussion/`,
`snares/`, `synth_chords/`, `synth_loops/`, `synth_one_shots/`, `toms/`, `vox/`) so every leaf directory name is globally unique (for
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
ZERO G - DISC 3/Drums/Kick 1.wav     ->  kicks/kick_1__zero-g-d3.wav
```

Repository metadata files are exceptions to the content naming rule: `AGENTS.md`,
`README.md`, `.gitattributes`, `strudel.json`, `strudel.local.json`, `provenance.json`,
`build_strudel_json.py`, `lint_repo.py`, and similar files keep their conventional names.

## Directory layout

- **Type-first hierarchy.** Samples are grouped into top-level type directories; nested
  subfolders are allowed for tempo buckets and vendor sub-packs:
  - Drum one-shots: `bd/` (kicks), `sd/` (snares), `hh/` (hats), `cp/` (claps),
    `cym/` (cymbals), `toms/`, `perc/` (percussion)
  - Drum loops & fills: `drum_loops/`, `drum_fills/`, `breaks/` (BPM buckets)
  - Synths: `synth_loops/`, `synth_one_shots/`, `synth_chords/`
  - Other categories: `bass/`, `vox/`, `spoken/`, `fx/`, `instruments/`, `midi/`
  - Vendor sub-packs live beneath their category, for example `bass/zero-g/` and
    `sd/zero-g/`.
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
- Patterns use the recursive form `<category>/**` across the 19 top-level content folders
  (`bass/**`, `breaks/**`, `claps/**`, `cymbals/**`, `drum_fills/**`, `drum_loops/**`,
  `fx/**`, `hats/**`, `instruments/**`, `kicks/**`, `licenses/**`, `midi/**`,
  `percussion/**`, `snares/**`, `synth_chords/**`, `synth_loops/**`, `synth_one_shots/**`,
  `toms/**`, `vox/**`). A bare directory name such as `hits` only matches
  the directory path itself and does **not** apply attributes to files inside.
- LFS applies to **all files inside each category and license directory**, not only audio.
  This means text files and artwork under `licenses/` are also stored as LFS pointers.
- `.gitattributes`, `.gitignore`, `AGENTS.md`, `README.md`, `build_strudel_json.py`,
  `lint_repo.py`, `strudel.json`, `strudel.local.json`, and `provenance.json` are stored as
  normal text.
- Snapshot after the November 2026 type-first flattening and `provenance.json` rollout:
  8,575 tracked entries, 8,567 LFS pointers (across 31 packs), and 9 non-LFS root
  metadata files (`.gitattributes`, `.gitignore`, `AGENTS.md`, `README.md`,
  `build_strudel_json.py`, `lint_repo.py`, `provenance.json`, `strudel.json`,
  `strudel.local.json`).

## Strudel sample map

`strudel.json` at the repo root is a generated sample map for
[Strudel](https://strudel.cc). It is committed as normal text and is **not** covered by
Git LFS; only the sample and license directories are. `strudel.local.json` is the same
map with a localhost `_base` for auditioning from disk.

Load the GitHub map in a live set with:

```js
samples('github:nweiler/samples');
```

`_base` in `strudel.json` points at
`https://media.githubusercontent.com/media/nweiler/samples/main/`, not
`raw.githubusercontent.com`. Raw GitHub serves the 130-byte LFS pointer files, so audio
would fail to decode. Do not change `_base` to a raw URL.

Audition locally instead with:

```sh
npx @strudel/sampler
```

```js
samples('http://localhost:5432/strudel.local.json');
```

`strudel.local.json` has `_base` set to `http://localhost:5432/`, so the sampler serves
the audio directly from disk. Regenerate it after a port change with
`python build_strudel_json.py --local --port 5555`.

Map structure:

- `bank_<category>` — one array per top-level category (18 banks: `bank_bass`, `bank_bd`,
  `bank_breaks`, `bank_cp`, `bank_cym`, `bank_drum_fills`, `bank_drum_loops`, `bank_fx`,
  `bank_hh`, `bank_instruments`, `bank_perc`, `bank_sd`, `bank_spoken`,
  `bank_synth_chords`, `bank_synth_loops`, `bank_synth_one_shots`, `bank_toms`,
  `bank_vox`). Each includes every audio file nested below it.
- `bank_<subfolder>` — one array per nested folder with audio, so a BPM range or vendor
  sub-pack can be auditioned on its own (for example `bank_breaks_090_099`,
  `bank_bass_zero_g`). `bank_root` covers loose audio files at the repository root.
  Arrays are in natural sort order, so `n` indexes are stable.
- `pack_<pack-code>` — one array per pack (31 banks, e.g. `pack_cymatics_odyssey_edm`,
  `pack_rhythm_lab_breakbeats_collection`), built from `provenance.json` so a single
  pack can be auditioned with `s("pack_...")`. Entries are grouped by category, then
  natural sort order. Hyphens in pack codes become underscores. If a file has moved
  from its recorded path, the generator resolves it by unique filename; it refuses to
  build the map only when a file cannot be attributed at all.
- One alias per audio file — the shortest path suffix that is globally unique, sanitized
  to `[a-z0-9_]`, at least three characters, never purely numeric, and never a Strudel
  built-in name (`bd`, `sd`, `hh`, …). For example `170_erupt_drumloop_1` and
  `hihat_loop_93_bpm`. Aliases never start with `bank_` or `pack_`.
- Only WebAudio-decodable files are included (`.wav`, `.mp3`, and similar). `.rx2`, `.asd`,
  `.mid`, and artwork are intentionally absent.

The file is pretty-printed with one entry per line — `_base`, then category and folder
banks, then pack banks, then file aliases — so additions and renames produce readable
diffs. Regenerate it rather than hand-editing.

Examples:

```js
s("170_erupt_drumloop_1")         // file alias
s("bank_breaks:3")                // fourth file in the bank
s("bank_breaks").n(3)             // same thing
s("pack_cymatics_orchid").n(run(8)) // first 8 files of one pack
s("bank_bd").n(irand(148))        // random kick roulette
```

Regenerate the maps after adding, renaming, or removing audio, and commit them with the
change:

```powershell
python build_strudel_json.py                  # writes strudel.json (GitHub)
python build_strudel_json.py --local          # writes strudel.local.json
python build_strudel_json.py --check          # fails if strudel.json is stale
python build_strudel_json.py --local --check  # fails if strudel.local.json is stale
python lint_repo.py                           # checks naming, layout, provenance, freshness
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
  - Python: `__pycache__/`, `*.pyc` (bytecode written when running
    `build_strudel_json.py` or `lint_repo.py`)
- If junk appears in the tree, delete it and stage the deletion in the same commit;
  tracked junk is not ignored by `.gitignore` until it has been removed.
- Root metadata files (`.gitignore`, `.gitattributes`, `strudel.json`, `strudel.local.json`,
  `provenance.json`, `build_strudel_json.py`, `lint_repo.py`, `README.md`, `AGENTS.md`) are
  exempt from the content naming rules.
- Run `python lint_repo.py` before committing. It checks top-level layout, naming,
  depth, OS junk, empty directories, `provenance.json` consistency (bidirectional file
  map, pack references, categories, sample counts), `strudel.json` invariants and
  freshness, breaks BPM ordering, `.gitattributes` coverage, and git index health
  (uppercase paths, untracked files). It must exit 0 before a commit is made.

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

- **`breaks/` leading BPM prefix**: Files in `breaks/` are prefixed with their integer BPM (`<bpm>_<name>.<ext>`, e.g., `122_20th_century-hot_pants.wav`, `94_a_tribe_called_quest-midnight_drum_loop.wav`) and stripped of redundant trailing BPM suffixes so natural sorting orders `breaks/` and `bank_breaks` monotonically by tempo.

## Change log

- **2026-11** — Regenerated `strudel.json` for the type-first restructure and added `strudel.local.json` for `npx @strudel/sampler`. Top-level `bank_<category>` arrays now roll up nested files, so `bank_breaks` (1,141) and `bank_drum_fills` (94) are whole-category banks again, alongside per-folder banks such as `bank_breaks_090_099` and `bank_bass_zero_g`. The map now has 46 banks, 31 pack banks, and 7,463 aliases across 7,463 audio files; every referenced path exists on disk. The generator accepts `--local`, `--base`, `--port`, and `--out`, and falls back to unique-filename matching when an audio file has moved away from its recorded `provenance.json` path (3,402 files in this snapshot, with one ambiguity resolved by the `kicks→bd`/`snares→sd`/`hats→hh`/`claps→cp`/`cymbals→cym`/`percussion→perc` rename map). `strudel.local.json` uses `_base: http://localhost:5432/`; load it with `samples('http://localhost:5432/strudel.local.json')` after starting the sampler. Updated `README.md`, `.gitattributes` (LF for the new map), `.gitignore` (`__pycache__/`, `*.pyc`), and `lint_repo.py`'s root-file exemption. `provenance.json`, `.gitattributes` LFS patterns, and `lint_repo.py`'s category list still reflect the pre-restructure tree and need a follow-up.

- **2026-11** — Added per-pack virtual banks to `strudel.json`: 31 `pack_<pack-code>` banks (hyphens in codes become underscores) built from `provenance.json`, grouped by category then natural order, so one pack can be auditioned with `s("pack_...")`. The generator now refuses to build the map if an audio file is missing from `provenance.json`. Added `lint_repo.py` (layout, naming, depth, junk, provenance consistency, map invariants and freshness, breaks BPM ordering, `.gitattributes` coverage, git index checks) and a human-facing `README.md` with bank/pack tables and audition recipes. Removed the stray empty `fills/` directory. Tracked entries 8,573 → 8,575; non-LFS root metadata files 6 → 8.

- **2026-11** — Renamed top-level sample directory `vocals/` to `vox/` (1,025 files). Updated `.gitattributes` (`vox/**`), `provenance.json` (`vox` category and file paths, plus 3 relocated `roll_snare_*` paths in `snares/`), and regenerated `strudel.json` (`bank_vocals` → `bank_vox`).

- **2026-11** — Prefixed 1,925 files in `breaks/` (leaving 20 already-prefixed files unchanged, 1,945 total) with their rounded integer BPM (`56`–`176` BPM, sourced from embedded REX2 `GLOB` headers for `rhythm-lab-breakbeats-collection`, filenames for `breaks` and `vox`, and bar-length/tempo calculation for `samples-extra` and `zero-g-sample-pack`) and stripped redundant trailing BPM suffixes from 48 filenames. Updated `provenance.json` and regenerated `strudel.json` so `bank_breaks` is ordered monotonically by BPM.

- **2026-11** — Normalized and organized 970 newly added samples across 9 new packs (`vhs-chords` 700, `boom-bap-drum-loops` 100, `chiptune` 75, `rdd-dubstep` 30, `whois-rossi` 20, `mc-hip-hop` 16, `bos-riddim-angles` 12, `pml-chill-grooves` 10, `wdh-drums` 7) into their corresponding top-level category directories (`synth_chords/`, `drum_loops/`, `synth_loops/`, `synth_one_shots/`, `bass/`, `fx/`, `kicks/`, `snares/`, `hats/`, `claps/`, `percussion/`, `toms/`, `drum_fills/`, `vocals/`). Relocated 29 `vox` hip-hop drum loops from `drum_loops/` to `breaks/` and removed 30 un-normalized duplicate copies in `breaks/`. Updated `provenance.json` (22 → 31 packs, 8,567 tracked content files) and regenerated `strudel.json` (7,519 audio files/aliases across 17 directory banks).

- **2026-11** — Split `drum_one_shots/` (1,111 files) into 7 top-level drum categories (`kicks/` 184, `snares/` 360, `hats/` 98, `claps/` 50, `cymbals/` 39, `toms/` 49, `percussion/` 331) so Strudel bank indexing (`bank_kicks`, `bank_snares`, etc.) and `npx @strudel/sampler` target specific drum types. Updated `provenance.json`, `.gitattributes` (13 → 19 category rules), and regenerated `strudel.json` (11 → 17 directory banks, 6,505 audio files/aliases).

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
