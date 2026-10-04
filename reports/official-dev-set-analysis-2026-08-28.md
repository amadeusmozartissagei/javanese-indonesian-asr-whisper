---
title: "Analisa Dev Set Resmi — 372 Klip (28 Agustus 2026)"
aliases:
  - Analisa Dev Set Resmi - 28 Agustus 2026
  - Analisa Dev Set Resmi
  - Official Dev Set 372
tags:
  - research
  - competition
  - dataset
  - eval
status: final
created: 2026-08-28
updated: 2026-08-28
data: Datasets/indonesian_dev/
source_type: measured-from-data
---

# Analisa Dev Set Resmi — 372 Klip

> [!summary] Ringkasan
> Dev set resmi akhirnya ada di repo, dan isinya **membatalkan dua keputusan yang sudah dianggap final**. Ortografinya sama sekali bukan ortografi Jember: **0% ejaan berdiakritik Jember muncul apa adanya**, sementara **69,4%-nya cocok setelah dilipat** — jadi target latihan harus pindah dari `text_official` ke `text_folded`. Dan klipnya jauh lebih panjang dari yang kita latih: rata-rata **24,9 detik** lawan 5,4 detik di Jember, dengan **10,2% melewati jendela 30 detik Whisper**. Bonusnya, kelima klip smoke test ternyata diambil dari sini, jadi NB 08 bisa gladi bersih dengan referensi yang diketahui.
>
> **Ibaratnya:** selama ini kita berlatih menjawab soal dengan tulisan tangan penuh tanda baca khusus, karena buku latihan kita ditulis begitu — lalu baru sekarang melihat lembar jawaban asli juri, dan ternyata mereka menulis polos. Bukan cuma itu: soal latihan kita kalimat-kalimat pendek, sementara soal aslinya paragraf panjang. Dua-duanya masih bisa dibetulkan, tapi harus sekarang, sebelum les privatnya dimulai.

> [!info] Cara pengukuran
> `Datasets/indonesian_dev/` (372 klip + `metadata.tsv`), diunduh 28 Agustus dari katalog MDC lewat Data download page kompetisi. Semua angka dihitung lokal, tanpa GPU. Durasi audio dibaca langsung dari header frame MPEG (tidak ada tooling audio di mesin ini) — 48 kHz, mono, 64 kbps CBR, konsisten di seluruh 372 file.

## Apa isinya

| | |
|---|---|
| klip | **372**, total **2,57 jam** |
| speaker | **4** (id 1, 5, 6, 7) |
| percakapan | **2** (`convo_id` 2 dan 5) |
| bahasa | `javind` **352**, `ind` **20**, `jav` **0** |
| token transkrip | 17.495 |
| audio | 48 kHz mono, 64 kbps MP3 |

Tidak ada satu pun klip berlabel `jav` murni. Distribusi test praktis **seluruhnya code-switching** — bukan Jawa murni, bukan Indonesia murni.

## Temuan 1 — ortografinya bukan ortografi Jember

Ini pertanyaan P0 yang menahan NB 04 sejak [[nb02-cross-audit-scorer-text-2026-08-26|Audit Silang - Scorer dan Asumsi Teks (26 Agustus 2026)]]. Jawabannya tidak ambigu.

```
token berdiakritik   53 / 17.495  =  0,30 %
karakter diakritik   é  (acute) 54×   ...  dan tidak ada yang lain
                     ê 0    è 0    ě 0    ḍ 0
```

Bandingkan Jember: **14,30%** token berdiakritik, memakai `ê` 5.372×, `è` 4.825×, `ě` 819×. Satu-satunya diakritik resmi, `é`, dipakai sebagai sufiks (`kuliahé`, `guruné`, `kancané`, `akhiré`) — bukan sistem vokal yang dipakai penganotasi Jember.

Kata penanda Jember, ditulis apa adanya di dev resmi:

| Jember | di dev resmi | | Jember | di dev resmi |
|---|---|---|---|---|
| `těrus` 0 | **`terus` 225** | | `nèng` 0 | **`neng` 24** |
| `bangêt` 0 | **`banget` 139** | | `ndèk` 0 | **`ndek` 11** |
| `nèk` 0 | **`nek` 73** | | `akèh` 0 | **`akeh` 3** |

