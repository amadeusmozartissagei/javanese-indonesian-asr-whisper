---
title: "Evaluasi Gap #1 — Konvensi Referensi vs Pendengaran"
aliases:
  - Evaluasi Gap 1
  - Gap konvensi referensi
tags:
  - research
  - competition
  - asr
  - error-analysis
  - gap-eval
status: final
created: 2026-09-27
updated: 2026-09-27
---

# Evaluasi gap #1: berapa banyak error kita yang sebenarnya konvensi referensi?

**Konteks.** Skor test terbaik kita 0,2901 (D, rank #57), sedangkan #1 di 0,2096. Gap-nya
~0,08. Pertanyaannya: berapa bagian error kita yang berasal dari konvensi penulisan
referensi (kapital, tanda baca, filler, ejaan varian, pemisahan kata), dan berapa yang
memang salah dengar? Semua angka di sini dihitung di dev resmi (372 klip, 17.485 token),
**hanya agregat**, dengan normalizer resmi (`score.py`). Skrip ada di scratchpad sesi
(`gap1_convention.py`, `gap1_rewrite_cv.py`) dan hanya mencetak hitungan.

## 1. Dekomposisi error D (dev 0,2268, 3.965 error)

| Bucket | Error | Poin WER | Sifat |
|---|---:|---:|---|
| Kapital saja | 95 | 0,0054 | konvensi |
| Tanda baca / elipsis / hubung | 158 | 0,0090 | konvensi |
| Angka di hipotesis | 10 | 0,0006 | konvensi |
| Filler (S 67 + I 138 + D 3) | 208 | 0,0119 | konvensi |
| Pemisahan/penggabungan kata | 104 | 0,0059 | konvensi |
| Ejaan varian, fold ringan (aksen, huruf ganda, dh/th) | 87 | 0,0050 | konvensi |
| Ejaan varian, fold berat (ng-/m- awal, -h/-k akhir, a~o, h antarvokal) | 452 | 0,0259 | **campuran** |
| Beda 1 huruf (≥4 huruf) | 448 | 0,0256 | campuran |
| Substitusi lain | 1.551 | 0,0887 | pendengaran/leksikal |
| Deletion lain | 365 | 0,0209 | pendengaran |
| Insertion lain | 487 | 0,0279 | pendengaran/halusinasi |

B (E4 beam5) memberi pola yang sama dengan selisih beberapa error per bucket.

**Oracle ladder** (fold yang sama dipasang ke referensi *dan* hipotesis): L1 lowercase −98 →
L2 +tanda baca −268 → L3 +buang filler −454 → L4 +fold ringan **−547 (WER 0,1969)** →
L5 +fold berat −1.033 (0,1689). **L5 tidak kredibel**: di kosakata referensi sendiri, fold
berat menggabungkan kata yang berbeda pada 19,7 % token. Fold ringan hanya 2,7 %.
CER (tanpa tanda baca, lowercase) 0,077.

**Batas atas konvensi yang kredibel ≈ 0,038** (kosmetik + filler + segmentasi + fold
ringan), dan paling banyak ~0,06 kalau sebagian besar varian berat ikut dihitung. Gap ke
#1 di test 0,08. Konvensi saja tidak menutup gap, bahkan dengan batas atas yang longgar.
**Sekitar 0,14 dari 0,23 adalah pendengaran/leksikal**.

## 2. Model menyalin konvensi data latih

- Dari 539 substitusi ejaan varian, **355 (66 %) memakai bentuk yang lebih sering muncul
  di teks latih E4** (Jember train + CV E4, 88.682 token / 10.574 tipe) daripada bentuk di
  referensi. Hanya 135 (25 %) yang ejaan referensinya tidak pernah muncul di teks latih.
  Jadi model bukan tidak tahu ejaannya. Ia memilih konvensi Jember/CV.
- **OOV.** 13,0 % token referensi tidak ada di teks latih. Error rate-nya 0,419, dan
  token ini menyumbang 28,5 % error S+D. Token in-vocab error rate-nya 0,157 dan
  menyumbang **71,5 %** error S+D. Bagian terbesar error ada di kata yang *sudah dikenal*.

## 3. Berapa yang benar-benar bisa ditarik oleh post-processing?

Estimasi jujur: aturan dipelajari di satu percakapan dev, lalu diuji di percakapan
lainnya (convo 5: 294 klip, convo 2: 78 klip). Bootstrap berpasangan per klip, 5.000×.

| Aturan (D) | Δ WER dev | CI 95 % | Klip lebih baik / lebih buruk |
|---|---:|---|---|
| Buang semua token filler dari hipotesis (tanpa belajar) | **−0,0051** | [−0,0073, −0,0030] | 105 / 44 |
| + tabel rewrite kosmetik/varian lintas-percakapan | **−0,0110** | [−0,0140, −0,0080] | 171 / 66 |
| (in-sample, optimistis, tabel semua substitusi) | −0,0296 | — | — |

Untuk B hasilnya sama: −0,0046 dan −0,0112. Per arah: tabel yang dipelajari dari 294 klip
dan diuji di 78 klip memberi −0,023 (82 error), sedangkan arah sebaliknya (belajar dari 78
klip) memberi −0,008. **Tabel membaik dengan data belajar yang lebih banyak.** Tabel yang
dipelajari dari seluruh 372 klip kemungkinan bernilai ~0,01–0,02 di data mirip-dev.

## Kesimpulan

1. **Konvensi itu nyata tapi bukan penyebab utama gap.** Batas atas kredibelnya ~0,04 dari
   gap 0,08. Yang bisa ditarik lewat post-processing ≈ 0,01 di dev. Karena kebiasaan ejaan
   model ~66 % mengikuti data latih, model yang dilatih dengan konvensi referensi (atau model
   yang *menghasilkan* referensi, omniASR_LLM_3B) mendapatkan bagian ini gratis.
2. **Mayoritas error adalah pendengaran pada kata yang sudah dikenal** (in-vocab 71,5 % dari
   S+D; bucket "lain" ~0,14 WER). Ini tuas model/akustik, jadi lead #2 (pilihan model) adalah
   tuas terbesar yang tersisa.
3. **NB 07-lite layak dibangun, murah, tanpa GPU training**: aturan buang-filler ditambah
   tabel rewrite yang dipelajari dari dev, masuk ke `postprocess.py` (`RULES`), satu-satunya
   knob yang tidak menyentuh paritas `main.py`. Perkiraan −0,005 sampai −0,015 di test.
   Dev proxy lemah, dan belum pasti referensi test memakai pipeline yang sama. Catatan:
   tabel dari dev berarti dev ikut "melatih" sistem. Aturan kompetisi tidak melarangnya (R9
   hanya soal test), tapi setelah itu dev bukan validasi yang bersih untuk post-processing.

## Keterbatasan

- Bucket "fold berat" dan "beda 1 huruf" mencampur varian ejaan dengan salah dengar sungguhan.
- Dev hanya 4 penutur / 2 percakapan. Cross-validation lintas percakapan adalah satu-satunya
  held-out yang ada, dan satu sisinya kecil (78 klip).
- Tidak ada cara mengukur apakah konvensi referensi test sama dengan dev.

Berikutnya: lead #2, pilihan model (omniASR / model lain, aturan, lisensi, muat di runtime).
Error NB 04 yang dikutip di brief NB 07 (~250 error bisa ditarik) konsisten dengan angka
in-sample di atas. Lihat [[nb07-brief-error-analysis-robustness]].
