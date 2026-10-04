---
title: "Brief Notebook 05 — XLS-R CTC + Language Model"
aliases:
  - Brief Notebook 05 - XLS-R CTC dan LM
  - Brief Notebook 05
tags:
  - brief
  - notebook
  - training
  - ctc
notebook_id: "05-xlsr-ctc"
lane: "B — CTC"
accelerator: "P100"
target: setelah NB 06
depends_on: "02"
status: deferred
---

# Brief Notebook 05 — XLS-R CTC + Language Model

> [!abstract] Untuk Claude di chat baru
> Pembanding arsitektur untuk [[nb04-brief-finetune-whisper-core|Brief Notebook 04 - Finetune Whisper Core]], pada split yang persis sama. Berjalan paralel, tidak saling menunggu. Nilai tambah utamanya bukan sekadar "model kedua" — CTC memberi **kontrol penuh atas vocabulary** dan membuka **rescoring dengan language model**, dua hal yang tidak bisa dilakukan pada Whisper.
>
> **Ibaratnya:** ini kandidat kedua yang dilatih dengan gaya belajar yang beda total — bukan "dengar lalu tebak kalimat utuh" kayak Whisper, tapi "dengar lalu eja huruf demi huruf". Gaya ini lebih ribet diatur, tapi hasilnya bisa dicek ulang pakai kamus bantu (language model) sebelum jawaban akhir diputuskan — sesuatu yang tidak bisa dilakukan ke kandidat pertama.

> [!warning] DITUNDA sampai NB 06 selesai — keputusan 31 Agustus, dan brief ini akan ditulis ulang lebih sempit
> Dua dari tiga alasan di bawah sudah gugur oleh temuan setelah brief ini ditulis:
>
> - **Alasan 1 (ortografi berdiakritik) gugur.** Dev resmi tidak memakai diakritik Jember sama sekali; target latihan sudah pindah ke `text_folded` sejak 28 Agustus. Kontrol penuh atas vocabulary tidak lagi membeli apa pun di sini.
> - **Alasan 2 (CTC tidak berhalusinasi) gugur.** Loop pengulangan sudah diselesaikan `no_repeat_ngram_size=4`. Di NB 04 insertion rate 0,04 dan rasio panjang 1,02 — tidak ada masalah halusinasi tersisa.
> - **Alasan 3 (LM n-gram) masih hidup, tapi punya masalah baru.** Teks sumber yang disebut brief ini — teks train Jember plus transkrip TTS — seluruhnya memakai konvensi ortografi Jember, yang NB 04 buktikan **salah** untuk referensi resmi (`kayak` 140:9 di referensi resmi, 2:738 di Jember). LM dari teks itu akan mendorong output makin jauh ke arah yang keliru. Transkrip dev resmi tidak boleh dipakai sebagai teks LM karena itu melatih di atas validasi.
>
> Ditambah perkiraan yang tidak menguntungkan: XLS-R dengan head CTC dilatih pada 8,5 jam saja kemungkinan besar jauh di bawah 0,2524, karena ia tidak punya kemampuan bahasa Indonesia bawaan sementara **70% token dev resmi adalah Indonesia atau dua-bahasa**. Whisper turbo mulai dari 0,2695 bahkan tanpa dilatih.
>
> **Rencana:** tulis ulang brief ini setelah NB 06, dipersempit jadi satu pertanyaan — apakah CTC + LM mengalahkan angka NB 06 di 372 klip resmi. Kalau tidak, lane B ditutup. Kalau ada kuota menganggur di akun lain sebelum itu, jalankan versi sempitnya secara paralel; ia tidak memakan kuota NB 06.

## Kenapa jalur ini layak dikerjakan

Tiga alasan yang spesifik untuk data ini, bukan sekadar diversifikasi:

