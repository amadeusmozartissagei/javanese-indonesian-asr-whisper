---
title: "Brief Notebook 03 — Zero-shot Baseline"
aliases:
  - Brief Notebook 03 - Zero-shot Baseline
  - Brief Notebook 03
tags:
  - brief
  - notebook
  - baseline
notebook_id: "03-zeroshot"
lane: "A — Whisper"
accelerator: "T4 x2"
target: 2026-08-27
depends_on: "02"
status: ready
---

# Brief Notebook 03 — Zero-shot Baseline

> [!abstract] Untuk Claude di chat baru
> Tidak ada training di sini. Tujuannya menetapkan **titik nol** dan menjawab empat pertanyaan yang menentukan seluruh eksperimen sesudahnya. Murah — seluruh notebook seharusnya di bawah 3 GPU-hour.
>
> **Ibaratnya:** ini seperti kasih tugas ke karyawan baru **sebelum** dia ditraining sama sekali, cuma buat lihat seberapa jauh kemampuan alaminya. Hasilnya jadi patokan: kalau setelah ditraining nanti dia tidak lebih baik dari sebelum ditraining, berarti ada yang salah di cara melatihnya, bukan di karyawannya.

## Konteks minimum

Kompetisi ASR Indonesian–Javanese, metrik WER. Notebook 02 sudah selesai dan **Gate 1 lulus penuh 25 Agustus 2026** — ketiga fase (build, produksi, verify) sudah di-rerun bersih setelah dua bug di normalizer ditemukan dan diperbaiki hari yang sama. Hasilnya di [[nb02-data-build-results|Hasil Notebook 02 - Data Build]]; jangan pakai angka dari sumber lain yang lebih tua.

> [!warning] Deadline dan runtime sudah bukan asumsi lagi
> Situs kompetisi dibaca penuh 25 Agustus: deadline resmi **25 September 2026** (bukan 16 September), submission sudah dibuka, dan runtime submission resmi adalah **1× A100 80GB, Python 3.12, tanpa internet**. Detail di [[rules-review-2026-08-23|Kaji Ulang Peraturan - 23 Agustus 2026]]. Latency yang notebook ini ukur tetap di T4 (anggaran eksperimen, bukan target submission) — jangan disalahartikan sebagai anggaran container.
>
> Ada juga **dev set resmi 372 klip** dari distribusi test asli (dialog voice-note dyadic), terpisah dari split Jember yang dipakai notebook ini. Belum diintegrasikan ke pipeline manapun — di luar cakupan notebook ini, tapi dicatat di sini supaya tidak terlewat saat merencanakan validasi di notebook-notebook berikutnya.

Yang perlu diketahui tentang datanya: percakapan spontan campur Jawa dan Indonesia, 74,1% segmen memuat kedua bahasa dalam satu kalimat, median panjang segmen 5 detik. Dev split **20 rekaman, 1.097 segmen, 1,63 jam**.

> [!warning] Layout dataset bukan seperti yang dibayangkan draft awal brief ini
> `jember-segments-16k` berisi **208 FLAC, satu per rekaman utuh** — bukan satu file per segmen. Kaggle memotong dataset di 500 file, jadi 6.638 klip tidak bisa diterbitkan. Segmen dialamatkan lewat offset sampel di manifest:
>
> ```python
> y, sr = sf.read(ROOT / r.path, start=r.start_sample, stop=r.end_sample, dtype="float32")
> ```
>
> Itu *seek* ke dalam FLAC, bukan decode ulang — murah. Companion file ada di `recordings/_meta/`: `manifest.csv`, `split.csv`, `lexicon_v1.csv`, `scorer.py`, `text_audit.json`, `dataset_findings.json`. Import scorer dengan `sys.path.insert(0, str(META_ROOT))`.
>
> Datasetnya milik akun **`hamzapratama`**, bukan `thoriqfarras` seperti tiga korpus sumber.

