# Claude note on v3.1.1 (2026-10-14 15:50 Lisbon) — blockers cleared, one open decision

## Blockers cleared

- `jev_sim_pool.csv` (96 runs, seeds 1000–1095, Jev probe lookup + label bias s 0.5) is in this folder. Recomputing the §4 table from it reproduces every number exactly: medians 0.983 / 0.803 / 0.022; intervals A 0.980–0.989, B 2.5 0.756–0.857, B 3 0.016–0.027; counts 12 (8–16), 4 (1–7).
- `verify_calib00g.py` is in this folder. Implements v3.1.1 §5 as written (no tolerance; invalids miss on counts; valid < 21 in any cell → INCOMPLETE; seed guard 300–323; optional secondary pulse stat).
- Accept all mu patches, including the narrower CONFIRMED wording and "sampling consistency, not a class law".
- My earlier header times ("~15:50") were wrong; mu's 15:36/15:43 stand.

## Open decision for HITL (before any data)

Self-test: if the simulator were **exactly right**, how often would a 24-run live sample score 5/5?

| Interval set | P(5/5 \| sim true) | P(3–4) | P(≤ 2) |
|---|---|---|---|
| Registered (§4, seed noise only) | **0.71** | 0.28 | 0.02 |
| Bootstrap incl. probe uncertainty (`jev_sim_boot.csv`, 200 resamples of the 10 label pairs) | **0.89** | 0.11 | 0.00 |

Bootstrap intervals: A 0.977–0.990 · B 2.5 0.694–0.960 · B 3 0.014–0.032 · runs ≥ 0.8: 7–16 · runs ≤ 0.3: 2–10.

- Registered intervals ignore that the probe itself is a sample (10 label pairs). Even a correct simulator would be called PARTIAL ~29% of the time — mostly from the A median band (0.009 wide).
- The bootstrap set adds only the measured probe uncertainty. A and B 3 bands stay narrow (A widens by 0.004), so it is not the ±0.05 slack mu rejected. The real widening is in B 2.5 — the bimodal cell mu calls the actual test.
- Wrong-model check: shifting B values by −0.15 gives REFUTED under both sets.

**Options:** (a) keep v3.1.1 registered intervals (stricter, CONFIRMED ceiling 71%); (b) adopt the bootstrap intervals as v3.1.2 before GO (honest about probe uncertainty, CONFIRMED ceiling 89%). Claude recommends (b). mu to review; HITL decides. Either must be fixed before the smoke.
