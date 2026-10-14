# calib-00k — Claude independent check (2026-10-14, after ALL DONE)

Inputs: grid.csv (108 rows), decisions.csv (66,523 rows, 72 Jev runs). Agree: minimum splitting dose = 0.05; explorer model HOLDS.

## Validity
- Z6 ants 0.938 / 0.927 / 0.113 → OK.
- Every Jev arm-cell has seeds 600–611 once; jev-1.13.0 throughout; invalid 0.
- Coin rate over two-option decisions (tick ≥ 40), per run: 0.10 arm 0.083–0.128; 0.05 arm 0.035–0.066; 0.02 arm 0.013–0.028. Pooled rates on target.

## Counts (recomputed)
| Coin | B2.5 switched | B3 stayed | Model 90% range | Verdict |
|---|---|---|---|---|
| 0.02 | 6/12 | 12/12 | 1–6 (top edge) | PARTIAL |
| 0.05 | 10/12 | 12/12 | 4–10 (top edge) | SPLIT |
| 0.10 | 11/12 | 12/12 | 8–12 | SPLIT |

All three inside → MODEL HOLDS, but at the top of each range. Refit on all six live points (00g, 00j, 00k): window ≈ 52 decisions, not 36. Refitted P(switch): 0.02 → 0.40, 0.05 → 0.73, 0.10 → 0.93.

## Two new findings from the decision log (post hoc, important)

1. **Jev is not a pure majority follower on mixed trails.** Jev's own picks (coin not fired, tick ≥ 40, TTL 2.5), by short marks among the 7 it reads:
   0/7 short → 0/7,655 (0.00) · 1/7 → 116/894 (0.13) · 2/7 → 162/351 (0.46) · 3/7 → 360/368 (0.98) · 4/7 to 7/7 → 1.00.
   It switches at about 2 of 7, not 4 of 7, and it varies at 1–2 of 7. So once one coin explorer puts a short mark in its view, Jev itself recruits more. The colony behaves like ants: a threshold, positive-feedback response to trail.
   Open question for mu: what exactly does the Jev prompt show per mark (count only, weights, ages, trip durations)? If marks carry trip duration or freshness, Jev may be preferring the faster/newer route for that reason. That would be a "duration leak" like the llama loop and must be stated.

2. **Why long memory stays locked.** In TTL 3 runs Jev never saw a short mark among its 7: all 20,792 own decisions after tick 40 were at 0/7. Coin explorers did go short (same ticks as in TTL 2.5, same seeds), but their marks never made the top 7, because long marks fade too slowly and stay heavier. In TTL 2.5 the old long marks fade fast enough for one fresh short mark to get into view. The memory boundary works through what fits in the 7-mark window.

## Other notes
- Coin draws are shared across arms with the same seed (same first-explorer ticks in TTL 2.5 and 3). The doses are paired comparisons, not independent samples. Fine for the question, worth stating.
- First Jev short pick came 4–120 ticks after the first coin explorer (e.g. s600 0.10: coin short at 40, Jev short at 44 seeing 2/7).

## Scorecard
Claude 0.05 / HOLDS: hit. mu 0.10 / MIXED-REFUTED lean: missed.
