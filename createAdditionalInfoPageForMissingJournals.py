import pywikibot
import re
import time
import mwparserfromhell
from collections import defaultdict

unknown_wikidata = "Q000000"

def get_missing_journals(site, page_title):
    """Extrahiert die Liste der fehlenden Journale von der Wikipedia-Seite."""
    page = pywikibot.Page(site, page_title)
    content = page.text

    matches = re.findall(r'\[\[([^|\]]+)[^\]]*\]\] \((.*?)\)', content)

    journals = []
    for name, bracket_content in matches:
        wikidata_match = re.search(r'\[\[:d:(Q\d+)', bracket_content)
        wikidata_id = wikidata_match.group(1) if wikidata_match else unknown_wikidata
        # print(bracket_content)
        # print(bracket_content, wikidata_match)
        journals.append((name, wikidata_id))

    # Einträge ohne Klammer
    matches = re.findall(r'\[\[([^|\]]+)[^\]]*\]\] -', content)
    for name in matches:
        journals.append((name, unknown_wikidata))
    # print(journals)
    return journals

def getWikidataItem(site, wikidata_id):
    try:
        repo = site.data_repository()  # Daten-Repository für Wikidata
        item = pywikibot.ItemPage(repo, wikidata_id)  # Wikidata-Item laden
        while item.isRedirectPage(): # eine oder mehrere Redirects abfangen
            item = pywikibot.ItemPage(repo, item.getRedirectTarget().title())
        item.get()  # Daten abrufen
        return item
    except Exception as e:
        print(f"Fehler beim Abrufen von {wikidata_id}: {e}")
        return None

def count_incoming_links(site, title):
    """Zählt die Anzahl der eingehenden Links auf eine Seite in der Wikipedia."""
    page = pywikibot.Page(site, title)
    return len(list(page.backlinks(namespaces=[0])))  # Nur Artikel-Namensraum

def count_links_via_templates(site, target_title, namespaces=[0]):
    """
    Zählt, wie viele Links auf `target_title` direkt im Wikitext vorkommen
    und wie viele über Vorlagen erzeugt werden.

    Args:
        site (pywikibot.Site): Wikipedia-Site, z. B. Site("de", "wikipedia")
        target_title (str): Titel der Zielseite, z. B. "Berlin"
        namespaces (list): Liste von Namespaces, in denen gesucht werden soll (Standard: [0] = Artikel)

    Returns:
        dict: {"direct": int, "template": int, "total": int}
    """
    target_page = pywikibot.Page(site, target_title)
    refs = list(target_page.getReferences(only_template_inclusion=False, namespaces=namespaces))

    direct_count = 0
    template_count = 0

    for page in refs:
        try:
            # Roh-Wikitext
            raw = page.text
            wikicode_raw = mwparserfromhell.parse(raw)
            raw_links = {str(link.title) for link in wikicode_raw.filter_wikilinks()}

            # Expandierter Text (inkl. Vorlagen)
            expanded = page.expand_text()
            wikicode_expanded = mwparserfromhell.parse(expanded)
            expanded_links = {str(link.title) for link in wikicode_expanded.filter_wikilinks()}

            # Entscheidung: direkt oder via Vorlage?
            if target_title in expanded_links:
                if target_title in raw_links:
                    direct_count += 1
                else:
                    template_count += 1

        except Exception as e:
            print(f"Fehler bei {page.title()}: {e}")

    return {
        "direct": direct_count,
        "template": template_count,
        "total": direct_count + template_count,
    }


def has_german_wikipedia_link(site, item):
    
    if item:
        german_page = item.sitelinks.get('dewiki', None)
        return {
            "has_german_wikipedia_link": german_page is not None,
            "german_page_name": german_page.title if german_page else ""
            }
    else:
        return {"has_german_wikipedia_link": False, "german_page_name":""}

