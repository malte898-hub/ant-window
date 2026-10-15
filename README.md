# ant-window

Jev is a product of TypeSafe AI. This project is independent and not affiliated with or endorsed by TypeSafe.

## Question

Can a colony of AI agents on a fading shared trail switch to a better new route when memory is short, and stay locked when memory is long (Deneubourg double bridge)?

## Result (host coin on argmax Jev; not a Jev temperature)

| id | finding |
|---|---|
| 00g | Jev coin 0: no switch. Simulator REFUTED 0/5. |
| 00j | coin 0.30: 12/12 switch, 12/12 lock (BOUNDARY RESTORED). coin 0.10: 10/12, AUC 0.882 (dose not confirmed). |
| 00k | minimum splitting dose = 0.05. Explorer model HOLDS. 0.02 PARTIAL 6/12. |

See WRITEUP.md. Llama loop: WRITEUP_llama-loop.md.

## Reproduce checkers

```
python3 -I checkers/verify_calib00g.py data/calib-00g/grid.csv
python3 -I checkers/verify_calib00j.py data/calib-00j/grid.csv
python3 -I checkers/verify_calib00k.py data/calib-00k/grid.csv
```

Filed outputs (this snapshot):

00g  SIMULATOR REFUTED — hits 0/5
     Ants A2.5 0.935 · B2.5 0.933 · B3 0.139 OK

00j  BOUNDARY RESTORED (dose not confirmed: eps0.10 AUC>0.75)
     0.30 switched 12/12 locked 12/12 · 0.10 switched 10/12 locked 12/12

00k  minimum splitting dose = 0.05 · explorer model: MODEL HOLDS
     0.02 PARTIAL 6/12 · 0.05 SPLIT 10/12 · 0.10 SPLIT 11/12

## Jev prompt

docs/jev_prompt_example.txt — route labels only in the 7 marks. No weights, ticks, duration, agent id, or note text.

## Licences

Code: MIT (LICENSE). Docs, plans, data: CC BY 4.0 (LICENSE-docs).

## Runners

src/ overnight_00g/00j/00k.py. Set API_KEY in the environment for Jev HTTP. No emulator of Jev is in this tree.
