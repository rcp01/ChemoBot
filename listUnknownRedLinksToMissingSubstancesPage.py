#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import itertools
import time
import traceback
import re
import requests
import mwparserfromhell
from helperfunctions import translate_substance_name_to_englisch, human_readable_time_difference
from typing import Optional
import argparse
from datetime import datetime, timedelta, timezone, UTC

# Globale Variablen
pages_checked = 0
rotlinks = {}  # Dictionary der Rotlinks: {Rotlink: [Seitennamen]}

def get_missing_substances_list(site, page_title):
    """
    Extrahiert die Liste fehlender Substanzen von der angegebenen Seite.

    Args:
        site (pywikibot.Site): Die Site-Instanz für Wikipedia.

    Returns:
        list: Eine Liste mit den Namen der fehlenden Substanzen.
    """
    
    print(f"Analysiere die Seite '{page_title}'...")
    page = pywikibot.Page(site, page_title)

    try:
        # Lade den Seiteninhalt
        content = page.text

        # Suche nach Listeneinträgen (Elemente in einer wikitext-Liste)
        # Annahme: Die Substanzen stehen in Zeilen, die mit einem "*" beginnen
        matches = re.findall(r'^\[\[(.*)\]\] \(', content, re.MULTILINE)

        # Entferne mögliche Kommentare oder Formatierungen (z.B. Links)
        substances = []
        for match in matches:
            # Entferne [[ und ]] von Links und trimme Leerzeichen
            substances.append(match)
            # print(match)

        print(len(substances))
        return substances
    except Exception as e:
        traceback.print_exc()
        print(f"Fehler beim Abrufen oder Analysieren der Seite: {e}")
        return []

def get_ignore_list(site):
    """
    Extrahiert die Liste fehlender Substanzen von der angegebenen Seite.

    Args:
        site (pywikibot.Site): Die Site-Instanz für Wikipedia.

    Returns:
        list: Eine Liste mit den Namen der fehlenden Substanzen.
    """
    
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Ausschlussliste"
    substances = []
    print(f"Analysiere die Seite '{page_title}'...")
    page = pywikibot.Page(site, page_title)

    try:
        # Lade den Seiteninhalt
        content = page.text

        # Suche nach Listeneinträgen (Elemente in einer wikitext-Liste)
        # Annahme: Die Substanzen stehen in Zeilen, die mit einem "*" beginnen
        matches = re.findall(r'^\[\[(.*)\]\] ', content, re.MULTILINE)

        # Entferne mögliche Kommentare oder Formatierungen (z.B. Links)
        for match in matches:
            # Entferne [[ und ]] von Links und trimme Leerzeichen
            substances.append(match)
            # print(match)

    except Exception as e:
        traceback.print_exc()
        print(f"Fehler beim Abrufen oder Analysieren der Seite: {e}")

    print(len(substances))

    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Varianten"
    print(f"Analysiere die Seite '{page_title}'...")
    page = pywikibot.Page(site, page_title)

    try:
        # Lade den Seiteninhalt
        content = page.text

        # Suche nach Listeneinträgen (Elemente in einer wikitext-Liste)
        # Annahme: Die Substanzen stehen in Zeilen, die mit einem "*" beginnen
        matches = re.findall(r'^\[\[(.*)\]\] ', content, re.MULTILINE)

        # Entferne mögliche Kommentare oder Formatierungen (z.B. Links)
        for match in matches:
            # Entferne [[ und ]] von Links und trimme Leerzeichen
            substances.append(match)
            # print(match)

    except Exception as e:
        traceback.print_exc()
        print(f"Fehler beim Abrufen oder Analysieren der Seite: {e}")

    print(len(substances))
    return substances


