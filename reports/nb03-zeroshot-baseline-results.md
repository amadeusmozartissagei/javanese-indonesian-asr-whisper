---
title: "Hasil Notebook 03 — Zero-shot Baseline (Lost in Transcription)"
aliases:
  - Hasil Notebook 03 - Zero-shot Baseline
  - Hasil Notebook 03
  - Zero-shot Baseline
tags:
  - research
  - competition
  - asr
  - baseline
status: final
created: 2026-08-27
updated: 2026-08-27
notebook: notebooks/03-zeroshot.ipynb
data: findings/03-zeroshot/dataset_findings.json
source_type: measured-from-data
---

# Hasil Notebook 03 — Zero-shot Baseline

> [!summary] Ringkasan
> Grid penuh 5 model × 3 language token dijalankan atas 1.097 utterance dev (1,63 jam), 30 baris hasil, 8/9 self-check lolos. **Baseline fine-tune: `whisper-large-v3-turbo`**, menang telak atas setiap model yang lebih murah di uji paired bootstrap. Angka mentahnya brutal — **WER 0,8960** — tapi strukturnya justru kabar baik: kesalahannya **bukan akustik**. Whisper mendengar dengan benar lalu **menerjemahkan Jawa ke Indonesia** (`iku→itu`, `sing→yang`, `dadi→jadi`) atau **membuangnya** — persis yang seharusnya diperbaiki fine-tuning. Dua temuan mengoreksi pembacaan pertama: pilihan `id` atas `jw` **tidak nyata secara statistik**, dan **6 poin WER hilang cuma karena decoder terjebak loop pengulangan**, bukan karena modelnya tidak tahu jawabannya.
>
> **Ibaratnya:** ini seperti mengetes penerjemah yang fasih bahasa Indonesia tapi baru pertama kali dengar bahasa Jawa. Dia menangkap bunyinya dengan benar, tapi refleksnya menuliskan padanan Indonesianya — bukan apa yang benar-benar diucapkan. Dan di beberapa rekaman dia macet seperti piringan hitam tergores, mengulang satu kata ratusan kali. Yang pertama butuh pelatihan; yang kedua cuma butuh mengganti setelan jarumnya.

> [!info] Sifat angka di catatan ini
> Diukur di Kaggle T4 dari mount `jember-segments-16k` yang sudah diverifikasi ([[nb02-data-build-results|Hasil Notebook 02 - Data Build]]). `scorer.self_test()` 30/30 dari mount. Referensi utama `text_official`; `text_folded` dilaporkan berdampingan. Seed `20260827`. Mentah di `findings/03-zeroshot/`. Setiap uji "nyata/tidak" di bawah adalah **paired bootstrap** (`scorer.compare_systems`, 2.000 resample) — nol GPU.

## Keputusan

> [!check] Baseline fine-tune: `whisper-large-v3-turbo`, language token `id` **atau** `jw`
> Turbo adalah satu-satunya model yang lolos uji siku. Soal language token, `id` dan `jw` **seri** — pilih atas dasar lain, bukan atas dasar WER. Ini masuk ke [[nb04-brief-finetune-whisper-core|Brief Notebook 04 - Finetune Whisper Core]] sebagai titik awal.

## Q1 — kurva ukuran model, dan siku yang tidak ada

Aturannya bukan "WER terendah menang" melainkan **model termurah yang tidak terbukti lebih buruk dari juara** (95% CI selisih masih memuat nol). Ternyata tidak ada satu pun.

| model | lang | WER | Δ vs juara | 95% CI selisih | lolos |
|---|---|---|---|---|---|
| whisper-tiny | jw | 2,4366 | +1,5407 | [+1,190, +1,906] | tidak |
| whisper-base | id | 2,0626 | +1,1666 | [+0,849, +1,459] | tidak |
| whisper-small | id | 1,3346 | +0,4386 | [+0,239, +0,663] | tidak |
| whisper-medium | id | 1,3602 | +0,4642 | [+0,244, +0,716] | tidak |
| **whisper-large-v3-turbo** | **id** | **0,8960** | — | — | **juara** |

