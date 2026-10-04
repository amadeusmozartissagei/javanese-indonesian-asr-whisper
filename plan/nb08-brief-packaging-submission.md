---
title: "Brief Notebook 08 — Packaging & Submission"
aliases:
  - Brief Notebook 08 - Packaging dan Submission
  - Brief Notebook 08
tags:
  - brief
  - notebook
  - submission
  - packaging
notebook_id: "08-packaging"
lane: "A — Whisper"
accelerator: "None / T4"
target: 2026-09-14
depends_on: "07 (untuk bobot final), tidak untuk kerangkanya"
status: dapat-dimulai-sekarang
---

# Brief Notebook 08 — Packaging & Submission

> [!abstract] Untuk Claude di chat baru
> Mengemas model menjadi ZIP yang bisa dijalankan penyelenggara. **Mulai sekarang, jangan tunggu model final.** Sekitar 80% pekerjaan di sini tidak bergantung pada model mana yang menang — kerangka `main.py`, pemuatan bobot dari disk, penulisan CSV, penanganan input aneh, dan uji offline semuanya bisa selesai lebih dulu. Yang tersisa saat spesifikasi resmi terbit hanyalah penyesuaian path dan format.
>
> **Ibaratnya:** ini kayak packing koper dan latihan lewat pemeriksaan bandara duluan, sebelum tahu baju mana yang bakal dipakai di tujuan. Sebagian besar packing-nya (koper, cara lipat, dokumen) tidak bergantung pada baju mana yang akhirnya kepilih (model mana yang menang).

> [!success] Spesifikasi resmi SEKARANG SUDAH ADA — koreksi 25 Agustus
> Draf brief ini ditulis 23 Agustus saat submission belum dibuka. **Sudah berubah**: submission sudah dibuka, dan runtime resmi terkonfirmasi dari halaman Code Submission Format — 1× A100 80GB, 24 vCPU, 220GB RAM, Python 3.12 berbasis `uv`, limit eksekusi **2 jam** (smoke test 1 menit), tanpa internet, `main.py` wajib di root ZIP, baca dari `/code_execution/data/`, tulis ke `/code_execution/src/`'s output convention. Detail lengkap di [[rules-review-2026-08-23|Kaji Ulang Peraturan - 23 Agustus 2026]]. Tabel "Asumsi kerja tentang runtime" di bawah ternyata sudah banyak yang tepat (path data/submission cocok persis) — baris GPU dan dependency perlu dibaca ulang dengan angka resmi ini, bukan lagi sebagai tebakan dari repo analog DrivenData.

> [!success] Format submission resmi sudah di repo — 28 Agustus
> `competition/submission_format.csv` dan `competition/smoke_test_submission_format.csv` diunduh dari Data download page. Tiga hal berhenti jadi tebakan:
>
> - **Test set = 2.118 klip.** Bukan "500 / 1.000 / 3.000" seperti yang masih diekstrapolasi di Fase 1 langkah 6 di bawah. Nama filenya 32 hex + `.mp3`, seluruhnya unik.
> - **Waktu inference bukan kendala sama sekali.** 2.118 klip × 0,203 detik/klip (`whisper-large-v3-turbo`, batch 8, T4, dari `findings/03-zeroshot/latency.json`) = **7,2 menit** melawan limit 2 jam — dan kontainernya A100, bukan T4.
> - **Yang mengikat justru smoke test.** Isinya cuma **5 klip**, jadi decode-nya ~1 detik dan seluruh limit 1 menit praktis habis untuk import plus memuat bobot. **Batas ukuran model ditentukan waktu load, bukan waktu decode.** Turbo butuh 9,3 detik load — aman, tapi ini alasan konkret untuk tidak menumpuk ensemble di dalam ZIP. Kelima klip smoke test tidak termasuk 2.118 klip test.
>
> Format CSV-nya terkonfirmasi persis seperti yang diasumsikan: header `audio_filename,transcript`, satu baris per klip. Lihat `competition/README.md`.

## Yang diketahui pasti dari aturan

| # | Fakta | Sumber |
|---|---|---|
| 1 | Submission berupa **ZIP berisi model dan kode inference**, dijalankan di container penyelenggara | Problem description |
| 2 | Input berupa **klip `.mp3`** | Problem description |
| 3 | Output **CSV** dengan kolom `audio_filename` dan `transcript`, satu baris per klip | Problem description |
| 4 | **Setiap sampel diproses independen**, dilarang memakai informasi dari sampel test lain | Official rules |
| 5 | **Tidak boleh memanggil API pihak ketiga**; model harus jalan lokal | Official rules |
| 6 | Inference otomatis pada data baru **tanpa retraining** | Official rules |
| 7 | Solusi pemenang dirilis **MPL 2.0** lengkap dengan weights, config, dan dependency | Official rules |

## Asumsi kerja tentang runtime

