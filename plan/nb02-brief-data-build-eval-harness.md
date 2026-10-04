---
title: "Brief Notebook 02 — Data Build & Eval Harness"
aliases:
  - Brief Notebook 02 - Data Build dan Eval Harness
  - Brief Notebook 02
tags:
  - brief
  - notebook
  - data
notebook_id: "02-data-build"
lane: "C — Data"
accelerator: none
target: 2026-08-25
blocks: "03, 04, 05, 06, 07"
status: ready
---

# Brief Notebook 02 — Data Build & Eval Harness

> [!abstract] Untuk Claude di chat baru
> Notebook ini **tidak melatih apa pun**. Tugasnya membangun empat artefak yang dipakai seluruh notebook sesudahnya: audio tersegmentasi, manifest, split yang dibekukan, dan scorer. Accelerator **None**. Ini jalur kritis — sampai selesai, tidak ada lane GPU yang boleh jalan.
>
> **Ibaratnya:** ini kerjaan "prep kitchen" sebelum dapur buka — motong bahan jadi porsi siap pakai dan kalibrasi timbangan, sebelum satu pun masakan mulai dibuat. Semua koki (notebook lain) menunggu ini kelar duluan, karena mereka semua makai bahan dan timbangan yang sama.

## Konteks minimum

Kompetisi Mozilla "Lost in Transcription", track Indonesian–Javanese. Tugasnya ASR untuk voice note percakapan campur bahasa Jawa dan Indonesia. Metriknya WER, per kata, tanpa nilai parsial.

Dataset utama **Jember Javanese Spontaneous Speech Corpus**: 208 rekaman MP3 tingkat sesi, 6.679 segmen, sekitar 10 jam. Audio **belum terpotong** — segmentasi memakai kolom start/end di TSV berformat `H:MM:SS`.

Notebook 01 sudah selesai dan hasilnya ada di `findings/01-dataset-eda/dataset_findings.json`. Yang perlu diketahui dari sana ada di bagian "Keputusan yang sudah diambil" di bawah.

## Input

Kaggle mount untuk akun ini **owner-scoped**, bukan `/kaggle/input/<slug>`:

```
/kaggle/input/datasets/thoriqfarras/jember-javanese-corpus/Jember Javanese Spontaneous Speech Corpus/
    Jember Javanese Spontaneous Speech Corpus - 1-200.tsv
    mp3 audio/1.mp3 ... 208.mp3
/kaggle/input/datasets/thoriqfarras/common-voice-corpus/id/
/kaggle/input/datasets/thoriqfarras/central-javanese-corpus/RECORDING TTS/
```

> [!warning] Jangan hardcode kedalaman path
> Temukan korpus lewat file penanda, lalu turunkan root-nya dari situ:
> - Jember: TSV yang header-nya memuat kolom start, end, dan text
> - Common Voice: `clip_durations.tsv`
> - TTS: folder `recordings (N)` yang berisi `mapping.tsv`

## Output yang harus dihasilkan

Semua lewat helper `out()` ke `/kaggle/working/findings/02-data-build/`, ikuti blok **OUTPUT CONVENTION** di cell 1 `notebooks/01-dataset-eda.ipynb` dan set `NOTEBOOK_ID = "02-data-build"`.

| File | Isi |
|---|---|
| `segments/<rec>_<idx>.flac` | audio per segmen, 16 kHz mono FLAC |
| `manifest.csv` | satu baris per segmen — skema di bawah |
| `split.csv` | `audio_filename,split` — **dibekukan setelah run ini** |
| `lexicon_v1.csv` | `word,origin,source` dengan origin ∈ `jv`/`id`/`both`/`unk` |
| `scorer.py` | modul mandiri, tanpa dependensi di luar stdlib + `jiwer` |
| `text_audit.json` | hasil audit karakter dan punctuation |
| `dataset_findings.json` | digest `rec()` seperti biasa |
| `run-log.txt` | otomatis dari konvensi |

Skema `manifest.csv`:

