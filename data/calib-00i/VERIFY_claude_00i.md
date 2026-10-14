# calib-00i — Claude check (2026-10-14 19:26 Lisbon)

Inputs: 00i.log, a2_pick.json, a2_llama.csv (1,680 rows). Agree with mu on both gates.

A1 Jev — AGREE PASS. 0/120 minority at (7,0)+(0,7); 420/420 jev-1.13.0; parse-fail 0. API request fields: state, model, questions only. No temperature/seed/sampling → the host coin is the only noise knob for Part B.

A2 llama — AGREE DROP, with one scoping note.
- P(short) at full trail (7,0): 0.43–0.50; at (0,7): 0.47–0.53, at every temperature. llama ignores bare mark counts entirely; choice is position-driven (first-listed 0.65–1.00).
- Scope: A2 probed BARE MARK COUNTS (answer = {"route": ...}). Live llama runs (00c–00e) fed rich written notes, which llama does read (gate 3a′ 78–96%). So the finding is "llama cannot read a count-only trail at any temperature", not "lower temperature cannot help llama in the note-based world". That second question was not tested. My A2 spec copied the Jev probe format; my error.
- The variety check (distinct notes per 20) is not meaningful here: the probe asks for a route only, so 1–2 distinct answers is expected. The drop stands on ε̂ ≈ 1.0 alone.

Pool: jev_coin_pool.csv is in 02_proofs/ant-window/ since 18:56 (copy of jev_eps_pool.csv, 576 rows). 00j = Z5 + Jev coin 0.30 + 0.10.
