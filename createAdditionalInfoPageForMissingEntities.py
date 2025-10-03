import pywikibot
import re
import time
import mwparserfromhell
from collections import defaultdict
from helperfunctions import human_readable_time_difference

unknown_wikidata = "Q000000"

def get_missing_entities(site, page_title):
    """Extrahiert die Liste der fehlenden Einträge von der Wikipedia-Seite."""
    page = pywikibot.Page(site, page_title)
    content = page.text

    matches = re.findall(r'\[\[([^|\]]+)[^\]]*\]\] \((.*?)\)', content)

    entities = []
    for name, bracket_content in matches:
        wikidata_match = re.search(r'\[\[:d:(Q\d+)', bracket_content)
        wikidata_id = wikidata_match.group(1) if wikidata_match else unknown_wikidata
        entities.append((name, wikidata_id))

    # Einträge ohne Klammer
    matches = re.findall(r'\[\[([^|\]]+)[^\]]*\]\] -', content)
    for name in matches:
        entities.append((name, unknown_wikidata))
    return entities

def getWikidataItem(site, wikidata_id):
    try:
        repo = site.data_repository()
        item = pywikibot.ItemPage(repo, wikidata_id)
        while item.isRedirectPage():
            item = pywikibot.ItemPage(repo, item.getRedirectTarget().title())
        item.get()
        return item
    except Exception as e:
        print(f"Fehler beim Abrufen von {wikidata_id}: {e}")
        return None

def count_incoming_links(site, title):
    page = pywikibot.Page(site, title)
    return len(list(page.backlinks(namespaces=[0])))

def count_links_via_templates(site, target_title, namespaces=[0]):
    target_page = pywikibot.Page(site, target_title)
    refs = list(target_page.getReferences(only_template_inclusion=False, namespaces=namespaces))

    direct_count = 0
    template_count = 0

    for page in refs:
        try:
            raw = page.text
            wikicode_raw = mwparserfromhell.parse(raw)
            raw_links = {str(link.title) for link in wikicode_raw.filter_wikilinks()}

            expanded = page.expand_text()
            wikicode_expanded = mwparserfromhell.parse(expanded)
            expanded_links = {str(link.title) for link in wikicode_expanded.filter_wikilinks()}

            if target_title in expanded_links:
                if target_title in raw_links:
                    direct_count += 1
                else:
                    template_count += 1
        except Exception as e:
            print(f"Fehler bei {page.title()}: {e}")

    return {"direct": direct_count, "template": template_count, "total": direct_count + template_count}

def has_german_wikipedia_link(item):
    if item:
        german_page = item.sitelinks.get('dewiki', None)
        return {
            "has_german_wikipedia_link": german_page is not None,
            "german_page_name": german_page.title if german_page else ""
        }
    else:
        return {"has_german_wikipedia_link": False, "german_page_name": ""}

def count_wikipedia_languages(item):
    if item:
        wikipedia_links = [site for site in item.sitelinks if (site.endswith('wiki') and not site == "commonswiki")]
        return len(wikipedia_links)
    else:
        return -1

def update_wikipedia_page(site, output_page_title, results, wikidata_description):
    page = pywikibot.Page(site, output_page_title)
    content = page.text
    
    counter = 1
    match = re.search(r'(^.*?)(==\s*Zusatzinformationen\s*==)', content, re.DOTALL)
    pre_text = match.group(1).strip() if match else ""
    new_content = f"{pre_text}\n\n== Zusatzinformationen ==\n"

    for wikidata, data in results.items():
        german_text = ""
        if data["has_german"]:
            page2 = pywikibot.Page(site, data["german_name"])
            if page2.isRedirectPage():
                german_text = f"(dabei auch anderer Artikel [[{data['german_name']}]] (Weiterleitung auf [[{page2.getRedirectTarget().title()}]]) in Deutsch) "
            else:
                german_text = f"(dabei auch anderer Artikel [[{data['german_name']}]] in Deutsch) "  
        langs_count = data['langs']
        wikidata_text = ""
        if langs_count == -1: 
           wikidata_text = f"und '''kein [[:d:{wikidata}|Wikidata-Eintrag]]''' ([https://www.wikidata.org/wiki/Special:NewItem?uselang=de&label={data['entities'][0]}&description={wikidata_description} Neu anlegen]) vorhanden"
        else:
            wikidata_text = f"und in [[:d:{wikidata}|{langs_count}]] anderen Sprachen {german_text}vorhanden"
        
        if len(data["entities"]) == 1:
            name = data["entities"][0]
            links = data['links'][0]
            template_links = data['template_links'][0]
            searchcount = data['searchcount'][0]
            page2 = pywikibot.Page(site, name)
            if page2.exists() and page2.isRedirectPage():
                new_content += f"* [[Spezial:Linkliste/{name}|{links}]] Link(s) {'' if template_links == 0 else f'(davon {template_links} aus Vorlagen) '}auf und [https://de.wikipedia.org/w/index.php?search=%22{name.replace(' ', '%20')}%22&ns0=1 {searchcount}] Suchtreffer {wikidata_text} für [[{name}]] (Weiterleitung auf [[{page2.getRedirectTarget().title()}]])\n"            
            else:
                new_content += f"* [[Spezial:Linkliste/{name}|{links}]] Link(s) {'' if template_links == 0 else f'(davon {template_links} aus Vorlagen) '}auf und [https://de.wikipedia.org/w/index.php?search=%22{name.replace(' ', '%20')}%22&ns0=1 {searchcount}] Suchtreffer {wikidata_text} für [[{name}]]\n"
        else:
            name_list = ""
            linklist_list = ""
            count = 0
            for s in data["entities"]:
                page2 = pywikibot.Page(site, s)
                if page2.exists() and page2.isRedirectPage():
                    name_list += f"[[{s}]] (Weiterleitung auf [[{page2.getRedirectTarget().title()}]])/"                
                else:
                    name_list += f"[[{s}]]/"
                links = f"{data['links'][count]}"
                linklist_list += f"[[Spezial:Linkliste/{s}|{links}]]+"
                count += 1
            
            template_links = sum(data['template_links'])
            new_content += f"* {sum(data['links'])} ({linklist_list.rstrip('+')}) Link(s) {'' if template_links == 0 else f'(davon {template_links} aus Vorlagen) '}auf und [https://de.wikipedia.org/w/index.php?search=%22{data['entities'][0].replace(' ', '%20')}%22&ns0=1 {sum(data['searchcount'])}] Suchtreffer {wikidata_text} für {name_list.rstrip('/')}\n"
        print(f"{counter}/{len(results.items())} {data['entities'][0]}")
        counter += 1

    page.text = new_content
    page.save(summary=f"Automatische Aktualisierung der Zusatzinformationen für {len(results)} Seiten")

