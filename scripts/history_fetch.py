#!/usr/bin/env python3
"""Tio års historik ur SEC EDGAR: årsserie ur XBRL + alla årsrapporter (10-K) som text.

Användning: python3 history_fetch.py TICKER UTMAPP [--years 10] [--extra-cik CIK ...]
  --extra-cik: hämtar även äldre 10-K från en föregångare/tidigare filer (t.ex. när bolaget bytt moderbolag eller CIK); upprepas vid behov.

Sparar i UTMAPP:
  historik_ar.csv / historik_ar.md   årsserie (intäkt, resultat, kassaflöde, SBC, aktier, balans) + härledda mått
  10k/10-K_<räkenskapsårets slut>.txt  varje årsrapport som ren text (så många som finns, max --years)
  10k/manifest_10k.json              fil, räkenskapsår, URL
Kräver bara Python 3 och curl. Hoppar över år som saknas (nylistade bolag) och säger det.
Alla härledda mått är beräknade ur XBRL-siffrorna; verifiera nyckeltal mot 10-K-texten med ctx.py innan de används som fakta.
"""
import csv, datetime as dt, html, json, os, re, subprocess, sys, time

def _ua():
    v = os.environ.get("SEC_USER_AGENT")
    if not v:
        f = os.path.expanduser("~/.config/casereport/sec_user_agent")
        if os.path.exists(f): v = open(f).read().strip()
    if not v:
        sys.exit('Sätt miljövariabeln SEC_USER_AGENT (t.ex. "Namn namn@exempel.se") eller lägg den i ~/.config/casereport/sec_user_agent; SEC kräver identifierande User-Agent.')
    return v
UA = _ua()

def get(url):
    time.sleep(0.25)
    r = subprocess.run(["curl", "-sL", "-m", "120", "-A", UA, url], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"curl misslyckades: {url}")
    return r.stdout.decode("utf-8", "ignore")

def totext(raw):
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

# rad i tabellen -> möjliga us-gaap-taggar (första som finns används per år)
TAGS = {
 "intakt": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
 "kostnad_salda_varor": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
 "bruttovinst": ["GrossProfit"],
 "rorelseresultat": ["OperatingIncomeLoss"],
 "nettoresultat": ["NetIncomeLoss", "ProfitLoss"],
 "eps_utspadd": ["EarningsPerShareDiluted"],
 "aktier_utspadda": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
 "kassaflode_drift": ["NetCashProvidedByUsedInOperatingActivities"],
 "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
 "avskrivningar": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "DepreciationAmortizationAndAccretionNet"],
 "sbc": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"],
 "aterkop": ["PaymentsForRepurchaseOfCommonStock"],
 "utdelning": ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"],
 "fou": ["ResearchAndDevelopmentExpense"],
 "forsaljning_marknadsf": ["SellingAndMarketingExpense", "SellingGeneralAndAdministrativeExpense"],
 "kassa": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
 "skuld_langfristig": ["LongTermDebt", "LongTermDebtNoncurrent", "ConvertibleNotesPayable", "SeniorNotes"],
 "goodwill": ["Goodwill"],
 "tillgangar": ["Assets"],
 "eget_kapital": ["StockholdersEquity"],
 "skattekostnad": ["IncomeTaxExpenseBenefit"],
}

def annual(facts, tags, unit_pref=("USD", "USD/shares", "shares")):
    out = {}
    for tag in tags:
        if tag not in facts: continue
        for unit, arr in facts[tag]["units"].items():
            for a in arr:
                if a.get("form") not in ("10-K", "10-K/A") or a.get("fp") != "FY": continue
                s, e = a.get("start"), a["end"]
                if s:  # flödesposter ska vara ca ett år
                    d = (dt.date.fromisoformat(e) - dt.date.fromisoformat(s)).days
                    if not 350 <= d <= 380: continue
                cur = out.get(e)
                if cur is None or a["filed"] > cur["filed"]:
                    out[e] = dict(val=a["val"], filed=a["filed"], tag=tag)
        if out: return out  # första taggen som ger data
    return out

