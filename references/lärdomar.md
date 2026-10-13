# Lärdomar (problem → orsak → lösning)

Läs före varje körning (steg 0). Lägg till en rad direkt när något fastnar eller löses. Lärdomar som förekommit två gånger flyttas till `fallgropar.md` eller arbetsflödet. Håll listan kort och allmän (inga personuppgifter).

Format: **Problem** · orsak · lösning · status (införd i: skript / fallgropar / steg / bara anteckning).

## Hämtning och källor
- **Pressmeddelanden hittades inte** · bilagan hette `exhibit991…`, inte `ex99…` · regexen i `edgar_fetch.py` accepterar nu `ex(hibit)?[-_]?99` · införd i skript.
- **Pressmeddelanden saknas för senaste kvartalen** · bilagan hette `…xearningsre.htm` (varken ex99 eller exhibit99) · `edgar_fetch.py` provar nu 1) ex99-namn, 2) namn med earnings/press/release/results, 3) största övriga htm-filen · införd i skript (testad på ett bolag, 12 av 12 pr hittade).
- **Äldre 10-K saknas (bolaget bytt moderbolag/CIK)** · SEC lagrar föregångaren under annan CIK · `history_fetch.py --extra-cik CIK` hämtar dem som `10-K_cik…` · införd i skript.
- **Bara 5 av 10 årsrapporter finns** · bolaget nylistat · säg det i faktabasen och använd XBRL-serien för resten · anteckning.
- **Tidsserier i XBRL blandar total och fortsättande verksamhet** (efter avyttring/omklassning) · senaste 10-K omräknar bara jämförelseåren · använd segmentnoterna eller omräknade pressmeddelanden och märk basen per år · fallgropar #7.
- **Nettoresultat saknas i XBRL för enskilda år** · bolaget använder taggen `ProfitLoss` · prova flera taggar (`NetIncomeLoss`, `ProfitLoss`, `NetIncomeLossAvailableToCommonStockholdersBasic`) · anteckning.
- **Aktieantal före/efter split är inte jämförbara i XBRL** · split justeras inte bakåt i äldre rapporter · dividera inte serier över splitten utan justering · anteckning.
- **Bolaget slutar redovisa ett mått** (t.ex. justerad EBITDA i ett senare pressmeddelande) · byte av nyckeltal · använd bolagets senast guidade marginal som märkt uppskattning och skriv att måttet utgått · fallgropar.
- **Händelser efter senaste 10-Q** (emissioner, lån, avtal) missas · de ligger bara i 8-K · lista alla 8-K sedan 10-Q via `submissions`-JSON och läs punkterna 1.01, 2.03, 5.02 · steg 2.
- **Sekundär datafeed skiljer sig från bolagets siffror** (aktieantal, EV, EBITDA) · annan definition eller äldre datum · räkna själv ur bolagets filing och förklara skillnaden i faktabasen · fallgropar #2, #4.
- **Motsägelser mellan två års 10-K** (samma uppgift olika) · tryckfel eller omklassning · använd en konsekvent källa och flagga det · fallgropar #19.

## Läsa filings
- **Sökträffar i inline-XBRL-huvudet** (tusentals taggar) bråkar med textsökning · huvudet ligger före själva dokumentet; rubrikfraser varierar i versaler/format · `ctx.py` skär nu bort allt före "UNITED STATES SECURITIES AND EXCHANGE COMMISSION" (skiftlägesokänsligt) · införd i skript.
- **Tal i SEC-text har mellanslag** (`$ 3,053`, `$ 29 billion`, ord klyvs som `m illion`) · konverteringen från HTML · sök på kortare delsträngar eller normalisera blanksteg · anteckning.
- **Procentrader i 10-K har etiketter i annan ordning än tabellen** · textutdragets kolumnordning · räkna procent själv ur beloppen och jämför med meningen i texten · anteckning.
- **Viktigaste risker står i 10-Q:s "Recent developments" och noter, inte i 10-K** (t.ex. garantier, finansieringsplattformar, kundkonvertibler) · nya åtaganden dyker upp mellan årsrapporterna · läs 10-Q:s noter om åtaganden, garantier och kundkoncentration alltid · steg 2.
- **Orderåtaganden (RPO) kan hoppa** · ett enskilt långtidskontrakt · läs definition och hur stor del som intäktsförs inom 12 månader innan den används som "backlog" · fallgropar #17.

## Modell och värdering
- **Reverse DCF löser inte ut någon CAGR** (kapitalintensivt/vinstlöst bolag, hög EV mot låg EBITDA) · sökgränsen nås · skriptet säger nu "ovan sökgränsen"; komplettera med IRR-tabell (`kansl_irr_cagr`) och tillväxtcapex (`capex_pct_tillvaxt`), marginalramp (`ar_marginal`) · införd i skript och referens.
- **Trailing EV/EBITDA meningslös** (EBITDA ≈ 0) · värdera på uppskattad framtida EBITDA och visa EV/intäkt · fallgropar #8.
- **Egna räknefel i texten** (jämförde 7,5 % med statsräntan åt fel håll, fel år-5-intäkt, fel tabellvärde) · värden skrevs för hand · hämta alla tal i text ur modellen/JSON via kod och kontrollräkna jämförelser ("högre/lägre än") · steg 9.
- **Slutsatser skrevs före beräkningen** · mönstertexten hann före reverse DCF · skriv slutsatser först efter att modellen körts; uppdatera `monster.md` i efterhand · steg 10.
- **Scenarier utan finansieringsbehov blir missvisande för kapitalintensiva bolag** · kassaunderskott ger utspädning · täck underskott med nya aktier till dagens kurs så att utspädningen syns · fallgropar #24.
- **Backstops, garantier och kundkonvertibler** ingår inte i nettoskulden · villkorliga åtaganden · redovisa som egen riskpost och i pre-mortem, och jämför beloppet med nettoskuld och börsvärde · fallgropar.

