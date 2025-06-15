# Konvertor datových souborů mezi Canoe123 a Eskymo

Soubor `eskymo123-conv.py` je skript v Pythonu na převod dat mezi Eskymo (CSV)
a Canoe123 (XML).

## Před závodem (import startovních listin do Canoe123)

Z Eskyma se do Canoe123 dají zkopírovat startovní listiny
takto:

1. V Eskymu připravte startovní listiny a každý list se startovní listinou
   uložte do samostatného souboru ve formátu CSV.

1. V Canoe123 vytvořte nový závod a ukončete program. Pokud chcete v Canoe123
   použít startovní čísla z Eskyma, zaškrtněte na kartě _Event Data
   / Properties_ volbu _Assign Bibs Eventwide in Participants_.

1. Pro každý CSV soubor, např. `k1m_sl.csv`, spusťte

        python3 eskymo123-conv.py -c e2c -C K1M k1m_sl.csv sl_K1M.xml

1. V libovolném textovém editoru z každého XML souboru smažte tagy `<root>`
   a `</root>` (1. a poslední řádek).

1. Zbylý obsah všech XML souborů (definice <Participants>) nakopírujte na
   začátek datového XML souboru Canoe123.

1. Nastartujte Canoe123. Pokud je vše proběhlo správně, bude vidět seznam
   účastníků a je možné vygenerovat startovní listiny.

Pokud používáte Linux (včetně WSL ve Windows), dají se kroky 3 a 4 provést
automaticky pro všechny kategorie skriptem `eskymo123-conv-sl.sh`, který vytvoří
jeden soubor `sl.xml` obsahující sloučený seznam účastníků ze všech kategorií.

## Po závodě (export výsledků do Eskyma)

Po ukončení závodu je možné příkazem pro každou kategorii, např.

    python3 eskymo123-conv.py -c c2e -C K1M canoe123-zavod.xml K1M.csv

vyexportovat výsledky ve formátu CSV. Každý řádek vytvořeného CSV souboru
obsahuje startovní číslo, časy a penalizace z obou jízd. Časy a penalizace je
pak potřeba vložit do příslušných sloupců listu s výsledky v Eskymu.

Aby bylo zajištěné, že obsah CSV se dá vložit se správným pořadím řádků
(startovních čísel) do výsledkového listu v Eskymu, je potřeba před spuštěním
`python eskymo123-conv.py` nejprve exportovat výsledkový list (s prázdnými časy
a penalizacemi). Tento soubor se pak zadává jako poslední parametr při volání
skriptu a bude přepsán exportovanými výsledky. Alternativně je možné tento
soubor přidat jako další parametr skriptu, pak zůstane zachován:

    python3 eskymo123-conv.py -c c2e -C K1M canoe123-zavod.xml K1M-out.csv K1M-export.csv

Pokud jsou v jednom XML souboru data více závodů z více dnů (typicky sobota
i neděle při víkendových závodech), je potřeba přidat při volání skriptu
parametr `--day X`, kde X je číslo dne v měsíci. Např. pro závody v sobotu
31.5. a neděli 1.6. spustíme skript dvakrát. Jednou použijeme `--day 31`,
podruhé `--day 1`.
