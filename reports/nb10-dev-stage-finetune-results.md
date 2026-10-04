---
title: "Hasil Notebook 10 — fine-tune tahap 2 di dev (c5)"
aliases:
  - Hasil NB 10
tags:
  - report
  - notebook
notebook_id: "10-dev-stage-finetune"
status: selesai
updated: 2026-09-28
---

# Hasil Notebook 10 — fine-tune tahap 2 di dev (latih convo 5, uji convo 2)

Brief: [[nb10-brief-dev-stage-finetune]]. Output: `findings/10-dev-stage-finetune-c5/`.
Checkpoint S: `amozaurus/mozilla-jv-10-dev-stage-finetune-c5@f7db407f`, `model.safetensors`
sha16 `10dbd350fac7465b`.

> [!summary] Verdict: JELAS LEBIH BAIK (aturan ditetapkan sebelum run)
> Di convo 2 (78 klip, 2 penutur yang tidak ikut dilatih), S − D = **−0,0267, CI95 [−0,0390, −0,0142]**,
> p(S lebih baik) 1,000. WER 0,2247 → **0,1980** (799 → 704 error). 23/23 check PASS.

## Keabsahan

- Kontrol D lewat `main.py` yang sama (sha `aa5a691f68011b81`) menyamai NB 08 **persis**:
  3.965 / 799 / 3.166 error (semua / convo 2 / convo 5). Jadi lingkungan decode di sini sama
  dengan submission D, dan S − D hanya datang dari bobot.
- Jalur decode S = D (328 pendek / 44 chunk / 88 jendela), tanpa transkrip kosong, log 4 baris.
- Latih dan uji tidak berbagi klip maupun penutur. 24 klip > 30 s dibuang, 270 dipakai.
- Training: 51 step, 11,4 menit di T4, loss 0,86 → 0,39. Bobot bergeser 0,056 % relatif
  (decoder 0,19 %, encoder 0,035 %). Perubahannya kecil dan terutama di sisi "bahasa".

## Rincian di convo 2 (held-out)

| subset | klip | S − D | CI95 |
|---|---|---|---|
| semua | 78 | −0,0267 | [−0,0390, −0,0142] |
| huruf kecil + tanpa tanda baca | 78 | −0,0267 | [−0,0385, −0,0148] |
| `javind` | 58 | −0,0304 | [−0,0445, −0,0160] |
| `ind` | 20 | −0,0151 | [−0,0363, +0,0078] |
| penutur #1 | 44 | −0,0325 | [−0,0492, −0,0153] |
| penutur #2 | 34 | −0,0209 | [−0,0391, −0,0030] |

- **Gainnya bukan kosmetik:** selisihnya sama persis di ruang huruf-kecil-tanpa-tanda-baca.
- **Asalnya dari substitusi.** Substitusi turun 656 → 537 (−119), deletion 56 → 51, dan
  **insertion naik 87 → 116** (+29). Rasio panjang hyp/ref 1,009 → 1,018. S sedikit lebih
  "cerewet" di penutur baru, sementara di convo latih insertion justru turun (538 → 338).
- Kedua penutur uji membaik. Klip `ind` (bahasa yang tidak ada di data latih) tidak memburuk.
- Tidak ada satu pun dari 78 transkrip S yang identik dengan D.

## Kurva greedy di convo 2 (observasi, bukan seleksi)

| epoch | step | WER greedy |
|---|---|---|
| 0 (= D) | 0 | 0,2317 |
| 1 | 17 | 0,2061 |
| 2 | 34 | 0,2002 |
| 3 | 51 | 0,2008 |

Sebagian besar gain datang di epoch 1, lalu mendatar di epoch 2–3. Tidak ada tanda kerusakan
di epoch 3, jadi resep yang sama (3 epoch) dipakai untuk varian `all`. Tidak disetel ulang dari
kurva ini, supaya convo 2 tidak ikut memilih hyperparameter.

