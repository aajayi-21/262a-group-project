"""Part 1: LP and IP values of (CFL) and (CFL+) on team 4's family S instances.

    python part1.py

Team 4 uses seeds 401, 402, 403 with capacity ratio 2, 4, 8.  For each instance
and formulation, the script solves the LP relaxation and the integer program
under GUROBI_SETTINGS and prints a table; it also writes results/part1.csv.
"""
import csv
import os
import pyomo.environ as pyo
from cfl_data import family
from cfl_model import build_cfl, solve

SEEDS = (401, 402, 403)
RATIOS = (2, 4, 8)
TOL = 1e-6


def run(fam='S'):
    rows = []
    for seed in SEEDS:
        for ratio in RATIOS:
            inst = family(fam, ratio=ratio, seed=seed)
            for form, strong in (('CFL', False), ('CFL+', True)):
                tag = f"{form.replace('+', 'p')}_{fam}_r{ratio}_s{seed}"
                lp = build_cfl(inst, relax=True, strong=strong)
                z_lp, _, t_lp = solve(lp, lp_file=tag + '_lp.lp')
                frac = sum(1 for i in inst['I'] if TOL < pyo.value(lp.y[i]) < 1 - TOL)
                ip = build_cfl(inst, strong=strong)
                z_ip, nodes, t_ip = solve(ip, lp_file=tag + '_ip.lp')
                rows.append(dict(
                    family=fam, seed=seed, ratio=ratio, form=form,
                    z_lp=round(z_lp, 2), z_ip=round(z_ip, 2),
                    gap_pct=round(100 * (z_ip - z_lp) / z_ip, 2),
                    frac_y=frac, open=sum(1 for i in inst['I'] if pyo.value(ip.y[i]) > 0.5),
                    nodes=int(nodes), time_s=round(t_ip, 2)))
    return rows


if __name__ == '__main__':
    rows = run('S')
    cols = list(rows[0])
    print(' '.join(f'{c:>8s}' for c in cols))
    for r in rows:
        print(' '.join(f'{str(r[c]):>8s}' for c in cols))
    os.makedirs('results', exist_ok=True)
    with open('results/part1.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
