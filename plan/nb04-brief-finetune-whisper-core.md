---
title: "Brief Notebook 04 — Fine-tune Whisper (Core)"
aliases:
  - Brief Notebook 04 - Finetune Whisper Core
  - Brief Notebook 04
tags:
  - brief
  - notebook
  - training
notebook_id: "04-whisper-core"
lane: "A — Whisper"
accelerator: "T4 x2"
target: 2026-08-31
depends_on: "02, 03"
status: done
---

# Brief Notebook 04 — Fine-tune Whisper (Core)

> [!abstract] Untuk Claude di chat baru
> Fine-tune Whisper **hanya pada data Jember**, tanpa dataset tambahan apa pun. Ini baseline yang menjadi pembanding seluruh eksperimen berikutnya. Gate 2 (sekarang **2 September**, digeser dari 31 Agustus setelah deadline resmi mundur ke 25 September — lihat [[execution-plan|Rencana Eksekusi - Lost in Transcription]]) bergantung pada notebook ini: kalau hasilnya tidak mengalahkan zero-shot, jangan lanjut ke data mixing.
>
> **Ibaratnya:** ini les privat beneran, pakai materi latihan asli, buat karyawan yang tadi diuji polosan di notebook 03. Kalau setelah les dia masih tidak lebih jago dari sebelum les, jangan lanjut nambah materi les yang lebih banyak lagi (notebook 06) — cari dulu apa yang salah dari cara ngajarnya.

> [!check] Titik awal sudah ditetapkan Notebook 03 (27 Agustus)
> **`whisper-large-v3-turbo`, language token `jw`.** Turbo satu-satunya model yang lolos uji siku — setiap model lebih murah terbukti lebih buruk di paired bootstrap. `id` dan `jw` **seri** (CI selisih memuat nol), jadi `jw` dipilih atas dasar sisi Jawa yang paling perlu diperbaiki, bukan atas dasar WER.
>
> Angka penjaga: **`jv_to_id_sub_pct` 30,15%** — kalau WER turun tapi angka ini tidak, perbaikannya datang dari sisi Indonesia saja dan tidak akan bertahan di test set. Detail di [[nb03-zeroshot-baseline-results|Hasil Notebook 03 - Zero-shot Baseline]].

> [!danger] JANGAN pakai 0,8960 sebagai pembanding Gate 2
> WER 0,8960 diukur dengan decoder greedy tanpa pengaman, yang membuang ~6 poin ke loop pengulangan (`dulu` 435×, `gede` 193×). Kalau NB 04 mengevaluasi model hasil fine-tune **dengan** `no_repeat_ngram_size=4` lalu membandingkannya ke 0,8960, keuntungan fine-tuning akan **dilebihkan sekitar 6 poin** — dan Gate 2 jadi condong meloloskan diri sendiri.
>
> **Yang benar:** di NB 04, decode dev split sekali dengan checkpoint turbo yang **belum** di-fine-tune, memakai setelan decode NB 04 sendiri, dan pakai angka itu sebagai pembanding. Biayanya ~4 menit GPU (1.097 klip × 0,22 detik) di notebook yang memang sudah memuat Whisper dan men-decode dev. Tidak perlu notebook baru dan tidak perlu mengulang grid NB 03. Laporkan keduanya: baseline apples-to-apples, dan 0,8960 sebagai catatan historis.

## Konteks minimum

ASR Indonesian–Javanese, metrik WER per kata tanpa nilai parsial. Data latih: `split == train` dari Jember, sekitar 8,5 jam dan 5.600 segmen setelah pembuangan. Dev: 25 rekaman, sekitar 1,5 jam.

Teks latihan adalah kolom **`text_folded`** dari manifest (lihat kotak merah di atas — ini berubah 28 Agustus) — hasil normalizer resmi. Perhatikan: normalizer resmi **melakukan lowercase huruf awal kalimat** dan **menghapus titik** kecuali elipsis yang menempel di kata; tanda hubung dipertahankan. Model harus belajar mengeluarkan bentuk itu persis.

Konvensi teks lain sudah dibandingkan dengan dev resmi dan **semuanya cocok** — elipsis menempel, tanda hubung, dan kapitalisasi (3,3% token di kedua korpus, nama diri dan akronim). Satu pengecualian kecil: **referensi resmi tidak pernah memakai digit**, seluruh angka dieja. Jadikan itu satu item pemeriksaan saat mengevaluasi — Whisper zero-shot terbukti mengeluarkan `40` untuk `empat puluh` di NB 03.

> [!danger] Target latihan: `text_folded`. Terjawab 28 Agustus, dan bukan jawaban yang dulu diduga.
> Dev set resmi sudah diperiksa: ortografinya **tidak** memakai diakritik Jember. Nol `ê`/`è`/`ě` di 17.495 token; satu-satunya diakritik adalah sufiks `é` (0,30%). Dari 9.385 token berdiakritik Jember, **0,0% cocok apa adanya dan 69,4% cocok setelah dilipat**.
>
> Jadi gunakan kolom **`text_folded`** dari manifest sebagai target, bukan `text_official`. Kolomnya sudah ada dan sudah diverifikasi identik dengan `fold_diacritics(text_official)` untuk 6.638 baris — tidak perlu rerun NB 02. Bukti di [[official-dev-set-analysis-2026-08-28|Analisa Dev Set Resmi - 28 Agustus 2026]].