Dua hal menonjol. **Kurvanya datar dari `medium`** — `medium` (1,3602) sedikit lebih buruk dari `small` (1,3346) meski 3× lebih besar, jadi menaikkan ukuran di kelas menengah tidak dibayar. Lalu turbo melompat 0,44 poin di bawah keduanya sambil **lebih murah dari `medium`** (1,6 GB vs 3,1 GB, 0,203 vs 0,415 detik/klip). Turbo bukan kompromi — ia menang di WER, ukuran, dan kecepatan sekaligus.

## Q2 — language token: satu klaim yang harus ditarik

Tabel mentahnya menggoda: `id` 0,8960 vs `jw` 0,9184 vs `auto` 0,9433. Notebook versi pertama melaporkan "`id` menang". **Itu tidak benar.**

| perbandingan | Δ | 95% CI | vonis |
|---|---|---|---|
| `jw` vs `id` | +0,0224 | **[−0,129, +0,159]** | **seri** — CI memuat nol, p(jw lebih baik) 0,360 |
| `auto` vs `id` | +0,0473 | [+0,004, +0,110] | `auto` **benar-benar lebih buruk** |

Jadi yang bisa dikatakan: **memaksa language token mengalahkan autodetect, tapi `id` dan `jw` tidak bisa dibedakan.** Menariknya keduanya membagi beban dengan cara berlawanan — `jw` lebih baik di token Jawa (`wer_jv` 0,8404 vs 0,8969), `id` lebih baik di token Indonesia (`wer_id` 0,6673 vs 0,6438 — terbalik). Totalnya saling menghapus. Untuk fine-tuning ini praktis bebas pilih; **`jw` sedikit lebih masuk akal** karena sisi Jawa yang harus paling banyak diperbaiki.

> [!warning] Distribusi bahasa terdeteksi tidak terukur
> `detected_lang_distribution` keluar `{"?": 1097}` — satu-satunya check yang gagal. Penyebabnya sudah dipastikan lewat probe: **transformers 5.0.0 tidak mengembalikan prefix decoder dari `generate()`**, jadi tidak ada token bahasa di indeks mana pun (probe mencetak `['Ġaku','Ġkan','Ġmau','Ġan']` — kata biasa). Sudah diganti memakai `model.detect_language()`. Karena `auto` **kalah** dan tidak dipakai, ini diagnostik yang hilang, bukan keputusan yang tertahan.

## Q3 — inilah masalah sebenarnya

`jv_to_id_sub_pct` **30,15%**: dari 2.471 substitusi yang token referensinya berkelas Jawa, **745 diganti kata Indonesia**. Ditambah penghapusan, polanya konsisten di seluruh tabel error:

```
ins  ->  dulu   435      del  ya     145      sub  iku  -> itu   121
ins  ->  gede   193      del  iku    127      sub  sing -> yang   62
                         del  sing    81      sub  dadi -> jadi   56
                         del  ngono   69      sub  ndèk -> di     51
                         del  lèk     52      sub  těrus-> terus  46
```

Kolom kanan adalah **penerjemahan**, kolom tengah adalah **pembuangan**. Keduanya kegagalan yang sama: Whisper memperlakukan Jawa sebagai Indonesia beraksen, bukan sebagai bahasa yang harus ditranskripsi. Itu tepat yang bisa dipindahkan oleh fine-tuning, dan `jv_to_id_sub_pct` sekarang jadi **angka penjaga** — kalau NB 04 menurunkan WER tapi angka ini tidak ikut turun, perbaikannya datang dari sisi Indonesia saja dan tidak akan bertahan di test set.

## Enam poin WER yang hilang percuma

Kolom kiri di atas bukan kesalahan pengenalan — itu **loop pengulangan**. `dulu` adalah token hipotesis paling sering di seluruh dev set (451 kemunculan), dan `dulu` + `gede` sendirian menyumbang **628 dari ~1.318 insertion**, hampir separuhnya.

```
rec 191   n= 31   wer 2,324   ref_tok 299 -> hyp_tok 678   ins 1,485
rec  52   n= 20   wer 1,860   ref_tok 228 -> hyp_tok 435   ins 1,132
rec   2   n=313   wer 0,767   ref_tok 1986 -> hyp_tok 1572 ins 0,036
```

