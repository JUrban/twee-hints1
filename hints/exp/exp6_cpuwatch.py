#!/usr/bin/env python3
"""abs/cpuwatch.py [EVERY]: kill any twee run outside production (cmdline without loops/UL) whose CPU time is past
1.5 x its --max-cpu + 60 s: such a run is stuck in one step of the main loop, where twee does not check its limits
(unbounded ground joinability, notes/2026-11-18-ground-joining-hangs.md). Kills by PID; logs to abs/cpuwatch.log."""
import os, sys, time
every = float(sys.argv[1]) if len(sys.argv) > 1 else 30
tick = os.sysconf('SC_CLK_TCK')
log = open('/project/hintwork/abs/cpuwatch.log', 'a')
while True:
    for pid in os.listdir('/proc'):
        if not pid.isdigit(): continue
        try:
            w = open(f'/proc/{pid}/cmdline', 'rb').read().split(b'\0')
            if not w or not os.path.basename(w[0]).startswith(b'twee-e') or any(b'loops/UL' in x for x in w): continue
            w = [x.decode() for x in w]
            if '--max-cpu' not in w: continue
            cap = float(w[w.index('--max-cpu') + 1])
            if cap <= 0: continue
            st = open(f'/proc/{pid}/stat').read().rsplit(')', 1)[1].split()
            cpu = (int(st[11]) + int(st[12])) / tick
            if cpu > 1.5 * cap + 60:
                os.kill(int(pid), 9)
                log.write(f'{time.strftime("%d %H:%M:%S")}\tkilled {pid}\tcpu {cpu:.0f}\tcap {cap:.0f}\t{" ".join(w[:2])}\n'); log.flush()
        except (OSError, ValueError, IndexError):
            pass
    time.sleep(every)
