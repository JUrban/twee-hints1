#!/usr/bin/env python3
"""Convert a LightGBM text model to twee's binary forest format.

Format (little endian): int32 ntrees; per tree: int32 nsplit, int32 nleaf,
nsplit x int32 split_feature, nsplit x float64 threshold, nsplit x int32
decision_type, nsplit x int32 left_child, nsplit x int32 right_child,
nleaf x float64 leaf_value.
"""
import struct, sys

def trees(path):
    cur = None
    for line in open(path):
        line = line.strip()
        if line.startswith('Tree='):
            if cur is not None:
                yield cur
            cur = {}
        elif line.startswith('end of trees'):
            break
        elif cur is not None and '=' in line:
            k, v = line.split('=', 1)
            cur[k] = v
    if cur is not None:
        yield cur

def main(src, dst):
    ts = list(trees(src))
    with open(dst, 'wb') as f:
        f.write(struct.pack('<i', len(ts)))
        for t in ts:
            sf = [int(x) for x in t.get('split_feature', '').split()]
            th = [float(x) for x in t.get('threshold', '').split()]
            dt = [int(x) for x in t.get('decision_type', '').split()]
            lc = [int(x) for x in t.get('left_child', '').split()]
            rc = [int(x) for x in t.get('right_child', '').split()]
            lv = [float(x) for x in t.get('leaf_value', '').split()]
            n = len(sf)
            f.write(struct.pack('<ii', n, len(lv)))
            f.write(struct.pack('<%di' % n, *sf))
            f.write(struct.pack('<%dd' % n, *th))
            f.write(struct.pack('<%di' % n, *dt))
            f.write(struct.pack('<%di' % n, *lc))
            f.write(struct.pack('<%di' % n, *rc))
            f.write(struct.pack('<%dd' % len(lv), *lv))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
