---
title: "NB 14 brief — stage 1 E4-native + TTS Central Javanese"
tags: [brief, nb14]
status: built
updated: 2026-10-03
---

# NB 14 — stage 1 E4-native + TTS Central Javanese (arm E1 jv-mix-16k)

**Pertanyaan.** K (stage 1 + 7,7 jam percakapan Indonesia) memperbaiki dev −0,0221 tapi test
memburuk ke 0,2698 (J 0,2655, F 0,2660), dan menaikkan salah-ubah Jawa→Indonesia 111 → 143.
Apakah arah sebaliknya, menguatkan **sisi Jawa** stage 1, menambah nilai di test?

**Satu variabel vs E4-native:** tambah arm E1 `jv-mix-16k` = TTS Central Javanese, 1.368 item /
8,02 jam / 92 folder, dibersihkan dan disambung ~25 s oleh NB 06a (verifier 52/52). Belum pernah
dilatih: NB 06 membatalkannya dengan alasan dev, dan dev terbukti tidak bisa menilai stage 1.

Uji lokal (manifest + `clips.csv` lokal): 1.368 item, 0 tumpang tindih dengan E4, 0 angka, 0 teks
kosong, maks 25,3 s, 0 ketidakcocokan teks/jumlah klip di **semua** item. Total 8.093 item →
**506 step** (E4-native 421). Proyeksi ~2,5–3 jam T4.

**Risiko:** ucapan dibacakan (gaya TTS), penutur per folder tidak diketahui, Jawa Tengah bukan
Jawa Timur/Pandhalungan.

**Jalur keputusan:** NB 14 → NB 10 `tts-all` → NB 08 arm L → slot test vs J 0,2655 / F 0,2660.
