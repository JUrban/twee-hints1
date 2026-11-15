#!/usr/bin/env python3
"""Unfold definitions in a TPTP problem (15 Nov).

Twee's KBO makes a definition f(X1..Xn) = t fold: t -> f(X1..Xn), since t is
the bigger side. Prover9's ordering unfolds it. On some stalled goals the
proof is one rewrite step once the defined symbols are expanded (goal 212 of
aK2_eq_aK3_r: Prover9 0.2 s, twee 0 of 20 s). This rewrites every formula of
a problem with the definitions substituted away and drops the definitions,
so twee works over the base signature (m, ld, rd, e).

  unfold.py IN.p OUT.p [f,g,..]   whole problem (axioms, lemmas, conjecture); only f, g, .. if given
  unfold.py --hints IN OUT --defs P.p   a hint file (one equation per line)

A definition is an axiom f(V1,..,Vn) = RHS with distinct variables, f not in
RHS. Defined symbols in hints are expanded with the definitions of problem P.
"""
import re, sys

TOK = re.compile(r"\s*([A-Za-z_$][A-Za-z0-9_$]*|!=|=>|<=>|<=|[(),\[\]:=|&~!?.]|'[^']*'|\S)")

def tokens(s):
    out, i = [], 0
    while i < len(s):
        m = TOK.match(s, i)
        if not m:
            break
        if m.group(1):
            out.append(m.group(1))
        i = m.end()
    return out

def parse_seq(tk, i, stop):
    """Parse tokens from i until a token in STOP at depth 0; return (items, i)."""
    items = []
    while i < len(tk) and tk[i] not in stop:
        t = tk[i]
        if re.match(r'[A-Za-z_$]', t) and i + 1 < len(tk) and tk[i + 1] == '(':
            args, i = [], i + 2
            while True:
                a, i = parse_seq(tk, i, (',', ')'))
                args.append(a)
                if tk[i] == ')':
                    i += 1
                    break
                i += 1
            items.append((t, args))
        elif t == '(':
            inner, i = parse_seq(tk, i + 1, (')',))
            items.append(('(', inner))
            i += 1
        elif t == '[':
            inner, i = parse_seq(tk, i + 1, (']',))
            items.append(('[', inner))
            i += 1
        else:
            items.append(t)
            i += 1
    return items, i

def render(items):
    out = []
    for x in items:
        if isinstance(x, str):
            out.append(x)
        elif x[0] == '(':
            out.append('(' + render(x[1]) + ')')
        elif x[0] == '[':
            out.append('[' + render(x[1]) + ']')
        else:
            out.append(x[0] + '(' + ','.join(render(a) for a in x[1]) + ')')
    s = ' '.join(out)
    s = re.sub(r' ?([(),\[\]]) ?', r'\1', s)
    return s.replace('! [', '! [').replace(':', ' : ')

def subst(items, env):
    out = []
    for x in items:
        if isinstance(x, str):
            out.extend(env.get(x, [x]))
        elif x[0] in '([':
            out.append((x[0], subst(x[1], env)))
        else:
            out.append((x[0], [subst(a, env) for a in x[1]]))
    return out

def expand(items, defs):
    out = []
    for x in items:
        if isinstance(x, str):
            out.append(x)
        elif x[0] in '([':
            out.append((x[0], expand(x[1], defs)))
        else:
            args = [expand(a, defs) for a in x[1]]
            d = defs.get((x[0], len(args)))
            if d:
                params, rhs = d
                out.extend(expand(subst(rhs, dict(zip(params, args))), defs))
            else:
                out.append((x[0], args))
    return out

def syms(items, acc):
    for x in items:
        if isinstance(x, tuple):
            if x[0] not in '([':
                acc.add((x[0], len(x[1])))
                for a in x[1]:
                    syms(a, acc)
            else:
                syms(x[1], acc)
    return acc

FORM = re.compile(r'^\s*(fof|cnf)\(\s*([^,]+?)\s*,\s*([a-z_]+)\s*,(.*)\)\s*\.\s*$')