| Aspek | Asumsi | Kalau salah |
|---|---|---|
| Entrypoint | `main.py` di **root ZIP**, tidak bersarang di folder | Pindahkan satu file |
| Path data | `/code_execution/data/` | Baca dari env var atau argumen, sediakan fallback |
| Path submission | `/code_execution/src/` | Turunkan dari `__file__`, jangan hardcode |
| **Internet** | **Diblokir total** | Ini asumsi yang aman ke arah manapun |
| Dependency | Sudah terpasang di image; menambah paket lewat PR ke `runtime/pyproject.toml` dengan lead time berhari-hari | **Kunci jalur utama ke `torch` + `transformers` saja** |
| GPU | Ada, tetapi tipe dan batas waktunya tidak diketahui | Sediakan jalur CPU yang tetap jalan meski lambat |

## Prinsip desain

1. **Bobot ikut di dalam ZIP.** Jangan pernah memanggil `from_pretrained("openai/...")` yang mengunduh. Muat dari path relatif terhadap `main.py`.
2. **Tidak ada I/O jaringan sama sekali.** Termasuk telemetri, cek versi, dan HuggingFace Hub. Set `HF_HUB_OFFLINE=1` dan `TRANSFORMERS_OFFLINE=1` di awal `main.py`.
3. **Jangan pernah crash.** Bungkus inference per klip dengan try/except; kalau gagal, tulis string kosong dan lanjut. Satu exception bisa menggagalkan seluruh submission.
4. **Deterministik.** Seed tetap, greedy atau beam tetap, tanpa sampling.
5. **Satu klip pada satu waktu, secara logis.** Batching untuk kecepatan boleh, tetapi tidak boleh ada informasi yang mengalir antar klip. Ini aturan kompetisi nomor 4, bukan preferensi.
6. **Path relatif, bukan absolut.** Turunkan semuanya dari lokasi `main.py`.

## Struktur

```
submission_src/
    main.py                 <- wajib di root ZIP
    inference.py            <- pemuatan model, decode
    postprocess.py          <- aturan final dari notebook 07
    model/                  <- bobot, config, tokenizer, feature extractor
    README.md               <- catatan reproduksi
```

Kerangka `main.py`:

```
1. set env offline, seed, dan device
2. temukan folder data test, kumpulkan seluruh .mp3
3. muat model sekali dari ./model
4. untuk tiap klip:
       muat audio, resample ke 16 kHz mono
       inference
       post-processing
       simpan hasil
   setiap iterasi dibungkus try/except -> string kosong kalau gagal
5. tulis CSV dengan kolom audio_filename, transcript
6. cetak ringkasan waktu ke log
```

## Langkah

### Fase 1 — sekarang, tanpa menunggu apa pun

1. Bangun `submission_src/` lengkap memakai **checkpoint terbaik yang ada sekarang** — bahkan model zero-shot pun cukup untuk menguji pipa-nya.
2. Tulis `main.py`, `inference.py`, dan `postprocess.py` sesuai kerangka di atas.
3. Bangun **harness uji lokal**: folder berisi 50 klip `.mp3` dari dev, dijalankan seolah-olah container. Pakai `competition/submission_format.csv` sebagai kontrak keluaran — baris dan urutannya harus cocok persis — dan `competition/smoke_test_submission_format.csv` untuk melatih jalur smoke test, termasuk **mengukur waktu import + load bobot terhadap limit 1 menit**. **Kelima klip smoke test itu ada di `Datasets/indonesian_dev/` lengkap dengan transkrip referensinya** — jadi gladi bersihnya bukan cuma "tidak crash", tapi bisa dicek transkripsinya masuk akal.
4. **Uji offline sungguhan.** Di Kaggle, matikan toggle Internet, lalu jalankan. Kalau ada yang mencoba mengunduh, di sinilah ketahuan.
5. Uji kelima kasus input aneh dari notebook 07: diam, sangat pendek, lebih dari 30 detik, noise saja, dan file rusak.

> [!danger] Klip di atas 30 detik BUKAN kasus aneh — itu kelas input yang diharapkan
> Spesifikasi resmi menyebut test berdurasi **2–40 detik**, sementara jendela encoder Whisper tepat **30 detik**: apa pun di atas itu dipotong diam-diam, dan sisa audionya jadi deletion murni. Ini tidak bisa diperbaiki dari sisi data latih — seluruh korpus Jember mentok di **29,0 detik** (0 segmen di atas 30 detik, 16 segmen saja yang di atas 20 detik), jadi model tidak akan pernah melihat contoh panjang berapa pun banyaknya kita melatih.
>
> **Konsekuensinya chunking wajib ada di `main.py`, bukan opsional.** Potong klip >30 detik dengan tumpang tindih kecil, transkripsi tiap potongan, lalu sambung. Uji jalur ini secara khusus: buat klip sintetis 35 dan 40 detik dari dev dan pastikan keluarannya tidak terpotong. Sekarang ada angkanya: di 372 klip dev resmi — distribusi yang sama dengan test — **10,2% melewati 30 detik** (mean 24,9s, median 26,3s, max 37,9s). Diekstrapolasi ke 2.118 klip test itu **sekitar 216 klip** yang akan dipotong diam-diam. Lihat [[official-dev-set-analysis-2026-08-28|Analisa Dev Set Resmi - 28 Agustus 2026]].
6. Ukur **wall-clock per klip** dan kalikan ke **2.118 klip** (ukuran test set yang sudah pasti dari `competition/submission_format.csv`). Untuk CPU dan GPU keduanya — jalur CPU tetap perlu diukur sebagai rencana cadangan kalau GPU di container bermasalah.
7. Catat **ukuran ZIP** per kandidat model.

