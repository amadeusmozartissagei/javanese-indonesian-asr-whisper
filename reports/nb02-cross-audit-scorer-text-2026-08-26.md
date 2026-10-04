---
title: "Audit Silang — Scorer & Asumsi Teks (26 Agustus 2026)"
aliases:
  - Audit Silang - Scorer dan Asumsi Teks (26 Agustus 2026)
  - Audit Silang Scorer
  - Cross-audit 2026-08-26
tags:
  - research
  - competition
  - eval
  - audit
status: final
created: 2026-08-26
updated: 2026-08-28
audits: findings/02-data-build/scorer.py
source_type: measured-from-data
---

# Audit Silang — Scorer & Asumsi Teks

> [!summary] Ringkasan
> Lima titik yang ditandai untuk diperiksa ulang sudah diuji langsung terhadap `scorer.py`, `manifest.csv`, dan halaman Problem description yang dibaca ulang hari ini. **Tiga lolos, dua tidak.** Implementasi normalizer setia pada daftar resmi dan self-test lolos 30/30, tapi (a) klaim "44,5% → 19,15% karena normalizer diperbaiki" **terbukti salah sebabnya** — angka lamanya berasal dari pemanggilan `wer(..., normalize=False)`, bukan dari normalizer yang lama, dan (b) argumen "strategi dominan" untuk diakritik **berdiri di atas premis yang belum diuji**, yaitu bahwa transkrip resmi memakai konvensi ejaan yang sama dengan Jember.
>
> **Ibaratnya:** timbangan dapurnya sendiri sudah benar — sudah dicek ulang terhadap manual pabriknya. Yang keliru adalah catatan di dinding tentang *kenapa* angkanya berubah kemarin, dan satu asumsi diam-diam bahwa resep yang mau dinilai juri ditulis pakai satuan yang sama dengan resep latihan kita. Yang kedua ini cuma bisa dijawab dengan membuka buku resep juri, dan buku itu sudah tersedia tapi belum pernah dibuka.

