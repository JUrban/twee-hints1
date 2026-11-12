"""Term features for similarity of goal statements and hints."""
import re
_tok = re.compile(r"[A-Za-z][A-Za-z0-9_]*|[(),=]")

def parse(s):
    toks = _tok.findall(s); pos = 0
    def term():
        nonlocal pos
        t = toks[pos]; pos += 1
        if pos < len(toks) and toks[pos] == '(':
            pos += 1; args = []
            while True:
                args.append(term())
                if toks[pos] == ',': pos += 1; continue
                if toks[pos] == ')': pos += 1; break
            return (t, args)
        return (t, [])
    return term()

def isvar(t):
    return t[0][0].isupper()

def shape(t, d):
    if isvar(t): return '*'
    if d == 0 or not t[1]: return t[0]
    return t[0] + '(' + ','.join(shape(a, d - 1) for a in t[1]) + ')'

def subterms(t):
    yield t
    for a in t[1]:
        yield from subterms(a)

def features(eq_l, eq_r, depth=2):
    f = set()
    for side in (parse(eq_l), parse(eq_r)):
        for s in subterms(side):
            if isvar(s): continue
            for d in range(1, depth + 1):
                f.add(shape(s, d))
    return f
