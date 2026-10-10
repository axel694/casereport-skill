# Reverse DCF och tioårshistorik

Läs vid steg 2b (historik) och steg 5b (reverse DCF). Verktyg: `scripts/history_fetch.py`, `scripts/reverse_dcf.py`.

## Tioårshistorik (steg 2b)
Kör `python3 scripts/history_fetch.py TICKER källor/ --years 10`. Ger `historik_ar.md/csv` (årsserie ur XBRL med härledda mått) och alla 10-K som text i `källor/10k/`. Nyare bolag har färre år: skriv det i faktabasen, hitta inte på.
Läs inte alla 10 årsrapporter i sin helhet. Läs per rapport med `ctx.py`: Item 1 (verksamhet, förändring i beskrivningen över tid), Item 1A (nya/borttagna risker), Item 7 (MD&A), segmentnoten, skuldnoten, förvärvsnoten, aktieersättning, efterföljande händelser. Jämför första och sista rapporten för att se hur bolaget förändrats.
Leta aktivt efter mönster och skriv dem som Fakta (siffror) eller Bedömning (tolkning):
1. **Tillväxt och marginal över tid**: CAGR 3/5/10 år, när tillväxten accelererade eller avtog, marginal före/efter strategiskt skifte. Är senaste åren en avvikelse eller en fortsättning?
2. **Vinstkvalitet över cykeln**: FCF/nettoresultat, FCF efter SBC, SBC % av intäkt, ökande/minskande förvärvsrelaterade poster, justeringar mot GAAP över tid.
3. **Kapitalallokering**: återköp mot utspädning (aktieantal), förvärv mot organisk tillväxt, skuldnivå över tid, utdelning. Vad hände med avkastningen på förvärvat kapital? Nedskrivningar?
4. **Ledningens trovärdighet**: jämför tidigare guider/långsiktiga mål med utfall (hämta guide ur äldre pressmeddelanden/10-K). Hur ofta nåddes de? Ändrade de måttdefinitioner när det gick sämre?
5. **Riskernas utveckling**: vilka risker som tillkommit, försvunnit eller blivit konkreta (regleringar, kundkoncentration, plattformsberoende, rättsprocesser).
6. **Cyklicitet och chocker**: hur betedde sig intäkt/marginal i tidigare nedgångar (2008–09, 2020, 2022–23 om bolaget fanns)? Det är bear-casens verkliga bas.
7. **Basrater**: hur ofta har bolag i denna storlek/tillväxttakt hållit en hög tillväxt i ytterligare 5 år? Använd bara belagda källor; annars skriv att basrate inte kunnat beläggas.
Sammanfatta i `källor/monster.md` (mönster, belägg med år och källa, status) och redovisa i rapporten (sektion 8–9) och på slide "Tio år i siffror".

## Reverse DCF (steg 5b)
Syfte: i stället för att gissa framtiden, lös ut vilken framtid dagens kurs kräver, och jämför med historik och rimlighet. Det kompletterar EV/EBITDA-scenarierna och ersätter dem inte (värdering i scenarier sker på EV/EBITDA).

**Metod** (`reverse_dcf.py`): tio års projektion. År 1–5 intäktstillväxt C (den som löses ut), år 6–10 linjär nedtrappning till terminaltillväxt g. EBITDA-marginal går linjärt från TTM-nivå till slutmarginal. FCF = EBITDA − skatt på (EBITDA − D&A − SBC) − capex − ökning rörelsekapital − SBC (aktiebaserad ersättning behandlas som verklig kostnad). Terminalvärde med Gordon-modellen. C löses så att nuvärdet = EV (börsvärde + nettoskuld på samma datum).

