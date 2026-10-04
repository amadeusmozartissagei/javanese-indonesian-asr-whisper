# findings/

Hasil run notebook Kaggle. Struktur di sini **identik** dengan struktur yang
ditulis notebook di `/kaggle/working`, jadi tidak ada penyortiran manual.

```
findings/
  01-dataset-eda/                 <- dari notebooks/01-dataset-eda.ipynb
    dataset_findings.json         digest terstruktur (dibaca Claude)
    run-log.txt                   seluruh output console, otomatis ter-tee
    _kaggle-artifacts/            file bikinan Kaggle, bukan hasil analisa
  02-<nama-notebook>/
    ...
```

## Cara simpan hasil run

1. Kaggle → tab **Output** → **Download all**.
2. Unzip isinya ke **root repo** (`mozilla-javanese-research/`).
3. Selesai. Arsipnya sudah berisi `findings/<notebook-id>/`, jadi filenya
   langsung masuk ke folder yang benar dan merge dengan yang sudah ada.

Tidak perlu bikin folder, rename, atau mindahin file satu-satu.

## Cara bikin notebook baru

Copy blok **OUTPUT CONVENTION** dari cell 1 `notebooks/01-dataset-eda.ipynb`,
ganti satu baris:

```python
NOTEBOOK_ID = "02-nama-notebook-baru"   # harus sama dengan nama file .ipynb
```

Semua penulisan file lewat helper `out("namafile.ext")` — tidak ada yang boleh
ditulis langsung ke `/kaggle/working`, supaya arsip download-nya tetap bersih.

## Catatan

- **Re-run cell 1 me-reset `run-log.txt`.** Kalau cuma re-run sebagian cell,
  log hanya berisi cell yang dijalankan setelahnya. `dataset_findings.json`
  tetap sumber kebenarannya.
- Kaggle kadang menulis file di root `/kaggle/working` **setelah** notebook
  selesai (mis. `__huggingface_repos__.json`). Notebook menyapu yang sempat
  terlihat ke `_kaggle-artifacts/`; sisanya pindahkan manual.
- Kalau notebook yang sama di-run ulang dengan hasil berbeda dan versi lama
  masih perlu, beri akhiran versi: `dataset_findings-v2.json`. Untuk notebook
  GPU yang lebih baru, pakai knob `RUN_NOTE` saja: dia membuat folder sendiri.
- **Jangan rename folder di sini.** Nama folder = `RUN_ID` yang ditulis notebook,
  jadi unzip berikutnya akan membuat folder lama muncul lagi di samping yang baru.

## Indeks run (per 26 Sep 2026)

Angka WER dev resmi di tabel ini memakai scorer kita (`scorer.py`), kecuali baris `08-*`
yang memakai normalizer resmi lewat `main.py`. Selisih keduanya konstan, −0,0003.

| Folder | Notebook | Apa | Angka kunci |
|---|---|---|---|
| `01-dataset-eda` | 01 | EDA tiga korpus | — |
| `02-data-build` | 02 fase 1–2 | build `jember-segments-16k` + scorer + split | Gate 1 |
| `02-verify` | 02 fase 3 | verifikasi dataset yang dipublikasi | 28/28 |
| `03-zeroshot`, `03-zeroshot-dryrun` | 03 | zero-shot turbo di Jember dev | 0,8960 (tanpa guard) |
| `04-whisper-core-sanity` | 04 | smoke: overfit, resume, speed | lolos |
| `04-whisper-core` | 04 | Jember native, 3 epoch | dev resmi 0,2650 |
| `04-whisper-core-full-concat25` | 04 | Jember concat25, 3 epoch | 0,2524, Gate 2 |
| `04-whisper-core-full-concat25-1epoch` | 04 | concat25, 1 epoch = **pembanding NB 06** | 0,2532 |
| `06-mix-build`, `06-mix-verify` | 06a | build + verifikasi `jv-mix-16k` | 52/52 |
| `06-data-mixing-E3` | 06b | + CV beraksen Jawa 0,54 jam | 0,2408 |
| `06-data-mixing-E4` | 06b | + CV terkurasi 6,53 jam = **kandidat E4** | 0,2312 (clean-222: 0,2336) |
| `06-data-mixing-E6` | 06b | E4 + Jember diulang ×2 | 0,2336 |
| `06-data-mixing-E5-A`, `-E5-B` | 06b | curriculum. **Tidak valid**: tahap B tidak menerima bobot A | 0,2591 / 0,2586 |
| `06-data-mixing-smoke-E4-native` | 06b | smoke E4-native | 20/21 (FAIL yang diharapkan) |
| `06-data-mixing-E4-native` | 06b | E4 dengan segmen Jember native, step terakhir | 0,2317 (clean-222: 0,2295) |
| `08-packaging` | 08 | ZIP E4 greedy (submission 1) | 19/19, 0,2309 |
| `08-packaging-ab` | 08 | arm A (NB04 native), B (E4 beam5), kontrol C | 48/48 |
| `08-packaging-e4native` | 08 | arm D (E4-native beam5), kontrol N dan C | 43/43, D 0,2268 |

Hasil test dari ZIP-ZIP ini: [`../submissions/README.md`](../submissions/README.md).
