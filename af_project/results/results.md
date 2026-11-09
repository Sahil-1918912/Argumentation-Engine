
### main (no self-attacks), N=1000 per p

| p | strategyproof | cond. holds (walk) | cond. holds (simple path) | cond holds & NOT SP | SP & cond fails (walk) | SP & cond fails (simple) |
|---|---|---|---|---|---|---|
| 0.15 | 632/1000 = 0.632 | 118 | 120 | 0 (walk) / 0 (simple) | 514 | 512 |
| 0.25 | 317/1000 = 0.317 | 31 | 33 | 0 (walk) / 0 (simple) | 286 | 284 |
| 0.35 | 126/1000 = 0.126 | 4 | 5 | 0 (walk) / 0 (simple) | 122 | 121 |

SP instances with failing condition: how many contain a real *swap* deviation (hiding changes which own arguments are accepted, utility equal)?

- p=0.15: 445/514 have a swap deviation; 69 have none
- p=0.25: 243/286 have a swap deviation; 43 have none
- p=0.35: 103/122 have a swap deviation; 19 have none

### variant (self-attacks allowed), N=1000 per p

| p | strategyproof | cond. holds (walk) | cond. holds (simple path) | cond holds & NOT SP | SP & cond fails (walk) | SP & cond fails (simple) |
|---|---|---|---|---|---|---|
| 0.15 | 535/1000 = 0.535 | 84 | 99 | 0 (walk) / 0 (simple) | 451 | 436 |
| 0.25 | 254/1000 = 0.254 | 12 | 16 | 0 (walk) / 0 (simple) | 242 | 238 |
| 0.35 | 101/1000 = 0.101 | 1 | 1 | 0 (walk) / 0 (simple) | 100 | 100 |