def get_exclusion_list(site):
    """
    Extrahiert die Liste der zu ignorierenden Seite von der angegebenen Seite.

    Args:
        site (pywikibot.Site): Die Site-Instanz für Wikipedia.

    Returns:
        list: Eine Liste mit den Namen der fehlenden Substanzen.
    """
    
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Gruppenausschluss"
    substances = []
    print(f"Analysiere die Seite '{page_title}'...")
    page = pywikibot.Page(site, page_title)

    try:
        # Lade den Seiteninhalt
        content = page.text

        # Suche nach Listeneinträgen (Elemente in einer wikitext-Liste)
        # Annahme: Die Substanzen stehen in Zeilen, die mit einem "*" beginnen
        matches = re.findall(r'^\[\[(.*)\]\] ', content, re.MULTILINE)

        # Entferne mögliche Kommentare oder Formatierungen (z.B. Links)
        for match in matches:
            # Entferne [[ und ]] von Links und trimme Leerzeichen
            substances.append(match)
            # print(match)

    except Exception as e:
        traceback.print_exc()
        print(f"Fehler beim Abrufen oder Analysieren der Seite: {e}")

    print(len(substances))
    return substances


def get_intermediate_list(site):
    """
    Extrahiert die Liste der zu ignorierenden Seite von der angegebenen Seite.

    Args:
        site (pywikibot.Site): Die Site-Instanz für Wikipedia.

    Returns:
        list: Eine Liste mit den Namen der Substanzen.
    """
    
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Neuzugänge/Zwischenlager"
    # page_title = "Benutzer:ChemoBot/Tests/Neuzugänge/Zwischenlager"
    substances = []
    print(f"Analysiere die Seite '{page_title}'...")
    page = pywikibot.Page(site, page_title)

    try:
        # Lade den Seiteninhalt
        content = page.text

        # Suche nach Listeneinträgen (Elemente in einer wikitext-Liste)
        # Annahme: Die Substanzen stehen in Zeilen, die mit einem "*" beginnen
        matches = re.findall(r'^\* \[\[(.*?)\]\] ', content, re.MULTILINE)

        # Entferne mögliche Kommentare oder Formatierungen (z.B. Links)
        for match in matches:
            # Entferne [[ und ]] von Links und trimme Leerzeichen
            substances.append(match)
            # print(match)

    except Exception as e:
        traceback.print_exc()
        print(f"Fehler beim Abrufen oder Analysieren der Seite: {e}")

    # print(substances)
    print(len(substances))
    return substances


def find_red_links(page):
    """
    Gibt eine Liste aller nicht existierenden, verlinkten Artikel auf der angegebenen Wikipedia-Seite zurück.

    Args:
        page: Die Pywikibot-Seite, die analysiert werden soll.

    Returns:
        Eine Liste von Titeln der nicht existierenden verlinkten Artikel.
    """
    try:
        # Filtere nur nicht existierende Seiten
        return [
            linked_page.title()
            for linked_page in page.linkedPages()
            if not linked_page.exists() and linked_page.namespace() == 0 and not linked_page.title().startswith("Vorlage:")
        ]
    except Exception as e:
        traceback.print_exc()
        print(f"Fehler beim Abrufen der verlinkten Artikel: {e}")
        return []


def get_pages_in_category(category_name, site):
    """
    Ruft alle Seiten in einer Kategorie und deren Unterkategorien ab.

    Args:
        category_name: Der Name der Kategorie.
        site: Das pywikibot.Site-Objekt, das die Wikipedia-Site repräsentiert.

    Returns:
        Ein Generator für Seiten in der Kategorie und deren Unterkategorien.
    """
    category = pywikibot.Category(site, category_name)
    ret = pagegenerators.CategorizedPageGenerator(category, recurse=True)
    
    count = sum(1 for _ in ret)
    print(f"Anzahl der Seiten in der Kategorie: {count}")
    
    ret = pagegenerators.CategorizedPageGenerator(category, recurse=True)

    return ret


