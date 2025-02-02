import pywikibot
import re
import time
from collections import defaultdict

def get_missing_substances(site, page_title):
    """Extrahiert die Liste der fehlenden Substanzen von der Wikipedia-Seite."""
    page = pywikibot.Page(site, page_title)
    content = page.text
    #substances = re.findall(r'\[\[(.*?)\]\] \(.*\[\[:d:(Q\d+)', content)
    substances = re.findall(r'\[\[([^|\]]+)[^\]]*\]\] \(.*\[\[:d:(Q\d+)', content)
    # print(substances)
    return substances

def count_incoming_links(site, title):
    """Zählt die Anzahl der eingehenden Links auf eine Seite in der Wikipedia."""
    page = pywikibot.Page(site, title)
    return len(list(page.backlinks(namespaces=[0])))  # Nur Artikel-Namensraum

def has_german_wikipedia_link(site, wikidata_id):
    repo = site.data_repository()  # Daten-Repository für Wikidata
    item = pywikibot.ItemPage(repo, wikidata_id)  # Wikidata-Item laden
    
    try:
        item.get()  # Daten abrufen
        if 'dewiki' in item.sitelinks:
            # print(f"{wikidata_id} hat einen Link zu: {item.sitelinks['dewiki'].title}")
            return True
        else:
            # print(f"{wikidata_id} hat KEINEN Link zu einer deutschen Wikipedia-Seite.")
            return False
    except Exception as e:
        print(f"Fehler beim Abrufen von {wikidata_id}: {e}")
        return False

def count_wikipedia_languages(site, wikidata_id):
    repo = site.data_repository() # Daten-Repository für Wikidata
    item = pywikibot.ItemPage(repo, wikidata_id)  # Wikidata-Item laden

    try:
        item.get()  # Daten abrufen
        # Filtere nur Wikipedia-Sprachlinks (die Endung '.wikipedia.org' haben)

        language_count = len(item.sitelinks)  # Anzahl der Sprachlinks zählen
        # print(f"{wikidata_id} hat {language_count} Links zu Wikipedia-Artikeln.")
 
        wikipedia_links = [site for site in item.sitelinks if (site.endswith('wiki') and not site == "commonswiki" )]
        language_count = len(wikipedia_links)  # Anzahl der Wikipedia-Sprachlinks

        # print(f"{wikidata_id} hat Wikipedia-Artikel in {language_count} Sprachen.")
        return language_count
    except Exception as e:
        print(f"Fehler beim Abrufen von {wikidata_id}: {e}")
        return -1

def update_wikipedia_page(site, results):
    page = pywikibot.Page(site, "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Zusatzinformationen")
    content = page.text
    
    # Trenne den vorhandenen Inhalt in den Teil vor "Zusatzinformationen" und den Rest
    match = re.search(r'(^.*?)(==\s*Zusatzinformationen\s*==)', content, re.DOTALL)
    if match:
        pre_text = match.group(1).strip()
        new_content = f"{pre_text}\n\n== Zusatzinformationen ==\n"
    else:
        new_content = "== Zusatzinformationen ==\n"
    
    for substance, links, german, langs, wikidata in results:
        german_text = "(dabei auch anderer Artikel in Deutsch) " if german else ""
        new_content += f"* {links:3d} Link(s) auf und in [[:d:{wikidata}|{langs:3d}]] anderen Sprachen {german_text}vorhanden für [[{substance}]]\n"
    
    # Seite aktualisieren
    page.text = new_content
    page.save(summary="Automatische Aktualisierung der Zusatzinformationen")


def human_readable_time_difference(start_time, end_time):
    """
    Gibt die Zeitdifferenz zwischen zwei datetime-Objekten in menschlich lesbarer Form zurück.

    :param start_time: Das Start-datetime-Objekt.
    :param end_time: Das End-datetime-Objekt.
    :return: Ein String, der die Zeitdifferenz in einer lesbaren Form darstellt.
    """
    # Berechne die Differenz
    delta = end_time - start_time
    
    # Extrahiere Tage, Stunden, Minuten und Sekunden
    days, seconds = divmod (delta, 3600*24)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    
    # Baue die menschlich lesbare Form auf
    result = []
    if days > 0:
        result.append(f"{days} Tage")
    if hours > 0:
        result.append(f"{hours} Stunden")
    if minutes > 0:
        result.append(f"{minutes} Minuten")
    if seconds > 0:
        result.append(f"{round(seconds,1)} Sekunden")
    
    return ', '.join(result)

def main():
    zeitanfang = time.time()	
    print("Start ...")
    site = pywikibot.Site('de', 'wikipedia')

    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen"
    
    print("Get missing substances ...")
    substances = get_missing_substances(site, page_title)
    results = []
    
    print("Get information for pages ...")
    count = 0
    for count, substance in enumerate(substances, start=1):
        # print(substance[0], " ", substance[0])
        incoming_links = count_incoming_links(site, substance[0])
        has_german = has_german_wikipedia_link(site, substance[1])
        language_count = count_wikipedia_languages(site, substance[1])
        
        print(f"{count}/{len(substances)} {substance[0]}: {incoming_links} Links, Deutscher Artikel: {has_german}, Sprachen: {language_count}")
        results.append((substance[0], incoming_links, has_german, language_count, substance[1]))
        
        # if count >= 20:
        #    break

    print("Sorting results ...")
    # Sortierung nach: has_german (False zuerst), incoming_links (absteigend), language_count (absteigend)
    results.sort(key=lambda x: (not x[2], -x[1], -x[3]))
    
    update_wikipedia_page(site, results)
    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))

if __name__ == "__main__":
    main()
