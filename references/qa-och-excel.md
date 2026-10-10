# Q&A-dokumentet och Excel-modellen (bara på begäran)

## `<Bolag>_QA.docx` (Times New Roman 12, första person)
Avdelningar: 1. Tesen i 30 sekunder · 2. Vad bolaget är · 3. Siffrorna · 4. Vinstkvalitet · 5. Tillväxtmotor/tema och regler · 6. Största affären · 7. Värdering (EV/EBITDA) · 8. Risker och vad som bryter caset · 9. Kalender · 10. Frågor och svar · 11. Obesvarat och ska kollas härnäst.
- **Frågor och svar: minst 20.** Alltid med: "Vilka är dina tre drivare och din största risk?", "Varför är [huvudrisken] din största risk?", "Vad betalade förvärven egentligen?", "Hur stor är [temat] egentligen?" (svara ärligt om det inte redovisas), "Hur kommer du fram till avkastningen?", "Vad är konkurrensfördelen?", "Vad bevakar du och när säljer du?", insyn/likviditet/blankning, marginalens hållbarhet, koncentration, skuld, skatt/EPS-justeringar, stor kursnedgång (vad drev den).
- Svar: 5–10 meningar, siffror med datum, ärlig svaghet uttalad ("jag vet inte X, jag skulle fråga bolaget Y"), vad som får användaren att ändra sig. Aldrig siffror som inte är verifierade; uppskattningar uttalas som uppskattningar.
- Lägg till en kort "30 sekunder"-version av tre drivare och risken, och ett block "Siffror att kunna utantill" (6–8 tal med bas och datum).

## `<Bolag>_modell.xlsx`
Stil: Calibri Light 12, rutnät av, mörkblå rubrikrader med vit text, **blå text på ljusgul bakgrund = inmatning/hårdkodat ur filings**, svart = formel, tunn överkant på delsummor, tal `#,##0.0;(#,##0.0);-`, år med format `0"A"`/`0"E"`, flikfärger, smal kolumn A, en lista med källor i sista fliken.
Flikar (anpassa efter bolaget): **Income statement** (antaganden överst som inmatning: tillväxt, marginal, D&A, ränta, skatt, aktier; sedan resultaträkning med formler; kalibrering mot bolagets guide), **Quarterly** (tolv kvartal från pressmeddelanden, marginaler, y/y, årskontroll mot summa), **Acquisitions** (pris upfront/max, earnout, EBITDA-bas, multiplar som formler), **Leverage** (kassa, skuld, nettoskuld per datum, pro forma), **Valuation** (scenarier EV/EBITDA → värde per aktie, känslighetstabell EBITDA × multipel, upside mot kurs; EPS/skatt som memo), **Customers**, **Tema** (känslighet med bas och marginal tydligt angivna), **Sources & notes**.
- Alla formler levande; ändrar användaren en inmatningscell räknas allt om. Inga hårdkodade resultat i formelceller.
- Modellen ska landa på bolagets guide för året och ge samma scenariovärden som slides och rapport.
- Kontroll: `formulas`-biblioteket (`formulas.ExcelModel().loads(fil).finish().calculate()`) för att läsa beräknade värden och leta felkoder; jämför med slides.
- Inbyggda diagram (openpyxl BarChart/LineChart) för tolv kvartal och kundmix.
