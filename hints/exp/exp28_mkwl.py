import sys
# twee hint file (lhs TAB rhs per line) -> TPTP watchlist clauses
n = 0
for l in open(sys.argv[1]):
    f = l.rstrip('\n').split('\t')
    if len(f) != 2: continue
    n += 1
    print(f'cnf(h{n},axiom,({f[0]} = {f[1]})).')
