---
title: "README — Mozilla Lost in Transcription (Indonesian–Javanese)"
aliases:
  - README
  - Peta Repo
tags:
  - index
status: closed
updated: 2026-10-21
---

# Mozilla *Lost in Transcription*: Indonesian–Javanese track

Research and pipeline of team **"Bulu Hidung"** for the Indonesian–Javanese code-switched ASR
challenge (Mozilla Data Collective × DrivenData). Model: `openai/whisper-large-v3-turbo`
fine-tuned with language token `jw`. All compute ran on **Kaggle**. This repo holds the notebooks,
notes and small outputs (CSV/JSON) only. Model weights live on a private HuggingFace account, and
the raw corpora (`Datasets/`) and submission ZIPs are not tracked in git.

**The competition is closed.** Metric: WER with the official `score.py` normalizer (case-sensitive).

**Write-up:** the story behind these notebooks, from the zero-shot baseline to the dev set that
pointed the wrong way, is on Medium:
[The dev set lied: fine-tuning Whisper for Javanese on a free GPU](https://medium.com/@hamzapratama000/the-dev-set-lied-fine-tuning-whisper-for-javanese-on-a-free-gpu-fad887c18527).
A shorter case study is on [hamza-pratama.is-a.dev](https://hamza-pratama.is-a.dev/projects/javanese-asr).

> Most notes in `plan/`, `reports/` and `docs/` are written in Indonesian. Notebook code and
> comments are mostly in English.

## Final result (private leaderboard, read 20 Oct 2026)

| | |
|---|---|
| Final standing | **Rank 18, private WER 0.2576** (private leaderboard, the one that decides the competition; #1 0.1983, #10 0.2387). The leaderboard shows the team's best private score only, so which submission produced it is not recorded here |
| Best public test WER | **0.2497, public rank 25**: arm L = stage 1 E4-native **+ TTS Central Javanese**, then stage 2 on the official dev set, beam 5 (submission `3516`, 3 Oct) |
| Earlier arms | J 0.2655 (stage 1, two epochs), F 0.2660 (E4-native + stage 2), K 0.2698 (+ Homostoria podcast), D 0.2901 (E4-native, beam 5), E4 beam 5 0.2950, H 0.3088 (no stage 1) |
| Main findings | (1) A short stage 2 on the official dev set (learning the reference transcription convention) cut test WER by 0.024. (2) Stage 1 is worth about 0.04 (H), but what helped was **Javanese data** (L −0.016), not more epochs (J) or Indonesian conversational speech (K +0.004). (3) The official dev set (4 speakers) could not judge stage-1 changes: it got the sign wrong for H and K and called L a tie. |

Every submission, with ZIP hashes and platform logs: [`submissions/README.md`](submissions/README.md).

## Pipeline in one paragraph

**Stage 1** fine-tunes whisper-large-v3-turbo for one epoch on native Jember segments (Javanese
spontaneous speech), a curated 6.5 h slice of Common Voice Indonesian packed into ~25 s items, and,
in the final arm, 8 h of TTS Central Javanese (`notebooks/06-data-mixing.ipynb` and its
descendants `12`–`14`). **Stage 2** continues for 3 epochs at LR 3e-6 on the official dev clips up to 30 s (335 of 372),
so the model learns the reference convention (`notebooks/10-dev-stage-finetune.ipynb`).
**Packaging** builds the submission ZIP (fp16 weights + `main.py`, beam 5, chunked decoding for
clips over 30 s) and proves parity against the training notebook's predictions inside a replica of
the competition container (`notebooks/08-packaging.ipynb`).

## Deliberately left out of this public repo

The competition's official rules forbid publishing or redistributing the competition Data, and that
obligation survives the end of the competition. This repo therefore does **not** contain:
- the organiser's official files (`competition/*.csv`: test and smoke clip lists);
- per-clip outputs on the official dev set: `predictions_official_dev.csv`, `baseline_zeroshot.json`,
  `submission_dev_*.csv`, `error_table_official_dev.csv`, per-clip omniASR CSVs, and the
  `run-log.txt` files that print dev clip names;
- the raw corpora (`Datasets/`), model weights (private HuggingFace) and submission ZIPs.

All aggregate numbers (WER, error counts, confidence intervals) remain in `dataset_findings.json`,
the reports and the ledger. In `notebooks/08-packaging.ipynb` the five hard-coded smoke-test clip
names were replaced by reading the attached official file. The exact list is in `.gitignore`.

## Repo map

```
README.md          <- this file: map, results, conventions
LICENSE            <- MPL 2.0, for the code
LICENSE-DATA.md    <- sources and licences of the derived data in findings/
CLAUDE.md          <- working rules for AI coding agents (Indonesian)
docs/              feasibility study, rules review, rename log
plan/              execution plan + one brief per notebook (nbNN-brief-*.md)
reports/           results and analysis per notebook (nbNN-*-results.md, ...)
notebooks/         Kaggle notebooks NN-*.ipynb + utility scripts
findings/          notebook outputs, mirror of /kaggle/working/findings/<run-id>/
submissions/       platform submission ledger + raw logs (logs/id-<n>_*.txt)
competition/       organiser files (README only in git)
Datasets/          raw corpora + Kaggle upload staging (local only; README only in git)
.obsidian/         the repo is also an Obsidian vault (notes link to each other via wikilinks)
```

Naming: ASCII kebab-case. The `nbNN-` prefix ties a note to notebook `NN`. Each note keeps its old
name as an alias in its frontmatter; the old → new map is in
[`docs/renames-2026-09-26.tsv`](docs/renames-2026-09-26.tsv).

## Notebooks and their artefacts

| NN | Notebook | What it does | Outcome | `findings/` | Notes |
|---|---|---|---|---|---|
| 01 | `01-dataset-eda.ipynb` | EDA of the three corpora | done | `01-dataset-eda` | [nb01](reports/nb01-dataset-analysis.md) |
| 02 | `02-data-build.ipynb`, `02-verify.ipynb` | Jember segmentation → Kaggle dataset `jember-segments-16k`, scorer, split | Gate 1 passed 25 Aug (28/28) | `02-data-build`, `02-verify` | [nb02](reports/nb02-data-build-results.md), [cross-audit](reports/nb02-cross-audit-scorer-text-2026-08-26.md) |
| — | — | analysis of the 372 official dev clips | done | — | [dev set analysis](reports/official-dev-set-analysis-2026-08-28.md) |
| 03 | `03-zeroshot.ipynb` | zero-shot baseline | done | `03-zeroshot`, `03-zeroshot-dryrun` | [nb03](reports/nb03-zeroshot-baseline-results.md) |
| 04 | `04-whisper-core.ipynb` | Jember-only fine-tune: native vs concat25, 3 vs 1 epoch | Gate 2 passed 31 Aug | `04-whisper-core*` | [nb04](reports/nb04-whisper-core-results.md) |
| 05 | — | XLS-R CTC + LM | not pursued | — | [brief](plan/nb05-brief-xlsr-ctc-lm.md) |
| 06 | `06-mix-build.ipynb`, `06-mix-verify.ipynb` | build the mixed dataset `jv-mix-16k` (CPU, phased) | verified 52/52 | `06-mix-build`, `06-mix-verify` | [nb06](reports/nb06-data-mixing-results.md) |
| 06 | `06-data-mixing.ipynb` | arms E3–E6 + **E4-native** (GPU) | Gate 4 closed 7 Sep (E4); E4-native 25 Sep | `06-data-mixing-*` | [nb06](reports/nb06-data-mixing-results.md) |
| 07 | — | error analysis + post-processing rules | not built | — | [brief](plan/nb07-brief-error-analysis-robustness.md) |
| 08 | `08-packaging.ipynb` | submission ZIP + container rehearsal + dev parity | used for every submission: B, D, F, P, H, J, K, **L (final, 3 Oct)** | `08-packaging*` | [brief](plan/nb08-brief-packaging-submission.md), [ledger](submissions/README.md) |
| 09 | `09-omniasr-zeroshot.ipynb` | omniASR zero-shot on the official dev (gap evaluation); separate venv | done 28 Sep: loses to D (v2 0.2518 vs 0.2268), lead closed | `09-omniasr-zeroshot*` | [gap eval 2](reports/gap-eval-2-omniasr-zeroshot-2026-09-28.md) |
| 10 | `10-dev-stage-finetune.ipynb` | stage 2 on the official dev (recipe F) on top of any stage-1 checkpoint | c5 −0.0267 on held-out convo 2; `all` = F 0.2660; `t0-all` = H 0.3088; `2ep-all` = J 0.2655; `homo-all` = K 0.2698; **`tts-all` = L 0.2497** | `10-dev-stage-finetune-*` | [nb10](reports/nb10-dev-stage-finetune-results.md) |
| 11 | `11-large-v3-probe.ipynb` | large-v3 vs turbo zero-shot on dev + T4 VRAM/speed probe | done 30 Sep (17/17): large-v3 zero-shot worse than turbo (+0.0138, CI [+0.005, +0.022]) and full fine-tune OOMs on a T4 → **closed** | `11-large-v3-probe-zeroshot-feasibility` | [nb11](reports/nb11-large-v3-probe-results.md) |
| 12 | `12-stage1-2epoch.ipynb` | stage 1 E4-native with **2 epochs** (one variable: `NUM_EPOCHS`) | run 1 lost its weights (HF quota); r2 1 Oct (21/21) → arm J, **test 0.2655** (F 0.2660: the second epoch did not help) | `12-stage1-2epoch-*` | [nb11](reports/nb11-large-v3-probe-results.md) (motivation: H test 0.3088) |
| 13 | `13-stage1-homostoria.ipynb` | stage 1 E4-native **+ Podcast Homostoria** (4,693 segments, 7.67 h Indonesian conversation) | 2 Oct (24/24): dev greedy 0.2096 vs 0.2317 (−0.0221) → arm K, **test 0.2698**: dev got the sign wrong | `13-stage1-homostoria-E4-native-homo` | [nb13](reports/nb13-stage1-homostoria-results.md) |
| 14 | `14-stage1-tts.ipynb` | stage 1 E4-native **+ TTS Central Javanese** (jv-mix-16k arm E1, 1,368 items / 8.02 h) | 3 Oct (23/23): dev tie (0.2339 vs 0.2317), Javanese-token WER 0.2425 → 0.2065 → arm L, **public test 0.2497 (best, public rank 25)**; final private 0.2576, rank 18 | `14-stage1-tts-E4-native-tts` | [nb14](reports/nb14-stage1-tts-results.md) |

Utility scripts: `util-audit-mounts.py` (audit Kaggle datasets against the MDC catalogue),
`util-pack-cv-subset.py` (pack a Common Voice subset for upload),
`util-extract-findings.ipynb` (pull the small findings folder out of a large Kaggle output).

## Checkpoints (HuggingFace, private, account `amozaurus`)

| Name | Repo @ revision | `model.safetensors` sha16 | Official dev (372) | Test |
|---|---|---|---|---|
| E4 | `mozilla-jv-06-data-mixing-E4@c79347a5` | `c58b0538dc4c2008` | 0.2309 greedy / 0.2260 beam 5 | 0.3005 / 0.2950 |
| **E4-native** | `mozilla-jv-06-data-mixing-E4-native@3437f442` | `b3438f32cf61ebbe` | 0.2313 greedy / 0.2268 beam 5 | — / **0.2901** |
| NB04 native | `mozilla-jv-04-whisper-core@9c00033f` | `3fc3a15f80cb7084` | 0.2647 | 0.3027 |
| NB04 concat25 1 ep | `mozilla-jv-04-whisper-core-full-concat25-1epoch@0a415ce6` | — | 0.2532* | — |
| F (E4-native + stage 2) | `mozilla-jv-10-dev-stage-finetune-all@e4df20fb` | `058f6d26fd621170` | dev fit† | — / 0.2660 |
| J (2 epochs + stage 2) | `mozilla-jv-10-dev-stage-finetune-2ep-all@b368a2ce` | `6680ef3cc3dab73e` | dev fit† | — / 0.2655 |
| **L (+ TTS + stage 2)** | `mozilla-jv-10-dev-stage-finetune-tts-all@a19346ca` | `b607116568cfb2e7` | dev fit† | — / **0.2497** |

Dev numbers use the official normalizer through `main.py` in NB 08, except * (our scorer, which
differs by −0.0003). E4 = Jember concat25 + curated Common Voice 6.53 h, 1 epoch. E4-native = same
recipe with native Jember segments and the final-step checkpoint (no dev selection).
† Stage-2 checkpoints were trained on the 372 dev clips themselves, so their dev score is not a result.

## Working conventions

- **Notebooks are authored locally and executed on Kaggle.** No training or ML dependencies on the
  laptop; local checks are static only (`ast.parse`, cross-cell names, unit tests of pure functions).
- **Run outputs:** Kaggle → Output → Download all → unzip into the repo root. The archive already
  contains `findings/<run-id>/`. A run with a different recipe must use its own `RUN_NOTE`, so it
  never overwrites a folder it is compared against.
- **Platform logs:** saved as `submissions/logs/id-<platform id>_<arm>_<smoke|full>.txt`, plus one
  row in `submissions/README.md`.
- **Competition data rule:** only aggregate numbers (WER, counts) were ever shared with AI tools;
  transcripts, clip names and per-clip predictions were not. `main.py` logs nothing about test data.
- The official dev set (4 speakers, 2 conversations) is a weak proxy for test: a 0.034 dev gap between
  E4 and NB04-native shrank to 0.002 on test, and stage-1 changes moved dev and test in opposite
  directions twice.

## For AI agents entering this repo

Read in this order: this file → [`CLAUDE.md`](CLAUDE.md) → [`submissions/README.md`](submissions/README.md)
→ the latest relevant report in `reports/` → `findings/<run-id>/dataset_findings.json` (each run's
JSON digest). Never walk `Datasets/` recursively: it holds tens of thousands of audio files.

## License

Code: [Mozilla Public License 2.0](LICENSE) (the competition rules license publicly shared code under
MPL 2.0). Derived data in `findings/` keeps the licence of its source corpus; see
[`LICENSE-DATA.md`](LICENSE-DATA.md).
