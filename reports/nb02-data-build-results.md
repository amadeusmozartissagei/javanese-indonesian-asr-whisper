---
title: "Hasil Notebook 02 — Data Build & Eval Harness (Lost in Transcription)"
aliases:
  - Hasil Notebook 02 - Data Build
  - Hasil Notebook 02
  - Data Build dan Eval Harness
tags:
  - research
  - competition
  - asr
  - dataset
  - eval
status: final
created: 2026-08-25
updated: 2026-08-28
notebook: notebooks/02-data-build.ipynb
verifier: notebooks/02-verify.ipynb
data: findings/02-data-build/dataset_findings.json
gate: "Gate 1 — LULUS 25 Agustus 2026"
source_type: measured-from-data
---

# Hasil Notebook 02 — Data Build & Eval Harness

> [!summary] Ringkasan
> Empat artefak yang menopang seluruh notebook sesudahnya sudah jadi dan **tervalidasi dari kernel terpisah**: audio 16 kHz, manifest, split beku, dan scorer. **Gate 1 lulus.** Tiga hal mengubah asumsi di [[nb02-brief-data-build-eval-harness|Brief Notebook 02 - Data Build dan Eval Harness]]: **padding ternyata mustahil** karena anotasinya kontinu, **pertanyaan diakritik sempat dianggap tidak perlu dijawab** karena ada strategi dominan — itu terbukti salah, dan sejak 28 Agustus target latihannya `text_folded`, bukan `text_official`, dan **audio harus disimpan per rekaman**, bukan per segmen, karena Kaggle memotong dataset di 500 file.
>
> **Ibaratnya:** ini bukan "masak"-nya, ini "prep kitchen"-nya — motong-motong bahan mentah jadi porsi siap pakai, dan mengkalibrasi timbangan dapur (alat penilai) supaya akurat, sebelum satu pun masakan (model) mulai dibuat. Kalau timbangannya salah, semua masakan sesudahnya ikut salah takaran, sekalipun rasanya kelihatan enak.

> [!info] Sifat angka di catatan ini
> Semua diukur dari data asli oleh `notebooks/02-data-build.ipynb` di Kaggle, lalu diperiksa ulang dari mount oleh `notebooks/02-verify.ipynb`. Hasil mentah di `findings/02-data-build/dataset_findings.json` dan `findings/02-verify/verify_report.json`. Seed `20260825`, tercatat di digest.

## Apa yang jadi

| artefak | isi |
|---|---|
| `recordings/*.flac` | **208** file, 16 kHz mono, satu per rekaman utuh, ~630 MB |
| `manifest.csv` | **6.638** baris, 21 kolom — offset sampel, tiga varian teks, asal kata, split, flag |
| `split.csv` | 208 rekaman → `train`/`dev` + kolom `fold` 0–4. **Beku** |
| `lexicon_v1.csv` | 23.803 entri, `jv`/`id`/`both`/`unk`. **Beku** |
| `scorer.py` | normalizer resmi + WER + WER per asal kata + tabel error + bootstrap CI |

Terbit sebagai dataset Kaggle `jember-segments-16k`. Namanya dipertahankan meski isinya rekaman utuh, karena sudah dirujuk brief 03–08.

> [!tip] Cara notebook 03+ membaca satu segmen
> ```python
> y, sr = sf.read(ROOT / r.path, start=r.start_sample, stop=r.end_sample, dtype='float32')
> ```
> Itu *seek* ke dalam FLAC, bukan decode ulang. Konsekuensinya penting: **bounds segmen cuma dua angka di manifest**, jadi keputusan padding bisa diubah saat training tanpa membangun ulang dataset.

## Segmentasi

Dari 6.679 baris TSV: **1 diperbaiki, 41 dibuang, 6.638 terpakai** (9,99 jam dari 10,01 jam audio).

Perbaikannya di `63_002`, tercatat `0:00:40 → 0:00:10`. Karena `end`-nya cocok persis dengan `start` baris berikutnya, yang salah ketik adalah `start`-nya — diperbaiki jadi `0:00:00 → 0:00:10`, dengan penjagaan agar span baru tidak menelan segmen lain. Sisanya 40 berdurasi nol dan 1 tumpang tindih (`63_001`), diselesaikan lewat *interval scheduling* yang membuang segmen sesedikit mungkin. Daftarnya di `dropped_segments.csv`.

