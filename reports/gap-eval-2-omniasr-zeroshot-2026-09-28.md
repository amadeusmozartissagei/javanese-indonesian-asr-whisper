---
title: "Evaluasi Gap #2 — omniASR Zero-shot vs D"
aliases:
  - Evaluasi Gap 2
  - omniASR zero-shot
tags:
  - research
  - competition
  - asr
  - gap-eval
  - omniasr
status: final
created: 2026-09-28
updated: 2026-09-28
---

# Evaluasi gap #2: apakah omniASR (pembuat referensi dev) lebih baik dari kita?

**Jawaban: tidak.** Tanpa fine-tune, omniASR kalah dari D di dev 372 klip, dengan
normalizer resmi. Lead #2 untuk omniASR **ditutup**.

Run: `notebooks/09-omniasr-zeroshot.ipynb`, T4, fp16, `findings/09-omniasr-zeroshot/`
(11/11 check) dan `findings/09-omniasr-zeroshot-smoke/` (12/12). Paket `omnilingual-asr`
0.2.0 di venv terpisah (torch 2.8.0, fairseq2 0.6).

## Hasil (dev 372 klip, 17.485 token)

| Sistem | WER resmi | Tanpa kapital & tanda baca | clean-222 | javind | ind | RTF T4 |
|---|---:|---:|---:|---:|---:|---:|
| **D (E4-native beam5)** | **0,2268** | **0,2115** | 0,2265 | 0,2294 | 0,1754 | — |
| omniASR_LLM_3B_v2, `jav_Latn` | 0,2518 | 0,2203 | 0,2528 | 0,2550 | 0,1893 | 0,164 |
| omniASR_LLM_3B, `jav_Latn` | 0,2675 | 0,2362 | 0,2624 | 0,2701 | 0,2172 | 0,166 |
| omniASR_CTC_3B_v2 | 0,4570 | 0,4348 | 0,4431 | 0,4614 | 0,3728 | 0,026 |

Selisih berpasangan (omni − D), bootstrap 3.000× per klip:

| | Resmi | Tanpa kapital & tanda baca | Klip lebih baik / lebih buruk |
|---|---|---|---|
| LLM_3B_v2 | +0,0250 [+0,0146, +0,0359] | +0,0089 [−0,0011, +0,0193] | 143 / 193 |
| LLM_3B | +0,0407 [+0,0315, +0,0503] | +0,0247 [+0,0158, +0,0337] | 99 / 239 |

## Yang dipelajari

1. **Pendengaran v2 kira-kira setara D, tidak lebih baik.** Tanpa kapital dan tanda baca,
   CI-nya menyentuh nol. Dengan WER resmi, v2 kalah 0,025 karena konvensi kapital dan tanda
   baca.
2. **Model yang disebut "pembuat referensi" (LLM_3B v1) justru yang terburuk** di antara
   varian LLM. Referensi dev jelas diedit berat dari output mentahnya (atau memakai versi
   atau setting lain). Hipotesis "top team cukup memakai model pembuat referensi" **tidak
   didukung**, begitu juga ide memindahkan konvensi omniASR lewat pseudo-label.
3. **CTC (satu-satunya jalur yang realistis masuk container) tertinggal jauh**: 0,457,
   dengan deletion 3.924. Tidak layak dikejar.
4. Oracle per-klip min(D, v2) = 0,2025. Ini batas atas teoretis kalau ada selector
   sempurna, dan butuh omniASR LLM jalan di container, padahal itu terblokir (torch 2.11 vs
   fairseq2/torch 2.8). Tidak realistis sebelum 2 Okt.

## Implikasi untuk gap ke #1 (0,2096 test)

Top team tidak sekadar memakai omniASR zero-shot. Sisa lead: fine-tune dengan data
berkonvensi referensi (NB 10, dev-stage), post-processing (NB 07-lite, ~−0,005 sampai
−0,011), dan forum/tulisan publik. Lihat [[gap-eval-1-reference-convention-2026-09-27]].

Catatan teknis: pin `torch==2.8.0 torchaudio==2.8.0` + `wrapt` wajib di venv (tanpa pin,
uv mengambil torchaudio 2.11 / CUDA 13). fp16 aman di T4 (bf16 4,9× lebih lambat, WER
beda +0,004 di 12 klip).