def filter_pages(target_pages_gen, exclusion_pages_gen):
    """
    Filtert Seiten aus, die in target_pages, aber nicht in exclusion_pages enthalten sind.

    Args:
        target_pages_gen: Ein Generator für Seiten in der Zielkategorie.
        exclusion_pages_gen: Ein Generator für Seiten in der Ausschlusskategorie.

    Yields:
        Seiten, die in target_pages_gen, aber nicht in exclusion_pages_gen enthalten sind.
    """
    exclusion_titles = {page.title() for page in exclusion_pages_gen}

    for page in target_pages_gen:
        title = page.title()
        if title not in exclusion_titles and not page.isRedirectPage():
            yield page

def search_wikidata_number(cas_number):
    url = f"https://tools.wmflabs.org/wikidata-todo/resolver.php?prop=231&value={cas_number}"  # Beispiel für eine umleitende URL
    response = requests.get(url, allow_redirects=True)

    # Regulärer Ausdruck zum Extrahieren der Nummer nach "Q"
    match = re.search(r"url=https://www.wikidata.org/wiki/(Q\d+)", response.text)

    if match:
        q_number = match.group(1)  # Die gefundene Nummer
        print("Gefundene Q-Nummer:", q_number, " für CAS ", cas_number)
        return q_number
    return ""

def search_cas_number(chemical_name):
    """
    Ruft die Common Chemistry-Suchseite mit dem angegebenen Namen auf
    und prüft, ob eine CAS-Nummer enthalten ist.
    
    Args:
        chemical_name (str): Der Name der chemischen Verbindung.
    
    Returns:
        str: Gefundene CAS-Nummer oder leerer String, wenn keine gefunden wurde.
    """
    
    # don't check suspicious names
    if " " in chemical_name:
       return ""         
        
    chemical_name_org = chemical_name
    chemical_name = translate_substance_name_to_englisch(chemical_name)
    
    url = f"https://commonchemistry.cas.org/results?q={chemical_name}"
    response = requests.get(url)

    if response.status_code == 200:
        match = re.search(r"(\d{2,8}-\d{2}-\d)", response.text)
        
        if match:
            print(f"\"{chemical_name_org}\" -> \"{chemical_name}\" : commonchemistry = {match.group(1)}")
            return match.group(1)
        else:
            url = f"https://www.chemicalbook.com/Search_EN.aspx?keyword={chemical_name}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Referer": "https://www.chemicalbook.com/" 
                }

            try:
                response = requests.get(url, headers=headers,timeout=5)
                response = requests.get(url, headers=headers,timeout=5) # retry
            except Exception as e:
                response.status_code = 408

            if response.status_code == 200:
                #print(response.text)
                match = re.search(r"(<table.*?</table>)", response.text, re.DOTALL)
                if match:
                    # print(match.group(1))
                    match = re.search(r"(\d{2,8}-\d{2}-\d)", match.group(1))
                    if match:
                        print(f"\"{chemical_name_org}\" -> \"{chemical_name}\" : chemicalbook = {match.group(1)}")
                        return match.group(1)
            else:
                print(f"Fehler: {response.status_code} für {chemical_name} {url}")
    else:
        print(f"Fehler: {response.status_code} für {chemical_name} {url}")

    #print(f"\"{chemical_name_org}\" -> \"{chemical_name}\" : None")
    return ""

TAXON_QID = "Q16521"
GROUPS = {
    "Q756": "tfpf", #"Pflanze",
    "Q729": "tfti", #"Tier",
    "Q764": "tfpi", #"Pilz",
    "Q7868": "tfmi", #"Mikroorganismus", # Oberbegriff
    "Q10876": "tfmi", #"Mikroorganismus",# Bacteria
    "Q10850": "tfmi", #"Mikroorganismus",# Archaea
    "Q808": "tfmi", #"Mikroorganismus",  # Virus
    "Q474548": "tfmi", #"Mikroorganismus" # Protist
}

# globaler Cache: QID -> Liste der Parent-QIDs
parent_cache: dict[str, list[str]] = {}


