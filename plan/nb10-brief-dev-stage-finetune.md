---
title: "Brief Notebook 10 — Fine-tune tahap 2 di dev resmi"
aliases:
  - Brief Notebook 10
tags:
  - brief
  - notebook
notebook_id: "10-dev-stage-finetune"
lane: "A — Whisper"
accelerator: "T4"
target: 2026-09-29
depends_on: "E4-native (NB 06), main.py D (NB 08)"
status: dibangun-belum-jalan
---

# Brief Notebook 10 — Fine-tune tahap 2 di dev resmi

**Pertanyaan.** Kalau D (E4-native, test 0,2901) dilatih sebentar lagi pada dev resmi, yang
ditulis dalam konvensi referensi, apakah WER turun pada penutur yang tidak ikut dilatih?
Latar belakangnya: [[gap-eval-1-reference-convention-2026-09-27]] menemukan 66 % error
varian ejaan mengikuti ejaan data latih kita.

**Membalik keputusan 28 Agu** ("dev tidak pernah untuk latih", [[official-dev-set-analysis-2026-08-28]]).
Dibolehkan aturan (R9 hanya soal test). Dibalik atas konfirmasi user 28 Sep.

## Desain (satu variabel vs D)

- Titik awal `amozaurus/mozilla-jv-06-data-mixing-E4-native@3437f442`, sha16 `b3438f32cf61ebbe`.
- Latih di **convo 5** (294 klip, 2 penutur). Klip > 30 s **dibuang** (24 klip, ~10 % audio):
  memotong audio tapi tetap memakai transkrip utuh mengajari halusinasi, dan membelah butuh
  timestamp kata yang tidak ada. Tersisa 270 klip, 17 step/epoch.
- Target: kolom `transcript` apa adanya. Dev tidak punya tag kurung, angka, atau em-dash;
  token mentah 17.495 vs 17.485 setelah normalizer, jadi tidak perlu dibersihkan.
- 3 epoch (51 step), LR 3e-6, warmup 10 %, linear, adafactor, batch efektif 16, SpecAugment.
  Step terakhir dikirim.
- Uji di **convo 2** (78 klip, 2 penutur lain, 20 `ind` + 58 `javind`, 3.556 token) lewat
  `main.py` D byte demi byte (sha `aa5a691f68011b81`), beam 5. D di-decode ulang di sesi yang
  sama sebagai kontrol; D di convo 2 menurut NB 08 = 799 error (0,2247).
- Verdict ditetapkan sebelum run: **JELAS LEBIH BAIK** kalau CI95 bootstrap per klip S − D
  seluruhnya < 0. Hanya dengan verdict itu varian `RUN_NOTE="all"` (372 klip) dibangun, lalu
  masuk NB 08 dan satu slot test.

## Lingkungan

Seluruh notebook jalan di `transformers<5` (versi container), jadi evaluasinya sama dengan
`main.py`. Tahap 1 dilatih di 5.0.0; itu satu-satunya perbedaan di luar data, dan kontrol D
menutupnya. Checkpoint S = file non-bobot D byte demi byte + `model.safetensors` baru, jadi
NB 08 memaketkannya lewat jalur muat yang sudah terbukti di container.

## Cek lokal yang sudah dilakukan (28 Sep)

Semua sel ter-parse, tidak ada nama lintas sel yang tak terdefinisi, `main.py` dan
`postprocess.py` identik dengan milik D. Sel 6 (split) dan sel 11 (skor + verdict) diuji
dengan prediksi D dan N tersimpan: kontrol D mereproduksi 3.965 / 799 / 3.166 error persis.