## Bygge och granskning
- **Tabeller flöt ut över varandra** · tomma celler får standardstorlek 18 pt · ersätt tom cell med ett hårt blanksteg (finns i `pptlib.py`) · införd i bibliotek.
- **Tjocka tabellramar i pptx** · tabellstilen · stil-id `{2D5ABB26-0587-4C30-8999-92F81FD0307C}` (ingen stil/inga linjer) · införd i bibliotek.
- **Kan inte rendera hela decket** (inget LibreOffice, PowerPoint-export hänger) · Quick Look visar bara första sliden · `scripts/rendera.py` gör en kopia per slide och tar miniatyr med `qlmanage -t` · införd i verktyg.
- **Text passar inte i rutor** · ingen rendering i förväg · `pptlib.py` har en enkel passningskontroll (uppskattad höjd mot ruta) som körs vid bygget · införd i bibliotek.
- **Fel i diagramtext/etiketter syns inte i förhandsvisning** · Quick Look ritar diagram ofullständigt · kontrollera diagramdata via koden, inte bilden · anteckning.
- **Faktagranskning gjordes för sent** · siffror skrevs in innan de verifierats · skripta kontrollen: lista alla nyckeltal som söksträngar mot källfilerna (`granska.py`-mönster: 40–65 kontroller) plus omräkning av summor och framåtkörning av modellen · steg 9.
- **Samma sak sägs i flera filer** (slides, rapport, notering) · manuell kopiering · allt som är ett tal kommer ur en gemensam `modell.py` · steg 6.

## Miljö och verktyg (macOS)
- **`timeout` finns inte** i zsh på macOS · använd `perl -e 'alarm N; exec @ARGV'` eller kör i bakgrunden · anteckning.
- **`sed -i` kräver `-i ''`** på macOS · använd `python3 -c`/Edit-verktyget för ersättningar · anteckning.
- **zsh tolkar `=====` i `echo`** som kommando · citera strängen · anteckning.
- **`/tmp` rensas mellan sessioner** (venv och hjälpfiler försvinner) · återskapa venv enligt steg 0, och lägg återanvändbara hjälpfiler i skillets `scripts/` i stället för i scratch · införd (hjälpbibliotek i `scripts/`).
- **Rtk/bash-wrappers ger tom utskrift för vissa sökningar** · använd Python för mönstersökning i filer · anteckning.
- **Sökning i stora eller molnsynkade mappar tar lång tid** · sök bara i angivna mappar, aldrig rekursivt över hela användarmappen · anteckning.

## Process
- **Samma uppställning byggdes om från noll för varje bolag** · hjälpkod låg i förra bolagets mapp · `pptlib.py`, `docxlib.py`, `rendera.py` ligger nu i `scripts/`; bygg bolagets `bygg_pptx.py`/`bygg_docx.py`/`modell.py` ovanpå dem · införd.
- **Bolag som inte passar mallen** (förlustbolag, kapitalintensiva, förvärvsdrivna, konglomerat) · mallen antar lönsamhet och EBITDA · se referensen "Kapitalintensiva bolag och bolag utan vinst"; för förvärvsdrivna bolag: redovisa alla affärer med pris, finansiering, intäktsbidrag och avyttringar (`rapportstruktur.md`, avsnitt 7) · införd.
- **Kontraktsdatum och leveransplan skrevs från minnet/fel pressmeddelande** (ett avtal daterades fel och en anläggning fick fel etikett) · ta datum, MW och leveransplan ur senaste 10-Q/10-K (avsnitt om avtal), inte ur ett äldre pr; granska.py ska söka datumsträngen i just den filen · införd som kontroll i granska-mönstret.
- **Bolag med orealiserade hedgar (kraft, råvaror)** · GAAP-intäkt och nettoresultat svänger av mark-to-market · använd bolagets justerade EBITDA och kontraktsintäkt, räkna preferensaktier och forward-åtaganden som skuld i EV, och visa båda måtten · anteckning.
- **Bolag yngre än tio år** · history_fetch ger färre år · skriv "åtta år" i rubrik och text i stället för att fylla med tomma år · anteckning.


## FICO (2026-10)
- **Quick Look hänger** (rendera.py) · qlmanage ger inget svar · kontrollera layout med `kontrollera_leverans.py` (bounding boxes, fit-check) och öppna filen i PowerPoint · införd i skript.
- **Punktdecimaler i svensk text** (21.367) · f-strängar med `:.3f` · använd `fmt(v, d)` överallt; `kontrollera_leverans.py` söker efter dem · införd i skript.
- **Egna räknefel i mönstertext** (3-års-CAGR, återköpssumma, tillväxtår) · skrevs för hand före modellen · hämta alla tal ur modellen; skriv mönster efter modellkörning · steg 10 (upprepning, nu regel).
- **Diagramunderlag saknas i rapporten** · slides hade diagram vars värden inte stod i texten · lägg bilaga med diagramunderlag (bilaga F) · införd i steg 9g.
- **Stackade diagram** saknades i pptlib · lagt till `kind="stack"` · införd.
