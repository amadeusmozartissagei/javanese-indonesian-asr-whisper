---
title: "Hasil Notebook 06 — Data Mixing (Lost in Transcription)"
aliases:
  - Hasil Notebook 06 - Data Mixing
  - Hasil Notebook 06
  - Data Mixing
tags:
  - research
  - competition
  - asr
  - data-mixing
  - gate4
status: final
created: 2026-09-07
updated: 2026-09-07
notebook: notebooks/06-data-mixing.ipynb
build_notebook: notebooks/06-mix-build.ipynb
verify_notebook: notebooks/06-mix-verify.ipynb
data: findings/06-data-mixing-E4/dataset_findings.json
source_type: measured-from-data
---

# Hasil Notebook 06 — Data Mixing

> [!success] Gate 4 — LOLOS. Kandidat submission dibekukan: **E4**
> Jember + Common Voice Indonesia terkurasi, pencampuran datar, 1 epoch. Dev resmi 372 klip: **0,2532 → 0,2312**, paired bootstrap CI [−0,0276, −0,0165], p(better) 1,000. Satu-satunya arm yang **lolos ketiga aturan pemilihan**.
>
> Bobot: `amozaurus/mozilla-jv-06-data-mixing-E4` @ `c79347a5` (privat, 3,24 GB, 7 file).
>
> **Ibaratnya:** karyawan tadinya cuma dilatih rekaman rapat Jember, jadi jago dialek tapi mulai salah dengar kalimat Indonesia biasa. Ditambahi latihan bacaan Indonesia yang bersih — dan bukan cuma sisi Indonesianya membaik, sisi Jawanya juga ikut naik.

> [!danger] Tiga hal yang harus dibaca sebelum memakai angka mana pun di catatan ini
> **1. Angka jujurnya 0,2336, bukan 0,2312.** 150 dari 372 klip dev resmi dipakai untuk memilih checkpoint. Di 222 klip yang **tidak pernah tersentuh pemilihan**, E4 mendapat **0,2336**. Selisih 0,0024 itu persis harga kontaminasi pemilihan. Kemenangan atas NB 04 tetap terbukti di sampel bersih ini: −0,0187, CI [−0,0261, −0,0117], p 1,000.
>
> **2. E4 dan E6 tidak terpisahkan pada WER.** Di 372 klip: delta −0,0023, CI [−0,0070, +0,0024], p 0,816. Di 222 klip bersih: delta −0,0006, p 0,567 — praktis imbang. **E4 dipilih bukan karena WER-nya lebih kecil**, melainkan karena lolos 3/3 aturan (E6 2/3), `jv_to_id`-nya lebih rendah, dan runnya 1,36 jam lawan 2,26 jam.
>
> **3. E5 (curriculum) TIDAK PERNAH DIUJI.** Tahap B gagal mengunduh bobot tahap A — `RESUME_FROM_HF is on but no usable checkpoint came down. Starting fresh.` Jadi ia hanya melatih Jember dari model dasar. Dua angka E5 di bawah menjelaskan komponennya, **bukan** curriculumnya. Jangan tulis "curriculum kalah" di laporan mana pun.

> [!info] Sifat angka di catatan ini
> Enam run GPU, semuanya Kaggle T4 tunggal, resep NB 04 tidak diubah sedikit pun: `whisper-large-v3-turbo`, token `jw`, target `text_folded`, `SEGMENT_MODE="concat25"`, 1 epoch, lr 6e-06, batch efektif 16, adafactor, decode greedy `no_repeat_ngram_size=4`, `LONG_MODE="chunk"`, `GEN_MAX_LENGTH=225`. **Satu-satunya variabel yang berubah antar-arm adalah komposisi data.** Pembanding NB 04 bukan diambil dari catatannya, melainkan prediksi per-klipnya ikut dimuat sebagai dataset (`nb04-baseline`) sehingga setiap klaim "lebih baik" adalah paired bootstrap, bukan perbandingan dua CI yang berdiri sendiri. Pemilihan checkpoint memakai **dev resmi**, bukan dev Jember — NB 04 membuktikan dev Jember antikorelasi.

## Enam arm, satu tabel

