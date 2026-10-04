---
title: "Brief Notebook 06 — Data Mixing"
aliases:
  - Brief Notebook 06 - Data Mixing
  - Brief Notebook 06
tags:
  - brief
  - notebook
  - training
  - data-mixing
notebook_id: "06-data-mixing"
lane: "A + B"
accelerator: "T4 x2"
target: 2026-09-07
depends_on: "02, 04"
status: done
completed: 2026-09-07
result: "Hasil Notebook 06 - Data Mixing.md"
---

# Brief Notebook 06 — Data Mixing

> [!success] SELESAI 7 September — baca hasilnya, bukan briefnya
> Gate 4 lolos, kandidat submission dibekukan: **E4** (Jember + Common Voice Indonesia terkurasi), dev resmi 0,2532 → **0,2312**, lolos 3/3 aturan. Semua angka, vonis per-arm, dan warisan untuk NB 07/08 ada di [[nb06-data-mixing-results|Hasil Notebook 06 - Data Mixing]].
>
> Brief ini disimpan sebagai catatan perencanaan. **Empat bagian di bawah sudah gugur oleh hasilnya** dan ditandai satu per satu di tempatnya: urutan "TTS dulu", jalur M2/M3, E2, dan butir pertama "Jebakan" soal dev.

> [!abstract] Untuk Claude di chat baru
> Menguji apakah menambahkan data di luar Jember menurunkan WER. Jawabannya **belum tentu ya** — dua kandidat tambahan sama-sama read speech, sedangkan target kita percakapan spontan. Notebook ini dirancang supaya setiap penambahan harus **membuktikan diri**, dan dibuang tanpa penyesalan kalau tidak.
>
> **Ibaratnya:** ini nyoba nambahin buku pelajaran tambahan ke sesi les — tapi cuma dipertahankan kalau nilai ujiannya beneran naik. Buku yang kelihatan bagus di rak tapi ternyata tidak membantu, langsung disingkirkan lagi, tidak dipaksa dipakai cuma karena sudah kadung dibeli.
>
> Prasyarat: notebook 04 sudah lulus Gate 2. Kalau fine-tune Jember saja belum mengalahkan zero-shot, jangan jalankan notebook ini.


> [!danger] M1 dan M2 TERBALIK sejak 28 Agustus — baca ini sebelum apa pun di bawah
> Dev set resmi menunjukkan referensi kompetisi **tidak memakai diakritik Jember**: nol `ê`/`è`/`ě` di 17.495 token. Target latihan sudah dipindah ke `text_folded`.
>
> Akibatnya **M1 (ruang terlipat) yang benar**, bukan gugur — dan **M2 (diakritisasi transkrip TTS) tidak ada gunanya lagi**: menambahkan diakritik yang tidak dipakai referensi cuma menciptakan kesalahan. Bonusnya, transkrip TTS yang memang polos jadi **langsung kompatibel tanpa pekerjaan apa pun**, jadi hambatan terbesar M2 lenyap bersama M2-nya. Bukti di [[official-dev-set-analysis-2026-08-28|Analisa Dev Set Resmi - 28 Agustus 2026]].

> [!danger] Notebook 04 selesai 31 Agustus dan membalik urutan pengujian di bawah — baca sebelum bagian mana pun
> **Gate 2 lolos**, jadi prasyarat notebook ini terpenuhi. Tapi NB 04 juga mengukur *bentuk* kegagalannya, dan bentuk itu bukan yang diasumsikan brief ini. Bukti lengkap di [[nb04-whisper-core-results|Hasil Notebook 04 - Whisper Core]].
>
> **1. Kegagalan yang terukur adalah sisi Indonesia, bukan sisi Jawa.** Fine-tune Jember memperbaiki Jawa besar-besaran (massa error −590) tapi **merusak Indonesia** (+286). Di dev resmi, WER Indonesia naik dari 0,1836 zero-shot ke 0,2058 bahkan pada resep 1-epoch yang paling sehat. Di level confusion, model berhenti menerjemahkan Jawa→Indonesia lalu mulai menerjemahkan Indonesia→Jawa (`jadi→dadi` 0→25).
>
> **2. Jadi urutan "TTS dulu, Common Voice belakangan" di bawah berdiri di atas premis yang gugur.** Alasan yang tertulis — "tambahan CV sebagian besar kata Indonesia, yang justru memicu kegagalan yang ingin kita hindari" — sekarang terbalik: kata Indonesia adalah **obatnya**, bukan racunnya. TTS Central Javanese menambah lagi read speech berbahasa Jawa, yaitu memperdalam distorsi yang sudah terukur. **Uji Common Voice Indonesia lebih dulu.** Kalau tim tetap ingin menguji TTS, jadikan ia arm kedua, bukan pertama.
>
> **3. Sasaran berangka, dua-duanya mustahil disentuh data Jember:** WER Indonesia 0,2058 (lawan 0,1836 zero-shot) dan kelas `unk` 0,4057 atas 2.396 token — seperlima seluruh massa error, dan satu-satunya kelas yang nyaris tidak pernah bergerak.

