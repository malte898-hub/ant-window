# BUILD_PLAN v3.1.1 — calib-00g "live Jev: does the simulator predict a real AI colony?"

Status: REVIEWED 2026-10-14 15:43 Lisbon — mu patches on v3.1 (file mtime 15:36; v3.1 header said ~15:50). Before any 00g data. Needs Claude checker + 96-run pool file in this folder + HITL "GO 00g".
New question (methods). Not a rescue of the closed forgetting thesis; no thesis PASS/KILL here.
00f remains void (v1.9 §6.3). This plan does not re-open it.

Change log v3.1 → v3.1.1:
- Header clock 15:36 write / 15:43 review, not ~15:50.
- "No Mac time" → no Ollama. Mac is the HTTP client (~2 h at measured 11.6 c/s).
- Key: load the API key from the process environment. Empty process env is not missing. Never print the key. Never chat/logs/git.
- Bare format path named: `02_proofs/calib-00_double-bridge/out/tier1/probe_jev_bare.csv` (jev-1.13.0, 210 rows, parse-fail 0).
- Verdict: five stats must land in the registered 90% interval. ±0.05 median tolerance is not a pass path (it would make A and B3 almost unkillable).
- Registered n = 24. Invalids (api_error_rate > 10%) are misses on the two count stats. Medians on valid cells. Valid < 21 → INCOMPLETE, no CONFIRMED/PARTIAL/REFUTED.
- Smoke A 2.5 seed 300 is reused as data. mu column filled before smoke.
- §4 96-run pool is not in this folder (WINDOW_claude 24-run lookup+s0.5 is 0.98 / 0.79 / 0.01, not the 90% table). GO blocked until `jev_sim_pool.csv` lands here so the checker can recompute the intervals.
- Out dir: `data/calib-00g/` in this repo.
- Checker `verify_calib00g.py` is Claude's, still missing.

## 1. Why

Prior-art check (`03_prior_art/tick3_prior_art_ant-window.md`): the design rules are textbook; what may be new is measuring real AI deciders' choice profiles and predicting colonies from them. The Tier 1 count-only screen failed (cannot predict ants). The ant-window simulator (weights, validated on ants) is the fixed version. It has never been tested on a live AI colony. Jev is the cheapest test: expected ≈ USD 1–2, ~2 h wall, no Ollama, near-deterministic, writes no notes.

## 2. Question

Q: Fed Jev's measured probe curve, does the ant-window simulator predict the live Jev colony?

## 3. Setup

- Decider: jev-1.13.0 (record version per cell). **v1.9 bare format exactly as in probe_jev_bare.csv**: top-7 marks strongest-first as a label list; options "route <label>"; option order shuffled per call; sample from returned probabilities (never argmax); no counts, no floor.
- World: BUILD_PLAN v1.6 §2, unchanged (deposit on return, no model call on return).
- Cells: A 2.5, B 2.5, B 3 × **24 seeds (300–323)**, mapping balanced 12/12. Ants on the same cells first (Z4) — ants miss → STOP.
- Per-decision log (read set labels in order, weights, probabilities returned, choice).
- No sense-check gate (that was v1.9's thesis gate; this plan's question needs the run). 00f void stands. Named risk: empty-board P is label-pair dependent (probe 10 pairs 0.38–0.67; one off-probe pair in 00f preflight was 0.76/0.24).
- Smoke: 1 cell A 2.5 seed 300, api_error_rate < 1%, reused as data. Do not start smoke before mu column is filled (done in §7).
- Limits: 3 h, USD 25 (expected ≈ 72 Jev cells × ~1,200 calls ≈ 83k calls, ≈ USD 1–2). Rate-limited or cap hit → STOP, no partial verdict.
- Key load: profile `.env` into the child process before any SKIP.

## 4. Pre-registered predictions (simulator: Jev probe lookup + per-run label bias s 0.5; 96-run pool; 90% intervals for a 24-run sample)

Source of the table: Claude 96-run pool, **not in this folder**. On-disk WINDOW_claude.md (24-run) lookup+s0.5: A 0.98 · B 2.5 0.79 · B 3 0.01. Do not score GO against numbers the checker cannot recompute.

| Statistic | Predicted | 90% interval |
|---|---|---|
| A 2.5 median | 0.983 | 0.980–0.989 |
| B 2.5 median | 0.803 | 0.756–0.857 |
| B 3 median | 0.022 | 0.016–0.027 |
| B 2.5 runs ≥ 0.8 (of 24) | 12 | 8–16 |
| B 2.5 runs ≤ 0.3 (of 24) | 4 | 1–7 |

Mechanism (secondary, not in the 5): Jev's share choosing the short route in ticks 40–49 of B runs — predicted low (median ≤ 0.10), unlike llama (0.46).

## 5. Verdict (checked in this order)

1. VALID: ants Z4 reproduce (A 2.5 ≥ 0.85, B 2.5 ≥ 0.85, B 3 ≤ 0.25 medians); invalid Jev cells (api_error_rate > 10%) ≤ 3. Else STOP / INCOMPLETE.
2. If valid Jev cells < 21 → INCOMPLETE. No CONFIRMED/PARTIAL/REFUTED.
3. Count each of the five statistics as a hit only if it falls **inside its 90% interval**. Medians have no extra ±0.05 pass path.
4. **SIMULATOR CONFIRMED** if 5 of 5 hit.
5. **PARTIAL** if 3–4 of 5.
6. **SIMULATOR REFUTED** if ≤ 2 of 5.

## 6. What each outcome allows

- CONFIRMED: "A choice profile measured in minutes predicted a live Jev colony in this world." One model, one world. Not: "predicted a real AI colony" as a class, not colony-readiness in general, not the ant mechanism.
- PARTIAL: report which statistics missed and why; no general claim.
- REFUTED: static profiles do not predict live Jev colonies even for a note-free, near-deterministic decider; this screen idea closes for Jev.

## 7. Predictions (judgment, before smoke)

| Outcome | Claude | mu |
|---|---|---|
| CONFIRMED | 40% | 20% |
| PARTIAL | 40% | 45% |
| REFUTED | 20% | 35% |

mu: A and B3 90% bands are 0.009 and 0.011 wide — live API + unseen label pairs will miss at least one median even if the sim is directionally right. B 2.5 bimodal is the actual test. CONFIRMED wording that sells a class result is overclaim.

## 8. GO checklist

- [x] mu review; patches → v3.1.1
- [ ] `jev_sim_pool.csv` in this folder (96-run pool; checker recomputes §4 intervals)
- [ ] adapter = probe bare format (no counts); per-decision logging; `.env` load
- [ ] Claude checker `verify_calib00g.py` (Claude writes before GO)
- [x] mu prediction column (§7)
- [ ] smoke A 2.5 s300 — not started
- [x] HITL "GO 00g"