def get_parents(item: pywikibot.ItemPage) -> list[str]:
    """Hole Eltern (P171) eines Items, benutze Cache falls vorhanden."""
    if item.id in parent_cache:
        return parent_cache[item.id]

    parents = []
    for claim in item.claims.get("P171", []):
        target = claim.getTarget()
        if isinstance(target, pywikibot.ItemPage):
            parents.append(target.id)

    parent_cache[item.id] = parents
    return parents


def classify_taxon(name: str, language: str = "de") -> Optional[tuple[str, Optional[str]]]:
    """
    Suche ein Taxon nach Name und klassifiziere es als Pflanze, Tier, Pilz oder Mikroorganismus.
    Gibt (QID, Gruppe) zurück oder None, falls kein Taxon gefunden.
    """
    
    if not " " in name:
        return None, None
    
    site = pywikibot.Site("wikidata", "wikidata")
    repo = site.data_repository()

    # Suche Item
    req = pywikibot.data.api.Request(
        site=site,
        parameters={
            "action": "wbsearchentities",
            "search": name,
            "language": language,
            "type": "item",
            "limit": 5,
        },
    )
    results = req.submit().get("search", [])
    if not results:
        return None, None

    for hit in results:
        qid = hit.get("id")
        if not qid:
            continue

        item = pywikibot.ItemPage(repo, qid)
        item.get()  # einmal laden

        # Prüfen, ob es ein Taxon ist (P31 = taxon)
        if not any(
            (c.getTarget().id == TAXON_QID)
            for c in item.claims.get("P31", [])
            if c.getTarget()
        ):
            continue

        # Baum hochlaufen (mit Cache durch Pywikibot intern)
        visited = set()
        queue = [item.id]
        while queue:
            cur_qid = queue.pop()
            if cur_qid in visited:
                continue
            visited.add(cur_qid)

            # Prüfen, ob Obergruppe erreicht
            if cur_qid in GROUPS:
                return qid, GROUPS[cur_qid]

            # Eltern holen
            cur_item = pywikibot.ItemPage(repo, cur_qid)
            cur_item.get()
            queue.extend(get_parents(cur_item))

        # kein Treffer im Baum → trotzdem QID zurück, Gruppe = None
        return qid, None

    return None, None
    