> [!check] Resep dasar yang diwariskan NB 04 — jangan diturunkan ulang
> `whisper-large-v3-turbo`, language token `jw`, target `text_folded`, **`SEGMENT_MODE="concat25"`**, **1 epoch**, lr 6e-06, batch efektif 16, adafactor, decode greedy `no_repeat_ngram_size=4` dengan `LONG_MODE="chunk"`. Run penuh 0,68 jam — cukup murah untuk menguji beberapa rasio pencampuran.
>
> **Pemilihan checkpoint TIDAK boleh memakai dev Jember.** NB 04 membuktikan dev Jember **antikorelasi** dengan distribusi yang dinilai: ia menyatakan `native` mengalahkan `concat25` dan menyatakan 3 epoch jauh mengalahkan 1 epoch, sementara dev resmi menyatakan sebaliknya di kedua kasus. Pindahkan pemilihan ke dev resmi, atau ke subset kurva 150 klip sambil menyisakan 222 sisanya sebagai validasi yang tidak pernah disentuh.

## Yang sudah diketahui dari data

Diukur di notebook 01, jadi tidak perlu diukur ulang:

| | Jam | Cakupan kosakata Jember | Diakritik |
|---|---:|---:|---|
| TTS Central Javanese | 7,89 | **56,2%** | **Nol** |
| Common Voice Indonesia | 35,94 | 41,5% | — |
| Keduanya | 43,83 | 69,5% | — |

**TTS menutup lebih banyak kosakata dengan seperempat jam.** Karena itu urutan pengujian dibalik dari rencana lama: TTS dulu, Common Voice belakangan. Tambahan CV di atas TTS hanya 13,3 poin cakupan, dan sebagian besar berupa kata Indonesia — yang justru memicu kegagalan yang ingin kita hindari.

> [!failure] GUGUR — paragraf di atas terbalik, dan ini terukur
> Cakupan kosakata ternyata bukan prediktor yang benar. Lima arm membuktikan **kata Indonesia adalah obatnya**: setiap arm yang menang menang lewat WER Indonesia, dan E4 menurunkannya sampai **di bawah** zero-shot (0,1836 → 0,1716). E3 membuktikan kedekatan aksen Jawa bukan mesinnya. **E1 (TTS) tidak dijalankan** — hipotesisnya sudah ditolak tiga kali dari arah berbeda. Bukti di [[nb06-data-mixing-results|Hasil Notebook 06 - Data Mixing]].

Common Voice juga punya masalah struktural: `train.tsv` bawaan hanya berisi 4 speaker, dan bahkan `validated.tsv` didominasi 10 speaker teratas yang memegang 59,1% jam. Kalau CV dipakai, split disusun sendiri dari `validated.tsv` dengan **batas jumlah klip per speaker**.

## Masalah inti: diakritik

TTS Central Javanese **sama sekali tidak memakai diakritik**. Jember memakainya berat — 5.374 `ê` dan 4.833 `è`. Mencampur mentah-mentah memberi model sinyal bertentangan untuk bunyi yang sama.

Tiga jalan keluar. Uji sesuai urutan, berhenti begitu ada yang bekerja.

| Jalan | Cara | Kelebihan | Kekurangan |
|---|---|---|---|
| **M1 — ruang terlipat** | Latih dan evaluasi seluruhnya pada `text_folded` | Paling sederhana | Kalah kalau scoring ternyata peka diakritik |
| **M2 — diakritisasi TTS** | Latih model teks-ke-teks kecil pada pasangan (folded → official) dari Jember, pakai untuk memberi diakritik pada transkrip TTS, lalu campur di ruang berdiakritik | Satu model ASR saja, dan akurasinya bisa diukur langsung | Perlu satu model tambahan |
| **M3 — adaptasi encoder saja** | Pakai audio TTS hanya untuk mengadaptasi encoder, decoder dibekukan atau dilatih hanya pada Jember | Menghindari masalah teks sepenuhnya | Manfaatnya lebih terbatas |