Dev resmi 372 klip, 17.473 token referensi. Pembanding: fine-tune Jember-saja dari NB 04 (`04-whisper-core-full-concat25-1epoch`).

| arm | komposisi | item | step | jam | WER | WER jv | WER id | `jv_to_id` | aturan | vonis |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|---|
| zero-shot | — | — | — | — | 0,2695 | 0,4370 | 0,1836 | 33,03% | — | — |
| NB 04 | Jember saja | 1.455 | 91 | 0,68 | 0,2532 | 0,2513 | 0,2058 | 14,31% | — | pembanding |
| **E4** | **+ CV terkurasi** | **2.639** | **165** | **1,36** | **0,2312** | **0,2393** | **0,1716** | **15,22%** | **3/3** | **KEEP** |
| E6 | + CV, Jember 2× | 4.094 | 256 | 2,26 | 0,2336 | 0,2347 | 0,1821 | 17,63% | 2/3 | drop |
| E3 | + 90 item CV aksen Jawa | 1.545 | 97 | 0,95 | 0,2408 | 0,2450 | 0,1923 | 16,37% | 3/3* | kalah dari E4 |
| E5-B | Jember saja (curriculum gagal) | 1.455 | 91 | 0,68 | 0,2586 | 0,2559 | 0,2045 | 15,61% | 0/3 | drop |
| E5-A | CV saja (tahap 1 curriculum) | 1.184 | 74 | 0,49 | 0,2591 | 0,4638 | 0,1559 | 35,45% | 0/3 | drop |

