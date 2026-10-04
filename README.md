---
title: "README — Mozilla Lost in Transcription (Indonesian–Javanese)"
aliases:
  - README
  - Peta Repo
tags:
  - index
status: closed
updated: 2026-10-05
---

# Mozilla *Lost in Transcription* — track Indonesian–Javanese

Riset dan pipeline tim **"Bulu Hidung"** untuk kompetisi ASR code-switching Indonesia–Jawa
(Mozilla Data Collective × DrivenData). Model: fine-tune `openai/whisper-large-v3-turbo`,
bahasa `jw`. Semua komputasi jalan di **Kaggle**. Repo ini hanya berisi notebook,
catatan, dan keluaran kecil (CSV/JSON); bobot model ada di HuggingFace (private), dan korpus
mentah (`Datasets/`) serta ZIP submission tidak ikut di git.

**Kompetisi sudah ditutup.** Metrik: WER, dengan `score.py` resmi (case-sensitive).

## Status akhir (3 Okt 2026)

| | |
|---|---|
| Skor test terbaik | **0,2497, peringkat 25**: L = stage 1 E4-native **+ TTS Central Javanese** + tahap 2 di dev resmi + beam 5 (submission `3516`, 3 Okt) |
| Sebelumnya | J 0,2655 (stage 1 dua epoch), F 0,2660 (E4-native + tahap 2), K 0,2698 (+ Homostoria), D 0,2901 (E4-native + beam 5), E4 + beam 5 0,2950, H 0,3088 (tanpa stage 1) |
| Temuan utama | (1) Tahap 2 di dev resmi (konvensi referensi) −0,024 di test. (2) Stage 1 bernilai ~0,04 (H), tapi yang membantu adalah **data Jawa** (L −0,016), bukan epoch (J) atau percakapan Indonesia (K +0,004). (3) Dev resmi (4 penutur) tidak bisa menilai perubahan stage 1: salah arah di H dan K, seri di L. |

Rincian setiap submission, lengkap dengan sha ZIP dan log: [`submissions/README.md`](submissions/README.md).

## Yang sengaja tidak ada di repo publik

Official rules kompetisi melarang mempublikasikan atau meredistribusi Data kompetisi, dan larangan
itu tetap berlaku sesudah kompetisi selesai. Karena itu repo ini **tidak memuat**:
- file resmi penyelenggara (`competition/*.csv`: daftar klip test dan smoke);
- keluaran per klip di dev resmi: `predictions_official_dev.csv`, `baseline_zeroshot.json`,
  `submission_dev_*.csv`, `error_table_official_dev.csv`, CSV per klip omniASR, dan `run-log.txt`
  yang mencetak nama klip dev;
- korpus mentah (`Datasets/`), bobot model (HuggingFace private), dan ZIP submission.

Semua angka agregat (WER, jumlah error, CI) tetap ada di `dataset_findings.json`, laporan, dan
ledger. Nama lima klip smoke di `notebooks/08-packaging.ipynb` diganti dengan pembacaan dari file
resmi yang di-attach. Daftar persisnya ada di `.gitignore`.

## Peta repo

```
README.md          <- file ini: peta, status, konvensi
LICENSE-DATA.md    <- atribusi dan lisensi data turunan di findings/
CLAUDE.md          <- aturan kerja untuk agen AI (baca ini kalau kamu LLM)
docs/              studi kelayakan, kajian aturan kompetisi, log rename
plan/              rencana eksekusi + satu brief per notebook (nbNN-brief-*.md)
reports/           hasil dan analisis per notebook (nbNN-*-results.md, dst.)
notebooks/         notebook Kaggle NN-*.ipynb + skrip util
findings/          keluaran notebook, cermin /kaggle/working/findings/<run-id>/
submissions/       ledger submission platform + log mentahnya (logs/id-<n>_*.txt)
competition/       file resmi penyelenggara (format submission) - jangan diedit
Datasets/          korpus mentah + staging upload Kaggle (lokal saja, tidak ada di git; hanya README-nya)
.obsidian/         repo ini juga vault Obsidian (catatan saling tertaut lewat wikilink)
```

Penamaan: nama file ASCII kebab-case. Prefix `nbNN-` mengikat file ke notebook `NN`.
Tiap catatan menyimpan nama lamanya sebagai alias di frontmatter. Peta nama lama → baru
ada di [`docs/renames-2026-09-26.tsv`](docs/renames-2026-09-26.tsv).

## Notebook dan artefaknya

