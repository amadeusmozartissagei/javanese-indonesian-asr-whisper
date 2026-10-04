---
title: "Hasil Notebook 04 — Fine-tune Whisper Core (Lost in Transcription)"
aliases:
  - Hasil Notebook 04 - Whisper Core
  - Hasil Notebook 04
  - Whisper Core
tags:
  - research
  - competition
  - asr
  - finetune
  - gate2
status: final
created: 2026-08-31
updated: 2026-08-31
notebook: notebooks/04-whisper-core.ipynb
data: findings/04-whisper-core/dataset_findings.json
source_type: measured-from-data
---

# Hasil Notebook 04 — Fine-tune Whisper Core

> [!success] Gate 2 — LOLOS 5/5, lewat ablation `concat25`
> Run baseline (`native`) **gagal** kriteria pertama: dev resmi 0,2695 → 0,2650, CI memuat nol. Ablation **`concat25` lolos**: **0,2695 → 0,2524**, CI [−0,0327, −0,0027], p(better) 0,992 — terbukti. Satu-satunya variabel yang berubah adalah panjang segmen latihan, dan runnya justru **lebih murah**: 2,45 jam lawan 4,36 jam.
>
> **Ibaratnya:** karyawan yang sama, materi yang sama, cuma format latihannya diubah dari potongan-potongan lima detik menjadi paragraf utuh seperti pekerjaan aslinya. Itu saja yang membedakan lulus dan tidak.

> [!danger] Dua temuan yang lebih penting daripada kelulusan itu sendiri
> **1. Dev Jember menunjuk ke arah yang salah.** `concat25` lebih **buruk** di Jember (0,3613 lawan 0,3458) dan lebih **baik** di dev resmi (0,2524 lawan 0,2650). Memilih model berdasarkan dev Jember akan memilih model yang keliru. Ia bukan sekadar proxy yang terlalu optimistis — di sini ia **antikorelasi**.
>
> **2. Hampir seluruh manfaat datang dalam 25 step pertama.** Kurva dev resmi: 0,2516 di step 25 (epoch 0,28), 0,2505 di step 250. 225 step berikutnya membeli **0,1 poin** di lapisan yang dinilai, sementara dev Jember turun 16 poin di rentang yang sama.

> [!info] Sifat angka di catatan ini
> **Dua run, satu variabel yang berbeda.** `native` (baseline): 1.041 step, 3 epoch, 4,36 jam, mentah di `findings/04-whisper-core/`. `concat25` (ablation): 273 step, 3 epoch, 2,45 jam, mentah di `findings/04-whisper-core-full-concat25/`. Keduanya Kaggle T4 tunggal, optimizer `adafactor` (bitsandbytes tidak ada di image), target `text_folded`, decode identik — greedy, `no_repeat_ngram_size=4`, `LONG_MODE="chunk"`, `GEN_MAX_LENGTH=225`. **Pembanding zero-shot diukur di dalam notebook ini**, bukan diambil dari NB 03, dan cache-nya divalidasi terhadap sidik jari setelan decode. Setiap klaim "lebih baik" adalah paired bootstrap 2.000 resample.

## Run baseline `native` — kenapa ia gagal

Bagian ini dan tiga bagian berikutnya menganalisa run **`native`**. Analisanya tetap berlaku dan justru menjelaskan kenapa `concat25` menang. Dev resmi 372 klip, 17.473 token referensi:

| metrik | zero-shot | fine-tuned | delta |
|---|---:|---:|---:|
| WER total | 0,2695 | 0,2650 | **−0,0045** |
| WER Jawa | 0,4370 | 0,2287 | **−0,2083** |
| WER Indonesia | 0,1836 | 0,2373 | **+0,0537** |
| WER kata dua-bahasa | 0,1609 | 0,1431 | −0,0178 |
| WER kata tak dikenal | 0,4253 | 0,4307 | +0,0054 |
| `jv_to_id` | 33,03% | 17,37% | **−15,66** |
| deletion rate | 0,0607 | 0,0239 | −0,0368 |
| insertion rate | 0,0207 | 0,0399 | +0,0192 |
| hipotesis mengandung digit | 16,40% | 2,15% | **−14,25** |
| rasio panjang hyp/ref | 0,9599 | 1,0160 | +0,0561 |

## Massa error, bukan rate — ini kuncinya

Rate per kelas menyesatkan kalau kelasnya tidak sama besar. Komposisi token referensi dev resmi: **dua-bahasa 39,6%, Indonesia 30,5%, Jawa 16,2%, tak dikenal 13,7%**.

