# Following plus a little noise: when an AI-agent colony adapts like ants

> Main limitation: marks were shown as a list sorted strongest-first, so list order and trail strength are not yet separated (§7; a shuffled-list run is in progress).

Swarms project, 2026-10-14 evening, from run files, Claude's independent checks.
Status: DRAFT v2. Covers calib-00f to calib-00k (minimum dose added 2026-10-14 late evening).
Companion: `calib-00/WRITEUP_llama-loop.md` (the earlier llama loop).

---

## 1. Summary

We asked whether a colony of AI agents, sharing a fading trail of marks, can do what ants do on the classic double bridge: switch to a better new route when trail memory is short, and stay stuck when it is long.

On their own, two AI models failed in opposite ways:
- **llama-3.1-8B is too noisy.** With bare trail marks it ignores the trail (at a full trail it picks the marked route only about half the time, at every temperature). It mostly picks whichever route is listed first.
- **Jev (jev-1.13.0, API) never explores on a settled trail.** It always picks its top-rated route, and on a unanimous trail that is the crowd's route: 0 minority picks in 63,733 live decisions. The colony freezes on its first habit, whatever the memory length (00g: 0/48 runs switched).

Adding exploration from outside fixed it. With a host coin that makes 30% of decisions at random, and Jev making the rest:
- short memory (TTL 2.5) switched to the new route in **12/12** runs;
- long memory (TTL 3) stayed on the old route in **12/12** runs.

That is the ant result. It holds down to a **5% coin** (marks shown sorted strongest-first) (10/12 switched, 12/12 stayed; pre-registered, fresh seeds). At 2% it is half-and-half (6/12). The 10% result replicated (11/12).

**The design rule this suggests:** let AI agents follow the shared memory; supply a small dose of exploration from the system, not from the model; tune how fast the memory fades.

---

## 2. The test

- **World (double bridge; Goss et al. 1989).** Nest, food, two routes. Short: round trip 4 ticks. Long: 8 ticks. 30 agents, 200 ticks.
  - Variant A: both routes open from the start.
  - Variant B: only the long route until tick 40, then the short one opens. Can the colony change its mind?
- **Trail.** Each returning agent leaves a mark (weight 1, plus reinforcement shared across the marks it read). Marks fade by exp(−1/TTL) per tick and drop below 0.05. Agents read the 7 strongest marks.
- **Memory length.** TTL 2.5 (marks fade before a long round trip completes) vs TTL 3 (they survive it).
- **Ant prediction, confirmed every run.** Real-ant rule (Deneubourg, k 20, n 2): B at TTL 2.5 switches, B at TTL 3 stays. Ant control medians in 00g and 00j (Z4, Z5): A 0.922–0.935, B2.5 0.933–0.936, B3 0.119–0.139. The ant control has passed in every run so far.
- **Measure.** Share of departures on the short route in the last 50 ticks. "Switched" ≥ 0.8. "Stayed" ≤ 0.3.

---

## 3. What each AI agent did on its own

### 3.1 llama-3.1-8B (calib-00c to 00e, 00i)
- With rich written notes (00c–00e): 5–8× noisier than ants run to run. The direction matched ants on average, but no clean boundary. See the llama write-up.
- With bare marks (00i, 1,680 calls, temperatures 0.7 / 0.4 / 0.2 / 0.0): at a full trail it picks the marked route only ~50% of the time. First-listed bias 0.65–1.00. Turning temperature down does not make it read the trail.
- Note: 00i tested bare marks only. Whether low temperature helps llama read written notes was not tested.

### 3.2 Jev (calib-00f to 00i)
- Jev's API returns stated probabilities (for example "2% the other route" at a full trail). Its actual pick is always the top one: 210/210 probe answers; 0/120 at full trails in the 00i re-probe; 0/63,733 live. The API has no temperature or seed setting.
- **00g (live colony, 72 runs).** A: all 24 runs locked on short (1.000). B: all 48 runs locked on long (0.000), at both memory lengths. Not one short pick after the bridge opened.
- A simulator that treated Jev's stated 2% as a real coin flip predicted switching (~0.80). It was refuted 0/5. Stated confidence is not behaviour.
- On mixed trails (only seen once a coin added explorers, 00k) Jev is not a simple majority follower: it already favours the short route at 2–3 of 7 marks (§5.3).

