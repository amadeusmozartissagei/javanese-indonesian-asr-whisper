---
title: "Serah terima 30 Sep — posisi dan taruhan berikutnya"
aliases:
  - Next steps 30 Sep
tags:
  - plan
  - handoff
status: active
updated: 2026-09-30
---

# Serah terima 30 Sep 2026: posisi, apa yang sudah habis, taruhan berikutnya

**Deadline: 2 Okt 2026, 00:00 UTC.** Submission yang *dimulai* sebelum deadline tetap dihitung.
**Sisa slot full: 4** (user melaporkan 5 pada 29 Sep, lalu 1 dipakai untuk P). Smoke 10/hari tidak
memberi skor test.

## Posisi

| | test |
|---|---|
| **Terbaik: F** = E4-native + tahap 2 di dev resmi (NB 10 `all`) + beam 5, submission `2914` | **0,2660** |
| P = F + tabel rewrite 30 aturan, `3097` | 0,2664 |
| D = E4-native + beam 5, `2693` | 0,2901 |
| #1 leaderboard (27 Sep) | 0,2096 |
| **Target user** | **< 0,2076** |

Jarak ke target ~0,058. Semua ZIP, sha, dan log ada di [`submissions/README.md`](../submissions/README.md).
Laporan tahap 2: [[nb10-dev-stage-finetune-results]].

## Apa yang terbukti, apa yang sudah habis

- **Konvensi referensi adalah tuas besar, dan sudah terpakai.** Tahap 2 di dev: −0,024 di test,
  sesuai perkiraan held-out convo 2 (−0,027). Sesudah itu tabel rewrite (−0,004 di held-out) tidak
  berpindah ke test (+0,0004). **Tuas konvensi di level token dianggap habis.**
- Sudah dicoba dengan gain ~0,005 atau kurang: beam 5, segmen native, LR tahap 2 6e-6 (convo 2
  −0,0037, CI menyentuh 0; varian `all-lr6e6` = arm G **belum dijalankan**, knob-nya sudah di NB 10).
- omniASR zero-shot kalah dari D (lead #2 ditutup). Post-processing filler sekarang merugikan.
- Sisa error F kira-kira pendengaran / leksikal pada kata yang sudah dikenal (evaluasi gap #1: ~0,14
  dari 0,23 WER dev D). Insertion naik setelah tahap 2 (convo 2: 87 → 116).

## Penilaian jujur

Dengan ~1,5 hari, menutup 0,058 lewat penyetelan kecil hampir mustahil. Tiap tuas selain konvensi
bernilai ≤ 0,005. Tim di 0,21 dengan 3 submission berarti **pendekatannya berbeda**, bukan
setelannya. Kalau target < 0,2076 dipertahankan, sisa slot harus dipakai untuk 1–2 taruhan berdampak
besar, bukan varian kecil seperti G.

## Taruhan yang layak dibahas di chat baru (urut: potensi / biaya)

1. **Cari tahu pendekatan tim atas** (lead #4 gap-eval, belum pernah dilakukan). Baca forum
   kompetisi dan write-up publik. Murah, dan bisa langsung menunjukkan apakah mereka memakai model
   dasar lain, data lain, atau LM.
2. **Pindahkan konvensi ke seluruh data latih.** Tahap 2 hanya memakai 2,2 jam dev. Target Jember
   (8,5 jam, teks emas) bisa ditulis ulang ke ejaan dev lewat pemetaan varian Jember → dev, lalu
   E4-native dilatih ulang, atau F dilanjutkan di atasnya. Risiko: pemetaan menggabungkan kata yang
   berbeda (fold berat 19,7 % tabrakan; fold ringan 2,7 %). Biaya: 1 run NB 06 (~2,7 jam T4) + NB 10 + NB 08.
3. **Model dasar lebih besar:** `whisper-large-v3` penuh (32 layer decoder, turbo hanya 4). Decoder
   turbo yang kecil mungkin membatasi pemodelan bahasa code-switched. Biaya: ~2× waktu latih tahap 1,
   ZIP ~3,1 GB fp16 (batas ukuran ZIP belum dicek), waktu decode test harus tetap < 2 jam di A100.
   Paling mahal, dan paling mungkin menutup jarak besar.
4. **Self-training di audio latih:** F mentranskripsi audio Jember / CV dalam konvensi dev, lalu
   hasilnya dipakai melatih. Diizinkan (R9 hanya soal test), tapi mewarisi error F.
5. G (`all-lr6e6`) hanya kalau ada slot tersisa di akhir. Perkiraannya ~−0,004.

## Aturan kerja yang tetap berlaku

`CLAUDE.md`: notebook ditulis di sini, dijalankan user di Kaggle; hanya agregat yang dibawa ke chat;
satu variabel per run dengan `RUN_NOTE` sendiri; **satu kandidat per slot, tunggu hasilnya sebelum
kandidat berikutnya** (koreksi user 29 Sep). `main.py` (sha `aa5a691f68011b81`) jangan diubah di luar
knob. Paritas dicek di NB 08.
