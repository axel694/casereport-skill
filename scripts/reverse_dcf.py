#!/usr/bin/env python3
"""Reverse DCF: vilken framtid prisar kursen in?

Användning: python3 reverse_dcf.py indata.json [utdata.json]

Idé: lös ut den intäktstillväxt (CAGR år 1–N) som gör att nuvärdet av framtida fritt kassaflöde
(efter aktiebaserad ersättning) = dagens EV. Allt annat är synliga antaganden i indata.json.

indata.json (alla belopp i samma enhet, t.ex. USD miljoner):
{
 "bolag": "Exempelbolag", "prisdatum": "ÅÅÅÅ-MM-DD", "kurs": 400.0, "aktier_utspadda": 340.0,
 "nettoskuld": 3000.0,                  # skuld - kassa vid senaste balansdag (negativ = nettokassa)
 "intakt_bas": 5500.0,                  # senaste 12 mån (TTM) intäkt, bolagets bas
 "marginal_bas": 0.75,                  # EBITDA-marginal TTM (bolagets justerade)
 "marginal_mal": 0.75,                  # EBITDA-marginal år 10 (linjär övergång)
 "sbc_pct": 0.04,                       # aktiebaserad ersättning % av intäkt (dras av som kostnad)
 "da_pct": 0.01, "capex_pct": 0.01,     # % av intäkt
 "nwc_pct_tillvaxt": 0.05,              # rörelsekapital % av intäktsökning
 "skatt": 0.21,
 "wacc": 0.10, "g_term": 0.03,
 "ar_hog_tillvaxt": 5,                  # antal år med konstant tillväxt (den som löses ut)
 "ar_totalt": 10,                       # därefter linjär nedtrappning till g_term till och med år 10
 "capex_pct_tillvaxt": 0.0,             # valfritt: extra capex per intäktsdollar i ökning (kapitalintensiva bolag), default 0
 "ar_marginal": 10,                     # valfritt: antal år till slutmarginal nås (default = ar_totalt)
 "kansl_wacc": [0.08,0.09,0.10,0.11,0.12],
 "kansl_g": [0.02,0.025,0.03,0.035,0.04],
 "kansl_marginal": [0.5,0.6,0.7,0.75,0.8],
 "kansl_irr_cagr": [0.3,0.5,0.7],     # valfritt: tabell med implicit avkastning (IRR) vid dessa CAGR x kansl_marginal
 "historisk_cagr": {"3ar":0.5,"5ar":0.4,"10ar":0.3}   # valfritt, för jämförelse
}
Utdata: implicerad CAGR, intäkt/EBITDA/FCF år 10, terminalvärdets andel av EV, implicerad exit-multipel,
samt tre känslighetstabeller (WACC × g, WACC × marginal, kurs × tillväxt) och årsbanan. Skrivs till utdata.json.
"""
import json, sys

def project(p, cagr):
    """Returnerar (ev, rader). FCF = EBITDA - skatt på (EBITDA-D&A-SBC) - capex - dNWC - SBC."""
    n, nh = p["ar_totalt"], p["ar_hog_tillvaxt"]; nm = p.get("ar_marginal", n); cg = p.get("capex_pct_tillvaxt", 0.0)
    rev, prev, pv, rows = p["intakt_bas"], p["intakt_bas"], 0.0, []
    for t in range(1, n + 1):
        if t <= nh: g = cagr
        else: g = cagr + (p["g_term"] - cagr) * (t - nh) / (n - nh)
        rev = prev * (1 + g)
        m = p["marginal_bas"] + (p["marginal_mal"] - p["marginal_bas"]) * min(t, nm) / nm
        ebitda = rev * m
        ebit_efter_sbc = ebitda - rev * p["da_pct"] - rev * p["sbc_pct"]
        skatt = max(ebit_efter_sbc, 0) * p["skatt"]
        fcf = ebitda - skatt - rev * p["capex_pct"] - (rev - prev) * (p["nwc_pct_tillvaxt"] + cg) - rev * p["sbc_pct"]
        pv += fcf / (1 + p["wacc"]) ** t
        rows.append(dict(ar=t, tillvaxt=g, intakt=rev, ebitda_marginal=m, ebitda=ebitda, fcf=fcf))
        prev = rev
    tv = rows[-1]["fcf"] * (1 + p["g_term"]) / (p["wacc"] - p["g_term"])
    pv_tv = tv / (1 + p["wacc"]) ** n
    return pv + pv_tv, rows, pv_tv, tv