def formulas(text):
    """(kind, name, role, body) for each formula; other lines are kept as (None, line)."""
    buf, out = '', []
    for line in text.splitlines():
        if not buf and (not line.strip() or line.lstrip().startswith('%')):
            out.append((None, line))
            continue
        buf += line.strip() + ' '
        if buf.rstrip().endswith(').'):
            m = FORM.match(buf)
            out.append(m.groups() if m else (None, buf))
            buf = ''
    return out

def definition(body):
    """(f, params, rhs items) if BODY is f(V1..Vn) = RHS with distinct variables and f not in RHS."""
    tk = tokens(body)
    while tk and tk[0] == '(' and tk[-1] == ')':
        tk = tk[1:-1]
    items, _ = parse_seq(tk, 0, ())
    if len(items) < 3 or items[1] != '=' or not isinstance(items[0], tuple) or items[0][0] in '([':
        return None
    f, args = items[0]
    params = [a[0] if len(a) == 1 and isinstance(a[0], str) else None for a in args]
    if None in params or len(set(params)) != len(params) or not all(re.match(r'[A-Z]', p) for p in params):
        return None
    rhs = items[2:]
    if (f, len(args)) in syms(rhs, set()):
        return None
    if any(isinstance(x, str) and x in ('|', '&', '=>', '!=') for x in rhs):
        return None
    return f, params, rhs

def problem_defs(text):
    defs = {}
    for g in formulas(text):
        if g[0] and g[2] == 'axiom':
            d = definition(g[3])
            if d and (d[0], len(d[1])) not in defs:
                defs[(d[0], len(d[1]))] = (d[1], d[2])
    return defs

def unfold_text(text, defs=None, only=None):
    """ONLY: a set of symbol names to unfold (default: every definition)."""
    defs = problem_defs(text) if defs is None else defs
    if only:
        defs = {k: v for k, v in defs.items() if k[0] in only}
    out = []
    for g in formulas(text):
        if not g[0]:
            out.append(g[1])
            continue
        kind, name, role, body = g
        d = definition(body) if role == 'axiom' else None
        if d and (d[0], len(d[1])) in defs and defs[(d[0], len(d[1]))][0] == d[1]:
            continue                       # the definition itself
        items, _ = parse_seq(tokens(body), 0, ())
        out.append(f'{kind}({name},{role},{render(expand(items, defs))}).')
    return '\n'.join(out) + '\n', defs

def unfold_eq(line, defs):
    items, _ = parse_seq(tokens(line), 0, ())
    return render(expand(items, defs))

# --- folded instances of lemmas, for folded runs (15 Nov) ---
# Goal 212 needs sibling 209 with X0 = X2: then 209's ld(X2,m(X1,X2)) folds to t(X1,X2). Twee
# reaches that critical pair (209 with the t rule) late or never. fold_instances adds such
# instances: for each non-variable subterm of a lemma that unifies with a definition's body, the
# lemma under the unifier, folded by the definitions.

def to_term(items):
    x = items[0]
    if isinstance(x, str):
        return x
    if x[0] == '(':
        return to_term(x[1])
    return (x[0], [to_term(a) for a in x[1]])

def is_var(t):
    return isinstance(t, str) and t[:1].isupper()

def eq_of(body):
    """(lhs, rhs) trees of a unit equation body (with or without a ! [..] : prefix), else None."""
    items, _ = parse_seq(tokens(body), 0, ())
    while True:
        while len(items) == 1 and isinstance(items[0], tuple) and items[0][0] == '(':
            items = items[0][1]
        if len(items) >= 3 and items[0] == '!' and isinstance(items[1], tuple) and items[1][0] == '[' and items[2] == ':':
            items = items[3:]
            continue
        break
    if len(items) != 3 or items[1] != '=':
        return None
    return to_term([items[0]]), to_term([items[2]])

def walk(t, s):
    while is_var(t) and t in s:
        t = s[t]
    return t

def occurs(v, t, s):
    t = walk(t, s)
    if t == v:
        return True
    return isinstance(t, tuple) and any(occurs(v, a, s) for a in t[1])

def unify(a, b, s):
    a, b = walk(a, s), walk(b, s)
    if a == b:
        return s
    if is_var(a):
        if occurs(a, b, s):
            return None
        s = dict(s); s[a] = b
        return s
    if is_var(b):
        return unify(b, a, s)
    if isinstance(a, str) or isinstance(b, str) or a[0] != b[0] or len(a[1]) != len(b[1]):
        return None
    for x, y in zip(a[1], b[1]):
        s = unify(x, y, s)
        if s is None:
            return None
    return s