> [!warning] Validasi utama pindah, dan ada ketimpangan panjang yang harus ditangani
> **Lapisan validasi utama sekarang 372 klip dev resmi** (`Datasets/indonesian_dev/`), bukan dev split Jember. Split Jember tetap dipakai untuk memantau progres training karena besar dan murah, tetapi setiap klaim "lebih baik" dikonfirmasi di 372 klip itu. Audionya perlu diunggah jadi dataset Kaggle dulu — 372 MP3, 70 MB.
>
> Dataset Kaggle **`indonesian_dev`** sudah terbit (Version 1, 74,1 MB, 373 file). Akarnya punya satu level ekstra, jadi temukan jalurnya lewat pencarian, jangan ditulis keras:
> ```python
> META = next(Path("/kaggle/input").rglob("indonesian_dev/metadata.tsv"))
> DEV_CLIPS = META.parent / "clips"   # 372 mp3, 48 kHz mono
> ```
> Sanity check di cell 1: 372 klip, 372 baris metadata, nama file cocok satu-satu.
>
> **Klip resmi rata-rata 24,9 detik; segmen Jember rata-rata 5,4 detik.** Melatih hanya pada potongan pendek mendorong model ke perilaku yang tidak cocok dengan bentuk test. Karena anotasi Jember adalah partisi kontinu (seluruh 6.471 jeda tepat 0 detik) dan audionya tersimpan per rekaman dengan offset sampel, **menyambung segmen berurutan sampai ~25 detik cuma berarti memakai jendela `[start_sample pertama, end_sample terakhir]`** — tanpa membangun data baru. Jadikan ini salah satu slot ablation.

## Input

- Kaggle dataset `jember-segments-16k`
- `manifest.csv`, `split.csv`, `lexicon_v1.csv`, `scorer.py`
- Model dan language token pemenang dari notebook 03

## Output

`NOTEBOOK_ID = "04-whisper-core"`.

| File | Isi |
|---|---|
| `train_log.csv` | step, loss, lr, dev WER, waktu |
| `eval_final.json` | WER total, Jawa, Indonesia, ins/del/sub, `jv_to_id` |
| `predictions_dev.csv` | `seg_id,hypothesis` pada model terbaik |
| `error_table_dev.csv` | pasangan `ref → hyp` tersering, dengan penanda diakritik/kapital/punctuation |
| `checkpoint_manifest.json` | repo HF, revision, ukuran disk, hash |
| `dataset_findings.json` | digest `rec()` |

Bobotnya sendiri **tidak** ikut ke `findings/` — dorong ke repo HuggingFace **privat**, catat repo dan revision-nya di `checkpoint_manifest.json`.

## Langkah

### 1. Uji sanity dulu, sebelum run panjang

Berurutan, dan jangan lompat:

1. **Overfit 32 segmen.** Latih sampai loss mendekati nol dan model mereproduksi teks latihannya sendiri. Kalau ini gagal, ada bug di data collator atau label masking, bukan di hyperparameter.
2. **Uji checkpoint-resume.** Latih 100 step, simpan, matikan sesi, mulai sesi baru, resume, latih 100 step lagi. Pastikan optimizer state, scheduler, dan posisi dataloader benar-benar pulih. **Ini syarat, bukan opsi** — sesi Kaggle putus di sekitar 12 jam.
3. **Ukur langkah per detik** pada konfigurasi sebenarnya, lalu ekstrapolasi wall-clock. Kalau proyeksinya melewati 10 jam, kecilkan sebelum memulai, bukan sesudah.

### 2. Resep latihan

Titik awal, disesuaikan setelah run pertama:

| Setelan | Nilai awal | Catatan |
|---|---|---|
| Model | pemenang NB 03, default `whisper-small` | |
| Epoch | 3–5 dengan early stopping | 8,5 jam data mudah overfit |
| Learning rate | 1e-5 untuk `small`, 6e-6 untuk `medium`/turbo | warmup 10% |
| Scheduler | linear decay | |
| Batch | efektif 16–32 lewat gradient accumulation | |
| Precision | fp16 | T4 punya tensor core |
| Gradient checkpointing | on kalau VRAM ketat | |
| SpecAugment | on, mask waktu dan frekuensi sedang | Regularisasi utama pada data kecil |
| Eval | tiap 200–400 step, pada **subset dev tetap 300 klip** | Eval penuh hanya di akhir |
| Metrik pemilihan checkpoint | **WER dev**, bukan loss | |
| Language token | dikunci ke pemenang NB 03 | |
| Simpan | tiap eval, simpan 3 terbaik | |

### 3. Yang harus diukur, bukan hanya WER

Setiap evaluasi mencatat:

- `wer_total`, `wer_jv`, `wer_id`, `ins_rate`, `del_rate`, `sub_rate`
- **`jv_to_id`** — berapa persen substitusi pada kata Jawa yang mendarat di kata Indonesia. Baseline-nya dari NB 03. Kalau naik, model justru makin sering menerjemahkan alih-alih mendengar
- Berapa persen kesalahan yang **hanya** perbedaan diakritik, kapitalisasi, atau punctuation. Angka ini seharusnya turun tajam dibanding zero-shot; kalau tidak, ada yang salah dengan teks latihan
- Panjang hipotesis rata-rata dibanding referensi — deteksi dini halusinasi dan truncation

### 4. Ablation yang layak dijalankan di sini

Hanya kalau baseline sudah stabil dan masih ada kuota. Satu variabel per run.

| Ablation | Pertanyaan yang dijawab |
|---|---|
| Latih pada `text_folded`, evaluasi pada `text_folded` | Berapa keuntungan kalau penyelenggara ternyata melipat diakritik |
| Bekukan 50% layer encoder bawah | Apakah membantu pada data kecil |
| Encoder dibekukan penuh, hanya decoder yang dilatih | Batas bawah yang murah, berguna kalau kuota menipis |
| `large-v3-turbo` dengan LoRA | Apakah kapasitas lebih besar memang menang di sini |

> [!warning] Satu variabel per run
> Dev hanya 1,5 jam. Notebook 03 sudah memberi bootstrap CI-nya. **Selisih WER yang lebih kecil dari CI itu bukan temuan.** Kalau dua konfigurasi berselisih tipis, jalankan pada 5-fold grouped dari kolom `fold` di `split.csv` sebelum memutuskan.

## Keputusan yang sudah diambil — jangan didebat ulang

| Keputusan | Alasan |
|---|---|
| Hanya data Jember di notebook ini | Ini baseline. Pencampuran data adalah notebook 06 |
| Teks latihan `text_folded`, kapitalisasi dipertahankan | Dev resmi tidak memakai diakritik Jember sama sekali (28 Agustus). Baris ini dulu berbunyi `text_official` — itu sudah dibatalkan, lihat kotak merah di atas. Case folding tetap tidak dilakukan: normalizer resmi tidak menyebutnya, dan kapitalisasi 3,3% token di kedua korpus |
| Pemilihan checkpoint berdasarkan WER dev, bukan loss | Loss dan WER tidak selalu searah pada seq2seq |
| Checkpoint didorong ke HF privat | Sesi Kaggle 12 jam, dan akun bisa hilang |
| Split tidak boleh diregenerasi | Semua angka proyek ini harus sebanding |
| MMS tidak dipertimbangkan | Lisensi CC-BY-NC-4.0 gugur di aturan kompetisi |

## Kriteria selesai — ini Gate 2

- [ ] WER dev model fine-tuned **lebih baik** daripada zero-shot terbaik dari NB 03
- [ ] WER Jawa membaik, atau kalau memburuk, alasannya dipahami dan tertulis
- [ ] `jv_to_id` tidak lebih buruk daripada baseline zero-shot
- [ ] Checkpoint-resume terbukti bekerja
- [ ] Checkpoint terbaik ada di HF privat dengan revision tercatat

Kalau kriteria pertama gagal: **jangan lanjut ke NB 06.** Kembali ke audit data dan hyperparameter. Kegagalan fine-tune pada 8,5 jam data in-domain hampir selalu berarti masalah label, masalah normalisasi, atau learning rate yang terlalu besar — bukan berarti butuh lebih banyak data.

## Jebakan

- Whisper memakai label `-100` untuk padding. Salah masking menghasilkan loss yang terlihat wajar tetapi model yang tidak belajar apa pun.
- Token khusus di awal urutan target harus dipangkas saat menyusun label, sesuai konvensi processor. Ini sumber bug paling umum pada fine-tune Whisper.
- Evaluasi dengan `generate` jauh lebih lambat daripada training step. Kalau eval terlalu sering, sebagian besar wall-clock habis di situ.
- Cache fitur log-Mel ke disk sekali, jangan hitung ulang tiap epoch.
- Simpan checkpoint ke `/kaggle/working` **dan** dorong ke HF. Kalau sesi mati, `/kaggle/working` bisa ikut hilang.
- Jangan pakai akun Kaggle sekunder untuk run yang menentukan.

## Setelah selesai

**SELESAI 31 Agustus 2026. Gate 2 lolos 5/5** lewat ablation `concat25`; resep dasar terkunci di `concat25` + 1 epoch. Hasil di [[nb04-whisper-core-results|Hasil Notebook 04 - Whisper Core]].

Instruksi asli di sini — "bandingkan dengan NB 05 sebelum masuk ke NB 06" — **digantikan**: [[nb05-brief-xlsr-ctc-lm|Brief Notebook 05 - XLS-R CTC dan LM]] ditunda sampai setelah NB 06, karena dua dari tiga alasannya gugur oleh temuan 28-31 Agustus. Lanjut langsung ke [[nb06-brief-data-mixing|Brief Notebook 06 - Data Mixing]], yang sudah membawa catatan knock-on dari notebook ini.
