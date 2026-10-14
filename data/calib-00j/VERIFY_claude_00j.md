# calib-00j — Claude independent check (2026-10-14, after ALL DONE)

Input: grid.csv (96 rows). Agree: BOUNDARY RESTORED, dose NOT confirmed.

## Validity
- Z5 ants: 0.922 / 0.936 / 0.119 → OK.
- Every arm-cell has seeds 500–511 exactly once (J30: A, B2.5, B3 × 12; J10: B2.5, B3 × 12). 60/60 Jev valid, api_error 0, jev-1.13.0 throughout.
- Coin fire rate over two-option decisions: J30 0.303–0.305 in every cell; J10 0.102–0.103. Coin went in as planned.

## Verdict recomputed
- ε 0.30: AUC 1.000; B2.5 switched 12/12 (0.83–0.89); B3 locked 12/12 (max 0.222); A2.5 median 0.85. → RESTORED.
- ε 0.10: B2.5 10/12 switched (0.92–0.97), 2 locked (s501 0.022, s510 0.053); B3 12/12 locked (max 0.079). AUC = 127/144 = 0.882 > 0.75 → dose NOT confirmed.

## Things to know before interpreting
1. At ε 0.30, A2.5 and B2.5 give IDENTICAL last-50 values for every seed (e.g. s500 0.8208 both). Not a bug as far as I can see: trips are 4 or 8 ticks so all departures fall on multiples of 4, the coin is seeded per (seed, agent, tick), and Jev's argmax is fixed once the trail is unanimous. Once both runs lock on short, they follow the same coin stream. Consequence: last-50 ≈ 1 − ε/2 when locked short and ≈ ε/2 when locked long. The real signal is WHICH route the colony ends on, not the decimals.
2. The simulator was wrong again at low noise. It predicted ε 0.10 would mostly stay frozen (B2.5 median 0.05, 17% switch). Live: 10/12 switched. The real threshold for Jev is below 0.10. My "step-like deciders need ~6× ant noise" claim is NOT supported.
3. At ε 0.10 the memory boundary still shows: TTL 2.5 switches 10/12, TTL 3 locks 12/12. With a little host exploration, Jev's colony separates the two memory lengths the way ants do. Post-hoc reading; the pre-registered verdict is "RESTORED only".

## Scorecard
Sim-if-true: RESTORED + DOSE 70% (wrong). Unconditional: Claude 45 / 10 / 20 / 25; mu 40 / 10 / 20 / 30. Outcome RESTORED only: both gave it 10%. Neither called it; the miss is the dose, same for both.

## Wording (agree with mu)
"A host coin on argmax Jev (30%, and mostly already 10%) restored the TTL 2.5 vs 3 split in this world." Not a Jev temperature. Not the ant mechanism. The coin does the exploring; Jev does the following; the trail memory decides who wins.