| Kolom | Isi |
|---|---|
| `seg_id` | `<rec>_<idx>`, contoh `63_004` |
| `audio_filename` | nomor rekaman induk, untuk grouping |
| `path` | path relatif ke FLAC |
| `start_s`, `end_s`, `dur_s` | detik, setelah padding |
| `text_raw` | teks TSV apa adanya |
| `text_official` | hasil `official_normalize()` — **ini teks latihan default** |
| `text_folded` | `text_official` + diakritik dilipat |
| `n_words`, `n_chars` | dihitung dari `text_official` |
| `jv_ratio` | porsi kata berasal-Jawa menurut `lexicon_v1` |
| `split` | `train` atau `dev` |
| `flags` | koma-terpisah: `zero_dur`, `overlap`, `has_ellipsis`, `has_redup`, `has_digit` |

> [!tip] Audio ikut ke output supaya bisa jadi Kaggle dataset
> Setelah run selesai, unduh Output tab lalu unggah folder `segments/` sebagai Kaggle dataset baru bernama **`jember-segments-16k`**. Notebook 03 ke atas mount dataset itu, bukan menghitung ulang. FLAC 16 kHz mono untuk 10 jam ada di kisaran 500–700 MB, masih nyaman.

## Langkah

### 1. Segmentasi audio

1. Parse `start` dan `end` berformat `H:MM:SS` menjadi detik. **Perhatikan bahwa presisinya hanya satu detik.**
2. Buang 41 segmen berdurasi nol atau negatif. Catat mana saja.
3. Periksa rekaman 63 — di sana ada 3 segmen bertumpuk dan satu `end` yang lebih kecil dari `start` selisih 30 detik. Perbaiki kalau bisa disimpulkan, kalau tidak buang.
4. **Ukur distribusi jeda antar segmen berurutan** dalam satu rekaman sebelum memutuskan padding.
5. Terapkan **padding 0,20 detik** di kedua sisi, dipotong supaya tidak melewati batas segmen tetangga maupun batas file. Alasannya: timestamp berpresisi satu detik pada ujaran spontan hampir pasti memotong onset dan offset kata. Laporkan berapa banyak segmen yang paddingnya terpotong tetangga.
6. Decode tiap MP3 **sekali** ke array, lalu iris di memori. Jangan panggil ffmpeg per segmen.
7. Resample ke **16 kHz mono**, tulis FLAC. Sample rate sumber campur 44,1 kHz (89 rekaman) dan 48 kHz (119 rekaman).
8. Verifikasi: jumlah file FLAC = jumlah baris manifest, dan tidak ada file berukuran nol.

### 2. Normalizer resmi

Implementasikan `official_normalize(text)` **persis** seperti yang penyelenggara sebutkan, tidak lebih:

1. hapus tag metalinguistik dalam kurung siku, misalnya `[laugh]`;
2. hapus penanda tidak terdengar `(???)` dan `[???]`;
3. hapus elipsis **berdiri sendiri** — yang punya spasi di kedua sisi;
4. **pertahankan** elipsis yang menempel ke kata, misalnya `mba...`;
5. hapus karakter punctuation `,?¿¡!";:` — **hanya ini, tidak ada tambahan**;
6. rapikan spasi ganda.

> [!danger] Tiga hal yang TIDAK boleh dilakukan
> - **Jangan lowercase.** Daftar resminya tidak menyebut case folding, jadi asumsikan scoring case-sensitive.
> - **Jangan hapus titik.** Titik tidak ada di daftar punctuation yang dihapus.
> - **Jangan hapus tanda hubung.** `arèk-arèk` harus tetap satu token.
>
> Dasarnya ada di [[rules-review-2026-08-23|Kaji Ulang Peraturan - 23 Agustus 2026]] bagian K1–K3. Prinsipnya: model harus belajar mengeluarkan bentuk yang persis sama dengan yang dinilai.

Lalu `fold_diacritics(text)`: NFD, buang combining mark, NFC. Praktisnya `ê è ě é → e`. Simpan sebagai kolom terpisah, jangan menimpa.

### 3. Audit teks — jawab pertanyaan yang masih menggantung

Tulis ke `text_audit.json` dan `rec()`:

