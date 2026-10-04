---
title: "Hasil Notebook 11 — large-v3 zero-shot + probe training"
aliases:
  - NB 11 results
tags:
  - report
status: done
updated: 2026-09-30
---

# Hasil NB 11 (30 Sep 2026): large-v3 ditutup, dan turbo zero-shot ternyata dekat dengan D

Run `findings/11-large-v3-probe-zeroshot-feasibility/`, T4, transformers 4.57.6. **17/17 PASS.**
Kontrol D tepat sama dengan NB 08 (3.965 / 799 / 3.166 error, +0), jadi lingkungan decode sama
dengan submission D. Brief: [[nb11-brief-large-v3-probe]].

## Angka (dev resmi 372 klip, `main.py` D, beam 5)

| arm | WER resmi | lower + tanpa tanda baca | convo 2 (lower) | S / D / I |
|---|---|---|---|---|
| D = E4-native (fine-tune) | 0,2268 | 0,2146 | 0,2188 | 2972 / 368 / 625 |
| T0 = turbo zero-shot | 0,2514 | 0,2329 | **0,2058** | 3163 / 885 / 347 |
| L0 = large-v3 zero-shot | 0,2655 | 0,2467 | 0,2151 | 3240 / 1024 / 378 |

**L0 − T0 (pendengaran, 372 klip): +0,0138, CI95 [+0,0050, +0,0221]** → menurut aturan yang
ditetapkan sebelum run: **L0 LEBIH BURUK, large-v3 dihentikan.** Di irisan pendek (paling mirip
test) lebih buruk lagi: +0,0170 [+0,0090, +0,0251].

## Kelayakan (dicatat walau sudah tidak menentukan)

- Full fine-tune large-v3 **OOM di T4 bahkan di micro-batch 1** (puncak 15,1 GB). Hanya varian
  encoder beku yang muat (12,0 GB, ~0,6 jam stage 1 terkalibrasi), dan itu variabel kedua.
- Decode test di A100 diproyeksikan ~2.740 s (4,4× D); load 1,7 s. Inference-nya layak, training penuhnya tidak.
- Kalibrasi probe: turbo sintetis 2,78 s/micro-batch vs 2,27 s nyata (faktor 0,82), puncak 9,45 vs 7,03 GB.

## Temuan yang tidak dicari: stage 1 kita hampir tidak menambah pendengaran

- T0 zero-shot hanya **+0,018** dari D di ruang lower+tanpa tanda baca, padahal D adalah hasil
  stage 1 di Jember + CV. Sebagian dari +0,018 itu pun kemungkinan penghapusan filler/disfluensi
  (T0 menghapus 885 token vs D 368), yang merupakan soal konvensi, dan konvensi sudah diurus tahap 2.
- Di **convo 2** (penutur held-out tahap 2, dan semua klip `ind`), T0 zero-shot **lebih baik** dari
  D: 0,2058 vs 0,2188 (ruang lower+tanpa tanda baca).
- Implikasinya, R3 (stage 1 dua epoch) tidak menjanjikan apa-apa sebelum kita tahu apakah stage 1 berguna sama sekali.

## Langkah berikutnya

NB 10 `RUN_NOTE="t0-c5"`: resep c5 persis, dengan titik awal turbo zero-shot. Pembandingnya S-c5
(0,1980 di convo 2), dihitung lokal. Aturan keputusannya ditulis di sel 1 NB 10 sebelum run.

## Tindak lanjut: NB 10 `t0-c5` (30 Sep) — stage 1 merugikan

`findings/10-dev-stage-finetune-t0-c5/`, 23/23 PASS, kontrol turbo zero-shot = NB 11 persis
(4.395 / 813 / 3.582). Resep c5 persis, titik awal turbo zero-shot. S =
`amozaurus/mozilla-jv-10-dev-stage-finetune-t0-c5@df987380`, sha16 `d42fc295c799a5cf`.