> [!danger] Keputusan berbalik: target latihan adalah `text_folded`
> Dari 9.385 token berdiakritik di Jember, **0 (0,0%)** ejaannya muncul di dev resmi apa adanya, dan **6.516 (69,4%)** muncul setelah dilipat. Melatih pada `text_official` berarti mengajari model menulis `těrus` ketika referensi menulis `terus` — setiap kejadian jadi satu substitution, dan penyelenggara **tidak pernah menyebut melipat diakritik**.
>
> Matriks "strategi dominan" di [[nb02-data-build-results|Hasil Notebook 02 - Data Build]] runtuh persis di kolom yang diprediksi audit 26 Agustus. Biayanya asimetris dan sekarang terukur: latih berdiakritik → rugi hingga 14,3%; latih terlipat → rugi 0,30% (sufiks `é` yang hilang, 53 token dari 17.495).
>
> **Tidak perlu rerun NB 02.** `text_folded` sudah ada di manifest dan sudah diverifikasi identik dengan `fold_diacritics(text_official)` untuk seluruh 6.638 baris. Ini satu baris di NB 04.

## Temuan 2 — panjang klipnya beda kelas

```
dev resmi : 372 klip   mean 24,9s   median 26,3s   min 6,4s   max 37,9s
Jember    : 6.638 seg  mean  5,4s   median  ~4s    min 1,0s   max 29,0s

  > 10s : 371 (99,7 %)
  > 20s : 305 (82,0 %)
  > 30s :  38 (10,2 %)   <- di luar jendela Whisper
  > 40s :   0 (0,0 %)
```

Dua konsekuensi terpisah, dan keduanya penting.

**Untuk NB 08: chunking wajib, dan sekarang ada angkanya.** 10,2% klip melewati 30 detik. Diekstrapolasi ke 2.118 klip test, itu **sekitar 216 klip** yang akan dipotong diam-diam oleh encoder Whisper, dengan sisa audionya jadi deletion murni. Ini bukan kasus tepi.

**Untuk NB 04: ada ketimpangan panjang antara latih dan uji.** Model dilatih pada potongan 5 detik lalu diuji pada klip 25 detik. Whisper memang menangani keduanya, tetapi fine-tuning pada segmen pendek saja mendorong model ke perilaku "satu utterance pendek per klip" yang tidak cocok dengan bentuk test.

> [!tip] Temuan "padding mustahil" dari NB 02 berubah jadi aset
> NB 02 menemukan anotasi Jember adalah **partisi kontinu** — seluruh 6.471 jeda antar segmen tepat 0 detik. Dulu itu kabar buruk (padding tidak pernah terjadi). Sekarang itu berarti **segmen berurutan bisa disambung tanpa kehilangan apa pun**: audionya memang bersebelahan, teksnya tinggal dirangkai.
>
> Dan karena audio disimpan **per rekaman** dengan offset sampel di manifest, menyambung N segmen cuma berarti memakai jendela `[start_sample pertama, end_sample terakhir]`. **Tidak ada data baru yang perlu dibangun, tidak ada rerun NB 02.** Ini kandidat kuat untuk salah satu slot ablation NB 04: latih pada segmen yang disambung sampai ~25 detik supaya distribusi panjangnya menyerupai test.

## Temuan 3 — kelima klip smoke test ada di sini

`competition/smoke_test_submission_format.csv` memuat 5 nama file. **Kelimanya ada di dev set ini**, lengkap dengan transkrip referensinya — dan tidak satu pun ada di 2.118 klip test.

Artinya NB 08 bisa **gladi bersih sungguhan**: jalankan `main.py` atas kelima klip itu persis seperti container, lalu bandingkan keluarannya dengan referensi yang sudah diketahui. Bukan cuma menguji pipa-nya tidak crash, tapi memastikan transkripsinya masuk akal — dan sekaligus mengukur waktu import + load bobot terhadap limit 1 menit.

## Peran dev set ini: validasi, bukan latihan

> [!check] Jangan dipakai melatih
> Tiga alasan, dan yang ketiga menentukan. **(1)** Cuma 4 speaker di 2 percakapan — sebagai data latih ia mengundang overfit ke empat suara. **(2)** 2,57 jam melawan 8,5 jam Jember; tambahannya kecil. **(3)** Test set ditahan penyelenggara dan tidak akan pernah kita pegang, jadi **ini satu-satunya sampel distribusi test yang akan pernah ada**. Membakarnya jadi data latih berarti menghapus satu-satunya sinyal validasi yang jujur, demi 30% tambahan data.
>
> Aturan kompetisi tidak melarangnya (R9 hanya melarang anotasi manual dan pseudo-label **di atas test set**), jadi ini keputusan strategi, bukan kepatuhan.

Perannya mulai NB 04: **lapisan validasi utama**. Dev split Jember turun statusnya jadi proxy same-corpus — berguna untuk memantau progres training karena besar dan murah, tetapi setiap klaim "model ini lebih baik" harus dikonfirmasi di 372 klip ini.