> [!failure] GUGUR — seluruh bagian "Masalah inti: diakritik" tidak berlaku lagi
> M1 (ruang terlipat) yang dipakai, dan ia benar: dev resmi terbukti tidak memakai diakritik sama sekali (28 Agustus). **M2 dan M3 gugur bersama E1** — keduanya hanyalah cara mengintegrasikan TTS, dan TTS tidak jadi dipakai. `diacritizer_eval.json` di daftar Output di bawah karenanya tidak pernah dibuat.

> [!tip] M2 layak dicoba dan murah
> Diakritisasi adalah tugas transliterasi karakter yang sangat teratur. Data latihnya gratis: setiap baris Jember memberi pasangan (terlipat, berdiakritik). Akurasinya bisa diukur langsung dengan held-out dari Jember. Kalau akurasi kata di atas 95%, M2 memberi hasil terbaik dari kedua dunia. Ini juga temuan yang layak ditulis, bukan sekadar trik.

## Eksperimen

Urut berdasarkan rasio bukti terhadap biaya. Berhenti dan lapor kalau sebuah eksperimen kalah — jangan otomatis lanjut ke berikutnya kalau anggarannya menipis.

| # | Komposisi | Jam | Pertanyaan |
|---|---|---:|---|
| **E1** | Jember + TTS, ruang terlipat (M1) | ~16 | Apakah TTS membantu sama sekali? |
| **E2** | Jember + TTS, ruang berdiakritik lewat M2 | ~16 | Apakah M2 mengalahkan M1? |
| **E3** | Jember + **439 klip CV beraksen Jawa** | ~9 | Subset kecil yang paling dekat domainnya. Sangat murah |
| **E4** | Jember + subset CV terkurasi, dibatasi per speaker, teks dideduplikasi | ~20–25 | Apakah CV membantu kalau dipilih dengan hati-hati |
| **E5** | Curriculum: pre-fine-tune pada tambahan, lalu fine-tune pada Jember saja | bervariasi | Sering mengalahkan pencampuran datar pada data kecil |
| **E6** | Upsampling Jember di dalam campuran, rasio 1:1 jam efektif | bervariasi | Mencegah data in-domain tenggelam |

> [!abstract] Apa yang benar-benar terjadi pada keenam baris di atas
> | # | dijalankan? | WER | vonis |
> |---|---|---:|---|
> | E1 | **tidak** — premisnya gugur, lihat callout di bagian sebelumnya | — | dibatalkan |
> | E2 | **tidak** — M2 gugur bersama E1 | — | dibatalkan |
> | E3 | ya, 0,95 jam | 0,2408 | drop (gagal aturan 3), kalah terbukti dari E4 |
> | **E4** | ya, 1,36 jam | **0,2312** | **KEEP — kandidat submission** |
> | E5 | dua tahap jalan, tapi **curriculumnya tidak pernah teruji**: tahap B gagal memuat bobot tahap A | 0,2591 / 0,2586 | drop, tapi bukan bukti soal curriculum |
> | E6 | ya, 2,26 jam | 0,2336 | drop (gagal aturan 3); tak terbedakan dari E4 pada WER |
>
> Catatan penting untuk E5: jangan pernah menuliskannya sebagai "curriculum kalah". Yang terukur cuma komponennya.
Catatan untuk E3: notebook 01 menemukan 439 klip CV yang kolom aksennya berlabel Jawa — `Javanese` 154, `jawa` 53, dan satu label gabungan 232. Itu bahasa Indonesia beraksen Jawa, jauh lebih dekat ke domain target daripada CV acak. Sangat murah untuk diuji dan hasilnya informatif ke arah mana pun.

Catatan untuk E4: sebelum dipakai, buang klip ber-`down_votes >= 1` dan deduplikasi kalimat. CV punya 30.465 klip tetapi hanya 12.170 kalimat unik, faktor pengulangan 2,5×.

## Aturan pemilihan

Sebuah campuran **hanya dipertahankan** kalau lolos ketiganya:

1. `wer_total` **turun** melebihi CI dev dari notebook 03. Selisih di bawah itu bukan temuan.
2. `wer_jv` **tidak memburuk**. Kalau WER total turun tetapi WER Jawa naik, kita sedang menukar akurasi Jawa demi akurasi Indonesia — dan test set-nya bukan bahasa Indonesia.
3. `jv_to_id` **tidak naik**. Ini alarm langsung untuk model yang mulai menerjemahkan alih-alih mendengar.