### Padding ternyata mustahil, dan itu temuan

> [!danger] Anotasi Jember adalah partisi kontinu
> **Seluruh 6.471 pasang segmen berurutan punya jeda tepat 0 detik.** Segmen n berakhir persis di titik mulai segmen n+1, tanpa kecuali. Timestamp-nya pun 100% detik bulat.

Akibatnya keputusan "padding 0,20 detik, dipotong agar tidak melewati tetangga" itu, dalam praktiknya, **tidak pernah terjadi**: hanya 4 segmen mendapat padding di awal dan 201 di akhir, semuanya di ujung rekaman. Rata-rata konteks yang benar-benar didapat **0,0055 detik dari 0,40 yang diminta** — 1,4%.

Untuk memutuskan apakah itu berbahaya, notebook mengukur energi bicara di 0,2 detik tepat di luar tiap batas, **beserta base rate-nya**:

```
di luar batas segmen : 47,4 %  jendela di atas ambang bicara
di sembarang tempat  : 59,8 %  (base rate, 1,8 juta jendela)
rasio                : 0,79 × base
```

Batas segmen **lebih jarang** jatuh di tengah bicara daripada momen acak. Anotator memang menaruhnya di dekat jeda, meski gridnya kasar. Karena itu `PAD_MODE` dibiarkan `clip_to_neighbour`: menambah 0,2 detik ke 100% klip demi memperbaiki masalah di 47% tepi berarti 53% sisanya dapat suara tetangga yang tidak ada di transkrip — dan itu langsung jadi *insertion*, yang dihitung penuh oleh WER.

> [!note] `PAD_S = 0.20` sekarang inert, bukan aktif
> Klipnya potongan murni `[start, end]`. Jangan ada yang mengira ada bantalan konteks di sana. Padding bersyarat — hanya di tepi yang terbukti ada bicara — adalah ablasi yang layak untuk [[nb07-brief-error-analysis-robustness|Brief Notebook 07 - Error Analysis dan Robustness]], dan sekarang gratis karena audionya per rekaman.

## Teks: tiga aturan yang mengikat semuanya

> [!danger] Koreksi 25 Agustus — bagian ini awalnya salah
> Draf pertama catatan ini (dan `scorer.py` pertama) membaca daftar normalizer penyelenggara sebagai "tidak lowercase, tidak hapus titik". Situs kompetisi dibaca ulang penuh hari yang sama dan **keduanya salah**. Sudah diperbaiki dua kali (lihat [[rules-review-2026-08-23|Kaji Ulang Peraturan - 23 Agustus 2026]]): pertama menambahkan lowercasing + strip titik yang benar, lalu memperbaiki bug idempotency di perbaikan pertama itu sendiri (koma/kutip di antara titik dan huruf berikutnya menghalangi deteksi awal-kalimat pada pass pertama). Ketiga fase notebook sudah di-rerun dan diverifikasi ulang — angka di bawah ini sudah yang benar.

`official_normalize()` menyalin persis daftar penyelenggara:

- **Melakukan lowercase huruf awal kalimat** — huruf pertama transkrip, dan huruf pertama setelah `. ! ? —`, kecuali diikuti huruf kapital lagi (dianggap akronim). Kapitalisasi di tengah kalimat (nama tempat, dsb.) tetap dipertahankan apa adanya.
- **Menghapus titik**, termasuk titik akhir kalimat — **kecuali** elipsis yang menempel di akhir kata (penanda disfluency, mis. `mba...`), yang dipertahankan verbatim. Elipsis berdiri sendiri tetap dihapus seperti sebelumnya.
- **Tidak menghapus tanda hubung** — ini yang tidak berubah, `arek-arek` tetap satu token.

> [!check] Harga kalau teks "dibersihkan" berlebihan: WER 19,15%
> Hipotesis yang lowercase penuh, hapus semua titik, dan lipat diakritik — **tanpa model akustik sama sekali** — kena WER 19,15% dibanding `text_official`. Kesimpulannya waktu itu: target latihan adalah keluaran `official_normalize()` apa adanya. **Sejak 28 Agustus komponen diakritiknya dibatalkan** — target sekarang `text_folded`, lihat bagian diakritik di bawah. Yang tetap berlaku: jangan lowercase penuh dan jangan hapus titik sendiri.
>
> Yang mahal di angka itu **bukan** lowercasing melainkan diakritik: lipat diakritik saja sudah 13,58%, lowercase penuh saja cuma 4,46%, hapus titik saja 1,23%. Dari 468 substitusi, 329 berasal dari diakritik dan 0 adalah kesalahan sungguhan.

