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
pattern = re.compile(r"^.*\]\] \(\s*(\d{2,7}-\d{2}-\d)(.*)", re.MULTILINE)

# Ergebnisse speichern
fehlende_wd_einträge = []

for match in pattern.finditer(text):
    wd = match.group(2).strip()
    cas_nummer = match.group(1).strip()
    
    # Falls kein "wd:"-Eintrag vorhanden ist
    if ":d:" not in match.group(2):
        fehlende_wd_einträge.append(cas_nummer)

# Ergebnisse ausgeben
print("Substanzen ohne Wikidata-Eintrag:")
for cas in fehlende_wd_einträge:
    print(f"{cas}")
    url = f"https://tools.wmflabs.org/wikidata-todo/resolver.php?prop=231&value={cas}"  # Beispiel für eine umleitende URL
    response = requests.get(url, allow_redirects=True)

    # Regulärer Ausdruck zum Extrahieren der Nummer nach "Q"
    match = re.search(r"url=https://www.wikidata.org/wiki/(Q\d+)", response.text)

    if match:
        q_number = match.group(1)  # Die gefundene Nummer
        print("Gefundene Q-Nummer:", q_number)
        page.text = page.text.replace(f"({cas})", f"({cas}, [[:d:{q_number}|wd]])")

page.save("update wikidata entries")