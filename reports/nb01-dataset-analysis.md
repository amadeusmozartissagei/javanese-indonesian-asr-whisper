---
title: "Analisa Dataset — Notebook 01 (Lost in Transcription)"
aliases:
  - Analisa Dataset - Notebook 01
  - Analisa Dataset Notebook 01
  - Dataset EDA Indonesian–Javanese
tags:
  - research
  - competition
  - asr
  - dataset
  - eda
status: final
created: 2026-08-20
updated: 2026-08-20
notebook: notebooks/01-dataset-eda.ipynb
data: findings/01-dataset-eda/dataset_findings.json
source_type: measured-from-data
---

# Analisa Dataset — Notebook 01

> [!summary] Ringkasan
> Ketiga dataset sudah dibaca penuh dan diukur langsung dari filenya, bukan dari deskripsi halaman dataset. Tiga hal mengubah rencana di [[feasibility-study|Feasibility Study - Mozilla Lost in Transcription]]: **TTS Central Javanese ternyata lebih berguna daripada Common Voice**, **ejaan Jember tidak konsisten pada 10,8% kata**, dan **Common Voice jauh lebih timpang daripada yang terlihat dari jumlah speaker-nya**.
>
> **Ibaratnya:** sebelum masak, cicipi dulu semua bahan mentahnya satu-satu — jangan cuma percaya label di kemasan. Ternyata bahan yang dikira kurang berguna (TTS) malah lebih segar dari yang diharap, dan bahan yang kelihatannya banyak variasi (Common Voice) ternyata didominasi segelintir "penyumbang" saja.

> [!info] Sifat angka di catatan ini
> Semua dihitung dari data asli oleh `notebooks/01-dataset-eda.ipynb` yang dijalankan di Kaggle. Hasil mentahnya di `findings/01-dataset-eda/dataset_findings.json`, log lengkapnya di `run-log.txt` pada folder yang sama. Kalau notebook di-run ulang, angka di catatan ini perlu disesuaikan manual.

## Kompetisinya minta apa

Membuat sistem yang **mengubah rekaman suara menjadi teks**, untuk percakapan voice note yang bahasanya campur Indonesia dan Jawa.

| Tahap | Isinya |
|---|---|
| Masukan | File audio `.mp3` berisi potongan percakapan |
| Keluaran | CSV dengan kolom `audio_filename` dan `transcript` |
| Cara kirim | Model + kode inference dikemas ZIP, dijalankan di server penyelenggara |
| Cara dinilai | **WER** — persentase kata yang salah, makin kecil makin baik |