def resolve(t, s):
    t = walk(t, s)
    return (t[0], [resolve(a, s) for a in t[1]]) if isinstance(t, tuple) else t

def match(p, t, s):
    if is_var(p):
        if p in s:
            return s if s[p] == t else None
        s = dict(s); s[p] = t
        return s
    if isinstance(p, str) or not isinstance(t, tuple):
        return s if p == t else None
    if p[0] != t[0] or len(p[1]) != len(t[1]):
        return None
    for x, y in zip(p[1], t[1]):
        s = match(x, y, s)
        if s is None:
            return None
    return s

def fold(t, rules):
    if isinstance(t, tuple):
        t = (t[0], [fold(a, rules) for a in t[1]])
        for f, params, pat in rules:
            s = match(pat, t, {})
            if s is not None:
                return fold((f, [s[p] for p in params]), rules)
    return t

def show(t):
    return t if isinstance(t, str) else f'{t[0]}({",".join(show(a) for a in t[1])})'

def subterms(t):
    if isinstance(t, tuple):
        yield t
        for a in t[1]:
            yield from subterms(a)

def canon(l, r):
    ren = {}
    def go(t):
        if is_var(t):
            ren.setdefault(t, f'X{len(ren)}')
            return ren[t]
        return (t[0], [go(a) for a in t[1]]) if isinstance(t, tuple) else t
    return show(go(l)), show(go(r))

def fold_rules(defs):
    rules = []
    for (f, n), (params, rhs) in defs.items():
        ren = {p: f'Def{i}' for i, p in enumerate(params)}
        pat = to_term(subst(rhs, {p: [v] for p, v in ren.items()}))
        rules.append((f, [ren[p] for p in params], pat))
    return rules

def fold_instances(l, r, rules):
    """Instances of the lemma l = r where a subterm meets a definition body, folded."""
    base = canon(fold(l, rules), fold(r, rules))
    out, seen = [], {base, base[::-1]}
    for u in list(subterms(l)) + list(subterms(r)):
        for f, params, pat in rules:
            s = unify(u, pat, {})
            if s is None or not any(not k.startswith('Def') for k in s):
                continue          # no unifier, or only the pattern is instantiated (plain folding)
            l2, r2 = fold(resolve(l, s), rules), fold(resolve(r, s), rules)
            if l2 == r2:
                continue
            c = canon(l2, r2)
            if c in seen:
                continue
            seen.add(c); seen.add(c[::-1]); out.append(c)
    return out

def lemma_fold_text(text, prefixes=('lemma_',), limit=8):
    """Folded instances of the problem's lemma axioms (names starting with PREFIXES), as cnf axioms."""
    rules = fold_rules(problem_defs(text))
    if not rules:
        return ''
    out, seen = [], set()
    for g in formulas(text):
        if not g[0] or g[2] != 'axiom' or not g[1].startswith(prefixes):
            continue
        e = eq_of(g[3])
        if not e:
            continue
        for c in fold_instances(e[0], e[1], rules)[:limit]:
            if c not in seen:
                seen.add(c)
                out.append(f'cnf(lemma_fold_{len(out)},axiom,{c[0]} = {c[1]}).')
    return ''.join(x + '\n' for x in out)

def main():
    if sys.argv[1] == '--fold':
        txt = open(sys.argv[2]).read()
        print(lemma_fold_text(txt), end='')
        return
    if sys.argv[1] == '--hints':
        _, _, src, dst, _, p = sys.argv[:6]
        defs = problem_defs(open(p).read())
        with open(dst, 'w') as f:
            for l in open(src):
                if l.strip():
                    f.write(unfold_eq(l.strip(), defs) + '\n')
        return
    only = set(sys.argv[3].split(',')) if len(sys.argv) > 3 else None
    txt, defs = unfold_text(open(sys.argv[1]).read(), only=only)
    open(sys.argv[2], 'w').write(txt)
    print('unfolded', ' '.join(f'{f}/{n}' for f, n in sorted(defs)), file=sys.stderr)

if __name__ == '__main__':
    main()
