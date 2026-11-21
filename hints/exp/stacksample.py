#!/usr/bin/env python3
"""(21 Nov 07:10) A sampling profiler for loop.py's threads (no py-spy here; ptrace_scope 1).

  stacksample.py OUT.txt SCRIPT ARGS...

Runs SCRIPT as __main__ with ARGS. A daemon thread samples every thread's stack every 5 ms (sys._current_frames)
and, at exit (or every 60 s), writes OUT.txt: per thread kind (main / worker), the share of samples in which each
function is on the stack (inclusive) and at the top (exclusive, Python level: time in C calls such as
subprocess waits counts for the calling function). The sampler holds the GIL briefly per sample.
"""
import atexit, collections, os, runpy, sys, threading, time

out, script = sys.argv[1], sys.argv[2]
sys.argv = sys.argv[2:]
main_id = threading.get_ident()
inc = collections.defaultdict(collections.Counter); exc = collections.defaultdict(collections.Counter)
tot = collections.Counter(); paths = collections.defaultdict(collections.Counter)


def key(fr):
    c = fr.f_code
    return f'{os.path.basename(c.co_filename)}:{c.co_name}'


def dump():
    with open(out + '.tmp', 'w') as f:
        for k in sorted(tot):
            f.write(f'== {k}: {tot[k]} samples\n')
            f.write('  exclusive:\n')
            for fn, c in exc[k].most_common(40):
                f.write(f'    {100 * c / tot[k]:5.1f}%  {fn}\n')
            f.write('  inclusive:\n')
            for fn, c in inc[k].most_common(60):
                f.write(f'    {100 * c / tot[k]:5.1f}%  {fn}\n')
            f.write('  paths (loop.py frames, outer to inner, then the leaf):\n')
            for fn, c in paths[k].most_common(50):
                f.write(f'    {100 * c / tot[k]:5.1f}%  {fn}\n')
    os.replace(out + '.tmp', out)


def sampler():
    me = threading.get_ident(); last = time.time()
    while True:
        time.sleep(0.005)
        for tid, fr in sys._current_frames().items():
            if tid == me:
                continue
            k = 'main' if tid == main_id else 'worker'
            tot[k] += 1
            exc[k][key(fr)] += 1
            seen = set(); leaf = key(fr); lp = []
            while fr is not None:
                s = key(fr)
                if s not in seen:
                    seen.add(s); inc[k][s] += 1
                if s.startswith('loop.py:') and s not in ('loop.py:<module>', 'loop.py:main'):
                    lp.append(s[8:])
                fr = fr.f_back
            paths[k][' > '.join(reversed(lp)) + ' | ' + leaf] += 1
        if time.time() - last > 60:
            dump(); last = time.time()


threading.Thread(target=sampler, daemon=True).start()
atexit.register(dump)
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
runpy.run_path(script, run_name='__main__')
