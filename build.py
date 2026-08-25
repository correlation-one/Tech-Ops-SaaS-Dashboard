#!/usr/bin/env python3
"""One-command monthly build for the Tech Ops SaaS dashboard.

Runs: parse_gl.py -> classify.py -> assemble.py, then verifies data.json
against the frozen history below. See MONTHLY-PROCEDURES.md for the runbook.
"""
import subprocess, sys, json

for step in ('parse_gl.py','classify.py','assemble.py'):
    print(f'\n=== {step} ===')
    r = subprocess.run([sys.executable, step])
    if r.returncode != 0:
        sys.exit(f'{step} failed - stop and investigate before shipping.')

# Frozen history (Aug 2026 rebuild): totals + COGS under the review-sheet classification.
# Verified against the finance GL to the cent. Add new months' figures once accepted.
EXPECTED = {
 'Jan': (151655.48, 110935.23), 'Feb': (157003.65, 111716.97), 'Mar': (163215.17, 119254.49),
 'Apr': (145267.49,  96265.76), 'May': (146127.40,  98038.67), 'Jun': (171927.88, 118719.33),
 'Jul': (152483.62,  98794.11)}

d = json.load(open('data.json'))
bad = []
for lbl, m in zip(d['monthLabels'], d['monthly']):
    if lbl in EXPECTED:
        t, c = EXPECTED[lbl]
        if abs(m['total']-t) > 0.02 or abs(m['cogs']-c) > 0.02:
            bad.append(f"{lbl}: total {m['total']:,.2f} (exp {t:,.2f}) cogs {m['cogs']:,.2f} (exp {c:,.2f})")
print('\n=== regression gate ===')
if bad:
    print('HISTORY CHANGED - do not ship without understanding why:')
    [print(' ', b) for b in bad]
    sys.exit(1)
print('History matches the frozen baseline to the cent. Safe to ship.')
