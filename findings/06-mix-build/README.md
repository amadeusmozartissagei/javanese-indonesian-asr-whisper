# jv-mix-16k

Read-speech audio prepared for the Mozilla *Lost in Transcription* Indonesian-Javanese
track. Built by `notebooks/06-mix-build.ipynb`; see LICENSE.txt for sources and terms.

## What this is
16 kHz mono FLAC shards of about ten minutes each, plus `shards/_meta/` holding a
clip-level and an item-level offset table. Individual clips are NOT stored as files:
they are addressed by sample offset inside a shard, because tens of thousands of loose
files are slow to mount and do not survive Kaggle's dataset builder.

## Changes made to the source material
  * decoded to 16 kHz mono and re-encoded as FLAC (originals: WebM/Opus and mp3)
  * clips concatenated into ~25 s training items, never crossing a speaker or a folder,
    with 0.30 s of silence between clips and 0.50 s between items
  * transcripts normalised with the competition's pre-scoring normalizer and folded to
    the diacritic-free space the official reference uses
  * clips removed: down-voted, duplicate-sentence, over the per-speaker cap, containing
    a numeral, or shorter than 2 words
No transcript wording was edited beyond that normalisation, and no audio was altered
beyond resampling, channel mixing and concatenation.

## Contents
  shards/*.flac            the audio
  shards/_meta/clips.csv   one row per source clip, with its offsets
  shards/_meta/items.csv   training items
  shards/_meta/shards.csv  shard lengths
  mix_manifest_<E>.csv     the items each experiment adds
  mix_spec_<E>.json        each experiment's composition, reproducible
