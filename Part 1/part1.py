"""Part 1: LP and IP values of (CFL), (CFL+), CFL-C and CFL-C+ on team 4's
family S instances.

    python part1.py

Team 4 uses seeds 401, 402, 403 with capacity ratio 2, 4, 8.  For each instance
and formulation, the script solves the LP relaxation and the integer program
under GUROBI_SETTINGS and prints a table.  It writes two files:
    results/part1_cfl.csv      (CFL) and (CFL+)
    results/part1_cfl_c.csv    CFL-C and CFL-C+
The "+" formulations add x_ij <= d_j * (open indicator of site i) (strong=True).
Columns: open = sites with a module open, large = sites with the large module
(always 0 for CFL), frac_y = fractional y variables in the LP solution.
"""
import csv
import os
import pyomo.environ as pyo
from cfl_data import family
from cfl_model import build_cfl, build_cfl_c, solve

SEEDS = (401, 402, 403)
RATIOS = (2, 4, 8)
TOL = 1e-6
# (name, builder, strong, output file)
FORMS = (('CFL', build_cfl, False, 'part1_cfl.csv'),
         ('CFL+', build_cfl, True, 'part1_cfl.csv'),
         ('CFL-C', build_cfl_c, False, 'part1_cfl_c.csv'),
         ('CFL-C+', build_cfl_c, True, 'part1_cfl_c.csv'))


def run(fam='S'):
    rows = []
    for seed in SEEDS:
        for ratio in RATIOS:
            inst = family(fam, ratio=ratio, seed=seed)
            for form, build, strong, out in FORMS:
                tag = f"{form.replace('+', 'p')}_{fam}_r{ratio}_s{seed}"
                lp = build(inst, relax=True, strong=strong)
                z_lp, _, t_lp = solve(lp, lp_file=tag + '_lp.lp')
                frac = sum(1 for v in lp.y.values() if TOL < pyo.value(v) < 1 - TOL)
                ip = build(inst, strong=strong)
                z_ip, nodes, t_ip = solve(ip, lp_file=tag + '_ip.lp')
                if build is build_cfl:
                    n_open = sum(1 for i in inst['I'] if pyo.value(ip.y[i]) > 0.5)
                    n_large = 0
                else:
                    n_open = sum(1 for i in inst['I']
                                 if pyo.value(ip.y[i, 's']) + pyo.value(ip.y[i, 'l']) > 0.5)
                    n_large = sum(1 for i in inst['I'] if pyo.value(ip.y[i, 'l']) > 0.5)
                rows.append(dict(
                    family=fam, seed=seed, ratio=ratio, form=form,
                    z_lp=round(z_lp, 2), z_ip=round(z_ip, 2),
                    gap_pct=round(100 * (z_ip - z_lp) / z_ip, 2),
                    frac_y=frac, open=n_open, large=n_large,
                    nodes=int(nodes), time_s=round(t_ip, 2), out=out))
    return rows


if __name__ == '__main__':
    rows = run('S')
    cols = [c for c in rows[0] if c != 'out']
    os.makedirs('results', exist_ok=True)
    for out in dict.fromkeys(r['out'] for r in rows):   # each file once, in order
        group = [r for r in rows if r['out'] == out]
        print(f'\n{out}')
        print(' '.join(f'{c:>8s}' for c in cols))
        for r in group:
            print(' '.join(f'{str(r[c]):>8s}' for c in cols))
        with open(os.path.join('results', out), 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore')
            w.writeheader()
            w.writerows(group)