def update_wikipedia_page(site, rotlinks, last_page_name, reason):

    global pages_checked

    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Neuzugänge"
    #page_title = "Benutzer:ChemoBot/Tests/Neuzugänge"
    page = pywikibot.Page(site, page_title)
 
    print(f'Automatische Aktualisierung des Abschnitts "Rotlinks" (letzte analysierte Seite: {pages_checked}. {last_page_name}, Anzahl Rotlinks={len(rotlinks)})')
 
    try:
        text = page.text
        section_pattern = r'(==+\s*Rotlinks\s*==+)(.*?)(?=\n==|\Z)'
        match = re.search(section_pattern, text, re.DOTALL)
        
        if not match:
            print("Abschnitt 'Rotlinks' nicht gefunden.")
            return
        
        section_header, section_content = match.groups()
        new_section_content = "\nAktuelle Rotlinks im Bereich Chemie, die nicht auf [[Wikipedia:Redaktion Chemie/Fehlende Substanzen]] und nicht in der [[Wikipedia:Redaktion Chemie/Fehlende Substanzen/Ausschlussliste]] bzw. [[Wikipedia:Redaktion Chemie/Fehlende Substanzen/Varianten]] genannt sind:\n\n"
        new_section_content += "Format ist <Rotlinklemmaname> >> <von Seiten verlinkt> >> <CAS-Nummer>, <wikidata eintrag> >> Abkürzung Kategorie\n"

        print(f"Number of Redlinks = {len(sorted(rotlinks.keys()))}")

        for red_link in sorted(rotlinks.keys()):

            red_link = red_link.strip()
            pages = ", ".join(sorted(rotlinks[red_link]))
            addon = ""
            addon2 = ""
            
            # search old redlink with cas/wikidata and abbr. if it is known
            escaped = re.escape(f'[[{red_link}]]')
            pattern = rf'\* {escaped}\s*>>.*?>>\s*(.*?)\s*>>\s*([A-Za-z]+)?\s*'
            match = re.search(pattern, section_content)
                                
            if match:
                # preserve old
                if match.group(1) != None and match.group(1).strip() != "":
                    addon = match.group(1).strip()
                if match.group(2) != None and match.group(2).strip() != "":
                    addon2 = match.group(2).strip()
            else:
                # new entry, try to guess entries
                cas = search_cas_number(red_link)
                if (cas != ""):
                    wikidata = search_wikidata_number(cas)
                    if (wikidata != ""):
                        addon = f"{cas},{wikidata}"
                    else:
                        addon = f"{cas}"
                else:
                    wikidata, group = classify_taxon(red_link)
                    if (wikidata and wikidata != ""):
                        addon = f"{wikidata}"
                    if (group and addon2 == ""):
                        addon2 = group

            print(f"redlink = {red_link}, pages= {pages}, CAS/Wikidata= {addon}, area= {addon2}")
            new_line = f"* [[{red_link}]] >> {pages} >> {addon} >>{addon2}\n"
            new_section_content += new_line

        new_text = text.replace(section_content, new_section_content)
        
        if new_text != text:
            page.text = new_text
            page.save(f'Automatische Aktualisierung des Abschnitts "Rotlinks" (letzte analysierte Seite: {pages_checked}. {last_page_name}, Anzahl Rotlinks={len(rotlinks)}, Art={reason})')
            print(f'Seite {page_title} aktualisiert.')
        else:
            print("Keine Änderungen notwendig.")
    except Exception as e:
        traceback.print_exc()

def save_red_links_to_file(filename, rotlinks, last_page_name):
    """
    Speichert die Liste der Rotlinks in eine Datei.
 
    Args:
        filename: Der Name der Datei.
        rotlinks: Das Dictionary der Rotlinks.
    """ 
    with open(filename, "w", encoding="utf-8") as file: 
       for red_link in rotlinks:
            pages = ", ".join(sorted(rotlinks[red_link]))
            file.write(f"* [[{red_link}]] >> {pages} >>  >>\n")
    print(f"Rotlinks wurden in '{filename}' gespeichert. (letzte analysierte Seite: {pages_checked}. {last_page_name})") 

def extract_all_minerals(site, mainpage_title):
    """
    Holt alle Mineralnamen aus der 'Liste der Minerale' inkl. Unterseiten.
    Nimmt nur Einträge aus den Tabellenzeilen (mit ||).
    Gibt eine Liste mit Mineralnamen zurück, in der Reihenfolge des Auftretens.
    """

    print(f"Analysiere die Liste der Minerale {mainpage_title}")

    mainpage = pywikibot.Page(site, mainpage_title)
    text = mainpage.text

    # Unterseiten finden: {{:Liste der Minerale/X}}
    subpages = re.findall(r"\{\{:(Liste der Minerale/[A-Z])\}\}", text)

    all_minerals = []
    seen = set()

    for sub in subpages:
        page = pywikibot.Page(site, sub)
        lines = page.text.splitlines()

        for line in lines:
            # nur Tabellenzeilen mit || (also Einträge, keine Überschriften/Kommentare)
            if line.startswith("|") and "||" in line:
                code = mwparserfromhell.parse(line)
                for link in code.filter_wikilinks():
                    title = str(link.title).strip()
                    if title not in seen:
                        all_minerals.append(title)
                        seen.add(title)

    print(f"Gesamtanzahl Minerale: {len(all_minerals)} (werden ignoriert)")

    return all_minerals

