"""Package a small, complete Common Voice Indonesian dataset for upload to Kaggle.

Why this exists
---------------
The Kaggle dataset `common-voice-corpus` mounts `id/clips/` holding **2,377** of the
60,804 mp3 files its own `clip_durations.tsv` names — a silently truncated upload of
60k loose files. Notebook 06's phase-1 run on 3 Sep 2026 hit it: every probed Common
Voice clip failed to decode with `No such file or directory`.

Re-uploading 60k loose files invites the same failure. Instead this script builds a
dataset holding only the clips any notebook-06 experiment can use, as **one tar** plus
the two TSVs the notebook reads. One archive cannot be half-uploaded without the upload
itself failing, and it is 0.38 GB rather than 1.7 GB.

Selection — deliberately a superset of what any experiment needs:
  * a duration in clip_durations.tsv
  * down_votes == 0            (annotation quality; nothing bypasses this)
  * one clip per sentence_id   (the corpus repeats each sentence ~2.5x)
  * NO speaker cap             (the cap is a notebook knob, applied at build time, so
                                capping here would freeze a decision that belongs there)
  * every Javanese-accented clip is kept regardless of the dedup

Stdlib + pandas only: this reads and copies files, it never decodes audio.

Run:  python notebooks/util-pack-cv-subset.py
Then: Kaggle -> Datasets -> New Dataset -> upload the whole out/ folder -> slug cv-id-subset
"""

import csv, shutil, sys, tarfile, time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
CV   = REPO / "Datasets" / "cv-corpus-26.0-2026-06-12" / "id"
OUT  = REPO / "Datasets" / "upload-cv-id-subset"
ACCENT_JV = ("javanese", "jawa", "central java", "medhok", "surakarta", "ngapak")


def main():
    if not (CV / "validated.tsv").exists():
        sys.exit("not found: %s\nExtract the corpus locally first." % (CV / "validated.tsv"))

    V = pd.read_csv(CV / "validated.tsv", sep="\t", dtype=str,
                    keep_default_na=False, quoting=csv.QUOTE_NONE)
    D = pd.read_csv(CV / "clip_durations.tsv", sep="\t", dtype=str, keep_default_na=False)
    dur = dict(zip(D[D.columns[0]], pd.to_numeric(D[D.columns[1]], errors="coerce")))
    V["dur_s"] = V["path"].map(lambda p: dur.get(p, float("nan")) / 1000.0)
    V["accent_jv"] = V["accents"].str.lower().map(
        lambda s: any(k in s for k in ACCENT_JV))
    print("validated.tsv rows        : %d" % len(V))

    n = len(V); V = V[V["dur_s"].notna()]
    print("no duration               : -%d -> %d" % (n - len(V), len(V)))

    n = len(V)
    V = V[pd.to_numeric(V["down_votes"], errors="coerce").fillna(0) < 1]
    print("down_votes >= 1           : -%d -> %d" % (n - len(V), len(V)))

    n = len(V)
    V = V.sort_values(["sentence_id", "path"], kind="mergesort")
    V = V[~V.duplicated(subset=["sentence_id"], keep="first") | V["accent_jv"]]
    print("duplicate sentence_id     : -%d -> %d" % (n - len(V), len(V)))

    V = V.sort_values("path", kind="mergesort")
    print("")
    print("selected                  : %d clips, %d speakers, %.2f h, %d accent-Javanese"
          % (len(V), V["client_id"].nunique(), V["dur_s"].sum() / 3600,
             int(V["accent_jv"].sum())))

    OUT.mkdir(parents=True, exist_ok=True)
    tar_path = OUT / "cv-id-clips.tar"
    t0, missing, total = time.time(), [], 0
    with tarfile.open(tar_path, "w") as tf:
        for i, name in enumerate(V["path"]):
            src = CV / "clips" / name
            if not src.exists():
                missing.append(name); continue
            tf.add(src, arcname=name)
            total += src.stat().st_size
            if (i + 1) % 2000 == 0:
                print("  %6d/%d  %.1f s" % (i + 1, len(V), time.time() - t0))
    print("")
    print("tar written               : %s" % tar_path)
    print("  %d clips, %.2f GB, %.0f s" % (len(V) - len(missing), tar_path.stat().st_size / 1e9,
                                           time.time() - t0))
    if missing:
        print("  !! %d clips missing from the LOCAL copy: %s" % (len(missing), missing[:5]))

    # The notebook finds Common Voice by clip_durations.tsv and reads validated.tsv; both
    # travel with the audio so the dataset is self-contained and the broken one can be
    # detached rather than left to compete with it during discovery.
    for f in ("validated.tsv", "clip_durations.tsv"):
        shutil.copy2(CV / f, OUT / f)
        print("copied                    : %s" % f)

    (OUT / "README.md").write_text(
        "# cv-id-subset\n\n"
        "Common Voice Indonesian 26.0 (CC0), reduced for the Mozilla *Lost in "
        "Transcription* id-jv track.\n\n"
        "`cv-id-clips.tar` holds %d of the corpus's 60,804 clips (%.2f h): every clip with "
        "a known duration and no down-vote, one per unique sentence, plus every "
        "Javanese-accented clip. No speaker cap is applied here — that is a knob in "
        "`notebooks/06-mix-build.ipynb`.\n\n"
        "Shipped as one archive because uploading the 60k loose clips truncated at 2,377 "
        "files.\n\n"
        "`validated.tsv` and `clip_durations.tsv` are the unmodified originals.\n"
        % (len(V) - len(missing), V["dur_s"].sum() / 3600), encoding="utf-8")

    print("")
    print("Upload the whole folder as ONE Kaggle dataset:")
    print("  %s" % OUT)
    print("  suggested slug: cv-id-subset")


if __name__ == "__main__":
    main()
