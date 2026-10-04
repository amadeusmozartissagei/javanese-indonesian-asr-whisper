# CLAUDE.md — aturan kerja untuk agen AI di repo ini

Mulai dari [`README.md`](README.md): isinya peta repo, status, checkpoint, dan konvensi.
File ini hanya berisi aturan yang **tidak boleh dilanggar**.

1. **Jangan jalankan pipeline di laptop ini.** Tugasmu menulis atau mengedit notebook di
   `notebooks/`; user yang menjalankannya di Kaggle. Jangan `pip install` paket audio/ML,
   dan jangan membuat mock `/kaggle/input`. Cek lokal yang boleh: `ast.parse` tiap sel,
   cek nama lintas sel, unit test fungsi murni terhadap metadata lokal.
2. **Aturan data kompetisi.** Transkrip, nama klip, dan prediksi per klip dari dev/test
   tidak boleh masuk ke percakapan. Skrip lokal boleh membaca CSV prediksi, tapi hanya
   boleh **mencetak agregat** (WER, jumlah error, CI). `main.py` tidak boleh me-log apa
   pun tentang data test.
3. **Satu variabel per eksperimen.** Run dengan resep berbeda memakai `RUN_NOTE` sendiri
   (folder `findings/` dan repo HF sendiri). Jangan menimpa run pembanding.
4. **Dev bukan penentu akhir.** Dev resmi terbukti proxy lemah untuk test. Seleksi
   checkpoint dan klaim "lebih baik" harus menyebut CI berpasangan, dan keputusan antar
   kandidat yang seri di dev diambil dari slot test.
5. **`notebooks/08-packaging.ipynb` → `main.py`** sudah terbukti identik 372/372 dengan
   NB 06 dan lolos di container resmi (`transformers<5`). Setiap perubahan di luar knob
   yang ada harus lolos cek paritas di notebook itu sendiri.
6. **Jangan rename** folder di `findings/` dan file di `notebooks/`: namanya terikat ke
   `NOTEBOOK_ID`/`RUN_ID` di notebook dan ke output Kaggle. Catatan markdown boleh
   di-rename asal wikilink ikut diperbarui dan nama lama masuk ke `aliases`.
7. Tulis catatan hasil ke `reports/`, brief ke `plan/`, dan log submission ke
   `submissions/logs/` + satu baris di `submissions/README.md`.
