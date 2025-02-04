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
        german_page = item.sitelinks.get('dewiki', None)
        return {
            "has_german_wikipedia_link": german_page is not None,
            "german_page_name": german_page.title if german_page else ""
            }
    except Exception as e:
        print(f"Fehler beim Abrufen von {wikidata_id}: {e}")
        return {"has_german_wikipedia_link": False, "german_page_name":""}

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
    pre_text = match.group(1).strip() if match else ""
    new_content = f"{pre_text}\n\n== Zusatzinformationen ==\n"

    for wikidata, data in results.items():
        german_text = f"(dabei auch anderer Artikel [[{data["german_name"]}]] in Deutsch ) " if data["has_german"] else ""
        if len(data["substances"]) == 1:
            substance = data["substances"][0]
            links = data['links'][0]
            new_content += f"* [[Spezial:Linkliste/{substance}|{links}]] Link(s) auf und in [[:d:{wikidata}|{data['langs']}]] anderen Sprachen {german_text}vorhanden für [[{substance}]]\n"
        else:
            # print(data["substances"])
            substance_list = ""
            linklist_list = ""
            count = 0
            for s in data["substances"]:
                substance_list += f"[[{s}]]/"
                links = f"{data['links'][count]}"
                linklist_list += f"[[Spezial:Linkliste/{s}|{links}]]+"
                count += 1
            
            new_content += f"* {sum(data['links'])} ({linklist_list.rstrip("+")}) Link(s) auf und in [[:d:{wikidata}|{data['langs']}]] anderen Sprachen {german_text}vorhanden für {substance_list.rstrip("/")}\n"

    page.text = new_content
    # print(new_content)
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
    
    results = defaultdict(lambda: {"substances": [], "links": [], "has_german": False, "german_name": "", "langs": 0})
    
    count = 0
    print("Get information for pages ...")
    for count, (name, wikidata_id) in enumerate(substances, start=1):
        incoming_links = count_incoming_links(site, name)
        result = has_german_wikipedia_link(site, wikidata_id)
        language_count = count_wikipedia_languages(site, wikidata_id)
        
        print(f"{count}/{len(substances)} {name}: {incoming_links} Links, Deutscher Artikel: {result["has_german_wikipedia_link"]}, Sprachen: {language_count}")
        
        results[wikidata_id]["substances"].append(name)
        results[wikidata_id]["links"].append(incoming_links)
        results[wikidata_id]["has_german"] |= result["has_german_wikipedia_link"]
        results[wikidata_id]["german_name"] = result["german_page_name"]
        results[wikidata_id]["langs"] = max(results[wikidata_id]["langs"], language_count)
        
        #if (count >= 500):
        #    break
    
    print("Sorting results ...")
    sorted_results = dict(sorted(results.items(), key=lambda x: (not x[1]["has_german"], -sum(x[1]["links"]), -x[1]["langs"])))

    update_wikipedia_page(site, sorted_results)

    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))

if __name__ == "__main__":
    main()