Tiga rekaman meledak; sisanya waras. Contohnya `kuwi e... dudu iki ya dudu perkara sing apa` dijawab `itu dulu dulu dulu dulu dulu dulu ...` sebanyak 15 kali.

> [!tip] Ini ~6 poin gratis, tanpa training
> 628 insertion atas 10.391 token referensi = **6,04 poin WER**, murni dari decoder greedy tanpa pengaman. `BASE_GEN_KWARGS` sekarang punya knob `DECODE_HYGIENE` (default `False` supaya grid 27 Agustus tetap reproducible) yang menyalakan `no_repeat_ngram_size=4`. Mengukurnya cuma butuh **satu model, satu language token, ~4 menit GPU** — bukan grid ulang. Kalau terbukti, setelan ini ikut ke NB 04 (evaluasi) **dan** NB 08 (inference submission), bukan cuma ke sini.

## Dua bug yang ditemukan smoke run

> [!danger] Smoke run membayar dirinya sendiri
> **Selektor baseline salah.** `best_model = best_per_model["model"].iloc[0]` membaca baris pertama tabel yang **diurutkan berdasarkan ukuran**, jadi selalu mengembalikan `whisper-tiny`. Di smoke run ia "memilih" tiny pada WER 2,62 sementara turbo ada di 0,75, lalu mencetak alasan yang palsu: *"tiny has the lowest WER"*. Kalau tidak tertangkap, NB 04 akan disuruh fine-tune model terkecil. Diganti dengan aturan siku berbasis paired bootstrap.
>
> **Self-validation meloloskannya**, karena check-nya cuma memastikan keputusan *ada*. Sekarang ada tiga guard tambahan: baseline terpilih tidak provably worse dari juara, tidak ada model lebih murah yang terlewat, dan autodetect melaporkan token asli. Check terakhir itulah satu-satunya yang gagal di run ini — persis fungsinya.

## Anggaran waktu, untuk NB 08

| model | disk | detik/klip (bs8, T4) |
|---|---|---|
| whisper-large-v3-turbo | 1.622 MB | **0,203** |
| whisper-medium | 3.060 MB | 0,415 |
| whisper-small | 971 MB | 0,101 |

Turbo memproses 1.097 klip dalam ~3,7 menit di T4. Kontainer submission memakai **A100 80 GB dengan limit 2 jam** ([[rules-review-2026-08-23|Kaji Ulang Peraturan - 23 Agustus 2026]]), jadi bahkan test set sepuluh ribu klip pun lapang. **Waktu inference bukan kendala** — bobot 1,6 GB di dalam ZIP juga aman.

## Yang belum terjawab

- **Dev set resmi 372 klip masih belum dipakai.** Seluruh angka di atas diukur pada dev split Jember, yang gaya bicaranya wawancara, bukan voice note dyadic seperti test. WER 0,8960 adalah baseline pada proxy — belum dikalibrasi ke distribusi sebenarnya. Lihat [[nb02-cross-audit-scorer-text-2026-08-26|Audit Silang - Scorer dan Asumsi Teks (26 Agustus 2026)]].
- **Diakritik.** `text_folded` cuma memperbaiki 0,8960 → 0,8719 (2,4 poin), jauh di bawah 14,3% beban diakritik korpus — karena modelnya terlalu jarang benar sampai diakritik jadi soal. Pertanyaan targetnya tetap terbuka sampai `indonesian_dev/metadata.tsv` dibaca.
- **Varian antar rekaman besar**: std 0,4112, dari 0,6875 (rec 111) sampai 2,3244 (rec 191). Sebagian besar sebaran itu adalah loop pengulangan di atas, bukan kesulitan asli.

## Berikutnya

[[nb04-brief-finetune-whisper-core|Brief Notebook 04 - Finetune Whisper Core]] dan [[nb05-brief-xlsr-ctc-lm|Brief Notebook 05 - XLS-R CTC dan LM]] berjalan paralel. Bawa: `whisper-large-v3-turbo`, language token `jw`, `jv_to_id_sub_pct` 30,15% sebagai angka penjaga, dan WER 0,8960 sebagai garis dasar yang harus dikalahkan telak.
