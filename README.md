# The Ant That Changed Its Mind

Swarms of AI agents that share notes get stuck when the world changes. In a classic ant
experiment rebuilt with 30 AI agents, the swarm adapted only when old notes faded fast
enough and about 5% of decisions were made at random.

| Test                                  | Runs        | Short memory: found the better path                        | Long memory: stayed stuck |
| ------------------------------------- | ----------- | ---------------------------------------------------------- | ------------------------- |
| Small AI model on its own             | 3 nights    | No clear pattern; it mostly picked the first-listed option | No clear pattern          |
| Second AI model on its own            | 72          | 0 of 24                                                    | 24 of 24                  |
| Second model + 30% coin               | 36          | 12 of 12                                                   | 12 of 12                  |
| Second model + 10% coin (two batches) | 48          | 21 of 24                                                   | 24 of 24                  |
| Second model + 5% coin                | 24          | 10 of 12                                                   | 12 of 12                  |
| Second model + 2% coin                | 24          | 6 of 12 (a toss-up)                                        | 12 of 12                  |
| Simulated ants (reference)            | every batch | Every time                                                 | Every time                |

- Plain-language summary: [SUMMARY.md](SUMMARY.md)
- Full technical write-up: [WRITEUP.md](WRITEUP.md) (and [WRITEUP_llama-loop.md](WRITEUP_llama-loop.md))
- Reproduce the verdicts: see [Reproduce](#reproduce) below

## Reproduce

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

## Repository map

[plans/](plans) · [checkers/](checkers) · [src/](src) · [data/](data) · [prior_art/](prior_art) · [docs/](docs)

## Licences

Code: MIT (LICENSE). Docs, plans, data: CC BY 4.0 (LICENSE-docs).

Jev is a product of TypeSafe AI. This project is independent and not affiliated with or endorsed by TypeSafe.
