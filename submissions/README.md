---
title: "Ledger Submission — Lost in Transcription"
aliases:
  - Ledger Submission
  - Submissions
tags:
  - index
  - submission
status: active
updated: 2026-09-30
---

# submissions/

Semua run di platform DrivenData, satu baris per ID. Log mentahnya ada di `logs/`,
dengan nama `id-<id platform>_<arm>_<smoke|full>.txt`. Log platform **tidak pernah memuat
skor**; skor dibaca manual dari halaman Submissions atau leaderboard.

- **smoke**: 5 klip yang diambil dari dev. Hanya menguji benar-jalan dan waktu load (limit
  1 menit). Skornya tidak berarti apa-apa: E4 smoke 0,2043 → test 0,3005.
- **full**: 2.118 klip test (limit 2 jam). Memotong kuota **3 per 7 hari per anggota**.

## Ledger

| ID | Waktu mulai (UTC) | Jenis | Arm | Checkpoint + decode | ZIP (entri, byte) | ZIP sha16 | Skor | Log |
|---|---|---|---|---|---|---|---|---|
| 2297 | 2026-09-21 23:10 | smoke | E4 | E4, greedy | 10, 1.621.785.707 | `bdc3408c82e194ba` | 0,2043 (smoke) | [log](logs/id-2297_E4-greedy_smoke.txt) |
| 2507 | 2026-09-24 11:50 | full | E4 | E4, greedy | 10, 1.621.785.707 | `bdc3408c82e194ba` | **0,3005** | [log](logs/id-2507_E4-greedy_full.txt) |
| 2515 | 2026-09-24 15:35 | smoke | B | E4, beam 5 | 10, 1.621.785.965 | `fa4cac28be39199b` | — | [log](logs/id-2515_B-e4beam5_smoke.txt) |
| 2529 | 2026-09-24 16:48 | smoke | A | NB04 native, greedy | 9, 1.621.975.241 | `1c41d4769b0deac1` | — | [log](logs/id-2529_A-nb04native_smoke.txt) |
| 2536 | 2026-09-24 17:13 | full | A | NB04 native, greedy | 9, 1.621.975.241 | `1c41d4769b0deac1` | **0,3027** | [log](logs/id-2536_A-nb04native_full.txt) |
| 2537 | 2026-09-24 17:30 | full | B | E4, beam 5 | 10, 1.621.785.965 | `fa4cac28be39199b` | **0,2950** | [log](logs/id-2537_B-e4beam5_full.txt) |
| 2691 | 2026-09-25 22:12 | smoke | D | E4-native, beam 5 | 8, 1.621.780.627 | `2b21287a0bcef718` | 0,2043 (smoke) | [log](logs/id-2691_D-e4native-beam5_smoke.txt) |
| 2693 | 2026-09-25 22:37 | full | D | E4-native, beam 5 | 8, 1.621.780.627 | `2b21287a0bcef718` | **0,2901** | [log](logs/id-2693_D-e4native-beam5_full.txt) |
| 2912 | 2026-09-28 01:41 | smoke | F | E4-native + tahap 2 dev (NB 10 all), beam 5 | 8, 1.621.780.627 | `8615cbff23e88056` | 0,1043 (smoke; klip smoke ikut dilatih) | [log](logs/id-2912_F-devstage-all-beam5_smoke.txt) |
| 2914 | 2026-09-28 01:56 | full | F | E4-native + tahap 2 dev (NB 10 all), beam 5 | 8, 1.621.780.627 | `8615cbff23e88056` | **0,2660** | [log](logs/id-2914_F-devstage-all-beam5_full.txt) |
| 3023 | 2026-09-29 02:10 | smoke | P | F + tabel rewrite 30 aturan (`postprocess.py`), beam 5 | 8, 1.621.783.064 | `7d3bebb72b598e63` | 0,1043 (smoke; sama dengan F) | [log](logs/id-3023_P-devstage-all-beam5-rewrite_smoke.txt) |
| 3097 | 2026-09-29 16:10 | full | P | F + tabel rewrite 30 aturan (`postprocess.py`), beam 5 | 8, 1.621.783.064 | `7d3bebb72b598e63` | **0,2664** (+0,0004 vs F, seri) | [log](logs/id-3097_P-devstage-all-beam5-rewrite_full.txt) |
| 3158 | 2026-09-30 09:58 | smoke | H | turbo zero-shot + tahap 2 dev (NB 10 t0-all), beam 5 | 13, 1.622.459.569 | `9e586409ed2def98` | 0,1087 (smoke; = referensi lokal 0,108696; klip smoke ikut dilatih) | [log](logs/id-3158_H-t0-all-beam5_smoke.txt) |
| 3159 | 2026-09-30 10:15 | full | H | turbo zero-shot + tahap 2 dev (NB 10 t0-all), beam 5 | 13, 1.622.459.569 | `9e586409ed2def98` | **0,3088** (+0,0428 vs F; convo 2 held-out meramal −0,0124) | [log](logs/id-3159_H-t0-all-beam5_full.txt) |
| 3363 | 2026-10-01 19:02 | smoke | J | stage 1 E4-native 2 epoch (NB 12 r2) + tahap 2 dev (NB 10 2ep-all), beam 5 | 8, 1.621.780.627 | `a964f7c56d291ff8` | 0,0870 (smoke; = referensi lokal 0,086957; klip smoke ikut dilatih) | [log](logs/id-3363_J-2ep-all-beam5_smoke.txt) |
| 3376 | 2026-10-01 22:11 | full | J | stage 1 E4-native 2 epoch (NB 12 r2) + tahap 2 dev (NB 10 2ep-all), beam 5 | 8, 1.621.780.627 | `a964f7c56d291ff8` | **0,2655** (−0,0005 vs F, praktis seri) | [log](logs/id-3376_J-2ep-all-beam5_full.txt) |
| 3463 | 2026-10-02 18:04 | smoke | K | stage 1 E4-native + Podcast Homostoria (NB 13) + tahap 2 dev (NB 10 homo-all), beam 5 | 8, 1.621.780.627 | `38e628e81934e8f5` | 0,1043 (smoke; = referensi lokal 0,104348; klip smoke ikut dilatih) | [log](logs/id-3463_K-homo-all-beam5_smoke.txt) |
| 3473 | 2026-10-02 18:54 | full | K | stage 1 E4-native + Podcast Homostoria (NB 13) + tahap 2 dev (NB 10 homo-all), beam 5 | 8, 1.621.780.627 | `38e628e81934e8f5` | **0,2698** (+0,0043 vs J, +0,0038 vs F; dev stage 1 meramal −0,0221) | [log](logs/id-3473_K-homo-all-beam5_full.txt) |
| 3516 | 2026-10-03 03:02 | full | L | stage 1 E4-native + TTS Central Javanese (NB 14) + tahap 2 dev (NB 10 tts-all), beam 5 | 8, 1.621.780.627 | `6a2080f69477dcb0` | **0,2497** ← terbaik (−0,0158 vs J, −0,0163 vs F; peringkat 25) | [log](logs/id-3516_L-tts-all-beam5_full.txt) |

