# Presentationen (`<Bolag>_case.pptx`)

Beslutsunderlag för användaren, inte säljmaterial. Bred 16:9. Redigerbara objekt (egna textrutor, tabeller och **inbyggda diagram**), inga bilder av text. Teckensnitt Calibri, serif/Times i rubriker. Färger: marinblå `1F3864` (neutral information), sandfärgad `B8A38D`, mörkröd `C00000` för risk och det som talar emot, grå `D9D9D9` för förklaringsfält. Språk svenska. Inga siffror från licensierade terminaler. Källrad längst ner (typ "Källa: <Bolag> 10-K FY.., 10-Q Q.. och bolagets pressmeddelanden. Uppskattningar är mina."). Prisdatum på varje slide med värdering. Slidetitlar beskriver innehållet ("Skuld och finansiering"), de säljer inget ("Kraftigt underskattad"). Inga säljande adjektiv. Det som talar emot ska synas lika tydligt som det som talar för, och risker kommer före fördelar.

## Slide 1: Beslutsöversikt
Fyra delar (med implicerad CAGR från reverse DCF som en rad under "Vad kursen redan prisar") plus titel (bolag, kurs och prisdatum, börsvärde, EV) och källrad:
- **Uppe till vänster:** inbyggt kolumndiagram över justerad EBITDA (utfall, senaste kvartal x4 och min uppskattning för målåret) med tydlig bas. Ingen pil som säljer uppsida; en etikett med faktor mot nuvarande nivå räcker.
- **Uppe till höger:** "Vad du köper" (5 korta punkter: vad bolaget är, intäktsmix senaste kvartal, tillväxt och backlog med datum, skuld, kundkoncentration) och "Vad kursen redan prisar" (EV/EBITDA trailing och forward).
- **Nere till vänster (röd rubrik först):** "Det som talar emot" (3 punkter, huvudrisken först) och "Det som talar för" (3 punkter), lika stora rutor.
- **Nere till höger:** "Vad du måste tro" (3–4 antaganden) och en tabell break-even (0 %, +50 %, +100 %: EBITDA och multipel som krävs) samt scenariovärden bear/bas/bull med kurs.

## Övriga slides (cirka 14)
2. Vad bolaget gör, enkelt flöde: vem betalar, för vad, hur tjänar bolaget pengar; intäktsmix med kvalitet (återkommande mot engångs).
3. Siffror: tolv kvartal (bolagets intäktsmått och justerad EBITDA), sammanfattningstabell FY-3…FY1E.
4. Kunder och kontrakt: koncentration, kontraktstyper, backlog med definition och datum.
5. Skuld och finansiering: skuldtabell, förfallostruktur, kassa, utspädning, närstående.
6. Förvärv och stora affärer (om relevant): pris upfront/max, multipel på samma bas, utfall.
7. Vinstkvalitet: justerad mot GAAP, skatt, SBC, EPS som risk.
8. Värdering: EV-bygge, trailing och forward EV/EBITDA, peers om belagda, scenariotabell **EV/EBITDA** (bear/bas/bull) med antaganden, känslighetstabell EBITDA × multipel, kurs jämförd med varje scenario.
8b. **Tio år i siffror** (efter Värdering eller före Siffror): inbyggda diagram över årsserien (intäkt och marginal, FCF efter SBC, aktieantal) och 4–5 mönster ur tioårsläsningen med belägg.
8c. **Reverse DCF – vad kursen prisar in** (två slides): (1) antaganden i tabell med källa/märkning (pris, datum, EV, TTM-bas, slutmarginal, SBC, D&A, capex, rörelsekapital, skatt, WACC-bygge, g, horisont), implicerad CAGR och vad den ger år 10, terminalvärdets andel, jämförelse mot historiskt CAGR och mål. (2) tre känslighetstabeller (WACC × g, WACC × slutmarginal, värde per aktie WACC × CAGR) med dagens läge markerat, samt "vad marknaden tror" i klartext och begränsningar.
9. Break-even och vad du måste tro: tabell över nivåer för 0 %, +50 %, +100 % och de antaganden som krävs; vad som redan är inprisat.
10. Risker (före katalysatorer): tabell risk/varför/allvar, pre-mortem ("så förlorar man pengar").
11. Katalysatorer och kalender, och vad som skulle ändra bilden åt båda hållen.
12. Det vi inte vet: funnet (med källa), saknas, ej bekräftat/motsägelser.
13. Bilaga: ledning, insyn, ägare, källor.

## Bygge och kontroll
- Bygg med python-pptx (eller pptxgenjs). Använd `chart.replace_data` vid uppdatering så formatet behålls. Efter ändring: öppna filen med python-pptx för att se att den läses, och sök alla textrutor efter förbjudna ord ("our", terminalnamn) och efter gamla siffror.
- Quick Look (`qlmanage -t`, en slide åt gången genom att göra en kopia med bara den sliden) visar bara delvis diagram och byter typsnitt; en förhandsvisning duger för layout (att text ryms i rutor) men diagram verifieras via data. Öppna alltid filen åt användaren i PowerPoint (`open -a "Microsoft PowerPoint" fil`). Hänger PowerPoint-export via AppleScript: avbryt, den är opålitlig.
- Skriv över samma filer (inga v2/v3).
