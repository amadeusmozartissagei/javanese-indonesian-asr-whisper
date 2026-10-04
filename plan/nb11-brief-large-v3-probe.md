---
title: "Brief Notebook 11 — large-v3: zero-shot di dev + probe training di T4"
aliases:
  - NB 11 brief
tags:
  - plan
  - brief
status: active
updated: 2026-09-30
---

# Brief NB 11 — large-v3 go/no-go

Langkah 1 dari rencana 30 Sep ([[next-steps-2026-09-30]]). Satu run Kaggle, tanpa training
dan tanpa push. Tujuannya memutuskan apakah stage 1 large-v3 (6–8 jam GPU) layak dijalankan.

## Kenapa large-v3

- Error F terbesar ada di bucket pendengaran/leksikal (~0,14 dari WER dev D, evaluasi gap #1).
  Tuas konvensi sudah habis (P 0,2664 vs F 0,2660).
- Semua model kita berawal dari turbo (decoder 4 layer). `whisper-large-v3` punya decoder 32
  layer dan belum pernah diukur di proyek ini (NB 03 hanya tiny–medium dan turbo).
- Aturan: model pretrained boleh asal bobotnya publik, gratis, dan lisensinya mengizinkan
  (MIT). Statusnya sama dengan turbo.

## Desain

| arm | model | peran |
|---|---|---|
| D | E4-native @ `3437f442` | kontrol paritas: harus 3.965 error (NB 08) |
| T0 | `openai/whisper-large-v3-turbo` zero-shot | pembanding |
| L0 | `openai/whisper-large-v3` zero-shot | kandidat |

- Decode: `main.py` D byte demi byte (sha `aa5a691f68011b81`, beam 5), 372 klip dev.
- Pembanding utama: L0 − T0 berpasangan di ruang lower + tanpa tanda baca (pendengaran),
  bootstrap per klip. Ruang resmi, irisan pendek/panjang, dan per convo ikut dilaporkan.
- Probe training sintetis: adafactor, fp16, gradient checkpointing, SpecAugment; full
  fine-tune di micro-batch 4 → 2 → 1, lalu encoder beku di 4. Turbo diprobe sebagai kalibrasi
  terhadap angka nyata NB 06 (2,27 s per micro-batch 4, 7,03 GB).

## Aturan keputusan (ditetapkan sebelum run)

- **L0 LEBIH BAIK** (CI95 seluruhnya < 0) + ada config full yang muat ≤ 14,5 GB dengan proyeksi
  stage 1 ≤ 9 jam → siapkan stage 1 large-v3 (resep E4-native, `RUN_NOTE` sendiri, bisa resume),
  lalu NB 10 c5 → convo 2 vs S-c5 0,1980.
- **SERI** → diputuskan bersama user.
- **L0 LEBIH BURUK** → large-v3 ditutup; sisa jalur turbo 2 epoch.
- Kelayakan inference: proyeksi decode test A100 ≤ 3.600 s, load ≤ 20 s.

## Keterbatasan yang sudah diketahui

- Zero-shot bukan fine-tune: selisih zero-shot hanya indikasi seberapa baik model mendengar,
  bukan ramalan hasil fine-tune.
- Proyeksi waktu test memakai rasio waktu T4 terhadap D, dan dev punya lebih banyak klip
  panjang (12 %) daripada test (3 %).
- Probe memakai audio acak dan label tetap 128 token, sehingga angkanya hanya proyeksi kasar.
  Karena itu probe dikalibrasi terhadap turbo.

## Output

`findings/11-large-v3-probe-zeroshot-feasibility/`: `dataset_findings.json`, `run-log.txt`,
`submission_dev_{D,T0,L0}.csv` (dianalisis lokal, agregat saja).
