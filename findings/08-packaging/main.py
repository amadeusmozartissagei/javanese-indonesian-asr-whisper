# main.py - Lost in Transcription, Indonesian-Javanese track.
#
# Runs inside the organiser's container. Working directory is /code_execution:
#   data/clips/*.mp3        read-only test audio
#   data/test_metadata.csv  audio_filename, file_duration_seconds, language
#   src/                    this file, postprocess.py and ./model
#   submission/             where submission.csv must be written
#
# Constraints this file is written against, all taken from the competition's
# own pages rather than assumed:
#   - no network of any kind, so weights ship in ./model and offline flags are
#     set BEFORE transformers is imported (it reads them at import time)
#   - 2 h for the full set, 1 min for the 5-clip smoke test: the smoke budget is
#     import + weight load, not decode, so nothing heavy happens at module scope
#   - logs are capped at 500 lines x 300 chars AND logging anything about the
#     test data is grounds for disqualification, so only aggregate counts and
#     timings are printed - never a filename, a duration, or a transcript
#   - each clip is processed independently (competition rule 4): no state, no
#     sorting by content, no cross-clip normalisation
#
# The decode path is notebook 06's evaluation code (its cells 1 and 7), constant
# for constant: the dev WER this model was chosen on only carries over to the
# test set if the submission decodes exactly the same way.
import os

# Must precede the transformers/HF imports below.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
# Library warnings go to stderr, which counts against the same 500-line cap.
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

import collections
import csv
import json
import math
import sys
import time
import traceback
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

_T_IMPORT_START = time.time()
import numpy as np
import torch
from transformers import (GenerationConfig, WhisperFeatureExtractor,
                          WhisperForConditionalGeneration, WhisperTokenizerFast)

try:
    import librosa
except Exception:
    librosa = None
_T_IMPORT = time.time() - _T_IMPORT_START

HERE = Path(__file__).resolve().parent
WORK = Path.cwd()
DATA = WORK / "data"
CLIPS = DATA / "clips"
OUT_DIR = WORK / "submission"
MODEL_DIR = HERE / "model"

# Notebook 06, cell 1 (knobs) and cell 7 (decode helpers).
SR = 16000
LANG = "jw"                 # Whisper's Javanese code is "jw", not ISO "jv"
GEN_MAX_LENGTH = 225
NO_REPEAT_NGRAM = 4
BATCH = 8                   # EVAL_BATCH
LONG_S = 29.8               # clips longer than this take the chunked path
CHUNK_S = 28.0              # LONG_CHUNK_S
OVERLAP_S = 2.0             # LONG_OVERLAP_S
MIN_WINDOW_S = 0.3          # a trailing window this short is dropped
MAX_OVERLAP_WORDS = 8       # seam de-duplication, longest match first

GEN_KWARGS = dict(task="transcribe", language=LANG, num_beams=1, do_sample=False,
                  no_repeat_ngram_size=NO_REPEAT_NGRAM, max_length=GEN_MAX_LENGTH,
                  return_timestamps=False)

# A few unreadable clips cost a few points. A run where many clips fail means
# something systemic broke - a library mismatch, a missing file - and would
# hand the platform a scored file of blanks that burns a submission. Past this
# rate no submission.csv is written and the run exits non-zero; failed runs do
# not count against the submission limit.
MAX_FAIL_RATE = 0.02
MAX_FAIL_FLOOR = 2
FAIL_FAST_AFTER = 16

# Set only by our own test notebook. Never set on the platform, where a
# traceback could say something about a test file.
DEBUG = os.environ.get("LIT_DEBUG") == "1"


def log(msg):
    # Aggregate facts only. Never clip identities or transcript content.
    print(msg, flush=True)