| Yang diukur | Kenapa penting |
|---|---|
| Berapa token berakhiran `.` | Kalau banyak, keputusan mempertahankan titik berdampak besar |
| Berapa token berawalan huruf kapital, dan berapa di posisi non-awal kalimat | Mengukur berapa besar taruhan case-sensitivity |
| Berapa token mengandung `...` menempel, dan bentuk persisnya | Sudah diketahui 718 segmen; sekarang di level token |
| Inventaris **seluruh karakter unik** setelah `official_normalize`, dengan frekuensinya | Menjadi charset untuk vocabulary CTC di NB 05 |
| Berapa token mengandung digit, dan bentuknya | Angka biasanya sumber WER yang tidak perlu |
| Berapa token mengandung `-`, dan berapa di antaranya reduplikasi | Sudah diketahui 1.558 segmen |
| 210 kata berejaan ganda: daftar lengkapnya dengan hitungan tiap varian | Bahan untuk keputusan diakritik dan untuk NB 06 |
| Perbandingan jumlah token unik sebelum dan sesudah `fold_diacritics` | Mengukur langsung berapa banyak yang bisa diselamatkan |

### 4. Leksikon asal kata

`lexicon_v1.csv` dengan kolom `word,origin,source`. Metodenya:

1. Kumpulkan vocabulary Common Voice Indonesia dari `validated_sentences.tsv` — ini proksi kosakata Indonesia.
2. Kumpulkan vocabulary TTS Central Javanese dari seluruh `mapping.tsv` — proksi kosakata Jawa.
3. Klasifikasi awal: ada di CV saja → `id`; ada di TTS saja → `jv`; ada di keduanya → `both`; tidak ada di keduanya → `unk`.
4. Perbaiki dengan daftar penanda Jawa berfrekuensi tinggi. Minimal: `sing iku ning iso lan ora nggo dadi kuwi karo ono wong okeh yen banget seko wes dewe luwih mergo aku kowe arep gawe jare ngono ngene piye opo iki kono kene mau mengko sopo pirang kabeh meneh ndue moco mbien ngeki liyo amergo menungso podo arèk dhèwè mbek ndèk têrus`.
5. Bandingkan dalam bentuk **terlipat diakritik** supaya `têrus` dan `těrus` tidak terklasifikasi berbeda.
6. **Bekukan hasilnya.** Versi berikutnya harus bernama `lexicon_v2` supaya angka lama tetap bisa dibandingkan.

> [!note] Ini pengukuran kasar dan memang seharusnya begitu
> Batas leksikal Jawa–Indonesia memang tidak tegas, dan penyelenggara sendiri menyebutkannya. Gunanya leksikon ini bukan linguistik, melainkan **konsistensi**: supaya "WER kata Jawa" berarti hal yang sama di notebook 03 sampai 07. Kelas `both` dan `unk` dilaporkan terpisah, tidak dipaksa masuk salah satu sisi.

### 5. Split yang dibekukan

- Grup adalah **`audio_filename`**, bukan segmen. Jangan pernah membagi acak per segmen — TSV Jember tidak punya kolom speaker, sehingga suara yang sama akan bocor ke kedua sisi.
- Target dev **15% durasi**, sekitar 25 rekaman dan 1,5 jam.
- Stratifikasi pada dua hal: median `jv_ratio` per rekaman dibagi 3 bucket, dan durasi rekaman dibagi 3 bucket. Isi dev dengan bin-packing greedy per sel stratum.
- Seed tetap. Tulis seed ke `dataset_findings.json`.
- Laporkan untuk train dan dev: jumlah rekaman, jam, jumlah segmen, distribusi `jv_ratio`, distribusi durasi segmen, dan jumlah token unik yang **hanya** ada di dev.
- **Bekukan.** `split.csv` masuk repo dan tidak pernah diregenerasi.

> [!question] Kalau dev terasa terlalu kecil
> 25 rekaman dan 1,5 jam berarti selisih WER di bawah sekitar 1 poin sulit dipercaya. Notebook 02 juga menyiapkan **pembagian 5-fold grouped** di `split.csv` kolom `fold` (0–4), tidak dipakai sekarang tetapi tersedia kalau NB 04 atau NB 06 menemui keputusan yang tipis.

### 6. Scorer

`scorer.py` sebagai modul mandiri yang bisa di-import notebook lain. Isinya:

```
official_normalize(text) -> str
fold_diacritics(text) -> str
wer(refs, hyps, normalize=True) -> dict
wer_by_origin(refs, hyps, lexicon) -> dict
error_table(refs, hyps, lexicon, top_k=50) -> DataFrame
```