> [!danger] Tiga angka dari NB 02 yang mengikat notebook ini
> - **Selisih WER di bawah ~1,5 poin tidak terbukti dari satu run.** Dev 95% CI ± 0,7–0,8 poin. Pakai `scorer.compare_systems()` — uji bootstrap berpasangan, nol GPU — sebelum menyatakan satu konfigurasi menang.
> - **Dua lantai WER dev**: 11,8% token dev tidak pernah muncul di train, dan 0,86% dari inkonsistensi ejaan. Dev tidak akan pernah mendekati nol.
> - **`text_official` adalah referensi utama.** `text_folded` hanya alat ukur: nilai prediksi yang sama di kedua dunia untuk mengukur berapa WER yang murni perselisihan diakritik. Keputusan melatih di ruang berdiakritik sudah final — jangan didebat ulang.

## Empat pertanyaan yang harus dijawab

| # | Pertanyaan | Kenapa menentukan |
|---|---|---|
| Q1 | **Ukuran model mana yang layak jadi titik awal?** | Menentukan apakah `whisper-small` cukup atau harus naik ke `large-v3-turbo` |
| Q2 | **Language token mana yang terbaik — `id`, `jw`, atau autodetect?** | Whisper punya token bahasa Jawa (`jw`) dan Indonesia (`id`). Selisihnya bisa besar dan gratis |
| Q3 | **Seberapa parah Whisper menormalisasi kata Jawa jadi Indonesia?** | Kegagalan yang sudah diduga sejak studi kelayakan. Harus diukur, bukan diasumsikan |
| Q4 | **Berapa detik per klip di T4?** | Runtime resmi sudah diketahui (A100 80GB, limit 2 jam), tapi belum ada angka latency model apa pun untuk dibandingkan terhadapnya — ini data pertama kita |

## Input

- Kaggle dataset `jember-segments-16k` (dari NB 02) — 208 FLAC per rekaman + `recordings/_meta/`
- `manifest.csv`, `split.csv`, `lexicon_v1.csv`, `scorer.py` dari `_meta/`
- **Evaluasi hanya pada `split == dev`.** Train tidak disentuh sama sekali di notebook ini
- Temukan root-nya lewat penanda, jangan hardcode kedalaman — dataset ini di-mount di bawah `/kaggle/input/datasets/hamzapratama/...` dan pohon output NB 02 ikut terbawa, jadi path aslinya dalam

## Output

`NOTEBOOK_ID = "03-zeroshot"`.

| File | Isi |
|---|---|
| `zeroshot_results.csv` | satu baris per kombinasi: model × lang × ref_variant × metrik |
| `predictions/<model>__<lang>.csv` | `seg_id,hypothesis` mentah, sebelum normalisasi |
| `error_tables/<config>.csv` | keluaran `scorer.error_table` untuk 3 konfigurasi terbaik |
| `jv_to_id_substitutions.csv` | daftar substitusi kata Jawa → kata Indonesia, dengan hitungannya |
| `latency.json` | detik per klip, per model, di T4 |
| `dataset_findings.json` | digest `rec()` |

## Langkah

### 1. Grid evaluasi

| Sumbu | Nilai |
|---|---|
| Model | `whisper-tiny`, `whisper-base`, `whisper-small`, `whisper-medium`, `whisper-large-v3-turbo` |
| Language token | `id`, `jw`, autodetect |
| Varian referensi | `text_official`, `text_folded` |

Semuanya MIT dan sudah lolos aturan lisensi kompetisi. Jangan menambahkan MMS — bobotnya CC-BY-NC-4.0 dan gugur.

Prediksi dibuat **sekali** per (model, lang), lalu dinilai terhadap kedua varian referensi. Jadi run-nya 5 × 3 = 15, bukan 30.

Efisiensi: kalau kuota terasa ketat, jalankan grid penuh hanya pada `tiny`, `base`, `small`, lalu bawa **language token pemenang saja** ke `medium` dan `large-v3-turbo`.

### 2. Setelan decode

Kunci setelan berikut untuk semua run supaya hasilnya bisa dibandingkan:

- `task="transcribe"`, bukan translate
- `return_timestamps=False`
- `condition_on_prev_tokens=False` — mencegah halusinasi merambat antar klip
- greedy, `num_beams=1`, `temperature=0.0` — determinisme lebih penting daripada skor terbaik pada tahap ini
- `no_repeat_ngram_size` dibiarkan default; penindas repetisi diuji nanti di NB 07
- batch inference, `fp16` di T4
- **Setiap klip diproses independen.** Ini juga aturan kompetisi (R8), bukan sekadar kebersihan eksperimen

Catat versi `transformers` dan `torch` ke `rec()`.