Ketiga submission penuh tanggal 24 Sep dikirim dari akun `hamzapratama000`.
Akun per submission penuh, dibaca dari halaman Submissions tim (disimpan 30 Sep): 2507/2536/2537
`hamzapratama000`, 2693 dan 2914 `thoriqibrahimfarras`, 3097 `daivafzn`.
**Kuota ternyata per TIM:** halaman itu menulis "Your team has 2 of 3 submissions left per 7 days".
Pada 24 Sep, skor 0,3005 berada di peringkat #58. Pada 27 Sep, skor terbaik 0,2901 (tim **Bulu Hidung**) berada di peringkat **#57**; #1 di 0,2096, #10 di 0,2228.

## Dari notebook mana setiap ZIP berasal

| Arm | Dibangun oleh | Folder findings | Cek di Kaggle |
|---|---|---|---|
| E4 | `notebooks/08-packaging.ipynb`, run 22 Sep | `findings/08-packaging/` | 19/19, prediksi dev identik 372/372 dengan NB 06 |
| A, B (+ kontrol C) | run 24 Sep, `RUN_NOTE="ab"` | `findings/08-packaging-ab/` | 48/48 |
| D (+ kontrol N, C) | run 25 Sep, `RUN_NOTE="e4native"` | `findings/08-packaging-e4native/` | 43/43, paritas N dan C tepat (Δ 0 error) |
| F | run 28 Sep, `RUN_NOTE="devstage"`; checkpoint dari `notebooks/10-dev-stage-finetune.ipynb` (`all`) | `findings/08-packaging-devstage/` | 20/20, paritas vs NB 10 tepat (2.448 error, Δ 0) |
| P | run 29 Sep, `RUN_NOTE="devstage-pp"`; F + tabel rewrite `F` | `findings/08-packaging-devstage-pp/` | 21/21, paritas tepat (2.389 error), transkrip dev = postprocess_P(F) 372/372 |

## Cara membaca hasil sejauh ini

- **Efek beam 5 pindah dari dev ke test hampir persis:** −0,0050 di dev, −0,0055 di test (E4).
- **Keunggulan resep di dev tidak ikut pindah ke test:** E4 unggul 0,034 atas NB04-native di
  dev, tapi hanya 0,002 di test. Karena itu D menguji satu variabel dari E4, yaitu segmen
  Jember native.
- **Segmen Jember native membantu di test (−0,0049), padahal di dev seri:** D 0,2901 vs B 0,2950, sedangkan di dev D 0,2268 vs B 0,2260. Ini arah yang sama dengan selisih panjang klip dev vs test.
- **Fine-tune tahap 2 di dev resmi menurunkan WER test 0,0241** (F 0,2660 vs D 0,2901). Di convo 2 yang
  held-out, NB 10 memperkirakan −0,0267, jadi gainnya pindah ke test hampir utuh. Referensi test
  ternyata memakai konvensi yang sama dengan dev, dan konvensi itulah tuas yang selama ini hilang.
- **Tabel rewrite di atas F tidak membantu di test** (P 0,2664 vs F 0,2660), padahal di convo 2
  held-out analognya −0,0039. Tuas konvensi di level token sudah habis setelah fine-tune tahap 2.
- Tanpa referensi test per klip tidak ada CI di test. Selisih beberapa per seribu bisa noise.

ZIP submission disimpan lokal di `submissions/zips/` (tidak ikut git, ~1,6 GB per ZIP); sha16-nya
ada di tabel di atas.
