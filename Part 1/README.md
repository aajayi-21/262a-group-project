# Part 1 — Modeling and a stronger formulation

Team 4: seeds 401, 402, 403; capacity ratios 2, 4, 8; family S (20 sites, 80 customers).

| File | Contents |
|---|---|
| `cfl_data.py` | instance generator (course starter, unchanged) |
| `cfl_model.py` | (CFL) in Pyomo; `build_cfl(inst, strong=True)` builds (CFL+), which adds x_ij <= d_j y_i |
| `part1.py` | solves the LP relaxation and the IP of (CFL) and (CFL+) on the 9 family S instances |
| `results/part1.csv` | output of `part1.py` |

## Reproduce

```
python -m pip install pyomo gurobipy
cd "Part 1"
python part1.py        # prints the table and writes results/part1.csv
```

All Gurobi runs use Presolve=0, Cuts=0, Heuristics=0 (`GUROBI_SETTINGS` in `cfl_model.py`).
Family S fits in the size-limited pip license; family L needs the academic license.

## Still to do

- Extension track: formulation and code (`TODO (Part 1(a))` in `cfl_model.py`)
