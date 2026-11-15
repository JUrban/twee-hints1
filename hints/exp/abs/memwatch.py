#!/usr/bin/env python3
"""Memory watchdog (user's request, 14 Nov): every 0.5 s, kill any twee process over PER GB RSS, and while
all twee processes together exceed TOTAL GB, kill the largest. Logs to /project/hintwork/memwatch.log."""
import os, sys, time, signal
PER = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
TOTAL = float(sys.argv[2]) if len(sys.argv) > 2 else 45.0
LOG = '/project/hintwork/memwatch.log'
def procs():
    out = []
    for p in os.listdir('/proc'):
        if not p.isdigit():
            continue
        try:
            with open(f'/proc/{p}/cmdline', 'rb') as f:
                cmd = f.read().split(b'\0')
            if not cmd or b'twee' not in os.path.basename(cmd[0]):
                continue
            with open(f'/proc/{p}/statm') as f:
                rss = int(f.read().split()[1]) * os.sysconf('SC_PAGE_SIZE') / 2**30
            out.append((rss, int(p), b' '.join(cmd[:2]).decode('utf8', 'replace')))
        except (OSError, ValueError, IndexError):
            pass
    return out
def kill(rss, pid, cmd, why):
    try:
        os.kill(pid, signal.SIGKILL)
        with open(LOG, 'a') as f:
            f.write(f'{time.strftime("%F %T")} KILL {why} pid={pid} rss={rss:.1f}G {cmd}\n')
    except OSError:
        pass
while True:
    ps = procs()
    for rss, pid, cmd in ps:
        if rss > PER:
            kill(rss, pid, cmd, f'per>{PER}G')
    ps = sorted((x for x in ps if x[0] <= PER), reverse=True)
    tot = sum(x[0] for x in ps)
    while ps and tot > TOTAL:
        rss, pid, cmd = ps.pop(0); tot -= rss
        kill(rss, pid, cmd, f'total>{TOTAL}G')
    time.sleep(0.5)
