"""Part 1: the strong rows cut off the optimum of the weak LP relaxation.

    python part1_cutoff.py

For each comparison, (CFL) vs (CFL+) and Track C vs Track C+, on one instance
(seed 401, ratio 4), the script solves the weak LP relaxation and takes its
optimum (x*, y*).  That point is feasible for the weak LP; the script finds
the strong row it violates most,
    CFL+:      x_ij <= d_j y_i
    Track C+:  x_ij <= d_j (y_is + y_il),
which shows the strong formulation cuts the point off.  It also solves the
strong LP relaxation, for its value.

Writes results/part1_cutoff.csv, one row per comparison.
"""
import csv
import os
import pyomo.environ as pyo
from cfl_data import family
from cfl_model import build_cfl, build_cfl_c, solve

SEED, RATIO = 401, 4
COMPARISONS = (('CFL vs CFL+', build_cfl), ('TrackC vs TrackC+', build_cfl_c))


def run():
    inst = family('S', ratio=RATIO, seed=SEED)
    rows = []
    for name, build in COMPARISONS:
        track_c = build is build_cfl_c
        weak = build(inst, relax=True)
        z_weak = solve(weak)[0]
        z_strong = solve(build(inst, relax=True, strong=True))[0]

        def open_level(i):       # y_i, or y_is + y_il for Track C
            return pyo.value(weak.y[i, 's'] + weak.y[i, 'l']) if track_c else pyo.value(weak.y[i])

        # the strong row the weak optimum violates most
        i, j = max(((i, j) for i in inst['I'] for j in inst['J']),
                   key=lambda ij: pyo.value(weak.x[ij]) - inst['d'][ij[1]] * open_level(ij[0]))
        x, d, y = pyo.value(weak.x[i, j]), inst['d'][j], open_level(i)
        load = sum(pyo.value(weak.x[i, jj]) for jj in inst['J'])
        y_point = {k: round(pyo.value(v), 4) for k, v in weak.y.items() if pyo.value(v) > 1e-6}
        rows.append(dict(
            comparison=name, seed=SEED, ratio=RATIO,
            z_lp_weak=round(z_weak, 2), z_lp_strong=round(z_strong, 2),
            site=i, customer=j, x_ij=round(x, 2), d_j=d,
            y_i=round(y, 4) if not track_c else '',
            y_is=round(pyo.value(weak.y[i, 's']), 4) if track_c else '',
            y_il=round(pyo.value(weak.y[i, 'l']), 4) if track_c else '',
            load_i=round(load, 2),
            capacity=inst['q2'][i] if track_c else inst['q'][i],
            strong_rhs=round(d * y, 2), violated=x > d * y + 1e-6,
            weak_optimum_y=y_point))
    return rows


if __name__ == '__main__':
    rows = run()
    os.makedirs('results', exist_ok=True)
    with open('results/part1_cutoff.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        y = f"y_{r['site']} = {r['y_i']}" if r['y_i'] != '' else \
            f"y_{r['site']},s + y_{r['site']},l = {r['y_is']} + {r['y_il']}"
        print(f"{r['comparison']}: LP {r['z_lp_weak']} -> {r['z_lp_strong']}\n"
              f"  weak optimum: site {r['site']} ships {r['load_i']} (capacity {r['capacity']}), {y}\n"
              f"  strong row (i={r['site']}, j={r['customer']}): x = {r['x_ij']} > {r['d_j']} * "
              f"{r['y_i'] if r['y_i'] != '' else round(r['y_is'] + r['y_il'], 4)}"
              f" = {r['strong_rhs']}  -> violated: {r['violated']}\n")