> [!warning] Aturan 3 dirumuskan ulang sebelum E4 dijalankan
> Versi di atas mengukur `jv_to_id` sebagai persentase substitusi Jawa — penyebutnya ikut mengecil setiap kali model membaik, jadi model yang lebih baik bisa terlihat gagal hanya karena ia lebih sedikit salah. Versi yang dipakai sejak E4: **jumlah token per 17.473 token referensi**, dengan pita derau ±√n. E3 masih dinilai dengan versi lama, jadi barisnya di `keep_rules.json` tidak sebanding langsung dengan E4/E6. Perumusan ulang ini tidak meloloskan E4 secara gratis — E4 tetap ditandai `MARGINAL`.

Kalau sebuah campuran gagal, **buang tanpa penyesalan** dan tulis alasannya. Hasil negatif yang terukur sama berharganya untuk laporan, dan lebih berharga daripada model yang lebih rumit tanpa dasar.

## Input

- `jember-segments-16k`, `manifest.csv`, `split.csv`, `lexicon_v1.csv`, `scorer.py`
- Kaggle dataset `central-javanese-corpus` dan `common-voice-corpus`
- Checkpoint terbaik dari notebook 04 dan 05

## Output

`NOTEBOOK_ID = "06-data-mixing"`.

| File | Isi |
|---|---|
| `mix_manifest_<E>.csv` | komposisi tiap eksperimen, bisa direproduksi |
| `results.csv` | satu baris per eksperimen dengan seluruh metrik guard |
| `diacritizer_eval.json` | akurasi kata dan karakter model M2 pada held-out Jember |
| `predictions_dev/<E>.csv` | prediksi per eksperimen |
| `dataset_findings.json` | digest `rec()` |

## Pembersihan yang wajib sebelum mencampur

Dari notebook 01, sudah terukur dan harus dieksekusi:

- **TTS:** buang 30 transkrip yang menunjuk file audio tidak ada
- **TTS:** buang sekitar 50 file duplikat lintas folder — nama file adalah hash, jadi nama sama berarti isi sama
- **TTS:** konversi WebM 48 kHz menjadi FLAC 16 kHz mono, konsisten dengan pipeline Jember
- **CV:** jangan pakai `train.tsv`; bangun dari `validated.tsv`
- **CV:** batasi klip per speaker, deduplikasi kalimat, buang `down_votes >= 1`

## Jebakan

- ~~**Dev tidak boleh berubah.** Seluruh evaluasi tetap pada dev Jember yang sama.~~ **GUGUR sejak NB 04:** dev Jember terbukti antikorelasi dengan distribusi yang dinilai, jadi lapisan keputusan dipindah ke **dev resmi 372 klip**. Yang tetap berlaku dari butir ini: dev-nya sendiri tidak boleh dicampuri data TTS atau CV. Perhatikan juga bahwa 150 dari 372 klip dipakai memilih checkpoint — angka bersihnya diukur di 222 sisanya.
- Klip read speech jauh lebih pendek daripada segmen spontan. Whisper memadatkan setiap input sampai 30 detik, jadi campuran yang didominasi klip pendek membuang komputasi dan menggeser kebiasaan model menjauh dari target. Pertimbangkan menyambung beberapa kalimat read speech menjadi satu contoh yang lebih panjang.
- Rasio pencampuran dihitung dalam **jam efektif setelah split**, bukan jam mentah dari halaman dataset.
- Model diakritisasi M2 dilatih pada teks train saja. Memakai teks dev adalah kebocoran.
- Setiap eksperimen harus punya manifest sendiri yang bisa direproduksi. Campuran yang dibuat spontan di memori tidak bisa diaudit.

## Setelah selesai — ini Gate 4

> [!success] Gate 4 DITUTUP 7 September 2026
> `Hasil Notebook 06 - Data Mixing.md` ditulis, dan model yang dibekukan adalah **E4**: `amozaurus/mozilla-jv-06-data-mixing-E4` @ `c79347a5`, 3,24 GB, 1,36 jam training di T4 tunggal — jauh di dalam anggaran runtime.

Tulis `Hasil Notebook 06 - Data Mixing.md`, lalu **bekukan satu model** sebagai kandidat submission. Kriterianya bukan WER terbaik semata, melainkan WER terbaik **yang muat di anggaran runtime**. Berikutnya: [[nb07-brief-error-analysis-robustness|Brief Notebook 07 - Error Analysis dan Robustness]] dan [[nb08-brief-packaging-submission|Brief Notebook 08 - Packaging dan Submission]].
