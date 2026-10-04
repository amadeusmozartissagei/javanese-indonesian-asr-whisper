---
title: "Rencana Eksekusi — Lost in Transcription (Notebook 02–08)"
aliases:
  - Rencana Eksekusi - Lost in Transcription
  - Rencana Eksekusi
  - Roadmap Notebook 02-08
tags:
  - research
  - competition
  - asr
  - plan
status: active
created: 2026-08-23
updated: 2026-09-22
deadline: 2026-10-02T07:00:00+07:00
team_size: 3
---

# Rencana Eksekusi — Notebook 02 sampai 08

> [!summary] Ringkasan
> Peta kerja dari hari ini sampai deadline. Tujuh notebook, tiga lane paralel, tiga decision gate aktif. Setiap notebook punya **brief tersendiri** yang bisa dibuka di chat Claude baru tanpa konteks apa pun dari chat sebelumnya.
>
> **Ibaratnya:** ini kalender bersama plus papan tugas tim, biar tiap orang tahu ngerjain apa dan kapan tanpa harus tanya-tanya tiap hari. "Decision gate" itu kayak checkpoint di lomba lari estafet — kalau pelari sebelumnya belum sampai checkpoint dengan hasil yang cukup bagus, pelari berikutnya belum boleh mulai lari.

> [!danger] Diperbarui 22 September 2026 — jadwal di bawah sudah usang
> **Deadline mundur lagi ke 2 Oktober 2026, 00:00 UTC** (07:00 WIB, 2 Oktober). Tabel [[#Jadwal]] masih dihitung dari 25 September, jadi baris "buffer 21–24 Sep" dan "submit final 25 Sep" **tidak berlaku lagi**. Jadwal baru belum disusun.
>
> Posisi per 22 September: NB 06 selesai 7 September (E4 dibekukan), NB 08 sudah ditulis tapi belum dijalankan, NB 07 belum mulai, dan per catatan 12 September belum ada submission. Limit submission sekarang jelas: 3 per 7 hari per anggota tim (tim kita = 9), smoke test 10 per hari.
>
> Detail dan sumbernya di [[rules-review-2026-08-23#Update 22 September 2026 — situs, forum, dan runtime repo dicek ulang|Kaji Ulang Peraturan - 23 Agustus 2026 > Update 22 September 2026 — situs, forum, dan runtime repo dicek ulang]].

> [!danger] Diperbarui 25 Agustus 2026 — tiga hal besar berubah
> Situs kompetisi dibaca penuh hari ini (sebelumnya diproksi lewat repo runtime sejenis), dan bug di eval harness ditemukan sekaligus diperbaiki. Detail lengkap di [[rules-review-2026-08-23|Kaji Ulang Peraturan - 23 Agustus 2026]].
>
> 1. **Deadline mundur ke 25 September 2026, tengah malam UTC** (07:00 WIB) — bukan 16 September. Itu tambahan **±9 hari** dari asumsi lama, sudah dipakai untuk melonggarkan jadwal di bawah.
> 2. **Submission ternyata sudah dibuka duluan** (270 peserta terdaftar). Gate lama yang mengecek "apakah submission sudah dibuka" jadi tidak perlu lagi — sudah terjawab.
> 3. **`scorer.py` punya bug nyata, sudah diperbaiki hari ini.** Normalizer resmi ternyata melakukan lowercase di awal kalimat dan menghapus titik — dua hal yang sebelumnya diasumsikan tidak terjadi. Sudah dipatch di file dan di notebook, lolos 28/28 self-test. Dampaknya lebih dari sekadar scorer: kolom `text_official` di `manifest.csv` dibangun langsung dari fungsi ini, jadi isi manifest-nya sendiri berubah. **Ketiga fase NB 02 (bukan cuma fase 1) wajib di-rerun** — audio tidak berubah, tapi `_meta/` yang baru perlu dipublikasikan ulang sebagai New Version sebelum angka WER dipakai sebagai dasar keputusan.

> [!info] Dokumen yang menjadi dasar
> - [[rules-review-2026-08-23|Kaji Ulang Peraturan - 23 Agustus 2026]] — aturan terverifikasi, termasuk update 25 Agustus
> - [[nb01-dataset-analysis|Analisa Dataset - Notebook 01]] — angka yang diukur langsung dari data
> - [[feasibility-study|Feasibility Study - Mozilla Lost in Transcription]] — konteks, biaya, dan alokasi lane awal

## Prinsip kerja

Enam aturan yang berlaku di seluruh notebook. Kalau sebuah keputusan bertentangan dengan salah satunya, prinsipnya yang menang.

1. **Latih pada keluaran normalizer resmi.** Distribusi output model harus identik dengan distribusi yang dinilai. Jangan tambahkan pembersihan sendiri di luar `scorer.official_normalize()` — itu satu-satunya sumber kebenaran, dan sudah diperbaiki 25 Agustus.
2. **Split dibekukan sekali, selamanya.** Dikelompokkan per rekaman. Setiap angka WER di proyek ini harus datang dari split yang sama, kalau tidak angkanya tidak bisa dibandingkan.
3. **Satu artefak dibangun sekali.** Audio tersegmentasi, leksikon asal-kata, dan scorer menjadi Kaggle dataset. Notebook GPU tinggal mount, tidak menghitung ulang.
4. **Selalu laporkan WER Jawa dan WER Indonesia terpisah.** WER total bisa menyembunyikan pertukaran akurasi antar bahasa. Ini guard, bukan pelengkap.
5. **Asumsikan internet mati saat inference.** Setiap keputusan model diuji terhadap pertanyaan: apakah ini masih jalan di dalam ZIP tanpa jaringan, dengan `torch` dan `transformers` saja? Ini sekarang fakta resmi, bukan dugaan — kontainer submission memang tanpa akses jaringan.
6. **Checkpoint sebelum run panjang.** Sesi Kaggle putus di sekitar 12 jam, dan batas eksekusi submission resmi 2 jam. Resume harus sudah diuji sebelum run yang lebih panjang dari 6 jam dimulai.

## Peta notebook

```
02 Data Build & Eval Harness  (CPU)     <- jalur kritis, semua menunggu ini
     |
     +--> 03 Zero-shot Baseline (GPU, murah)
     |         |
     |         +--> 04 Fine-tune Whisper Core (GPU)  --+
     |         |                                       |
     |         +--> 05 XLS-R CTC + LM (GPU)          --+--> 06 Data Mixing (GPU)
     |                                                          |
     +--> 08 Packaging & Submission (CPU/GPU)  <--- 07 Error Analysis & Robustness
              ^                                          ^
              |                                          |
        dimulai paralel sejak hari 1,              butuh model terbaik dari 06
        tidak menunggu model
```

| Notebook | Brief | Lane | Accelerator | Target selesai |
|---|---|---|---|---|
| 02 — Data Build & Eval Harness | [[nb02-brief-data-build-eval-harness\|Brief Notebook 02 - Data Build dan Eval Harness]] | C (Thoriq) | **None** | 25 Agu — selesai, tapi **perlu rerun fase 1** untuk validasi scorer.py yang diperbaiki |
| 03 — Zero-shot Baseline | [[nb03-brief-zeroshot-baseline\|Brief Notebook 03 - Zero-shot Baseline]] | A (Pratama) | T4 ×2 | 27 Agu |
| 04 — Fine-tune Whisper Core | [[nb04-brief-finetune-whisper-core\|Brief Notebook 04 - Finetune Whisper Core]] | A (Pratama) | T4 ×2, **2 akun = 4 slot paralel** | 2 Sep |
| 05 — XLS-R CTC + LM | [[nb05-brief-xlsr-ctc-lm\|Brief Notebook 05 - XLS-R CTC dan LM]] | B (Fadil) | P100 | 2 Sep |
| 06 — Data Mixing | [[nb06-brief-data-mixing\|Brief Notebook 06 - Data Mixing]] | A + B | T4 ×2, 4 slot paralel | 12 Sep — **selesai 7 Sep, Gate 4 lolos**, kandidat E4 dibekukan → [[nb06-data-mixing-results\|Hasil Notebook 06 - Data Mixing]] |
| 07 — Error Analysis & Robustness | [[nb07-brief-error-analysis-robustness\|Brief Notebook 07 - Error Analysis dan Robustness]] | semua | T4 | 18 Sep |
| 08 — Packaging & Submission | [[nb08-brief-packaging-submission\|Brief Notebook 08 - Packaging dan Submission]] | A (Pratama) | None / T4 | 20 Sep |

## Workstream 0 — administrasi

Tidak butuh GPU. Beberapa item sudah terjawab sendiri lewat pembacaan situs 25 Agustus, sisanya masih menunggu dan sudah lewat tenggat.

| # | Tugas | PIC | Tenggat | Status |
|---|---|---|---|---|
| W0.1 | Salin tanggal deadline persis | Pratama | 23 Agu | **Tertutup 25 Agu** — 25 September 2026, tengah malam UTC, dibaca langsung dari halaman kompetisi |
| W0.2 | Posting sembilan pertanyaan P0–P2 ke forum penyelenggara | Thoriq | 23 Agu | **Sebagian tertutup** — deadline, case-sensitivity, dan titik sudah terjawab dari situs sendiri. Diakritik dan batas submission harian **masih perlu ditanyakan** |
| W0.3 | Verifikasi Territory, usia ≥18, pendaftaran atas nama pribadi | Fadil | 24 Agu | **Terlambat.** Territory sudah terjawab lewat aturan resmi (Indonesia lolos, lihat [[rules-review-2026-08-23\|Kaji Ulang Peraturan - 23 Agustus 2026]]); usia dan status pendaftaran pribadi masih perlu dicek manual |
| W0.4 | Pastikan ketiga anggota terdaftar sebagai satu tim | Pratama | 24 Agu | **Terlambat, belum ada bukti selesai** |
| W0.5 | Pemantauan harian halaman kompetisi | Thoriq | harian | Bisa dikurangi — spesifikasi runtime dan status submission sudah terbit, tinggal pantau forum dan perubahan spesifikasi |
| W0.6 | Repo HuggingFace privat untuk checkpoint | Fadil | 24 Agu | **Terlambat, belum ada bukti selesai** — jadi prasyarat keras sebelum NB 04/05 mulai run panjang |
| W0.7 | Catat kuota GPU aktual tiap akun Kaggle | semua | 24 Agu | **Terlambat, dan sekarang lebih penting** — lihat [[#Alokasi compute personal]], rencana 4-slot paralel butuh angka ini supaya tidak menembak kuota tanpa sadar |

> [!warning] Soal akun sekunder
> ToS Kaggle melarang satu orang punya lebih dari satu akun. **Rekomendasi tidak berubah: jangan pakai akun sekunder untuk run yang menentukan**, dan jangan taruh checkpoint satu-satunya di sana.

## Artefak yang dihasilkan

Ini yang harus ada di akhir proyek, terlepas dari model mana yang menang.

| Artefak | Dibuat di | Bentuk | Dipakai oleh |
|---|---|---|---|
| `jember-segments-16k` | NB 02 | Kaggle dataset — 208 FLAC 16 kHz mono, satu per rekaman | 03, 04, 05, 06, 07 |
| `manifest.csv` | NB 02 | satu baris per segmen: path, durasi, teks 3 varian, split, rasio-Jawa | semua |
| `split.csv` | NB 02 | pemetaan `audio_filename` ke train/dev, **dibekukan** | semua |
| `lexicon_v1.csv` | NB 02 | klasifikasi asal kata: `jv` / `id` / `both` / `unk` | semua evaluasi |
| `scorer.py` | NB 02 | normalizer resmi + WER + WER per asal kata — **diperbaiki 25 Agu**, versi lama tidak boleh dipakai lagi | semua evaluasi |
| `submission_src/` | NB 08 | `main.py` datar + bobot model | submission |
| Laporan Obsidian per notebook | tiap NB | markdown di vault root | tim |

> [!tip] Kenapa segmentasi jadi Kaggle dataset, bukan dihitung ulang tiap notebook
> Memotong 208 mp3 menjadi ribuan klip dan resample ke 16 kHz memakan waktu belasan menit CPU setiap kali. Kalau dilakukan di dalam tiap notebook GPU, waktunya dibayar dengan kuota GPU dan hasilnya berisiko berbeda antar-notebook. Sekali bangun, semua orang mount yang sama.
>
> **Soal 3 fase (feasibility → production → verify) dan limit download 500 file:** masalah download 600MB yang gagal berulang kemarin ternyata bukan soal ukuran, tapi limit Kaggle 500 file per "Download all" — sudah teratasi dengan layout satu-FLAC-per-rekaman (231 file). Ini **tidak menghapus** kebutuhan 3 fase: fase produksi tetap publish server-side (lebih baik daripada download-lalu-upload-ulang), dan fase verifikasi tetap butuh kernel baru yang independen dari kernel yang menulis datanya. Yang berubah cuma satu trik kecil di fase 1 (menyembunyikan folder bulk dari output) — sekarang jadi jaring pengaman, bukan keharusan.

## Jadwal

Dihitung dari deadline resmi **25 September 2026, tengah malam UTC** (07:00 WIB).

> [!warning] Usang sejak 12 September
> Deadline sekarang 2 Oktober 2026. Lihat callout 22 September di bagian atas.

| Tanggal | Hari | Fokus | Deliverable |
|---|---|---|---|
| 25 Agu | Sel — **hari ini** | Rerun NB 02 ketiga fase (manifest + scorer + republish + verify) + mulai NB 03 | `manifest.csv` dan WER NB 02 tervalidasi ulang dengan normalizer yang benar |
| 26–27 Agu | Rab–Kam | NB 03 | Tabel zero-shot: model × language token × varian teks |
| 28 Agu – 2 Sep | Jum–Rab | NB 04 + NB 05 paralel, pakai 4 slot T4 (baseline + 3 ablation NB 04 sekaligus, lihat [[#Alokasi compute personal]]) | Whisper fine-tuned dan XLS-R CTC pada split yang sama |
| 2 Sep | Rab | — | **Gate 2** — fine-tune harus mengalahkan zero-shot |
| 3–12 Sep | Kam–Sab | NB 06, 4 slot paralel (E1 & E3 murah duluan, lanjut E2/E4 sesuai hasil) | Satu campuran data terbaik terpilih dan terbukti |
| 12 Sep | Sab | — | **Gate 3** — satu model dibekukan sebagai kandidat |
| 13–18 Sep | Min–Jum | NB 07 | Error analysis, augmentation, checkpoint averaging |
| 3–20 Sep | paralel sejak awal | NB 08 | Container terkemas, diuji offline, latency terukur |
| 21–24 Sep | Sen–Kam | — | **Buffer 4 hari** — perbaikan saja, bukan eksperimen baru |
| 25 Sep | Jum | — | **Submit final**, sebelum tengah malam UTC |

Notebook 08 sengaja dimulai paralel sejak awal September dan tidak menunggu model final. Kerangka `main.py`, pemuat bobot dari disk, penulis CSV, dan uji offline tidak bergantung pada model mana yang akhirnya menang.

> [!tip] Buffer sekarang 4 hari, bukan 1
> Jadwal lama (deadline 16 September) hanya menyisakan satu hari buffer. Dengan deadline yang benar (25 September), buffer diperbesar jadi 4 hari — dipakai untuk hal tak terduga (bug packaging, run yang gagal, spesifikasi runtime berubah), bukan untuk eksperimen baru.

## Decision gates

Gate lama yang mengecek "apakah submission sudah dibuka" (dulu dijadwalkan 1 September) **dihapus dari daftar** — sudah terjawab 25 Agustus, submission ternyata sudah dibuka duluan.

| Gate | Tanggal | Kriteria lulus | Kalau gagal |
|---|---|---|---|
| **1** | 25 Agu | `jember-segments-16k`, `split.csv`, `scorer.py` selesai dan tervalidasi | Hentikan semua lane GPU — jalur kritis, tidak ada yang bisa jalan tanpanya |
| **2** | 2 Sep | Whisper fine-tuned pada Jember **lebih baik daripada zero-shot terbaik**, diukur pada dev yang sama | Jangan lanjut ke data mixing. Kembali ke audit data, normalisasi, dan hyperparameter |
| **3** | 12 Sep | Ada **satu** model yang menang di dev dan muat di anggaran runtime | Bekukan model terbaik apa adanya. Seluruh sisa waktu ke NB 08 |

> [!success] Gate 1 LULUS PENUH — 25 Agustus, setelah dua bug ditemukan dan diperbaiki
> Perbaikan pertama (lowercase + strip titik) sendiri punya bug idempotency — koma/kutip di antara titik dan huruf berikutnya menghalangi deteksi awal-kalimat di pass pertama (21 dari 6.638 baris kena). Sudah diperbaiki. Ketiga fase sudah di-rerun: fase 1 (11/11 self-check), fase 2 (republish `_meta/` sebagai New Version dataset), fase 3 (**28/28 lolos**, termasuk "fingerprints match the reviewed pass: 6 of 6" dan "official_normalize is idempotent on the shipped text: 6638 rows"). `>>> DATASET VERIFIED. Notebook 03 may mount it.`
>
> Detail lengkap ada di [[nb02-data-build-results|Hasil Notebook 02 - Data Build]]. **Audit 26 Agustus ([[nb02-cross-audit-scorer-text-2026-08-26|Audit Silang - Scorer dan Asumsi Teks (26 Agustus 2026)]]) mengoreksi dua hal di sana**: angka lama 44,5% ternyata bukan efek normalizer melainkan `wer(..., normalize=False)` — perbaikan normalizer cuma bernilai 0,4 poin persen — dan argumen "strategi dominan" untuk diakritik gugur sampai `indonesian_dev/metadata.tsv` diunduh dan diperiksa apakah referensi resmi memakai diakritik. Itu item P0 baru sebelum Notebook 04.

## Alokasi compute personal

Bagian ini spesifik untuk lane A (Pratama): **2 akun Kaggle, masing-masing sesi T4 ×2, jalan bersamaan lewat `CUDA_VISIBLE_DEVICES` (bukan DDP)** = **4 proses training independen sekaligus**.

> [!important] Ini kompresi waktu, bukan tambahan kuota
> Kuota mingguan Kaggle dihitung per jam sesi, bukan per GPU yang dipakai — jadi memilih T4 ×2 tidak membakar kuota dua kali lebih cepat dibanding T4 ×1. Nilai sebenarnya dari 4 slot ini: **ablation yang tadinya menunggu baseline selesai sekarang bisa jalan bersamaan dengannya.** Angka kuota persis per akun masih belum diverifikasi (W0.7) — cek itu sebelum menjadwalkan run 20 jam+.

**NB 04 — Fine-tune Whisper Core (28 Agu – 2 Sep):**

| Slot | Isi | Kenapa |
|---|---|---|
| 1 | Sanity chain (overfit 32 segmen → uji checkpoint-resume → ukur step/s) lalu **baseline `whisper-small` full fine-tune** | Run yang menentukan Gate 2 |
| 2 | Ablation: latih + eval di `text_folded` | Estimasi langsung nilai taruhan diakritik ke penyelenggara |
| 3 | Ablation: bekukan 50% layer encoder bawah | Cadangan murah kalau kuota menipis |
| 4 | Ablation: `large-v3-turbo` + LoRA | Paling berat — ganti ke "encoder dibekukan penuh" kalau VRAM/waktu tidak muat |

Slot 2–4 tidak menunggu slot 1 selesai — begitu resep learning rate/batching tervalidasi dari sanity chain, langsung jalan bersamaan.

**NB 06 — Data Mixing (3–12 Sep):**

| Slot | Eksperimen | Jam perkiraan |
|---|---|---:|
| 1 | E1 — Jember + TTS, ruang terlipat | ~16 |
| 2 | E3 — Jember + 439 klip Common Voice beraksen Jawa | ~9 (sinyal murah duluan) |
| 3 | Latih model diakritisasi M2 (kecil, cepat) → lanjut E2 | ~16 |
| 4 | Nganggur sampai E3 kelar, lalu E4 kalau E1/E2 lolos aturan pemilihan | ~20–25 |

Urutan ini sengaja: E3 kasih sinyal murah duluan untuk memutuskan apakah layak lanjut ke E4 yang mahal, tanpa antre di belakang E1/E2.

**NB 05 (Fadil, P100)** bukan bagian default alokasi ini — kalau Fadil butuh backup kuota, salah satu dari 4 slot bisa dipinjamkan, tapi jangan diasumsikan otomatis.

## Ladder model

Spesifikasi runtime sekarang sudah resmi (lihat [[rules-review-2026-08-23|Kaji Ulang Peraturan - 23 Agustus 2026]]): 1× A100 80GB, jadi ruang jauh lebih longgar dari asumsi lama. Semua kandidat di bawah tetap berlisensi permisif dan lolos aturan kompetisi.

| Prioritas | Model | Params | Lisensi | Catatan |
|---|---|---|---|---|
| 1 | `openai/whisper-small` | 244 M | MIT | Baseline utama. Aman di T4 untuk full fine-tune |
| 2 | `openai/whisper-large-v3-turbo` | 809 M | MIT | Decoder hanya 4 layer sehingga inference jauh lebih murah daripada large-v3. **Kandidat terkuat** — dan sekarang jelas muat di anggaran A100 80GB |
| 3 | `facebook/wav2vec2-xls-r-300m` | 300 M | Apache-2.0 | Jalur CTC. Vocabulary bisa dikontrol penuh, cocok untuk ortografi berdiakritik |
| 4 | `openai/whisper-medium` + LoRA | 769 M | MIT | Hanya kalau prioritas 1 dan 2 stabil dan masih ada kuota |
| 5 | `openai/whisper-base` | 74 M | MIT | Jaring pengaman kalau ternyata ada batas ukuran submission tersembunyi |
| — | MMS | — | CC-BY-NC-4.0 | **Gugur.** Tidak lolos syarat lisensi komersial bebas |
| — | Omnilingual ASR | 300 M–7 B | perlu dicek | Hanya kalau lisensinya terverifikasi dan waktu tersisa |

Aturan pemilihannya tidak berubah: **model terkecil yang menang di dev, bukan model terbesar yang muat.**

## Alokasi lane

| Lane | PIC | Accelerator | Beban |
|---|---|---|---|
| **A — Whisper** | Pratama | T4 ×2 × 2 akun = **4 slot paralel** | NB 03, 04, 06, 08 — lihat [[#Alokasi compute personal]] |
| **B — CTC** | Fadil | P100 | NB 05, kontribusi ke 06 dan 07 |
| **C — Data** | Thoriq | tanpa accelerator | NB 02, forum, pemantauan, kontribusi ke 07 |

## Risiko yang aktif dipantau

| # | Risiko | Status | Mitigasi |
|---|---|---|---|
| 1 | ~~Submission tidak pernah dibuka tepat waktu~~ | **Selesai — sudah dibuka sejak sebelum 25 Agu** | — |
| 2 | Paket yang kita butuhkan tidak ada di runtime image | Spesifikasi resmi sudah terbit: `uv`, `pyproject.toml`/`uv.lock` | Jalur utama hanya `torch` + `transformers`. CTC + KenLM adalah cadangan lewat PR ke runtime repo |
| 3 | Batas ukuran model lebih kecil daripada dugaan | **Tertutup sebagian** — 1× A100 80GB dikonfirmasi, jauh lebih longgar dari asumsi lama | Ladder model di atas tetap jadi acuan urutan |
| 4 | Scoring ternyata case-sensitive dan kita sudah lowercase | **Terjadi, tapi sebaliknya** — scoring melakukan lowercase parsial, scorer lama tidak. Sudah diperbaiki 25 Agu | `scorer.py` dipatch, 28/28 self-test lolos |
| 5 | Diakritik tidak dinormalisasi penyelenggara | Masih terbuka — belum disebut di mana pun | NB 02 menyimpan varian raw dan folded; NB 06 punya jalur restorasi diakritik (M2) |
| 6 | Run panjang putus di 12 jam | Aktif | Checkpoint-resume diuji di NB 04 sebelum run panjang, wajib untuk slot 3–4 yang paling berat |
| 7 | Akun Kaggle sekunder hilang | Aktif | Jangan dipakai untuk run final; checkpoint di HF Hub privat (W0.6, masih belum ada bukti selesai) |
| 8 | Dev split terlalu kecil, keputusan jadi bising | Aktif | NB 03 mengukur variansi dev; kalau perlu, pindah ke 5-fold grouped CV untuk keputusan tipis. **Ada dev set resmi 372 klip dari distribusi test asli** yang belum dipakai — lihat [[rules-review-2026-08-23\|Kaji Ulang Peraturan - 23 Agustus 2026]] |
| 9 | Whisper berhalusinasi pada jeda dan noise | Aktif | `condition_on_prev_tokens=False`, ambang no-speech, penindas repetisi — diuji di NB 07 |
| 10 | Overfit pada 8,5 jam data latih | Aktif | Early stopping, SpecAugment, dan run mixing di NB 06 |

## Definition of done

Proyek dianggap selesai kalau seluruh hal berikut ada, bahkan jika peringkatnya tidak juara.

- [ ] Submission valid terkirim sebelum deadline, atau alasan tertulis kenapa tidak
- [ ] Satu model terbaik dengan WER dev yang terukur, dilaporkan bersama WER Jawa dan WER Indonesia terpisah
- [ ] Seluruh notebook 02–08 bisa dijalankan ulang dari nol dan menghasilkan angka yang sama
- [ ] Repo siap dirilis di bawah MPL 2.0: kode, config, weights, dan dependency
- [ ] Setiap dataset eksternal yang dipakai untuk training sudah ada di MDC atau siap dipublikasikan ke sana
- [ ] Catatan Obsidian per notebook lengkap, dengan angka yang dirujuk ke `dataset_findings.json` masing-masing

## Cara memakai brief

Setiap brief dirancang untuk **dibuka di chat Claude yang baru**, tanpa membawa konteks apa pun. Isinya sudah memuat konteks minimum, keputusan yang tidak boleh didebat ulang, dan kriteria selesai.

Alurnya:

1. Buka chat baru, tempelkan isi brief yang bersangkutan.
2. Claude menulis notebook mengikuti konvensi output di `findings/README.md`.
3. Notebook dijalankan di Kaggle, Output tab → Download all → unzip ke root repo.
4. Blok `BEGIN CLAUDE-HANDOFF-JSON` … `END CLAUDE-HANDOFF-JSON` ditempel balik ke chat.
5. Claude menulis catatan Obsidian hasilnya di vault root.
6. Brief notebook berikutnya diperbarui kalau ada keputusan yang berubah.

Semua brief:

- [[nb02-brief-data-build-eval-harness|Brief Notebook 02 - Data Build dan Eval Harness]]
- [[nb03-brief-zeroshot-baseline|Brief Notebook 03 - Zero-shot Baseline]]
- [[nb04-brief-finetune-whisper-core|Brief Notebook 04 - Finetune Whisper Core]]
- [[nb05-brief-xlsr-ctc-lm|Brief Notebook 05 - XLS-R CTC dan LM]]
- [[nb06-brief-data-mixing|Brief Notebook 06 - Data Mixing]]
- [[nb07-brief-error-analysis-robustness|Brief Notebook 07 - Error Analysis dan Robustness]]
- [[nb08-brief-packaging-submission|Brief Notebook 08 - Packaging dan Submission]]