> [!warning] Koreksi 26 Agustus — angka 44,5% di draf sebelumnya salah sebabnya
> Draf ini sempat menulis "turun dari 44,5% karena normalizer resmi kini mengerjakan sebagian pembersihan itu sendiri". **Rekonstruksi membantah itu.** Normalizer lama dijalankan ulang dengan resep demo yang sama dan menghasilkan **0,1956**, bukan 0,445 — jadi perbaikan normalizer hanya bernilai **0,4 poin persen**. Angka 44,5% direproduksi persis oleh `wer(text_raw, hyp, normalize=False)`, yaitu membandingkan hipotesis terhadap referensi yang belum dinormalisasi sama sekali. Itu perbaikan **pemanggilan**, bukan perbaikan normalizer. Detail di [[nb02-cross-audit-scorer-text-2026-08-26|Audit Silang - Scorer dan Asumsi Teks (26 Agustus 2026)]].

Normalizer terbukti idempoten di seluruh 6.638 baris — butuh dua percobaan untuk benar-benar terbukti (lihat kotak koreksi di atas), tapi sekarang tervalidasi dari kernel produksi **dan** dari kernel verifikasi terpisah (fase 3, 28/28 lolos, sidik jari 6/6 cocok).

**Charset setelah normalisasi: masih 75 karakter** — ini vocabulary CTC untuk [[nb05-brief-xlsr-ctc-lm|Brief Notebook 05 - XLS-R CTC dan LM]]. Jumlahnya kebetulan sama dengan sebelum perbaikan, tapi komposisinya beralasan berbeda sekarang: huruf kapital yang tersisa (`A`–`Z`) adalah nama diri di tengah kalimat, bukan lagi huruf awal kalimat yang salah tidak di-lowercase. Titik `.` yang tersisa datang dari elipsis menempel, bukan lagi titik akhir kalimat yang seharusnya sudah terhapus. Tanda kutip melengkung dan `…` (80 kemunculan) tidak ada di daftar hapus penyelenggara, jadi ia masuk ke referensi apa adanya. Entah model belajar mengeluarkannya, atau itu WER permanen.

## Diakritik: pertanyaannya tidak perlu dijawab

Ini membatalkan risiko #5 di [[execution-plan|Rencana Eksekusi - Lost in Transcription]].

Angka "10,8% massa token berejaan ganda" dari [[nb01-dataset-analysis|Analisa Dataset - Notebook 01]] benar, tapi **bukan ukuran kerugian**. Di hampir setiap grup satu varian mendominasi telak (`lèk` 815 vs `lek` 2; `bangêt` 209 vs `banget` 1). Model akan belajar bentuk mayoritas; yang hilang cuma kemunculan minoritasnya:

```
massa token ejaan-ganda : 7.087  (10,80 %)
massa varian minoritas  :   562  ( 0,86 %)   ← yang benar-benar tak terselamatkan
```

**0,86%, dan ini lantai keras** — tidak bisa diperbaiki post-processing apa pun, karena letaknya di *referensi*, bukan di hipotesis.

Token yang mengandung diakritik: 14,3%. Matriksnya jadi timpang:

| kita latih dengan | penyelenggara **tidak** melipat | penyelenggara **melipat** |
|---|---|---|
| **`text_official`** | rugi **0,86 %** | rugi **0 %** |
| `text_folded` | rugi hingga **14,3 %** | rugi 0 % |

> [!check] ~~Keputusan 25 Agustus: latih dengan `text_official`~~ — DIBATALKAN, lihat di bawah
> Alasannya waktu itu: strategi dominan, menang atau seri di setiap kemungkinan. Premisnya ternyata salah.

