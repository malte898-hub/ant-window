# BUILD_PLAN v4.0.1 — Noise bracket (calib-00i gate + calib-00j)

Status: REVIEWED 2026-10-14 18:34 Lisbon (v4.0 file mtime 18:31; header said "evening"). Before any 00i/00j data. Needs HITL "GO 00i" then later "GO 00j". This file is not a start order.
Checker: `verify_calib00j.py` in this folder (v4.0 §6). Do not start Part B without it.

Change log v4.0 → v4.0.1:
- Header clock 18:31/18:34.
- 00g live Jev calls = **64,453** (grid n_depart_calls), not 28,800. Probe chosen==argmax **210/210**. Live: **0** minority on unanimous boards (63,733); **320** ≠ argmax overall (empty/tie sampling). Do not say "always argmax" for empty boards.
- Mixed top-7 never occurred in 00g (0 mixed-mark calls). Lock, not a mixed-board test.
- Z5 ants = live Deneubourg k=20 n=2 (same as 00g Z4), **not** an ε-coin 0.05 overlay.
- Part B Jev: **argmax of returned probabilities, then host coin**. Do not sample-from-P then coin (double noise). 00g sampled; unanimous boards were 0/1 so equivalent there.
- Coin is **host RNG**, seeded per (seed, agent, tick). RESTORED wording = "boundary returns when 30% of decisions are replaced by a coin", not "Jev grew temperature".
- §4 96-run pool (seeds 3000–3095) is **not in this folder**. Numbers stay as written; GO 00j blocked until `jev_coin_pool.csv` lands so the checker/odds can be recomputed. Do not mint replacement intervals.
- Run order Part B: Z5 first (miss → STOP) → Jev ε 0.30 → Jev ε 0.10 → llama. 4-wide. Llama cap 8 h (00e 36 cells was 4.43 h). Jev cap 3 h.
- llama U/PASS drops the v1.8.2 even+odd mapping clause (n=12 is 6/6 seeds; still require that split in the runner, not the checker). Named.
- RESTORED switched bar 7/12 is easier than the 82% table (~10/12). Named, not raised from review.
- Key: the process environment into the process. Empty os.environ is not missing. Never print.
- Out dir: `02_proofs/ant-window/out/calib-00i/` and `.../calib-00j/`. Studio tree is not the project.
- v3.2 staggered-llama is a different question. Do not merge.

## 1. Why

- llama-8B at T 0.7: too much noise (fitted ε ≈ 0.40). No clean ant boundary (00c–00e; 00e ceiling 0.708 UNINTERPRETABLE).
- Jev: near-zero exploration on a unanimous trail. Probe 210/210 chosen=argmax. 00g: 0 minority on unanimous boards; colony freezes on first habit at both TTL 2.5 and 3 (A last50=1.0 all 24; B last50=0.0 all 48).
- Ants: Deneubourg k=20 n=2. Clean boundary every Z so far (Z4: 0.935 / 0.933 / 0.139).
- Hypothesis: **host-injected** exploration noise is the design variable. Tune it and the ant boundary comes back.
- Simulator claim (not in-tree): Jev as argmax lookup + coin, said to reproduce 00g; predicts a step-like decider needs ≈ 0.30 coin, not 0.05.

## 2. Part A — calib-00i: choice re-probe (gate, ~1 h)

Goal: measure what models DO (chosen route), not stated P.

A1 Jev
- Check the API for temperature / seed / sampling settings. Record them. Do not change any for Part B unless a v4.1.x amendment is approved.
- Trail states (n_short, n_long): (0,0) (1,0) (0,1) (4,3) (3,4) (7,0) (0,7). 3 fresh label pairs. 20 repeats each, order alternated. 420 calls.
- Record the CHOSEN route (not the stated probability). Also persist returned P, model string, label pair.
- Gate A1 PASS: minority-choice rate at (7,0)+(0,7) ≤ 1% (argmax-on-unanimous holds). If > 1%: STOP, Claude re-fits, v4.1.x re-registers Part B before any GO 00j.

A2 llama-3.1-8B
- Temperatures 0.7, 0.4, 0.2, 0.0. Same 7 states × 3 label pairs × 20 repeats = 1,680 calls. Pin the 00e serving tag/digest.
- Per temperature: minority-choice rate at full trail (ε̂ ≈ 2 × rate only as a coin-equivalent report, not a Deneubourg identity), empty-board first-listed share, parse-fail, distinct notes per 20.
- Pick for Part B: temperature whose ε̂ is nearest 0.10, among parse-fail ≤ 5% and variety ≥ 5 distinct notes per 20. Ties → higher temperature.
- If none qualify: llama arm drops from Part B (Jev arm still runs).

## 3. Part B — calib-00j: the bracket

World: 00g / v3.1.1 (L 2/4, TTL 2.5 and 3, T_open 40, N 30, 200 ticks, top-7, drop 0.05, deposit on return). Seeds **500–511** (fresh, 6 even / 6 odd). 4-wide.
Jev choice: argmax(probabilities), then coin. Never use Jev's `choice` field as the only source if it disagrees with argmax of `probabilities` — log both.

