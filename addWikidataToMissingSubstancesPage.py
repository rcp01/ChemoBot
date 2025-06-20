import requests
import pywikibot
import re
from helperfunctions import translate_substance_name_to_englisch

def finde_wikidata_item(name):
    wikidatasite = pywikibot.Site("wikidata", "wikidata")
    repo = wikidatasite.data_repository()
    sprache="de"
    
    # Suchanfrage an Wikidata
    search_results = wikidatasite.search(name, total=5, namespaces=[0])

    for page in search_results:
        # print(f"Seite {page.title()} gefunden für {name}")
        seite = pywikibot.Page(wikidatasite, page.title())
        if seite.exists():
            item = pywikibot.ItemPage(repo, seite.title())
            item.get()
            labels = item.labels
            # print(f"labels = {labels}")
            if sprache in labels and labels[sprache].lower() == name.lower():
                return item.id  # z.B. "Q123456"
   
    sprache="en"
    name = translate_substance_name_to_englisch(name)
    #print(name)
    search_results = wikidatasite.search(name, total=5, namespaces=[0])
    
    for page in search_results:
        # print(f"Seite {page.title()} gefunden für {name}")
        seite = pywikibot.Page(wikidatasite, page.title())
        if seite.exists():
            item = pywikibot.ItemPage(repo, seite.title())
            item.get()
            labels = item.labels
            # print(f"labels = {labels}")
            if sprache in labels and labels[sprache].lower() == name.lower():
                return item.id  # z.B. "Q123456"

    return None  # Kein Treffer gefunden

# Verbindung zur deutschen Wikipedia
site = pywikibot.Site("de", "wikipedia")

# Die zu durchsuchende Seite
page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen"
#page_title = "Benutzer:ChemoBot/Tests/Fehlende Substanzen"
page = pywikibot.Page(site, page_title)

# Seite abrufen
text = page.text

# Regulärer Ausdruck für Zeilen mit CAS-Nummer und ohne Wikidata-Link
pattern = re.compile(r"^\[\[(.*?)\]\] \(\s*(\d{2,8}-\d{2}-\d)(.*)", re.MULTILINE)

# Ergebnisse speichern
fehlende_wd_einträge = []

for match in pattern.finditer(text):
    wd = match.group(3).strip()
    cas_nummer = match.group(2).strip()
    name = match.group(1).strip()
    
    # Falls kein "wd:"-Eintrag vorhanden ist
    if ":d:" not in match.group(3):
        fehlende_wd_einträge.append((name, cas_nummer))

# Ergebnisse ausgeben
print(f"Prüfe Substanzen ohne Wikidata-Eintrag: {len(fehlende_wd_einträge)}")
changed = 0

for i, (name, cas) in enumerate(fehlende_wd_einträge, 1):  # Counter hinzufügen
    print(f"{i}/{len(fehlende_wd_einträge)}: Check Wikidata entry for CAS {cas}")  # Ausgabe mit laufender Nummer
    url = f"https://tools.wmflabs.org/wikidata-todo/resolver.php?prop=231&value={cas}"  # Beispiel für eine umleitende URL
    response = requests.get(url, allow_redirects=True)

    # Regulärer Ausdruck zum Extrahieren der Nummer nach "Q"
    match = re.search(r"//www.wikidata.org/wiki/(Q\d+)", response.text)

    if match:
        q_number = match.group(1)  # Die gefundene Nummer
        print("Gefundene Q-Nummer:", q_number, " für CAS ", cas)
        page.text = page.text.replace(f"({cas})", f"({cas}, [[:d:{q_number}|wd]])")
        changed += 1
    else:
        ret = finde_wikidata_item(name)
        if (ret):
            q_number = ret
            print("Gefundene Q-Nummer per Namenssuche:", q_number, " für CAS ", cas)
            page.text = page.text.replace(f"({cas})", f"({cas}, [[:d:{q_number}|wd]])")
        else:
            url = f"https://www.ncbi.nlm.nih.gov/pccompound?term=%22{cas}%22%5BSynonym%5D"  # Beispiel für eine umleitende URL
            response = requests.get(url, allow_redirects=True)
              
            match = re.search("Quoted phrase not found", response.text)
            if match:
                print("Not found in Pubchem")
            else:
                match = re.search(r"https://pubchem\.ncbi\.nlm\.nih\.gov/compound/(\d+)", response.text)
                if match:
                    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{match.group(1)}/JSON/?response_type=display"
                    response = requests.get(url, allow_redirects=True)
                    match = re.search(r"//www.wikidata.org/wiki/(Q\d+)", response.text)
                    if match:
                        q_number = match.group(1)  # Die gefundene Nummer
                        print("Gefundene Q-Nummer in Pubchem:", q_number, " für CAS ", cas)
                        page.text = page.text.replace(f"({cas})", f"({cas}, [[:d:{q_number}|wd]])")
                        changed += 1
                    else:
                        print("Not found in Pubchem page")
                else:
                    print(response.text) 

page.save(f"Ergänze fehlende Wikidata Einträge anhand suche nach CAS Nummer für {changed} von {len(fehlende_wd_einträge)} Einträgen ohne Wikidata")
print(f"{changed} von {len(fehlende_wd_einträge)} Einträgen ohne Wikidata ergänzt")