## Fit data latih (bukan hasil)

Di convo 5: D 0,2273 → S 0,1413 (−0,086). Selisihnya jauh lebih besar daripada di convo 2,
jadi model sebagian menghafal penuturnya. Gain yang berlaku umum adalah angka held-out (−0,027).

## Batasan

- Convo 2 hanya 2 penutur. CI per klip meremehkan variasi antar penutur. Test punya jauh
  lebih banyak penutur, dan dev sudah dua kali terbukti proxy yang lemah untuk test.
- Mekanismenya (konvensi referensi) hanya berpindah ke test **kalau referensi test dibuat dengan
  pipeline yang sama** (omniASR + edit manual). Penyelenggara tidak pernah menjawab ini.
- Insertion yang naik perlu dilihat di test: klip test lebih pendek, dan halusinasi kecil punya
  bobot lebih besar di klip pendek.

## Langkah berikutnya

Varian `RUN_NOTE="all"`: latih di 372 klip (335 setelah membuang > 30 s, 21 step/epoch = 63
step), resep sama, tanpa evaluasi held-out. Setelah itu NB 08 (entri CHECKPOINTS + arm beam 5) dan
slot test melawan D **0,2901**. Checkpoint c5 sudah ada di HF dan bisa dipakai sebagai cadangan.

## Varian `all` (28 Sep)

`findings/10-dev-stage-finetune-all/`, 17/17 PASS. Latih 335 klip (37 > 30 s dibuang), 63 step,
12,1 menit, loss 0,91 → 0,35. Checkpoint `amozaurus/mozilla-jv-10-dev-stage-finetune-all@e4df20fb`,
sha16 `058f6d26fd621170`. WER dev lewat `main.py` beam 5 = 0,1400 (2.448 error): **fit data latih,
bukan hasil**. Cek kewajaran: di convo 5 (dilatih di kedua varian) `all` 1.949 vs `c5` 1.968 error.
Dipaketkan di NB 08 sebagai arm F, dengan paritas terhadap angka NB 10 ini.

## Hasil test (28 Sep)

> [!summary] F (varian `all`, beam 5) = **0,2660** di test, submission `2914`
> D 0,2901 → F 0,2660: **−0,0241**. Held-out convo 2 memperkirakan −0,0267. Untuk pertama kalinya
> angka dev (yang held-out) meramal test dengan baik, karena yang diuji adalah konvensi referensi,
> bukan penutur atau panjang klip.

Full run: 2.118 klip, 0 gagal, 0 kosong, 673,9 s (D 619,9 s), jalur decode 2051 / 67 / 134 sama
dengan semua run sebelumnya. Smoke `2912`: 0,1043 (klip smoke ikut dilatih, tidak berarti).

## Post-processing di atas F: masih layak? (28 Sep, lokal, agregat saja)

Held-out yang jujur: convo 2, prediksi c5 (tidak pernah melihat convo 2). Tabel rewrite untuk F
hanya bisa dipelajari dari prediksi F di dev, yang sudah jadi data latihnya. Padanannya di c5:
belajar dari prediksi c5 di convo 5 (data latihnya), uji di convo 2. Metode tabel sama dengan
[[gap-eval-1-reference-convention-2026-09-27]]; bootstrap per klip 5.000×. Skrip: scratchpad sesi
(`pp_f.py`, `pp_f2.py`).

| di convo 2 (held-out) | D (0,2247) | S c5 (0,1980) |
|---|---:|---:|
| buang semua filler dari hipotesis | +0,0003 | **+0,0011** (merugikan) |
| tabel kosmetik+varian dari prediksi D di convo 5 (36 aturan) | **−0,0233** [−0,0296, −0,0173] | −0,0017 [−0,0049, +0,0012] |
| tabel kosmetik+varian dari prediksi S di convo 5 (22 aturan, min 2) | −0,0031 | **−0,0039** [−0,0071, −0,0014], 10/1 klip |
| tabel yang sama, min 3 (6 aturan) / min 4 (2 aturan) | — | −0,0017 / −0,0014 |
| tabel semua substitusi dari prediksi D di convo 5 | −0,0194 | +0,0039 (merugikan) |