E1 (TTS Central Javanese) **tidak dijalankan**. Alasannya di bagian [[#E1 dibatalkan, dan itu keputusan berdasar bukti|E1 dibatalkan]].

\* Kolom "aturan" dihitung ulang dengan perumusan aturan 3 yang berlaku sekarang, per token referensi dengan pita derau ±9,6 — bukan angka yang tercetak di `results.csv` tiap arm, karena E3 dan E5-A berjalan sebelum perumusan itu ada. Hitungan penuhnya:

| arm | `n_jv_to_id` | per 17.473 token | selisih dari NB 04 | aturan 3 |
|---|---:|---:|---:|---|
| NB 04 | 92 | 0,5265% | — | pembanding |
| **E4** | **95** | 0,5437% | **+3** | **lolos** (marginal) |
| E3 | 101 | 0,5780% | +9 | **lolos** (marginal) |
| E5-B | 103 | 0,5895% | +11 | gagal |
| E6 | 107 | 0,6124% | +15 | gagal |
| E5-A | 374 | 2,1404% | +282 | gagal telak |

> [!warning] Vonis `drop` E3 di `results.csv` sudah kedaluwarsa
> E3 dinilai dengan aturan 3 versi lama (persentase substitusi Jawa, 14,31% → 16,37%) dan gagal karenanya. Di bawah aturan yang berlaku sekarang **E3 lolos 3/3**. Yang tidak berubah adalah nasibnya: E3 kalah dari E4 secara terbukti (−0,0096, CI [−0,0146, −0,0044], p 1,000). **E3 kalah karena didominasi, bukan karena didiskualifikasi** — dan itu perbedaan yang penting kalau angkanya masuk laporan.

## E4 memperbaiki persis apa yang dirusak NB 04

Ini temuan utama notebook ini. NB 04 mendiagnosis kegagalannya sebagai **regresi sisi Indonesia**: fine-tune Jember memperbaiki Jawa besar-besaran tapi menaikkan WER Indonesia dari 0,1836 (zero-shot) ke 0,2058. Pertanyaan yang ditulis di `mix_spec_E4.json` sebelum run dimulai: *"Does curated Common Voice repair the Indonesian regression?"*

Jawabannya ya — dan lebih dari sekadar memperbaiki.

| metrik | zero-shot | NB 04 | **E4** | E4 − NB 04 |
|---|---:|---:|---:|---:|
| WER total | 0,2695 | 0,2532 | **0,2312** | **−0,0220** |
| WER Indonesia | 0,1836 | 0,2058 | **0,1716** | **−0,0342** |
| WER Jawa | 0,4370 | 0,2513 | **0,2393** | −0,0120 |
| WER dua-bahasa | 0,1609 | 0,1379 | **0,1130** | −0,0249 |
| WER tak dikenal (`unk`) | 0,4253 | 0,4057 | **0,3873** | −0,0184 |
| `jv_to_id` | 33,03% | 14,31% | 15,22% | +0,91 |
| deletion rate | 0,0607 | 0,0224 | 0,0161 | −0,0063 |
| insertion rate | 0,0207 | 0,0395 | 0,0422 | +0,0027 |
| rasio panjang hyp/ref | 0,9599 | 1,0171 | 1,0261 | +0,0090 |
| hipotesis mengandung digit | 16,40% | 2,42% | 1,34% | −1,08 |

> [!check] WER Indonesia turun **di bawah zero-shot**, bukan sekadar pulih
> 0,2058 → 0,1716, sementara zero-shot 0,1836. Jadi CV bukan hanya menambal kerusakan yang dibuat fine-tune Jember; ia membawa sisi Indonesia lebih jauh dari titik awalnya. **Dan tidak ada yang dibayar untuk itu** — WER Jawa juga turun. Ini bukan pertukaran, ini kenaikan di keempat kelas token sekaligus.

> [!warning] Kelas `unk` akhirnya bergerak, sedikit
> NB 04 mencatat `unk` sebagai satu-satunya kelas yang nyaris tidak pernah bergeser padahal memegang 22% massa error. E4 menurunkannya 0,4057 → 0,3873. Nyata, tapi kecil: kelas ini tetap yang paling buruk dan tetap target utama NB 07. Tak satu pun dari tiga korpus tambahan menyentuh kosakata yang duduk di kelas ini.

## E4 lawan E6: yang memutuskan bukan WER

Dua arm ini memakai campuran yang **identik** — 1.184 item CV yang sama, `struct_hash` yang sama. Bedanya cuma satu: E6 mengulang setiap item Jember dua kali agar data in-domain tidak kalah suara.

Paired bootstrap 2.000 resample:

| perbandingan | dari | ke | delta | CI 95% | p(B lebih baik) |
|---|---:|---:|---:|---|---:|
| NB 04 → E4 | 0,2532 | 0,2312 | −0,0220 | [−0,0276, −0,0165] | 1,000 |
| NB 04 → E6 | 0,2532 | 0,2336 | −0,0196 | [−0,0250, −0,0139] | 1,000 |
| NB 04 → E3 | 0,2532 | 0,2408 | −0,0124 | [−0,0170, −0,0079] | 1,000 |
| E3 → E4 | 0,2408 | 0,2312 | −0,0096 | [−0,0146, −0,0044] | 1,000 |
| **E6 → E4** | **0,2336** | **0,2312** | **−0,0023** | **[−0,0070, +0,0024]** | **0,816** |

Baris terakhir memuat nol. Di 222 klip yang tidak pernah dipakai memilih checkpoint, jaraknya menyusut lagi jadi −0,0006 dengan p 0,567 — itu lemparan koin. **Pada WER, kedua arm ini adalah sistem yang sama.**

Jadi keputusannya jatuh ke tiga hal lain, dan ketiganya menunjuk arah yang sama:

1. **Aturan 3.** E6 menaikkan `jv_to_id` dari 92 ke 107 token dari 17.473 — di luar pita derau ±9,6. E4 naik ke 95, di dalam pita. E6 gagal, E4 lolos.
2. **`jv_to_id` absolut.** 17,63% lawan 15,22%. E6 lebih sering menerjemahkan alih-alih mendengar, dan test set-nya bukan bahasa Indonesia.
3. **Biaya.** 2,26 jam lawan 1,36 jam untuk hasil yang tak terbedakan. Upsampling membeli 91 step tambahan dan tidak membeli apa pun selain itu.

> [!tip] Yang sebenarnya dibuktikan E6
> Kekhawatiran "data in-domain akan tenggelam kalau ditambahi 6,5 jam read speech" — yang jadi alasan E6 ditulis — **tidak terbukti**. Rasio 1:1 tidak lebih baik dari rasio apa adanya. Itu hasil negatif yang layak ditulis: pada skala ini, melindungi data in-domain dengan pengulangan hanya menambah biaya.

## E3: murah, nyata, tapi kalah telak

439 klip Common Voice yang kolom aksennya berlabel Jawa, menyusut jadi 90 item setelah dikurasi dan disambung — 0,54 jam, satu arm termurah di seluruh notebook. Ia **berhasil**: 0,2532 → 0,2408, terbukti.

Dihitung ulang dengan aturan 3 yang berlaku sekarang, E3 **lolos ketiganya** — jadi ia arm kedua yang sah, bukan arm yang gugur. Tapi E4 mengalahkannya secara terbukti (−0,0096, CI [−0,0146, −0,0044], p 1,000).

Kesimpulannya bersih: **yang menolong bukan aksen Jawa-nya, melainkan bahasa Indonesianya.** 0,54 jam aksen Jawa memberi separuh perbaikan yang diberi 6,53 jam CV umum. Kalau kedekatan aksen yang jadi mesinnya, urutannya akan terbalik.

> [!tip] E3 adalah cadangan yang layak, dan itu ada gunanya
> Ia lolos tiga aturan, hanya butuh 0,54 jam data tambahan dan 0,95 jam GPU, serta memakai porsi Common Voice yang paling kecil dan paling mudah dipertanggungjawabkan asal-usulnya. Kalau NB 08 menemukan masalah lisensi, ukuran, atau reproduksi pada porsi CV besar E4, E3 adalah mundur satu langkah yang tetap mengalahkan NB 04 secara terbukti.

## E5: curriculum tidak pernah diuji, dan dua angkanya tetap berguna

Rencananya: tahap A melatih di campuran saja, tahap B melanjutkan dari bobot itu di Jember saja. Tahap B tidak pernah menerima bobot tahap A. `run-log.txt` baris 167 mencatatnya apa adanya, dan run tetap jalan dari model dasar. Guard yang menolak resume-yang-diminta-tapi-tidak-terjadi baru ditambahkan **setelah** ini terjadi.

Dua angkanya tetap mengajari sesuatu:

**E5-A (CV saja, 0,2591).** Ini yang terjadi kalau model dilatih read speech Indonesia tanpa Jember sama sekali: WER Indonesia terbaik di seluruh notebook (**0,1559**) dan WER Jawa terburuk (**0,4638**, praktis sama dengan zero-shot 0,4370). `jv_to_id` melonjak ke 35,45%, lebih tinggi dari zero-shot. Model itu berhenti mendengar bahasa Jawa dan mulai menuliskannya sebagai bahasa Indonesia. **Ini kalibrasi yang bagus untuk aturan 2 dan 3:** memperlihatkan seperti apa bentuk kegagalan yang dijaga dua aturan itu.

**E5-B (Jember saja, 0,2586).** Data, jadwal, dan seed identik dengan run 1-epoch NB 04 — 1.455 item, 91 step, seed 20260829. Bedanya hanya **lapisan tempat checkpoint dipilih**: NB 04 memilih di dev Jember (dapat step 75), E5-B di dev resmi (dapat step 50). Hasilnya 0,2586 lawan 0,2532.

> [!warning] Selisih 0,0054 itu adalah goyangan pemilihan checkpoint, dan ia lebih besar dari jarak E4–E6
> Konfigurasi yang sama persis, hanya beda titik eval yang dipilih, sudah menggeser WER dev resmi sebanyak 0,0054. Jarak E4 ke E6 hanya 0,0023. Ini alasan kuantitatif kenapa dua arm itu tidak boleh diurutkan berdasarkan WER — dan pengingat bahwa memilih di dev resmi bukan jaminan angka yang lebih baik, hanya angka yang lebih jujur arahnya.

## Kurva E4 masih turun saat epoch habis

Diukur pada subset kurva 150 klip selama training:

| step | epoch | WER | WER jv | WER id | `jv_to_id` |
|---:|---:|---:|---:|---:|---:|
| 25 | 0,15 | 0,2430 | 0,2810 | 0,1560 | 19,19 |
| 50 | 0,30 | 0,2556 | 0,2757 | 0,1920 | 16,50 |
| 75 | 0,46 | 0,2433 | 0,2469 | 0,1916 | 17,05 |
| 100 | 0,61 | 0,2394 | 0,2469 | 0,1868 | 14,94 |
| 125 | 0,76 | 0,2295 | 0,2356 | 0,1707 | 17,90 |
| **150** | **0,91** | **0,2276** | **0,2312** | **0,1655** | **15,87** |

> [!danger] Ini membalik pola NB 04, dan menyisakan satu tuas yang belum ditarik
> NB 04 menemukan hampir seluruh manfaat datang dalam 25 step pertama, lalu kurvanya datar. **Dengan campuran, kurvanya tidak datar** — titik terbaik adalah titik terakhir, dan tren 100 → 125 → 150 masih menurun saat epoch habis. Artinya E4 kemungkinan besar **belum konvergen**, dan epoch kedua adalah eksperimen paling murah yang tersisa untuk NB 07. Biayanya sekitar 1,4 jam. Catatan jujur: ini ekstrapolasi dari kurva, bukan hasil terukur.

## Aturan pemilihan, dan kenapa aturan 3 dirumuskan ulang

Aturan 3 semula berbunyi "`jv_to_id` tidak naik", diukur sebagai persentase substitusi Jawa. Masalahnya: penyebutnya adalah jumlah substitusi Jawa, yang **ikut mengecil setiap kali model membaik**. Model yang lebih baik bisa terlihat gagal aturan 3 hanya karena ia membuat lebih sedikit kesalahan secara keseluruhan.

Perumusan ulang: hitung `jv_to_id` sebagai **jumlah token per 17.473 token referensi**, dengan pita derau ±√n. Penyebutnya jadi konstan.

> [!check] Perumusan ulang ini dilakukan **sebelum** E4 dijalankan, dan E4 hampir gagal karenanya
> Ini yang membedakannya dari menggeser gawang. E4 naik dari 92 ke 95 token — di dalam pita ±9,6, tapi tetap kenaikan, dan `keep_rules.json` menandainya `MARGINAL`. Kalau aturan ini disusun untuk meloloskan E4, ia tidak akan menyisakan tanda itu. **E6 (+15) dan E5-B (+11) tetap gagal** di bawah perumusan baru, dan E5-A (+282) gagal telak — jadi aturannya masih menolak empat dari enam arm.

Ketiga aturan untuk E4, apa adanya dari `keep_rules.json`:

| # | aturan | detail | |
|---|---|---|:---:|
| 1 | `wer_total` turun melebihi CI | 0,2532 → 0,2312, CI [−0,0276, −0,0166] | ✅ |
| 2 | `wer_jv` tidak memburuk | 0,2513 → 0,2393 | ✅ |
| 3 | `jv_to_id` tidak naik (per token referensi) | 0,5265% → 0,5437% (92 → 95 dari 17.473, pita ±9,6) — MARGINAL | ✅ |

## Dua FAIL self-validation yang ternyata bug pemeriksanya, bukan bug datanya

Run E4 melaporkan 19/21. Keduanya diselidiki sampai ke data, dan keduanya adalah pemeriksa warisan NB 04 yang tidak selamat pindah rumah.

**FAIL 1 — "training target is text_folded of exactly the segments it covers", `1 items verified; first mismatch: cv_6fc4f5a146cc_i0532`.** Pemeriksa itu mencocokkan setiap item ke `MANIFEST`, yaitu tabel segmen **Jember**, yang tidak tahu apa-apa soal shard campuran. Item CV pertama yang ditemuinya menghasilkan nol baris, lalu dinyatakan tidak cocok. Klaimnya sendiri diperiksa ulang secara lokal terhadap `shards/_meta/clips.csv`: item `cv_6fc4f5a146cc_i0532` punya 3 klip, dan teksnya **persis** gabungan teks ketiga klip itu berurutan. Diperiksa untuk **seluruh 1.184 item campuran E4**, bukan sampel — nol ketidakcocokan.

**FAIL 2 — "checkpoint selection used dev WER, not loss", `official_wer`.** Daftar putihnya masih `("wer", "eval_wer")` warisan NB 04, sementara `SELECT_ON="official"` mengganti nama metriknya jadi `official_wer`. Jadi run yang **dikonfigurasi dengan benar** justru gagal pemeriksaan itu. Pemeriksa berikutnya — "checkpoint selected on the official dev, not the Jember dev" — menegaskan hal yang benar dan LOLOS.

Keduanya sudah diperbaiki di `notebooks/06-data-mixing.ipynb` (7 September):

- Pemeriksa target dipecah dua: bagian Jember tetap dicocokkan ke `MANIFEST`, bagian campuran ke tabel klip milik campuran sendiri di mount yang benar-benar dilatih — sehingga dataset yang tertukar atau basi tetap tidak bisa lolos.
- Daftar putih metrik diperluas ke `official_wer` / `eval_official_wer`.

> [!info] Angka E4 tidak perlu dihitung ulang
> Kedua FAIL itu ada di lapisan pelaporan, bukan di jalur data maupun jalur training. Klaim yang mereka wakili sudah dibuktikan terpisah — bagian campuran oleh verifier fase 3 NB 06 atas seluruh item campuran plus `struct_hash`, dan diulang lokal atas 1.184 item E4; pemilihan checkpoint oleh pemeriksa tetangganya yang lolos.

## E1 dibatalkan, dan itu keputusan berdasar bukti

Brief awal menempatkan TTS Central Javanese sebagai arm pertama, dengan alasan cakupan kosakatanya lebih tinggi per jam (56,2% dalam 7,89 jam, lawan 41,5% dalam 35,94 jam untuk CV). NB 04 membalik premis itu: kegagalan yang terukur ada di **sisi Indonesia**, dan TTS adalah tambahan read speech **berbahasa Jawa** — memperdalam distorsi yang sudah ada, bukan menambalnya.

Lima arm berikutnya mengonfirmasi arah itu dengan angka:

- Setiap arm yang menang menang lewat **WER Indonesia** (E4 −0,0342, E6 −0,0237, E3 −0,0135).
- E5-A memperlihatkan versi ekstremnya: Indonesia murni memberi WER Indonesia terbaik yang pernah diukur di proyek ini.
- E3 memperlihatkan bahwa kedekatan aksen Jawa **bukan** mesinnya.

Menjalankan E1 berarti membelanjakan sekitar 1,5 jam GPU untuk menguji hipotesis yang sudah ditolak tiga kali dari arah berbeda. **Keputusan: E1 tidak dijalankan.** Kalau tim ingin tetap menjalankannya untuk kelengkapan laporan, biayanya murah dan notebooknya siap — tapi ia bukan jalan menuju WER yang lebih rendah.

M2 (diakritisasi TTS) dan M3 (adaptasi encoder saja) ikut gugur bersama E1: keduanya adalah cara mengintegrasikan TTS, dan M2 secara khusus sudah gugur sejak 28 Agustus ketika dev resmi terbukti tidak memakai diakritik sama sekali.

## Kandidat yang dibekukan

| | |
|---|---|
| repo | `amozaurus/mozilla-jv-06-data-mixing-E4` (privat) |
| revision | `c79347a54d8523f9876cfbf17bd7ea217d1db800` |
| ukuran | 3,24 GB, 7 file |
| `model.safetensors` | sha256[:16] `c58b0538dc4c2008` |
| checkpoint | step 150 dari 165, dipilih di dev resmi |
| base | `openai/whisper-large-v3-turbo` |
| decode | greedy, `no_repeat_ngram_size=4`, `max_length=225`, `LONG_MODE="chunk"` (28 s, overlap 2 s) |
| bahasa | token `jw` |
| WER dev resmi | **0,2312** (372 klip) / **0,2336** (222 klip bersih) |
| wall clock | 1,36 jam, T4 tunggal |

Komposisi latihnya, bisa direproduksi dari `findings/06-mix-build/mix_manifest_E4.csv`:

- **Jember train** 1.455 item, 8,36 jam, `concat25`, tanpa upsampling
- **Common Voice Indonesia terkurasi** 1.184 item, 6,53 jam, 283 speaker, speaker terbesar memegang 3,64% jam
- Kebijakan kurasi: buang `down_votes >= 1`, deduplikasi kalimat, maksimum 100 klip per speaker, klip beraksen Jawa selalu dipertahankan, kalimat berdigit dibuang, minimum 2 kata, disambung ke item ~25 detik
- `struct_hash` `8640e1cf…` — sidik jari yang sama dengan yang ditinjau di fase 1 NB 06

## Yang diwariskan ke NB 07 dan NB 08

> [!check] Jangan diturunkan ulang
> 1. **Kandidat submission adalah E4.** Semua perbandingan NB 07 dipatok ke sana, bukan ke NB 04.
> 2. **Angka acuan bersih adalah 0,2336** (222 klip yang tidak menyentuh pemilihan). Pakai ini kalau NB 07 memilih checkpoint lagi di dev resmi, supaya tidak menumpuk kontaminasi.
> 3. **Upsampling tidak membantu.** Jangan diulang.
> 4. **Kedekatan aksen bukan mesin perbaikan; bahasa Indonesia adalah mesinnya.** Setiap ide penambahan data harus dinilai dengan pertanyaan itu.
> 5. **Kelas `unk` masih 0,3873 dan tidak tersentuh korpus mana pun.** Ini target terbesar yang tersisa.

Yang masih terbuka, diurut berdasarkan rasio bukti terhadap biaya:

| | tuas | biaya | dasar |
|---|---|---|---|
| 1 | Epoch kedua untuk E4 | ~1,4 jam | Kurva masih menurun di step terakhir |
| 2 | Curriculum E5, kali ini dengan hub menyala | ~1,2 jam | Belum pernah benar-benar diuji |
| 3 | E1 (TTS) untuk kelengkapan laporan | ~1,5 jam | Sudah ditolak dari tiga arah; bukan jalan ke WER lebih rendah |

## Catatan operasional yang mahal dipelajari

- **`HF_TOKEN` adalah secret per-notebook di Kaggle, bukan per-akun.** Lima arm pertama selesai training lalu kehilangan bobotnya karena token tidak terpasang di notebook itu. Sekarang ada guard yang menolak `RUN_MODE="train"` tanpa hub.
- **Early stopping memotong run 1-epoch.** Satu run E4 berhenti di step 100 dari 165 dengan patience habis, lalu `load_best_model_at_end` memulihkan bobot **step 25** — sepertiga jadwal. Angkanya (0,2344) sempat terbaca sebagai derau antar-run padahal ia adalah model yang berbeda. `EARLY_STOP = False` sekarang default; pada jadwal satu epoch, patience 3 lebih cepat habis daripada trainingnya selesai.
- **`RUN_NOTE` harus diisi sebelum mengulang arm**, atau folder hasilnya tertimpa. Prediksi per-klip E4 run pertama hilang karena ini.
- **Bundle `-lite.zip` hasil publish Kaggle menciptakan salinan metadata ganda** di dalam dataset yang diterbitkan. Verifier fase 3 memilih kandidat `items.csv` berdasarkan jumlah `.flac` di bawah root-nya, bukan berdasarkan kedalaman path.

## Lampiran — reproduksi

Semua angka di catatan ini bisa dihitung ulang dari file yang ada di repo, tanpa GPU. Muat `scorer.py` dari `findings/02-data-build/`, normalisasi referensi `metadata.tsv` dan hipotesis tiap arm dengan `scorer.official_normalize`, lalu jalankan `scorer.compare_systems(refs, hyps_a, hyps_b, n_boot=2000, seed=20260829)`.

Subset pemilihan 150 klip direkonstruksi dengan `O.sample(n=150, random_state=20260829)` atas `metadata.tsv` dalam urutan file. Rekonstruksi itu terverifikasi: WER E4 di subset hasil rekonstruksi adalah 0,2276, angka yang sama persis dengan `best_eval_wer` dan titik step-150 pada kurva notebook.

Mentah per arm: `findings/06-data-mixing-{E3,E4,E5-A,E5-B,E6}/`. Campuran dan manifesnya: `findings/06-mix-build/`. Verifikasi struktural campuran: `findings/06-mix-verify/`.

Berikutnya: [[nb07-brief-error-analysis-robustness|Brief Notebook 07 - Error Analysis dan Robustness]] dan [[nb08-brief-packaging-submission|Brief Notebook 08 - Packaging dan Submission]].