---

## 4. The fix: host coin plus Jev (calib-00j)

Each decision: with probability ε the host's random generator picks a route at random (no Jev call); otherwise Jev's top choice. Seeds 500–511. Pre-registered (v4.0.1), independent checker.

| Coin ε | B, TTL 2.5 switched | B, TTL 3 stayed | Verdict |
|---|---|---|---|
| 0 (00g) | 0/24 | 24/24 | frozen |
| 0.10 | 10/12 | 12/12 | dose check failed (AUC 0.88 > 0.75): already mostly works |
| 0.30 | 12/12 | 12/12 | **BOUNDARY RESTORED** (AUC 1.00) |

- Validity: ants 0.922 / 0.936 / 0.119. 60/60 Jev runs valid, no API errors, coin fired 30.3–30.5% and 10.2–10.3% as set.
- Cost of the coin: in A the colony settles at ~0.85 instead of 1.00 (about 1 − ε/2). Exploration costs efficiency in a static world.
- Quirk: once settled, the end score is set by the coin alone (A and B2.5 give identical values per seed at ε 0.30). What matters is which route the colony ends on.
- Prediction record: my simulator said 10% would mostly stay frozen. Live: 10/12 switched. The simulator was wrong twice and has been retired.

---

## 5. Interpretation

### 5.1 What this shows
- An AI colony can show the ant memory boundary once exploration is supplied from outside. With exploration, memory length decides the outcome: short memory adapts, long memory stays stuck.
- The two failures are opposite ends of one dial: llama too much (and the wrong kind: position bias), Jev none. Ants sit in between.
- The forgetting question from the llama loop is answered from a different angle: forgetting matters for AI colonies too, but only when something explores.

### 5.2 What it does not show
- That Jev "thinks like an ant", or has any temperature. The host coin does the exploring.
- Anything beyond this toy world: two routes, one model, 30 agents, 12 runs per setting.

### 5.3 Mechanism (from the 00k decision log; post hoc)
- A coin-driven explorer goes short; its mark returns in 4 ticks.
- **Long memory:** the explorer's mark never makes it into the 7 marks agents read. Old long marks fade too slowly and stay heavier. In all 20,792 of Jev's own decisions after the bridge opened at TTL 3, it saw 0 short marks. So it never switched.
- **Short memory:** old long marks fade fast enough for the fresh short mark to get into view. Then Jev itself recruits: its own picks of the short route were 13% at 1 of 7 short marks, 46% at 2 of 7, 98% at 3 of 7, 100% at 4+ of 7. That is a threshold, positive-feedback response, like ants. It is not a pure majority vote: Jev switches at about 2 of 7.
- So the memory boundary works through what fits in the 7-mark window, and the coin only has to get one mark in.
- A simple rule, P(switch) = 1 − (1 − coin/2)^W, fits all six live points with a window W ≈ 52 decisions.
- What Jev sees (confirmed from the run code, `docs/jev_prompt_example.txt`): the 7 marks as route labels only, listed strongest first. No weight, age, trip time, agent id or note text; the two route options are shuffled per call. So there is no trip-time leak. The only strength cue is list order: fresh short marks sit at the top, and Jev's early pull toward them (e.g. 2 short of 7 listed first → stated 0.74 short, picked short) reads like a primacy effect on an ordered list. That is still trail information (order = strength), the same signal ants use, but delivered through position rather than numbers.

### 5.4 Minimum dose (calib-00k)
Pre-registered (v4.2), seeds 600–611, ants 0.938 / 0.927 / 0.113, 0 invalid.

| Coin | Short memory switched | Long memory stayed | Verdict |
|---|---|---|---|
| 0.02 | 6/12 | 12/12 | PARTIAL (half-and-half) |
| 0.05 | 10/12 | 12/12 | SPLIT |
| 0.10 (replicate) | 11/12 | 12/12 | SPLIT |