def get_changedate_of_comment(page, comment_filter):

    print(f"Änderungen auf '{page.title()}' mit Kommentar enthält: '{comment_filter}'\n")

    for rev in page.revisions():
        comment = rev.comment or ""
        if comment_filter.lower() in comment.lower():
            return rev.timestamp  # datetime, timezone-aware (UTC)  

    return None

def get_recently_changed_rotlinks_articles(site, page_title, section_title="Rotlinks", days=7):
    """
    Liest den Abschnitt 'Rotlinks' einer Seite aus, extrahiert alle verlinkten Artikelnamen
    zwischen dem ersten und zweiten '>>', prüft, ob sie in den letzten 'days' Tagen über recentchanges
    geändert wurden, und gibt den Status aus.
    """
    
    print(f"Öffne Seite {page_title}")
    
    page = pywikibot.Page(site, page_title)
    text = page.text

    print("Analysiere Seiteninhalt")

    # Abschnitt finden
    section_regex = rf"==\s*{re.escape(section_title)}\s*==(.+?)(?:(?:==)|\Z)"
    match = re.search(section_regex, text, re.DOTALL)
    if not match:
        print(f"Abschnitt '{section_title}' nicht gefunden.")
        return []

    section_text = match.group(1)

    # Alle Zeilen extrahieren
    lines = [line.strip() for line in section_text.splitlines() if line.strip().startswith("*")]

    # Alle verlinkten Artikel sammeln
    article_set = set()
    current_list = {}
    for line in lines:
        parts = line.split(">>")
        if len(parts) > 2:
            linked_part = parts[1]
            redlinks = re.findall(r"\[\[([^\]|]+)", parts[0])
            links = re.findall(r"\[\[([^\]|]+)", parts[1])
            article_set.update(links)
            if not redlinks:
                printf(f"Kann die folgende Zeile nicht analysieren: {line}")
                continue
            redlink = redlinks[0]
            for target in links:
                if target not in current_list:
                    current_list[target] = []
                current_list[target].append(redlink)
                    
    print(f"{len(article_set)} Seiten gefunden")

    # Zeitpunktberechnung
    now = datetime.now(UTC)
    
    start = now.strftime("%Y%m%d%H%M%S")          # neuester Zeitpunkt
    # search for last complete update
    end = get_changedate_of_comment(page, "Art=Artikel in Chemie-Kategorie")
    
    if end == None:
        seven_days_ago = now - timedelta(days)
        end = seven_days_ago.strftime("%Y%m%d%H%M%S") # ältester Zeitpunkt  
    else:
        # one day safety margin for runtime of script
        end = end - timedelta(days=1)

    print(f"Hole Seitenänderungen zwischen {start}, {end}")

    # recentchanges abrufen (last X days)
    recent_titles = set()
    recent_changes = site.recentchanges(reverse=False, start=start, end=end, top_only=True, namespaces=[0])

    print(f"geänderte Seiten abgerufen")
    
    for idx, change in enumerate(recent_changes, start=1):
        recent_titles.add(change['title'])
        if idx % 10000 == 1:
            print(f"{idx}. changes, current = {change['title']}, {change['timestamp']}")

    print(f"{len(recent_titles)} geänderte Seiten")

    # Ausgabe mit Status
    younger_articles = []
    unchanged_article_redlinks = {}
    for idx, title in enumerate(sorted(article_set), start=1):
        if title in recent_titles:
            status = "neu (<=7 Tage)"
            younger_articles.append(title)
        else:
            unchanged_article_redlinks[title] = current_list[title]
            status = f"älter als {days} Tage"

        print(f"{idx}/{len(article_set)} {title}: {status}")

    return younger_articles, unchanged_article_redlinks

