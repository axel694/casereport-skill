#!/usr/bin/env python3
"""Hämtar primärkällor för ett USA-noterat bolag från SEC EDGAR.

Användning: python3 edgar_fetch.py TICKER UTMAPP [--quarters 12]

Sparar i UTMAPP:
  pr_YYYY-MM-DD.txt   resultatpressmeddelanden (8-K punkt 2.02, bilaga 99.1) som ren text
  10-K_*.txt, 10-Q_*.txt   senaste årsrapport (2 st) och kvartalsrapporter (4 st) som ren text
  companyfacts.json   XBRL-fakta (maskinläsbara siffror)
  facts_summary.txt   kompakt tabell över nyckeltal ur XBRL (senaste 12 kvartal + år)
  manifest.json       varje fil med källa-URL, rapportdatum och typ (använd för källhänvisningar)
Kräver bara Python 3 och curl. SEC kräver User-Agent med namn och e-post.
"""
import json, os, re, subprocess, sys, time, html

def _ua():
    v = os.environ.get("SEC_USER_AGENT")
    if not v:
        f = os.path.expanduser("~/.config/casereport/sec_user_agent")
        if os.path.exists(f): v = open(f).read().strip()
    if not v:
        sys.exit('Sätt miljövariabeln SEC_USER_AGENT (t.ex. "Namn namn@exempel.se") eller lägg den i ~/.config/casereport/sec_user_agent; SEC kräver identifierande User-Agent.')
    return v
UA = _ua()

def get(url, binary=False):
    time.sleep(0.25)  # SEC: max 10 anrop/s, vi håller oss långt under
    r = subprocess.run(["curl", "-sL", "-m", "90", "-A", UA, url], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"curl misslyckades: {url}")
    return r.stdout if binary else r.stdout.decode("utf-8", "ignore")

def totext(raw):
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    ticker, out = sys.argv[1].upper(), sys.argv[2]
    nq = int(sys.argv[sys.argv.index("--quarters") + 1]) if "--quarters" in sys.argv else 12
    os.makedirs(out, exist_ok=True)
    tick = json.loads(get("https://www.sec.gov/files/company_tickers.json"))
    row = next((v for v in tick.values() if v["ticker"].upper() == ticker), None)
    if not row:
        sys.exit(f"Hittar inte {ticker} hos SEC (inte USA-noterat eller fel ticker).")
    cik = int(row["cik_str"]); cik10 = f"{cik:010d}"
    print(f"{ticker} = {row['title']}, CIK {cik10}")
    sub = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik10}.json"))
    rec = sub["filings"]["recent"]
    n = len(rec["form"])
    items = [dict(form=rec["form"][i], acc=rec["accessionNumber"][i], date=rec["filingDate"][i],
                  doc=rec["primaryDocument"][i], items=rec.get("items", [""] * n)[i]) for i in range(n)]
    manifest = {"ticker": ticker, "name": row["title"], "cik": cik10, "files": []}

    def base(acc): return f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}"

    # 1) Resultatpressmeddelanden
    earn = [x for x in items if x["form"] == "8-K" and "2.02" in x["items"]][:nq]
    for x in earn:
        try:
            idx = json.loads(get(base(x["acc"]) + "/index.json"))
            names = [d["name"] for d in idx["directory"]["item"]]
            ex = next((m for m in names if re.search(r"ex(hibit)?[-_]?99", m, re.I) and m.lower().endswith((".htm", ".html"))), None)
            if not ex:
                print("  hoppar över (ingen bilaga 99):", x["date"]); continue
            url = base(x["acc"]) + "/" + ex
            fn = f"pr_{x['date']}.txt"
            open(os.path.join(out, fn), "w").write(totext(get(url)))
            manifest["files"].append(dict(file=fn, type="earnings_pr", date=x["date"], url=url))
            print("  pressmeddelande", x["date"])
        except Exception as e:
            print("  fel", x["date"], e)

    # 2) 10-K (2 st) och 10-Q (4 st)
    for form, k in (("10-K", 2), ("10-Q", 4)):
        for x in [y for y in items if y["form"] == form][:k]:
            url = base(x["acc"]) + "/" + x["doc"]
            fn = f"{form}_{x['date']}.txt"
            try:
                open(os.path.join(out, fn), "w").write(totext(get(url)))
                manifest["files"].append(dict(file=fn, type=form, date=x["date"], url=url))
                print("  ", form, x["date"])
            except Exception as e:
                print("  fel", form, x["date"], e)

    # 3) XBRL-fakta
    try:
        cf = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json")
        open(os.path.join(out, "companyfacts.json"), "w").write(cf)
        manifest["files"].append(dict(file="companyfacts.json", type="xbrl", date=time.strftime("%Y-%m-%d"),
                                      url=f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json"))
        facts = json.loads(cf)["facts"].get("us-gaap", {})
        tags = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "GrossProfit", "OperatingIncomeLoss",
                "NetIncomeLoss", "EarningsPerShareDiluted", "WeightedAverageNumberOfDilutedSharesOutstanding",
                "CashAndCashEquivalentsAtCarryingValue", "LongTermDebt", "NetCashProvidedByUsedInOperatingActivities",
                "PaymentsToAcquirePropertyPlantAndEquipment", "DepreciationDepletionAndAmortization", "Goodwill"]
        lines = []
        for t in tags:
            if t not in facts: continue
            for unit, arr in facts[t]["units"].items():
                q = {}
                for a in arr:
                    if a.get("fp") in ("Q1", "Q2", "Q3", "Q4", "FY") and a.get("form") in ("10-K", "10-Q"):
                        key = (a["end"], a.get("start", ""))
                        q[key] = a
                rows = sorted(q.values(), key=lambda a: a["end"])[-nq - 6:]
                lines.append(f"## {t} [{unit}]")
                for a in rows:
                    lines.append(f"{a.get('start','')}→{a['end']}  {a['fp']}  {a['val']}  ({a['form']} filed {a['filed']})")
        open(os.path.join(out, "facts_summary.txt"), "w").write("\n".join(lines))
        manifest["files"].append(dict(file="facts_summary.txt", type="xbrl_summary", date=time.strftime("%Y-%m-%d"), url="(härledd ur companyfacts.json)"))
    except Exception as e:
        print("  XBRL misslyckades:", e)

    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1, ensure_ascii=False)
    print(f"Klart: {len(manifest['files'])} filer i {out}")

if __name__ == "__main__":
    main()
