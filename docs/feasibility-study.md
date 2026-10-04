---
title: "Feasibility Study — Mozilla Lost in Transcription: Indonesian–Javanese ASR"
aliases:
  - Feasibility Study - Mozilla Lost in Transcription
  - Mozilla Indonesian–Javanese ASR Feasibility Study
  - Lost in Transcription Feasibility Study
tags:
  - research
  - competition
  - asr
  - javanese
  - indonesian
  - code-switching
status: draft-for-team-review
created: 2026-08-17
updated: 2026-08-17
deadline: 2026-09-17T06:59:00+07:00
review_meeting: 2026-08-18T13:00:00+07:00
team_size: 3
source_type: official-primary
---

# Feasibility Study — Mozilla Lost in Transcription: Indonesian–Javanese ASR

> [!summary] Verdict
> **GO.** Proyek ini layak dikerjakan sebagai riset sekaligus dikejar sebagai kompetisi, dengan konfigurasi tim tiga orang dan akses Kaggle yang tersedia. Compute **bukan** faktor pembatas. Risiko terbesar adalah waktu yang tersisa sekitar empat minggu dan belum lengkapnya spesifikasi submission/runtime.
>
> **Ibaratnya:** ini seperti survei jalur pendakian sebelum ajak seluruh tim naik gunung — bukan mendaki dulu baru sadar salah jalur. Yang dicek: alat (compute) cukup atau tidak, jalurnya (aturan lomba) sudah jelas atau masih berkabut, dan waktu tersisa masih cukup untuk sampai puncak sebelum matahari terbenam (deadline).

