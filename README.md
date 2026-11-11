# neonick-samples

A local library of third-party sample packs, reorganized by sample type for
use with [Strudel](https://strudel.cc). 31 packs, 8,567 content files, of which
7,519 are playable audio samples. Audio and pack metadata are tracked with Git
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
s("bank_kicks").n(irand(192))                 // random kick roulette
s("pack_cymatics_odyssey_edm").n(irand(367))  // random sample from one pack
s("94_a_tribe_called_quest-midnight_drum_loop") // a specific file by alias
```

Browsers cache the map. After samples are added or renamed, bust the cache:

```js
samples('https://raw.githubusercontent.com/nweiler/samples/main/strudel.json?version=2');
```

## Audition locally

Serve the repo from its root (audio loads from disk, no GitHub round trip):

```sh
npx @strudel/sampler
```

```js
samples('local:');              // same as samples('http://localhost:5432')
s("breaks").n(run(8))           // banks are plain folder names here
s("breaks").n(irand(1037))     // random break roulette
```

Note the difference: the local server names banks after folders (`breaks`),
while the GitHub map prefixes them (`bank_breaks`) and adds `pack_*` banks.

Once a map is loaded, the REPL's `sounds` tab lists every sound name with its
sample count — searchable, and useful for confirming what a bank contains.

## Banks

| Bank | Contents | Files |
|---|---|---:|
| `bank_bass` | bass one-shots and loops | 418 |
| `bank_breaks` | funk/soul/hip-hop drum breaks, ordered by BPM | 1037 |
| `bank_claps` | claps | 51 |
| `bank_cymbals` | crashes, rides, splashes | 39 |
| `bank_drum_fills` | drum fills | 94 |
| `bank_drum_loops` | drum loops | 744 |
| `bank_fx` | impacts, risers, textures | 1106 |
| `bank_hats` | closed/open hats | 101 |
| `bank_instruments` | melodic instruments | 241 |
| `bank_kicks` | kicks | 192 |
| `bank_percussion` | shakers, congas, misc percussion | 334 |
| `bank_snares` | snares and rim shots | 370 |
| `bank_synth_chords` | chord samples and stabs | 1019 |
| `bank_synth_loops` | synth loops | 413 |
| `bank_synth_one_shots` | synth one-shots | 285 |
| `bank_toms` | toms | 50 |
| `bank_vox` | vocals | 1025 |

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
| `pack_zero_g_sample_pack` | 3156 |

## Layout and conventions

- One flat directory per sample type (`kicks/`, `breaks/`, `synth_chords/`, …),
  so leaf folder names are globally unique. Pack documentation lives under
  `licenses/<pack>/`.
- Names are lowercase `a-z 0-9 _ - .`; breaks are prefixed with their BPM
  (`122_20th_century-hot_pants.wav`) so banks sort by tempo; colliding names
  from different packs get a `__<pack-code>` suffix.
- `provenance.json` maps every file back to its pack and original path, and
  records vendor, source, and license per pack.

## Maintenance

```sh
python build_strudel_json.py   # regenerate strudel.json after changes
python lint_repo.py            # check naming, layout, provenance, map freshness
```

Full rules and the change log are in `AGENTS.md`.
