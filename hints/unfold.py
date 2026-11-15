#!/usr/bin/env python3
"""Unfold definitions in a TPTP problem (15 Nov).

Twee's KBO makes a definition f(X1..Xn) = t fold: t -> f(X1..Xn), since t is
the bigger side. Prover9's ordering unfolds it. On some stalled goals the
proof is one rewrite step once the defined symbols are expanded (goal 212 of
aK2_eq_aK3_r: Prover9 0.2 s, twee 0 of 20 s). This rewrites every formula of
a problem with the definitions substituted away and drops the definitions,
so twee works over the base signature (m, ld, rd, e).

  unfold.py IN.p OUT.p            whole problem (axioms, lemmas, conjecture)
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

def unfold_text(text, defs=None):
    defs = problem_defs(text) if defs is None else defs
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

def main():
    if sys.argv[1] == '--hints':
        _, _, src, dst, _, p = sys.argv[:6]
        defs = problem_defs(open(p).read())
        with open(dst, 'w') as f:
            for l in open(src):
                if l.strip():
                    f.write(unfold_eq(l.strip(), defs) + '\n')
        return
    txt, defs = unfold_text(open(sys.argv[1]).read())
    open(sys.argv[2], 'w').write(txt)
    print('unfolded', ' '.join(f'{f}/{n}' for f, n in sorted(defs)), file=sys.stderr)

if __name__ == '__main__':
    main()