**Obligatoriska antaganden som ska stå synliga på sliden och i rapporten**, var och ett med källa eller märkt "min uppskattning":
- Pris, datum, utspädda aktier, nettoskuld (datum), EV.
- Bas: TTM-intäkt och TTM-EBITDA-marginal (bolagets justerade; säg bas).
- Slutmarginal år 10 och varför (historiskt intervall, peers, bolagets mål).
- SBC, D&A, capex i % av intäkt (historiska medel från tioårsserien), rörelsekapital, skattesats (statutory vs cash).
- WACC (visa hur den byggs: riskfri ränta med datum och källa, ERP, beta med källa, kapitalstruktur) och terminaltillväxt (≤ långsiktig nominell BNP-tillväxt).
- Horisont och nedtrappningsregel.

**Utdata som ska redovisas:**
1. Implicerad intäkts-CAGR år 1–5 och vad den ger år 10 (intäkt, EBITDA, FCF); terminalvärdets andel av EV; implicerad exit-multipel.
2. Jämförelse mot historiskt CAGR (3/5/10 år), mot bolagets egna mål och mot marknadens/analytikernas konsensus om det går att belägga (datera, märk sekundärt).
3. Vad marknaden alltså "tror": en mening per antagande, i klartext.
4. **Känslighetstabeller (minst tre):** (a) implicerad CAGR för WACC × terminaltillväxt, (b) implicerad CAGR för WACC × slutmarginal, (c) värde per aktie för WACC × CAGR, med dagens kurs markerad. Visa också en "bear/bas/bull-trio" av egna CAGR-antaganden → värde per aktie, så att läsaren ser vad var och en betyder mot kursen.
5. Rimlighetskontroll: kräver kursen en marknadsandel/intäkt år 10 som är större än hela den adresserbara marknaden eller historiskt unik? Skriv det som Bedömning.
6. Begränsningar: terminalvärdet bär oftast 50–80 % av EV; små ändringar i WACC/g flyttar mycket; modellen är en spegel av kursen, inte en prognos.

**Hårda regler:** inga antaganden utan synlig siffra; WACC väljs inte baklänges för att "få det att gå ihop"; SBC får inte läggas tillbaka; samma EV som i EV/EBITDA-delen; kör `reverse_dcf.py` och använd dess utdata oförändrad på slides och i rapport (samma tal överallt).

## Kapitalintensiva bolag och bolag utan vinst
- **Tillväxtcapex och marginalramp:** sätt `capex_pct_tillvaxt` (extra capex per intäktsdollar i ökning) och `ar_marginal` (antal år till slutmarginal) i indata. Rörelsekapitalet sätts som andel av intäktsökningen (ur balansräkningen: kundfordringar + lager − leverantörsskulder, delat med TTM-intäkt).
- **När CAGR-lösningen inte hittas** (skriptet skriver "OVAN SÖKGRÄNSEN 150 %"): kursen går inte att motivera med antagandena. Redovisa det som resultat, visa vid vilken WACC och slutmarginal den ändå löses, och komplettera med **tabell D: implicit avkastning (IRR)** via `kansl_irr_cagr` i indata. Tabellen visar årlig avkastning vid dagens EV för givna tillväxtbanor och slutmarginaler och är det bästa sättet att visa vad som måste gå rätt.
- **Trailing EV/EBITDA meningslös** (EBITDA ≈ 0): värdera på framåtblickande uppskattad EBITDA (FY27E/FY28E) och visa dagens EV/EBITDA på dessa. Modellera kassaunderskott i scenarierna (investeringar, rörelsekapital) och låt det täckas med nya aktier till dagens kurs så att utspädningen syns i värdet per aktie.
- **Utspädning:** visa aktieantal över tid, ATM-/emissionshistorik, konvertibler (konverteringskurs mot kurs), warranter till kunder, och källornas olika aktieantal (10-Q omslag, bolagets guide, datafeed).
- **Kundfordran och koncentration:** läs 10-Q:s notis om kundkoncentration (andel av fordringar, betalvillkor) och lyft den som egen risk.
- **Non-GAAP:** jämför alltid bolagets "non-GAAP-vinst" med justerad EBITDA och kontrollera skatteeffektjusteringar.
- **Händelser efter senaste 10-Q:** läs alla 8-K sedan dess (nya emissioner, skuld, avtal) via SEC:s submissions-lista.
