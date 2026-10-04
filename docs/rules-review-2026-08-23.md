---
title: "Kaji Ulang Peraturan — Lost in Transcription (23 Agustus 2026)"
aliases:
  - Kaji Ulang Peraturan - 23 Agustus 2026
  - Kaji Ulang Peraturan Kompetisi
  - Rules Re-review 2026-08-23
tags:
  - research
  - competition
  - rules
  - compliance
status: final
created: 2026-08-23
updated: 2026-09-22
source_type: official-primary
---

# Kaji Ulang Peraturan — 23 Agustus 2026

> [!summary] Ringkasan
> Halaman resmi dibaca ulang hari ini. **Tidak ada aturan yang berubah** dibanding yang sudah kita tulis di [[feasibility-study|Feasibility Study - Mozilla Lost in Transcription]], tetapi ada **lima hal yang salah atau kurang** di catatan kita, dan **satu status yang genting**: sampai hari ini **submission masih belum dibuka**, sementara sisa waktu tinggal sekitar 3,5 minggu.
>
> Tiga temuan baru berdampak langsung ke pipeline teks: normalizer penyelenggara **tidak menyebut lowercasing**, **tidak menghapus titik**, dan **mempertahankan elipsis yang menempel di kata**. Ketiganya nilai gratis yang bisa hilang kalau kita melatih model pada teks yang bentuknya berbeda dari referensi.
>
> **Ibaratnya:** ini seperti baca ulang kunci jawaban ujian malam sebelum tes, dan sadar cara penilaiannya sedikit beda dari yang dikira. Kalau AI-nya dilatih menulis jawaban dengan format yang beda dari yang dipakai penilai, dia bakal dianggap salah terus meski isinya sudah benar — padahal itu bisa dihindari cuma dengan menulis dalam format yang sama persis.

