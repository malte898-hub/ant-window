# The llama loop (calib-00 → calib-00e): small LLMs are too noisy to be ants

Swarms project · written 2026-10-14 by Claude (planner/checker) from the run files, mu's reports and Claude's independent checks.
Status: llama track CLOSED (HITL 2026-10-14). Next and last shot on this question: calib-00f with Jev (BUILD_PLAN_v1.9).

---

## 1. One-paragraph summary

We asked whether a colony of AI agents, each a small text LLM (llama-3.1-8B, run locally), behaves like an ant colony on the classic double-bridge test: when a shorter bridge appears late, do the agents switch to it if — and only if — their trail "forgets" fast enough? Real-ant rules (our simulator) do this perfectly: with short memory 24/24 runs switch, with slightly longer memory 0/24. Over 172 llama runs in three overnight runs, the llama colony pointed the same way on average, but it was 5 to over 100 times noisier than the ants from run to run, could not reliably hold a choice even when nothing changed, and the one clean-looking result (calib-00d) did not replicate on fresh starts (calib-00e). **Conclusion: in this setup, llama-8B agents are too noisy to act as ants.** Forgetting nudges them in the right direction, but the noise hides the sharp ant boundary.

---

## 2. The test in plain words

- **Double bridge (Deneubourg 1990).** A nest, food, two bridges. Short bridge: round trip 4 ticks. Long bridge: 8 ticks. 30 agents, 200 ticks.
  - **Variant A:** both bridges open from the start. A healthy colony settles on the short one.
  - **Variant B:** only the long bridge at first; the short one opens at tick 40. Can the colony change its mind?
- **Trail.** Each agent coming home leaves a mark. Marks fade (memory length = TTL). Agents read the 7 strongest marks before choosing.
- **The ant prediction.** If marks fade before the colony has had time to try the new short bridge (memory shorter than about one long round trip), old habits die and the colony switches. If marks last longer, the colony stays locked on the long bridge.
  - Ratio used: memory_lifetime_ratio (mlr) = TTL·ln20/8. TTL 2.5 → mlr 0.94 (switch expected). TTL 3 → mlr 1.12 (lock-in expected).
- **The LLM version.** Each agent is one call to llama-3.1-8B (temperature 0.7). It reads the 7 strongest trail notes and picks a route; on return it writes a short note.
- **Success measure.** Share of departures on the short bridge in the last 50 ticks (frac_short_last50). "Re-decided" = ≥ 0.8 in variant B.

---

## 3. Timeline

| Date | Step | What happened |
|---|---|---|
| 10-11 | Project opened | Nature-first loop; double-bridge calibration chosen as ground truth before any real proof. |
| 10-12 | Gates 1–2 (ants only) | Simulator sane. Gate 2c′: without trail deletion ants never re-decide (0/3) → forgetting is the driver. Ant TTL sweep set the boundary. |
| 10-12 | smoke-00 → calib-00b | First LLM smoke failed; model selection across 5 models (qwen3-8B, llama-3.1-8B, Claude Sonnet 4.6, Claude Haiku 4.5, GPT-4.1). |
| 10-12 | Gate 3a (empty board) | **All 5 models failed**: with no trail, they pick the first-listed route 88–100% of the time. qwen3 also failed variety (2 distinct notes per 20). llama chosen: local, passes variety. |
| 10-12 | Gate 3a′ (content vs position) | llama does read content: picks the route with the good note 78–96% (Haiku ~100%). |
| 10-12 | Gate C3 (novel route) | llama invents routes that do not exist in 18–54% of answers (Haiku 0%). |
| 10-12/13 | **calib-00c** (run 1) | 64 cells, 4 seeds, TTL sweep, 15.6 h, 34M tokens. Variant B re-decided: TTL 2.5 3/4, 2 2/4, 3 1/4, 5 0/4, 10 0/4, ∞ 1/4. Floor not met (A ∞ 1/4, A 10 2/4). Invented content 81%; first-listed bias 66%. |
| 10-13 | Plan v1.7 → v1.7.8 | Kill rule pre-registered; ant control (block Z) added; speed gate; 4-wide Ollama only 1.32× (accepted). |
| 10-13 | **calib-00d** (run 2) | 72 llama + 72 ant cells, 12 seeds. **Floor not met** → uninterpretable. Primary: re-decided 5/12 at 2.5, 1/12 at 5, 0/12 at 3 and ∞ (would have been KILL). Ants: 12/12 at 2.5, 0/12 elsewhere. |
| 10-13 | Post-hoc look | Continuous measure: every TTL 2.5 run (0.63–0.96) beat every TTL 3 run (0.01–0.56). Looked like the ant boundary. Flagged as post-hoc. |
| 10-13 | Plan v1.8 → v1.8.2 | Confirmation test pre-registered on fresh seeds, judged against the colony's own level; bars only tightened after mu review. |
| 10-13/14 | **calib-00e** (run 3) | 36 llama + 36 ant cells, seeds 100–111, 4.4 h. **Uninterpretable**: colony's own level 0.708 < 0.75. Diagnostic U = 99/144 (KILL side). Direction held; clean boundary did not. Ants perfect again. |
| 10-14 | HITL | Llama track closed. One Jev shot approved (calib-00f). |

