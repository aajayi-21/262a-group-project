# Part 1 — Modeling: CFL, CFL+, CFL-C and CFL-C+

Team 4: seeds 401, 402, 403; capacity ratios 2, 4, 8; family S (20 sites, 80 customers).

| File | Contents |
|---|---|
| `cfl_data.py` | instance generator (course starter, unchanged) |
| `cfl_model.py` | `build_cfl(inst)` builds (CFL); `build_cfl_c(inst)` builds (CFL-C), the Track C extension; `strong=True` gives the "+" version of either |
| `part1.py` | solves the LP relaxation and the IP of all four formulations on the 9 family S instances |
| `results/part1_cfl.csv` | (CFL) and (CFL+) |
| `results/part1_cfl_c.csv` | CFL-C and CFL-C+ |
| `part1_cutoff.py` | shows each strong formulation cuts off the optimum of the weak LP relaxation |
| `results/part1_cutoff.csv` | output of `part1_cutoff.py`: one point per comparison |

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
`M.one_module` is the at-most-one-module constraint.

## The "+" formulations

`strong=True` adds `M.strong`, one row per site and customer:

- CFL+: x_ij <= d_j y_i
- CFL-C+: x_ij <= d_j (y_is + y_il)

Each is valid for the integer program (an open site never ships a customer more
than its demand), so the IP value is unchanged, but it cuts off fractional LP
points where y is set to (flow / capacity). It adds |I| x |J| = 1,600 rows on family S.

`part1_cutoff.py` exhibits one such point per comparison (seed 401, ratio 4).
In both weak LP optima, site 6 ships 71 units, all 35 units of customer 68's
demand among them, while the LP opens it only as far as capacity requires:

| Comparison | Weak LP optimum at site 6 | Strong row (6, 68) | LP value, weak → strong |
|---|---|---|---|
| CFL vs CFL+ | y_6 = 71/449 = 0.1581 | 35 ≤ 35 × 0.1581 = 5.53, violated | 47,398.67 → 51,981.17 |
| CFL-C vs CFL-C+ | y_6s = 0, y_6l = 71/898 = 0.0791 | 35 ≤ 35 × 0.0791 = 2.77, violated | 40,744.82 → 51,830.45 |

Each point is feasible for the weak LP relaxation but not for the strong one.
In `results/part1_cutoff.csv`, `strong_rhs` is d_j times the open level of site i
at that point, and `weak_optimum_y` lists every nonzero y of the point.

## Results

Columns in both files: `z_lp`, `z_ip` (LP and IP values),
`gap_pct` = 100 (z_ip − z_lp) / z_ip, `frac_y` (fractional y in the LP solution),
`open` (sites open in the IP), `large` (sites with the large module, always 0 for CFL),
`nodes` (branch-and-bound nodes), `time_s` (IP solve time).

Average gap over the three seeds:

| Ratio | CFL | CFL+ | CFL-C | CFL-C+ |
|---|---|---|---|---|
| 2 | 3.1% | 1.6% | 8.8% | 1.7% |
| 4 | 9.4% | 0.7% | 21.4% | 1.6% |
| 8 | 24.3% | 0.4% | 34.3% | 0.7% |

- Each "+" formulation has the same IP value as its base formulation, and a higher LP bound.
- The weak gap grows with the capacity ratio, because the capacity row lets the LP set y_i = flow / q_i and pay only that fraction of the fixed cost. The "+" rows tie y to d_j instead of q_i, so their gap stays small.
- CFL-C's IP value is never above CFL's. Large modules pay off when capacity is tight (4 per instance at ratio 2); at ratio 8 the optimum uses only small modules.
- CFL-C's base LP is weaker than CFL's: per unit of capacity the large module costs 0.8 times the small one, so the LP opens fractions of large modules. CFL-C+ closes most of that gap, and branch and bound needs far fewer nodes (for example 929 → 95, 839 → 67).
- The "+" formulations take about 2–3× longer per IP solve because of the extra rows; all runs are under 0.25 s.

## Reproduce

```
python -m pip install pyomo gurobipy
cd "Part 1"
python part1.py        # prints both tables and writes results/part1_cfl.csv, results/part1_cfl_c.csv
python part1_cutoff.py # writes results/part1_cutoff.csv
```

All Gurobi runs use Presolve=0, Cuts=0, Heuristics=0 (`GUROBI_SETTINGS` in `cfl_model.py`).
Family S fits in the size-limited pip license; family L needs the academic license.
`build_cfl_c` uses the dict `|` operator, so it needs Python 3.9 or later.
