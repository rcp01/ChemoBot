#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import itertools
import time
import traceback
import re
import requests
from helperfunctions import translate_substance_name_to_englisch, human_readable_time_difference

# Globale Variablen
pages_checked = 0
rotlinks = {}  # Dictionary der Rotlinks: {Rotlink: [Seitennamen]}

def get_missing_substances_list(site):
    """
    Extrahiert die Liste fehlender Substanzen von der angegebenen Seite.

    Args:
        site (pywikibot.Site): Die Site-Instanz für Wikipedia.

    Returns:
        list: Eine Liste mit den Namen der fehlenden Substanzen.
    """
    
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen"
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

    start_time = time.time()  # Startzeit der Schleife
    interval = 60  # Intervall in Sekunden
    count = 0
    redlink_count = 0
    last_page = ""

    print("Analyse der Seiten...")
    for page in filtered_pages:
        global pages_checked, rotlinks
        pages_checked += 1

        if time.time() - start_time >= interval:
            start_time = time.time()  # Reset der Startzeit für die nächste Nachricht
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
                response = requests.get(url, headers=headers)
                response = requests.get(url, headers=headers) # retry
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

    print(f"\"{chemical_name_org}\" -> \"{chemical_name}\" : None")
    return ""

def update_wikipedia_page(site, rotlinks, last_page_name):
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Neuzugänge"
    #page_title = "Benutzer:ChemoBot/Tests/Neuzugänge"
    page = pywikibot.Page(site, page_title)
    
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

        for red_link in sorted(rotlinks.keys()):
            pages = ", ".join(sorted(rotlinks[red_link]))
            addon = ""

            # preserve old cas if it is known
            try:
                match = re.search(fr'\* \[\[{red_link}\]\] >> .*? >>\s*(.*?)\s*>>\s*', section_content, re.DOTALL)
            except Exception as e:
                print(f"Fehler beim Verarbeiten der Seite {page.title()}: {e}")
                print(f"red_link = {red_link}")
                print(f"section_content = {section_content}")

            if match and match.group(1).strip() != "":
                addon = f"{match.group(1).strip()}"
            else:
                cas = search_cas_number(red_link)
                if (cas != ""):
                    wikidata = search_wikidata_number(cas)
                    if (wikidata != ""):
                        addon = f"{cas},{wikidata}"
                    else:
                        addon = f"{cas}"            

            new_section_content += f"* [[{red_link}]] >> {pages} >> {addon} >>\n"
               
        new_text = text.replace(section_content, new_section_content)
        
        if new_text != text:
            global pages_checked
            page.text = new_text
            page.save(f'Automatische Aktualisierung des Abschnitts "Rotlinks" (letzte analysierte Seite: {pages_checked}. {last_page_name}, Anzahl Rotlinks={len(rotlinks)})')
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


if __name__ == "__main__":
    start_time = time.time()
    site = pywikibot.Site('de', 'wikipedia')

    # fehlende Substanzen Seite auswerten 
    missing_substances_list = get_missing_substances_list(site)
    ignore_list = get_ignore_list(site)
    exclusion_list = get_exclusion_list(site)
    intermediate_list = get_intermediate_list(site)

    # Kategorien und Ausschlüsse
    category_names = ["Kategorie:Chemische Verbindung nach Element", "Kategorie:Chemische Verbindung nach Strukturelement"]
    exclusion_category_names = ["Kategorie:Mineral", "Kategorie:Chemikaliengruppe", "Kategorie:Wirkstoffgruppe"]

    # Analyse starten
    last_page_name= process_category(category_names, exclusion_category_names, site, missing_substances_list, ignore_list, exclusion_list, intermediate_list)

    # Rotlinks speichern
    update_wikipedia_page(site, rotlinks, last_page_name)

    #save_red_links_to_file("rotlinks.txt", rotlinks, last_page_name)

    # Zusammenfassung
    print(f"\nAnzahl geprüfter Seiten: {pages_checked}")
    print(f"Anzahl gefundener Rotlinks: {len(rotlinks)}")
    print("\nLaufzeit: ", human_readable_time_difference(start_time, time.time()))
