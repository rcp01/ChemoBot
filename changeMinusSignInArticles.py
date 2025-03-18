#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
import itertools
import time

# Fix UnicodeEncodeError: 'charmap' codec can't encode characters
import sys
import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pages_checked = 0
pages_changed = 0


def change_text_of_page(page):
    """
    Adds text to the end of a Wikipedia page.

    Args:
        page: The Wikipedia page to which text is to be added.
    """
    page_title = page.title()
    text = page.get()
    # Text in Zeilen aufteilen
    lines = text.splitlines()

    # Durch die Zeilen iterieren und nach "(-)" suchen
    for line_number, line in enumerate(lines, start=1):
        matches = re.finditer(r"\(-\)", line)
        for match in matches:
            match_start = match.start()
            match_end = match.end()
            # Überprüfen, ob das Match zwischen '[[Datei:' und '|' steht
            before_match = line[:match_start]  # Teil der Zeile vor dem Match
            after_match = line[match_end:]  # Teil der Zeile nach dem Match
           
            if before_match.endswith('|Name='):
                continue

            # Überprüfen, ob das Match zwischen '|Titel=' und '}}' steht
            last_titel_pos = before_match.rfind('|Titel=')
            if last_titel_pos != -1:  # Wenn '|Titel=' vor dem Match existiert
                first_brace_pos = after_match.find('}}') + match_end
                
                if first_brace_pos > match_end:  # Wenn '}}' nach dem Match existiert
                    continue
           
            global pages_changed
            if '[[Datei:' in before_match and '|' in after_match:
                # Letztes Auftreten von '[[Datei:' vor dem Match und erstes Auftreten von '|' nach dem Match suchen
                last_datei_pos = before_match.rfind('[[Datei:')
                first_pipe_pos = after_match.find('|') + match_end  # relative Position korrigieren
                
                if not (last_datei_pos > match_start and first_pipe_pos > match_end):
                    print(f"Gefunden in Zeile {line_number} of {page_title}: '{line.strip()}'")
                    pages_changed = pages_changed + 1
            else:
                print(f"Gefunden in Zeile {line_number} of {page_title}: '{line.strip()}'")
                pages_changed = pages_changed + 1

            
    
def get_pages_in_category(category_name, site):
    """
    Retrieves all pages in a given category and its subcategories.

    Args:
        category_name: The name of the category.
        site: The pywikibot.Site object representing the Wikipedia site.

    Returns:
        A set of pages in the category and its subcategories.
    """
    category = pywikibot.Category(site, category_name)
    return pagegenerators.CategorizedPageGenerator(category, recurse=True)

def filter_pages(target_pages_gen, exclusion_pages_gen):
    """
    Filters pages that are in target_pages but not in exclusion_pages.

    Args:
        target_pages_gen: A generator for pages in the target category.
        exclusion_pages_gen: A generator for pages in the exclusion category.

    Yields:
        Pages that are in target_pages_gen but not in exclusion_pages_gen.
    """
    
    special_excludes = []
    
    exclusion_titles = {page.title() for page in exclusion_pages_gen}

    for page in target_pages_gen:
        title = page.title()
        if title not in exclusion_titles and not page.isRedirectPage() and (title not in special_excludes):
            yield page

def process_category(category_names, exclusion_category_names, site):
    """
    Adds text to all pages in a category and its subcategories.

    Args:
        category_name: The name of the category to process.
        site: The pywikibot.Site object representing the Wikipedia site.
    """
    target_pages = []
    # Get all pages in the exclusion category and its subcategories
    for inclusion_category_name in category_names:
        print(f"get pages in category {inclusion_category_name}")
        target_pages = itertools.chain(target_pages, get_pages_in_category(inclusion_category_name, site))

    # Get all pages in the exclusion category and its subcategories
    print("get pages in exclusion category")
    
    exclusion_pages = []
    for exclusion_category_name in exclusion_category_names:
        print(f"exclude pages from {exclusion_category_name}")
        exclusion_pages = itertools.chain(exclusion_pages, get_pages_in_category(exclusion_category_name, site))

    # Subtract exclusion pages from target pages
    print("filter out exclusion category pages from category pages")
    filtered_pages = filter_pages(target_pages, exclusion_pages)

    print("process pages")
    for page in filtered_pages:
        # print(page.title())
        global pages_checked
        pages_checked = pages_checked + 1
        if page.namespace() == 0:  # Only process articles (namespace 0)
            try:
                change_text_of_page(page)
                # print(f"Added text to page: {page.title()}")
            except Exception as e:
                print(f"Failed to add text to page {page.title()}: {e}")

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


if __name__ == "__main__":
    zeitanfang = time.time()	
    # Beispielhafte Strings
    # string = "Das ist ein Testβ-3-Test-N-4-βTest-O-1. ### Aflatoxin-B1-8,9-epoxid ## "
    strings = ['Aluminium-tris(8-hydroxychinolin)',
'4-Acetamido-TEMPO',
'Delphinidin-3-O-sambubiosid-5-O-glucosid',
'Trans-2-((Dimethylamino)methylimino)-5-(2-(5-nitro-2-furyl)vinyl)-1,3,4-oxadiazol',
'Aflatoxin-B1-8,9-epoxid',
'Cis-Abienol',
'Tetrakis(triphenylphosphin)palladium(0)',
'(Z)-3-Hexenolprimverosid',
'Isopropyl-β-D-thiogalactopyranosid',
'Beta-Sekretase-Inhibitor',
]

#    for string in strings:
#        sorted_string = sort_patterns_to_end(string)

#        # Ergebnis anzeigen
#        print(string, "->", remove_brackets_except_roman_numerals(string), " -> ",  sorted_string)

#    exit(1)
   
    site = pywikibot.Site('de', 'wikipedia')  
    category_names = ["Kategorie:Chemische Verbindung nach Element", "Kategorie:Chemische Verbindung nach Strukturelement"]  
    exclusion_category_names = ["Kategorie:Mineral", "Kategorie:Chemikaliengruppe", "Kategorie:Wirkstoffgruppe"]

    process_category(category_names, exclusion_category_names, site)
    print(f"\npages_checked = {pages_checked}, pages_changed = {pages_changed}")
    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))
