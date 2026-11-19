import re, sys
# twee hint file (lhs TAB rhs per line) -> TPTP watchlist clauses
# (19 Nov 09:30) hints with tokens TPTP cannot read (e.g. '-e') are skipped
ok = re.compile(r'^[A-Za-z0-9_(),]+$')
n = 0
for l in open(sys.argv[1]):
    f = l.rstrip('\n').split('\t')
    if len(f) != 2 or not ok.match(f[0]) or not ok.match(f[1]): continue
    n += 1
    print(f'cnf(h{n},axiom,({f[0]} = {f[1]})).')