def load_audio(path):
    # Notebook 06's load_official_audio: librosa first, soundfile + polyphase
    # resampling as the fallback. The same loader and the same resampler mean
    # the model sees the samples it was measured on.
    if librosa is not None:
        try:
            y, _ = librosa.load(str(path), sr=SR, mono=True)
            return y.astype(np.float32)
        except Exception:
            pass
    import soundfile as sf
    y, sr0 = sf.read(str(path), dtype="float32")
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr0 != SR:
        from scipy.signal import resample_poly
        g = math.gcd(int(sr0), SR)
        y = resample_poly(y, SR // g, int(sr0) // g)
    return y.astype(np.float32)


def split_windows(y):
    # Fixed windows with an overlap, so a word straddling a boundary is seen
    # whole by at least one window. Whisper's encoder window is 30 s and
    # anything past it would be silently cut.
    step = int((CHUNK_S - OVERLAP_S) * SR)
    win = int(CHUNK_S * SR)
    parts = [y[i:i + win] for i in range(0, len(y), step)]
    return [p for p in parts if len(p) > int(MIN_WINDOW_S * SR)]


def join_overlapping(texts):
    # Consecutive windows usually repeat a few words at the seam. Drop the
    # longest repeated run, longest match first.
    joined = ""
    for t in texts:
        t = (t or "").strip()
        if not t:
            continue
        if not joined:
            joined = t
            continue
        a, b = joined.split(), t.split()
        k = 0
        for n in range(min(MAX_OVERLAP_WORDS, len(a), len(b)), 0, -1):
            if [w.lower() for w in a[-n:]] == [w.lower() for w in b[:n]]:
                k = n
                break
        joined = " ".join(a + b[k:])
    return joined.strip()


def _read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


FE_KEYS = ("feature_size", "sampling_rate", "hop_length", "chunk_length", "n_fft",
           "padding_value", "dither")


def feature_extractor_config():
    # The checkpoint was saved by transformers 5, which writes a single
    # processor_config.json with the feature extractor nested inside it.
    # transformers 4 - the version the runtime pins - expects a separate
    # preprocessor_config.json. Reading the values by hand makes the file
    # layout of either major version irrelevant.
    pre = MODEL_DIR / "preprocessor_config.json"
    cfg = _read_json(pre) if pre.exists() else _read_json(MODEL_DIR / "processor_config.json")
    if "feature_size" in cfg:
        return cfg
    for v in cfg.values():
        if isinstance(v, dict) and "feature_size" in v:
            return v
    raise RuntimeError("no feature extractor settings found in ./model")


class Recogniser:
    def __init__(self):
        t0 = time.time()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32

        fe_cfg = feature_extractor_config()
        self.fe = WhisperFeatureExtractor(**{k: fe_cfg[k] for k in FE_KEYS if k in fe_cfg})
        # Built straight from tokenizer.json, which both major versions write in
        # the same format; tokenizer_config.json is the file whose format moved.
        # The only thing decoding needs from it is the clean-up flag.
        self.tok = WhisperTokenizerFast(tokenizer_file=str(MODEL_DIR / "tokenizer.json"))
        tok_cfg_path = MODEL_DIR / "tokenizer_config.json"
        tok_cfg = _read_json(tok_cfg_path) if tok_cfg_path.exists() else {}
        self.cleanup = bool(tok_cfg.get("clean_up_tokenization_spaces", False))

        model, info = WhisperForConditionalGeneration.from_pretrained(
            str(MODEL_DIR), local_files_only=True, dtype=self.dtype, output_loading_info=True)
        # With library warnings silenced, a checkpoint whose tensor names do not
        # match would load as random weights without a word. Refuse instead. Two
        # tensors may legitimately be absent from a file saved by another major
        # version: the output projection (tied to the token embedding) and the
        # encoder's fixed sinusoidal positions, which the library recomputes.
        derived = ("proj_out.weight", "encoder.embed_positions.weight")
        missing = info.get("missing_keys", [])
        self.n_derived = sum(1 for k in missing if k.endswith(derived))
        bad = len(missing) - self.n_derived + len(info.get("mismatched_keys", []))
        if bad:
            raise RuntimeError("checkpoint does not fit the model: %d tensors missing or mismatched" % bad)
        self.n_unexpected = len(info.get("unexpected_keys", []))
        # The explicit cast makes the dtype independent of which keyword this
        # transformers release honours (dtype vs torch_dtype).
        self.model = model.to(device=self.device, dtype=self.dtype).eval()
        self.model.config.use_cache = True
        if getattr(self.model.config, "forced_decoder_ids", None) is not None:
            self.model.config.forced_decoder_ids = None
        if self.fe.feature_size != self.model.config.num_mel_bins:
            raise RuntimeError("feature extractor has %d mel bins, model expects %d"
                               % (self.fe.feature_size, self.model.config.num_mel_bins))

        # generation_config.json carries Whisper's language table; without it
        # language="jw" cannot be honoured. Loaded explicitly so that a file this
        # release cannot parse stops the run instead of silently decoding with a
        # default config.
        gc = GenerationConfig.from_pretrained(str(MODEL_DIR), local_files_only=True)
        if "<|%s|>" % LANG not in (getattr(gc, "lang_to_id", None) or {}):
            raise RuntimeError("generation_config.json has no <|%s|> entry" % LANG)
        # Notebook 06's apply_gen_config: language and task pinned, the legacy
        # forced_decoder_ids path switched off so it cannot silently win.
        gc.language = LANG
        gc.task = "transcribe"
        gc.forced_decoder_ids = None
        gc.num_beams = 1
        gc.do_sample = False
        gc.no_repeat_ngram_size = NO_REPEAT_NGRAM
        gc.max_length = GEN_MAX_LENGTH
        gc.use_cache = True
        self.model.generation_config = gc
        self.t_load = time.time() - t0

    @torch.no_grad()
    def transcribe(self, arrays):
        feats = self.fe(arrays, sampling_rate=SR, return_tensors="pt").input_features
        ids = self.model.generate(feats.to(self.device, dtype=self.dtype), **GEN_KWARGS)
        return [t.strip() for t in self.tok.batch_decode(
            ids, skip_special_tokens=True, clean_up_tokenization_spaces=self.cleanup)]


def read_names():
    meta_path = DATA / "test_metadata.csv"
    if meta_path.exists():
        with open(meta_path, newline="", encoding="utf-8") as fh:
            return [r["audio_filename"] for r in csv.DictReader(fh)]
    # The manifest is documented, but walking clips/ costs nothing and means
    # a missing or renamed manifest degrades instead of failing the run.
    return sorted(p.name for p in CLIPS.glob("*.mp3"))


def main():
    t_start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    names = read_names()
    log("clips to transcribe: %d" % len(names))

    rec = Recogniser()
    log("import %.1fs | model load %.1fs | device %s | %s | tensors recomputed %d, unexpected %d"
        % (_T_IMPORT, rec.t_load, rec.device, str(rec.dtype).replace("torch.", ""),
           rec.n_derived, rec.n_unexpected))

    from postprocess import postprocess

    results = {}
    stats = collections.Counter()
    errors = collections.Counter()
    buf_names, buf_audio = [], []

    def failed(exc):
        stats["failed"] += 1
        errors[type(exc).__name__] += 1
        if DEBUG and errors[type(exc).__name__] == 1:
            traceback.print_exc()

    def run_short():
        # One generate() call per BATCH short clips in manifest order - the batch
        # composition notebook 06 measured. If the batch throws, each clip is
        # retried alone so one bad input cannot blank its neighbours.
        try:
            texts = rec.transcribe(buf_audio)
        except Exception:
            texts = []
            for a in buf_audio:
                try:
                    texts.append(rec.transcribe([a])[0])
                except Exception as e:
                    failed(e)
                    texts.append(None)
        for nm, tx in zip(buf_names, texts):
            results[nm] = "" if tx is None else postprocess(tx)
        stats["short"] += len(buf_names)
        buf_names.clear()
        buf_audio.clear()

    for name in names:
        try:
            y = load_audio(CLIPS / name)
        except Exception as e:
            failed(e)
            results[name] = ""
        else:
            if len(y) / SR > LONG_S:
                # Decoded on the spot, without flushing the short-clip buffer
                # first: notebook 06 did the same, so batches line up clip for clip.
                try:
                    parts = split_windows(y)
                    results[name] = (postprocess(join_overlapping(rec.transcribe(parts)))
                                     if parts else "")
                    stats["chunked"] += 1
                    stats["windows"] += len(parts)
                except Exception as e:
                    failed(e)
                    results[name] = ""
            else:
                buf_names.append(name)
                buf_audio.append(y)
                if len(buf_names) == BATCH:
                    run_short()
        if len(results) >= FAIL_FAST_AFTER and stats["failed"] == len(results):
            raise RuntimeError("the first %d clips all failed (%s) - stopping before a blank file"
                               " is scored" % (len(results), ", ".join(sorted(errors))))
    if buf_names:
        run_short()

    n = len(names)
    n_empty = sum(1 for nm in names if not results.get(nm, "").strip())
    log("short %d | chunked %d (%d windows) | failed %d | empty %d | %d clips in %.1fs"
        % (stats["short"], stats["chunked"], stats["windows"], stats["failed"], n_empty,
           n, time.time() - t_start))
    if errors:
        log("failure types: %s" % ", ".join("%s x%d" % kv for kv in sorted(errors.items())))
    if stats["failed"] > max(MAX_FAIL_FLOOR, int(MAX_FAIL_RATE * n)):
        log("too many failed clips - no submission.csv written, exiting non-zero")
        return 1

    # csv.writer, not string formatting: transcripts contain commas and quotes,
    # and the platform rejects a hand-assembled file.
    out = OUT_DIR / "submission.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["audio_filename", "transcript"])
        for nm in names:
            w.writerow([nm, results.get(nm, "")])
    log("wrote %d rows" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