### Fase 2 — hari runtime repo terbit

1. Baca `Dockerfile` dan `pyproject.toml`-nya. Catat versi `torch` dan `transformers` yang tersedia.
2. Cocokkan versi library lokal dengan yang ada di image. Beda versi `transformers` bisa mengubah perilaku `generate`.
3. Sesuaikan path dan format output kalau berbeda dari asumsi.
4. **Kalau ada paket yang kurang, ajukan PR hari itu juga.** Lead time-nya berhari-hari dan ini bisa menjadi jalur kritis di minggu terakhir.
5. Jalankan container resmi secara lokal kalau memungkinkan.
6. Submit **submission percobaan** secepatnya — jangan menunggu model final. Tujuannya memvalidasi format, bukan mengejar skor.

### Fase 3 — pengemasan final

1. Ganti isi `model/` dengan checkpoint dari `final_recipe.json`.
2. Jalankan ulang seluruh uji Fase 1.
3. Verifikasi bahwa WER pada dev **melalui `main.py`** sama dengan WER yang dilaporkan notebook 07. Kalau berbeda, ada ketidakcocokan antara pipeline eksperimen dan pipeline submission — ini bug klasik dan mahal.
4. Submit.

## Anggaran runtime

Batasnya belum diketahui, jadi siapkan tabel keputusan sebelum angka resminya keluar. Isi dari data notebook 03 dan Fase 1.

| Kandidat | Ukuran ZIP | Detik/klip GPU | Detik/klip CPU | Total untuk 1.000 klip |
|---|---|---|---|---|
| `whisper-base` fine-tuned | | | | |
| `whisper-small` fine-tuned | | | | |
| `whisper-large-v3-turbo` fine-tuned | | | | |
| XLS-R 300M CTC greedy | | | | |
| Ensemble | | | | |

Aturannya: **pilih model terkecil yang WER-nya masih dalam CI dev dari yang terbaik.** Kalau `small` dan `turbo` selisihnya tidak signifikan, pilih `small` — risiko runtime-nya jauh lebih kecil.

## Checklist kepatuhan sebelum submit

- [ ] Tidak ada panggilan jaringan sama sekali; sudah diuji dengan Internet mati
- [ ] Tidak ada API pihak ketiga (R7)
- [ ] Tiap klip diproses independen, tidak ada state lintas klip (R8)
- [ ] Tidak ada retraining saat inference (R10)
- [ ] Seluruh bobot berlisensi permisif: Whisper MIT, XLS-R Apache-2.0 (R6, R14)
- [ ] Tidak ada bobot MMS di mana pun (CC-BY-NC-4.0 gugur)
- [ ] Seluruh dataset training ada di MDC atau siap dipublikasikan ke sana (R5)
- [ ] Repo siap dirilis MPL 2.0 dengan weights, config, dan dependency (R13)
- [ ] Kode tidak pernah dibagikan privat di luar tim (R12)
- [ ] Header CSV persis `audio_filename,transcript`
- [ ] Jumlah baris CSV sama dengan jumlah klip test, tanpa duplikat dan tanpa yang hilang

## Jebakan

- **Ketidakcocokan antara pipeline eksperimen dan pipeline submission** adalah cara paling umum kehilangan poin. Muat MP3 dengan library yang sama, resample dengan cara yang sama, dan pakai fungsi post-processing yang sama persis.
- `torchaudio` dan `librosa` bisa menghasilkan resampling yang sedikit berbeda. Kunci satu, dan pakai yang sama di notebook 02.
- Test set berupa MP3, sementara data latih kita FLAC hasil konversi. Uji model pada dev yang **di-encode ulang ke MP3** untuk memastikan tidak ada kejutan.
- ZIP tidak boleh punya folder pembungkus. `main.py` harus di root.
- Simbolik link dan file `.git` di dalam ZIP bisa membuat unzip gagal. Kemas bersih.
- Model cache HuggingFace kadang tersimpan di `~/.cache`. Salin bobot ke dalam ZIP, jangan mengandalkan cache.
- Waktu muat model dihitung dalam batas waktu container. Kalau batasnya ketat, ini bisa jadi masalah untuk model besar.

## Setelah selesai

Tulis `Hasil Notebook 08 - Packaging.md`, berisi tabel anggaran runtime terisi, kandidat terpilih beserta alasannya, dan catatan reproduksi yang cukup untuk memenuhi kewajiban dokumentasi pemenang.
