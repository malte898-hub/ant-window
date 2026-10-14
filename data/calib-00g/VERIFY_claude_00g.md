# calib-00g — Claude independent check

2026-10-14, after ALL DONE. Inputs: grid.csv, decisions.csv, overnight.log, jev_B_ttl2.5_s300/metrics.json, t1data/probe_jev_bare.csv, aw2.py (my lookup sim).

## 1. Verdict check — AGREE: SIMULATOR REFUTED, 0/5

- Grid clean: 72 ant + 72 Jev rows. Each cell has seeds 300–323 exactly once. No duplicates from the dead first launch (ant A2.5 s300 reused once, skipped=True; ants are deterministic per seed).
- Ants valid: 0.935 / 0.933 / 0.139.
- Jev: 72/72 valid, api_error 0, model jev-1.13.0.
- Recomputed frac_short_last50 from raw decisions.csv: A2.5 = 1.000 in all 24 runs; B2.5 = 0.000 in all 24; B3 = 0.000 in all 24. Same as grid and mu.
- Validity of the B arm: short route WAS offered. metrics.json shows n_jev_skip_one 150 (ticks 0–32, one option) and 600 Jev calls with two options from tick 40.
- B arms: 0 short choices out of 28,800 two-option Jev calls. A arm: 0 long choices after tick 10. Tick 0 (empty board) varied 11–21 of 30 short per seed (mean 0.53; probe said 0.52).

## 2. Root cause — my error in the simulator, now found

The probe's p_short is Jev's STATED probability (its "probabilities" field), not an observed choice rate. Jev's actual choice is always the argmax of what it states: 210/210 probe rows. My lookup sim (aw2.py) treated the stated numbers as coin flips. At a full trail Jev states about 0.02 for the other route; the sim therefore sent about 2% of agents the "wrong" way. That 2% was the entire switching mechanism in B2.5 (the bimodal ~0.80 prediction). Live Jev never picks the stated minority.

Post-hoc counterfactual (same sim, seeds 1000–1023): set the full-trail tails to 0/1 only → A2.5 1.000, B2.5 0.000 (24/24 ≤ 0.3), B3 0.000. Reproduces the live grid exactly. Post-hoc, labelled as such; not a new test.

## 3. Plain wording

- A static probe did not predict the live Jev colony. The reason is specific: confidence numbers are not behaviour.
- Jev is a zero-noise follower once any trail exists: it locks onto whatever the colony did first. In A that is short (short trips return first). In B that is long, forever, whatever the memory length.
- So memory length did nothing for Jev. Forgetting cannot rescue a colony with no explorers. Matches the ant window (failure mode "too steep, no exploration") and MMAS τ_min / Deneubourg ε.
- llama: too much noise. Jev: none. Ants: ε ≈ 0.05. Noise is a design variable, not a nuisance.

## 4. Scorecard

Claude 40% CONFIRMED / mu 35% REFUTED. Outcome REFUTED. mu closer.

## 5. Method lesson

Never use a model's self-reported probabilities as its choice rate. Measure choice frequencies from repeated sampled calls (or check the API's sampling setting) before building a simulator on them.
