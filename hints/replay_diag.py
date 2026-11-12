#!/usr/bin/env python3
"""Diagnose a hint replay: which proof lemmas were matched late and why.

usage: replay_diag.py ORIG_TRACE.pl REPLAY_TRACE.pl HINTFILE.p
Traces are twee --trace outputs; hints are the $hinteq lines of HINTFILE.
"""
import re, sys
sys.path.insert(0, '/project/twee/hints')
import hintlib

_tok = re.compile(r"[A-Za-z][A-Za-z0-9_]*|'[^']*'|[(),=]")

def canon(eq):
    """canonical form of 'l = r' modulo variable renaming and orientation."""
    l, r = [x.strip() for x in eq.split('=')]
    def c(a, b):
        vm = {}
        out = []
        for t in _tok.findall(a + ' = ' + b):
            if t[0].isupper():
                vm.setdefault(t, 'V%d' % len(vm)); out.append(vm[t])
            else:
                out.append(t)
        return ''.join(out)
    return min(c(l, r), c(r, l))

def parse_trace(f):
    adds, hints = {}, {}
    for line in open(f):
        line = line.strip()
        m = re.match(r'step\(add\(rule\((\d+), (.*)\)\)\)\.$', line)
        if m:
            parts = split_top(m.group(2))
            adds[int(m.group(1))] = [canon(p) for p in parts]
        m = re.match(r'step\(hint\((\d+), (\d+)\)\)\.$', line)
        if m:
            hints.setdefault(int(m.group(1)), int(m.group(2)))
    return adds, hints

def split_top(s):
    out, d, cur = [], 0, ''
    for ch in s:
        if ch == '(':
            d += 1
        elif ch == ')':
            d -= 1
        if ch == ',' and d == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return [o.strip() for o in out]

def main():
    orig, _ = parse_trace(sys.argv[1])
    rep, hm = parse_trace(sys.argv[2])
    H = []
    for line in open(sys.argv[3]):
        if 'hinteq' in line:
            body = line[line.index("'$hinteq'(") + 10:line.rindex(')).')]
            l, r = split_top(body)
            H.append(canon(l + ' = ' + r))
    hid = {h: i for i, h in enumerate(H)}
    # first time each canonical eqn was added in replay
    first_rep = {}
    for i in sorted(rep):
        first_rep.setdefault(rep[i][0], i)
    first_orig = {}
    for i in sorted(orig):
        first_orig.setdefault(orig[i][0], (i, orig[i][1:]))
    late = []
    for h, i in hid.items():
        t = first_rep.get(h)
        o = first_orig.get(h)
        if o is None:
            continue
        parents = o[1]
        pt = [first_rep.get(p, 0 if p not in first_orig else None) for p in parents]
        ready = None if any(x is None for x in pt) else max(pt + [0])
        late.append((t if t is not None else 10**9, i, ready, pt))
    late.sort()
    prev = 0
    for t, i, ready, pt in late:
        flag = ''
        if ready is not None and t - ready > 20:
            flag = '  <== LATE (parents ready at %d)' % ready
        print(f'hint {i:4d} added {t if t < 10**9 else "never":>6} parents {pt}{flag}')

main()