Penilaian per kata dan **tidak mengenal nilai parsial**. Salah satu huruf membuat kata itu dihitung salah sepenuhnya — sebabnya hal sepele seperti diakritik bisa berdampak nyata. Lihat [[#Temuan Jember]] nomor 2.

## Ringkasan ketiga dataset

| | Jember Javanese | Common Voice id 26.0 | TTS Central Javanese |
|---|---|---|---|
| **Peran** | Dataset utama | Kandidat tambahan | Kandidat tambahan |
| Jumlah | 6.679 segmen / 208 rekaman | 30.465 klip (validated) | 4.599 klip / 93 folder |
| Durasi | 10,01 jam | 35,94 jam | 7,89 jam |
| Speaker | **tidak diketahui** | 468 | **tidak diketahui** |
| Jenis bicara | Spontan, dialog | Bacaan naskah | Bacaan naskah |
| Format | mp3, mono, 44,1 & 48 kHz | mp3 | WebM, mono, 48 kHz |
| Panjang klip | median 5,0 dtk | median 3,96 dtk | median 6,03 dtk |
| Diakritik | Dipakai berat | — | **Nol** |
| Lisensi | CC-BY-NC-SA-4.0 | CC0 | CC-BY-SA |

---

## Temuan Jember

Dataset utama. Ini satu-satunya sumber percakapan spontan in-domain yang kita punya.

### J1 — Percakapannya memang bercampur, dan itu mayoritas

**74,1% segmen** mengandung kata Jawa dan Indonesia sekaligus dalam satu kalimat yang sama.

| Porsi kata Jawa dalam segmen | Segmen | |
|---|---:|---|
| 0% (Indonesia penuh) | 135 | `▌` 2% |
| 0–20% | 51 | `▌` 1% |
| 20–40% | 378 | `██` 6% |
| 40–60% | 1.452 | `███████` 22% |
| 60–80% | 2.739 | `█████████████` 41% |
| 80–100% (Jawa penuh) | 1.924 | `█████████` 29% |

> [!check] Artinya
> Premis kompetisi terbukti di data. Model yang hanya dilatih bahasa Jawa akan kehilangan nilai pada bagian Indonesia, dan sebaliknya. **Ukur ketepatan kata Jawa dan kata Indonesia secara terpisah** — angka gabungan bisa menutupi satu sisi yang memburuk.

### J2 — Ejaan tidak konsisten pada 10,8% kata

Korpus memakai lima bentuk huruf e. Ada **210 kata** yang ditulis dengan lebih dari satu ejaan.

| Bentuk | Contoh | Kemunculan |
|---|---|---:|
| `e` biasa | terus | 18.590 |
| `ê` circumflex | têrus | 5.374 |
| `è` grave | ndèk | 4.833 |
| `ě` caron | těrus | 820 |
| `é` acute | — | 1 |

Contoh paling mencolok: **`těrus` 759 kali** tapi **`têrus` hanya 4 kali**. Contoh lain: `mbêk` 96 / `mbèk` 74 / `mbek` 7. Ini bukan variasi bahasa — ini perbedaan kebiasaan antar pencatat transkrip.

> [!danger] Kenapa ini menyentuh skor
> Normalisasi pra-penilaian yang disebut penyelenggara mencakup penghapusan tag `[laugh]`, penanda ucapan tak terdengar, sebagian elipsis, dan sebagian tanda baca. **Diakritik tidak disebut sama sekali.** Kalau tidak diseragamkan, `têrus` dan `těrus` dihitung sebagai dua kata berbeda — sampai sekitar 10% nilai ditentukan oleh hal yang tidak ada hubungannya dengan kemampuan model mendengar. Ini [[#Pertanyaan untuk penyelenggara|pertanyaan nomor satu]].

### J3 — Anotasinya rapi, tapi ada 41 penanda waktu rusak

Dari 6.679 segmen, **41 berdurasi nol atau negatif**. Terburuk di rekaman 63: waktu selesai `0:00:10` padahal mulai `0:00:40` — minus 30 detik. Rekaman 63 juga satu-satunya yang punya segmen bertumpuk (3 buah). Buang sebelum training.

Selain itu strukturnya bagus: 208 mp3 cocok persis dengan 208 nomor rekaman di TSV, tidak ada yang yatim di kedua arah, dan **semua segmen di bawah 30 detik** sehingga langsung muat di Whisper tanpa perlu dipotong lagi.

### J4 — Tidak ada audio cadangan yang belum ditranskrip

Coverage anotasi **99,6%** — sisa yang belum hanya sekitar 2 menit dari 10 jam. Gagasan memakai audio tanpa transkrip untuk self-training/pseudo-labelling **tidak ada bahannya di sini**.

### J5 — Notasi disfluency ternyata bersih

Nol tag `[...]`, `(...)`, atau `<...>`. Yang ada hanya elipsis `...` (718 segmen) dan reduplikasi (1.558 segmen: `wong-wong` 123, `arèk-arèk` 45, `rata-rata` 27). Pipeline normalisasi teks jadi jauh lebih sederhana daripada dugaan awal.

### J6 — Rekamannya panjang dan bervariasi

Median rekaman 100 detik, terpanjang 20 menit, terpendek 6 detik. Median 18 segmen per rekaman. Sample rate campur: **44,1 kHz pada 89 rekaman, 48 kHz pada 119 rekaman**, semua mono. Perlu diseragamkan ke 16 kHz.

---

## Temuan Common Voice Indonesia

Di feasibility study ini "hipotesis yang diuji". Setelah dilihat isinya, kualitasnya sebagai bahan latihan lebih lemah daripada yang terlihat dari angka 35,94 jam.

### C1 — Split resmi tidak layak dipakai apa adanya

| Split | Klip | Jam | Speaker | Klip/speaker |
|---|---:|---:|---:|---:|
| validated | 30.465 | 35,94 | 468 | 65 |
| **train** | 4.981 | 7,70 | **4** | **1.245** |
| dev | 3.489 | 4,02 | 43 | 81 |
| test | 3.700 | 4,25 | 418 | 9 |
| other | 27.531 | 28,72 | 483 | 57 |
| invalidated | 2.808 | 2,73 | 190 | 15 |

Split `train` bawaan berisi 7,7 jam **dari 4 orang saja**. Melatih dengan itu berarti model hanya mendengar empat suara. **Susun split sendiri dari `validated.tsv`.**

### C2 — Bahkan `validated` sangat terkonsentrasi

Ini yang lebih penting daripada C1 dan mudah terlewat, karena angka "468 speaker" terdengar sehat.

| | Porsi jam validated |
|---|---:|
| 1 speaker teratas | 9,1% |
| 10 speaker teratas | **59,1%** |
| 25 speaker teratas | 74,7% |
| 100 speaker teratas | 92,6% |

Hanya **178 speaker punya ≥10 klip**, dan 80 speaker punya ≥50 klip. Jadi 35,94 jam itu efektifnya didominasi belasan orang. Kalau menyusun split sendiri, **batasi jumlah klip per speaker** supaya tidak didominasi segelintir suara.

### C3 — Ada kebocoran speaker antar split resmi

| | train | dev | test | other | invalidated |
|---|---:|---:|---:|---:|---:|
| **test** | 0 | 0 | 418 | **257** | 120 |
| **train** | 4 | 0 | 0 | 4 | 4 |

`train` memang bersih dari `dev` dan `test`. Tapi **257 dari 418 speaker di `test` juga muncul di `other`**. Kalau `other` dipakai sebagai tambahan data latih, angka pada `test` resmi jadi tidak jujur. Karena kita toh akan menyusun split sendiri, ini lebih merupakan peringatan kalau ada yang ingin memakai `test` CV sebagai pembanding.

### C4 — Kalimatnya banyak diulang

30.465 klip tetapi hanya **12.170 kalimat unik** — faktor pengulangan 2,5×. Kalau dipakai, pertimbangkan deduplikasi teks supaya model tidak menghafal kalimat.

### C5 — Demografinya timpang, dan metadata aksen hampir kosong

| Kolom | Isi |
|---|---|
| Umur | remaja + 20-an = **65,7%** dari seluruh klip |
| Gender | laki-laki 64,7% dari yang mengisi (14.030 vs 7.647) |
| Aksen | **96,3% kosong** |
| Variant | 100% kosong |

Tapi ada temuan kecil yang berguna: dari yang mengisi kolom aksen, **439 klip berlabel Jawa** — `Javanese` 154, `jawa` 53, dan satu label gabungan berisi *Jawa Tengah / medhok / surakarta / tionghoa / bindeng* sebanyak 232. Itu bahasa Indonesia beraksen Jawa — jauh lebih dekat ke domain target daripada CV acak. Kecil, tapi ini subset yang layak diuji lebih dahulu daripada seluruh CV.

### C6 — Kualitas anotasinya wajar

Median 2 up-vote per klip, dan **8,6% klip punya minimal 1 down-vote** meski sudah masuk `validated`. Tidak mengkhawatirkan, tapi kalau ingin bersih, buang yang `down_votes >= 1`.

---

## Temuan TTS Central Javanese

Di feasibility study statusnya "opsional". Setelah diukur, ini justru kandidat tambahan terkuat — lihat [[#Temuan lintas dataset]].

### T1 — Strukturnya rapi dan transkripnya lengkap

4.599 klip WebM tersebar di **93 folder** `recordings (N)`, masing-masing ~50 klip dengan satu `mapping.tsv` berkolom `audio_filename` dan `sentence`. Semua 48 kHz mono, klip 1,74–13,2 detik (median 6,03).

Estimasi total **7,89 jam**, cocok dengan 7 jam 45 menit yang tertulis di halaman dataset — validasi bagus bahwa pembacaannya benar.

Semua 4.630 baris transkrip terpasangkan ke nama file, dan **tidak ada audio yatim**.

### T2 — Ada cacat kecil yang perlu dibersihkan

- ~~**30 transkrip menunjuk file audio yang tidak ada.**~~
- Dari 4.599 file hanya **4.549 nama unik** — sekitar 50 file duplikat lintas folder. Karena nama filenya hash, nama sama berarti isi sama.

Kecil, tapi harus dibuang supaya tidak menghitung data yang sama dua kali.

> [!failure] Kedua cacat di atas salah didiagnosis — dikoreksi 3 September 2026
> Ditemukan saat NB 06 fase 1 benar-benar membuka file audionya, dan diverifikasi terhadap zip aslinya.
>
> **1. Tidak ada 30 audio yang hilang.** Ketiga puluh baris itu adalah **transkrip multi-baris**: kalimatnya mengandung newline, jadi baris nama file berakhir di tab-nya dengan teks kosong, dan sisa kalimatnya jadi baris yatim yang dibaca sebagai nama file mustahil oleh pembaca tabel mana pun. Dibaca ulang baris demi baris, **31 transkrip pulih utuh dan audio yang hilang jadi 0**. Angkanya 31, bukan 30 — pembacaan lama melewatkan satu.
>
> **2. Bukan ~50 file duplikat lintas folder, melainkan satu folder yang terduplikasi.** Salinan lokal punya 92 folder dan nol duplikat; mount Kaggle punya 93, dan `recordings (93)` mengulang 50 klip. Jadi yang perlu dibuang bukan file-file yang tersebar, melainkan satu folder.
>
> Keduanya sudah ditangani di `notebooks/06-mix-build.ipynb` dan tidak memengaruhi angka jam mana pun di bagian ini.

### T3 — Nol diakritik, dan ini bentrok dengan Jember

Transkrip TTS **tidak memakai diakritik sama sekali** (`non-ASCII chars: []`), sedangkan Jember memakai 5.374 `ê` dan 4.833 `è`.

> [!warning] Konsekuensi
> Menggabungkan keduanya mentah-mentah memberi model sinyal yang bertentangan untuk bunyi yang sama. **Penyeragaman ejaan menjadi syarat sebelum mencampur, bukan pilihan.**

### T4 — Teksnya paragraf naratif yang nyambung

Bukan kalimat lepas. Contoh berurutan dari satu folder:

> Koyo sing sakdurunge dibahas, ngeki kado kuwi ora melulu ngeki barang.
> Ning Islam, ngeki senyuman ning wong liyo iku wes termasuk ngeki hadiah mergo wes nyenengke wong liyo.

Kosakatanya Jawa inti: `sing, iku, ning, iso, lan, ora, nggo, dadi, kuwi, karo, ono, wong, okeh, yen, banget, seko, wes, dewe, luwih, mergo`. Selain untuk akustik, teks ini juga bahan yang layak untuk language modeling.

### T5 — Jumlah speaker tidak diketahui

93 folder **belum tentu 93 orang**. Tidak ada metadata speaker sama sekali dan nama file hanya hash. Ada juga folder bersarang (`recordings (11)/recordings (3)`), jadi jumlah folder tidak bisa langsung dianggap jumlah sesi.

---

## Temuan lintas dataset

### X1 — Dataset "opsional" justru menutup kosakata paling banyak

Berapa persen kata yang muncul di Jember juga tersedia di dataset pendukung:

| Sumber | Jam | Cakupan kata Jember | |
|---|---:|---:|---|
| Common Voice Indonesia | 35,94 | 41,5% | `████████` |
| **TTS Central Javanese** | **7,89** | **56,2%** | `███████████` |
| Keduanya digabung | 43,83 | 69,5% | `██████████████` |

TTS menutup lebih banyak dengan **seperempat jumlah jam**. Tambahan CV di atas TTS hanya **13,3 poin**, dan sebagian besar berupa kata Indonesia — yang justru memicu kegagalan Whisper yang sudah teridentifikasi (menormalisasi kata Jawa jadi Indonesia).

Ada 3.940 tipe kata Jawa di TTS yang tidak ada di Jember: `iso, ono, yen, ndue, meneh, kabeh, mergane, menungso, moco, mbien, ngeki, liyo, amergo, podo`.

> [!warning] Tapi jangan langsung dipakai
> Cakupan kosakata **bukan** jaminan manfaat akustik. TTS adalah bacaan naskah dialek Jawa Tengah; target kita percakapan spontan dialek Jember/Pandhalungan. Domain gap-nya sama persis dengan keberatan terhadap CV. Yang berubah adalah **urutan pengujian**, bukan kesimpulannya.

### X2 — Jurang domain bacaan vs spontan

| | Panjang klip | Token per kalimat |
|---|---:|---:|
| Jember (spontan) | median 5,0 dtk, p95 12,0 | 9 |
| Common Voice (bacaan) | median 3,96 dtk, p95 7,03 | 6 |
| TTS (bacaan) | median 6,03 dtk | — |

Whisper mengisi setiap masukan sampai 30 detik. Klip bacaan yang pendek membuang komputasi dan menggeser kebiasaan model menjauh dari target.

### X3 — Tokenizer Whisper boros pada kata Jawa, parah pada kata ulang

| Kelompok kata | Potongan per kata |
|---|---:|
| Common Voice Indonesia | 2,47 |
| Jember | 2,72 |
| Jember, kata yang tak ada di CV | 2,87 |

Yang berat adalah reduplikasi berdiakritik: **`cêdhêk-cêdhêk` → 13 potongan**, `sênêng-sênêng` → 9. Padahal ada 1.558 segmen yang memuat kata ulang. Ini biaya decode nyata, dan sebagian akan hilang sendiri kalau diakritik diseragamkan.

---

## Yang berubah dari feasibility study

| Hal | Rencana semula | Setelah melihat data |
|---|---|---|
| Urutan uji dataset | Jember → campur Common Voice | Jember → **campur TTS lebih dahulu** |
| Status TTS Central Javanese | Opsional | **Kandidat utama** untuk diuji |
| Status Common Voice | Hipotesis utama | Turun jadi kandidat lemah; subset beraksen Jawa lebih menjanjikan daripada keseluruhannya |
| Penyeragaman ejaan | Disebut sebagai risiko umum | **Terukur 10,8%**; jadi syarat sebelum mencampur dataset |
| Pembagian data uji | Belum ditentukan | **Harus dikelompokkan per rekaman**, bukan per kalimat |
| Pseudo-labelling | — | Tidak mungkin, sisa audio hanya 2 menit |

### Soal pembagian data uji

Tabel Jember tidak mencantumkan siapa yang berbicara, hanya nomor rekaman. Membagi acak per kalimat akan menaruh suara orang yang sama di sisi latihan dan sisi ujian sekaligus, sehingga nilainya terlihat lebih bagus daripada kemampuan sebenarnya.

| Disisihkan | Rekaman | Jam uji | Jam latih |
|---|---:|---:|---:|
| 10% | 20 | 1,08 | 8,89 |
| **15%** | **25** | **1,52** | **8,46** |
| 20% | 42 | 2,06 | 7,91 |

---

## Pertanyaan untuk penyelenggara

| Prioritas | Pertanyaan | Kenapa mendesak |
|---|---|---|
| **Tinggi** | Apakah normalisasi pra-penilaian menyeragamkan diakritik (`ê`, `è`, `ě` → `e`)? | Menentukan pipeline teks, keputusan mencampur dataset, dan sampai ~10% nilai WER |
| **Tinggi** | Kapan submission dibuka, dan seperti apa spesifikasi container serta batas waktu inference? | Menentukan apakah pengemasan bisa selesai sebelum tenggat |
| Sedang | Audio uji berupa potongan yang sudah dipisah, atau rekaman utuh yang harus dipotong sendiri? | Menentukan apakah perlu membangun pemotong otomatis |
| Sedang | Berapa batas jumlah submission per hari? | Menentukan seberapa berani mencoba di leaderboard |

Item pertama adalah tambahan baru untuk tabel "Informasi yang masih belum diketahui" di [[feasibility-study|Feasibility Study - Mozilla Lost in Transcription]].

## Langkah berikutnya

- [ ] **Notebook 02 — baseline.** Normalisasi teks, split per rekaman, latih Whisper pada Jember saja sebagai titik acuan.
- [ ] Buang 41 segmen bertimestamp rusak dan 30 transkrip TTS yang menunjuk file hilang.
- [ ] Siapkan **dua versi teks**: asli dan diakritik-diseragamkan, sampai penyelenggara menjawab.
- [ ] Percobaan 1: Jember + TTS Central Javanese (ejaan diseragamkan) — hanya 8 jam, murah diuji.
- [ ] Percobaan 2: Jember + 439 klip CV beraksen Jawa, bukan seluruh CV.
- [ ] Ukur WER kata Jawa dan kata Indonesia **terpisah** di setiap percobaan.

## Batasan analisa ini

- Angka percampuran bahasa adalah **perkiraan**, bukan pelabelan manual. Metodenya membandingkan kata Jember dengan kosakata Common Voice Indonesia ditambah daftar kata khas Jawa. Arahnya dapat dipercaya, angka pastinya tidak.
- **Jumlah speaker Jember dan TTS tidak diketahui.** Split hanya bisa dijamin terpisah per rekaman/folder, bukan per orang.
- **Kualitas suara belum diperiksa** — derau, gema, suara bertumpuk. Perlu analisa sinyal, bukan pembacaan metadata.
- **Label dialek per rekaman** (Jember atau Pandhalungan) tidak tersedia di data.
- Kandungan bahasa **Madura** disebut di deskripsi korpus tapi tidak ada penandanya di data, jadi tidak terukur.

## Cara reproduksi

1. Buka `notebooks/01-dataset-eda.ipynb` di Kaggle, attach ketiga dataset.
2. Accelerator **None**, Internet **On**. Run All (~5–12 menit).
3. Output tab → Download all → unzip ke root repo. Hasilnya masuk sendiri ke `findings/01-dataset-eda/`.

> [!caution] Jangan re-run sebagian
> Cell 1 mereset akumulator `FINDINGS`, jadi menjalankan ulang sebagian cell menghasilkan digest yang tidak lengkap. Cell terakhir akan memperingatkan kalau itu terjadi.
