import requests
import pywikibot
import re

# Verbindung zur deutschen Wikipedia
site = pywikibot.Site("de", "wikipedia")

# Die zu durchsuchende Seite
page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen"
#page_title = "Benutzer:ChemoBot/Tests/Fehlende Substanzen"
page = pywikibot.Page(site, page_title)

# Seite abrufen
text = page.text

# Regulärer Ausdruck für Zeilen mit CAS-Nummer und ohne Wikidata-Link
pattern = re.compile(r"^.*\]\] \(\s*(\d{2,8}-\d{2}-\d)(.*)", re.MULTILINE)

# Ergebnisse speichern
fehlende_wd_einträge = []

for match in pattern.finditer(text):
    wd = match.group(2).strip()
    cas_nummer = match.group(1).strip()
    
    # Falls kein "wd:"-Eintrag vorhanden ist
    if ":d:" not in match.group(2):
        fehlende_wd_einträge.append(cas_nummer)

# Ergebnisse ausgeben
print(f"Prüfe Substanzen ohne Wikidata-Eintrag: {len(fehlende_wd_einträge)}")
changed = 0

for i, cas in enumerate(fehlende_wd_einträge, 1):  # Counter hinzufügen
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