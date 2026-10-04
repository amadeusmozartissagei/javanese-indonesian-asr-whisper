# =============================================================================
# MOUNT AUDIT - do the attached Kaggle corpora match their MDC catalog entries?
#
# Written 3 Sep 2026, after `common-voice-corpus` was found holding 2,377 of the
# 60,804 mp3 files its own metadata names: a silently truncated upload of 60k
# loose files that every earlier notebook missed, because until notebook 06
# nothing opened an audio file - the TSVs were complete and every measurement
# was made from them.
#
# Run in a fresh Kaggle notebook with `jember-javanese-corpus` and
# `central-javanese-corpus` attached. Accelerator: None. ~1 minute.
# =============================================================================
import os, sys, collections, hashlib, random, subprocess, shutil
from pathlib import Path

INPUT   = Path("/kaggle/input")
FFPROBE = shutil.which("ffprobe")
FFMPEG  = shutil.which("ffmpeg")
N_PROBE = 8
random.seed(20260903)

# What the source of truth says. Catalog sizes are of the DOWNLOAD archive, and mp3/
# webm barely compress, so the extracted tree should land within ~15 % of them.
EXPECT = {
    "jember": dict(
        catalog="Jember Javanese Spontaneous Speech Corpus (CC-BY-NC-SA-4.0)",
        mb=271.65, hours=10.0, n_audio=208, n_rows=6679, ext=".mp3"),
    "tts": dict(
        catalog="TTS Central Javanese (CC-BY-SA-4.0)",
        mb=440.11, hours=7.75, n_audio=4599, n_rows=4630, ext=".webm"),
}

def probe_s(p):
    if not FFPROBE: return float("nan")
    try:
        r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=nokey=1:noprint_wrappers=1", str(p)],
                           capture_output=True, text=True, timeout=30)
        return float(r.stdout.strip())
    except Exception:
        return float("nan")