def process_category(category_names, exclusion_category_names, site, missing_substances_list, ignore_list, exclusion_list, intermediate_list):
    """
    Analysiert alle Seiten in einer Kategorie und deren Unterkategorien, um Rotlinks zu finden.

    Args:
        category_names: Eine Liste von Zielkategorien.
        exclusion_category_names: Eine Liste von Kategorien, die ausgeschlossen werden sollen.
        site: Das pywikibot.Site-Objekt, das die Wikipedia-Site repräsentiert.
    """
    target_pages = []
    for inclusion_category_name in category_names:
        print(f"Seiten in Kategorie {inclusion_category_name} abrufen...")
        target_pages = itertools.chain(target_pages, get_pages_in_category(inclusion_category_name, site))

    exclusion_pages = []
    for exclusion_category_name in exclusion_category_names:
        print(f"Seiten aus Kategorie {exclusion_category_name} ausschließen...")
        exclusion_pages = itertools.chain(exclusion_pages, get_pages_in_category(exclusion_category_name, site))
        
    print("Filterung der Zielseiten...")
    filtered_pages = filter_pages(target_pages, exclusion_pages)

    redlink_count = 0
    last_page = ""

    print("Analyse der Seiten...")
    for page in filtered_pages:
        global pages_checked, rotlinks
        pages_checked += 1

        print(f"{pages_checked}. Anzahl bisheriger unbekannter Rotlinks: {redlink_count}, aktuelle Seite: {page.title()}")

        if page.namespace() == 0 and not page.isRedirectPage() and not page.title() in exclusion_list:  # Nur Artikel im Hauptnamensraum analysieren
            try:
                red_links = find_red_links(page)
                for red_link in red_links:
                    if (red_link not in missing_substances_list):
                        if (red_link not in ignore_list and red_link not in intermediate_list):
                            if red_link not in rotlinks:
                                rotlinks[red_link] = []
                                redlink_count = redlink_count + 1
                            title = "[[" + page.title() + "]]"
                            if title not in rotlinks[red_link]:
                                rotlinks[red_link].append(title)
                            #if (redlink_count >= 500):
                            #    return page.title()
                        # else:
                        #     print(red_link + " bereits auf Ausschlussseite")
                    # else:
                    #    print(red_link + " bereits auf fehlender Seite")
            except Exception as e:
                traceback.print_exc()
                print(f"Fehler beim Verarbeiten der Seite {page.title()}: {e}")
        last_page = page.title()
    return last_page