Aturan `wer_by_origin`:

- Lakukan alignment kata per kata sekali, lalu **atribusikan** substitution dan deletion ke kelas asal **token referensi**.
- **Insertion tidak punya token referensi**, jadi jangan dipaksa masuk kelas mana pun. Laporkan sebagai angka global `ins_rate` dan sebagai daftar kata yang paling sering disisipkan.
- Keluarkan: `wer_total`, `wer_jv`, `wer_id`, `wer_both`, `wer_unk`, `ins_rate`, `del_rate`, `sub_rate`, dan jumlah token referensi tiap kelas.
- `error_table` mengeluarkan pasangan `ref → hyp` tersering, ditandai apakah pasangan itu **hanya berbeda diakritik**, **hanya berbeda kapitalisasi**, atau **hanya berbeda punctuation**. Tiga kategori itu adalah kesalahan yang bisa dihilangkan tanpa menyentuh model sama sekali.

### 7. Validasi diri

Sebelum menutup notebook, pastikan dan `rec()`:

- [ ] jumlah FLAC = jumlah baris manifest, tidak ada file kosong
- [ ] total durasi manifest cocok dengan total durasi TSV setelah pembuangan, selisih di bawah 1%
- [ ] tidak ada `audio_filename` yang muncul di train dan dev sekaligus
- [ ] `official_normalize` idempoten: menerapkannya dua kali sama dengan sekali
- [ ] `scorer.wer(refs, refs) == 0.0`
- [ ] `scorer.wer(refs, [""] * len(refs)) == 1.0`
- [ ] round-trip: baca kembali 20 FLAC acak, cek sample rate 16.000 dan channel 1
- [ ] setiap segmen di bawah 30 detik sehingga muat di Whisper tanpa dipotong lagi

## Keputusan yang sudah diambil — jangan didebat ulang

| Keputusan | Alasan |
|---|---|
| Split dikelompokkan per rekaman, bukan per segmen | Tidak ada kolom speaker; pembagian per segmen membocorkan suara yang sama |
| Buang 41 segmen berdurasi nol atau negatif | Terukur di notebook 01 |
| Jangan pakai `train.tsv` Common Voice | Hanya 4 speaker. Kalau CV dipakai, split dibangun dari `validated.tsv` yang punya 468 speaker |
| Teks latihan default adalah `text_official`, bukan lowercase | Normalizer resmi tidak menyebut case folding |
| Simpan `text_folded` sebagai kolom kedua, bukan pengganti | Pertanyaan diakritik ke penyelenggara belum dijawab |
| Semua audio 16 kHz mono | Syarat Whisper dan XLS-R |
| Padding 0,20 detik | Timestamp berpresisi 1 detik memotong ujung kata |

## Kriteria selesai

Notebook 02 selesai kalau `jember-segments-16k` sudah terbit sebagai Kaggle dataset, `split.csv` dan `lexicon_v1.csv` sudah masuk repo, dan `scorer.py` lulus ketujuh uji validasi diri. Setelah itu **Gate 1 lulus** dan lane A dan B boleh mulai.

## Jebakan

- **Jangan** ekstrak korpus penuh ke disk lokal Windows. Hanya tersisa sekitar 5 GB di drive C. Seluruh pekerjaan audio dilakukan di Kaggle.
- **Jangan** re-run sebagian cell. Cell 1 mereset akumulator `FINDINGS`, jadi run parsial menghasilkan digest yang tidak lengkap.
- `pydub` dan `librosa` memanggil ffmpeg per file; pastikan decode dilakukan sekali per rekaman, bukan sekali per segmen. Selisihnya belasan menit versus berjam-jam.
- Nama file FLAC harus stabil dan bisa diurutkan — pakai indeks segmen dengan padding nol, `63_004` bukan `63_4`.
- Tulis `manifest.csv` dengan `quoting=csv.QUOTE_ALL`. Teksnya mengandung koma dan titik dua.

## Setelah selesai

Lapor ke chat dengan blok handoff, lalu tulis catatan Obsidian `Hasil Notebook 02 - Data Build.md` di vault root. Brief berikutnya: [[nb03-brief-zeroshot-baseline|Brief Notebook 03 - Zero-shot Baseline]].