| kelas | token | error zero-shot | error fine-tuned | selisih |
|---|---:|---:|---:|---:|
| Indonesia | 5.331 | 979 | 1.265 | **+286** |
| dua-bahasa | 6.913 | 1.112 | 989 | −123 |
| Jawa | 2.833 | 1.238 | 648 | **−590** |
| tak dikenal | 2.396 | 1.019 | 1.032 | +13 |
| **total** | 17.473 | **4.709** | **4.631** | **−78** |

Perbaikan sisi Jawa besar dan nyata: **massa error Jawa turun 48%**. Tapi sisi Jawa cuma 16,2% dari token, sementara sisi Indonesia 30,5% — jadi kemenangan 590 error dimakan 286 error kerugian, dan sisanya diserap kelas `unk` yang tidak bergerak sama sekali.

> [!warning] Kelas `unk` tidak tersentuh, dan ia memiliki 22% massa error
> 2.396 token (13,7%) tidak ada di `lexicon_v1` — nama diri, serapan Inggris, ejaan yang tidak muncul di Jember. WER-nya 0,425 sebelum dan 0,431 sesudah. Data Jember tidak bisa memperbaikinya, dan ini seperlima dari seluruh error yang tersisa.

## Diagnosis: modelnya tidak belajar mendengar, ia belajar prior baru

Ini kalimat terpenting di seluruh catatan. Bandingkan confusion yang **dihapus** fine-tuning dengan yang **diciptakannya**:

**Dihapus** — persis kegagalan yang diidentifikasi [[nb03-zeroshot-baseline-results|Hasil Notebook 03 - Zero-shot Baseline]]:

| ref → hyp | zero-shot | fine-tuned |
|---|---:|---:|
| `iki → ini` | 21 | 0 |
| `dadi → jadi` | 18 | 2 |
| `nek` dihapus | 16 | 0 |
| `sing → yang` | 15 | 0 |
| `soale → soalnya` | 15 | 0 |
| `dua → 2` | 21 | 0 |
| `e...` dihapus | 55 | 0 |

**Diciptakan:**

| ref → hyp | zero-shot | fine-tuned |
|---|---:|---:|
| `kayak → kaya` | 5 | 100 |
| `e` disisipkan | 0 | 83 |
| `tuh → tu` | 0 | 74 |
| `gak → nggak` | 3 | 61 |
| `e...` disisipkan | 0 | 50 |
| `pengen → pengin` | 0 | 27 |
| `jadi → dadi` | 0 | 25 |
| `sampai → sampek` | 0 | 23 |

Totalnya: **3.583 instance error dihapus, 3.505 diciptakan, net −78.** Dua gerakan raksasa yang berlawanan arah dan nyaris saling meniadakan.

Perhatikan `dadi → jadi` turun dari 18 ke 2, sementara `jadi → dadi` naik dari 0 ke 25. Model berhenti menerjemahkan Jawa ke Indonesia — lalu mulai menerjemahkan Indonesia ke Jawa. Ia tidak belajar *mendengar* mana yang diucapkan. Ia menukar satu prior buta dengan prior buta lainnya.

## Sebagian besar kerugian itu konvensi transkripsi, bukan pendengaran

Frekuensi bentuk ejaan di kedua korpus, dihitung dari referensi resmi dan dari `manifest.csv`:

| bentuk resmi | bentuk model | di dev resmi | di Jember | error |
|---|---|---|---|---:|
| `kayak` | `kaya` | 140 vs 9 | 2 vs 738 | 95 |
| `tuh` | `tu` | 154 vs 8 | 1 vs 2 | 74 |
| `pengen` | `pengin` | 35 vs 0 | 7 vs 72 | 27 |
| `jadi` | `dadi` | 255 vs 35 | 7 vs 706 | 25 |
| `sampai` | `sampek` | 34 vs 0 | 3 vs 143 | 23 |
| `tahun` | `taun` | 27 vs 0 | 3 vs 56 | 22 |
| `karena` | `karna` | 47 vs 0 | 49 vs 66 | 19 |

Preferensinya terbalik sempurna antara kedua korpus. Model menyerap konvensi Jember secara utuh — termasuk cara Jember menuliskan filler, yang menjelaskan 164 dari 264 insertion (`e` 83, `e...` 50, `ya` 31).