## Yang berubah di dokumen lain

| Dokumen | Perubahan |
|---|---|
| [[nb02-data-build-results\|Hasil Notebook 02 - Data Build]] | matriks diakritik selesai — `text_folded` menang |
| [[nb04-brief-finetune-whisper-core\|Brief Notebook 04 - Finetune Whisper Core]] | target `text_folded`; validasi utama pindah; ablation segmen disambung |
| [[nb08-brief-packaging-submission\|Brief Notebook 08 - Packaging dan Submission]] | chunking wajib (10,2%); gladi bersih smoke test dengan referensi |
| [[nb06-brief-data-mixing\|Brief Notebook 06 - Data Mixing]] | **M2 (diakritisasi transkrip TTS) gugur** — tidak ada gunanya menambahkan diakritik yang tidak dipakai referensi |
| [[nb02-cross-audit-scorer-text-2026-08-26\|Audit Silang - Scorer dan Asumsi Teks (26 Agustus 2026)]] | temuan #4 dan #5 tertutup |

## Temuan 4 — konvensi teks selain diakritik ternyata cocok

Diperiksa setelah dataset diunggah. Diakritik adalah **satu-satunya** ketidakcocokan ortografi; sisanya sejalan.

| konvensi | dev resmi | Jember | vonis |
|---|---|---|---|
| tag `[laugh]` | 0% | 0% | tidak relevan di data kita |
| penanda `(???)` | 0% | 0% | tidak relevan di data kita |
| elipsis menempel | 29,3% baris | 10,8% baris | **sama-sama dipakai** (baris dev 5× lebih panjang) |
| tanda hubung | 75,3% baris | 23,6% baris | **sama-sama dipakai** |
| kapital pasca-normalisasi | **3,3%** token | **3,3%** token | **identik** — nama diri & akronim |
| angka digit | **0** token | 17 token | resmi **selalu mengeja**, tidak pernah digit |
| kutip melengkung | **0** | 38 baris / 57 token | artefak Jember saja |

Tiga konsekuensi kecil tapi konkret:

- **Model tidak boleh mengeluarkan digit.** Referensi resmi mengeja seluruh angka. NB 03 sudah melihat gejalanya: Whisper zero-shot menjawab `40` untuk `empat puluh`. Fine-tuning pada teks Jember (yang praktis juga selalu mengeja) semestinya memperbaikinya sendiri — tapi jadikan ini item pemeriksaan di NB 04, dan jaring pengaman digit→kata di post-processing NB 08 kalau masih bocor.
- **Kapitalisasi terkonfirmasi.** Sama-sama 3,3% dan sama-sama nama diri/akronim (`SMA`, `SMP`, `Indonesia`, `Jepang`). Melatih pada teks yang mempertahankan kapital di tengah kalimat memang benar.
- **Kutip melengkung cuma ada di Jember.** 57 token yang mengajari model mengeluarkan karakter yang tidak pernah dipakai referensi resmi — 0,09%, terlalu kecil untuk dikejar, tapi ini juga menutup celah kutip melengkung yang ditandai di [[nb02-cross-audit-scorer-text-2026-08-26|Audit Silang - Scorer dan Asumsi Teks (26 Agustus 2026)]] §2: celah itu hanya menyentuh teks Jember, tidak pernah menyentuh referensi yang dinilai.

## Sudah terbit di Kaggle

Dataset **`indonesian_dev`**, Version 1, 74,1 MB, 373 file (372 `.mp3` + 1 `.tsv`). Strukturnya punya satu level ekstra: akar dataset berisi folder `indonesian_dev/`, baru di dalamnya `clips/` dan `metadata.tsv`. Jadi jalur mount-nya:

```
/kaggle/input/<slug>/indonesian_dev/clips/*.mp3
/kaggle/input/<slug>/indonesian_dev/metadata.tsv
```

NB 04 sebaiknya **menemukan jalur ini lewat pencarian**, bukan menuliskannya keras — pola yang sama dengan cell 1 NB 03:

```python
META = next(Path("/kaggle/input").rglob("indonesian_dev/metadata.tsv"))
DEV_CLIPS = META.parent / "clips"
```

## Yang masih terbuka

- **Berapa banyak dari 2.118 klip test yang melewati 30 detik** tetap tidak diketahui. 10,2% adalah estimasi dari dev, dan dev berasal dari distribusi yang sama — pakai itu sebagai angka perencanaan, bukan sebagai fakta.
