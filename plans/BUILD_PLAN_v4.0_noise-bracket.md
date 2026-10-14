# BUILD_PLAN v4.0 — Noise bracket (calib-00i gate + calib-00j)

Draft by Claude, 2026-10-14 evening, after 00g. Status: DRAFT for mu review. Nothing runs without HITL words "GO 00i" (Part A) and later "GO 00j" (Part B).
Checker: `verify_calib00j.py` (same folder), tested on simulated PASS and null grids.

## 1. Why

- llama-8B at T 0.7: too much noise (fitted ε ≈ 0.40). No clean ant boundary (00c–00e).
- Jev: no noise. Always picks its top-rated option (210/210 probe rows; 0 minority picks in 28,800 live calls, 00g). Colony freezes on its first habit, whatever the memory length.
- Ants: ε ≈ 0.05. Clean boundary every time.
- Hypothesis: noise is the design variable. Tune it and the ant boundary comes back.
- Corrected simulator (Jev = argmax lookup, validated by reproducing 00g exactly) adds a sharper, non-obvious prediction: **a step-like decider like Jev needs much more noise than ants (≈ 0.30, not 0.05)**, because it has no soft zone at low trail strength.

## 2. Part A — calib-00i: choice re-probe (gate, ~1 h)

Goal: measure what models DO, not what they say.

A1 Jev
- Check the API for temperature / seed / sampling settings. Record them. Do not change any for Part B unless a v4.1 amendment is approved.
- Trail states (n_short, n_long): (0,0) (1,0) (0,1) (4,3) (3,4) (7,0) (0,7). 3 fresh label pairs. 20 repeats each, order alternated. 420 calls.
- Record the CHOSEN route (not the stated probability).
- Gate A1 PASS: minority-choice rate at (7,0)+(0,7) ≤ 1% (argmax model holds). If > 1%: STOP, Claude re-fits the simulator, v4.1 re-registers Part B predictions before any GO 00j.

A2 llama-3.1-8B
- Temperatures 0.7, 0.4, 0.2, 0.0. Same 7 states × 3 label pairs × 20 repeats = 1,680 calls.
- Per temperature report: minority-choice rate at full trail (→ ε ≈ 2 × rate), empty-board first-listed share, parse-fail rate, distinct notes per 20 (variety).
- Pre-registered pick rule for Part B: the temperature whose ε is nearest 0.10, among those with parse-fail ≤ 5% and variety ≥ 5 distinct notes per 20. Ties → higher temperature.
- If no temperature qualifies: llama arm drops from Part B (Jev arm still runs).

## 3. Part B — calib-00j: the bracket (Jev ~1 h; llama ~4.5 h overnight)

World: unchanged (v3.1.1 / 00g world: L 2/4, TTL 2.5 and 3, T_open 40, N 30, 200 ticks, top-7, drop 0.05). Seeds 500–511 (fresh). 4-wide.

| Arm | Noise | Cells × seeds | Runs |
|---|---|---|---|
| Jev coin | ε 0.30: each decision, with prob 0.30 pick a route uniformly at random (no Jev call); else Jev's pick | A2.5, B2.5, B3 × 12 | 36 |
| Jev coin | ε 0.10 (dose check) | B2.5, B3 × 12 | 24 |
| llama | temperature from A2 (no coin) | A2.5, B2.5, B3 × 12 | 36 |
| Ant control Z5 | ε 0.05 rule | A2.5, B2.5, B3 × 12 | 36 |

- ε = 0 is already measured (00g). Not re-run.
- Coin is done in code, seeded per (seed, agent, tick). Log coin_fired per decision.
- grid.csv columns: agent, noise, variant, ttl, seed, frac_short_last50, invalid, api_error_rate, parse_fail_rate_depart, parse_fail_rate_return, model_id, n_depart_calls, n_coin.

## 4. Predictions (corrected simulator, 96 runs per cell, seeds 3000–3095)

| Arm | A2.5 | B2.5 median | B2.5 switched (≥ 0.8) | B3 median | B3 locked (≤ 0.3) |
|---|---|---|---|---|---|
| Jev ε 0 (00g, live) | 1.00 | 0.00 | 0% | 0.00 | 100% |
| Jev ε 0.10 | 0.95 | 0.05 | 17% | 0.05 | 100% |
| Jev ε 0.30 | 0.85 | 0.84 | 82% | 0.15 | 100% |
| Ants ε 0.05 | 0.92 | 0.93 | 98% | 0.12 | 100% |

Verdict odds for Jev if the simulator is right (resampling 12 of 96): RESTORED + DOSE 70%, RESTORED only 3%, INCONCLUSIVE 27%, NOT RESTORED < 1%.

llama: no numeric intervals. The static simulator has already been wrong about the real llama colony (first-impression lottery, label bias). Simulator says ε 0.10 should work (B2.5 0.92, B3 0.09). Directional prediction only. Claude and mu each log a probability of PASS before GO 00j.

## 5. Validity (before any verdict)

- Ants Z5 medians: A2.5 ≥ 0.85, B2.5 ≥ 0.85, B3 ≤ 0.25.
- Seeds 500–511 only; every arm-cell exactly 12 rows; ≤ 2 invalid runs per arm.
- Invalid run = invalid flag, api_error > 10% or parse-fail > 10%. Counted against the prediction (B2.5 → not switched, B3 → not locked).
- Model id constant within an arm (Jev version as in 00g: jev-1.13.0; if it changes → STOP, HITL).

## 6. Verdict rules (verify_calib00j.py)

Jev (judged at ε 0.30):
- **BOUNDARY RESTORED**: AUC(B2.5 > B3) ≥ 0.90 AND B3 locked ≥ 10/12 AND B2.5 switched ≥ 7/12 AND A2.5 median ≥ 0.75.
- **+ DOSE CONFIRMED**: also ε 0.10 AUC ≤ 0.75 (too little noise still freezes).
- **NOT RESTORED**: AUC ≤ 0.70. Otherwise INCONCLUSIVE.

llama (chosen temperature; v1.8.2 relative rules, fresh seeds):
- ceiling = median A2.5. ceiling < 0.75 → UNINTERPRETABLE.
- PASS: U ≥ 120/144, median rel B2.5 ≥ 0.90, median rel B3 ≤ 0.60. KILL: U ≤ 100 or rel B2.5 < 0.70. Else INCONCLUSIVE.

Checker tested: simulated-true grid → RESTORED + DOSE / llama PASS; null grid (ε 0) → NOT RESTORED / llama UNINTERPRETABLE.

## 7. What each result means

- Jev RESTORED + DOSE: first constructive result. A zero-noise LLM colony becomes ant-like with tuned noise; the needed dose depends on how step-like the decider is.
- Jev NOT RESTORED: noise alone is not enough for Jev; something else in the trail or prompt blocks switching.
- llama PASS at low temperature: the llama failure was too much noise, not inability.
- llama KILL: llama's problems are biases (position, label, invented content), not temperature.

## 8. Prior art (owed before any public claim)

Exploration noise is textbook (Deneubourg ε, MMAS τ_min, ε-greedy). Candidate-new: measured too-much and too-little noise failures in two LLM colonies with an ant control, and the decider-steepness → dose rule. Full read of the six papers plus a search for "noise-tuned LLM multi-agent herding" before any claim.

## 9. Security (unchanged)

Key from the process environment into the process only. Never print it. Never chat, logs or git.