| convo 2 (held-out), beam 5 | error | WER |
|---|---|---|
| S-c5 (E4-native + tahap 2) | 704 / 3556 | 0,1980 |
| **S_T0 (turbo zero-shot + tahap 2)** | **660 / 3556** | **0,1856** |

S_T0 − S-c5 berpasangan (dihitung lokal): **−0,0124 CI95 [−0,0231, −0,0023]**, p 0,991; ruang
lower+tanpa tanda baca −0,0132 [−0,0238, −0,0031]. Kedua penutur −0,012 (CI masing-masing
menyentuh 0), javind −0,0126, ind −0,0116. Aturan yang ditetapkan sebelum run: CI seluruhnya < 0 →
**stage 1 (Jember + CV) merugikan setelah tahap 2** → varian `t0-all` (= resep F, titik awal
turbo) lalu satu slot test melawan F 0,2660. Kurva greedy convo 2: 0,2329 → 0,1918 → 0,2042 →
0,1867 (tidak monoton; tetap step terakhir).

## Hasil test arm H (30 Sep): **0,3088** — convo 2 salah arah

Submission 3159 (smoke 3158), run normal (2.118 klip, 0 gagal, 0 kosong, jalur 2051/67/134).
H = turbo zero-shot + tahap 2 resep F. **Test 0,3088 vs F 0,2660 (+0,0428)**, bahkan lebih buruk
dari D 0,2901 (D tanpa tahap 2 sama sekali). Analog held-out convo 2 meramal −0,0124 dengan CI di
bawah 0: **arah dan besarnya salah.**

Bacaan:
- **Stage 1 (Jember + CV) bernilai besar di test**, minimal ~0,04, walau di dev hampir tidak
  terlihat (T0 zero-shot hanya +0,018 dari D, dan di convo 2 malah lebih baik). Test (2.118 klip,
  banyak penutur) jauh lebih mirip data stage 1 daripada 4 penutur dev. Convo 2 memuat semua klip
  `ind`, tempat turbo zero-shot memang kuat.
- **Dev mengukur konvensi, bukan keluasan pendengaran.** Tahap 2 (konvensi) berpindah ke test
  (−0,027 → −0,024); perubahan stage 1 tidak (E4 vs NB04, sekarang H). Keputusan tentang stage 1
  hanya bisa diambil dari slot test.
- Konsekuensi untuk NB 11: verdict "large-v3 lebih buruk" juga diukur di 4 penutur dev, jadi tidak
  lagi dianggap kuat. large-v3 tetap tertutup karena alasan praktis (full FT OOM di T4).
- **F tetap terbaik.** Arah ke depan: base E4-native; tuas yang layak adalah yang memperkuat stage 1
  (lebih banyak data/epoch), dinilai hanya lewat test.

## Hasil test arm J (1 Okt): **0,2655**, praktis seri dengan F

J = stage 1 E4-native **2 epoch** (NB 12 r2, `5cba4549f1b7f57e`) + tahap 2 resep F (NB 10 `2ep-all`,
`6680ef3cc3dab73e`) + beam 5, ZIP `a964f7c56d291ff8`. Smoke 3363 = 0,0870 (sama persis dengan referensi
lokal), full 3376 run normal (2.118 klip, 0 gagal, 0 kosong, jalur 2051/67/134, 676 s).
**Test 0,2655 vs F 0,2660 (−0,0005)**: skor terbaik tim secara angka, tapi selisihnya jauh di bawah
derau satu submission. Epoch kedua stage 1 tidak memberi apa-apa yang terlihat.

Bacaan:
- Stage 1 bernilai ~0,04 kalau dibuang (H), tapi **menambah epoch pada data yang sama tidak
  menambah**. Yang dibeli stage 1 adalah keluasan data, bukan lamanya latihan. Tuas berikutnya yang
  masuk akal adalah data stage 1 baru yang lisensinya bebas, bukan epoch.
- Jarak ke #1 (0,2076) tetap ~0,058. Tidak ada satu pun eksperimen dari NB 09–12 yang mendekati.