1. **Ortografi berdiakritik bisa dikodekan langsung.** Vocabulary CTC adalah karakter yang kita pilih sendiri, jadi `ê`, `è`, `ě`, titik, dan tanda hubung menjadi simbol kelas satu. Whisper harus memecahnya menjadi beberapa subword — notebook 01 mengukur `cêdhêk-cêdhêk` menjadi 13 potongan.
2. **CTC tidak bisa berhalusinasi.** Tidak ada decoder autoregresif, jadi tidak ada pengulangan tak berujung pada jeda dan noise. Pada voice note yang berisik ini bisa jadi keunggulan nyata.
3. **Language model n-gram itu murah dan sering besar dampaknya** pada ASR low-resource. Teks Jember train ditambah transkrip TTS Central Javanese sudah cukup untuk 5-gram karakter atau kata.

Risikonya juga jelas: beam search dengan LM butuh `pyctcdecode` dan `kenlm`, dan **paket itu belum tentu ada di runtime image kompetisi**. Karena itu jalur ini dirancang berlapis — lihat bagian rencana kontingensi.

## Input

- Kaggle dataset `jember-segments-16k`
- `manifest.csv`, `split.csv`, `lexicon_v1.csv`, `scorer.py`
- Inventaris karakter dari `text_audit.json` notebook 02

## Output

`NOTEBOOK_ID = "05-xlsr-ctc"`.

| File | Isi |
|---|---|
| `vocab.json` | vocabulary karakter, dibekukan |
| `train_log.csv` | step, loss, lr, dev WER, dev CER |
| `eval_final.json` | WER greedy dan WER dengan LM, keduanya dipecah per asal kata |
| `lm/jember_tts_5gram.arpa` | language model, plus dokumentasi teks sumbernya |
| `predictions_dev.csv` | greedy dan hasil beam+LM, kolom terpisah |
| `decode_sweep.csv` | WER terhadap `alpha`, `beta`, `beam_width` |
| `dataset_findings.json` | digest `rec()` |

## Langkah

### 1. Vocabulary

Bangun dari inventaris karakter `text_official` di notebook 02, bukan dari asumsi.

- Sertakan huruf, seluruh varian diakritik `e`, spasi sebagai `|`, titik, tanda hubung, dan titik-titik elipsis.
- Buang karakter berfrekuensi sangat rendah — di bawah 20 kemunculan — dan catat berapa token yang terdampak.
- Tambahkan `<pad>`, `<unk>`, dan blank CTC.
- **Bekukan `vocab.json`.** Vocabulary yang berubah membuat checkpoint lama tidak bisa dipakai.
- Laporkan ukuran vocab dan berapa persen teks yang bisa direkonstruksi sempurna darinya.

### 2. Latihan

| Setelan | Nilai awal |
|---|---|
| Model | `facebook/wav2vec2-xls-r-300m`, Apache-2.0 |
| Learning rate | 3e-4 sampai 1e-4 dengan warmup, ini jauh lebih besar daripada Whisper |
| Feature extractor | dibekukan |
| Layer bawah encoder | dibekukan beberapa layer pertama |
| SpecAugment / masking | aktif — ini bawaan resep wav2vec2 dan penting pada data kecil |
| Epoch | 15–30; CTC butuh lebih banyak epoch daripada seq2seq |
| Batch | efektif 8–16, kelompokkan berdasarkan panjang untuk mengurangi padding |
| Precision | fp16 |
| Metrik | WER **dan** CER; CER bergerak lebih halus dan lebih enak dipakai memantau |

> [!warning] P100 tidak bisa kuantisasi
> Compute capability P100 adalah 6.0, sedangkan `bitsandbytes` butuh minimal 7.5. Tidak ada int8 dan tidak ada 4-bit di lane ini. Untungnya XLS-R 300M full fine-tune memang muat di 16 GB tanpa kuantisasi, dan P100 punya bandwidth memori 2,3× T4 sehingga justru cocok untuk beban yang memory-bound seperti ini. Jangan mengandalkan kernel attention hemat-memori di sini; lebihkan margin VRAM.

### 3. Language model