| Arm | Noise | Cells × seeds | Runs |
|---|---|---|---|
| Jev coin | ε 0.30: with prob 0.30 pick uniformly at random (no Jev call); else argmax(P) | A2.5, B2.5, B3 × 12 | 36 |
| Jev coin | ε 0.10 (dose check) | B2.5, B3 × 12 | 24 |
| llama | temperature from A2 (no coin) | A2.5, B2.5, B3 × 12 | 36 |
| Ant control Z5 | Deneubourg k=20 n=2 (not a coin) | A2.5, B2.5, B3 × 12 | 36 |

- ε = 0 is 00g. Not re-run.
- Coin in code, seeded per (seed, agent_id, tick). Log coin_fired per decision.
- grid.csv: agent, noise, variant, ttl, seed, frac_short_last50, invalid, api_error_rate, parse_fail_rate_depart, parse_fail_rate_return, model_id, n_depart_calls, n_coin.
- Run order: Z5 → Jev 0.30 → Jev 0.10 → llama. Ants miss VALID → STOP (no Jev, no llama).
- Caps: Jev 3 h; llama 8 h; rate-limit or cap → STOP, no partial verdict.

## 4. Predictions (simulator 96 runs / cell, seeds 3000–3095 — CSV not in folder)

| Arm | A2.5 | B2.5 median | B2.5 switched (≥ 0.8) | B3 median | B3 locked (≤ 0.3) |
|---|---|---|---|---|---|
| Jev ε 0 (00g, live) | 1.00 | 0.00 | 0% | 0.00 | 100% |
| Jev ε 0.10 | 0.95 | 0.05 | 17% | 0.05 | 100% |
| Jev ε 0.30 | 0.85 | 0.84 | 82% | 0.15 | 100% |
| Ants k=20 n=2 | 0.92 | 0.93 | 98% | 0.12 | 100% |

Verdict odds for Jev if the simulator is right (resampling 12 of 96): RESTORED + DOSE 70%, RESTORED only 3%, INCONCLUSIVE 27%, NOT RESTORED < 1%. Unverified until pool file exists.

llama: no numeric intervals. Directional only. Log P(PASS) before GO 00j.

## 5. Validity (before any verdict)

- Ants Z5 medians: A2.5 ≥ 0.85, B2.5 ≥ 0.85, B3 ≤ 0.25.
- Seeds 500–511 only; every required arm-cell exactly 12 rows; ≤ 2 invalid runs per arm.
- Invalid = invalid flag, api_error > 10% or parse-fail > 10%. B2.5 invalid → not switched; B3 invalid → not locked.
- Model id constant within an arm (Jev: jev-1.13.0 as 00g; change → STOP, HITL).

## 6. Verdict (verify_calib00j.py)

Jev at ε 0.30:
- **BOUNDARY RESTORED**: AUC(B2.5 > B3) ≥ 0.90 AND B3 locked ≥ 10/12 AND B2.5 switched ≥ 7/12 AND A2.5 median ≥ 0.75.
- **+ DOSE CONFIRMED**: also ε 0.10 AUC ≤ 0.75.
- **NOT RESTORED**: AUC ≤ 0.70. Else INCONCLUSIVE.

llama (A2 temperature; relative to own A2.5 median; 12×12=144):
- ceiling < 0.75 → UNINTERPRETABLE.
- PASS: U ≥ 120/144, median rel B2.5 ≥ 0.90, median rel B3 ≤ 0.60.
- KILL: U ≤ 100 or rel B2.5 < 0.70. Else INCONCLUSIVE.

## 7. What each result means

- Jev RESTORED + DOSE: first constructive result **of host coin-noise on an argmax Jev colony**. Not: "Jev uses the ant mechanism." Not a temperature in the API.
- Jev NOT RESTORED: coin-noise at 0.30 is not enough; something else blocks switching.
- llama PASS at the A2 temperature: too much sampling noise was a cause. Not a proof that biases are gone.
- llama KILL: remaining failure is not fixed by turning T down.

## 8. Prior art

Exploration noise is textbook (Deneubourg ε, MMAS τ_min, ε-greedy). Candidate-new: measured too-much and too-little noise in two AI colonies with an ant control, plus steepness → dose. Full read owed **before any public claim**, not before GO 00i.

## 9. Security

Key from the process environment into the process only. Never print it. Never chat, logs or git.

## 10. Predictions (judgment, before 00i)

| Outcome | Claude (implied by §4) | mu |
|---|---|---|
| Jev RESTORED + DOSE | 70% | 40% |
| Jev RESTORED only | 3% | 10% |
| Jev INCONCLUSIVE | 27% | 20% |
| Jev NOT RESTORED | <1% | 30% |
| llama PASS (if arm runs) | (unlogged) | 15% |

mu: 00g already killed a Jev lookup simulator. Coin may restore B2.5 by brute force and still miss the 7/12+AUC AND. llama first-impression pulse (EXPORT_ANALYSIS) is not a temperature.

## 11. GO checklist

- [x] mu review; patches → v4.0.1
- [x] `jev_coin_pool.csv` in this folder before GO 00j (not required for GO 00i)
- [x] A1/A2 scripts; chosen-route logged; `.env` load
- [x] checker `verify_calib00j.py` in folder
- [x] HITL "GO 00i" — Part A only
- [x] A1 PASS; A2 pick or llama drop logged (DROP: no T qualifies)
- [ ] mu llama P(PASS) filled before GO 00j (if llama arm lives) — N/A, arm dropped
- [x] HITL "GO 00j" — Part B only, this file