Totals: 172 llama runs (64 + 72 + 36), ≈ 77M tokens, ≈ 30 h of Mac Studio time, plus over 100 ant runs (seconds each).

---

## 4. The evidence that llama is too noisy

### 4.1 Run-to-run spread (00d + 00e pooled, same cells, fresh seeds)

| Cell | Ants: median · spread (SD) · range | llama: median · spread (SD) · range |
|---|---|---|
| A, TTL 2.5 (nothing changes) | 0.93 · **0.02** · 0.88–0.96 | 0.74 · **0.16** · 0.43–1.00 |
| A, TTL ∞ (nothing changes) | 1.00 · **0.00** · 0.99–1.00 | 0.75 · **0.22** · 0.26–1.00 |
| B, TTL 2.5 (should switch) | 0.94 · **0.02** · 0.89–0.97 | 0.79 · **0.11** · 0.60–0.96 |
| B, TTL 3 (should stay locked) | 0.13 · **0.04** · 0.06–0.23 | 0.33 · **0.29** · 0.01–1.00 |

- llama is **5–8× noisier** than the ant rule on identical cells where something happens (B 2.5: 5×, B 3: 7×, A 2.5: 8×), and **over 100× noisier** when nothing changes at all (A ∞).
- With nothing to change (A), the ants settle every time; llama settles (≥ 0.7) in only 15/24 runs at TTL 2.5 and 6/12 at TTL ∞.
- At TTL 3, ants never switch (max 0.23); llama runs land anywhere from 0.01 to 1.00 — 4/24 at ≥ 0.7.

### 4.2 The boundary: direction yes, sharpness no

- Pooled over calib-00d and calib-00e, a TTL 2.5 run beats a TTL 3 run 87.5% of the time (504/576 pairs). The direction is real and matches the ants.
- calib-00d alone: 100% (144/144). calib-00e alone: 69% (99/144). The perfect separation was partly luck.
- Ants: 100% in both.
- Note: the pooled figure is descriptive only. calib-00d is where the pattern was found, so it cannot confirm itself.

### 4.3 Where the noise comes from (observed, not all proven causal)

1. **Sampling randomness.** Temperature 0.7 on every call; no fixed sampler seed in Ollama, so no run is repeatable.
2. **Position bias.** With an empty board every model picked the first-listed route 88–100% (gate 3a). In runs, 59–78% of picks went to the first-listed option.
3. **Label bias.** Which random label the short bridge got shifted results by 0.07–0.18 (e.g. 00e colony level: one labelling 0.82, the other 0.63).
4. **Invented content.** 81–85% of notes contain made-up details (berries, wasps, oaks). In gate C3 llama chose routes that do not exist 18–54% of the time.
5. **A second channel besides the trail.** 77–100% of notes state the trip time ("RT-D20, 4 ticks"). Agents can follow the story in the notes, not only the strength of the trail. This "duration leak" blurs what forgetting alone does.
6. **Format failures.** Up to 17% unreadable answers in single runs (rule: >10% = invalid run).