> [!important] Update terbaru — 22 September 2026
> Deadline sekarang **2 Oktober 2026, 00:00 UTC**, dan limit submission sudah jelas: 3 per 7 hari per anggota tim. Lihat [[#Update 22 September 2026 — situs, forum, dan runtime repo dicek ulang]].

> [!info] Sumber dan waktu akses
> Seluruh isi catatan ini dibaca pada **23 Agustus 2026** dari halaman publik berikut:
> - [Competition home](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/1/)
> - [Problem description](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/2/)
> - [About & references](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/3/)
> - [Official rules](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/rules/)
> - [Pengumuman MDC](https://community.mozilladatacollective.com/no/)
>
> Referensi tidak resmi tapi sangat berguna: [childrens-speech-recognition-runtime](https://github.com/drivendataorg/childrens-speech-recognition-runtime) — runtime repo DrivenData untuk kompetisi ASR sejenis. Bukan runtime kompetisi kita, tapi konvensinya hampir pasti sama.

## Status kompetisi hari ini

| Hal | Status 23 Agustus 2026 |
|---|---|
| Peserta terdaftar | **256 joined** |
| Submission | **Belum dibuka.** Halaman masih berbunyi *"Submissions in this competition will open at a later date."* |
| Leaderboard | Belum ada |
| Batas submission per hari | Belum ditampilkan; aturan menyatakan angkanya muncul di website saat submission aktif |
| Runtime repository | Belum dipublikasikan |
| Spesifikasi test set | Belum dipublikasikan |
| Countdown di halaman | **"4 weeks left"** |

> [!danger] Countdown-nya tidak konsisten — periksa ini hari ini juga
> Studi kelayakan (17 Agustus) mencatat deadline **16 September 2026, 23:59 UTC**. Kalau benar, hari ini sisanya 24 hari, sekitar 3,4 minggu. Tetapi halaman **masih menampilkan "4 weeks left"**, angka yang sama seperti seminggu lalu.
>
> Dua kemungkinan: countdown-nya dibulatkan atau di-cache, atau **deadline-nya digeser**. Selisihnya bisa empat hari kerja. **Buka halaman kompetisi dalam keadaan login dan salin tanggal persisnya.** Ini item P0 di [[execution-plan|Rencana Eksekusi - Lost in Transcription]].

## Aturan yang dikonfirmasi ulang

Semuanya sudah benar di catatan kita. Ditulis ulang di sini supaya ada satu tempat rujukan.

| # | Aturan | Sumber |
|---|---|---|
| R1 | Metrik tunggal **WER** = (S + D + I) / N. Partial word match tetap dihitung salah. | Problem description |
| R2 | **Code execution challenge.** Model dan kode inference dikirim sebagai ZIP, dijalankan di container penyelenggara. | Problem description |
| R3 | Output **CSV** dengan kolom `audio_filename` dan `transcript`, satu baris per klip. | Problem description |
| R4 | Input test berupa **klip `.mp3`** — sudah terpotong, bukan rekaman utuh. | Problem description |
| R5 | External data boleh, **asal punya seluruh hak dan izin**, dan **harus dipublikasikan ke MDC setelah kompetisi selesai**. | Official rules |
| R6 | Pretrained model boleh, asal **bobotnya publik dan gratis untuk semua peserta**, lisensinya mengizinkan, dan **jalan tanpa hosted API**. | Official rules |
| R7 | **Dilarang mengirim data kompetisi ke model atau API pihak ketiga.** | Official rules |
| R8 | Setiap sampel test **diproses independen**; dilarang memakai informasi dari sampel test lain. | Official rules |
| R9 | Dilarang **anotasi manual test set** dan **pseudo-labeling di atas test set**. | Official rules |
| R10 | Sistem harus bisa inference otomatis pada data baru **tanpa retraining**. | Official rules |
| R11 | **Satu orang satu akun.** Multi-akun dianggap cheating dan berujung diskualifikasi. Satu orang hanya boleh berada di satu tim. | Official rules |
| R12 | **Private code sharing di luar tim dilarang.** Sharing publik boleh, dan otomatis berlisensi MPL. | Official rules |
| R13 | Solusi pemenang **wajib dirilis di bawah MPL 2.0**, lengkap dengan weights, config, dan dependency. | Official rules |
| R14 | Seluruh supporting software harus berlisensi open-source yang **mengizinkan penggunaan komersial bebas**. | Official rules |
| R15 | Peserta harus **individu, usia minimal 18 tahun**, legal resident di Territory, bukan subjek sanksi dagang AS. **Legal entity tidak boleh mendaftar.** | Official rules |
| R16 | Bonus USD 2.000 hanya untuk tim dengan **anggota identik di ketiga track**. | Competition home |

## Yang salah atau kurang di catatan kita

### K1 — Normalizer tidak menyebut lowercasing, jadi WER-nya kemungkinan case-sensitive

Daftar normalisasi pra-scoring yang dipublikasikan hanya berisi empat hal:

1. hapus tag metalinguistik dalam kurung siku, misalnya `[laugh]`;
2. hapus penanda tidak terdengar `(???)` dan `[???]`;
3. hapus elipsis berdiri sendiri, yaitu yang berspasi di kedua sisi;
4. hapus punctuation `,?¿¡!";:`.

**Case folding tidak ada di daftar itu.** Kalau memang tidak dilakukan, `Aku` dan `aku` adalah dua kata berbeda, dan setiap huruf kapital awal kalimat yang meleset menjadi satu substitution.

Konsekuensi praktis: **jangan lowercase teks latihan.** Latih model pada teks hasil normalizer resmi apa adanya, termasuk kapitalisasinya.

### K2 — Titik tidak dihapus

Daftar punctuation yang dihapus adalah `,?¿¡!";:` — **tanpa titik dan tanpa tanda hubung**. Artinya:

- `omah.` tetap `omah.` dan model harus mengeluarkan titiknya juga;
- `arèk-arèk` tetap satu token bertanda hubung, jadi reduplikasi harus ditulis persis.

Ini konsisten dengan aturan elipsis: kalau semua titik dihapus, aturan "elipsis yang menempel dipertahankan" tidak akan ada gunanya.

### K3 — Elipsis yang menempel di kata justru harus diproduksi model

Aturannya spesifik: elipsis **berdiri sendiri** dihapus, elipsis **yang menempel ke kata** dipertahankan sebagai penanda disfluency. Di Jember ada **718 segmen** mengandung elipsis — lihat [[nb01-dataset-analysis|Analisa Dataset - Notebook 01]] temuan J5.

Kalau kita membuang elipsis dari teks latihan, model tidak akan pernah mengeluarkannya, dan setiap `mba...` di referensi menjadi substitution. **Pertahankan.**

> [!check] Prinsip yang lahir dari K1 sampai K3
> **Latih model pada keluaran normalizer resmi, bukan pada teks yang menurut kita bersih.** Distribusi output model harus sama persis dengan distribusi yang dinilai. Ini menjadi keputusan mengikat untuk [[nb02-brief-data-build-eval-harness|Brief Notebook 02 - Data Build dan Eval Harness]].

### K4 — Ada syarat kelayakan peserta yang belum pernah kita periksa

R15 belum pernah masuk daftar risiko. Tiga hal yang harus dipastikan sebelum menghabiskan 200 person-hour:

1. **Territory** — apakah Indonesia termasuk wilayah yang boleh menerima hadiah? Aturan menyebut "legal residents within the Territory" tanpa mendefinisikannya di ringkasan halaman. Akan aneh kalau track Indonesian–Javanese menutup peserta Indonesia, tetapi ini harus dibaca hitam di atas putih, bukan diasumsikan.
2. **Usia minimal 18 tahun** untuk ketiga anggota.
3. **Legal entity dilarang** — pendaftaran harus atas nama pribadi, bukan nama lab, kampus, atau perusahaan.

### K5 — Batas ukuran tim: tidak ada batas atas di aturan publik

Item 7 pada daftar "Informasi yang masih belum diketahui" praktis **tertutup**. Aturan hanya menyebut bahwa beberapa individu boleh berkolaborasi, masing-masing dengan akun terpisah, dan satu orang hanya boleh berada di satu tim. Tidak ada angka maksimum. **Formasi tiga orang sah.** Tetap layak dikonfirmasi di forum, tetapi statusnya turun dari blocker menjadi formalitas.

## Yang bisa disimpulkan tentang runtime, walau spesifikasinya belum keluar

Runtime repo kompetisi ini belum ada. Tetapi DrivenData memakai pola yang sama di semua kompetisi code-execution mereka, dan yang paling dekat adalah [childrens-speech-recognition-runtime](https://github.com/drivendataorg/childrens-speech-recognition-runtime) — sama-sama ASR, sama-sama DrivenData.

| Aspek | Pola DrivenData | Artinya untuk kita |
|---|---|---|
| Isi ZIP | **`main.py` wajib ada di root ZIP**, tidak boleh bersarang di folder | Rancang `submission_src/` datar sejak awal |
| Eksekusi | `entrypoint.sh` meng-unzip submission lalu memanggil `main.py` | Tidak ada argumen CLI yang bisa diandalkan; baca path dari konvensi |
| Path di container | `/code_execution/data/` untuk data test, `/code_execution/src/` untuk isi submission | Jangan hardcode path lain |
| **Internet** | **Diblokir total saat run resmi** | **Bobot model wajib ikut di dalam ZIP.** Tidak ada `from_pretrained` yang mengunduh |
| Dependency | Sudah terpasang di image; menambah paket berarti **PR ke `runtime/pyproject.toml`** lalu menunggu image di-rebuild | **Ini punya lead time berhari-hari.** Kunci stack ke paket paling standar |
| Output | Ditulis ke folder `submission/` | Kompetisi kita memakai CSV per R3, bukan JSONL |

> [!danger] Lead-time dependency adalah risiko tersembunyi
> Kalau resep terbaik kita ternyata butuh paket yang tidak ada di image — `pyctcdecode`, `kenlm`, `peft`, `bitsandbytes`, atau `torchaudio` versi tertentu — kita **tidak bisa memasangnya sendiri saat run**. Harus lewat PR ke runtime repo dan menunggu.
>
> Mitigasi: rancang jalur utama supaya **hanya butuh `torch` dan `transformers`**, dan perlakukan apa pun di luar itu sebagai jalur cadangan yang diputuskan pada hari runtime repo terbit.

## Status daftar "Informasi yang masih belum diketahui"

Merujuk tabel di [[feasibility-study|Feasibility Study - Mozilla Lost in Transcription]].

| # | Pertanyaan | Status 23 Agustus |
|---|---|---|
| 1 | Kapan submission dibuka | **MASIH TERBUKA.** Halaman tetap "at a later date". Ini pemicu decision gate 1 September |
| 2 | Ukuran dan komposisi test set | **MASIH TERBUKA.** Yang pasti hanya bentuknya: klip `.mp3` |
| 3 | Image dan container specification | **MASIH TERBUKA.** Proksi terbaik: runtime repo sejenis di atas |
| 4 | Batas ukuran model | **MASIH TERBUKA.** Rencanakan ladder model, jangan bertaruh pada satu ukuran |
| 5 | RAM, CPU, GPU, storage, waktu inference | **MASIH TERBUKA** |
| 6 | Jumlah submission per hari | **MASIH TERBUKA** |
| 7 | Maksimum ukuran tim | **TERTUTUP.** Tidak ada batas atas; formasi 3 orang sah — lihat K5 |
| 8 | Baseline WER dan leaderboard | **TERTUTUP sementara.** Tidak ada baseline, tidak ada leaderboard. Kita tidak punya pembanding eksternal sampai submission dibuka |
| 9 | CC-BY-NC-SA dan CC-BY-SA versus kewajiban MPL 2.0 | **TURUN PRIORITAS.** R13 dan R14 berbicara tentang *solusi* dan *software*, bukan lisensi data; lisensi data diatur klausa external-data-with-rights (R5). Jember adalah dataset yang penyelenggara sendiri sorot untuk training. Tetap ditanyakan, tetapi bukan blocker |
| 10 | Lisensi bobot MMS dan Omnilingual | **MMS TERTUTUP — gugur.** CC-BY-NC-4.0 tidak lolos R14 "free commercial use". Omnilingual masih perlu dicek kalau mau dipakai |
| 11 | Peninjauan dataset yang dieliminasi | **BIARKAN TERTUTUP.** Tidak ada waktu, dan temuan X1 di [[nb01-dataset-analysis\|Analisa Dataset - Notebook 01]] menunjukkan TTS Central Javanese sudah cukup |

**Item baru** yang masuk ke daftar:

| # | Pertanyaan | Kenapa |
|---|---|---|
| 12 | **Apakah Indonesia termasuk "Territory" yang boleh menerima hadiah?** | **TERTUTUP 25 Agustus — YA.** Lihat catatan di bawah |
| 13 | **Apakah deadline masih 16 September 2026, 23:59 UTC?** | Countdown "4 weeks left" tidak cocok dengan tanggal itu |
| 14 | **Apakah scoring case-sensitive?** | K1. Bisa bernilai beberapa poin WER |
| 15 | **Apakah titik di akhir kata dipertahankan saat scoring?** | K2 |

## Update 25 Agustus 2026 — halaman Rules & Terms dibaca ulang

Teks lengkap halaman *Rules and Terms of Data Use* (generik/legal, bukan problem description) dibaca ulang. Tidak ada perubahan pada R1–R16; satu pertanyaan lama tertutup, satu referensi baru ditemukan.

- **Item #12 tertutup — Indonesia termasuk Territory.** Definisi resmi: *"Territory" means any country... where the laws of the United States or local law do not prohibit participating or receiving a prize... and excludes any area designated by [OFAC]... Individual participants or team members located in the Russian Federation are not eligible to win a prize.* Ini bukan daftar putih negara — cakupannya luas, hanya mengecualikan wilayah bersanksi OFAC dan Rusia. Indonesia lolos keduanya. K4 poin 1 selesai.
- **Template dokumentasi pemenang, link eksplisit:** [Winning Model Documentation Template](https://github.com/drivendataorg/prize-winner-template/blob/main/example_documentation_guide.pdf). Relevan untuk Gate 3 kalau lolos ke tahap submission.
- Item #1, #13, #14, #15 (kapan submission dibuka, deadline pasti, case-sensitivity, titik di akhir kalimat) **masih terbuka** — halaman ini generik/legal, tidak membahas normalizer atau tanggal spesifik.

## Update 25 Agustus 2026 (lanjutan) — situs kompetisi dibaca penuh, bukan diproksi

Sesi sebelumnya membaca halaman generik *Rules and Terms*. Hari ini seluruh navigasi situs kompetisi dibaca: Home, Problem description, Code submission format, About. Ini menutup hampir semua item **"MASIH TERBUKA"** di tabel di atas.

### Status kompetisi berubah total

- **Submission SUDAH DIBUKA.** 270 peserta terdaftar (227 solo + 33 tim) per hari ini. Item #1 tertutup.
- **Deadline resmi: 25 September 2026, tengah malam UTC.** Ini BUKAN 16 September seperti diasumsikan di [[feasibility-study|Feasibility Study - Mozilla Lost in Transcription]] dan [[execution-plan|Rencana Eksekusi - Lost in Transcription]] — kedua dokumen itu perlu dibaca sebagai snapshot lama untuk urusan tanggal. Item #13 tertutup, jawabannya beda dari dugaan.
- **Hadiah track ini: $4.000 (1st) + $2.000 (2nd) = $6.000.** Ada bonus prize lintas-track untuk tim yang submit ke ketiga track dengan anggota identik.
- Item #2 (ukuran/komposisi test set) **tertutup sebagian**: klip `.mp3`, 48kHz mono, durasi 2–40 detik, sudah tersegmentasi per-utterance.

### Dev set resmi — bukan proxy dari Jember

Problem description sekarang mempublikasikan dev set asli: **372 klip (~2,5 jam)**, dari dua percakapan di antara empat speaker yang **tidak muncul di test set**, tapi berasal dari sumber data yang sama dengan test (dialog voice-note dyadic code-switched — beda dari rekaman sesi Jember). Format:

```
indonesian_dev/
├── clips/*.mp3
└── metadata.tsv   # audio_filename, speaker, transcript, language (javind/jav/ind), convo_id
```

**Ini mengubah posisi dev split NB 02.** Split yang diukir dari Jember adalah proxy in-domain, sementara dev set ini berasal dari distribusi test yang sebenarnya. Perlu diunduh dari data download page (perlu login/join) dan dijadikan lapisan validasi utama, bukan cuma tambahan — lihat rencana terpisah untuk pemakaiannya.

### Text preprocessing — koreksi, bukan cuma pelengkap K1–K3

Problem description sekarang memuat daftar normalizer LENGKAP, beda dari yang dibaca 23 Agustus:

1. Hapus tag metalinguistik `[laugh]`.
2. Hapus penanda unintelligible `(???)` / `[???]`.
3. **Lowercase huruf awal transkrip, dan huruf pertama setelah `. ! ? —`** (kecuali diikuti huruf kapital lagi → dianggap akronim, dibiarkan). Casing di luar itu dibandingkan apa adanya.
4. Hapus punctuation `,?¿¡!";:` (sama seperti sebelumnya).
5. **Hapus titik**, kecuali elipsis yang menempel di akhir kata (disfluency marker) — elipsis berdiri sendiri tetap dihapus seperti sebelumnya.
6. Collapse spasi berulang.

**K1 dan K2 di atas SALAH** — bukan cuma "belum dikonfirmasi", tapi terbukti keliru: scoring TIDAK sepenuhnya case-insensitive-agnostic (ada lowercasing parsial di awal kalimat) dan titik TIDAK dipertahankan. K3 (elipsis menempel dipertahankan) tetap benar. Diakritik masih tidak disebut sama sekali — pertanyaan P0 soal itu tetap terbuka.

> [!danger] scorer.py punya bug nyata, sudah diperbaiki hari ini — dan dampaknya lebih besar dari dugaan awal
> `findings/02-data-build/scorer.py` dan `SCORER_SRC` di `notebooks/02-data-build.ipynb` secara eksplisit mengasumsikan "tidak lowercase, tidak strip titik" (lihat header komentarnya sebelum perbaikan). Ini sudah dipatch dan lolos 28/28 self-test. **Karena normalizer diterapkan ke referensi maupun hipotesis sebelum dibandingkan, ini melonggarkan beban ortografi model, bukan memperberat.**
>
> **Koreksi atas catatan sebelumnya:** ini bukan cuma soal `scorer.py`. `manifest.csv` membangun kolom `text_official` langsung lewat `S["text_official"] = S["text_raw"].map(official_normalize)` — jadi **isi `manifest.csv` sendiri berubah** (titik hilang, huruf awal kalimat jadi lowercase), begitu juga `text_folded` (turunan darinya), `n_words`, `n_chars`, dan angka-angka di `text_audit.json`. Audio (208 FLAC) tidak tersentuh sama sekali — normalisasi teks tidak mengubah byte audio.
>
> **Yang perlu dijalankan ulang:** fase 1 (regenerasi `manifest.csv`/`text_audit.json`/`scorer.py`, murah ~15 menit CPU) **dan** fase 2 (republish `_meta/` yang baru sebagai New Version dari `jember-segments-16k` — audionya tidak berubah tapi tetap perlu ikut serta karena dibundel jadi satu paket, dan publish-nya server-side jadi tidak mahal), lalu fase 3 (verify) sebelum NB 03 mulai mount dataset itu.

### Spesifikasi runtime NB 08 — resmi, bukan lagi proksi dari repo analog

- Python 3.12, image berbasis `uv` (`pyproject.toml` + `uv.lock`)
- **1× NVIDIA A100 80GB VRAM, 24 vCPU, 220GB RAM**
- **Limit eksekusi 2 jam** per submission normal; smoke test **1 menit**
- **Tanpa akses jaringan** — semua bobot model wajib ikut di dalam ZIP
- `main.py` wajib di root `submission.zip`, baca dari `data/` (read-only), tulis ke `submission/submission.csv`
- Tidak ada root access di container
- Log dibatasi 500 baris / 300 karakter per baris, direview manual — jangan log apa pun tentang test set (bisa didiskualifikasi)
- Smoke test tidak mengurangi kuota submission harian; angka kuota harian yang pasti masih belum ketemu (baru muncul di halaman Submissions setelah join)
- Dependency tambahan lewat PR ke `pyproject.toml`/`uv.lock` di runtime repo — sama seperti dugaan lama, sekarang terkonfirmasi resmi

### Yang masih belum terjawab

- Diakritik (`ê/è/ě/é→e`) — masih tidak disebut di mana pun.
- Batas submission harian yang pasti.
- Item #14/#15 lama soal case-sensitivity dan titik kini **tertutup** (lihat di atas), tapi belum ditulis ulang ke tabel "Informasi yang masih belum diketahui" — lakukan itu di revisi berikutnya kalau ada waktu.

## Update 22 September 2026 — situs, forum, dan runtime repo dicek ulang

Dibaca 21–22 September dari halaman track Indonesian–Javanese, **forum resmi kompetisi** (belum pernah kita baca sebelumnya), dan runtime repo DrivenData. Ada satu perubahan besar, dan forum ternyata menjawab beberapa pertanyaan yang selama ini kita anggap masih terbuka.

> [!info] Sumber
> - Situs track: [Home](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription-in-jv/page/1/) · [Problem description](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription-in-jv/page/2/) · [Code submission format](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription-in-jv/page/16/) · [Official rules](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription-in-jv/rules/) · [Leaderboard](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription-in-jv/leaderboard/)
> - [Forum kategori Lost in Transcription](https://mdc-competitions.discourse.group/c/lost-in-transcription/5) — bisa dibaca tanpa login
> - [Runtime repo](https://github.com/drivendataorg/lost-in-transcription-runtime) — riwayat commit, `runtime/pyproject.toml`, pull request
>
> Halaman Submissions dan Data download butuh login, jadi **tidak ikut dicek**. Jumlah submission kita sendiri belum diverifikasi.

### Yang berubah

**1. Deadline mundur lagi: 2 Oktober 2026, 00:00 UTC** (07:00 WIB, 2 Oktober).

- [Pengumuman di forum](https://mdc-competitions.discourse.group/t/weve-extended-the-competition-deadline/49), 12 September, di-pin. Alasannya supaya peserta sempat submit ke ketiga track.
- Halaman Home sekarang menulis *Competition End Date: Oct. 2, 2026, midnight UTC*.
- **Submission yang dimulai sebelum deadline tetap dihitung** asal jalan sukses, walaupun baru selesai setelah deadline lewat.
- Item #13 berubah untuk ketiga kalinya: 16 September → 25 September → **2 Oktober**.

**2. Catatan baru di Code submission format, ditambahkan 10 September:** klip smoke test **berasal dari dev set**. Halaman yang sama sekarang juga menjelaskan aturan quoting CSV secara rinci. Transkrip yang mengandung koma, tanda kutip, atau baris baru wajib dibungkus tanda kutip, jadi file harus ditulis lewat library CSV, bukan dirakit manual per baris.

**3. Isi image runtime bertambah.**

| Paket | Masuk | Kegunaan |
|---|---|---|
| `kenlm==0.3.0`, `pyctcdecode==0.5.0` | 4 Sep | CTC beam search dengan language model |
| `ctranslate2==4.8.2`, `faster-whisper==1.2.1` | 9 Sep | Inference Whisper yang jauh lebih ringan. Jalan keluar kalau load model mepet limit 1 menit smoke test |

Torch di image **2.11.0+cu130**, dan override `transformers<5` masih berlaku. `peft`, `accelerate`, `vllm`, dan `qwen-asr` juga tersedia. Callout "Lead-time dependency" di atas praktis sudah tidak relevan: paket yang dulu kita khawatirkan sekarang ada semua, dan PR penambahan paket terbukti diproses dalam hitungan hari.

**4. R17 — aturan asisten coding sekarang tertulis eksplisit** (Official rules, bagian *External data*). Peserta boleh memakai asisten coding hosted dan tool pengembangan umum, **asal tidak mengunggah, mengirim, atau membuka Data, informasi rahasia, maupun materi nonpublik turunan Data** ke tool tersebut. Aturan ini belum tercatat di review 23 dan 25 Agustus; entah baru ditambahkan, entah terlewat. Klarifikasi penyelenggara ada di tabel berikutnya.

> [!note] Keputusan tim, 22 September
> R17 ditangani di akhir kompetisi, bukan sekarang. Dicatat di sini supaya tidak lupa: tinjau ulang sebelum memilih submission final, atau kalau masuk top 2 dan diminta dokumentasi pemenang.

### Klarifikasi penyelenggara di forum

Semua jawaban berasal dari pihak penyelenggara (DrivenData / MDC).

| Topik | Jawaban | Tanggal | Dampak ke kita |
|---|---|---|---|
| Limit submission | **3 per 7 hari per individu.** Untuk tim, limit berlaku per anggota | 1 Sep | Tim 3 orang = **9 submission per 7 hari** |
| Limit smoke test | **10 per hari.** UI sempat menampilkan angka yang salah | 9 Sep | Bebas dipakai untuk uji load time |
| Skor smoke test | Boleh diabaikan; smoke test hanya untuk memastikan kode jalan | 8 Sep | Seorang peserta dapat 0,1174 di smoke dan 0,3419 di full. Jangan dijadikan estimasi |
| Kolom `language` di `test_metadata.csv` | Nilainya **sama untuk semua klip** dalam satu track | 3 Sep | Routing per klip berdasarkan bahasa **tidak mungkin** |
| Statistik agregat test set | Tidak dipublikasikan. Menghitung atau me-log-nya dari kode submission **melanggar** aturan pemrosesan independen | 3 Sep | Jangan log statistik apa pun dari `test_metadata.csv` |
| Dataset MDC berklausul "no AI training" | Kalau ragu, peserta sendiri yang wajib minta izin eksplisit ke pemilik dataset | 1–2 Sep | Jember (disorot penyelenggara) dan Common Voice (CC0) aman |
| Asisten coding dan metrik agregat | Boleh, selama yang dikirim bukan Data atau turunan nonpublik dari Data | 1 Sep | Lihat R17 |
| Dev set di Kaggle privat | Bukan "ya" bersih. Yang dipersoalkan **unggahannya** — di mana salinan data berakhir — dan itu tergantung terms platform serta konfigurasinya | 9 Sep | Dataset Kaggle kita privat, tapi ini tetap penilaian kita sendiri |
| `omnilingual-asr` di runtime | Gagal karena dependensinya mengunci versi torch lama; penyelenggara tidak akan mengganti torch | 11 Sep | Model Omnilingual tidak realistis untuk submission |

Satu pertanyaan **tidak dijawab**: apakah referensi test dibuat dengan cara yang sama seperti dev. Menurut peserta yang bertanya, halaman dataset dev di MDC menyebut transkripnya dibuat otomatis dengan omniASR_LLM_3B lalu diedit manual. Ini belum kita cek langsung.

### Runtime repo

- **Tidak ada commit sejak 9 September.** `score.py` tidak berubah, jadi validasi `scorer.py` kita (selisih −0,0003, seragam di semua arm) tetap berlaku.
- Dua PR masih terbuka dan **belum merged**. Jangan menyusun rencana di atas keduanya:
  - **#8 "Add Huggingface model cache"**, dari maintainer, dengan CHANGELOG bertanggal 17 September. Kalau jadi, container akan me-mount cache model HF read-only di `/code_execution/huggingface_models/`, sehingga bobot tidak perlu ikut di ZIP. Isinya sekarang baru `openai/whisper-tiny`, dan model lain ditambahkan lewat admin.
  - **#7** menambahkan `sherpa-onnx`.

### Leaderboard 21 September

| Rank | WER publik |
|---|---|
| #1 | 0,2193 |
| #2 | 0,2198 |
| #3 | 0,2225 |
| #4 | 0,2228 |
| #5 | 0,2247 |
| #6 | 0,2269 |
| #7 | 0,2330 |

Estimasi dev E4 (0,2309 dengan normalizer resmi, 0,2336 di 222 klip yang tidak dipakai untuk seleksi) setara **sekitar #7–8**. Jarak ke #2 sekitar 0,014. Problem description sendiri menyebut dev set sebagai sanity check, bukan estimasi presisi. Skor test kita yang sebenarnya belum pernah terlihat.

### Yang tidak berubah

R1–R16, normalizer enam langkah (update 25 Agustus), metrik WER, layout container, hardware A100 80GB, limit 2 jam / 1 menit, batas log 500 baris × 300 karakter, output `submission/submission.csv`, lisensi MPL 2.0 untuk pemenang, dan hadiah $4.000 / $2.000 plus bonus lintas-track.

### Status pertanyaan lama

| Item | Status 22 September |
|---|---|
| #6 / P2 — jumlah submission per hari | **TERTUTUP.** 3 per 7 hari per anggota tim; smoke test 10 per hari |
| #13 — deadline | **BERUBAH.** 2 Oktober 2026, 00:00 UTC |
| P1 — paket di image dan cara menambahkannya | **TERTUTUP.** Lihat `runtime/pyproject.toml`; tambahan lewat PR ke runtime repo |
| P0 — diakritik | Terjawab lewat dev set resmi, bukan lewat penyelenggara. Lihat [[official-dev-set-analysis-2026-08-28\|Analisa Dev Set Resmi - 28 Agustus 2026]] |
| P2 — distribusi durasi test | **Ditolak penyelenggara.** Tidak ada statistik test yang dipublikasikan |

### Dampak ke rencana

- Jadwal di [[execution-plan|Rencana Eksekusi - Lost in Transcription]] masih memakai 25 September. Baca sebagai snapshot lama.
- NB 08 sudah ditulis (12 September) dan `main.py`-nya sudah sesuai semua ketentuan di atas, tapi **belum pernah dijalankan**. Per catatan 12 September, kita belum punya satu pun submission.
- Dengan sisa ±10 hari dan jatah 9 submission per minggu, urutannya: NB 08 dijalankan → smoke test → submission penuh pertama, baru kemudian NB 07.

## Pertanyaan untuk forum — versi siap kirim

Urut berdasarkan berapa banyak pekerjaan yang tertahan olehnya.

| P | Pertanyaan | Yang tertahan |
|---|---|---|
| **P0** | Does the pre-scoring normalizer fold diacritics (`ê`, `è`, `ě`, `é` → `e`)? The Jember corpus spells roughly 10.8% of its token mass inconsistently across annotators. | Pipeline teks, seluruh rencana pencampuran dataset, sampai ~10% nilai WER |
| **P0** | Is scoring case-sensitive, and is a sentence-final period preserved? Neither appears in the published normalizer description. | Bentuk teks latihan |
| **P0** | When do submissions open, and where will the runtime repository be published? | Seluruh Phase 7; menentukan apakah target kompetisi dipertahankan |
| **P1** | What are the container limits — GPU model, RAM, wall-clock per submission, maximum submission size? | Pemilihan ukuran model |
| **P1** | Which Python packages are available in the runtime image, and what is the process and deadline for requesting additions? | Boleh tidaknya memakai CTC dengan KenLM |
| **P1** | Is Indonesia within the eligible Territory for prize awards? | Keabsahan seluruh proyek sebagai kompetisi |
| **P2** | What is the daily submission limit? | Strategi eksperimen di leaderboard |
| **P2** | Test clips are `.mp3` — what is their duration distribution, and were they segmented with the same convention as the Jember TSV? | Panjang maksimum input, kebutuhan VAD |
| **P2** | Confirming there is no maximum team size — is a three-person team permitted? | Formalitas |

> [!warning] Cara bertanya
> R12 melarang private sharing kode dan data di luar tim, dan **apa pun yang dibagikan publik otomatis berlisensi MPL**. Pertanyaan di atas aman karena tidak memuat kode maupun temuan. Kalau nanti ingin memposting potongan kode di forum, sadari bahwa itu langsung menjadi MPL dan terbaca semua pesaing.

## Yang berubah dari catatan lama

| Catatan | Bagian | Perubahan |
|---|---|---|
| [[feasibility-study\|Feasibility Study - Mozilla Lost in Transcription]] | Rules & Constraints | Ditambah R14 (free commercial use), R15 (eligibility), dan konfirmasi tidak ada batas ukuran tim |
| [[feasibility-study\|Feasibility Study - Mozilla Lost in Transcription]] | Informasi yang masih belum diketahui | Item 7, 8, 10 tertutup; item 9 turun prioritas; item 12 sampai 15 ditambahkan |
| [[feasibility-study\|Feasibility Study - Mozilla Lost in Transcription]] | Konfigurasi model | **MMS resmi gugur** karena R14, bukan lagi sekadar "perlu diverifikasi" |
| [[nb01-dataset-analysis\|Analisa Dataset - Notebook 01]] | Pertanyaan untuk penyelenggara | Pertanyaan diakritik naik menjadi P0 bersama case-sensitivity dan titik |
| — | baru | Prinsip **latih pada keluaran normalizer** (K1 sampai K3) |
| [[execution-plan\|Rencana Eksekusi - Lost in Transcription]] | Jadwal | Deadline 25 September usang; sekarang **2 Oktober** (update 22 September) |

Rencana turunannya ada di [[execution-plan|Rencana Eksekusi - Lost in Transcription]].