def getSearchCount(site, name):
    results = list(site.search("\""+name+"\"", total=500, namespaces=[0]))
    return len(results)

def main(input_page_title, output_page_title, wikidata_description):
    zeitanfang = time.time()	
    print("Start ... ")
    site = pywikibot.Site('de', 'wikipedia')

    print("Bearbeite Einträge von {input_page_title}")
    entities = get_missing_entities(site, input_page_title)
    
    results = defaultdict(lambda: {"entities": [], "links": [], "template_links": [], "searchcount": [], "has_german": False, "german_name": "", "langs": -1})
    
    for count, (name, wikidata_id) in enumerate(entities, start=1):
        searchcount = getSearchCount(site, name)
        
        if wikidata_id == unknown_wikidata:
            incoming_links = count_incoming_links(site, name)
            incoming_links_templates = count_links_via_templates(site, name)["template"] if incoming_links > 3 else 0
            print(f"{count}/{len(entities)} {name}: {incoming_links} Links, Vorlagen {incoming_links_templates}, Suchtreffer {searchcount}, Deutscher Artikel: False, Sprachen: -1")
            
            results[name]["entities"].append(name)
            results[name]["links"].append(incoming_links)
            results[name]["template_links"].append(incoming_links_templates)
            results[name]["searchcount"].append(searchcount)
        
        else:
            incoming_links = count_incoming_links(site, name)
            incoming_links_templates = count_links_via_templates(site, name)["template"] if incoming_links > 3 else 0
            item = getWikidataItem(site, wikidata_id)
            result = has_german_wikipedia_link(item)
            language_count = count_wikipedia_languages(item)
            
            print(f"{count}/{len(entities)} {name}: {incoming_links} Links, Vorlagen {incoming_links_templates}, Suchtreffer {searchcount}, Deutscher Artikel: {result['has_german_wikipedia_link']}, Sprachen: {language_count}")
            
            results[wikidata_id]["entities"].append(name)
            results[wikidata_id]["links"].append(incoming_links)
            results[wikidata_id]["template_links"].append(incoming_links_templates)
            results[wikidata_id]["has_german"] |= result["has_german_wikipedia_link"]
            results[wikidata_id]["german_name"] = result["german_page_name"]
            results[wikidata_id]["langs"] = max(results[wikidata_id]["langs"], language_count)
            results[wikidata_id]["searchcount"].append(searchcount)
    
    print("Sorting results ...")
    sorted_results = dict(sorted(results.items(), key=lambda x: (
        not x[1]["has_german"], 
        x[1]["langs"] != -1, 
        -(sum(x[1]["links"])), 
        -x[1]["langs"], 
        -sum(x[1]["searchcount"]), 
        x[1]["entities"][0].lower() if x[1]["entities"] else ""
    )))

    print("Update page ...")
    update_wikipedia_page(site, output_page_title, sorted_results, wikidata_description)

    print("\nLaufzeit:", human_readable_time_difference(zeitanfang, time.time()))

if __name__ == "__main__":
    main(
        "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Sonstige Themen",
        "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Sonstige Themen/Zusatzinformationen",
        ""
    )
    main(
        "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Unternehmen",
        "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Unternehmen/Zusatzinformationen",
        "chemische%20Verbindung"
    )
    main(
        "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Journals",
        "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Journals/Zusatzinformationen",
        "wissenschaftliches Journal"
    )
    main(
        "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Taxa",
        "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Taxa/Zusatzinformationen",
        "Organismus"
    )