### 4.4 What did work

- The simulator: ants hit the textbook result every time (gates and blocks Z/Z2).
- llama does read content (gate 3a′) and responds to forgetting on average.
- The method: pre-registration, ant control, independent checker, fresh seeds. It stopped a false positive (the calib-00d pattern) from becoming a claim.

---

## 5. What we can and cannot say

**Can say:**
- "In a double-bridge colony, llama-3.1-8B agents at temperature 0.7 are 5–8× noisier than an ant rule run to run (over 100× when nothing changes) and cannot reliably hold a choice even when nothing changes."
- "Shorter trail memory pushes the llama colony toward the new better route on average, the same direction as ants, but not with the ants' sharp switch."
- "A sharp boundary seen in one run did not replicate on fresh starts."

**Cannot say:**
- That all small LLMs fail. Only llama-3.1-8B ran the full grid; others only ran gates (all failed the empty-board gate).
- That LLM agents use the ant mechanism. The trip-time leak in notes was never closed.
- That bigger or calibrated models would pass. Untested (Jev = calib-00f).

---

## 6. How it fits prior art

- **Li et al. 2026 (PRL):** a memory phase transition whose position is set by noise. Our result is consistent: more decision noise blurs the memory boundary.
- **Morimoto 2025 (p_c = μ):** exploration noise can replace forgetting. Our escape-without-forgetting check was 0/12 at TTL ∞ for llama, so its noise did not help it escape lock-in; it just made it unstable.
- **Talamali et al. 2021:** constrained communication helps swarm adaptation. Our llama notes are the opposite of constrained (rich, invented, duration-carrying text).
- Novelty check (03_prior_art): "forgetting coupled to feedback delay in an LLM colony with an ant control" was the only candidate-new claim. It remains untested cleanly, not refuted.

---

## 7. Method lessons (keep for every future proof)

1. **Calibrate success bars to the agent, not to ants.** The ant "0.8 = re-decided" line sat at llama's own ceiling.
2. **Measure the colony's own level first** (variant A) and gate on it.
3. **Always run the nature control** (ants) in the same grid.
4. **Fresh seeds for any confirmation.** Never pool the night that produced the idea.
5. **Independent checker before reading the builder's verdict.** It caught: Claude's own estimate errors, mislabelled invalid side, sum-vs-elapsed wall time, a checker that would have accepted old seeds.
6. **Close side channels** (here: trip times in notes) before claiming a mechanism.
7. **Small, honest no-results are cheap** (one night each) compared with a published false positive.

---

## 8. Prediction record (Claude optimist / pessimist vs mu)

- 00c: Claude 1/4 hits.
- 00d: pessimist closer on 3 of 5 items; n2.5 came in below both (5 vs 7 and 9).
- 00e: Claude pessimist closest on every item (verdict "no result" called correctly); mu predicted "in between".
- Pattern: optimism was consistently wrong about how stable the llama colony is.

---

## 9. Files

- Plans: `02_proofs/calib-00_double-bridge/BUILD_PLAN.md` (v1.6), `BUILD_PLAN_v1.7_calib-00d.md` (v1.7.8), `BUILD_PLAN_v1.8_calib-00e.md` (v1.8.2), `BUILD_PLAN_v1.9_calib-00f-jev.md` (next).
- Checkers: `verify_calib00c.py`, `verify_calib00d.py`, `verify_calib00e.py`, `verify_calib00f.py`.
- Results: `out/calib-00b/model_selection.csv`, `out/calib-00c/` (REPORT, VERIFY_claude, grid, gate files), `out/calib-00d/` (REPORT, verdict, VERIFY_claude_00d v2, grid), `out/calib-00e/` (REPORT, verdict, VERIFY_claude_00e, grid, z2.json).
- State: `loop_state.json`. Prior art: `03_prior_art/`, `SOURCES.md`.
