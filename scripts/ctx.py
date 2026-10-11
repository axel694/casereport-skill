#!/usr/bin/env python3
"""Visar textutdrag runt träffar: python3 ctx.py FIL REGEX [antal=5] [bredd=300]
Används för att läsa siffror i sin kontext i hämtade rapporter, aldrig från minnet.
Skär bort inline-XBRL-huvudet (tusentals taggar före själva dokumentet) så att träffarna är läsbar text."""
import re, sys
f, pat = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
w = int(sys.argv[4]) if len(sys.argv) > 4 else 300
t = open(f, errors="ignore").read()
m = re.search(r"UNITED\s+STATES\s+SECURITIES\s+AND\s+EXCHANGE\s+COMMISSION", t, re.I)
if m and m.start() < 400000: t = t[m.start():]
hits = list(re.finditer(pat, t, re.I))
print(f"## {pat} ({len(hits)} träffar)")
for k, h in enumerate(hits):
    if k >= n: break
    print(f"[{k+1}] …{t[max(0, h.start()-w):h.end()+w]}…\n")
