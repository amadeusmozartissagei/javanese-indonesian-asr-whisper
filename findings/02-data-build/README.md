# jember-segments-16k

A derivative of the **Jember Javanese Spontaneous Speech Corpus**, prepared for the
Mozilla *Lost in Transcription* Indonesian–Javanese ASR track. Built by
`notebooks/02-data-build.ipynb` and verified from a fresh kernel by
`notebooks/02-verify.ipynb`.

**Licence: CC-BY-NC-SA-4.0, the same as the source.** See `LICENSE.txt` for attribution
and terms, including the one file that is *not* covered by it.

## What this is

The same 208 recordings as the source corpus, re-encoded, plus the segment table and
evaluation harness that every later notebook in the project depends on.

The name says "segments" but the audio is **one FLAC per whole recording**, not one file
per segment. Segments are addressed by sample offset in `manifest.csv`:

```python
y, sr = sf.read(ROOT / r.path, start=r.start_sample, stop=r.end_sample, dtype="float32")
```

6,638 loose clips would be a bad way to ship ten hours of audio — Kaggle's dataset builder
truncated exactly that attempt at 500 files, and thousands of small files make every mount
slow even where it works.

## Contents

| file | what it holds |
|---|---|
| `recordings/*.flac` | 208 files, 16 kHz mono, one per recording |
| `manifest.csv` | 6,638 segments: sample offsets, three text variants, per-word origin counts, split |
| `split.csv` | the frozen split — train 5,541 / dev 1,097 segments |
| `dropped_segments.csv` | the 41 segments removed, each with its reason |
| `lexicon_v1.csv` | word → origin (`jv` / `id` / `both` / `unk`), 23,805 entries |
| `scorer.py` | the evaluation harness (original code, see `LICENSE.txt`) |
| `text_audit.json`, `dataset_findings.json` | measurements from the build |

## Changes made to the source material

* **Audio:** mp3 (44.1/48 kHz) decoded and re-encoded as 16 kHz mono FLAC. No trimming,
  no gain change, no denoising — the sample content is the source content, resampled.
* **Segments:** the source TSV carries `H:MM:SS` bounds at one-second precision. Bounds
  that a neighbouring row proved to be typos were repaired; 41 rows that could not be
  repaired were dropped and are listed in `dropped_segments.csv`. 6,679 rows → 6,638
  segments.
* **Text:** kept verbatim as `text_raw`, plus two derived columns — `text_official`
  (the competition's published pre-scoring normalizer) and `text_folded` (that, with
  diacritics folded). No wording was edited.
* **Split:** grouped by recording so no voice appears on both sides, stratified on
  Javanese-ratio × duration, seeded. Frozen: a different split must be a new file.
* **Origin tagging:** each word labelled `jv` / `id` / `both` / `unk` by attestation in
  two other corpora plus a marker list of high-frequency Javanese function words.

Nothing in the source corpus was removed for any reason other than an unrepairable
timestamp, and nothing was added to it.
