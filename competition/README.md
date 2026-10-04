# competition/

Artefak **resmi dari penyelenggara**, diunduh apa adanya dari Data download page
kompetisi. Bukan hasil analisa kita, bukan korpus latih — jangan diedit, jangan
dibangun ulang oleh notebook mana pun.

Beda dengan folder lain di repo ini:

| folder | isi |
|---|---|
| `Datasets/` | korpus latih dari katalog MDC (Jember, TTS, Common Voice) |
| `findings/` | keluaran notebook Kaggle, cerminan `/kaggle/working` |
| `competition/` | **file resmi penyelenggara** — sumber primer |

## Isi

| file | baris | keterangan |
|---|---|---|
| `submission_format.csv` | 2.118 + header | daftar persis klip test yang harus ada di `submission.csv` |
| `smoke_test_submission_format.csv` | 5 + header | daftar klip untuk smoke test (limit 1 menit) |

Keduanya berkolom `audio_filename,transcript` dengan `transcript` diisi
placeholder `hello world`. Nama file test berbentuk 32 hex + `.mp3`, seluruhnya
unik. Kelima klip smoke test **tidak** termasuk dalam 2.118 klip test.

## Kenapa ini penting untuk Notebook 08

- **Ukuran test set sekarang pasti: 2.118 klip.** Sebelumnya cuma tebakan
  (brief 08 masih mengekstrapolasi ke "500 / 1.000 / 3.000 klip").
- **Waktu inference bukan kendala.** 2.118 klip × 0,203 detik/klip
  (`whisper-large-v3-turbo`, batch 8, T4 — diukur di
  `findings/03-zeroshot/latency.json`) = **7,2 menit**. Kontainer submission
  memakai A100 80 GB dengan limit **2 jam**. Lapang sekali.
- **Yang mengikat justru smoke test.** 5 klip berarti inference-nya ~1 detik;
  seluruh limit 1 menit praktis habis untuk import dan memuat bobot. Jadi batas
  ukuran model ditentukan oleh **waktu load**, bukan waktu decode. Turbo butuh
  9,3 detik untuk load di Kaggle — aman, tapi ini alasan konkret untuk tidak
  menumpuk ensemble di dalam ZIP.
- Format CSV yang selama ini diasumsikan **terkonfirmasi persis**: dua kolom,
  satu baris per klip, header `audio_filename,transcript`.

> [!warning] Tidak dipublikasikan
> File CSV resmi di folder ini **tidak ikut di repo git publik**. Official rules melarang peserta
> mempublikasikan atau meredistribusi Data kompetisi, termasuk sesudah kompetisi selesai. Unduh
> sendiri dari halaman data kompetisi.