**Bacaan.**
- Tabel rewrite yang dipelajari dari D bernilai −0,023 di D, hampir sama dengan gain test F
  (−0,024). **Fine-tune tahap 2 sudah menyerap hampir seluruh tuas post-processing.**
- Di atas S yang tersisa sekitar **−0,004** (14 error dari 3.556), dari tabel kecil yang dipelajari
  dari prediksi model sendiri di data latihnya. CI-nya tidak menyentuh 0, tapi angkanya kecil, dan
  versi yang lebih ketat (≥ 3 kemunculan) turun ke −0,0015.
- Membuang filler sekarang merugikan: S sudah menulis filler seperti referensi.
- Untuk F, tabel yang setara berisi 30 aturan (min 2) atau 8 aturan (min 3).

**Keputusan yang disarankan:** tidak memakai slot test hanya untuk post-processing. Kalau
nanti ada slot untuk resep tahap 2 yang baru, tabel ini bisa ikut sebagai arm terpisah hanya
bila slotnya cukup.

## Varian `c5-lr6e6`: LR 6e-6 vs 3e-6 (29 Sep)

`findings/10-dev-stage-finetune-c5-lr6e6/`, 23/23 PASS, kontrol D tepat lagi (3.965 / 799 / 3.166).
Satu variabel vs c5: LR 6e-6. Checkpoint `…-c5-lr6e6@d59cb293`, sha16 `473c9d17b0b86401`.

| convo 2 (held-out) | D | c5 (3e-6) | c5-lr6e6 |
|---|---:|---:|---:|
| WER | 0,2247 | 0,1980 | **0,1943** |
| error (S / D / I) | 799 (656/56/87) | 704 (537/51/116) | 691 (524/50/117) |
| kurva greedy epoch 1 / 2 / 3 | — | 0,2061 / 0,2002 / 0,2008 | 0,2028 / **0,1954** / 0,1985 |
| fit convo 5 (latih), S − D | — | −0,086 | −0,112 |

**lr6e6 − c5 di convo 2: −13 error, −0,0037, CI95 [−0,0101, +0,0028], p(lebih baik) 0,857**,
26/15 klip. Menurut aturan yang ditetapkan sebelum run (CONDONG butuh p ≥ 0,90), hasilnya
**"F (3e-6) tetap"**.

- Gain held-out kecil dan tidak pasti. Fit data latih naik jauh lebih banyak (−0,112 vs −0,086),
  jadi sebagian besar LR ekstra dipakai untuk menghafal 2 penutur latih.
- Kurva greedy mencapai titik terbaik di epoch 2 lalu naik lagi di epoch 3, tanda overfit mulai
  muncul. Di c5 (3e-6) kurvanya datar.
- Penutur uji #2 dan subset `ind` tidak membaik secara jelas (CI menyentuh 0).
- Insertion tetap tinggi (117 vs D 87). LR yang lebih besar tidak memperbaikinya.

## Arm P di test: F + tabel rewrite (29 Sep)

Submission `3097` (full), ZIP sha16 `7d3bebb72b598e63`: **0,2664**, vs F 0,2660 (+0,0004). Smoke
`3023`: 0,1043 (= F). Full run 2.118 klip, 0 gagal, 636,6 s, jalur 2051 / 67 / 134.

Analog held-out memperkirakan −0,0039 [−0,0071, −0,0014]; test memberi +0,0004. **Tabel rewrite
tidak berpindah ke test.** Tabel itu dipelajari dari 4 penutur dev, dan sesudah fine-tune tahap 2 yang
tersisa kemungkinan kebiasaan penutur dev, bukan konvensi referensi. Tuas konvensi di level token
dianggap habis. F tetap yang terbaik.
