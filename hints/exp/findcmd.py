#!/usr/bin/env python3
"""findcmd.py PATTERN [N] [--from YYYY-MM-DDTHH] : tool calls (Bash commands, Write contents) in the twee session
transcript that contain PATTERN, with their timestamps (first N, default 5)."""
import json, sys
a = sys.argv[1:]; frm = ''
if '--from' in a:
    i = a.index('--from'); frm = a[i + 1]; del a[i:i + 2]
pat = a[0]; N = int(a[1]) if len(a) > 1 else 5; W = 1500
n = 0
for line in open('/home/mptp/.claude/projects/-project/06816eaa-f48d-4d65-80b0-498c3b54febf.jsonl', errors='replace'):
    if pat not in line:
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get('type') != 'assistant' or (d.get('timestamp') or '') < frm:
        continue
    for b in d['message'].get('content', []):
        if isinstance(b, dict) and b.get('type') == 'tool_use':
            c = b['input'].get('command') or b['input'].get('content') or ''
            if pat in c and 'findcmd.py' not in c:
                i = c.find(pat)
                print('###', d['timestamp'][:16], b['input'].get('file_path', ''))
                print(c[max(0, i - W // 2): i + W // 2]); n += 1
                if n >= N:
                    sys.exit()
