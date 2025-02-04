#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import itertools
import time
import traceback
import re

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
            if not linked_page.exists() and not linked_page.title().startswith("Vorlage:")
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


def process_category(category_names, exclusion_category_names, site, missing_substances_list, ignore_list):
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
            print(f"{pages_checked}. Seite: {page.title()}")

        if page.namespace() == 0 and not page.isRedirectPage():  # Nur Artikel im Hauptnamensraum analysieren
            try:
                red_links = find_red_links(page)
                for red_link in red_links:
                    if (red_link not in missing_substances_list):
                        if (red_link not in ignore_list):
                            if red_link not in rotlinks:
                                rotlinks[red_link] = []
                                redlink_count = redlink_count + 1
                            rotlinks[red_link].append("[[" + page.title() + "]]")
                            if (redlink_count >= 500):
                                return
                        # else:
                        #     print(red_link + " bereits auf Ausschlussseite")
                    # else:
                    #    print(red_link + " bereits auf fehlender Seite")
            except Exception as e:
                traceback.print_exc()
                print(f"Fehler beim Verarbeiten der Seite {page.title()}: {e}")


def update_wikipedia_page(site, new_entries):
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Neuzugänge"
    #page_title = "Benutzer:Rjh/Test4"
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
            new_section_content += f"* [[{red_link}]] >> {pages} >>  >>\n"

        new_text = text.replace(section_content, new_section_content)
        
        if new_text != text:
            page.text = new_text
            page.save("Automatische Aktualisierung des Abschnitts 'Rotlinks'")
            print("Seite aktualisiert.")
        else:
            print("Keine Änderungen notwendig.")
    except Exception as e:
        traceback.print_exc()

def save_red_links_to_file(filename, rotlinks):
    """
    Speichert die Liste der Rotlinks in eine Datei.

    Args:
        filename: Der Name der Datei.
        rotlinks: Das Dictionary der Rotlinks.
    """
    with open(filename, "w", encoding="utf-8") as file:
        file.write("== Rotlinks ==\n")
        file.write("Aktuelle Rotlinks im Bereich Chemie, die nicht auf [[Wikipedia:Redaktion Chemie/Fehlende Substanzen]] und nicht in der [[Wikipedia:Redaktion Chemie/Fehlende Substanzen/Ausschlussliste]] bzw. [[Wikipedia:Redaktion Chemie/Fehlende Substanzen/Varianten]] genannt sind:\n\n")
        file.write("Format ist <Rotlinklemmaname> >> <von Seiten verlinkt> >> <CAS-Nummer>, <wikidata eintrag> >> Abkürzung Kategorie\n")
        for red_link in sorted(rotlinks.keys()):
            pages = ", ".join(sorted(rotlinks[red_link]))
            file.write(f"* [[{red_link}]] >> {pages} >>  >>\n")
    print(f"Rotlinks wurden in '{filename}' gespeichert.")



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
        result.append(f"{days} Tage")
    if hours > 0:
        result.append(f"{hours} Stunden")
    if minutes > 0:
        result.append(f"{minutes} Minuten")
    if seconds > 0:
        result.append(f"{round(seconds, 1)} Sekunden")

    return ', '.join(result)


if __name__ == "__main__":
    start_time = time.time()
    site = pywikibot.Site('de', 'wikipedia')

    # fehlende Substanzen Seite auswerten 
    missing_substances_list = get_missing_substances_list(site)
    ignore_list = get_ignore_list(site)

    # Kategorien und Ausschlüsse
    category_names = ["Kategorie:Chemische Verbindung nach Element", "Kategorie:Chemische Verbindung nach Strukturelement"]
    exclusion_category_names = ["Kategorie:Mineral", "Kategorie:Chemikaliengruppe", "Kategorie:Wirkstoffgruppe"]

    # Analyse starten
    process_category(category_names, exclusion_category_names, site, missing_substances_list, ignore_list)

    # Rotlinks speichern
    update_wikipedia_page(site, rotlinks)

    # Zusammenfassung
    print(f"\nAnzahl geprüfter Seiten: {pages_checked}")
    print(f"Anzahl gefundener Rotlinks: {len(rotlinks)}")
    print("\nLaufzeit: ", human_readable_time_difference(start_time, time.time()))
