#!/usr/bin/env python3
"""Proofs against the loop's abstract work instead of wall time (16 Nov).

  workcurve.py SET ARM... [--at W1,W2,...]

The loops' hour budget is wall-clock, so a loaded machine fits fewer runs into it: the same configuration
gave 971 and 919 at 60 min (LVS, LV4; REPORT 2aq). Here each cascade run costs its level's abstract seconds
(5, 80, 320) when it fails, and for a proof the wall time times the arm's abstract-per-wall ratio of its
failed runs at that level, capped at the level. A goal counts as solved at the work done when its proof file
appeared (OUT/hints mtime; the transfer worker's proofs land there too).
"""
import os, sys
args = sys.argv[1:]
at = [1000, 2000, 4000, 7000, 10000, 15000, 20000, 30000]
if '--at' in args:
    i = args.index('--at'); at = [int(x) for x in args[i + 1].split(',')]; del args[i:i + 2]
S, arms = args[0], args[1:]
G = {l.strip() for l in open(S) if l.strip()}
LV = {'L0': 5, 'L1': 80, 'L2': 320, 'L3': 1280}
for d in arms:
    D = f'loops/{d}'
    t0 = os.stat(f'{D}/config.json').st_mtime
    rows = []
    for l in open(f'{D}/r1/results.tsv'):
        w = l.rstrip('\n').split('\t')
        rows.append((float(w[5][2:]), w[4], w[1] == 'THM', float(w[2])))
    ratio = {}
    for lv in LV:
        f = [x[3] for x in rows if x[1] == lv and not x[2] and x[3] > 0]
        ratio[lv] = LV[lv] * len(f) / sum(f) if f else 1.0
    ev = sorted((t, LV[lv] if not thm else min(LV[lv], wall * ratio[lv])) for t, lv, thm, wall in rows)
    cum, W = [], 0.0
    for t, c in ev:
        W += c; cum.append((t, W))
    sol = sorted(os.stat(f'{D}/hints/{g}').st_mtime - t0 for g in os.listdir(f'{D}/hints') if g in G)
    out, j, k = [], 0, 0
    for w in at:
        while j < len(cum) and cum[j][1] <= w: j += 1
        if j == len(cum) and cum[-1][1] < w: break
        tw = cum[j - 1][0] if j else 0
        out.append(f'{w}:{sum(1 for s in sol if s <= tw)}@{tw / 60:.0f}m')
    print(f'{d:6} {" ".join(out)}  total work {W:.0f} in {ev[-1][0] / 60:.0f} min, {len(sol)} solved')
