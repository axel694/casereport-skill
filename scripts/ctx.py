#!/usr/bin/env python3
"""Visar textutdrag runt träffar: python3 ctx.py FIL REGEX [antal=5] [bredd=300]
Används för att läsa siffror i sin kontext i hämtade rapporter, aldrig från minnet."""
import re, sys
f, pat = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
w = int(sys.argv[4]) if len(sys.argv) > 4 else 300
t = open(f, errors="ignore").read()
for k, m in enumerate(re.finditer(pat, t, re.I)):
    if k >= n: break
    print(f"[{k+1}] …{t[max(0, m.start()-w):m.end()+w]}…\n")
