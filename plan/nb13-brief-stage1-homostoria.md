---
title: "NB 13 brief — stage 1 E4-native + Podcast Homostoria"
tags: [brief, nb13]
status: built
updated: 2026-10-02
---

# NB 13 — stage 1 E4-native + Podcast Homostoria

**Pertanyaan.** H (tanpa stage 1) = 0,3088 dan J (stage 1 2 epoch) = 0,2655 vs F 0,2660. Stage 1
bernilai ~0,04 di test, tapi epoch tambahan pada data yang sama tidak menambah. Apakah **data baru**
(percakapan Indonesia spontan) menambah nilai itu?

**Satu variabel vs E4-native:** tambah segmen Podcast Homostoria. Sisanya resep E4-native persis
(Jember native + CV terkurasi E4, 1 epoch, LR 6e-6, batch efektif 16, final step, seed 20260829).

## Data

- MDC `cmiepnyu1001jo207hzslvb5m`, CC-BY-SA-4.0, tombol Download (bukan Request Access), diunduh
  2 Okt 2026 → `Datasets/homostoria/`, diunggah user sebagai dataset Kaggle private.
- 16 mp3 64 kbps = 11,30 jam; `transcript_homostoria.tsv` (`Audio file`, `Start`, `End`, `Text`),
  5.163 baris, timestamp resolusi 1 detik, menutup seluruh audio tanpa celah.
- Bahasa Indonesia santai + Inggris; bahasa Jawa praktis nol walau deskripsinya menyebut Jawa.
- Penutur sedikit (host podcast).

## Filter (diuji lokal terhadap TSV asli + `scorer.py` lokal)

| | segmen |
|---|---|
| baris TSV | 5.163 |
| durasi ≤ 0 | −99 |
| > 29 s | −240 |
| memuat angka | −131 |
| **dipakai** | **4.693 (7,67 jam, 16 episode)** |

Target = `fold_diacritics(official_normalize(Text))`, sama dengan `text_folded` jv-mix-16k.
Total item 5.541 + 1.184 + 4.693 = 11.418 → **714 step** (E4-native 421). Proyeksi ~3,5–4 jam T4.

## Risiko

Timestamp 1 detik → ujung segmen bisa memotong kata. Tidak ada pad (segmen bersambung). Penutur
sedikit. Kalau kalah di test, dua hal ini tersangka pertama.

## Jalur keputusan

NB 13 → NB 10 `all` (BASE = checkpoint NB 13, `RUN_NOTE` baru) → NB 08 arm baru → slot test vs
F 0,2660 / J 0,2655. Dev hanya observasi (pelajaran H).
