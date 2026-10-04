# Datasets/

Salinan lokal korpus mentah, ditambah folder staging untuk upload ke Kaggle. Total beberapa GB
dan puluhan ribu file audio. **Jangan scan rekursif** (`du`, `find`, glob `**`): folder
`clips/` Common Voice saja sudah ~60 ribu file. Baca metadata TSV-nya langsung.

Nama folder dan arsip di sini sengaja dibiarkan sama dengan nama unduhan aslinya dari
katalog MDC, supaya bisa dicocokkan dengan sumbernya.

| Path | Isi | Kaggle |
|---|---|---|
| `Jember Javanese Spontaneous Speech Corpus/` | TSV transkrip + `mp3 audio/` (korpus utama, CC-BY-NC-SA-4.0) | `jember-javanese-corpus`; turunannya `jember-segments-16k` (NB 02) |
| `RECORDING TTS/`, `RECORDING TTS.zip` | TTS Jawa Tengah, `recordings (N).zip` (CC-BY-SA-4.0) | `central-javanese-corpus` |
| `cv-corpus-26.0-2026-06-12/` | Common Voice Indonesia 26.0 (CC0) | `common-voice-corpus` (unggahan ini terpotong, lihat util-audit-mounts) |
| `homostoria/` | Podcast Homostoria (MDC `cmiepnyu1001jo207hzslvb5m`, CC-BY-SA-4.0): 16 mp3 episode (64 kbps, ~11,3 jam) + `transcript_homostoria.tsv` (`Audio file`, `Start`, `End`, `Text`; timestamp resolusi 1 detik). Diunduh 2 Okt 2026 | belum diunggah |
| `indonesian_dev/` | **dev resmi**: `metadata.tsv` + `clips/` (372 klip) | `indonesian_dev` |
| `*.tar.gz` | arsip asli unduhan di atas | — |
| `upload-cv-id-subset/` | subset CV yang dipaket `notebooks/util-pack-cv-subset.py` | staging upload |
| `upload-nb04-baseline/` | prediksi dan pembanding NB 04 untuk NB 06 (ada README sendiri) | `nb04-baseline` |

Dataset turunan yang hanya ada di Kaggle: `jember-segments-16k` (NB 02) dan `jv-mix-16k` (NB 06a).