def count_wikipedia_languages(site, item):

    if item:
        # Filtere nur Wikipedia-Sprachlinks (die Endung '.wikipedia.org' haben)

        language_count = len(item.sitelinks)  # Anzahl der Sprachlinks zählen
        # print(f"{wikidata_id} hat {language_count} Links zu Wikipedia-Artikeln.")
 
        wikipedia_links = [site for site in item.sitelinks if (site.endswith('wiki') and not site == "commonswiki" )]
        language_count = len(wikipedia_links)  # Anzahl der Wikipedia-Sprachlinks

        # print(f"{wikidata_id} hat Wikipedia-Artikel in {language_count} Sprachen.")
        return language_count
    else:
        return -1

def update_wikipedia_page(site, results):
    page = pywikibot.Page(site, "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Journals/Zusatzinformationen")
    #page = pywikibot.Page(site, "Benutzer:ChemoBot/Tests/Zusatzinformationen")
    content = page.text
    
    counter = 1
    
    # Trenne den vorhandenen Inhalt in den Teil vor "Zusatzinformationen" und den Rest
    match = re.search(r'(^.*?)(==\s*Zusatzinformationen\s*==)', content, re.DOTALL)
    pre_text = match.group(1).strip() if match else ""
    new_content = f"{pre_text}\n\n== Zusatzinformationen ==\n"
    for wikidata, data in results.items():
        german_text = ""
        if data["has_german"]:
            page2 = pywikibot.Page(site, data["german_name"])
            if page2.isRedirectPage():
                german_text = f"(dabei auch anderer Artikel [[{data["german_name"]}]] (Weiterleitung auf [[{page2.getRedirectTarget().title()}]]) in Deutsch) "
            else:
                german_text = f"(dabei auch anderer Artikel [[{data["german_name"]}]] in Deutsch) "  
        langs_count = data['langs']
        wikidata_text = ""        
        if langs_count == -1: 
           wikidata_text = f"und '''kein [[:d:{wikidata}|Wikidata-Eintrag]]''' ([https://www.wikidata.org/wiki/Special:NewItem?uselang=de&label={data["journals"][0]}&description=chemische%20Verbindung Neu anlegen]) vorhanden"
        else:
            wikidata_text = f"und in [[:d:{wikidata}|{langs_count}]] anderen Sprachen {german_text}vorhanden"
        
        if len(data["journals"]) == 1:
            substance = data["journals"][0]
            links = data['links'][0]
            template_links = data['template_links'][0]
            searchcount = data['searchcount'][0]
            page2 = pywikibot.Page(site, substance)
            if page2.exists() and page2.isRedirectPage():
                new_content += f"* [[Spezial:Linkliste/{substance}|{links}]] Link(s) {"" if template_links == 0 else f"(davon {template_links} aus Vorlagen) "}auf und [https://de.wikipedia.org/w/index.php?search=%22{substance.replace(" ", "%20")}%22&ns0=1 {searchcount}] Suchtreffer {wikidata_text} für [[{substance}]] (Weiterleitung auf [[{page2.getRedirectTarget().title()}]])\n"            
            else:
                new_content += f"* [[Spezial:Linkliste/{substance}|{links}]] Link(s) {"" if template_links == 0 else f"(davon {template_links} aus Vorlagen) "}auf und [https://de.wikipedia.org/w/index.php?search=%22{substance.replace(" ", "%20")}%22&ns0=1 {searchcount}] Suchtreffer {wikidata_text} für [[{substance}]]\n"
        else:
            # print(data["journals"])
            substance_list = ""
            linklist_list = ""
            count = 0
            for s in data["journals"]:
                page2 = pywikibot.Page(site, s)
                if page2.exists() and page2.isRedirectPage():
                    substance_list += f"[[{s}]] (Weiterleitung auf [[{page2.getRedirectTarget().title()}]])/"                
                else:
                    substance_list += f"[[{s}]]/"
                links = f"{data['links'][count]}"
                linklist_list += f"[[Spezial:Linkliste/{s}|{links}]]+"
                count += 1
            
            template_links = sum(data['template_links'])
            new_content += f"* {sum(data['links'])} ({linklist_list.rstrip("+")}) Link(s) {"" if template_links == 0 else f"(davon {template_links} aus Vorlagen) "}auf und [https://de.wikipedia.org/w/index.php?search=%22{data["journals"][0].replace(" ", "%20")}%22&ns0=1 {sum(data['searchcount'])}] Suchtreffer {wikidata_text} für {substance_list.rstrip("/")}\n"
        print(f"{counter}/{len(results.items())} {data["journals"][0]}")
        counter += 1

    page.text = new_content
    #print(new_content)
    page.save(summary=f"Automatische Aktualisierung der Zusatzinformationen für {len(results)} Seiten")


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
        result.append(f"{int(days)} Tage")
    if hours > 0:
        result.append(f"{int(hours)} Stunden")
    if minutes > 0:
        result.append(f"{int(minutes)} Minuten")
    if seconds > 0:
        result.append(f"{round(seconds,1)} Sekunden")
    
    return ', '.join(result)