> [!danger] TERTUTUP 28 Agustus — matriks di atas SALAH, dan keputusannya berbalik
> Kedua kolomnya mengandaikan referensi resmi ditulis berdiakritik seperti Jember. Dev set resmi sekarang ada di repo dan membantah itu: **0,30% token berdiakritik, dan satu-satunya diakritik adalah `é`** — nol `ê`, nol `è`, nol `ě`. Dari 9.385 token berdiakritik Jember, **0,0% muncul di dev resmi apa adanya, 69,4% muncul setelah dilipat** (`těrus`→`terus`, yang muncul 225× di sana).
>
> **Target latihan adalah `text_folded`, bukan `text_official`.** Latih berdiakritik → rugi hingga 14,3%; latih terlipat → rugi 0,30%. Kolomnya sudah ada di manifest dan sudah diverifikasi, jadi ini satu baris di NB 04 dan **tidak perlu rerun NB 02**. Konsekuensi lain: **M1 di brief 06 hidup kembali dan M2 gugur.** Bukti lengkap di [[official-dev-set-analysis-2026-08-28|Analisa Dev Set Resmi - 28 Agustus 2026]].

Konsekuensi untuk [[nb06-brief-data-mixing|Brief Notebook 06 - Data Mixing]] **terbalik sejak 28 Agustus**: **M1 (ruang terlipat) justru yang benar**, dan **M2 (diakritisasi transkrip TTS) gugur** — tidak ada gunanya menambahkan diakritik yang tidak dipakai referensi resmi. Ini juga membuat transkrip TTS yang memang polos langsung kompatibel, tanpa pekerjaan diakritisasi sama sekali.

## Leksikon asal kata

23.803 entri dari Common Voice (proksi Indonesia), TTS Central Javanese (proksi Jawa), dan 51 penanda Jawa berfrekuensi tinggi. Perbandingan dilakukan dalam bentuk terlipat.

| kelas | massa token Jember | tipe |
|---|---|---|
| `jv` | **39,2 %** | 4.272 |
| `both` | **27,9 %** | 2.117 |
| `unk` | 18,7 % | 4.039 |
| `id` | 14,2 % | 13.375 |

> [!warning] Baca "WER kata Jawa" bersama jumlah tokennya
> `wer_jv` hanya mencakup 39% token dan `wer_id` hanya 14%. Kelas `both` yang 27,9% itu bukan kegagalan pengukuran — batas leksikal Jawa–Indonesia memang kabur, dan penyelenggara sendiri menyebutkannya. Gunanya leksikon ini konsistensi, bukan linguistik. **Beku**: versi berikutnya harus bernama `lexicon_v2`.

`jv_ratio = n_jv / (n_jv + n_id)`, median **0,75**. 213 segmen tidak punya token `jv` maupun `id` sehingga rasionya kosong — notebook 03+ harus menanganinya.

## Split beku

Dikelompokkan per **rekaman**, bukan segmen, karena TSV Jember tidak punya kolom speaker. Stratifikasi pada median `jv_ratio` × durasi rekaman, seed `20260825`.

| | rekaman | segmen | jam | jv_ratio median |
|---|---|---|---|---|
| train | 188 | 5.541 | 8,36 | 0,75 |
| dev | **20** | **1.097** | **1,63** | 0,75 |

Dev = 16,3% durasi (target 15%). Lima fold tersedia di kolom `fold`, masing-masing ~2,0 jam, belum dipakai.

### Dua lantai WER yang harus diingat

> [!danger] Dev tidak bisa turun ke nol, dan tahu batasnya penting
> - **11,8% token dev** adalah kata yang **tidak pernah muncul di train** (808 tipe). Model tidak bisa menebaknya.
> - **0,86%** dari inkonsistensi ejaan di atas.

### Resolusi dev set

Diukur dengan bootstrap yang me-resample **ujaran**, bukan token — karena token dalam satu kalimat gagal berbarengan:

```
WER 16,4 %  →  95% CI ± 0,72 poin
WER 26,8 %  →  95% CI ± 0,77 poin
dev: 1.097 ujaran, 10.394 token referensi
```

> [!check] Selisih WER di bawah ~1,5 poin tidak terbukti dari satu run
> Ini memberi **Gate 2** definisi operasional: "fine-tune mengalahkan zero-shot" berarti selisihnya lewat ambang itu, atau dikonfirmasi `scorer.compare_systems()` — uji berpasangan yang jauh lebih peka daripada membandingkan dua CI. Biayanya nol GPU. Pakai itu sebelum membayar seed kedua.