- **Minimum splitting dose: 5%** (between 2% and 5%). Predicted beforehand: Claude 5%, mu 10%.
- Explorer rule HOLDS (all three counts inside the pre-registered ranges, at their upper edges).
- Long memory never broke lock at any dose (60/60 across 00j and 00k).
- Doses share coin draws per seed (paired comparison).

---

## 6. Prior art and what may be new

Literature check run 2026-10-14 (web search, about 15 queries; not exhaustive; paywalled venues not read), plus a GitHub scan (410 repos via the GitHub API repo search; code search not yet run). No study or repo found that runs this experiment. Several tools ship fading "pheromone" memory for AI agents (e.g. Stigmergy-mcp, PheroPath, scentline) without evidence on decay or exploration settings. The ingredients are known:

| Work | What it shows | Overlap with us |
|---|---|---|
| Goss et al. 1989 (double bridge, short vs long branch); Deneubourg et al. 1990 (equal branches, choice rule); Dorigo & Stützle (ACO, MMAS) | Double bridge; evaporation and minimum trail levels keep ant colonies adaptive | The ant rules and the design idea are textbook |
| Krishnamurthy et al. 2024 (NeurIPS) | Single LLMs fail to explore in bandit tasks without external help | LLMs under-explore: known |
| Choi et al. 2026 (arXiv 2607.11250, "Multi-Agent LLMs Fail to Explore Each Other") | LLM agents commit early to one peer; prompting cannot fix it; an algorithmic bandit layer (MACE) can | Closest in spirit: host-side exploration fixes LLM commitment. Peer selection, no trail, no forgetting, no ant control |
| Jimenez-Romero, Yegenoglu & Blum 2025 (arXiv 2503.03800) | LLM-driven ants with pheromones in NetLogo; exploration poor until a "random" action was added; LLM+rule hybrids did well | Closest setup: LLM ants with pheromones. No route switch, no evaporation test, no dose |
| Cho et al. 2025 (Herd behaviour in LLM multi-agent systems); Zomer & De Domenico 2026 (npj AI) | LLM agents herd and converge prematurely | LLM conformity: known |
| Rodriguez 2026 (arXiv 2601.08129) | Temporal decay helps LLM agents coordinating through a shared artifact (on/off ablation) | Decay helps LLM coordination: suggested, not swept |
| Rahman, Schranz & Hayat 2025 (arXiv 2506.14496; code Atta66/swarms-rulebased-vs-llms) | LLM agents run a two-path (short/long) ant colony with pheromones; exploration only via a prompt schedule; an early prompt gave 0% exploration | Closest LLM two-path setup. Static paths: no late shortcut, no memory sweep, no live ant control, no dose |
| Meinhold 2026 (GitHub nickmeinhold/aco-swarm-research) | ε-greedy heuristic ants plus an LLM "queen" on file-based pheromones; n = 1 toy runs; evaporation sweep planned | Same spirit (host randomness + LLM); not a switching test |
| roanbrasil/agentic-superorganisms (GitHub, 2026) | Rule-based double bridge with a late shortcut; no evaporation → never switches | Our ant-side result, independently; no LLM |

**Candidate-new (modest):**
1. The ant memory boundary (TTL 2.5 switches, TTL 3 stays) reproduced in an LLM-agent colony, against a live ant control, and shown to depend on externally supplied exploration.
2. Two opposite failures of LLM agents measured in the same trail world: too noisy and wrong (llama), deterministic and frozen (Jev).
3. Method finding: an LLM's stated probabilities are not its choice rate (Jev: states 2%, does 0%). Simulators built on stated confidence mispredict colony behaviour.
4. Dose: about 5% outside exploration is enough; at 2% it is a coin toss. A one-parameter "first explorer" rule predicts the dose curve. With marks shown sorted strongest-first; not yet tested with a shuffled list.
5. Mechanism: the memory boundary acts through the agents' limited reading window (top 7 marks); the LLM's own response to mixed trails is a threshold recruitment curve.