def getSearchCount(site, name):
    results = list(site.search("\""+name+"\"", total=500, namespaces=[0]))
    #print(f"Treffer für '{name}' im Artikelnamensraum: {len(results)}")
    return len(results)

def main():
    zeitanfang = time.time()	
    print("Start ...")
    site = pywikibot.Site('de', 'wikipedia')

    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Journals"
    
    print("Get missing journals ...")
    journals = get_missing_journals(site, page_title)
    
    results = defaultdict(lambda: {"journals": [], "links": [], "template_links": [], "searchcount": [], "has_german": False, "german_name": "", "langs": -1})
    
    count = 0
    print("Get information for pages ...")
    for count, (name, wikidata_id) in enumerate(journals, start=1):
        
        searchcount = getSearchCount(site, name)
        
        if wikidata_id == unknown_wikidata:
            incoming_links = count_incoming_links(site, name)
            if (incoming_links > 3):
                incoming_links_templates = count_links_via_templates(site, name)["template"]
            else:
                incoming_links_templates = 0
            print(f"{count}/{len(journals)} {name}: {incoming_links} Links, davon Vorlagen {incoming_links_templates}, Suchtreffer: {searchcount}, Deutscher Artikel: {False}, Sprachen: {-1}")
            
            results[name]["journals"].append(name)
            results[name]["links"].append(incoming_links)
            results[name]["template_links"].append(incoming_links_templates)
            results[name]["has_german"] |= False
            results[name]["german_name"] = ""
            results[name]["langs"] = -1
            results[name]["searchcount"].append(searchcount)
        
        else:
            incoming_links = count_incoming_links(site, name)
            if (incoming_links > 3):
                incoming_links_templates = count_links_via_templates(site, name)["template"]
            else:
                incoming_links_templates = 0
            item = getWikidataItem(site, wikidata_id)
            result = has_german_wikipedia_link(site, item)
            language_count = count_wikipedia_languages(site, item)
            
            print(f"{count}/{len(journals)} {name}: {incoming_links} Links, davon Vorlagen {incoming_links_templates}, Suchtreffer: {searchcount}, Deutscher Artikel: {result["has_german_wikipedia_link"]}, Sprachen: {language_count}")
            
            results[wikidata_id]["journals"].append(name)
            results[wikidata_id]["links"].append(incoming_links)
            results[wikidata_id]["template_links"].append(incoming_links_templates)
            results[wikidata_id]["has_german"] |= result["has_german_wikipedia_link"]
            results[wikidata_id]["german_name"] = result["german_page_name"]
            results[wikidata_id]["langs"] = max(results[wikidata_id]["langs"], language_count)
            results[wikidata_id]["searchcount"].append(searchcount)
        
        # if (count >= 100):
        #    break
    
    print("Sorting results ...")
    sorted_results = dict(sorted(results.items(), key=lambda x: (
        not x[1]["has_german"], 
        x[1]["langs"] != -1, 
        -(sum(x[1]["links"])), 
        -x[1]["langs"], 
        -sum(x[1]["searchcount"]), 
        x[1]["journals"][0].lower() if x[1]["journals"] else ""
    )))

    print("Update page ...")
    update_wikipedia_page(site, sorted_results)

    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))

if __name__ == "__main__":
    main()
