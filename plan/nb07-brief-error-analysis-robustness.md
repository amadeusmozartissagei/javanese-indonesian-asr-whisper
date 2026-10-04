---
title: "Brief Notebook 07 — Error Analysis & Robustness"
aliases:
  - Brief Notebook 07 - Error Analysis dan Robustness
  - Brief Notebook 07
tags:
  - brief
  - notebook
  - evaluation
notebook_id: "07-error-robustness"
lane: "semua"
accelerator: "T4"
target: 2026-09-11
depends_on: "06"
status: dapat-dimulai-sekarang
---

# Brief Notebook 07 — Error Analysis & Robustness

> [!danger] Diperbarui 22 September 2026 — beberapa asumsi brief ini sudah usang
> - **NB 06 selesai 7 September.** E4 dibekukan sebagai kandidat (lihat [[nb06-data-mixing-results|Hasil Notebook 06 - Data Mixing]]). Brief ini tidak lagi terblokir; target 11 September sudah lewat dan belum diganti.
> - **Urutannya terbalik: NB 08 dulu, NB 07 sesudahnya.** `notebooks/08-packaging.ipynb` sudah menulis `main.py` dan `postprocess.py` dengan daftar `RULES` yang sengaja dikosongkan. Hasil NB 07 mengisi `RULES` itu, bukan membangun `main.py` dari nol lewat `final_recipe.json` seperti tertulis di bawah.
> - Deadline sekarang 2 Oktober 2026. Detail di [[rules-review-2026-08-23#Update 22 September 2026 — situs, forum, dan runtime repo dicek ulang|Kaji Ulang Peraturan - 23 Agustus 2026 > Update 22 September 2026 — situs, forum, dan runtime repo dicek ulang]].

> [!abstract] Untuk Claude di chat baru
> Model sudah dibekukan di notebook 06. Notebook ini mencari **poin WER yang bisa diambil tanpa melatih ulang dari nol**, dan memastikan model tidak runtuh pada kondisi audio yang berbeda dari dev. Untuk kompetisi WER berdurasi pendek, tahap ini sering lebih menguntungkan daripada menambah ukuran model.
>
> **Ibaratnya:** ini periksa lembar jawaban ujian yang sudah dikoreksi, buat lihat **di mana** nilainya hilang. Ada yang cuma salah tulis huruf besar/kecil (gampang dibetulin, gratis), ada yang memang salah dengar/salah paham (butuh belajar lebih dalam lagi, tidak bisa dibetulin instan).

## Bagian A — Error analysis

Tujuannya menemukan kesalahan yang punya **penyebab tunggal**, karena hanya itu yang bisa diperbaiki dengan murah.

### A1 — Pecah kesalahan berdasarkan penyebab

Dari `scorer.error_table` pada dev, klasifikasikan setiap substitution:

| Kategori | Contoh | Perbaikannya |
|---|---|---|
| Hanya beda diakritik | `terus` versus `têrus` | Post-processing atau normalisasi teks latihan |
| Hanya beda kapitalisasi | `Aku` versus `aku` | Post-processing |
| Hanya beda punctuation | `omah` versus `omah.` | Post-processing |
| Hanya beda tanda hubung | `arek arek` versus `arèk-arèk` | Post-processing |
| Jawa diganti Indonesia | `ora` menjadi `tidak` | Butuh perubahan pada model atau data |
| Salah dengar sungguhan | — | Butuh perubahan pada model atau data |

Empat kategori pertama adalah **nilai gratis**. Ukur total kontribusinya terhadap WER. Kalau angkanya di atas 2 poin, perbaikan post-processing lebih berharga daripada eksperimen model apa pun yang tersisa.

### A2 — Pecah berdasarkan sifat segmen

Cari di mana model paling sering gagal:

- **Rasio kata Jawa** per segmen — apakah WER naik pada segmen yang paling Jawa?
- **Durasi segmen** — apakah segmen sangat pendek atau sangat panjang lebih buruk?
- **Per rekaman** — mana 5 rekaman terburuk, dan apa kesamaannya? Dengarkan langsung, jangan hanya melihat angka
- **Ada tidaknya reduplikasi** — 1.558 segmen memuatnya
- **Ada tidaknya elipsis** — 718 segmen memuatnya
- **Kata yang tidak ada di data latih** — berapa WER pada segmen yang memuat OOV

### A3 — Dengarkan

Ambil 30 segmen dengan WER tertinggi, dengarkan, dan kategorikan manual: transkrip referensinya salah, audionya memang tidak jelas, ada tumpang tindih suara, atau modelnya yang keliru. **Batas atas WER yang bisa dicapai ditentukan oleh kategori pertama dan kedua.** Kalau sebagian besar segmen terburuk ternyata referensinya bermasalah, berhenti mengejar poin di sana.

## Bagian B — Perbaikan tanpa melatih ulang

### B1 — Post-processing

Bangun dari temuan A1, uji satu per satu di dev, pertahankan hanya yang memperbaiki:

- Pemetaan diakritik ke bentuk yang paling sering muncul di data latih. Notebook 02 punya daftar 210 kata berejaan ganda beserta hitungan tiap varian — pakai varian mayoritas
- Aturan kapitalisasi, misalnya huruf besar hanya di awal kalimat
- Penyeragaman tanda hubung untuk pola reduplikasi
- Penyeragaman bentuk elipsis

> [!warning] Setiap aturan harus dibuktikan di dev
> Post-processing yang terdengar masuk akal bisa memperburuk WER. Uji satu per satu, catat deltanya, dan buang yang netral atau negatif. Simpan aturan final sebagai fungsi tunggal supaya bisa langsung dipakai di `main.py` notebook 08.

### B2 — Setelan decode

Untuk Whisper:

- `num_beams` 1 versus 5 — ukur perbaikan WER dan biaya waktunya
- `no_repeat_ngram_size` dan penindas repetisi
- Ambang no-speech dan ambang logprob untuk menekan halusinasi
- `condition_on_prev_tokens` tetap `False`
- Batas panjang keluaran diturunkan berdasarkan distribusi panjang referensi

Untuk CTC: sweep `alpha`, `beta`, dan `beam_width` sudah ada di notebook 05; di sini tinggal terapkan yang terbaik pada model final.

### B3 — Checkpoint averaging

Rata-ratakan 3–5 checkpoint terbaik dari run yang sama. Murah, sering memberi 0,3 sampai 1 poin, dan **tidak menambah biaya inference sama sekali**. Selalu layak dicoba.

### B4 — Ensemble, hanya kalau runtime mengizinkan

Whisper dan CTC punya profil kesalahan yang berbeda — notebook 05 mengukurnya. ROVER atau penggabungan sederhana bisa membantu. Tetapi biayanya dua model di dalam ZIP dan dua kali waktu inference, sementara batas runtime belum diketahui. **Jangan kerjakan sebelum spesifikasi runtime terbit.** Kalau tetap dikerjakan, sediakan jalur mundur ke satu model.

## Bagian C — Robustness

Test set kompetisi belum dideskripsikan. Yang diketahui hanya bahwa isinya klip `.mp3`. Karena itu uji ketahanan model terhadap kondisi yang mungkin berbeda dari dev.

### C1 — Uji ketahanan

Terapkan pada dev, ukur WER masing-masing, jangan latih ulang:

| Perlakuan | Meniru |
|---|---|
| Re-encode MP3 pada 32, 24, 16 kbps | Kompresi voice note |
| Encode Opus dan AMR-NB lalu decode lagi | Voice note WhatsApp dan Telegram |
| Tambah noise SNR 20, 15, 10 dB | Rekaman di luar ruangan |
| Reverb ringan | Ruangan berbeda |
| Perubahan gain ±6 dB | Jarak mikrofon berbeda |
| Speed perturbation 0,9× dan 1,1× | Kecepatan bicara berbeda |
| Potong 0,3 detik di kedua ujung | Konvensi segmentasi test set yang berbeda |

Baris terakhir penting: timestamp Jember berpresisi satu detik, dan kita menambahkan padding 0,2 detik di notebook 02. Kalau test set dipotong dengan konvensi lain, model harus tetap tahan.

### C2 — Augmentation kalau ada yang runtuh

Kalau ada perlakuan yang menaikkan WER lebih dari 3 poin, latih ulang model final dengan augmentation yang meniru perlakuan itu. Biasanya cukup satu run pendek melanjutkan dari checkpoint terbaik.

### C3 — Perilaku pada input aneh

Container akan menerima apa pun yang penyelenggara berikan. Uji dan pastikan tidak ada yang crash:

- klip yang isinya hanya diam
- klip sangat pendek, di bawah 0,5 detik
- klip lebih panjang dari 30 detik
- klip yang isinya hanya noise
- file MP3 rusak

Untuk setiap kasus, `main.py` nanti harus mengeluarkan **string kosong**, bukan exception. Satu crash bisa menggagalkan seluruh submission.

## Output

`NOTEBOOK_ID = "07-error-robustness"`.

| File | Isi |
|---|---|
| `error_breakdown.csv` | kesalahan per kategori penyebab, dengan kontribusi WER-nya |
| `error_by_segment_property.csv` | WER per rasio Jawa, durasi, rekaman, OOV |
| `listening_notes.csv` | 30 segmen terburuk dengan kategorisasi manual |
| `postproc_ablation.csv` | delta WER per aturan post-processing |
| `decode_ablation.csv` | delta WER per setelan decode |
| `robustness.csv` | WER per perlakuan audio |
| `edge_cases.json` | perilaku pada input aneh |
| `final_recipe.json` | **resep final** — checkpoint, setelan decode, aturan post-processing |
| `dataset_findings.json` | digest `rec()` |

`final_recipe.json` adalah kontrak dengan notebook 08. Isinya harus cukup untuk membangun `main.py` tanpa menebak apa pun.

## Kriteria selesai

- [ ] Kontribusi WER tiap kategori penyebab terukur
- [ ] Aturan post-processing final terpilih dan terbukti di dev
- [ ] Setelan decode final terpilih, dengan biaya waktunya tercatat
- [ ] Checkpoint averaging diuji
- [ ] Tabel robustness lengkap, dan tidak ada kasus yang menaikkan WER lebih dari 3 poin tanpa mitigasi
- [ ] Kelima kasus input aneh tidak ada yang crash
- [ ] `final_recipe.json` terisi lengkap

## Setelah selesai

Tulis `Hasil Notebook 07 - Error Analysis.md`. Serahkan `final_recipe.json` ke [[nb08-brief-packaging-submission|Brief Notebook 08 - Packaging dan Submission]].