Sebagian bisa ditambal tanpa data baru sama sekali. Untuk pasangan yang bentuk modelnya **tidak pernah** muncul di referensi resmi (`pengin`, `sampek`, `taun`, `karna`) penulisan ulang output aman total: **91 error**. Kalau pasangan yang rasionya sangat timpang ikut disertakan (`kaya`→`kayak` memperbaiki 95 dan paling banter merusak 9; `tu`→`tuh` 74 lawan 8), perkiraan konservatifnya **±250 error ≈ 1,4 poin WER** — bukan solusinya, tapi murah dan nyata untuk [[nb08-brief-packaging-submission|Brief Notebook 08 - Packaging dan Submission]].

`gak` vs `nggak` **tidak** masuk kategori ini: di referensi resmi 135 lawan 107, benar-benar campur. Di situ model hanya bisa menang dengan benar-benar mendengar.

## Yang harus dicatat sebagai kemenangan

- **Prosedur trainingnya sehat.** Overfit 32 segmen: WER 0,0161 terhadap target sendiri. Kurva eval turun monoton 0,4125 → 0,3401 di delapan titik, loss ikut turun, tidak ada tanda overfitting, early stopping tidak pernah menyala. Tidak ada bug label, masking, atau normalisasi.
- **`jv_to_id` turun 33,03% → 17,37%.** Angka penjaga dari NB 03 bergerak ke arah yang benar, di lapisan yang benar.
- **Masalah digit selesai.** 16,4% → 2,15% hipotesis mengandung angka, cocok dengan konvensi referensi resmi yang tidak pernah memakai numeral.
- **Model berhenti membuang kata.** Deletion rate 0,0607 → 0,0239; rasio panjang 0,96 → 1,016.
- **Checkpoint-resume terbukti**, in-process dan cross-session, dan checkpoint terbaik ada di HF privat dengan revision tercatat.

## Temuan yang mengubah perencanaan proyek

> [!danger] Proxy Jember melebih-lebihkan kesulitan test, dan selisihnya besar
> Zero-shot turbo, setelan decode identik: **0,7499 di dev Jember, 0,2695 di dev resmi.** Hipotesis dari 8 klip di run sanity ternyata bertahan di n=372. Selama ini seluruh proyek berlabuh pada angka Jember, termasuk WER 0,8960 di [[nb03-zeroshot-baseline-results|Hasil Notebook 03 - Zero-shot Baseline]].
>
> Konsekuensinya: headroom sebenarnya jauh lebih sempit dari yang diasumsikan, dan **setiap keputusan yang divalidasi hanya di dev Jember patut ditinjau ulang**. Dev Jember tetap berguna untuk memantau progres training — murah dan besar — tapi ia bukan wakil distribusi test dan tidak pernah boleh dipakai sendirian untuk memutuskan.

## Ablation `concat25` — dan kurva yang seharusnya ada sejak awal

Item latihan disambung dari segmen berurutan sampai ~25 detik: 1.455 item rata-rata 20,7 detik, dari audio dan token yang **sama persis** dengan baseline. Dev tetap native, decode tetap identik. Run 2,45 jam, 273 step.

Dev resmi 372 klip, ketiganya berdampingan:

| metrik | zero-shot | native | `concat25` |
|---|---:|---:|---:|
| **WER total** | 0,2695 | 0,2650 | **0,2524** |
| WER Jawa | 0,4370 | 0,2287 | 0,2316 |
| WER Indonesia | 0,1836 | 0,2373 | **0,2185** |
| WER dua-bahasa | 0,1609 | 0,1431 | 0,1368 |
| **WER tak dikenal** | 0,4253 | 0,4307 | **0,3944** |
| deletion | 0,0607 | 0,0239 | 0,0204 |
| `jv_to_id` | 33,03% | 17,37% | 17,50% |
| digit di hipotesis | 16,40% | 2,15% | 1,88% |
| **WER dev Jember** | 0,7499 | **0,3458** | 0,3613 |

Keuntungannya **tidak** datang dari sisi Jawa — di situ keduanya setara. Ia datang dari dua tempat: regresi Indonesia yang lebih kecil (−1,9 poin dibanding native) dan **kelas `unk` yang akhirnya bergerak** (−3,6 poin, pertama kalinya kelas ini merespons apa pun). Masuk akal: konteks yang lebih panjang membantu model menebak nama diri dan serapan.

### Kurva dev resmi selama training

Diukur di 150 klip tetap, di tiap titik eval — artefak baru run ini:

| step | epoch | WER resmi | Jawa | Indonesia | WER Jember |
|---:|---:|---:|---:|---:|---:|
| 25 | 0,27 | **0,2516** | 0,2914 | **0,1778** | 0,5204 |
| 50 | 0,55 | 0,2579 | 0,2609 | 0,2067 | 0,4421 |
| 75 | 0,82 | 0,2690 | 0,2487 | 0,2124 | 0,4104 |
| 100 | 1,10 | 0,2559 | 0,2312 | 0,2048 | 0,4013 |
| 150 | 1,65 | 0,2616 | 0,2208 | 0,2300 | 0,3808 |
| 200 | 2,20 | 0,2509 | 0,2173 | 0,2124 | 0,3634 |
| 250 | 2,75 | **0,2505** | 0,2243 | 0,2143 | **0,3578** |

> [!warning] Baca baris pertama dan terakhir bersamaan
> Di **step 25**, model sudah memperbaiki Jawa 14,6 poin (0,4370 → 0,2914) **tanpa merusak Indonesia sama sekali** — 0,1778 justru sedikit lebih baik dari zero-shot 0,1836. Di step 250, Jawa membaik 6,7 poin lagi tapi Indonesia memburuk 3,7 poin, dan totalnya berhenti di tempat yang sama.
>
> Jadi 225 step tambahan itu bukan pembelajaran, melainkan **pertukaran**: membeli akurasi Jawa dengan akurasi Indonesia, pada distribusi yang 70% tokennya Indonesia atau dua-bahasa. Model step-25 mencapai WER total yang sama tanpa membayar pajak itu, dan bentuknya jauh lebih sehat untuk digeneralisasi ke test set yang komposisinya belum tentu identik dengan dev.
>
> Selisih 0,2516 lawan 0,2505 sendiri ada di dalam noise dan diukur pada 150 klip — yang kuat bukan selisihnya, melainkan **dekomposisinya**, yang konsisten di sepuluh titik.

## Run 1-epoch — resep dasar untuk NB 06

Menguji apa yang disiratkan kurva: apakah 1 epoch mencapai WER total yang sama tanpa membayar pajak Indonesia. `concat25`, 91 step, **0,68 jam** wall-clock.

| metrik | zero-shot | 3 epoch | 1 epoch |
|---|---:|---:|---:|
| **WER resmi total** | 0,2695 | **0,2524** | **0,2532** |
| WER Jawa | 0,4370 | 0,2316 | 0,2513 |
| **WER Indonesia** | 0,1836 | 0,2185 | **0,2058** |
| WER dua-bahasa | 0,1609 | 0,1368 | 0,1379 |
| WER tak dikenal | 0,4253 | 0,3944 | 0,4057 |
| **`jv_to_id`** | 33,03% | 17,50% | **14,31%** |
| digit di hipotesis | 16,40% | 1,88% | 2,42% |
| WER dev Jember | 0,7499 | 0,3613 | 0,4054 |
| **wall-clock** | — | 2,45 jam | **0,68 jam** |

Selisih total 0,0008 — jauh di dalam noise; keduanya lolos Gate 2 sendiri-sendiri (1 epoch: CI [−0,0306, −0,0026], p 0,99). Tapi bentuknya berbeda: 3 epoch membeli 2 poin Jawa dengan 1,3 poin Indonesia, dan **1 epoch justru lebih baik di angka penjaga** `jv_to_id` (14,31% lawan 17,50%). Untuk test set yang komposisi Jawa/Indonesianya belum tentu identik dengan dev, model yang kurang terdistorsi lebih bisa dipercaya.

**Resep dasar untuk NB 06: 1 epoch.** Seri pada metrik yang dinilai, lebih baik pada dua metrik penjaga, dan **3,6× lebih murah** — yang berarti setiap rasio pencampuran di NB 06 bisa diuji dengan biaya sepertiga.

> [!warning] Koreksi atas pembacaan kurva sebelumnya
> Catatan ini sempat menyimpulkan "hampir seluruh manfaat datang dalam 25 step pertama". Itu **artefak jadwal**, bukan sifat model. Run 1-epoch punya jadwal LR yang meluruh sepanjang 91 step, dan di step 25 ia baru mencapai 0,2738 — lebih buruk dari step 25 run 3-epoch. Yang bertahan lintas jadwal adalah kesimpulan yang lebih longgar dan tetap berguna: **satu epoch sudah cukup**. Jangan mencoba melatih 25 step.

## Kriteria Gate 2

Dinilai pada run `concat25` (run `native` gagal kriteria pertama):