- Teks sumber: `text_official` dari **`split == train` saja**, ditambah seluruh transkrip TTS Central Javanese.
- **Jangan pernah memasukkan teks dev.** Itu kebocoran, dan angkanya akan menipu.
- TTS tidak memakai diakritik sama sekali sedangkan Jember memakainya berat. Latih **dua LM**: satu di ruang `text_official` dengan Jember saja, satu di ruang `text_folded` dengan Jember plus TTS. Bandingkan keduanya — ini sekaligus bukti awal apakah pencampuran TTS membantu, sebelum notebook 06 menghabiskan GPU untuk mengujinya secara akustik.
- 5-gram kata dengan pruning; kalau data terasa terlalu tipis, coba juga 6-gram karakter.
- Decode dengan `pyctcdecode`, sweep `alpha` (bobot LM), `beta` (bonus panjang), dan `beam_width`. Sweep di dev, laporkan seluruh permukaan hasilnya di `decode_sweep.csv`.

### 4. Rencana kontingensi runtime

Runtime image kompetisi belum terbit, dan `kenlm` serta `pyctcdecode` belum tentu ada di sana. Siapkan tiga lapis dan laporkan WER ketiganya:

| Lapis | Kebutuhan | Status |
|---|---|---|
| **L1** greedy CTC | `torch` + `transformers` saja | **Selalu aman.** Ini angka yang wajib dilaporkan |
| **L2** beam search tanpa LM | implementasi murni Python/NumPy, bisa dibundel di ZIP | Aman |
| **L3** beam + KenLM | `pyctcdecode` + `kenlm` di image | **Bergantung pada penyelenggara** |

Kalau L3 memberi keunggulan besar dibanding L1, itu argumen kuat untuk mengajukan penambahan paket lewat PR ke runtime repo begitu terbit. Kalau selisihnya kecil, jangan buang waktu.

### 5. Perbandingan dengan Whisper

Laporkan berdampingan dengan hasil notebook 04, pada dev yang sama:

| Dimensi | Kenapa dibandingkan |
|---|---|
| WER total | Yang paling jelas |
| WER Jawa versus Indonesia | Hipotesisnya CTC lebih setia pada kata Jawa karena tidak "menerjemahkan" |
| `jv_to_id` | Uji hipotesis di atas secara langsung |
| Tingkat halusinasi | CTC seharusnya nyaris nol |
| Ketepatan diakritik | Hipotesisnya CTC lebih baik karena diakritik adalah simbol vocabulary |
| Detik per klip dan ukuran bobot | Masuk anggaran runtime |

Perbandingan ini bisa menghasilkan kesimpulan yang lebih menarik daripada sekadar "siapa WER-nya lebih kecil" — misalnya kalau CTC kalah di WER total tetapi menang telak di WER kata Jawa, itu bahan untuk ensemble atau untuk pemilihan model berdasarkan komposisi test set.

## Kriteria selesai

- [ ] WER dev greedy CTC tercatat, dipecah per asal kata
- [ ] WER dengan LM tercatat untuk kedua LM dan seluruh sweep decode
- [ ] Ketiga lapis kontingensi terukur, sehingga keputusan bisa diambil kapan pun runtime repo terbit
- [ ] Tabel perbandingan langsung dengan notebook 04
- [ ] `vocab.json` dibekukan dan masuk repo

## Jebakan

- Learning rate CTC jauh lebih besar daripada seq2seq. Memakai 1e-5 ala Whisper membuat model tidak konvergen dan mudah disalahartikan sebagai "CTC tidak cocok".
- CTC memerlukan input yang lebih panjang daripada target. Segmen sangat pendek dengan teks panjang menghasilkan `inf` loss — buang atau tandai.
- `ctc_zero_infinity=True` mencegah satu batch buruk merusak seluruh run.
- Kelompokkan batch berdasarkan panjang. Tanpa itu, padding memakan sebagian besar komputasi.
- KenLM perlu dikompilasi. Kalau instalasi di Kaggle bermasalah, ada wheel siap pakai; jangan habiskan waktu berjam-jam di sini — L1 dan L2 sudah memberi jawaban utama.
- LM dilatih pada teks train saja. Ini gampang terlanggar tanpa sadar kalau memakai gabungan manifest.

## Setelah selesai

Tulis `Hasil Notebook 05 - XLS-R CTC.md`. Bawa pemenangnya ke [[nb06-brief-data-mixing|Brief Notebook 06 - Data Mixing]].