def solve(p, mal_ev):
    lo, hi = -0.30, 1.50
    for _ in range(200):
        mid = (lo + hi) / 2
        if project(p, mid)[0] < mal_ev: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def solve_irr(p, ev, cagr):
    """Diskonteringsränta (implicit avkastning) som gör nuvärdet = EV givet en vald tillväxtbana. None om ingen finns."""
    lo, hi = p["g_term"] + 0.002, 1.5
    f = lambda w: project(dict(p, wacc=w), cagr)[0] - ev
    if f(lo) < 0 or f(hi) > 0: return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def implied(p, ev):
    c = solve(p, ev)
    v, rows, pv_tv, tv = project(p, c)
    return dict(cagr=c, ev=v, intakt_ar_n=rows[-1]["intakt"], ebitda_ar_n=rows[-1]["ebitda"], fcf_ar_n=rows[-1]["fcf"],
                tv_andel=pv_tv / v, exit_multipel_ebitda=tv / rows[-1]["ebitda"], rader=rows)

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    p = json.load(open(sys.argv[1]))
    ev = p["kurs"] * p["aktier_utspadda"] + p["nettoskuld"]
    res = dict(indata=p, borsvarde=p["kurs"] * p["aktier_utspadda"], ev=ev, bas=implied(p, ev))
    # 1) WACC x g_term -> implicerad CAGR
    t1 = []
    for w in p["kansl_wacc"]:
        rad = []
        for g in p["kansl_g"]:
            q = dict(p, wacc=w, g_term=g)
            rad.append(solve(q, ev) if w > g else None)
        t1.append(rad)
    # 2) WACC x slutmarginal -> implicerad CAGR
    t2 = []
    for w in p["kansl_wacc"]:
        t2.append([solve(dict(p, wacc=w, marginal_mal=m), ev) for m in p["kansl_marginal"]])
    # 3) Värde per aktie om tillväxten blir X (framåt: vad är aktien värd vid olika CAGR och WACC)
    cagrs = [round(res["bas"]["cagr"] + d, 4) for d in (-0.10, -0.05, 0, 0.05, 0.10)]
    t3 = []
    for w in p["kansl_wacc"]:
        rad = []
        for c in cagrs:
            v = project(dict(p, wacc=w), c)[0]
            rad.append((v - p["nettoskuld"]) / p["aktier_utspadda"])
        t3.append(rad)
    res["kansl_wacc_g"] = dict(rader=p["kansl_wacc"], kolumner=p["kansl_g"], varden=t1)
    res["kansl_wacc_marginal"] = dict(rader=p["kansl_wacc"], kolumner=p["kansl_marginal"], varden=t2)
    res["kansl_varde_per_aktie"] = dict(rader=p["kansl_wacc"], kolumner=cagrs, varden=t3)
    if "kansl_irr_cagr" in p:   # valfri tabell 4: implicit avkastning vid givna CAGR x slutmarginal (när CAGR-lösningen är orimlig)
        res["kansl_irr"] = dict(rader=p["kansl_irr_cagr"], kolumner=p["kansl_marginal"],
            varden=[[solve_irr(dict(p, marginal_mal=m), ev, c) for m in p["kansl_marginal"]] for c in p["kansl_irr_cagr"]])
    out = sys.argv[2] if len(sys.argv) > 2 else "reverse_dcf_ut.json"
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    b = res["bas"]
    cap = " (OVAN SÖKGRÄNSEN 150 %: kursen går inte att motivera med dessa antaganden)" if b["cagr"] > 1.499 else ""
    print(f"EV {ev:,.0f} (börsvärde {res['borsvarde']:,.0f}); implicerad intäkts-CAGR år 1–{p['ar_hog_tillvaxt']}: {b['cagr']*100:.1f} %{cap}")
    print(f"År {p['ar_totalt']}: intäkt {b['intakt_ar_n']:,.0f}, EBITDA {b['ebitda_ar_n']:,.0f}, FCF {b['fcf_ar_n']:,.0f}; "
          f"terminalvärde {b['tv_andel']*100:.0f} % av EV; implicerad exit EV/EBITDA {b['exit_multipel_ebitda']:.1f}x")
    if "historisk_cagr" in p: print("Historik för jämförelse:", p["historisk_cagr"])

if __name__ == "__main__":
    main()
