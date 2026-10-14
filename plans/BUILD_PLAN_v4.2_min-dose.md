# BUILD_PLAN v4.2 — Minimum coin dose (calib-00k)

Draft by Claude, 2026-10-14 22:03 Lisbon (checker file 22:02). Status: DRAFT for mu review. Nothing runs without HITL words "GO 00k".
Checker: `verify_calib00k.py` (same folder), tested on 3 synthetic grids (model-true, frozen, lock-broken).
Builds on: 00g (coin 0), 00j (coin 0.30, 0.10). Same world, same Jev wiring as 00j (argmax of returned P, then host coin; coin seeded per seed, agent, tick).

## 1. Question

What is the smallest host coin that still lets the colony's memory decide: short memory (TTL 2.5) switches to the new short route, long memory (TTL 3) stays locked?
Live so far (B2.5 switched / B3 locked, n 12 unless noted): coin 0 → 0/24 · 24/24 (00g). Coin 0.10 → 10/12 · 12/12. Coin 0.30 → 12/12 · 12/12.

## 2. Arms (seeds 600–611, fresh; 4-wide; run order Z6 → 0.10 → 0.05 → 0.02)

| Arm | Cells × seeds | Runs |
|---|---|---|
| Ant control Z6 (Deneubourg k 20, n 2) | A2.5, B2.5, B3 × 12 | 36 |
| Jev coin 0.10 (replicate of 00j, fresh seeds) | B2.5, B3 × 12 | 24 |
| Jev coin 0.05 | B2.5, B3 × 12 | 24 |
| Jev coin 0.02 | B2.5, B3 × 12 | 24 |

- No A arms for Jev: at small coin A is ≈ 1 − coin/2 by construction (00j showed A = B2.5 once locked).
- 0.10 replicate is included because the 00j 10/12 reading was post hoc.
- Expected wall time ≈ 1 h (B runs 150–270 s). Cap 3 h. Ants miss VALID → STOP.
- Log per decision (decisions.csv, top level): variant, ttl, seed, tick, agent_id, coin_fired, chosen, top7_n_short, top7_n_long. Needed to see how the first explorer tips the trail.

## 3. Prediction — explorer model (replaces my simulator, which missed twice)

Plain idea: the colony switches if at least one coin-driven explorer goes short inside a short window after the bridge opens. Each decision sends an explorer short with chance coin/2. Fitted to the three live points: the window ≈ 36 decisions (about one wave of 30 agents plus a few).
P(switch) = 1 − (1 − coin/2)^36.

| Coin | P(switch) | Expected switched / 12 | 90% range | P(SPLIT: ≥ 7/12) |
|---|---|---|---|---|
| 0.02 | 0.30 | 3.6 | 1–6 | 4% |
| 0.05 | 0.60 | 7.2 | 4–10 | 66% |
| 0.10 | 0.84 | 10.1 | 8–12 | 99% |

- B3 (TTL 3): predicted locked 12/12 at every dose (long marks survive between waves; 00j locked 24/24).
- The window size is uncertain (fits between ≈ 15 and 70 decisions). That uncertainty is why the model is tested, not assumed.

## 4. Expected answer

Most likely: minimum splitting dose = 0.05 (≈ 60%), with 0.02 FROZEN or PARTIAL. 0.10 (≈ 30%) if 0.05 falls short. 0.02 (≈ 5%). No split even at 0.10 (≈ 5%; would mean 00j's 10/12 was luck).

## 5. Validity

- Z6 medians: A2.5 ≥ 0.85, B2.5 ≥ 0.85, B3 ≤ 0.25.
- Seeds 600–611 exactly once per Jev arm-cell. ≤ 2 invalid per arm. One model_id (jev-1.13.0 expected; change → STOP, HITL).
- Coin rate per arm (n_coin / (n_coin + n_depart_calls)) within 0.8–1.2 × target.
- Invalid run counts against: B2.5 → not switched; B3 → not locked.

## 6. Verdict rules (verify_calib00k.py)

Per dose: S = B2.5 runs ≥ 0.8; L = B3 runs ≤ 0.3.
- SPLIT: S ≥ 7 and L ≥ 10 (memory decides).
- FROZEN: S ≤ 3 and L ≥ 10 (too little exploration).
- NOISY: L ≤ 9 (exploration breaks the long-memory lock).
- else PARTIAL.
Minimum dose = lowest coin with SPLIT.
Explorer model: HOLDS if switched counts at all 3 doses sit inside the 90% ranges; REFUTED if 2+ outside; else MIXED.

Note: SPLIT uses counts, not AUC. In 00j the 0.10 arm (10/12, 12/12) had AUC 0.882 because the two locked B2.5 runs tie with B3. Counts state the question directly. This is a new rule for this loop, set before data, not a re-scoring of 00j.

## 7. Wording of results

"With argmax Jev plus a host coin, the memory split appears from a coin of X upward in this world." Not a Jev temperature. Not the ant mechanism. A minimum near ants' effective exploration would be worth reporting; the literature check is still owed before any public claim.

## 8. Security — unchanged

Key from the process environment into the process only. Never print it. Never chat, logs or git.
