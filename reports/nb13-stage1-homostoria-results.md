---
title: "NB 13 — stage 1 E4-native + Podcast Homostoria: hasil"
tags: [report, nb13]
status: active
updated: 2026-10-02
---

# NB 13 — stage 1 E4-native + Podcast Homostoria

Brief: [[nb13-brief-stage1-homostoria]]. Run `13-stage1-homostoria-E4-native-homo`, 2 Okt 2026,
**24/24 cek lolos**, 3,09 jam wall clock, 714 step, final step dikirim.

Checkpoint: `amozaurus/mozilla-jv-13-stage1-homostoria-E4-native-homo@1bbab855c44e1d18aac52f86b50fd74ddc15cf07`,
`model.safetensors` sha16 `dde745d5eff80bd8` (fp32, tata letak transformers 5 seperti D).

## Data yang benar-benar masuk

| sumber | item | jam |
|---|---|---|
| Jember native | 5.541 | 8,36 |
| CV terkurasi (jv-mix-16k E4) | 1.184 | 6,53 |
| **Homostoria** | **4.693** | **7,67** (16 episode) |

16 episode ter-decode = 11,30 jam audio, 0 segmen perlu di-clamp. Angka filter sama persis dengan
uji lokal (dur ≤ 0 −99, > 29 s −240, angka −131).

## Dev resmi (greedy, 372 klip, dihitung lokal, agregat saja)

| pembanding | WER a → NB 13 | Δ | CI95 berpasangan |
|---|---|---|---|
| E4-native, semua 372 | 0,2317 → **0,2096** | **−0,0221** | [−0,0268, −0,0177] |
| E4-native, 222 klip di luar kurva | 0,2295 → 0,2101 | −0,0194 | [−0,0252, −0,0136] |
| E4-native, convo 2 | 0,2312 → 0,2051 | −0,0262 | [−0,0380, −0,0156] |
| E4-native, convo 5 | 0,2319 → 0,2108 | −0,0211 | [−0,0264, −0,0161] |
| NB 12 r2 (2 epoch), semua | 0,2371 → 0,2096 | −0,0274 | [−0,0328, −0,0221] |

Per kelas token (digest): wer_id **0,1754 → 0,1367**, wer_jv 0,2425 → 0,2450 (datar), wer_unk
0,3969 → 0,3831, n_jv_to_id 111 → 143 (prior Indonesia menguat, seperti E3 → E4). Jember dev
folded 0,3632 → 0,3705 (sedikit lebih buruk). Kurva resmi (150 klip) turun sampai step terakhir:
0,2323 → 0,2085.

Ini perbaikan dev terbesar sejak E4 (−0,0244 vs NB 04), dan konsisten di kedua percakapan dan
kedua kelas bahasa. **Tetap bukan keputusan**: H membuktikan dev bisa salah arah untuk perubahan
stage 1, dan sebagian keuntungan ini mungkin konvensi tulisan Indonesia santai yang juga diajarkan
tahap 2. Yang memutuskan: NB 10 `homo-all` → NB 08 → slot test vs F 0,2660 / J 0,2655.

## Tahap 2: NB 10 `homo-all` (2 Okt)

17/17, 63 step, 11,9 menit, resep F persis dengan titik awal checkpoint NB 13. S =
`amozaurus/mozilla-jv-10-dev-stage-finetune-homo-all@f93454bf41d78a393a5bc2a3c6a3fee27ad5ad10`,
sha16 `09ad57361da47cc7`. Fit dev (beam 5, data latih, bukan hasil): 2.449 error = 0,140063
(F 2.448, J 2.454 — tahap 2 menyamakan semuanya di dev), clean-222 0,140914, smoke-5 0,104348.
NB 08 di-patch untuk **arm K** (`RUN_NOTE="homo-all"`, ZIP `submission_K_homo_all_beam5.zip`).

## Packaging: NB 08 arm K (2 Okt)

21/21, **SIAP SUBMIT**. Paritas persis (2.449 error, selisih 0), gladi smoke 0,1043 = referensi.
ZIP `submission_K_homo_all_beam5.zip`: 8 entri, 1,619 GB, sha16 `38e628e81934e8f5` (salinan lokal
user dicek 3 Okt, sha sama).

## Hasil test arm K (2 Okt): **0,2698** — dev salah arah lagi

Smoke 3463 = 0,1043 (= referensi lokal). Full 3473 run normal (2.118 klip, 0 gagal, 0 kosong,
jalur 2051/67/134, 648 s). **Test 0,2698 vs J 0,2655 (+0,0043) dan F 0,2660 (+0,0038).**
Stage 1 NB 13 meramal −0,0221 di dev dengan CI jauh di bawah 0: **arahnya salah**, kali ini ke sisi
optimis (H salah ke sisi pesimis).

Bacaan:
- Selisih +0,004 kecil (satu sampel test, tanpa CI), tapi jelas **bukan** perbaikan. 7,7 jam
  percakapan Indonesia santai dari dua host tidak menambah nilai stage 1 di test.
- Penjelasan paling mungkin untuk dev: keuntungan dev NB 13 sebagian besar ada di **wer_id**
  (0,175 → 0,137), yaitu gaya tulisan Indonesia santai yang juga diajarkan tahap 2 di 372 klip dev.
  Setelah tahap 2, ketiga model (F, J, K) sama di dev (2.448 / 2.454 / 2.449 error), dan sisa
  perbedaannya di test tidak ada yang positif.
- Kemungkinan lain yang tidak bisa dipisahkan dengan satu slot: batas segmen 1 detik memotong
  kata (mengajari model menghapus/menambah kata di tepi), penutur hanya dua, dan prior Indonesia
  menguat (n_jv_to_id 111 → 143) sementara test kemungkinan lebih Jawa daripada dev.
- **Pelajaran yang lebih umum:** dev (4 penutur) gagal menilai perubahan stage 1 ke dua arah
  (H dan K). Tiga eksperimen stage 1 sejak 30 Sep (H, J, K) tidak ada yang mengalahkan F secara
  berarti. Skor terbaik tetap J 0,2655 ≈ F 0,2660.
