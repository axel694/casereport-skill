# casereport

Ett skill för Claude Code som bygger ett faktagranskat **beslutsunderlag** om ett USA-noterat aktiecase från bara en ticker (`/casereport TICKER`).

Det är inte ett säljmaterial och ger ingen köp- eller säljrekommendation. Det ger siffror ur primärkällor, argument för och emot, vad som redan är inprisat, vad man måste tro, break-even, scenarier på EV/EBITDA och en **reverse DCF** med känslighetstabeller.

## Arbetsflöde i korthet
1. Hämta SEC-data (10-K, 10-Q, pressmeddelanden, XBRL) och tio års årsrapporter.
2. Läs källorna i sin kontext och bygg en faktabas (varje påstående med källa och status: bekräftad / uppskattning / ej bekräftat).
3. Hitta mönster över tio år (tillväxt, marginal, kapitalallokering, ledningens trovärdighet, kundkoncentration, utspädning).
4. Värdera på EV/EBITDA i bear/bas/bull, räkna break-even och kör reverse DCF (vad kursen kräver av framtiden).
5. Bygg rapport (docx) och presentation (pptx med inbyggda diagram).
6. Faktagranska två gånger: omhämtning mot källor, konsistens, motprövning, omkörning av modellen.

## Innehåll
- `SKILL.md`: arbetsflöde och hårda regler
- `references/`: fallgropar, rapport- och slidestruktur, reverse DCF och tioårshistorik, valfritt Q&A/Excel
- `scripts/`: `edgar_fetch.py` (SEC-hämtning), `history_fetch.py` (tio års XBRL och 10-K), `reverse_dcf.py` (reverse DCF och IRR-tabell), `ctx.py` (läs en siffra i sin kontext)

## Installera
```bash
git clone https://github.com/<ditt-konto>/casereport-skill ~/.claude/skills/casereport
export SEC_USER_AGENT="Ditt Namn din@epost.se"   # SEC kräver en identifierande User-Agent
```
Starta sedan Claude Code och kör `/casereport TICKER`. Skripten kräver Python 3 och `curl`; rapport och presentation byggs med `python-pptx`, `python-docx` och `matplotlib` (skapas i en venv enligt SKILL.md). Skillet är skrivet på svenska; byt språk genom att be om det.

## Förbehåll
Underlag och modeller bygger på offentliga filings och mina antaganden. De är inte finansiell rådgivning.