## Scorer

```
official_normalize / fold_diacritics / lex_key / tokenize
wer / wer_by_origin / error_table
wer_ci / compare_systems          ← di luar permintaan brief
```

Stdlib saja; `jiwer` hanya untuk cek silang kalau kebetulan terpasang, `pandas` hanya agar `error_table` mengembalikan DataFrame. `wer_by_origin` mengatribusikan substitusi dan deletion ke kelas asal **token referensi**; insertion tidak punya token referensi sehingga dilaporkan global dan sebagai daftar frekuensi — tidak dipaksa masuk kelas mana pun.

## Verifikasi independen (fase 3)

`02-verify` jalan di kernel bersih terhadap dataset yang **sudah terbit**, dan meng-import `scorer.py` dari mount, bukan membawa salinan. **28/28 lolos.**

Yang paling berarti: **sidik jari 6/6 cocok** dengan pass yang direview, jadi artefak yang terbit terbukti byte-per-byte sama dengan yang angkanya disepakati. Ditambah: tidak ada segmen yang menunjuk sampel melewati akhir rekamannya — kegagalan yang akan ditimbulkan upload terpotong.

### Clipping: 5 rekaman berurutan

| | |
|---|---|
| segmen dengan >1% sampel mentok | **54** (0,81%) |
| rekaman terdampak | **194, 195, 196, 197, 198** |
| di dev | 7 segmen (0,64% dev) |

Rekamannya **berurutan** — satu sesi dengan gain kesetel terlalu tinggi. Itu properti sumber mp3, bukan cacat konversi (bug konversi akan merata di 208 rekaman). Republish tidak akan memperbaikinya. Dicatat agar [[nb07-brief-error-analysis-robustness|Brief Notebook 07 - Error Analysis dan Robustness]] bisa memeriksa apakah segmen ini menyumbang error lebih dari jatahnya.

## Alur tiga fase

Notebook ini dijalankan tiga kali, dan polanya berlaku untuk notebook mana pun yang outputnya besar:

| fase | saklar | output |
|---|---|---|
| 1 — review | `WRITE_AUDIO = False` | beberapa MB, diunduh utuh, angkanya direview |
| 2 — produksi | `WRITE_AUDIO = True` | ~630 MB, terbit server-side, tidak pernah diunduh |
| 3 — verifikasi | `02-verify.ipynb` | beberapa ratus KB |

Fase 1 dan 2 wajib satu file dengan satu saklar: dua notebook produsen akan melenceng, dan artefak yang direview berhenti jadi artefak yang dipakai. Fase 3 wajib file terpisah: dia konsumen, dan **ketidak-tergantungannya pada produsen itulah yang sedang diuji**. Sidik jari sha256 yang mengikat ketiganya.

> [!note] Pelajaran ongkos
> Percobaan pertama menerbitkan 6.638 klip **gagal** — Kaggle memotong di 500 file. Perpindahan ke 208 rekaman menyelesaikannya sekaligus memberi keuntungan yang tidak diminta: keputusan padding jadi parameter dataloader, bukan artefak beku.

## Yang dibawa ke notebook berikutnya

- [ ] Target latihan **`text_official`** apa adanya — sudah lowercase-awal-kalimat dan sudah bebas titik (kecuali elipsis menempel) dari normalizer resmi sendiri. Jangan proses ulang, jangan hapus tanda hubung.
- [ ] Baca segmen lewat `sf.read(start=, stop=)`. Jangan decode ulang mp3.
- [ ] `split.csv` beku. Jangan pernah diregenerasi.
- [ ] Selisih WER < ~1,5 poin belum terbukti. Pakai `compare_systems()`.
- [ ] Ingat dua lantai: 11,8% (kata khusus dev) dan 0,86% (ejaan).
- [ ] Charset 75 karakter siap jadi vocabulary CTC di NB 05.
- [ ] NB 06: **M2 gugur, kerjakan M1** (terbalik 28 Agustus — lihat [[official-dev-set-analysis-2026-08-28|Analisa Dev Set Resmi - 28 Agustus 2026]]).
- [ ] NB 07: periksa 54 segmen clipped, dan ablasi padding bersyarat.

Brief berikutnya: [[nb03-brief-zeroshot-baseline|Brief Notebook 03 - Zero-shot Baseline]].
