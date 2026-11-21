# Part 1 — Modeling: base CFL and Track C extension

Team 4: seeds 401, 402, 403; capacity ratios 2, 4, 8; family S (20 sites, 80 customers).

| File | Contents |
|---|---|
| `cfl_data.py` | instance generator (course starter, unchanged) |
| `cfl_model.py` | `build_cfl(inst)` builds (CFL); `build_cfl_c(inst)` builds the Track C extension |
| `part1.py` | solves the LP relaxation and the IP of (CFL) and Track C on the 9 family S instances |
| `results/part1.csv` | output of `part1.py` |

## Track C: modular capacity

Each site opens at most one module: small (`f[i]`, `q[i]`) or large (`f2[i]`, `q2[i]`),
where the large module has twice the capacity at 1.6 times the fixed cost.

```
min  sum_i (f_is y_is + f_il y_il) + sum_i sum_j c_ij x_ij
s.t. sum_i x_ij = d_j                         for j in J
     sum_j x_ij <= q_is y_is + q_il y_il      for i in I
     y_is + y_il <= 1                         for i in I
     y_is, y_il in {0, 1},  x_ij >= 0
```

In `cfl_model.py`, `y[i, 's']` and `y[i, 'l']` are the module variables and
`M.one_module` is the at-most-one-module constraint. Both builders also accept
`strong=True`, which adds `M.strong`: x_ij <= d_j y_i (CFL+) or
x_ij <= d_j (y_is + y_il) (Track C). `part1.py` does not use it.

## Results (`results/part1.csv`)

Columns: `z_lp`, `z_ip` (LP and IP values), `gap_pct` = 100 (z_ip − z_lp) / z_ip,
`frac_y` (fractional y in the LP solution), `open` (sites open in the IP),
`large` (sites with the large module), `nodes`, `time_s`.

Averages over the three seeds:

| Ratio | CFL gap | Track C gap | Track C IP vs CFL | Large modules |
|---|---|---|---|---|
| 2 | 3.1% | 8.8% | about 11% cheaper | 4 per instance |
| 4 | 9.4% | 21.4% | 0–3% cheaper | 0–2 |
| 8 | 24.3% | 34.3% | equal | 0 |

- Track C's IP value is never above CFL's, since it can open everything CFL can.
- Large modules pay off when capacity is tight (ratio 2); with loose capacity (ratio 8) the optimum uses only small modules.
- Track C's LP relaxation is weaker than CFL's: per unit of capacity the large module costs 0.8 times the small one, so the LP opens fractions of large modules. Its gaps are wider and branch and bound needs more nodes.

## Reproduce

```
python -m pip install pyomo gurobipy
cd "Part 1"
python part1.py        # prints the table and writes results/part1.csv
```

All Gurobi runs use Presolve=0, Cuts=0, Heuristics=0 (`GUROBI_SETTINGS` in `cfl_model.py`).
Family S fits in the size-limited pip license; family L needs the academic license.
`build_cfl_c` uses the dict `|` operator, so it needs Python 3.9 or later.
