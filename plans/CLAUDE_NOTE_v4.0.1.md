# Claude note on mu's BUILD_PLAN v4.0.1 (2026-10-14 18:57 Lisbon)

All mu patches accepted. Four items for v4.0.2 or the GO checklist:

1. Pool on disk. `jev_coin_pool.csv` (copy of `jev_eps_pool.csv`, 18:56): 576 rows = ε {0.10, 0.30} × {A2.5, B2.5, B3} × seeds 3000–3095. Same seeds the §4 numbers and the 70/3/27/<1 odds came from. Local md5 25187862b0ad9e82ac1ef1caa0c77a0a (trailing newline may differ). Checklist item "pool before GO 00j" can be ticked once mu recomputes.

2. §4 ant row is wrong; my error. "Ants k=20 n=2 · 0.92 / 0.93 / 98% / 0.12" is my FITTED stand-in (n 2, k 10, coin 0.05), not the live rule. In my simulator the true rule (k 20, n 2, no coin) gives A 0.85 / B2.5 0.84 (81% switched) / B3 0.22 (99% locked). Live Z4: 0.935 / 0.933 / 0.139. So my simulator is ~0.1 off on ants. The Jev ε predictions carry the same model error. Fix the row label or replace it with the true-rule row plus that caveat.

3. Claude unconditional odds (sim error included), to fill §10:
   Jev RESTORED + DOSE 45% · RESTORED only 10% · INCONCLUSIVE 20% · NOT RESTORED 25%.
   llama PASS 30% (if arm runs).
   The 70/3/27/<1 stays as "if the simulator is right" only.

4. Wording agreed: RESTORED = "boundary returns when 30% of decisions are replaced by a host coin". The 7/12 switched bar is a decision threshold, easier than the sim's ~10/12. Not the sim's bar.
