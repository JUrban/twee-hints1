#!/usr/bin/env python3
"""Solved counts per AIM60k part for run.py dirs (results.tsv) and loop.py
dirs (solved.tsv, r*/results.tsv).

summary.py LABEL=DIR[+DIR] ...   (DIR/results.tsv or a loop dir)
Prints, per system, the solved problems in train/devel/holdout/all, the CPU
seconds over all runs, and pairwise gains against the first system.
"""
import os, sys, glob

NAMES = '/project/AIM60k/problems'

def part_of():
    p = {}
    for part in ('train', 'devel', 'holdout'):
        for line in open(os.path.join(NAMES, part + '.names')):
            if line.strip():
                p[line.split()[0]] = part
    return p

def load(d):
    solved, cpu = set(), 0.0
    files = [os.path.join(d, 'results.tsv')] if os.path.exists(os.path.join(d, 'results.tsv')) else \
        sorted(glob.glob(os.path.join(d, 'r*', 'results.tsv')))
    for f in files:
        for line in open(f):
            x = line.rstrip('\n').split('\t')
            if len(x) < 3:
                continue
            cpu += float(x[2])
            if x[1] == 'THM':
                solved.add(x[0])
    sp = os.path.join(d, 'solved.tsv')  # a loop started with --init lists the imported round too
    if os.path.exists(sp):
        solved |= set(l.split('\t')[0] for l in open(sp) if l.strip())
    return solved, cpu

def main():
    parts = part_of()
    systems = []
    for arg in sys.argv[1:]:
        label, ds = arg.split('=', 1)
        solved, cpu = set(), 0.0
        for d in ds.split('+'):  # DIR+DIR: union, CPU added (e.g. an --init loop and its source's round 0)
            s1, c1 = load(d)
            solved |= s1; cpu += c1
        systems.append((label, solved, cpu))
    print(f'{"system":30} {"train":>7} {"devel":>7} {"holdout":>7} {"all":>7} {"CPU h":>7}')
    for label, s, cpu in systems:
        c = {p: sum(1 for n in s if parts.get(n) == p) for p in ('train', 'devel', 'holdout')}
        print(f'{label:30} {c["train"]:7} {c["devel"]:7} {c["holdout"]:7} {len(s):7} {cpu/3600:7.1f}')
    if len(systems) > 1:
        base = systems[0]
        for label, s, _ in systems[1:]:
            gain = s - base[1]; loss = base[1] - s
            hg = sum(1 for n in gain if parts.get(n) == 'holdout'); hl = sum(1 for n in loss if parts.get(n) == 'holdout')
            print(f'{label} vs {base[0]}: +{len(gain)}/-{len(loss)} (holdout +{hg}/-{hl}); union {len(s | base[1])}')

if __name__ == '__main__':
    main()
