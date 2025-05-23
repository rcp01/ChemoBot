import pywikibot
import re
import time
from collections import defaultdict

unknown_wikidata = "Q000000"
unknown_cas = "-"

def get_missing_substances(site, page_title):
    """Extrahiert die Liste der fehlenden Substanzen von der Wikipedia-Seite."""
    page = pywikibot.Page(site, page_title)
    content = page.text

    matches = re.findall(r'\[\[([^|\]]+)[^\]]*\]\] \((.*?)\)', content)

    substances = []
    for name, bracket_content in matches:
        wikidata_match = re.search(r'\[\[:d:(Q\d+)', bracket_content)
        wikidata_id = wikidata_match.group(1) if wikidata_match else unknown_wikidata
        # print(bracket_content)
        cas_match = re.search(r'(\d+-\d+-\d)', bracket_content)
        cas_nr = cas_match.group(1) if cas_match else unknown_cas
        # print(bracket_content, wikidata_match)
        substances.append((name, wikidata_id, cas_nr))

    # Einträge ohne Klammer
    matches = re.findall(r'\[\[([^|\]]+)[^\]]*\]\] -', content)
    for name in matches:
        cas_match = re.search(r'\d+-\d+-\d', bracket_content)
        cas_nr = cas_match.group(1) if cas_match else unknown_cas
        substances.append((name, unknown_wikidata, cas_nr))
    # print(substances)
    return substances

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
    page = pywikibot.Page(site, "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Zusatzinformationen")
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
        cas_nr = data["cas_nr"]
        langs_count = data['langs']
        wikidata_text = ""        
        if langs_count == -1: 
            if len(cas_nr)>1:
                name=data["substances"][0]
                name = name.replace(" ", "%20")
                wikidata_text = f"und '''kein [//tools.wmflabs.org/wikidata-todo/resolver.php?prop=231&value={cas_nr} Wikidata]-Eintrag''' ([https://www.wikidata.org/wiki/Special:NewItem?uselang=de&label={name}&description=chemische%20Verbindung Neu anlegen]) vorhanden"
                # print(wikidata_text)
            else:
                wikidata_text = f"und '''kein [[:d:{wikidata}|Wikidata-Eintrag]]''' ([https://www.wikidata.org/wiki/Special:NewItem?uselang=de&label={data["substances"][0]}&description=chemische%20Verbindung Neu anlegen]) vorhanden"
        else:
            wikidata_text = f"und in [[:d:{wikidata}|{langs_count}]] anderen Sprachen {german_text}vorhanden"
        
        if len(cas_nr)>1:
            cas_nr = "{{CASRN|"+cas_nr+"}}"
        if len(data["substances"]) == 1:
            substance = data["substances"][0]
            links = data['links'][0]
            searchcount = data['searchcount'][0]
            page2 = pywikibot.Page(site, substance)
            if page2.exists() and page2.isRedirectPage():
                new_content += f"* [[Spezial:Linkliste/{substance}|{links}]] Link(s) auf und [https://de.wikipedia.org/w/index.php?search=%22{substance.replace(" ", "%20")}%22&ns0=1 {searchcount}] Suchtreffer {wikidata_text} für [[{substance}]] (Weiterleitung auf [[{page2.getRedirectTarget().title()}]]), CAS:{cas_nr}\n"            
            else:            
                new_content += f"* [[Spezial:Linkliste/{substance}|{links}]] Link(s) auf und [https://de.wikipedia.org/w/index.php?search=%22{substance.replace(" ", "%20")}%22&ns0=1 {searchcount}] Suchtreffer {wikidata_text} für [[{substance}]], CAS:{cas_nr}\n"
        else:
            # print(data["substances"])
            substance_list = ""
            linklist_list = ""
            count = 0
            for s in data["substances"]:
                page2 = pywikibot.Page(site, s)
                if page2.exists() and page2.isRedirectPage():
                    substance_list += f"[[{s}]] (Weiterleitung auf [[{page2.getRedirectTarget().title()}]])/"                
                else:
                    substance_list += f"[[{s}]]/"
                links = f"{data['links'][count]}"
                linklist_list += f"[[Spezial:Linkliste/{s}|{links}]]+"
                count += 1
            
            new_content += f"* {sum(data['links'])} ({linklist_list.rstrip("+")}) Link(s) auf und [https://de.wikipedia.org/w/index.php?search=%22{data["substances"][0].replace(" ", "%20")}%22&ns0=1 {sum(data['searchcount'])}] Suchtreffer {wikidata_text} für {substance_list.rstrip("/")}, CAS:{cas_nr}\n"
        print(f"{counter}/{len(results.items())} {data["substances"][0]}")
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

    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen"
    
    print("Get missing substances ...")
    substances = get_missing_substances(site, page_title)
    
    results = defaultdict(lambda: {"substances": [], "links": [], "searchcount": [], "has_german": False, "german_name": "", "langs": -1, "cas_nr" : ""})
    
    count = 0
    print("Get information for pages ...")
    for count, (name, wikidata_id, cas_nr) in enumerate(substances, start=1):
        
        searchcount = getSearchCount(site, name)
        
        if wikidata_id == unknown_wikidata:
            incoming_links = count_incoming_links(site, name)
            
            print(f"{count}/{len(substances)} {name}: {incoming_links} Links, Suchtreffer: {searchcount}, Deutscher Artikel: {False}, Sprachen: {-1}, cas: {cas_nr}")
            
            results[name]["substances"].append(name)
            results[name]["links"].append(incoming_links)
            results[name]["has_german"] |= False
            results[name]["german_name"] = ""
            results[name]["langs"] = -1
            results[name]["cas_nr"] = cas_nr
            results[name]["searchcount"].append(searchcount)
        
        else:
            incoming_links = count_incoming_links(site, name)
            item = getWikidataItem(site, wikidata_id)
            result = has_german_wikipedia_link(site, item)
            language_count = count_wikipedia_languages(site, item)
            
            print(f"{count}/{len(substances)} {name}: {incoming_links} Links, Suchtreffer: {searchcount}, Deutscher Artikel: {result["has_german_wikipedia_link"]}, Sprachen: {language_count}, cas: {cas_nr}")
            
            results[wikidata_id]["substances"].append(name)
            results[wikidata_id]["links"].append(incoming_links)
            results[wikidata_id]["has_german"] |= result["has_german_wikipedia_link"]
            results[wikidata_id]["german_name"] = result["german_page_name"]
            results[wikidata_id]["langs"] = max(results[wikidata_id]["langs"], language_count)
            results[wikidata_id]["cas_nr"] = cas_nr
            results[wikidata_id]["searchcount"].append(searchcount)
        
        # if (count >= 100):
        #    break
    
    print("Sorting results ...")
    sorted_results = dict(sorted(results.items(), key=lambda x: (
        not x[1]["has_german"], 
        x[1]["langs"] != -1, 
        -sum(x[1]["links"]), 
        -x[1]["langs"], 
        -sum(x[1]["searchcount"]), 
        x[1]["substances"][0].lower() if x[1]["substances"] else ""
    )))

    print("Update page ...")
    update_wikipedia_page(site, sorted_results)

    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))

if __name__ == "__main__":
    main()