def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    ticker, outd = sys.argv[1].upper(), sys.argv[2]
    ny = int(sys.argv[sys.argv.index("--years") + 1]) if "--years" in sys.argv else 10
    os.makedirs(os.path.join(outd, "10k"), exist_ok=True)
    tick = json.loads(get("https://www.sec.gov/files/company_tickers.json"))
    row = next((v for v in tick.values() if v["ticker"].upper() == ticker), None)
    if not row: sys.exit("Hittar inte tickern hos SEC.")
    cik = int(row["cik_str"]); cik10 = f"{cik:010d}"

    # --- årsserie ur XBRL
    cf = json.loads(get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json"))["facts"].get("us-gaap", {})
    series = {k: annual(cf, v) for k, v in TAGS.items()}
    ends = sorted({e for s in series.values() for e in s})[-ny:]
    rows = []
    for e in ends:
        r = {"rakenskapsar_slut": e}
        for k, s in series.items():
            r[k] = s[e]["val"] if e in s else ""
        rows.append(r)
    def num(r, k):
        v = r.get(k); return float(v) if v not in ("", None) else None
    prev = None
    for r in rows:
        i, ebit = num(r, "intakt"), num(r, "rorelseresultat")
        da, sbc = num(r, "avskrivningar"), num(r, "sbc")
        cfo, cap = num(r, "kassaflode_drift"), num(r, "capex")
        r["tillvaxt_pct"] = round((i / num(prev, "intakt") - 1) * 100, 1) if prev and i and num(prev, "intakt") else ""
        r["rorelsemarginal_pct"] = round(ebit / i * 100, 1) if i and ebit is not None else ""
        r["ebitda_gaap_approx"] = round(ebit + da) if ebit is not None and da is not None else ""
        r["ebitda_marginal_pct"] = round((ebit + da) / i * 100, 1) if i and ebit is not None and da is not None else ""
        r["fcf"] = round(cfo - cap) if cfo is not None and cap is not None else ""
        r["fcf_marginal_pct"] = round((cfo - cap) / i * 100, 1) if i and cfo is not None and cap is not None else ""
        r["fcf_efter_sbc"] = round(cfo - cap - sbc) if cfo is not None and cap is not None and sbc is not None else ""
        r["sbc_pct_intakt"] = round(sbc / i * 100, 1) if i and sbc is not None else ""
        a1, a0 = num(r, "aktier_utspadda"), num(prev, "aktier_utspadda") if prev else None
        r["aktieantal_forandring_pct"] = round((a1 / a0 - 1) * 100, 1) if a1 and a0 else ""
        prev = r
    if rows:
        cols = list(rows[0].keys())
        with open(os.path.join(outd, "historik_ar.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
        with open(os.path.join(outd, "historik_ar.md"), "w") as f:
            f.write("# Årsserie ur XBRL (USD, flöden = räkenskapsår). Taggar: " +
                    ", ".join(f"{k}={next(iter(s.values()))['tag']}" for k, s in series.items() if s) + "\n\n")
            f.write("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n")
            for r in rows: f.write("| " + " | ".join(str(r[c]) for c in cols) + " |\n")
        print(f"Årsserie: {len(rows)} år ({ends[0]} – {ends[-1]})")
    else:
        print("Ingen årsserie i XBRL.")

    # --- alla 10-K
    extra = [sys.argv[i + 1] for i, x in enumerate(sys.argv) if x == "--extra-cik"]
    sub = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik10}.json"))
    pages = [sub["filings"]["recent"]]
    for fobj in sub["filings"].get("files", []):
        try: pages.append(json.loads(get("https://data.sec.gov/submissions/" + fobj["name"])))
        except Exception as ex: print("  äldre lista misslyckades:", fobj["name"], ex)
    ks = []
    for p in pages:
        for i in range(len(p["form"])):
            if p["form"][i] in ("10-K", "10-K405", "10-KSB"):
                ks.append((p["filingDate"][i], p["accessionNumber"][i], p["primaryDocument"][i], p.get("reportDate", [""] * len(p["form"]))[i]))
    for ec in extra:   # äldre 10-K från föregångarens CIK
        ecik = int(ec); esub = json.loads(get(f"https://data.sec.gov/submissions/CIK{ecik:010d}.json"))
        epages = [esub["filings"]["recent"]] + [json.loads(get("https://data.sec.gov/submissions/" + fo["name"])) for fo in esub["filings"].get("files", [])]
        for p in epages:
            for i in range(len(p["form"])):
                if p["form"][i] in ("10-K", "10-K405", "10-KSB"):
                    ks.append((p["filingDate"][i], p["accessionNumber"][i], p["primaryDocument"][i], p.get("reportDate", [""] * len(p["form"]))[i], ecik))
    ks = sorted(set(ks), reverse=True)[:ny]
    man = []
    for rec in ks:
        fdate, acc, doc, rep = rec[:4]; ccik = rec[4] if len(rec) > 4 else cik
        url = f"https://www.sec.gov/Archives/edgar/data/{ccik}/{acc.replace('-', '')}/{doc}"
        fn = f"10-K_{rep or fdate}.txt" if ccik == cik else f"10-K_cik{ccik}_{rep or fdate}.txt"
        try:
            open(os.path.join(outd, "10k", fn), "w").write(totext(get(url)))
            man.append(dict(file=fn, filed=fdate, fiscal_year_end=rep, url=url)); print("  ", fn)
        except Exception as ex:
            print("  fel", fdate, ex)
    json.dump(man, open(os.path.join(outd, "10k", "manifest_10k.json"), "w"), indent=1)
    print(f"Klart: {len(man)} årsrapporter. Saknas år (bolaget nyare än {ny} år?) ska stå i faktabasen.")

if __name__ == "__main__":
    main()
