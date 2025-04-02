#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import itertools
import time
import traceback
import re
import requests

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
    return pagegenerators.CategorizedPageGenerator(category, recurse=True)


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
                            rotlinks[red_link].append("[[" + page.title() + "]]")
                            if (redlink_count >= 500):
                                return page.title()
                        # else:
                        #     print(red_link + " bereits auf Ausschlussseite")
                    # else:
                    #    print(red_link + " bereits auf fehlender Seite")
            except Exception as e:
                traceback.print_exc()
                print(f"Fehler beim Verarbeiten der Seite {page.title()}: {e}")
    return page.title()

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

def translate_substance_name_to_englisch(substance_name):
    if bool(re.search(r"e$" , substance_name)) and not re.search(r"(säure|ose|ase)$", substance_name):
        substance_name += "s"
    elif re.search(r"(on|id|en|din|mid|dol)$", substance_name):
        substance_name += "e"
#    else:
#        print("nothing")
    substance_name = substance_name.replace("essigsäure", "acetic acid")
    substance_name = substance_name.replace("benzoesäure", "benzoic acid")
    substance_name = substance_name.replace("propansäure", "propanoic acid")
    substance_name = substance_name.replace("andelsäure", "andelic acid")
    substance_name = substance_name.replace("salicylsäure", "salicylic acid")
    substance_name = substance_name.replace("catechusäure", "catechuic acid")
    substance_name = substance_name.replace("allussäure", "allic acid")
    substance_name = substance_name.replace("phthalsäure", "phthalic acid")
    substance_name = substance_name.replace("uttersäure", "utyric acid")
    substance_name = substance_name.replace("hosphonsäure", "hosphorous acid")
    substance_name = substance_name.replace("cyansäure", "cyanic acid")
    substance_name = substance_name.replace("diensäure", "dienoic acid")
    substance_name = substance_name.replace("weinsäure", "tartaric acid")
    substance_name = substance_name.replace("ylsäure", "ylic acid")
    substance_name = substance_name.replace("insäure", "inic acid")
    substance_name = substance_name.replace("ilsäure", "ilic acid")
    substance_name = substance_name.replace("onsäure", "onic acid")
    substance_name = substance_name.replace("olsäure", "olic acid")
    substance_name = substance_name.replace("oesäure", "oic acid")
    substance_name = substance_name.replace("säure", " acid")
    substance_name = substance_name.replace("naphthalin", "naphthalene")
    substance_name = substance_name.replace("chinone", "quinone")
    substance_name = substance_name.replace("chinon", "quinone")
    substance_name = substance_name.replace("cumarin", "coumarin")
    substance_name = substance_name.replace("Natrium", "Sodium ")
    substance_name = substance_name.replace("natrium", "sodium ")
    substance_name = substance_name.replace("Kalium", "Potassium ")
    substance_name = substance_name.replace("kalium", "potassium ")
    substance_name = substance_name.replace("Mangan", "Manganese ")
    substance_name = substance_name.replace("mangan", "manganese ")
    substance_name = substance_name.replace("enzol", "enzene")
    substance_name = substance_name.replace("oxazol", "oxazole")
    substance_name = substance_name.replace("azetat", "acetate")
    substance_name = substance_name.replace("aldehyd", "aldehyde")
    substance_name = substance_name.replace("azin", "azine")
    substance_name = substance_name.replace("pikryl", "picryl")
    substance_name = substance_name.replace("zucker", " sugar")
    substance_name = substance_name.replace("ethinyl", "ethynyl")
    substance_name = substance_name.replace("citrat", "citrate")
    substance_name = substance_name.replace("laurin", "laurine")
    substance_name = substance_name.replace("phosphat", "phosphate")
    substance_name = substance_name.replace("phenolat", "phenolate")
    substance_name = substance_name.replace("silicat", "silicate")
    substance_name = substance_name.replace("than", "thane")
    substance_name = substance_name.replace("phthalat", "phthalate")
    substance_name = substance_name.replace("oluol", "oluene")
    substance_name = substance_name.replace("resorcin", "resorcinol")
    substance_name = substance_name.replace("imonen-", "imonene-")
    substance_name = substance_name.replace("Brenzcatechin", "Catechol")
    substance_name = substance_name.replace("brenzcatechin", "catechol")
    substance_name = substance_name.replace("farbstoff", " dye")
    substance_name = substance_name.replace(" (Chemie)", "")
    substance_name = substance_name.replace("Salz", "Salt")
    substance_name = substance_name.replace("salz", "salt")
    substance_name = substance_name.replace("harz", "resin")
    substance_name = substance_name.replace("blei", "lead ")
    substance_name = substance_name.replace("Blei", "Lead ")
    substance_name = substance_name.replace("Eisen", "Iron ")
    substance_name = substance_name.replace("eisen", "iron ")
    substance_name = substance_name.replace("Titan", "Titanium ")
    substance_name = substance_name.replace("titan", "titanium ")
    substance_name = substance_name.replace("Zink", "Zinc ")
    substance_name = substance_name.replace("zink", "zinc ")
    substance_name = substance_name.replace("Wolfram", "Tungsten ")
    substance_name = substance_name.replace("wolfram", "tungsten ")
    substance_name = substance_name.replace("Zinn", "Tin ")
    substance_name = substance_name.replace("zinn", "tin ")
    substance_name = substance_name.replace("Quecksilber", "Mercury ")
    substance_name = substance_name.replace("quecksilber", "mercury ")
    substance_name = substance_name.replace("Silber", "Silver ")
    substance_name = substance_name.replace("silber", "silver ")
    substance_name = substance_name.replace("molybdän", "molybdenum ")
    substance_name = substance_name.replace("Molybdän", "Molybdenum ")
   
    if not "bromid" in substance_name.lower():
        substance_name = substance_name.replace("brom", "bromo")    
        substance_name = substance_name.replace("Brom", "bromo")

    if "fluoranthen" in substance_name.lower():
        substance_name = substance_name.replace("fluoranthen", "fluoranthene")        
        substance_name = substance_name.replace("fluoranthenee", "fluoranthene")        
    elif "fluoranthen" in substance_name.lower(): 
        substance_name = substance_name.replace("fluoriden", "fluorene")
    elif "fluorenon" in substance_name.lower(): 
        substance_name = substance_name.replace("fluorenon", "fluorenone")
    else:
        if not "fluorid" in substance_name.lower() and not "fluoren" in substance_name.lower():
            substance_name = substance_name.replace("fluor", "fluoro")
            substance_name = substance_name.replace("Fluor", "fluoro")

    if not "chlorid" in substance_name.lower():
        substance_name = substance_name.replace("chlor", "chloro")
        substance_name = substance_name.replace("Chlor", "chloro")

    if not "iodid" in substance_name.lower() and not "iodo" in substance_name.lower():
        substance_name = substance_name.replace("iod", "iodo")
        substance_name = substance_name.replace("Iod", "Iodo")

    return substance_name


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

            response = requests.get(url, headers=headers)
            response = requests.get(url, headers=headers) # retry

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