def process_current_list(site, missing_substances_list, ignore_list, exclusion_list, intermediate_list):

    print("Analyse der Seiten...")

    younger, unchanged_article_redlinks = get_recently_changed_rotlinks_articles(
        site,
        "Wikipedia:Redaktion Chemie/Fehlende_Substanzen/Neuzugänge",
        section_title="Rotlinks",
        days=7
    )

    redlink_count = 0
    last_page = ""
    global rotlinks, pages_checked

    for page_title, red_links in unchanged_article_redlinks.items():
        pages_checked += 1
        #print(f"{pages_checked} / {len(rotlinks)} page_title = {page_title}, red_links = {red_links}")
        for red_link in red_links:
            if (red_link not in missing_substances_list):
                if (red_link not in ignore_list and red_link not in intermediate_list):
                    if red_link not in rotlinks:
                        rotlinks[red_link] = []
                        redlink_count = redlink_count + 1
                    title = "[[" + page_title + "]]"
                    if title not in rotlinks[red_link]:
                        rotlinks[red_link].append(title)
        print(f"{pages_checked}. Anzahl bisheriger bekannter Rotlinks: {redlink_count}, aktuelle Seite: {page_title}")

    print(f"Artikel jünger als 7 Tage: {len(younger)}")

    for i, page_title in enumerate(younger, start=1):

        pages_checked += 1

        page = pywikibot.Page(site, page_title)

        print(f"{pages_checked}. Anzahl bisheriger unbekannter Rotlinks: {redlink_count}, aktuelle Seite: {page.title()}")

        if page.namespace() == 0 and not page.isRedirectPage() and not page.title() in exclusion_list:  # Nur Artikel im Hauptnamensraum analysieren
            try:
                red_links = find_red_links(page)
                for red_link in red_links:
                    if (red_link not in missing_substances_list):
                        if (red_link not in ignore_list and red_link not in intermediate_list):
                            if red_link not in rotlinks:
                                rotlinks[red_link] = []
                                redlink_count = redlink_count + 1
                            title = "[[" + page.title() + "]]"
                            if title not in rotlinks[red_link]:
                                rotlinks[red_link].append(title)
            except Exception as e:
                traceback.print_exc()
                print(f"Fehler beim Verarbeiten der Seite {page.title()}: {e}")
        last_page = page.title()

    return last_page
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Chemobot Update Script")

    # Optionaler Flag
    parser.add_argument(
        "--only_update_list",
        action="store_true",
        help="Nur die Liste aktualisieren, keine neuen oder geänderten Artikel verarbeiten"
    )

    # Optionaler Flag
    parser.add_argument(
        "--update_new_and_changed_and_listed",
        action="store_true",
        help="Neue, geänderte und bereits gelistete Artikel aktualisieren"
    )

    # Argumente parsen
    args = parser.parse_args()

    # Beispiel-Logik
    if args.only_update_list and args.update_new_and_changed_and_listed:
        print("Beide Flags sind gesetzt – das wird nicht unterstützt.")
        exit(1)

    start_time = time.time()
    site = pywikibot.Site('de', 'wikipedia')

    # fehlende Substanzen Seite auswerten 
    missing_substances_list = get_missing_substances_list(site, "Wikipedia:Redaktion Chemie/Fehlende Substanzen")
    missing_taxa_list = get_missing_substances_list(site, "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Taxa")
    missing_journal_list = get_missing_substances_list(site, "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Journals")
    missing_companies_list = get_missing_substances_list(site, "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Unternehmen")
    missing_others_list = get_missing_substances_list(site, "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Sonstige Themen")
    missing_substances_list = missing_substances_list + missing_taxa_list + missing_journal_list + missing_companies_list + missing_others_list

    ignore_list = get_ignore_list(site)
    minerals = extract_all_minerals(site, "Liste der Minerale")
    ignore_list = ignore_list + minerals

    exclusion_list = get_exclusion_list(site)
    intermediate_list = get_intermediate_list(site)

    # Kategorien und Ausschlüsse
    category_names = ["Kategorie:Chemische Verbindung nach Element", "Kategorie:Chemische Verbindung nach Strukturelement", "Kategorie:Mineral"]
    exclusion_category_names = ["Kategorie:Chemikaliengruppe", "Kategorie:Wirkstoffgruppe"]
    last_page_name = ""
    
    # Prüfen, welche Flags gesetzt wurden
    if args.only_update_list:
        print("Nur die Liste wird aktualisiert.")
        reason = "geänderte Artikel aus Neuzugänge"
        last_page_name= process_current_list(site, missing_substances_list, ignore_list, exclusion_list, intermediate_list)
    elif args.update_new_and_changed_and_listed:
        print("Neue, geänderte und gelistete Artikel werden aktualisiert.")
        print("Suchart aktuell noch nicht unterstützt")
        exit(0)
    else:
        # Analyse starten
        reason = "Artikel in Chemie-Kategorie"
        last_page_name= process_category(category_names, exclusion_category_names, site, missing_substances_list, ignore_list, exclusion_list, intermediate_list)
    
    # Rotlinks speichern
    update_wikipedia_page(site, rotlinks, last_page_name, reason)

    #save_red_links_to_file("rotlinks.txt", rotlinks, last_page_name)

    # Zusammenfassung
    print(f"\nAnzahl geprüfter Seiten: {pages_checked}")
    print(f"Anzahl gefundener Rotlinks: {len(rotlinks)}")
    print("\nLaufzeit: ", human_readable_time_difference(start_time, time.time()))
