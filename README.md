# neonick-samples

A local library of third-party sample packs, reorganized by sample type for
use with [Strudel](https://strudel.cc). 31 packs, 7,605 content files, of which
7,463 are playable audio samples. Audio and pack metadata are tracked with Git
LFS; every file's pack and original path is recorded in `provenance.json`.

## Play it in Strudel

Load the map from GitHub:

```js
samples('github:nweiler/samples');
```

Then:

```js
s("bank_breaks:3")                            // 4th break, ordered by tempo
s("bank_breaks").n(run(16))                   // first 16 breaks, tempo order
s("bank_bd").n(irand(148))                    // random kick roulette
s("pack_cymatics_odyssey_edm").n(irand(367))  // random sample from one pack
s("94_a_tribe_called_quest_midnight_drum_loop") // a specific file by alias
```

Browsers cache the map. After samples are added or renamed, bust the cache:

```js
samples('https://raw.githubusercontent.com/nweiler/samples/main/strudel.json?version=2');
```

## Audition locally

Serve the repo from its root, then load the local map. `strudel.local.json` is
identical to `strudel.json` except that `_base` points at the sampler, so the
same banks, pack banks, and aliases work from disk without a GitHub round trip:

```sh
npx @strudel/sampler          # http://localhost:5432
```

```js
samples('http://localhost:5432/strudel.local.json');
s("bank_breaks").n(run(8));
s("bank_bd").n(irand(148));
```

Use a different port with `PORT=5555 npx @strudel/sampler`, then regenerate the
local map with `python build_strudel_json.py --local --port 5555`.

The sampler can also synthesize a map on the fly with `samples('local:')`. That
map has no pack banks and names banks after leaf folders (`breaks`, `090-099`,
`zero-g`), so prefer `strudel.local.json` for the full library.

Once a map is loaded, the REPL's `sounds` tab lists every sound name with its
sample count — searchable, and useful for confirming what a bank contains.

## Banks

| Bank | Contents | Files |
|---|---|---:|
| `bank_bass` | bass one-shots and loops | 418 |
| `bank_bd` | kicks (`bd` = Strudel kick) | 148 |
| `bank_breaks` | funk/soul/hip-hop drum breaks, ordered by BPM | 1141 |
| `bank_cp` | claps (`cp`) | 51 |
| `bank_cym` | crashes, rides, splashes | 39 |
| `bank_drum_fills` | drum fills | 94 |
| `bank_drum_loops` | drum loops | 637 |
| `bank_fx` | impacts, risers, textures | 1106 |
| `bank_hh` | closed/open hats (`hh`) | 89 |
| `bank_instruments` | melodic instruments | 241 |
| `bank_perc` | shakers, congas, misc percussion | 334 |
| `bank_sd` | snares and rim shots (`sd`) | 370 |
| `bank_spoken` | spoken word and field recordings | 22 |
| `bank_synth_chords` | chord samples and stabs | 1019 |
| `bank_synth_loops` | synth loops | 413 |
| `bank_synth_one_shots` | synth one-shots | 285 |
| `bank_toms` | toms | 50 |
| `bank_vox` | vocals | 1004 |
| `bank_root` | loose format-neutral files at the repo root | 2 |

Top-level banks include everything nested below them. Nested folders also get
their own banks: the 13 `bank_breaks_<bpm-range>` buckets (for example
`bank_breaks_090_099`), the `bank_drum_fills_*` buckets, and the
`bank_<category>_zero_g` subsets.

## Pack banks

`strudel.json` also generates one bank per pack, so a single pack can be
browsed at a time. Entries are grouped by category, then natural order:

| Pack bank | Files |
|---|---:|
| `pack_antidote_dubstep` | 62 |
| `pack_boom_bap_drum_loops` | 100 |
| `pack_bos_riddim_angles` | 12 |
| `pack_breaks` | 40 |
| `pack_bt_vintage_modernized_kicks_volume_1` | 10 |
| `pack_chiptune` | 75 |
| `pack_cymatics_chaos` | 52 |
| `pack_cymatics_odyssey_edm` | 367 |
| `pack_cymatics_orchid` | 175 |
| `pack_deep_space_chord_samples` | 46 |
| `pack_focusrite_drum_pack` | 210 |
| `pack_foley` | 13 |
| `pack_loopcult_future` | 240 |
| `pack_mc_hip_hop` | 16 |
| `pack_minilogue` | 97 |
| `pack_mode_audio_aerosol` | 162 |
| `pack_mode_audio_aerosol_free` | 6 |
| `pack_mode_audio_spectre_free` | 6 |
| `pack_moonboy_bass` | 12 |
| `pack_nu_wav_baby_audio` | 23 |
| `pack_pml_chill_grooves` | 10 |
| `pack_rdd_dubstep` | 30 |
| `pack_rhythm_lab_breakbeats_collection` | 898 |
| `pack_sampleradar_mammoth_synth_chords_sample_pack` | 180 |
| `pack_samples_extra` | 608 |
| `pack_soundpacks_com_magical_chords_samples` | 90 |
| `pack_vhs_chords` | 700 |
| `pack_vox` | 96 |
| `pack_wdh_drums` | 7 |
| `pack_whois_rossi` | 20 |
| `pack_zero_g_sample_pack` | 3100 |

## Layout and conventions

- Top-level directories group samples by type (`bd/`, `sd/`, `hh/`, `cp/`,
  `cym/`, `perc/`, `breaks/`, `synth_chords/`, …). Some categories have nested
  folders for BPM ranges (`breaks/090-099/`) or vendor sub-packs
  (`bass/zero-g/`). Pack documentation lives under `licenses/<pack>/`.
- Names are lowercase `a-z 0-9 _ - .`; breaks are prefixed with their BPM
  (`122_20th_century-hot_pants.wav`) so banks sort by tempo; colliding names
  from different packs get a `__<pack-code>` suffix.
- `provenance.json` maps every file back to its pack and original path, and
  records vendor, source, and license per pack.

## Maintenance

```sh
python build_strudel_json.py            # regenerate strudel.json (GitHub)
python build_strudel_json.py --local    # regenerate strudel.local.json
python lint_repo.py                     # check naming, layout, map freshness
```

Full rules and the change log are in `AGENTS.md`.