| NN | Notebook | Isi | Status | `findings/` | Catatan |
|---|---|---|---|---|---|
| 01 | `01-dataset-eda.ipynb` | EDA tiga korpus | selesai | `01-dataset-eda` | [[nb01-dataset-analysis]] |
| 02 | `02-data-build.ipynb`, `02-verify.ipynb` | segmentasi Jember → dataset Kaggle `jember-segments-16k`, scorer, split | Gate 1 lolos 25 Agu (28/28) | `02-data-build`, `02-verify` | [[nb02-data-build-results]], [[nb02-cross-audit-scorer-text-2026-08-26]] |
| — | — | analisis 372 klip dev resmi | selesai | — | [[official-dev-set-analysis-2026-08-28]] |
| 03 | `03-zeroshot.ipynb` | baseline zero-shot | selesai | `03-zeroshot`, `03-zeroshot-dryrun` | [[nb03-zeroshot-baseline-results]] |
| 04 | `04-whisper-core.ipynb` | fine-tune Jember saja: native vs concat25, 3 vs 1 epoch | Gate 2 lolos 31 Agu | `04-whisper-core*` | [[nb04-whisper-core-results]] |
| 05 | — | XLS-R CTC + LM | ditunda | — | [[nb05-brief-xlsr-ctc-lm]] |
| 06 | `06-mix-build.ipynb`, `06-mix-verify.ipynb` | build dataset campuran `jv-mix-16k` (CPU, berfase) | terverifikasi 52/52 | `06-mix-build`, `06-mix-verify` | [[nb06-data-mixing-results]] |
| 06 | `06-data-mixing.ipynb` | arm E3–E6 + **E4-native** (GPU) | Gate 4 ditutup 7 Sep (E4); E4-native 25 Sep | `06-data-mixing-*` | [[nb06-data-mixing-results]] |
| 07 | — | error analysis + aturan post-processing | belum dibangun | — | [[nb07-brief-error-analysis-robustness]] |
| 08 | `08-packaging.ipynb` | ZIP submission + gladi container + paritas dev | dipakai untuk semua submission: B, D, F, P, H, J, K, **L (terakhir, 3 Okt)** | `08-packaging`, `08-packaging-ab`, `08-packaging-e4native`, `08-packaging-devstage`, `08-packaging-devstage-pp`, `08-packaging-t0all`, `08-packaging-2ep-all`, `08-packaging-homo-all`, `08-packaging-tts-all` | [[nb08-brief-packaging-submission]], [`submissions/README.md`](submissions/README.md) |
| 09 | `09-omniasr-zeroshot.ipynb` | omniASR zero-shot di dev resmi (evaluasi gap, lead #2); venv terpisah | selesai 28 Sep: kalah dari D (v2 0,2518 vs 0,2268), lead ditutup | `09-omniasr-zeroshot*` | [[gap-eval-2-omniasr-zeroshot-2026-09-28]] |
| 10 | `10-dev-stage-finetune.ipynb` | tahap 2 di dev resmi (resep F) di atas checkpoint stage 1 mana pun | c5 −0,0267 di convo 2; `all` = F 0,2660; `t0-all` = H 0,3088; `2ep-all` = J 0,2655; `homo-all` = K 0,2698; **`tts-all` = L 0,2497** | `10-dev-stage-finetune-{c5,all,c5-lr6e6,t0-c5,t0-all,2ep-all,homo-all,tts-all}` | [[nb10-dev-stage-finetune-results]] |
| 11 | `11-large-v3-probe.ipynb` | large-v3 vs turbo zero-shot di dev (lewat `main.py` D) + probe VRAM/kecepatan training di T4 | selesai 30 Sep (17/17): large-v3 zero-shot lebih buruk dari turbo (+0,0138 CI [+0,005, +0,022]) dan full FT OOM di T4 → **ditutup**; turbo zero-shot hanya +0,018 dari D | `11-large-v3-probe-zeroshot-feasibility` | [[nb11-large-v3-probe-results]] |
| 12 | `12-stage1-2epoch.ipynb` | stage 1 E4-native dengan **2 epoch** (NB 06 apa adanya, satu variabel `NUM_EPOCHS`); dinilai hanya lewat test setelah NB 10 `all` + NB 08 | run 1 kehilangan bobot (kuota HF); r2 jalan 1 Okt (21/21) → NB 10 `2ep-all` → arm J, **test 0,2655** (F 0,2660: epoch ke-2 tidak membantu) | `12-stage1-2epoch-E4-native-2ep`, `12-stage1-2epoch-E4-native-2ep-r2` | [[nb11-large-v3-probe-results]] (alasan: H test 0,3088) |
| 13 | `13-stage1-homostoria.ipynb` | stage 1 E4-native **+ Podcast Homostoria** (4.693 segmen, 7,67 jam percakapan Indonesia; satu variabel: data); dinilai lewat NB 10 `all` + NB 08 + test | jalan 2 Okt (24/24): dev greedy 0,2096 vs E4-native 0,2317 (−0,0221) → NB 10 `homo-all` → arm K, **test 0,2698** (J 0,2655): dev salah arah, Homostoria tidak membantu | `13-stage1-homostoria-E4-native-homo` | [[nb13-stage1-homostoria-results]] |
| 14 | `14-stage1-tts.ipynb` | stage 1 E4-native **+ TTS Central Javanese** (arm E1 jv-mix-16k, 1.368 item / 8,02 jam; satu variabel: data Jawa); dinilai lewat NB 10 + NB 08 + test | jalan 3 Okt (23/23): dev seri dengan E4-native (0,2339 vs 0,2317), wer_jv 0,2425 → 0,2065 → NB 10 `tts-all` → arm L, **test 0,2497 (terbaik, peringkat 25)** | `14-stage1-tts-E4-native-tts` | [[nb14-stage1-tts-results]] |

Skrip util: `util-audit-mounts.py` (audit dataset Kaggle vs katalog MDC),
`util-pack-cv-subset.py` (paket subset Common Voice untuk upload),
`util-extract-findings.ipynb` (ambil folder findings kecil dari output Kaggle yang besar).

## Checkpoint (HuggingFace, private, akun `amozaurus`)

| Nama | Repo @ revisi | `model.safetensors` sha16 | Dev resmi (372) | Test |
|---|---|---|---|---|
| E4 | `mozilla-jv-06-data-mixing-E4@c79347a5` | `c58b0538dc4c2008` | 0,2309 greedy / 0,2260 beam5 | 0,3005 / 0,2950 |
| **E4-native** | `mozilla-jv-06-data-mixing-E4-native@3437f442` | `b3438f32cf61ebbe` | 0,2313 greedy / 0,2268 beam5 | — / **0,2901** |
| NB04 native | `mozilla-jv-04-whisper-core@9c00033f` | `3fc3a15f80cb7084` | 0,2647 | 0,3027 |
| NB04 concat25 1 ep | `mozilla-jv-04-whisper-core-full-concat25-1epoch@0a415ce6` | — | 0,2532* | — |
| F (E4-native + tahap 2) | `mozilla-jv-10-dev-stage-finetune-all@e4df20fb` | `058f6d26fd621170` | fit dev* | — / 0,2660 |
| J (2 epoch + tahap 2) | `mozilla-jv-10-dev-stage-finetune-2ep-all@b368a2ce` | `6680ef3cc3dab73e` | fit dev* | — / 0,2655 |
| **L (+ TTS + tahap 2)** | `mozilla-jv-10-dev-stage-finetune-tts-all@a19346ca` | `b607116568cfb2e7` | fit dev* | — / **0,2497** |

Angka dev memakai normalizer resmi lewat `main.py` di NB 08, kecuali * (scorer kita,
selisihnya −0,0003). E4 = Jember concat25 + Common Voice terkurasi 6,53 jam, 1 epoch.
E4-native = resep sama, segmen Jember native, checkpoint step terakhir (tanpa seleksi dev).
fit dev* = checkpoint tahap 2 dilatih di 372 klip dev itu sendiri, jadi angka dev-nya bukan hasil.

## Konvensi kerja

- **Claude menulis notebook, user menjalankannya di Kaggle.** Tidak ada training atau
  install dependensi ML di laptop. Pengecekan lokal hanya statis.
- **Output run:** Kaggle → Output → Download all → unzip ke root repo. Arsipnya sudah
  berisi `findings/<run-id>/`. Run ulang dengan resep lain wajib memakai `RUN_NOTE`
  sendiri, supaya folder lama tidak tertimpa.
- **Log platform:** simpan sebagai `submissions/logs/id-<id platform>_<arm>_<smoke|full>.txt`,
  lalu tambah satu baris di `submissions/README.md`.
- **Aturan data kompetisi:** hanya angka agregat (WER, hitungan) yang boleh dibawa ke
  asisten AI. Transkrip, nama klip, dan prediksi per klip tidak. Log `main.py` tidak
  boleh mencetak apa pun tentang data test.
- Dev resmi (4 penutur, 2 percakapan) adalah proxy yang lemah untuk test: selisih dev
  0,034 antara E4 dan NB04-native menyusut jadi 0,002 di test.

## Kalau kamu LLM yang baru masuk ke repo ini

Urutan baca: file ini → [`CLAUDE.md`](CLAUDE.md) → [`submissions/README.md`](submissions/README.md)
→ laporan notebook terakhir yang relevan di `reports/` → `findings/<run-id>/dataset_findings.json`
(digest JSON setiap run). Jangan menelusuri `Datasets/` secara rekursif: isinya puluhan ribu file audio.
