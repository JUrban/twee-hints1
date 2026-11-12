"""Helpers for twee equation hints: extract from twee output, write hint files."""
import re, os

PROB = '/project/AIM60k/problems/tptp'

_cnf = re.compile(r'(?:cnf|fof)\(\s*hint\s*,\s*axiom\s*,\s*(.*)\)\.\s*$', re.S)

def _split_eq(body):
    body = ' '.join(body.split())
    m = re.match(r'!\s*\[[^\]]*\]\s*:\s*(.*)$', body)
    if m:
        body = m.group(1).strip()
    while body.startswith('(') and body.endswith(')'):
        body = body[1:-1].strip()
    if body.count('=') != 1 or '!=' in body:
        return None
    l, r = body.split('=')
    return l.strip(), r.strip()

def _clauses(block):
    """Split a block of TPTP text into clause strings."""
    out, cur = [], []
    for line in block.splitlines():
        if not line.strip():
            continue
        cur.append(line.strip())
        if line.rstrip().endswith(').'):
            out.append(' '.join(cur)); cur = []
    return out

_hintre = re.compile(r'(?:fof|cnf)\(hint, axiom, (.*?)\)\.\s*(?=(?:fof|cnf)\(hint|HINTS-|$)', re.S)

def extract_hints(text):
    """Return (lemmas, goals) as lists of (lhs, rhs) strings from twee --print-hints output."""
    i = text.find('HINTS-BEGIN')
    j = text.find('HINTS-GOAL')
    k = text.find('HINTS-END')
    if i < 0 or j < 0 or k < 0:
        return [], []
    def parse(block):
        res = []
        for m in _hintre.finditer(block):
            e = _split_eq(m.group(1))
            if e:
                res.append(e)
        return res
    a = text.find('HINTS-AUX')
    if a < 0:
        return parse(text[i + 11:j]), parse(text[j + 10:k])
    return parse(text[i + 11:j]), parse(text[j + 10:a])

def extract_aux(text):
    a = text.find('HINTS-AUX')
    k = text.find('HINTS-END')
    if a < 0 or k < 0:
        return []
    return [e for m in _hintre.finditer(text[a + 9:k]) for e in [_split_eq(m.group(1))] if e]

_ident = re.compile(r"[a-z][A-Za-z0-9_]*|'[^']*'")

def symbols(term):
    return set(_ident.findall(term))

def problem_signature(name):
    """Function symbols occurring in the axioms of a problem."""
    sig = set()
    for line in open(os.path.join(PROB, name + '.p')):
        if line.startswith('cnf(') and ',axiom,' in line:
            body = line.split(',axiom,', 1)[1]
            sig |= symbols(body)
    return sig

def hint_line(l, r, tag='h'):
    return f"cnf({tag},axiom,'$hinteq'({l},{r})).\n"

def write_problem_with_hints(name, hints, path):
    """hints: iterable of (lhs, rhs)."""
    with open(path, 'w') as f:
        f.write(open(os.path.join(PROB, name + '.p')).read())
        f.write('\n')
        for l, r in hints:
            f.write(hint_line(l, r))

_tok = re.compile(r"[A-Za-z][A-Za-z0-9_]*|'[^']*'|[(),]")

def generalize(l, r, sig):
    """Replace constants not in sig (goal skolems) by fresh variables.
    Returns canonical (l, r) with variables renamed X0, X1, ... in order of occurrence."""
    vmap = {}
    def tr(t):
        out = []
        toks = _tok.findall(t)
        for i, x in enumerate(toks):
            if x[0].isupper():
                key = ('v', x)
            elif x[0].islower() and x not in sig and not (i + 1 < len(toks) and toks[i + 1] == '('):
                key = ('c', x)
            else:
                out.append(x); continue
            if key not in vmap:
                vmap[key] = 'X%d' % len(vmap)
            out.append(vmap[key])
        return ''.join(out)
    return tr(l), tr(r)

def term_size(t):
    return len([x for x in _tok.findall(t) if x not in '(),'])
