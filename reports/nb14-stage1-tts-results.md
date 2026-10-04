---
title: "NB 14 — stage 1 E4-native + TTS Central Javanese: hasil"
tags: [report, nb14]
status: active
updated: 2026-10-03
---

# NB 14 — stage 1 E4-native + TTS Central Javanese

Brief: [[nb14-brief-stage1-tts]]. Run `14-stage1-tts-E4-native-tts`, 3 Okt 2026, **23/23 cek lolos**,
2,22 jam, 506 step, final step dikirim. Checkpoint:
`amozaurus/mozilla-jv-14-stage1-tts-E4-native-tts@e892b99c36147ef13addc3ae1efe2ca239f2f63a`,
`model.safetensors` sha16 `b494633b0708e5f9`.

Komposisi: Jember native 5.541 item / 8,36 jam + CV E4 1.184 / 6,53 jam + **TTS E1 1.368 / 8,02 jam**.

## Dev resmi (greedy, 372 klip, berpasangan, dihitung lokal)

| pembanding | WER → NB 14 | Δ | CI95 |
|---|---|---|---|
| E4-native, semua | 0,2317 → 0,2339 | +0,0022 | [−0,0025, +0,0066] (seri) |
| E4-native, 222 di luar kurva | 0,2295 → 0,2331 | +0,0035 | [−0,0027, +0,0096] |
| E4-native, convo 2 | 0,2312 → 0,2461 | +0,0149 | [+0,0029, +0,0261] |
| E4-native, convo 5 | 0,2319 → 0,2308 | −0,0011 | [−0,0061, +0,0040] |
| NB 13 (Homostoria), semua | 0,2096 → 0,2339 | +0,0243 | [+0,0184, +0,0301] |

Per kelas: **wer_jv 0,2425 → 0,2065** (sisi Jawa terbaik di proyek), wer_id 0,1754 → 0,1934,
wer_unk 0,3969 → 0,4136, n_jv_to_id 111 → **91**. Jember dev folded 0,3632 → 0,3645. Profilnya
**kebalikan K**: K memperbaiki Indonesia dan memburuk di test. Convo 2 (memuat semua klip `ind`)
lebih buruk, konsisten dengan sisi Indonesia yang melemah.

Dev total seri, jadi tidak ada ramalan. Jalur: NB 10 `tts-all` (di-patch 3 Okt, BASE E4NT) →
NB 08 arm L → slot test vs J 0,2655 / F 0,2660.

## Tahap 2: NB 10 `tts-all` (3 Okt)

17/17, 63 step, 12,1 menit, resep F persis dengan titik awal checkpoint NB 14. S =
`amozaurus/mozilla-jv-10-dev-stage-finetune-tts-all@a19346cac56f3b8691b4e4bd233e681a819746db`,
sha16 `b607116568cfb2e7`. Fit dev (beam 5, data latih, bukan hasil): **2.402 error = 0,137375**
(F 2.448, J 2.454, K 2.449 — pertama kali tahap 2 mendarat lebih rendah, −46 error), clean-222
0,138902, smoke-5 0,091304. NB 08 di-patch untuk **arm L** (`RUN_NOTE="tts-all"`, ZIP
`submission_L_tts_all_beam5.zip`).

## Packaging: NB 08 arm L (3 Okt)

21/21, **SIAP SUBMIT**. Paritas persis (2.402 error, selisih 0), gladi smoke 0,0913 = referensi.
ZIP `submission_L_tts_all_beam5.zip`: 8 entri, 1,619 GB, sha16 `6a2080f69477dcb0` (salinan lokal
user dicek, sha sama).

## Hasil test arm L (3 Okt): **0,2497** — terbaik, peringkat 25

Full 3516, run normal (2.118 klip, 0 gagal, 0 kosong, jalur 2051/67/134, 635 s). ZIP sama dengan
yang dicek (8 entri, 1.621.780.627 byte). **Test 0,2497 vs J 0,2655 (−0,0158) dan F 0,2660
(−0,0163).** Peringkat akhir tim: 25. Kompetisi ditutup setelah submission ini.

Bacaan:
- Dev stage 1 menyebut seri (+0,0022, CI melewati 0); test memberi perbaikan terbesar sejak F.
  Dev ketiga kalinya tidak bisa membaca perubahan stage 1 (H pesimis, K optimis, L buta).
- Satu-satunya sinyal dev yang searah dengan test adalah **profil per bahasa**: L memperkuat sisi
  Jawa (wer_jv 0,2425 → 0,2065, salah-ubah Jawa→Indonesia 111 → 91) dan K memperkuat sisi
  Indonesia (wer_id 0,1754 → 0,1367, Jawa→Indonesia 111 → 143). Test menghargai L dan menghukum K,
  jadi test kemungkinan **lebih Jawa daripada dev**.
- Yang dibeli stage 1 adalah **data berbahasa Jawa**, bukan epoch (J) dan bukan percakapan
  Indonesia (K). TTS Central Javanese dulu dibatalkan di NB 06 hanya karena alasan dev.
