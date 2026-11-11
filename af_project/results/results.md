
### main (no self-attacks), N=1000 per p

| p | strategyproof | cond. holds (walk) | cond. holds (simple path) | cond holds & NOT SP | SP & cond fails (walk) | SP & cond fails (simple) |
|---|---|---|---|---|---|---|
| 0.15 | 632/1000 = 0.632 | 118 | 120 | 0 (walk) / 0 (simple) | 514 | 512 |
| 0.25 | 317/1000 = 0.317 | 31 | 33 | 0 (walk) / 0 (simple) | 286 | 284 |
| 0.35 | 126/1000 = 0.126 | 4 | 5 | 0 (walk) / 0 (simple) | 122 | 121 |

Strategyproof instances whose condition FAILS (walk reading), classified by the kind of deviation they contain (swap / loss-only / inert, defined in analyse.py):

| p | #SP & cond fails | swap | loss-only | inert |
|---|---|---|---|---|
| 0.15 | 514 | 445 | 69 | 0 |
| 0.25 | 286 | 243 | 43 | 0 |
| 0.35 | 122 | 103 | 19 | 0 |

### variant (self-attacks allowed), N=1000 per p

| p | strategyproof | cond. holds (walk) | cond. holds (simple path) | cond holds & NOT SP | SP & cond fails (walk) | SP & cond fails (simple) |
|---|---|---|---|---|---|---|
| 0.15 | 535/1000 = 0.535 | 84 | 99 | 0 (walk) / 0 (simple) | 451 | 436 |
| 0.25 | 254/1000 = 0.254 | 12 | 16 | 0 (walk) / 0 (simple) | 242 | 238 |
| 0.35 | 101/1000 = 0.101 | 1 | 1 | 0 (walk) / 0 (simple) | 100 | 100 |

Strategyproof instances whose condition FAILS (walk reading), classified by the kind of deviation they contain (swap / loss-only / inert, defined in analyse.py):

| p | #SP & cond fails | swap | loss-only | inert |
|---|---|---|---|---|
| 0.15 | 451 | 330 | 121 | 0 |
| 0.25 | 242 | 155 | 87 | 0 |
| 0.35 | 100 | 47 | 53 | 0 |