- [x] **WER dev fine-tuned lebih baik dari zero-shot** — 0,2695 → 0,2524, CI [−0,0327, −0,0027], p(better) 0,992. *(native: 0,2650, CI memuat nol — gagal.)*
- [x] **WER Jawa membaik** — 0,4370 → 0,2316.
- [x] **`jv_to_id` tidak lebih buruk** — 33,03% → 17,50%.
- [x] **Checkpoint-resume terbukti** — in-process dan cross-session.
- [x] **Checkpoint di HF privat dengan revision** — `amozaurus/mozilla-jv-04-whisper-core-full-concat25`.

**Gate 2 lolos. [[nb06-brief-data-mixing|Brief Notebook 06 - Data Mixing]] boleh mulai.**

## Rekomendasi

Gate 2 sudah lolos, jadi pertanyaannya bukan lagi "boleh lanjut atau tidak", melainkan ke mana kuota berikutnya dibelanjakan.

**1. Hentikan pemakaian dev Jember sebagai pemilih.** Ini konsekuensi paling mendesak dari run ini. Dev Jember menyatakan `native` lebih baik; dev resmi menyatakan `concat25` lebih baik; yang kedua yang dinilai. Ia masih berguna sebagai penanda bahwa training berjalan — murah dan besar — tapi **tidak boleh lagi memutuskan apa pun sendirian**, termasuk pemilihan checkpoint. Untuk NB 06, pemilihan checkpoint sebaiknya pindah ke dev resmi, dengan kesadaran penuh bahwa itu mulai membelanjakannya sebagai sinyal tuning; alternatif yang lebih hemat adalah memilih pada subset tetap 150 klip dan menyimpan 222 sisanya sebagai validasi yang tidak pernah disentuh.

**2. Resep dasar sudah diuji dan berubah: 1 epoch, bukan 3.** Seri pada WER resmi (0,2532 lawan 0,2524), lebih baik pada `jv_to_id` dan WER Indonesia, **3,6× lebih murah**. Pakai ini sebagai titik awal setiap eksperimen NB 06.

**3. Baru NB 06, dan targetnya sekarang berangka.** Sisa error terbesar sudah teridentifikasi dan tidak satu pun bisa disentuh data Jember:
- **WER Indonesia 0,2185, masih lebih buruk dari zero-shot 0,1836.** Fine-tuning tetap merusak sisi Indonesia sebesar 3,5 poin. Common Voice Indonesian menyasar ini secara langsung.
- **Kelas `unk` 0,3944 atas 2.396 token** — seperlima massa error, dan `concat25` baru menggerakkannya 3,6 poin.

**4. Untuk NB 08, ada ~250 error yang bisa dipanen tanpa model sama sekali** — penulisan ulang varian ejaan yang preferensinya terbalik antara Jember dan referensi resmi. Sekitar 1,4 poin, murah, dan tidak berinteraksi dengan apa pun di atas.

Yang **tidak** perlu dilakukan: menambah epoch, dan mengaudit ulang label atau learning rate.

## Lampiran — tiga run, konfigurasi lengkap

Yang sama di ketiganya: `openai/whisper-large-v3-turbo`, language token `jw`, target `text_folded`, lr 6e-06 dengan warmup 10% dan linear decay, batch efektif 16 (4 × grad accum 4), optimizer adafactor, fp16 + gradient checkpointing, SpecAugment on, decode greedy `no_repeat_ngram_size=4` `GEN_MAX_LENGTH=225` `LONG_MODE="chunk"`, pemilihan checkpoint pada WER dev Jember.

| | `native` | `concat25` | `concat25` 1 epoch |
|---|---|---|---|
| item latihan | 5.541 @ 5,4 dtk | 1.455 @ 20,7 dtk | 1.455 @ 20,7 dtk |
| epoch / step | 3 / 1.041 | 3 / 273 | **1 / 91** |
| eval tiap | 125 step | 25 step | 25 step |
| checkpoint terpilih | 1000 (Jember 0,34006) | 250 (0,35781) | 75 (0,40306) |
| peak VRAM | 7,03 GB | — | — |
| wall-clock | 4,36 jam | 2,45 jam | **0,68 jam** |
| **WER dev resmi** | 0,2650 | **0,2524** | **0,2532** |
| Gate 2 | gagal kriteria 1 | **lolos 5/5** | **lolos 5/5** |
| findings | `04-whisper-core/` | `04-whisper-core-full-concat25/` | `…-full-concat25-1epoch/` |

Dev selalu native di ketiga run, dan pembanding zero-shot diukur ulang di dalam tiap run dengan sidik jari setelan decode yang diverifikasi — jadi ketiga kolom sebanding.
