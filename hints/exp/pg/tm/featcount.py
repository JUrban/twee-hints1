import sys, collections
E, A = collections.Counter(), collections.Counter(); nE = []; nA = []; rules = 0
for f in sys.argv[1:]:
    for l in open(f, errors='replace'):
        if not l.startswith('PGR '): continue
        w = l.split(' ', 8)
        if w[6] == 'E-': continue
        ke = [kv.rsplit(':', 1)[0] for kv in w[6][1:].split(',') if kv]
        ka = [kv.rsplit(':', 1)[0] for kv in w[7][1:].split(',') if kv]
        E.update(ke); A.update(ka); nE.append(len(ke)); nA.append(len(ka)); rules += 1
print('runs %d, rules %d' % (len(sys.argv) - 1, rules))
print('named:     %5d distinct features, %.1f per rule (max %d)' % (len(E), sum(nE) / len(nE), max(nE)))
print('anonymous: %5d distinct features, %.1f per rule (max %d)' % (len(A), sum(nA) / len(nA), max(nA)))
for B in (1024, 4096, 8192):
    for name, C in (('named', E), ('anonymous', A)):
        b = collections.Counter(int(k) % B for k in C)
        coll = sum(v - 1 for v in b.values())
        print('  base %5d %-9s: %4d features share a bucket with another (%.1f%%)' % (B, name, coll, 100 * coll / len(C)))
