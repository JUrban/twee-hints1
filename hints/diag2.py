#!/usr/bin/env python3
"""Replay diagnosis with tracked hints.

usage: diag2.py PROBLEM HINTS.tsv [twee args...]
Runs twee twice:
  1. unguided, tracking HINTS (to find when each hint is derived and from
     which parent rules), with --trace
  2. guided by HINTS, with --trace
and prints, for each hint, its original rule, its parents' hint ids, and
when it and its parents were derived in the guided run.
"""
import re, subprocess, sys, os
TW = os.environ.get('TWEE', '/project/bin/twee-h6')
P, H = sys.argv[1], sys.argv[2]
extra = sys.argv[3:]
prob = f'/project/AIM60k/problems/tptp/{P}.p'
tmp = '/tmp/diag2_%d' % os.getpid()

def run(args, tr):
    out = subprocess.run([TW, prob, '--no-colour', '--no-proof', '--max-time', '60', '--trace', tr, 'm'] + args + extra,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode()
    return out

def parse_trace(tr):
    rules = {}   # id -> (eqn, parent1, parent2)
    for line in open(tr):
        m = re.match(r'step\(add\(rule\((\d+), (.*)\)\)\)\.$', line.strip())
        if m:
            parts = split_top(m.group(2))
            rules[int(m.group(1))] = parts
    return rules

def split_top(s):
    out, d, cur = [], 0, ''
    for ch in s:
        if ch == '(': d += 1
        elif ch == ')': d -= 1
        if ch == ',' and d == 0:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
    out.append(cur.strip())
    return out

_tok = re.compile(r"[A-Za-z][A-Za-z0-9_]*|[(),=]")
def canon(eq):
    l, r = [x.strip() for x in eq.split(' = ')] if ' = ' in eq else eq.split('=')
    def c(a, b):
        vm = {}; out = []
        for t in _tok.findall(a + '=' + b):
            if t[0].isupper():
                vm.setdefault(t, 'V%d' % len(vm)); out.append(vm[t])
            else:
                out.append(t)
        return ''.join(out)
    return min(c(l, r), c(r, l))

def matches(out, base=0):
    d = {}
    for m in re.finditer(r'\(matched hint (\d+)\) (\d+)\.', out):
        h, r = int(m.group(1)) - base, int(m.group(2))
        d.setdefault(h, r)
    return d

o1 = run(['--track-hints', H], tmp + '_1.pl')
orig = parse_trace(tmp + '_1.pl')
hint_orig = matches(o1, 1000000)       # hint -> original rule id
o2 = run(['--hints-file', H], tmp + '_2.pl')
hint_rep = matches(o2)                 # hint -> replay rule id
print('orig rules', len(orig), 'replay rules', len(parse_trace(tmp + '_2.pl')))
print('orig:', [l for l in o1.splitlines() if l.startswith('HINTSTATS')])
print('replay:', [l for l in o2.splitlines() if l.startswith('HINTSTATS')])
# map canonical eqn -> first original rule id
first = {}
for i in sorted(orig):
    first.setdefault(canon(orig[i][0]), i)
rule_hint = {r: h for h, r in hint_orig.items()}
rows = []
for h, r in sorted(hint_orig.items(), key=lambda x: x[1]):
    eq, *par = orig[r]
    pr = [first.get(canon(p)) for p in par]
    ph = [rule_hint.get(x) if x is not None else None for x in pr]
    ready = [hint_rep.get(x) if x is not None else None for x in ph]
    rows.append((r, h, pr, ph, hint_rep.get(h), ready, eq))
for r, h, pr, ph, t, ready, eq in rows:
    note = ''
    if t is None:
        note = 'NEVER'
    elif all(x is not None for x in ready) and ready and t - max(ready) > 30:
        note = f'LATE by {t - max(ready)}'
    print(f'orig {r:5d} hint {h:4d} parents(orig) {pr} parents(hint) {ph} replay {t} parents-ready {ready} {note}  {eq[:70]}')