> [!question] Keputusan yang diminta pada rapat 18 Agustus 2026
> 1. **Commit atau tidak** pada track Indonesian–Javanese sampai 16 September.
> 2. **Konfirmasi pembagian lane** dan PIC pada tabel [[#Alokasi tim dan accelerator]].
> 3. **Tunjuk pemilik** untuk setiap item pada [[#Informasi yang masih belum diketahui]], dengan tenggat 24 Agustus.
> 4. **Setujui anggaran** — rencana dasar Rp 0; putuskan apakah dana cadangan pada [[#Biaya Proyek]] disiapkan.

> [!info] Status informasi
> Studi ini dibuat pada **17 Agustus 2026 (WIB)**. Deadline publik tercantum **16 September 2026, 23:59 UTC**, yaitu **17 September 2026, 06:59 WIB**. Halaman publik masih menyatakan bahwa submission akan dibuka kemudian, sehingga status submission dan spesifikasi runtime perlu dikonfirmasi pada fase berikutnya.

> [!danger] Update 22 September 2026 — deadline mundur lagi
> Deadline sekarang **2 Oktober 2026, 00:00 UTC** (07:00 WIB, 2 Oktober). Tanggal 25 September di callout bawah ini juga sudah usang. Dokumen ini tetap snapshot 17 Agustus; info terkini ada di [[rules-review-2026-08-23#Update 22 September 2026 — situs, forum, dan runtime repo dicek ulang|Kaji Ulang Peraturan - 23 Agustus 2026 > Update 22 September 2026 — situs, forum, dan runtime repo dicek ulang]].

> [!danger] Update 25 Agustus 2026 — deadline dan status submission berubah
> Situs kompetisi dibaca ulang penuh hari ini. **Deadline resmi ternyata 25 September 2026, tengah malam UTC** — bukan 16 September seperti tertulis di seluruh dokumen ini. **Submission sudah dibuka** (270 peserta terdaftar per hari ini), jadi seluruh pertanyaan tentang "kapan submission dibuka" di bawah sudah terjawab. Spesifikasi runtime NB 08 juga sudah resmi (Python 3.12, 1× A100 80GB, limit eksekusi 2 jam, tanpa internet). Detail lengkap dan sumbernya ada di [[rules-review-2026-08-23|Kaji Ulang Peraturan - 23 Agustus 2026]]. Tanggal dan angka hadiah di bawah ($4.000/$2.000 track ini, deadline 16 September) **belum diperbarui** — baca sebagai snapshot 17 Agustus, bukan kondisi saat ini.

## Executive Summary

Kompetisi **Lost In Transcription** mengevaluasi ASR untuk dialog bilingual nyata pada tiga pasangan bahasa, termasuk Indonesian–Javanese. Track ini menawarkan hadiah **USD 4.000** untuk peringkat pertama dan **USD 2.000** untuk kedua. Sumber: [halaman resmi kompetisi](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/1/).

Proyek ini menarik karena:

- dataset utama hanya sekitar 10 jam sehingga eksperimen individual masih realistis;
- task mencakup spontaneous speech, code-switching, dialek Jember/Pandhalungan, lexical borrowing, dan disfluency;
- open-weight pretrained models dan external data diperbolehkan dengan ketentuan tertentu;
- tersedia data tambahan Indonesian dan berbagai dialek Jawa di Mozilla Data Collective (MDC).

- biaya uangnya nol: bobot Whisper (MIT) dan XLS-R (Apache-2.0), dataset MDC, serta compute Kaggle seluruhnya gratis;
- tim tiga orang dapat menjalankan lane Whisper, CTC, dan data preparation secara paralel.

Keterbatasan utama:

- waktu tersisa sekitar empat minggu;
- detail test set, runtime container, batas inference, dan kuota submission belum lengkap;
- data utama kecil, spesifik dialek, dan juga mengandung Madura serta Inggris;
- fine-tuning standar kemungkinan menghasilkan baseline yang baik, tetapi belum tentu kompetitif untuk peringkat atas.

Strategi yang direkomendasikan adalah membangun pipeline kompetisi yang stabil terlebih dahulu, lalu menguji satu atau dua hipotesis riset yang terarah. Jangan memulai dengan arsitektur baru atau model 7B.

### Jenis pernyataan

- **Fakta** — dinyatakan sumber resmi.
- **Interpretasi** — kesimpulan yang ditarik dari fakta.
- **Hipotesis** — dugaan teknis yang perlu diuji.
- **Rekomendasi** — tindakan yang disarankan.
- **Asumsi** — informasi yang belum dikonfirmasi penyelenggara.

## Competition Overview

### Apa kompetisinya?

**Fakta.** Lost In Transcription adalah kompetisi ASR code-switched pada tiga track:

1. North American Spanish–English
2. Spanish–Nahuatl
3. Indonesian–Javanese

Peserta diminta membangun sistem yang mentranskripsikan percakapan bilingual alami berbentuk voice-note dialogue. Data mengandung code-switching dan lexical borrowing yang berat. Sumber: [competition overview](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/1/).

Untuk track Indonesian–Javanese, batas leksikal antara bahasa Jawa dan Indonesia tidak selalu jelas. Penyelenggara secara khusus menyebut bahwa sebagian kata sulit ditetapkan secara tegas sebagai milik salah satu bahasa. Ini membuat word-level language identification menjadi lebih rumit.

### Input dan output

**Fakta.** Berdasarkan [problem description resmi](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/2/):

- training utama menggunakan audio MP3 tingkat sesi dan TSV berisi timestamp serta transkripsi;
- test input akan berupa klip audio `.mp3`;
- sistem harus menghasilkan transkripsi untuk setiap klip;
- output direncanakan sebagai CSV dengan kolom `audio_filename` dan `transcript`;
- kompetisi menggunakan **code execution submission**: peserta mengirim model dan kode inference dalam ZIP untuk dijalankan di container penyelenggara.

Detail final struktur ZIP, repository runtime, dan resource constraints belum tersedia pada halaman publik.

### Penilaian

**Fakta.** Metrik utama adalah **Word Error Rate (WER)**:

$$
WER = \frac{S + D + I}{N}
$$

Substitution, deletion, dan insertion dihitung pada level kata. Nilai lebih rendah lebih baik, dan partial word match tetap dianggap salah.

Sebelum scoring, penyelenggara akan melakukan normalisasi yang mencakup:

- penghapusan tag metalinguistik seperti `[laugh]`;
- penghapusan penanda unintelligible speech;
- penghapusan sebagian ellipsis;
- penghapusan punctuation tertentu.

Pemenang kuantitatif ditentukan menggunakan **private leaderboard**, yang dapat berbeda dari leaderboard publik. Jika skor identik, submission yang lebih awal mendapat peringkat lebih tinggi. Sumber: [problem description](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/2/) dan [official rules](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/rules/).

### Hadiah dan tanggal

| Track Indonesian–Javanese | Hadiah |
|---|---:|
| Peringkat 1 | USD 4.000 |
| Peringkat 2 | USD 2.000 |

Terdapat bonus **USD 2.000** untuk rata-rata WER terbaik pada seluruh tiga track. Agar memenuhi syarat, tim pada ketiga track harus memiliki anggota yang sama, walaupun boleh menggunakan model berbeda.

- **Deadline resmi:** 16 September 2026, 23:59 UTC
- **Konversi WIB:** 17 September 2026, 06:59 WIB
- **Status submission:** ambigu; halaman menampilkan countdown tetapi masih menyatakan bahwa submission akan dibuka kemudian

## Dataset & Problem

### Dataset utama

Track Indonesian–Javanese menyorot [Jember Javanese Spontaneous Speech Corpus](https://mozilladatacollective.com/datasets/cmlgm5a94008kny07nz2intus).

| Properti | Nilai |
|---|---|
| Durasi | Sekitar 10 jam |
| Ukuran | 271,65 MB |
| Audio | 208 MP3 sesi, mono, 44,1 kHz |
| Transkripsi | 6.679 utterance |
| Alignment | Timestamp `start`/`end` dalam TSV |
| Lokasi | Jember, Jawa Timur |
| Varietas | Javanese Jember dan Pandhalungan |
| Bahasa yang muncul | Jawa, Indonesia, Madura, Inggris |
| Gaya | Spontan, informal/semi-formal |
| Lisensi | CC-BY-NC-SA-4.0 |

Audio belum dipotong menjadi utterance individual. Segmentasi perlu dilakukan menggunakan timestamp. Corpus mengandung code-mixing, code-switching, reduplikasi, kata terpotong, disfluency, serta variasi fonologis dan leksikal. Transkripsi menggunakan alfabet Latin, diakritik, dan konvensi ortografi Jawa dengan rujukan Bausastra Jawa.

**Interpretasi.** Nama track “Indonesian–Javanese” menyederhanakan kondisi data karena training utama juga mengandung Madura dan Inggris. Model yang memaksakan klasifikasi biner Jawa/Indonesia berisiko memperburuk transkripsi.

### Apakah data dapat dipakai untuk training?

**Fakta.** Ya. Dataset Jember secara eksplisit ditampilkan penyelenggara sebagai highlighted training dataset. Lisensinya membatasi penggunaan pada riset dan non-komersial serta melarang voice cloning, dubbing, identifikasi speaker, dan eksploitasi komersial.

**Interpretasi.** Penggunaannya untuk kompetisi jelas dikehendaki penyelenggara, tetapi model turunan tidak boleh langsung diasumsikan aman untuk penggunaan komersial di luar kompetisi.

### Syarat kelayakan dataset

Sebuah dataset hanya boleh masuk pipeline jika lolos **seluruh** syarat berikut. Gagal pada satu syarat saja cukup untuk mengeliminasi.

| # | Syarat | Sumber |
|---|---|---|
| **S1** | Tim memiliki seluruh hak dan izin yang diperlukan | Official rules |
| **S2** | Sudah berada di MDC, **atau** dapat dipublikasikan ke MDC setelah kompetisi — artinya tim harus punya hak **redistribusi**, bukan sekadar hak pakai | Official rules |
| **S3** | Seluruh dependency dapat diserahkan ke penyelenggara untuk verifikasi | Official rules |
| **S4** | Lisensinya **diketahui** dan kompatibel dengan kewajiban rilis MPL 2.0 | Official rules |
| **S5** | Seluruh ketentuan tambahan pemilik data sudah dipenuhi, misalnya izin tertulis | Halaman dataset |
| **S6** | Bukan test set kompetisi, dan tidak dipakai untuk pseudo-labeling test set | Official rules |

S2 adalah saringan paling tajam dan paling sering disalahpahami. Berada di MDC melewatkan S2 secara otomatis, tetapi **tidak** melewatkan S4 dan S5 — lisensi dan ketentuan tambahan tetap berlaku per-dataset.

> [!note] Catatan tentang S4 dan lisensi NC/SA
> Dataset utama Jember berlisensi CC-BY-NC-SA-4.0, sementara penyelenggara yang sama mewajibkan solusi pemenang dirilis di bawah MPL 2.0. Penyelenggara jelas tidak memandang lisensi data merambat ke bobot model, karena jika sebaliknya, kompetisi mereka sendiri tidak akan konsisten. Dengan penalaran itu, dataset ber-CC-BY-SA juga tidak dianggap gugur. Tetap perlu dikonfirmasi ke forum sebagai item Phase 1, tetapi statusnya klarifikasi, bukan blocker.

### Dataset yang dipakai

Hanya tiga dataset di bawah ini yang lolos seluruh syarat dan boleh masuk pipeline.

| Dataset | Volume | Lisensi | Peran |
|---|---|---|---|
| [Jember Javanese Spontaneous Speech Corpus](https://mozilladatacollective.com/datasets/cmlgm5a94008kny07nz2intus) | ±10 jam | CC-BY-NC-SA-4.0 | **Dataset utama.** In-domain, di-highlight penyelenggara. Basis seluruh baseline dan validation split. |
| [Common Voice Indonesian 26.0](https://mozilladatacollective.com/datasets/cmqinqwef00xonr07z4vbfovw) | 33,76 jam tervalidasi (dari 67,38 jam) | **CC0** | **Hipotesis yang diuji, bukan bahan yang otomatis dicampur.** Lihat [[#Mengapa data Indonesian dipakai pada task Javanese]]. |
| [TTS Central Javanese](https://mozilladatacollective.com/datasets/cml5bn4k900aame07u0rwidcg) | 7 jam 45 menit | CC-BY-SA | **Opsional.** Satu-satunya sumber variasi dialek Jawa yang lolos. Scripted dan beda dialek, jadi hanya dipertahankan bila terbukti menurunkan WER. |

Corpus Jember tetap menjadi dataset utama dan baseline. Dua dataset lainnya adalah **opsi** untuk augmentation atau pre-fine-tuning, dan hanya dipertahankan apabila menurunkan WER pada validation split Jember.

#### Mengapa data Indonesian dipakai pada task Javanese

Pertanyaan yang wajar muncul: kalau targetnya transkripsi bahasa Jawa, mengapa menambahkan 33 jam bahasa Indonesia?

**Karena task-nya bukan ASR Jawa, melainkan ASR Indonesia–Jawa yang code-switched.** Nama track-nya sendiri Indonesian–Javanese, datanya berbentuk dialog bilingual dengan pergantian bahasa di dalam satu utterance, dan tabel dataset Jember mencantumkan Jawa, Indonesia, Madura, dan Inggris sebagai bahasa yang muncul. Penyelenggara bahkan menyebut bahwa batas leksikal Jawa–Indonesia sering tidak tegas. Kata Indonesia di test set bukan gangguan yang bisa diabaikan — kalau salah ditranskripsi, WER tetap naik.

Alasan teknis penambahannya:

1. **Volume.** Data in-domain hanya ±10 jam, terlalu tipis untuk full fine-tune tanpa overfit.
2. **Transfer fonetik.** Jawa dan Indonesia berbagi sebagian besar inventori fonem dan sama-sama beraksara Latin, sehingga representasi akustiknya sebagian terpakai lintas bahasa.
3. **Lisensi CC0.** Tanpa hambatan hilir sama sekali.

> [!warning] Risiko yang harus diawasi
> Penambahan ini berpotensi **memperparah kegagalan yang sudah teridentifikasi pada Whisper**, yaitu kecenderungan menormalisasi kata Jawa menjadi kata Indonesia. Semakin banyak data Indonesian, semakin condong model ke arah itu. Ditambah lagi Common Voice adalah read speech yang bersih dan berkalimat lengkap, sementara target kita adalah voice note spontan yang disfluent dan noisy. Whisper juga sudah melihat bahasa Indonesia dalam jumlah besar saat pretraining, sehingga nilai tambah marginalnya belum tentu besar.

**Rekomendasi guard.** WER total dapat menyembunyikan masalah ini, karena penurunan pada kata Indonesia bisa menutupi kenaikan pada kata Jawa. Karena itu **ukur WER secara terpisah untuk kata asal-Jawa dan kata asal-Indonesia**. Jika Focused mix menurunkan WER total tetapi menaikkan WER kata Jawa, tim sedang menukar akurasi Jawa demi akurasi Indonesia — keputusan yang harus disadari, bukan terjadi tanpa sengaja.

**Urutan eksperimen.** Jalankan Core (Jember saja) lebih dahulu sebagai baseline, baru Focused mix. Jika Focused mix tidak menang pada metrik terpisah di atas, Common Voice Indonesian dibuang tanpa penyesalan.

### Dataset yang dieliminasi

| Dataset | Gagal di | Alasan |
|---|---|---|
| [Javanese TTS Banyumasan](https://mozilladatacollective.com/datasets/cmmamtaf104nemh07xa9e7sdx) | **S5** | Meski berada di MDC dan berlabel CC-BY-SA, halaman datasetnya meminta **izin tertulis** yang belum dimiliki tim. Mengurus izin di tengah jadwal empat minggu tidak sebanding dengan 9 jam 40 menit data scripted yang berbeda domain. |
| [TTS Javanese Ngapak](https://mozilladatacollective.com/datasets/cmlgmf58l0096nx07tahttd6y) | **S4** | Lisensinya tidak tercantum dan belum diverifikasi. Tanpa kepastian lisensi, dataset ini tidak dapat dipertanggungjawabkan terhadap kewajiban rilis MPL 2.0. |
| [Podcast Hari Minggoean](https://mozilladatacollective.com/datasets/cmhlvswz200fio007c7szypw8) | **S4** + kegunaan | Lisensi tidak tercantum. Terlepas dari itu, hanya ada **satu speaker**, sehingga nilainya untuk acoustic training mendekati nol. Paling banter berguna sebagai korpus teks untuk language modeling — dan itu pun tidak menjadi prioritas. |
| **Bojonegoro** | **S2** | Disebut pada skenario Broad dialect mix dan pada peluang riset dialect-aware transfer, tetapi **tidak memiliki tautan, volume, maupun lisensi**. Keberadaannya di MDC belum terkonfirmasi, sehingga tidak dapat dinilai sama sekali. |
| Scraping YouTube, podcast, radio | **S1** + **S2** | Tim tidak memiliki hak atas materinya, dan tidak dapat mempublikasikannya ulang ke MDC. |

### Dataset yang ditunda

| Dataset | Status | Pemicu peninjauan |
|---|---|---|
| [Common Voice Spontaneous Javanese 4.0](https://mozilladatacollective.com/datasets/cmqi294n3004mmf07wvybp3fn) | Lisensi **CC0** dan domainnya paling dekat dengan Jember, sehingga secara kelayakan **lolos semua syarat**. Yang menjadi masalah adalah volume: dari 232 klip, **221 transkripsinya masih pending** dan belum ada split tervalidasi. Sisa yang benar-benar terpakai terlalu kecil untuk training. | Masukkan ke pipeline jika transkripsinya tervalidasi sebelum akhir Phase 3 (31 Agustus). |

**Interpretasi.** Setelah penyaringan, volume yang benar-benar tersedia adalah **±51 jam** — jauh di bawah ±70–80 jam yang sempat diasumsikan. Ini tidak mengubah verdict, karena analisis kita sendiri menyimpulkan bahwa kesesuaian domain lebih menentukan daripada jumlah jam, dan skenario Focused mix yang menjadi kandidat model final tetap dapat dipenuhi sepenuhnya. Yang hilang hanyalah skenario Broad dialect mix, yang memang sudah ditandai berisiko negative transfer dan bukan prioritas.

### Tantangan data utama

- Training in-domain hanya sekitar 10 jam.
- Dialek Jember/Pandhalungan berbeda dari Jawa standar, dan satu-satunya sumber dialek pembanding yang lolos penyaringan adalah Central Javanese.
- Code-switching terjadi di dalam utterance.
- Madura dan Inggris menciptakan multilingual interference tambahan.
- Voice-note audio dapat mengandung noise, channel compression, jeda, dan disfluency.
- WER sensitif terhadap ortografi dan diakritik.
- Jumlah speaker dan strategi split belum dijelaskan secara publik.
- Karakteristik rinci test set belum dirilis.

## Technical Feasibility

### Kandidat baseline

#### Whisper

Whisper sangat masuk akal sebagai baseline. Model ini dilatih menggunakan 680.000 jam data multilingual dan dirancang untuk transfer zero-shot. Penyelenggara juga mencantumkannya sebagai referensi awal. Sumber: [Whisper paper](https://arxiv.org/abs/2212.04356).

Kelebihan:

- baseline zero-shot cepat;
- decoder seq2seq dapat menangani campuran kosakata;
- relatif kuat terhadap noise dan variasi audio.

Kekurangan:

- language token tunggal dapat menjadi kendala untuk code-switching;
- dapat menormalisasi kata Jawa menjadi kata Indonesia;
- berisiko hallucination pada jeda atau noise;
- output orthography belum tentu cocok dengan reference.

#### wav2vec2/XLS-R atau MMS

MMS menggunakan representasi wav2vec2 dan menyediakan ASR untuk lebih dari 1.000 bahasa. Sumber: [MMS paper](https://jmlr.org/papers/v25/23-1318.html).

Kelebihan:

- cocok untuk supervised fine-tuning pada data kecil;
- vocabulary/tokenizer dapat dikontrol;
- eksperimen CTC, language model, dan adapter mudah diisolasi.

Kekurangan:

- perlu vocabulary code-switched yang tepat;
- decoding dan normalisasi menjadi sangat penting;
- adapter per bahasa konvensional dapat kesulitan saat bahasa berganti dalam satu utterance.

#### Omnilingual ASR

Omnilingual ASR tersedia dalam keluarga model dari 300M sampai 7B parameter dan dirancang untuk adaptasi low-resource. Sumber: [Omnilingual ASR paper](https://arxiv.org/abs/2511.09690).

Varian 300M layak menjadi baseline pembanding. Varian 7B terlalu mahal sebagai titik awal dan mungkin tidak sesuai dengan runtime kompetisi. Lisensi bobotnya perlu diverifikasi sebelum dipakai.

### Apakah fine-tuning diperlukan?

- **Untuk baseline:** tidak mutlak; zero-shot dapat langsung diukur.
- **Untuk hasil kompetitif:** kemungkinan besar diperlukan.
- **Untuk riset:** sangat relevan, khususnya domain adaptation dan code-switch-aware adaptation.

**Hipotesis.** Fine-tuning hanya pada 10 jam Jember dapat mengurangi domain mismatch tetapi berisiko overfit. Campuran bertahap antara data Indonesian/Javanese monolingual dan Jember in-domain kemungkinan lebih stabil daripada mencampur semuanya dengan bobot sama.

Penelitian pada pasangan bahasa lain menunjukkan bahwa penggabungan atau routing adapter lintas bahasa dapat membantu code-switched ASR, tetapi belum membuktikan efektivitas khusus untuk Jawa–Indonesia. Sumber: [code-switching adapter study](https://arxiv.org/abs/2310.07423).

### Perkiraan compute

> [!warning] Perkiraan, bukan batas resmi
> Angka berikut merupakan estimasi engineering. Batas compute dan runtime resmi belum dipublikasikan.

- Zero-shot evaluation dapat dilakukan pada satu GPU consumer.
- Fine-tuning model sekitar 300M atau Whisper small/medium realistis pada GPU 16–24 GB dengan mixed precision, gradient accumulation, checkpointing, atau parameter-efficient fine-tuning.
- Whisper large atau model 1B+ lebih nyaman pada GPU 40–80 GB; full fine-tuning di luar jangkauan hardware yang tersedia.
- Omnilingual 7B sebaiknya hanya dipertimbangkan jika tersedia GPU besar/rental dan runtime mengizinkan.
- Dataset 10 jam membuat satu training run relatif ringan; biaya utama berasal dari banyak iterasi.

Bottleneck terbesar kemungkinan bukan training mentah, melainkan:

1. validasi segmentasi dan transkripsi;
2. pembuatan dev split tanpa speaker leakage;
3. pemilihan external data tanpa domain/dialect mismatch;
4. normalisasi ortografi;
5. packaging inference setelah runtime specification tersedia.

### Pemilihan accelerator Kaggle

> [!success] Kesimpulan
> **Training feasible, dan compute bukan blocker.** Unit kerja dasarnya tetap **1× GPU 16 GB**, bukan satu GPU besar. Konfigurasi ini cukup untuk full fine-tuning Whisper base/small atau XLS-R sekitar 300M dengan memory-saving settings. Whisper medium realistis melalui LoRA/PEFT **selama dijalankan di T4**. Whisper large-v3 dan model 7B tetap tidak efisien untuk waktu kompetisi ini.
>
> Urutan pilihan: **T4 ×2 sebagai lane utama, P100 sebagai lane kedua, TPU v5e-8 tidak dipakai** dalam siklus empat minggu ini.

Kaggle menyediakan tiga jenis accelerator. Ketiganya tidak setara untuk beban kerja ini:

| | T4 ×2 | P100 | TPU v5e-8 |
|---|---|---|---|
| VRAM | 16 GB × 2 (**tidak** digabung menjadi 32 GB) | 16 GB HBM2 | 16 GB × 8 chip |
| Arsitektur | Turing (sm75) | Pascal (sm60) | TPU |
| Tensor core | Ya | **Tidak** | MXU |
| FP16 matmul | ~65 TFLOPS per GPU | ~19 TFLOPS | sangat tinggi |
| Bandwidth memori | 320 GB/s per GPU | **732 GB/s** | sangat tinggi |
| bf16 | Tidak | Tidak | Ya |
| bitsandbytes int8 / 4-bit | **Ya** | **Tidak** (butuh sm ≥ 7.5) | tidak relevan |
| Jalan langsung di HF Trainer | Ya | Ya | **Tidak** — perlu port ke XLA/JAX |

Tiga hal yang menentukan pilihan:

**1. P100 tidak dapat menjalankan kuantisasi bitsandbytes.** Int8 dan 4-bit memerlukan compute capability minimal 7.5; P100 berada di 6.0. Konsekuensinya, seluruh rencana LoRA terkuantisasi — Whisper medium dan large-v3 pada tabel wall-clock di bawah — bersifat **T4-only**. Ini bukan soal cepat atau lambat, melainkan jalan atau tidak.

**2. P100 tetap berguna untuk beban yang berbeda.** Tanpa tensor core, P100 kalah jauh pada matmul FP16, tetapi bandwidth memorinya 2,3× lipat T4. Untuk full fine-tune yang memory-bound seperti XLS-R 300M CTC, P100 kompetitif. Untuk Whisper seq2seq yang matmul-heavy, T4 unggul jelas. Catatan praktis: di P100 jangan mengandalkan kernel attention hemat-memori, sehingga margin VRAM perlu dilebihkan.

**3. TPU v5e-8 adalah risiko waktu, bukan risiko kapasitas.** Di atas kertas ini yang terkuat, tetapi memerlukan PyTorch/XLA atau JAX. Masalah spesifiknya: loop generation autoregresif Whisper memicu rekompilasi XLA berulang karena shape-nya dinamis. Biaya realistis untuk menstabilkan satu run adalah beberapa hari dari total 28 hari yang tersedia.

**Rekomendasi.** Satu-satunya argumen sah untuk TPU adalah kuotanya berada pada **pool terpisah** dari kuota GPU. Simpan sebagai opsi cadangan minggu ketiga jika jam GPU menipis, dan hanya untuk resep CTC yang shape-nya tetap dan tanpa decode autoregresif — bukan untuk Whisper.

Spesifikasi GPU: [NVIDIA T4 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/tesla-t4/t4-tensor-core-datasheet.pdf).

### Kuota dan batas sesi

Kaggle mendokumentasikan kuota GPU mingguan sekitar **30 jam per akun, kadang lebih tinggi tergantung demand dan resource**. Kuota aktual perlu dilihat di UI masing-masing akun. Data preparation sebaiknya dijalankan tanpa accelerator, dan GPU session dihentikan segera setelah training selesai. Sumber: [Kaggle efficient GPU usage](https://www.kaggle.com/docs/efficient-gpu-usage).

> [!warning] Batas durasi sesi adalah kendala keras
> Satu sesi notebook Kaggle terputus otomatis pada kisaran **12 jam**. Setiap baris pada tabel wall-clock di bawah yang estimasinya melewati angka itu — seluruh kolom Focused mix untuk Whisper small ke atas — **wajib** memiliki checkpoint-resume yang sudah diuji sebelum run panjang dimulai. Ini persyaratan Phase 3, bukan optimasi opsional.

### Alokasi tim dan accelerator

Tim terdiri atas tiga orang dengan total enam akun Kaggle, dua per orang. Pada kuota perencanaan ~30 GPU-hour per akun per minggu, kapasitas agregatnya adalah **sekitar 180 GPU-hour per minggu**, dibandingkan kebutuhan minimum 20–35 jam pada [[#Budget eksperimen yang realistis]].

| Lane | PIC | Akun | Accelerator | Beban kerja |
|---|---|---|---|---|
| **A — Whisper** | Pratama | 1 | T4 ×2 (dua run paralel) | Whisper base zero-shot, lalu Whisper small full fine-tune pada Core |
| **B — CTC** | Fadil | 1 | P100 | XLS-R 300M CTC pada split yang sama |
| **C — Data** | Thoriq | 1 | **tanpa accelerator** | Segmentasi, dev split bebas speaker leakage, replikasi normalizer scoring |
| **Overflow** | Pratama + Fadil | akun ke-2 | T4 ×2 | Focused-mix run panjang dan pengulangan run yang gagal |
| **Overflow** | Thoriq | akun 1 + 2 | T4 ×2 / P100 | Kuota GPU penuh dari kedua akun, karena Lane C tidak memakai accelerator |

Lane C sengaja tidak memakai GPU: data preparation tidak membutuhkan accelerator dan tidak memakan kuota. Lane C juga merupakan jalur kritis, karena Lane A dan B sama-sama menunggu dev split darinya.

> [!warning] Risiko akun sekunder
> ToS Kaggle melarang satu orang memiliki lebih dari satu akun. Karena ketiga anggota masing-masing memakai dua akun, **separuh dari kapasitas 180 GPU-hour/minggu berada pada akun sekunder** dan tidak dapat dijamin. Mitigasi: jangan menempatkan run final yang menentukan pada akun sekunder, dan simpan checkpoint di lokasi yang tidak ikut hilang bersama akunnya. Aturan "satu peserta satu akun" pada [[#Rules & Constraints]] adalah ketentuan platform Mozilla dan terpisah dari hal ini.

### Perencanaan training

#### Skenario volume data

| Skenario | Komposisi | Raw audio | Kegunaan |
|---|---|---:|---|
| **Core** | Jember saja | ±10 jam | Baseline dan eksperimen in-domain pertama |
| **Focused mix** | Jember + subset terkurasi Common Voice Indonesian | ±25–40 jam | **Kandidat utama** untuk model final setelah data selection |
| **Full mix** | Jember + seluruh CV Indonesian tervalidasi | ±44 jam | Berguna untuk studi domain adaptation, tetapi tidak perlu menjadi run pertama |
| **Dialect mix** | Full mix + TTS Central Javanese | ±51 jam | Batas atas yang tersedia setelah penyaringan lisensi. Berisiko negative transfer; bukan prioritas sebelum ada evidence |

Angka raw audio bukan durasi efektif training. Setelah dev split, filtering, dan membuang alignment bermasalah, jumlah training audio akan lebih kecil. Sebaliknya, jumlah epoch membuat model melihat audio yang sama beberapa kali.

#### Estimasi wall-clock pada satu T4

Estimasi berikut adalah **planning range**, bukan benchmark pada dataset ini. Margin error praktisnya dapat mencapai sekitar **2×** tergantung panjang utterance, padding, batch size, evaluasi dengan generation, versi library, dan bottleneck penyimpanan.

Asumsi:

- satu T4 16 GB, FP16;
- audio maksimal sekitar 30 detik per example;
- 3–5 epoch dengan early stopping;
- gradient checkpointing dan gradient accumulation bila diperlukan;
- feature extraction di-cache;
- evaluasi tidak dilakukan terlalu sering;
- waktu preprocessing/download tidak termasuk.

| Model / metode | ±10 jam Core | ±25–40 jam Focused mix | Kelayakan pada 1×T4 |
|---|---:|---:|---|
| Whisper base, full fine-tune | **2–4 jam** | **5–10 jam** | Sangat aman; bagus untuk debugging tetapi ceiling akurasi mungkin lebih rendah |
| Whisper small, full fine-tune | **4–8 jam** | **10–20 jam** | **Pilihan utama**; kemungkinan membutuhkan checkpointing dan batch kecil |
| XLS-R 300M, CTC fine-tune | **3–7 jam** | **8–16 jam** | **Pilihan utama kedua**; vocabulary dan decoding perlu dirancang baik |
| MMS/Omnilingual sekitar 300M, adapter/fine-tune | **4–9 jam** | **10–20 jam** | Feasible, tetapi pipeline lebih eksperimental |
| Whisper medium, LoRA/PEFT | **6–12 jam** | **18–35 jam** | Feasible tetapi borderline untuk iterasi cepat; full fine-tune tidak disarankan |
| Whisper large-v3, int8 + LoRA | **12–24 jam** | **35–70 jam** | Mungkin secara teknis, tetapi berisiko OOM dan boros kuota; bukan strategi utama |
| Model 7B | Tidak direkomendasikan | Tidak direkomendasikan | Tidak cocok untuk satu T4 dan runtime kompetisi yang belum diketahui |

Sebagai kalibrasi, tutorial resmi Hugging Face melatih Whisper small pada sekitar 8 jam data selama 5.000 steps atau sekitar 12 epoch dan melaporkan waktu **5–10 jam tergantung GPU**. Karena rencana di atas memakai 3–5 epoch dan early stopping, rentang untuk Core dibuat lebih pendek tetapi tetap konservatif. Sumber: [Hugging Face Whisper fine-tuning guide](https://huggingface.co/blog/fine-tune-whisper).

PEFT/LoRA mengurangi kebutuhan memori karena base model dibekukan dan optimizer hanya menyimpan state untuk adapter yang kecil. Ini membuat model lebih besar mungkin dimuat pada T4, tetapi tidak menghilangkan biaya forward/backward dan tidak menjamin hasil setara full fine-tuning. Sumber: [Hugging Face PEFT documentation](https://huggingface.co/docs/transformers/en/peft).

#### Budget eksperimen yang realistis

Angka berikut adalah kebutuhan **per lane**, dihitung pada satu GPU:

| Aktivitas | Estimasi GPU time |
|---|---:|
| Sanity check dan overfit subset kecil | 0,5–1 jam |
| Zero-shot baseline dan evaluasi | 0,5–2 jam |
| Whisper small pada Core | 4–8 jam |
| XLS-R 300M pada Core | 3–7 jam |
| Satu ablation/augmentation pada model terbaik | 4–8 jam |
| Final focused-mix run | 8–16 jam |
| **Total minimum yang masuk akal** | **20–35 jam** |

**Interpretasi.** Kebutuhan 20–35 GPU-hour ini berada jauh di bawah kapasitas agregat tim (~180 GPU-hour/minggu), dan bahkan masih di bawah 90 GPU-hour/minggu yang tersedia dari akun primer saja. Satu akun tunggal sudah cukup untuk menyelesaikannya dalam satu minggu. **Compute karena itu bukan faktor pembatas proyek ini** — pengikat sebenarnya adalah kalender empat minggu dan batas durasi sesi 12 jam, bukan jumlah jam yang tersedia. Kelonggaran ini sebaiknya dipakai untuk ablation dan pengulangan run yang gagal, bukan untuk hyperparameter sweep besar yang tidak dipandu error analysis.

#### Menggunakan dua T4: jalankan dua eksperimen, bukan DDP

Sesi T4 ×2 dapat dipakai dengan dua cara. Untuk konfigurasi tim ini, pilihan keduanya lebih baik.

| Pendekatan | Hasil | Kompleksitas |
|---|---|---|
| Distributed data parallel | Satu run **1,6–1,8× lebih cepat** | Tinggi — perlu penyesuaian effective batch size dan learning rate |
| **Dua run independen** (`CUDA_VISIBLE_DEVICES` per proses) | **2× throughput eksperimen** | Rendah — tidak ada kode distributed |

**Rekomendasi.** Yang dibutuhkan tim bukan satu run yang lebih cepat, melainkan lebih banyak run per hari untuk ablation. Jalankan dua eksperimen independen per sesi. DDP baru masuk akal untuk satu final focused-mix run jika jadwal ternyata mepet.

Catatan yang tetap berlaku: VRAM per GPU tetap 16 GB, sehingga model yang tidak muat pada satu T4 tidak menjadi muat hanya karena ada dua. Reliabilitas checkpoint dan restart tetap lebih penting daripada mengejar scaling.

#### Konfigurasi model yang direkomendasikan

1. **Baseline cepat:** Whisper base zero-shot dan fine-tuned.
2. **Baseline utama:** Whisper small full fine-tune pada Jember, 3–5 epoch dengan early stopping.
3. **Pembanding arsitektur:** XLS-R 300M CTC pada split yang sama.
4. **Model final awal:** pemenang antara Whisper small dan XLS-R, dilatih pada focused mix 25–40 jam.
5. **Eksperimen opsional:** Whisper medium LoRA, hanya di T4 dan hanya setelah Whisper small stabil.

> [!danger] Periksa lisensi model sebelum memilih baseline
> **Whisper berlisensi MIT** dan **XLS-R berlisensi Apache-2.0**; keduanya permisif dan kompatibel dengan kewajiban rilis MPL 2.0 bagi pemenang. Sebaliknya, **bobot MMS dirilis di bawah CC-BY-NC-4.0**, yang berpotensi bentrok dengan kewajiban tersebut. Status lisensi Omnilingual ASR perlu diverifikasi terpisah. **Rekomendasi:** batasi baseline utama pada Whisper dan XLS-R; jadikan verifikasi lisensi MMS/Omnilingual sebagai item Phase 1.

> [!warning] Go / No-Go compute
> **GO pada T4:** Whisper base/small full fine-tune, XLS-R 300M CTC, dan Whisper medium dengan LoRA/PEFT.  
> **GO pada P100:** Whisper base/small dan XLS-R 300M — **tanpa** kuantisasi apa pun.  
> **NO sebagai strategi utama:** full fine-tuning Whisper medium/large, Whisper large-v3 LoRA berulang, ensemble besar, model 7B, dan seluruh jalur TPU.

## Biaya Proyek

> [!success] Ringkasan biaya
> **Rencana dasar: Rp 0.** Seluruh komponen berbayar dapat dihindari sepenuhnya. Biaya sesungguhnya dari proyek ini adalah **waktu tim**, bukan uang.

### Klarifikasi: Whisper tidak berbayar

Ada dua hal berbeda yang sering tertukar:

| | Whisper open-weights | OpenAI Audio API |
|---|---|---|
| Bentuk | Bobot model di HuggingFace (`whisper-small`, `large-v3`, dll.) | Endpoint transkripsi berbayar |
| Lisensi | **MIT** | Layanan komersial |
| Biaya | **Rp 0** — unduh dan jalankan sendiri | ~USD 0,006 per menit audio |
| Boleh dipakai di kompetisi ini | **Ya** | **Tidak** |

Yang dipakai proyek ini adalah kolom kiri. OpenAI merilis bobot Whisper di bawah lisensi MIT, sehingga bebas diunduh, di-fine-tune, dan didistribusikan ulang. Yang berbayar adalah API transkripsi OpenAI, dan API tersebut justru **dilarang** oleh aturan kompetisi: data kompetisi tidak boleh dikirim ke hosted model atau inference service pihak ketiga. Jalur berbayar karena itu bukan hanya tidak perlu, melainkan mendiskualifikasi.

### Komponen biaya

| Komponen | Biaya | Catatan |
|---|---:|---|
| Compute training dan evaluasi | **Rp 0** | Kaggle T4/P100/TPU gratis, ~30 GPU-hour per akun per minggu |
| Bobot pretrained (Whisper, XLS-R) | **Rp 0** | MIT dan Apache-2.0 |
| Dataset (Jember, Common Voice, TTS Jawa) | **Rp 0** | Tersedia di MDC |
| Penyimpanan dataset dan checkpoint | **Rp 0** | Kaggle Datasets; audio ±45 jam dalam MP3 masih di bawah batas |
| Tooling eksperimen | **Rp 0** | HuggingFace Hub dan Weights & Biases memadai di free tier |
| Biaya submission | **Rp 0** | Tidak ada entry fee |
| Bandwidth unduhan | dapat diabaikan | Dataset utama 271,65 MB; mix terluas beberapa GB |
| **Total rencana dasar** | **Rp 0** | |

### Dana cadangan (opsional)

Hanya relevan jika kuota Kaggle habis atau akun bermasalah menjelang deadline. Kurs asumsi Rp 16.500/USD — sesuaikan saat rapat.

| Skenario | Isi | Perkiraan |
|---|---|---:|
| **Tidak ada cadangan** | Sepenuhnya bergantung pada Kaggle | **Rp 0** |
| **Asuransi ringan** | Colab Pro 1 bulan untuk 1–2 orang | USD 10–20 (±Rp 165–330 rb) |
| **Akselerasi akhir** | Sewa GPU spot 30–50 jam untuk final run (RTX 4090 ±USD 0,4–0,7/jam; A100 40 GB ±USD 1,0–1,6/jam) | USD 20–80 (±Rp 330 rb–1,3 jt) |
| **Batas atas wajar** | Kedua hal di atas untuk seluruh tim | **< USD 150 (±Rp 2,5 jt)** |

**Rekomendasi.** Jangan alokasikan dana di muka. Mulai dengan Rp 0, dan tinjau ulang di akhir minggu kedua ketika konsumsi kuota yang sebenarnya sudah terukur. Sewa GPU baru dipertimbangkan jika ada bukti bahwa kuota Kaggle benar-benar menjadi pengikat — sejauh analisis ini, tidak.

### Biaya yang sebenarnya: waktu

| Sumber daya | Estimasi |
|---|---:|
| Durasi proyek | 4 minggu |
| Anggota tim | 3 orang |
| Beban wajar per orang | 15–20 jam/minggu |
| **Total person-hours** | **±180–240 jam** |

**Interpretasi.** Dibandingkan hadiah USD 4.000 untuk peringkat pertama, biaya uang proyek ini praktis nol dan biaya waktunya signifikan. Keputusan commit karena itu adalah keputusan alokasi waktu tim, bukan keputusan anggaran. Perlu dicatat bahwa peluang menang belum dapat diperkirakan karena baseline dan leaderboard belum tersedia, sehingga proyek ini sebaiknya dinilai dari nilai risetnya lebih dahulu dan hadiahnya sebagai bonus.

## Competitive Feasibility

**Interpretasi.** Tingkat kesulitan kemungkinan menengah–tinggi. Dataset kecil membuat entry barrier rendah, tetapi juga memungkinkan banyak peserta menggunakan pretrained model kuat dengan cepat.

Fine-tuning standar kemungkinan menghasilkan submission yang valid dan cukup baik, tetapi belum tentu memenangkan track. Sumber keunggulan yang paling mungkin:

- pengetahuan linguistik Jawa–Indonesia;
- dev split yang representatif;
- error analysis per speaker, bahasa, dan dialek;
- pemilihan rasio data Jember dan external data;
- VAD serta segmentasi;
- augmentation yang menyerupai voice notes;
- vocabulary dan normalisasi diakritik;
- local language-model rescoring;
- checkpoint averaging atau ensemble jika runtime memungkinkan;
- penanganan disfluency dan hallucination.

**Hipotesis.** Improvement terbesar kemungkinan datang dari data curation, decoding, dan normalisasi, bukan sekadar memperbesar model.

Kompetisi ini bersifat hybrid research dan engineering. Dengan waktu sekitar empat minggu, engineering serta reproducibility perlu diprioritaskan sebelum eksperimen riset tambahan.

Baseline score, leaderboard, dan jumlah peserta aktif belum tersedia secara publik. Karena itu, competitive potential belum dapat dinilai HIGH dengan keyakinan.

## Research Opportunities

Peluang riset yang paling kuat:

1. **Low-resource code-switched ASR** — data utama hanya sekitar 10 jam dengan lebih dari dua bahasa aktual.
2. **Domain adaptation** — transfer dari read speech ke spontaneous voice notes.
3. **Dialect-aware transfer** — membandingkan Jember/Pandhalungan dengan Central Javanese. Cakupannya menyempit karena Ngapak, Banyumasan, dan Bojonegoro gugur pada penyaringan lisensi.
4. **Code-switch-aware fine-tuning/adapters** — mengatasi keterbatasan adapter monolingual pada pergantian bahasa intrakalimat.
5. **Data selection dan curriculum learning** — monolingual lalu code-mixed lalu Jember in-domain.
6. **Orthography-aware decoding** — normalisasi diakritik dan bentuk kata sesuai reference.
7. **Acoustic augmentation untuk voice notes** — codec compression, noise, gain, reverberation, dan speed perturbation.
8. **Language modeling dan post-processing lokal** — menggunakan corpus terbuka yang memenuhi aturan external data.

Arah yang belum cukup didukung evidence:

- membangun arsitektur ASR baru;
- diarization kompleks;
- word-level language identification sebagai objective utama;
- synthetic speech berskala besar sebelum mengetahui jarak domain dan runtime.

## Rules & Constraints

Fakta dari [competition home](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/1/) dan [official rules](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/rules/):

- Open-weight pretrained model diperbolehkan jika tersedia publik, lisensinya sesuai, dan dapat dijalankan secara lokal.
- Data kompetisi tidak boleh dikirim ke hosted model, proprietary model API, atau inference service pihak ketiga.
- External data diperbolehkan jika peserta memiliki seluruh hak dan izin yang diperlukan.
- External training data yang belum berada di MDC harus dipublikasikan ke MDC setelah kompetisi.
- Semua external dependency harus diberikan kepada penyelenggara untuk verifikasi.
- Setiap test sample harus diproses secara independen.
- Pseudo-labeling atau unsupervised learning pada kumpulan test dilarang secara default.
- Sistem harus dapat melakukan inference otomatis pada data baru tanpa retraining.
- Satu peserta hanya boleh memakai satu akun dan tidak boleh berada di lebih dari satu tim.
- Private sharing data atau kode di luar tim dilarang.
- Jumlah submission dibatasi, tetapi angka spesifik belum dipublikasikan.
- Solusi pemenang harus didokumentasikan dan dilisensikan di bawah MPL 2.0.
- Pemenang harus menyediakan model, weights, kode, konfigurasi, dan dependency yang diperlukan untuk reproduksi.
- Tidak ada batas maksimum anggota tim yang terlihat pada aturan publik.
- Tidak ada batas GPU/training compute yang dipublikasikan.
- Peserta harus berupa individu dewasa yang memenuhi persyaratan wilayah dan sanksi; legal entities tidak dapat menjadi peserta.

### Informasi yang masih belum diketahui

Seluruh item di bawah adalah agenda Phase 1. Kolom PIC diisi pada rapat 18 Agustus; tenggat seluruhnya **24 Agustus 2026**.

| # | Pertanyaan | PIC | Sumber |
|---|---|---|---|
| 1 | Kapan submission dibuka | | Halaman kompetisi / forum |
| 2 | Ukuran dan komposisi test set | | Problem description / forum |
| 3 | Image dan container specification | | Runtime repository |
| 4 | Batas ukuran model | | Runtime repository |
| 5 | RAM, CPU, GPU, storage, dan waktu maksimal inference | | Runtime repository |
| 6 | Jumlah submission per hari | | Official rules / forum |
| 7 | **Maksimum ukuran tim** — menentukan apakah formasi tiga orang sah | | Official rules / forum |
| 8 | Baseline WER dan status leaderboard | | Halaman kompetisi |
| 9 | **Kompatibilitas CC-BY-NC-SA-4.0 (Jember) dan CC-BY-SA dengan kewajiban rilis MPL 2.0** — syarat S4 | | Forum penyelenggara |
| 10 | Lisensi bobot MMS dan Omnilingual ASR | | Model card |
| 11 | Apakah keputusan eliminasi pada [[#Dataset yang dieliminasi]] perlu ditinjau — khususnya lisensi TTS Javanese Ngapak dan keberadaan dataset Bojonegoro | | Halaman dataset / forum |

Item 7 dan 9 adalah yang paling menentukan: item 7 menyangkut keabsahan formasi tim, dan item 9 menyangkut apakah solusi pemenang dapat dirilis sesuai aturan. Keduanya perlu ditanyakan pada hari pertama.

## Feasibility Assessment

| Dimension | Rating | Reason |
|---|---|---|
| Technical | **HIGH** | Task ASR standar dan tersedia beberapa foundation model terbuka; tantangan utama adalah adaptation, bukan pembangunan model dari nol. |
| Data | **MEDIUM** | Data utama in-domain hanya sekitar 10 jam, tetapi ada data tambahan Indonesian/Javanese dengan kualitas, dialek, dan lisensi yang tidak seragam. |
| Compute | **HIGH** | Kapasitas agregat tim ±180 GPU-hour/minggu — ±90 jam dari akun primer saja — melawan kebutuhan 20–35 jam. Whisper small dan XLS-R 300M nyaman di T4/P100; Whisper medium LoRA realistis di T4. Full fine-tune model besar dan ensemble tetap di luar jangkauan, tetapi bukan jalur yang direncanakan. |
| Biaya | **HIGH** | Rencana dasar Rp 0. Seluruh compute, bobot model, dan dataset gratis; tidak ada entry fee. |
| Research Potential | **HIGH** | Low-resource, spontaneous speech, code-switching, dialek, dan domain shift menyediakan pertanyaan riset nyata. |
| Competitive Potential | **MEDIUM** | Hadiah dan entry barrier menarik, tetapi baseline/leaderboard belum tersedia dan waktunya pendek. |
| Time/Effort | **MEDIUM–HIGH** | Sekitar empat minggu tersisa dan ini kendala yang mengikat. Tiga orang bekerja paralel meringankan beban dibandingkan pengerjaan solo, tetapi data engineering, evaluasi, dan containerization tetap harus selesai sebelum deadline. |

### Kesimpulan

- **Apakah layak dikerjakan?** Ya.
- **Layak sebagai research project?** Sangat layak.
- **Layak sebagai competition project?** Ya, dengan syarat runtime specification segera terkonfirmasi.
- **Berapa biayanya?** Rp 0 pada rencana dasar; yang dipertaruhkan adalah ±180–240 person-hours.
- **Apakah compute cukup?** Ya, dengan margin besar. Bukan faktor pembatas.
- **Alasan terkuat:** problem bermakna dan belum jenuh; cukup kecil untuk individu tetapi cukup kompleks untuk menghasilkan kontribusi ilmiah.
- **Risiko terbesar:** waktu pendek dan detail submission/runtime yang belum lengkap.
- **Risiko teknis terbesar:** overfitting serta domain/dialect mismatch, bukan sekadar kekurangan compute.

## Key Risks

1. Deadline sekitar empat minggu lagi.
2. Model besar atau ensemble mungkin tidak sesuai runtime yang belum diumumkan.
3. Data utama kecil dan dialek-spesifik.
4. Kemungkinan train–test domain shift.
5. Orthographic mismatch dapat meningkatkan WER walaupun prediksi fonetis benar.
6. Beberapa external dataset memiliki ketentuan tambahan di luar label lisensi singkat.
7. Belum ada baseline score atau leaderboard publik.
8. Hosted model/API dilarang dan solusi pemenang harus dapat direproduksi serta dibuka di bawah MPL.
9. Batas sesi Kaggle ~12 jam memutus run panjang; tanpa checkpoint-resume yang teruji, focused-mix run akan gagal berulang.
10. Separuh dari kapasitas 180 GPU-hour/minggu berasal dari tiga akun sekunder yang melanggar ToS Kaggle dan dapat hilang sewaktu-waktu. Kapasitas yang benar-benar aman adalah ±90 GPU-hour/minggu.
11. Lisensi bobot MMS (CC-BY-NC-4.0) berpotensi bentrok dengan kewajiban rilis MPL 2.0 bagi pemenang.
12. Formasi tiga orang belum tentu sah karena batas maksimum ukuran tim belum dipublikasikan.

## Recommended Next Steps

Deadline efektif adalah **Rabu 16 September 2026**, karena batas resmi jatuh pada Kamis 17 September pukul 06.59 WIB.

| Minggu | Tanggal | Phase | PIC | Deliverable |
|---|---|---|---|---|
| **1** | 18–24 Agu | Phase 1 — Competition & literature research | semua | Jawaban atas [[#Informasi yang masih belum diketahui]]; verifikasi lisensi MMS/Omnilingual |
| **1** | 18–24 Agu | Phase 2 — Dataset exploration | Thoriq (Lane C) | Audio tersegmentasi, dev split bebas speaker leakage, normalizer scoring direplikasi |
| **2** | 25–31 Agu | Phase 3 — Baseline reproduction | Pratama (A), Fadil (B) | WER zero-shot dan fine-tuned dari Whisper small dan XLS-R 300M pada split yang sama |
| **3** | 1–7 Sep | Phase 4 — Experiment design | semua | Satu atau dua hipotesis terpilih dari error analysis |
| **3** | 1–7 Sep | Phase 5 — Model improvement | Pratama, Fadil | Final focused-mix run pada model terbaik |
| **4** | 8–14 Sep | Phase 6 — Evaluation | semua | Ablation, robustness check, dan reproducibility check |
| **4** | 8–14 Sep | Phase 7 — Competition submission | Pratama | Container inference terkemas dan tervalidasi |
| **Buffer** | 15–16 Sep | Cadangan | — | Submit paling lambat 15 September; 16 September hanya untuk perbaikan |

Phase 1 dan 2 berjalan paralel. Phase 2 adalah jalur kritis: Phase 3 tidak dapat dimulai sebelum dev split selesai.

### Decision gates

Verdict GO ini bukan komitmen tanpa syarat. Tinjau ulang pada tiga titik berikut:

| Titik | Kriteria | Jika tidak terpenuhi |
|---|---|---|
| **24 Agu** (akhir Phase 1–2) | Runtime dan jadwal submission terkonfirmasi, dan dev split siap | Turunkan target ke research-only; hentikan pekerjaan containerization |
| **31 Agu** (akhir Phase 3) | Fine-tuned WER lebih baik daripada zero-shot pada dev split | Hentikan focused-mix run; kembali ke audit data dan normalisasi |
| **7 Sep** (akhir Phase 5) | Ada satu model yang siap dikemas | Bekukan model terbaik apa adanya; alihkan seluruh sisa waktu ke Phase 7 |

Jika submission belum juga dibuka pada **1 September**, perlakukan proyek ini sebagai riset dan lepaskan target kompetisi.

> [!success] Go / No-Go
> **GO**, dengan fokus tunggal pada track Indonesian–Javanese dan scope riset yang sempit. Biaya uangnya nol, sehingga risiko finansial dari keputusan ini juga nol — yang dipertaruhkan hanya waktu tim. Lakukan pemeriksaan ulang pada tiga decision gate di atas. Jika runtime terlalu ketat atau submission terlambat dibuka, proyek tetap layak dilanjutkan sebagai riset meskipun target kompetisinya diturunkan.
>
> **Tidak dikejar:** bonus USD 2.000 untuk rata-rata WER terbaik lintas tiga track. Menuntut anggota yang sama di ketiga track sekaligus, dan tidak realistis untuk tim tiga orang dalam empat minggu. Dinyatakan gugur agar tidak menjadi distraksi.

## Primary Sources

- [Competition home](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/1/)
- [Problem description](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/2/)
- [Competition about and references](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/3/)
- [Official rules](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/rules/)
- [Mozilla Data Collective announcement](https://community.mozilladatacollective.com/no/)
- [Jember Javanese Spontaneous Speech Corpus](https://mozilladatacollective.com/datasets/cmlgm5a94008kny07nz2intus)
- [Common Voice Indonesian 26.0](https://mozilladatacollective.com/datasets/cmqinqwef00xonr07z4vbfovw)
- [Common Voice Spontaneous Javanese 4.0](https://mozilladatacollective.com/datasets/cmqi294n3004mmf07wvybp3fn)
- [Whisper paper](https://arxiv.org/abs/2212.04356)
- [MMS paper](https://jmlr.org/papers/v25/23-1318.html)
- [Omnilingual ASR paper](https://arxiv.org/abs/2511.09690)
- [Code-switching adapter study](https://arxiv.org/abs/2310.07423)