**Not new:** that LLMs under-explore; that random exploration or evaporation keeps swarms adaptive; that LLM agents herd.

---

## 7. Limits

- One world, two routes, one deterministic model (Jev) for the positive result.
- The coin is external, so the result is about system design, not model behaviour.
- llama was tested with bare marks in 00i; its note-reading under low temperature is untested.
- Jev reads mark strength only through list order (primacy). A version that shuffles the 7 marks would separate trail strength from position.
- Calls used the model alias `jev-latest`; every response reported jev-1.13.0. A future alias change could change results.
- 12 runs per setting: counts like 10/12 have wide uncertainty.
- The literature search was a web search, not a systematic review.

---

## 8. Method lessons (added to the llama-loop list)

1. Measure what a model picks, not what it says it would pick.
2. A simulator that fits one point can still miss the next; register it, test it, retire it when it fails.
3. Keep the ant control in every run (it has passed every time).
4. Read the raw grid before the builder's verdict: it caught the call-count error, the identical-score quirk, and the probe-format limit.

---

## 9. Run record

| Run | Question | Result |
|---|---|---|
| 00f | One Jev shot with notes | Void (sense check failed) |
| 00g | Does a probe-based simulator predict live Jev? | REFUTED 0/5. Jev colony frozen |
| 00i | Re-probe: real pick rates | Jev picks top choice (0/120). llama ignores marks (dropped) |
| 00j | Does a host coin restore the ant boundary? | RESTORED at 30%; 10% already mostly works |
| 00k | Minimum dose | 5% splits (10/12); 2% half (6/12); 10% replicated (11/12) |

Files: plans `BUILD_PLAN_v3.1.1_live-jev.md`, `BUILD_PLAN_v4.0.1_noise-bracket.md`, `BUILD_PLAN_v4.2_min-dose.md`; checkers `verify_calib00g.py`, `verify_calib00j.py`, `verify_calib00k.py`; results and Claude checks in `out/calib-00g`, `out/calib-00i`, `out/calib-00j`, `out/calib-00k`.

---

## Sources

- Goss, Aron, Deneubourg, Pasteels (1989). Self-organized shortcuts in the Argentine ant. Naturwissenschaften 76:579–581. https://doi.org/10.1007/BF00462870
- Deneubourg, Aron, Goss, Pasteels (1990). The self-organizing exploratory pattern of the Argentine ant. Journal of Insect Behavior 3:159–168. https://doi.org/10.1007/BF01417909
- Choi, Li, Li, Wang, Li (2026). Multi-Agent LLMs Fail to Explore Each Other. https://arxiv.org/html/2607.11250
- Jimenez-Romero, Yegenoglu, Blum (2025). Multi-Agent Systems Powered by Large Language Models: Applications in Swarm Intelligence. https://arxiv.org/abs/2503.03800
- Krishnamurthy et al. (2024). Can Large Language Models Explore In-Context? https://arxiv.org/html/2403.15371v3
- Cho et al. (2025). Herd Behavior: Investigating Peer Influence in LLM-based Multi-Agent Systems. https://arxiv.org/html/2505.21588v1
- Zomer, De Domenico (2026). Unraveling the emergence of collective behavior in networks of cognitive agents. npj Artificial Intelligence. https://www.nature.com/articles/s44387-026-00091-5
- Rodriguez (2026). Emergent Coordination in Multi-Agent Systems via Pressure Fields and Temporal Decay. https://arxiv.org/html/2601.08129v3
- Rahman, Schranz, Hayat (2025). LLM-Powered Swarms: A New Frontier or a Conceptual Stretch? https://arxiv.org/abs/2506.14496
- Pal, Wang, Buehler (2026). SwarmWorld: Stigmergic technological evolution in societies of language-model agents. https://arxiv.org/html/2608.26081v1
- Dorigo, Di Caro, Gambardella (1999). Ant algorithms for discrete optimization. https://staff.washington.edu/paymana/swarm/dorigo99-al.pdf