def update_wikipedia_page(site, new_entries, last_page_name):
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
            match = re.search(fr'\* \[\[{red_link}\]\] >> .*? >>\s*(.*?)\s*>>\s*', section_content, re.DOTALL)
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
            page.save(f'Automatische Aktualisierung des Abschnitts "Rotlinks" (letzte analysierte Seite: {pages_checked}. {last_page_name})')
            print(f'Seite {page_title} aktualisiert.')
        else:
            print("Keine Änderungen notwendig.")
    except Exception as e:
        traceback.print_exc()


def human_readable_time_difference(start_time, end_time):
    """
    Gibt die Zeitdifferenz zwischen zwei Zeitpunkten in menschlich lesbarer Form zurück.

    Args:
        start_time: Startzeit.
        end_time: Endzeit.

    Returns:
        String: Zeitdifferenz in lesbarer Form.
    """
    delta = end_time - start_time
    days, seconds = divmod(delta, 3600 * 24)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    result = []
    if days > 0:
        result.append(f"{int(days)} Tage")
    if hours > 0:
        result.append(f"{int(hours)} Stunden")
    if minutes > 0:
        result.append(f"{int(minutes)} Minuten")
    if seconds > 0:
        result.append(f"{round(seconds, 1)} Sekunden")

    return ', '.join(result)


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

    # Zusammenfassung
    print(f"\nAnzahl geprüfter Seiten: {pages_checked}")
    print(f"Anzahl gefundener Rotlinks: {len(rotlinks)}")
    print("\nLaufzeit: ", human_readable_time_difference(start_time, time.time()))