### 3. Pengukuran per pertanyaan

**Q1 — kurva ukuran model.** Tabel WER terhadap ukuran. Yang dicari bukan hanya siapa yang menang, tetapi **di mana kurvanya mulai datar**. Kalau `small` ke `medium` hanya menghasilkan sedikit perbaikan, `small` adalah pilihan fine-tune yang benar.

**Q2 — language token.** Untuk model terbaik, bandingkan `id`, `jw`, dan autodetect pada WER total, WER Jawa, dan WER Indonesia terpisah. Untuk autodetect, catat juga **distribusi bahasa yang terdeteksi per klip** — kalau berpindah-pindah, itu sendiri temuan.

**Q3 — normalisasi Jawa ke Indonesia.** Ini pengukuran khusus, bukan turunan WER:

1. Ambil semua token referensi berkelas `jv` di `lexicon_v1`.
2. Dari alignment, kumpulkan substitusi yang terjadi pada token-token itu.
3. Hitung berapa persen di antaranya diganti dengan token berkelas `id`.
4. Keluarkan `jv_to_id_substitutions.csv` berisi pasangan tersering, misalnya `ora → tidak`, `wes → sudah`, `iso → bisa`.

Angka ini menjadi **metrik guard** yang dilaporkan di setiap notebook sesudahnya. Kalau data mixing menurunkan WER total tetapi menaikkan angka ini, kita sedang menukar akurasi Jawa demi akurasi Indonesia.

**Q4 — latency.** Ukur detik per klip pada satu T4, `fp16`, batch 1 dan batch 8. Batch 1 adalah yang relevan untuk container. Catat juga waktu muat model dari disk dan ukuran bobot di disk per model.

### 4. Analisa tambahan yang murah tapi berharga

- **Halusinasi.** Hitung berapa hipotesis yang panjangnya lebih dari 3× panjang referensi, dan berapa yang memuat n-gram berulang. Whisper cenderung mengulang pada jeda dan noise.
- **Selisih raw versus folded.** Berapa poin WER yang berubah hanya karena melipat diakritik. Ini **estimasi langsung** dari nilai yang dipertaruhkan pada pertanyaan P0 ke penyelenggara.
- **Kesalahan yang bisa dihilangkan tanpa model.** Dari `error_table`, berapa persen substitusi yang hanya berbeda kapitalisasi, hanya berbeda diakritik, atau hanya berbeda punctuation.
- **Variansi dev.** Hitung WER per rekaman di dev, lalu laporkan standar deviasinya dan bootstrap 95% CI untuk WER total. Ini yang menentukan seberapa besar selisih WER yang boleh dipercaya di notebook-notebook berikutnya.

## Kriteria selesai

- [ ] Tabel WER lengkap untuk seluruh grid, dengan WER Jawa dan WER Indonesia terpisah
- [ ] Satu (model, language token) terpilih sebagai titik awal fine-tune, dengan alasan tertulis
- [ ] Angka `jv_to_id` terukur dan tercatat sebagai baseline guard
- [ ] Bootstrap CI dev tersedia, sehingga notebook berikutnya tahu batas selisih yang bermakna
- [ ] `latency.json` terisi untuk seluruh model

## Jebakan

- **Jangan lowercase hipotesis sebelum scoring.** Pakai `scorer.official_normalize` saja, itu titik kesepakatannya.
- Whisper memakai kode bahasa `jw` untuk bahasa Jawa, bukan `jv`. Salah kode akan diam-diam jatuh ke default.
- `large-v3-turbo` punya decoder 4 layer, jadi jauh lebih cepat dari `large-v3` tetapi bukan model yang sama. Jangan tertukar saat mencatat hasil.
- Muat model sekali per konfigurasi, jangan per batch.
- Kalau autodetect dipakai, hasil deteksi bisa berbeda antar-run pada klip yang ambigu meski greedy. Catat hasil deteksinya supaya bisa direproduksi.

## Setelah selesai

Tulis catatan Obsidian `Hasil Notebook 03 - Zero-shot Baseline.md`. Berikutnya: [[nb04-brief-finetune-whisper-core|Brief Notebook 04 - Finetune Whisper Core]] dan [[nb05-brief-xlsr-ctc-lm|Brief Notebook 05 - XLS-R CTC dan LM]] berjalan paralel.