> [!info] Cara pengujian
> `scorer.py` dijalankan lokal (Python 3.11, stdlib saja — tidak ada yang di-install, tidak ada GPU). Setiap angka di bawah dihitung ulang dari `findings/02-data-build/manifest.csv` (6.638 baris, 65.612 token referensi). Halaman [Problem description](https://competitions.mozilladatacollective.com/competitions/1/lost-in-transcription/page/2/) dibaca ulang 26 Agustus 2026 sebagai sumber primer, bukan lewat catatan turunan.

## Papan hasil

| # | Yang diperiksa | Vonis |
|---|---|---|
| 1 | Kesetiaan `_lowercase_sentence_initial()` & `_strip_periods_keep_attached_ellipsis()` pada 6 langkah resmi | **Lolos** — urutan dan isi cocok |
| 2 | Keputusan melompati `PUNCT_REMOVED` saat mencari huruf awal kalimat | **Lolos bersyarat** — hasilnya wajar, alasannya keliru, ada celah kecil |
| 3 | Penjelasan penurunan 44,5% → 19,15% | **GAGAL** — sebabnya bukan normalizer |
| 4 | Status diakritik & argumen strategi dominan | **GAGAL** — dan **terkonfirmasi 28 Agu**: target pindah ke `text_folded` |
| 5 | Dev set resmi 372 klip belum dipakai | **Terkonfirmasi** — sudah diunduh 28 Agu, dan memang jadi kunci #4 |

## 1 — Implementasi setia pada daftar resmi

Halaman resmi dibaca ulang hari ini dan memuat enam langkah, urutannya persis seperti yang dicatat di [[rules-review-2026-08-23|Kaji Ulang Peraturan - 23 Agustus 2026]]. Satu kalimat penegas yang belum pernah dikutip di catatan kita:

> normalization does **not** lowercase text in general … casing is compared as written

`official_normalize()` menjalankan keenamnya dalam urutan yang sama: tag kurung siku → penanda tak terdengar → lowercase awal kalimat → hapus `,?¿¡!";:` → hapus titik kecuali elipsis menempel → collapse spasi. Urutan langkah 4 sebelum 5 penting dan **kebetulan sudah benar**: `iku ..., ngono` hanya menjadi elipsis berdiri-sendiri *setelah* komanya hilang, jadi kalau urutannya dibalik elipsis itu justru akan lolos dan dipertahankan.

Hasil uji:

```
self-test lokal                                  30/30 lolos
text_official == official_normalize(text_raw)    6.638/6.638 cocok
idempoten pada text_official yang dikirim        0 gagal
```

Pengecualian akronim (`nxt.isupper()`), em-dash (`—`), dan `…` (U+2026, hanya 4 kemunculan dan semuanya menempel di kata) semuanya berperilaku sama di bawah bacaan resmi maupun implementasi kita. Tidak ada yang perlu diubah di sini.

## 2 — Melompati `PUNCT_REMOVED`: hasilnya wajar, alasannya salah

Alasan yang dipakai untuk perbaikan kedua adalah **idempotency**. Alasan itu tidak sah: penyelenggara menjalankan normalizer **sekali**, jadi normalizer yang tidak idempoten tidak otomatis salah. Non-idempotency adalah gejala, bukan bukti.

Tiga bacaan yang sama-sama masuk akal atas kalimat *"the first letter following a `.`, `!`, `?`, or `—`"*, diuji ke seluruh korpus:

| Varian | Yang dilompati saat mencari huruf | Beda dari yang dikirim | Idempoten |
|---|---|---|---|
| **A — yang dikirim** | spasi + `,?¿¡!";:` | — | ya |
| B — naif | spasi saja | 30 baris / 31 token | **tidak** (21 baris) |
| C — literal | apa pun yang bukan huruf | 8 baris / 11 token | ya |

Contoh yang membedakan A dari B: `E..., Sabtu ngajar privat.` → A menghasilkan `e... sabtu`, B menghasilkan `e... Sabtu`. Kalau penyelenggara memakai regex naif semacam `[.!?—]\s*([A-Z])` — implementasi yang paling mungkin ditulis orang — maka **B yang benar dan A yang salah**, dan perbaikan kemarin justru menjauhkan kita dari mereka.

Celah nyata di A: tanda kutip melengkung `“ ”` **tidak ada** di `PUNCT_REMOVED`, jadi ia menghentikan pencarian.

```
karakter yang menghentikan pencarian A tapi bukan huruf:
  ”  23x      “  2x      (57 kutip melengkung bertahan di text_official)
```

Akibatnya `“Nggak tau, makanan…` mempertahankan `N` kapital sementara `Nggak` di posisi setara tanpa kutip akan di-lowercase — tidak konsisten dengan dirinya sendiri.

> [!check] Rekomendasi: catat, jangan rerun
> Seluruh sengketa ini bernilai **31 token dari 65.612 = 0,047% WER absolut**. Mererun tiga fase Notebook 02 untuk memindahkan 11–31 token adalah pertukaran yang buruk. Varian C lebih setia pada teks aturan *dan* idempoten *dan* menutup celah kutip melengkung tanpa daftar tambal — **kalau ada alasan lain untuk rerun, ganti skipper-nya ke C sekalian**; kalau tidak ada, biarkan.

## 3 — Angka 44,5% itu bukan efek normalizer

Klaim di [[nb02-data-build-results|Hasil Notebook 02 - Data Build]] berbunyi: angka turun karena normalizer resmi kini sudah mengerjakan sebagian "pembersihan" itu sendiri. **Klaim ini tidak lolos rekonstruksi.**

Normalizer lama (tanpa lowercasing, tanpa strip titik) dibangun ulang dan resep demo yang sama dijalankan di atasnya:

```
target BARU, lower + hapus titik + lipat diakritik   0,1915   <- angka sekarang
target LAMA, resep yang sama                         0,1956   <- seharusnya 0,445 kalau klaimnya benar
```

Selisih yang benar-benar disebabkan perbaikan normalizer adalah **0,4 poin persen**, bukan 25. Angka 44,5% direproduksi persis dengan cara lain:

```
wer(text_raw, hyp, normalize=False)   0,4450
```

Jadi 44,5% adalah hasil membandingkan hipotesis terhadap referensi **yang belum dinormalisasi sama sekali** — setiap koma, tag `[laugh]`, dan tanda tanya di referensi ikut dihitung sebagai kesalahan, padahal scorer menghapusnya. Itu bukan pengukuran yang berarti, dan perbaikannya adalah perbaikan pemanggilan, bukan perbaikan normalizer.

Dekomposisi 19,15% yang sekarang (head 400, sama seperti demo notebook):

| Yang dilakukan hipotesis | WER |
|---|---|
| hapus titik saja | 1,23 % |
| lowercase penuh saja | 4,46 % |
| **lipat diakritik saja** | **13,58 %** |
| lowercase + lipat | 18,04 % |
| ketiganya | 19,15 % |

Substitusinya: 468 total — 329 diakritik, 109 case, 27 punct, 3 campuran, **0 kesalahan sungguhan**. Kesimpulan strategisnya tetap berdiri (latih pada keluaran `official_normalize()`), tapi **beban buktinya berpindah**: yang mahal bukan lowercasing, melainkan diakritik — sendirian ia menanggung 71% dari substitusi.

## 4 — Diakritik: matriksnya kehilangan satu kolom

Halaman resmi dikonfirmasi **tidak menyebut diakritik sama sekali**, jadi premis "pertanyaannya terbuka" benar. Yang tidak benar adalah bahwa pertanyaan itu tidak perlu dijawab.

Matriks strategi dominan di [[nb02-data-build-results|Hasil Notebook 02 - Data Build]] punya dua kolom: penyelenggara melipat, atau tidak melipat. Keduanya diam-diam mengandaikan bahwa **referensi resmi ditulis dengan diakritik**, seperti Jember. Tapi test dan dev resmi berasal dari korpus yang berbeda — voice note dyadic, tim anotasi yang berbeda, konvensi ejaan yang berbeda. Kolom ketiga yang hilang:

| kita latih dengan | tidak melipat, ref **berdiakritik** | melipat | tidak melipat, ref **tanpa diakritik** |
|---|---|---|---|
| `text_official` | rugi 0,86 % | rugi 0 % | **rugi hingga 14,3 %** |
| `text_folded` | rugi hingga 14,3 % | rugi 0 % | rugi 0 % |

Beban diakritik di Jember, diukur ulang:

```
token berdiakritik   9.385 / 65.612  = 14,30 %
ê 5.372   è 4.825   ě 819   ḍ 17   é 1
teratas: lèk 811, ndèk 780, těrus 756, nèk 484, nèng 452
```

Kalau transkrip resmi menulis `lek`, `ndek`, `terus` polos dan penyelenggara tidak melipat, maka melatih pada `text_official` **menyuntikkan** diakritik yang tidak ada di referensi — dan 14,3% token menjadi substitusi. Strategi dominan berubah menjadi kalah telak. Ini bukan spekulasi jauh: diakritik `ê/è/ě` adalah pilihan ortografi penganotasi Jember, bukan standar Bahasa Jawa Latin sehari-hari.

## 5 — Dev set resmi belum ada, dan itu yang mengunci #4

Terkonfirmasi: `Datasets/` hanya berisi Jember, RECORDING TTS, dan Common Voice. Tidak ada `indonesian_dev/`, tidak ada `metadata.tsv`.

> [!danger] Ini satu unduhan yang menutup pertanyaan terbesar
> Kolom ketiga di matriks #4 tidak perlu diperdebatkan — ia bisa **dibaca langsung** dari `indonesian_dev/metadata.tsv`. Satu perintah grep atas 372 baris transkrip menjawab apakah referensi resmi memakai diakritik atau tidak, dan jawaban itu menentukan target latihan seluruh Notebook 04 sampai 07. Selama file itu belum diunduh, keputusan "latih dengan `text_official`" berstatus **taruhan**, bukan strategi dominan.

Dev set 372 klip juga satu-satunya sampel in-distribution yang kita punya untuk gaya bicara test (voice note dyadic vs sesi wawancara Jember). Setiap angka WER yang dilaporkan Notebook 03+ dari dev split Jember adalah proxy yang belum pernah dikalibrasi terhadap distribusi sebenarnya.

## 6 — Apakah Notebook 02 perlu di-rerun? Tidak

Diperiksa terpisah setelah pertanyaan itu diajukan. **Tidak ada temuan di atas yang membatalkan artefak yang sudah terbit.**

```
6 file ber-fingerprint: lokal == terbit, 6/6 identik
verify fase 3          : 28/28 lolos
scorer dari mount      : 30/30
text_folded == fold(text_official) : 6.638/6.638 cocok
```

Alasan per temuan:

| Temuan | Menyentuh artefak? | Perlu rerun? |
|---|---|---|
| #1 setia pada aturan | tidak | tidak |
| #2 skipper varian A/B/C | ya, `text_official` (11–31 token) | **tidak** — 0,047% WER, tidak sepadan |
| #3 angka 44,5% | tidak — nilai tersimpan sudah `0.1915` yang benar | tidak |
| #4 diakritik | tidak — `text_folded` **sudah ada** di manifest dan terverifikasi | tidak; ganti target = satu baris di NB 04 |
| #5 dev set resmi | tidak — itu dataset baru terpisah | tidak |

> [!warning] Satu cacat tersisa, tapi metadata — bukan perilaku
> `dataset_findings.json` yang terbit masih memuat flag lama `scorer.does_not_lowercase = True` dan `does_not_strip_periods = True`. `notebooks/02-data-build.ipynb` **sudah** diperbaiki menjadi `lowercases_sentence_initial` / `strips_periods_except_attached_ellipsis`, tapi run terakhir yang diunduh belum memakainya. `scorer.py` sendiri benar dan fingerprint-nya cocok, dan tidak ada notebook 03+ yang membaca boolean itu secara program — mereka cuma menulis digest sendiri. **Risikonya manusia, bukan mesin:** sesi berikutnya membaca flag itu dan menyimpulkan ulang asumsi yang persis memulai seluruh kekacauan ini.
>
> Mitigasi tanpa rerun: cell 1 Notebook 03 memverifikasi **perilaku** (`scorer.self_test()`), bukan flag. Itu sudah ada di brief. Cukup.

> [!note] Kalau suatu saat ada rerun karena alasan lain, bawa sekalian
> 1. Flag `rec("scorer", ...)` — sudah diperbaiki di source, tinggal ikut terbit.
> 2. Skipper `_next_letter_pos()` → varian C (§2).
>
> Keduanya **tidak** mengubah file ber-fingerprint kecuali `manifest.csv`/`text_audit.json` (dari #2). Rerun sekarang hanya untuk dua boolean adalah pertukaran yang buruk.

> [!check] Tertutup 28 Agustus — tebakan #4 terbukti, dan mahal kalau terlewat
> Dev set resmi diunduh dan diperiksa: **0,30% token berdiakritik, hanya `é`**, nol `ê`/`è`/`ě`. Dari 9.385 token berdiakritik Jember, **0,0% cocok apa adanya, 69,4% cocok setelah dilipat**. Kolom ketiga yang "hilang" di matriks itulah yang benar. Target latihan pindah ke `text_folded`, A1 dan A2 selesai, A5 dijalankan mulai NB 04. Tidak ada rerun. Lihat [[official-dev-set-analysis-2026-08-28|Analisa Dev Set Resmi - 28 Agustus 2026]].

## Tindakan

| # | Tindakan | Biaya | Kapan |
|---|---|---|---|
| A1 | ~~Unduh `indonesian_dev/`, grep diakritik~~ | — | **selesai 28 Agu** |
| A2 | ~~Tulis ulang matriks diakritik di [[nb02-data-build-results\|Hasil Notebook 02 - Data Build]]~~ | — | **selesai 28 Agu** |
| A3 | Koreksi kotak "44,5%" — sudah dikerjakan 26 Agustus | — | selesai |
| A4 | Ganti skipper `_next_letter_pos()` ke varian C **hanya jika** ada rerun karena alasan lain | 0 | oportunistik |
| A5 | Jadikan dev set resmi lapisan validasi utama; dev split Jember turun jadi proxy | — | Notebook 03 |