def decodes(p):
    if not FFMPEG: return False
    r = subprocess.run([FFMPEG, "-v", "error", "-nostdin", "-i", str(p), "-t", "1",
                        "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                       capture_output=True)
    return r.returncode == 0 and len(r.stdout) > 0

RESULT = []
def check(corpus, name, ok, detail=""):
    RESULT.append((corpus, name, ok))
    print("  %-4s %-38s %s" % ("PASS" if ok else "FAIL", name, detail))

# ---------------------------------------------------------------- discovery --
cv_dirs = {p.parent for p in INPUT.glob("**/clip_durations.tsv")}
jem_tsv, tts_maps = [], sorted(INPUT.glob("**/mapping.tsv"))
for q in INPUT.glob("**/*.tsv"):
    if q.parent in cv_dirs or q.name == "mapping.tsv":
        continue
    try:
        h = q.open(encoding="utf-8", errors="replace").readline().lower()
    except Exception:
        continue
    if "start" in h and "end" in h and "text" in h:
        jem_tsv.append(q)
JEM_TSV = max(jem_tsv, key=lambda q: q.stat().st_size) if jem_tsv else None
TTS_ROOT = Path(os.path.commonpath([str(p.parent) for p in tts_maps])) if tts_maps else None

# ------------------------------------------------------------------ jember --
print("=" * 74); print("JEMBER  --  %s" % EXPECT["jember"]["catalog"]); print("=" * 74)
if JEM_TSV is None:
    print("  NOT FOUND - attach jember-javanese-corpus")
else:
    E = EXPECT["jember"]
    root = JEM_TSV.parent
    audio = sorted(root.rglob("*" + E["ext"]))
    mb = sum(p.stat().st_size for p in audio) / 1e6
    rows = [l.rstrip("\n").split("\t") for l in
            JEM_TSV.open(encoding="utf-8", errors="replace").read().splitlines()]
    hdr, body = rows[0], rows[1:]
    col = {c.strip().lower(): i for i, c in enumerate(hdr)}
    fcol = next((col[k] for k in ("audio file", "audio_file", "audio filename",
                                  "audio_filename", "file") if k in col), 0)
    names = {p.stem for p in audio}
    want = {r[fcol].strip().rsplit(".", 1)[0] for r in body if len(r) > fcol and r[fcol].strip()}
    print("  root: %s" % root)
    check("jember", "audio files present", len(audio) == E["n_audio"],
          "%d found, %d expected" % (len(audio), E["n_audio"]))
    check("jember", "total size matches the catalog", abs(mb - E["mb"]) / E["mb"] < 0.15,
          "%.1f MB on mount, %.1f MB in catalog" % (mb, E["mb"]))
    check("jember", "transcript rows", len(body) == E["n_rows"],
          "%d rows, %d expected" % (len(body), E["n_rows"]))
    check("jember", "every transcript has its audio", not (want - names),
          "%d referenced files absent" % len(want - names))
    smp = random.sample(audio, min(N_PROBE, len(audio)))
    ok = [decodes(p) for p in smp]
    durs = [probe_s(p) for p in audio]
    h = sum(d for d in durs if d == d) / 3600.0
    check("jember", "sampled files really decode", all(ok),
          "%d/%d decoded" % (sum(ok), len(ok)))
    check("jember", "duration matches the catalog", abs(h - E["hours"]) / E["hours"] < 0.15,
          "%.2f h measured, ~%.1f h in catalog" % (h, E["hours"]))

# --------------------------------------------------------------------- tts --
print(""); print("=" * 74); print("TTS  --  %s" % EXPECT["tts"]["catalog"]); print("=" * 74)
if not tts_maps:
    print("  NOT FOUND - attach central-javanese-corpus")
else:
    E = EXPECT["tts"]
    audio = sorted(TTS_ROOT.rglob("*" + E["ext"]))
    mb = sum(p.stat().st_size for p in audio) / 1e6
    body, missing = [], []
    for m in tts_maps:
        lines = m.open(encoding="utf-8", errors="replace").read().splitlines()
        for l in lines[1:]:
            parts = l.split("\t")
            if len(parts) < 2 or not parts[0].strip():
                continue
            body.append(parts[0].strip())
            if not (m.parent / parts[0].strip()).exists():
                missing.append(parts[0].strip())
    print("  root: %s" % TTS_ROOT)
    check("tts", "mapping.tsv files", len(tts_maps) >= 92, "%d found" % len(tts_maps))
    check("tts", "audio files present", len(audio) == E["n_audio"],
          "%d found, %d expected" % (len(audio), E["n_audio"]))
    check("tts", "total size matches the catalog", abs(mb - E["mb"]) / E["mb"] < 0.15,
          "%.1f MB on mount, %.1f MB in catalog" % (mb, E["mb"]))
    check("tts", "transcript rows", len(body) == E["n_rows"],
          "%d rows, %d expected" % (len(body), E["n_rows"]))
    # 30 absent files and ~50 duplicate hash names are KNOWN defects of this corpus,
    # measured in notebook 01 and removed by notebook 06. They are reported, not failed.
    dup = len(body) - len(set(body))
    print("  NOTE known defects: %d transcripts without audio (nb01 saw 30), "
          "%d duplicate filenames (nb01 saw ~50)" % (len(missing), dup))
    smp = random.sample(audio, min(N_PROBE, len(audio)))
    ok = [decodes(p) for p in smp]
    check("tts", "sampled files really decode", all(ok),
          "%d/%d decoded" % (sum(ok), len(ok)))
    smp2 = random.sample(audio, min(200, len(audio)))
    mean_s = sum(probe_s(p) for p in smp2) / len(smp2)
    h = mean_s * len(audio) / 3600.0
    check("tts", "duration matches the catalog", abs(h - E["hours"]) / E["hours"] < 0.15,
          "~%.2f h from a %d-file sample, %.2f h in catalog" % (h, len(smp2), E["hours"]))
    print("  NOTE the catalog page says '457 clips'; the tree holds %d. The 7h45m "
          "duration matches, so 457 is not a clip count." % len(audio))

# ----------------------------------------------------------------- verdict --
print(""); print("=" * 74)
for c in ("jember", "tts"):
    r = [x for x in RESULT if x[0] == c]
    if not r:
        print("%-8s NOT AUDITED" % c.upper()); continue
    bad = [x[1] for x in r if not x[2]]
    print("%-8s %s" % (c.upper(), "OK - %d/%d checks" % (len(r), len(r)) if not bad
                       else "MISMATCH: " + "; ".join(bad)))
print("=" * 74)
