#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
import itertools
import time
import traceback

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
    new_text = text
    
    # Text in Zeilen aufteilen
    lines = text.splitlines()

    # Durch die Zeilen iterieren und nach pattern suchen
    for line_number, line in enumerate(lines, start=1):
        pattern = r'\((R|S|E|Z)\)-|(tert|sec|cis|trans|iso)-'
        matches = re.finditer(pattern, line)
        for match in matches:
            match_start = match.start()
            match_end = match.end()

            before_match = line[:match_start]  # Teil der Zeile vor dem Match
            after_match = line[match_end:]  # Teil der Zeile nach dem Match
           
            if before_match.endswith('|Name='):
                continue

            if before_match.endswith('[['):
                continue

            if before_match.rfind('[[', 0, match_start) != -1 and after_match.rfind('|', 0) != -1:
                continue

            if before_match.rfind('[[Datei:', 0, match_start) != -1 and after_match.rfind('|', 0) != -1:
                continue

            if before_match.rfind('[[Datei:', 0, match_start) != -1 and after_match.rfind(']]', 0) != -1:
                continue

            if before_match.rfind('<nowiki>', 0, match_start) != -1 and after_match.rfind('</nowiki>', 0) != -1:
                continue

            if before_match.rfind('<ref', 0, match_start) != -1 and after_match.rfind('</ref>', 0) != -1:
                continue

            if before_match.rfind('| title', 0, match_start) != -1 and after_match.rfind('}}', 0) != -1:
                continue

            if before_match.rfind('|titel=', 0, match_start) != -1:
                continue

            if (before_match.rfind('| Suchfunktion', 0, match_start) != -1) or (before_match.rfind('|Suchfunktion', 0, match_start) != -1):
                continue

            if before_match.rfind('|Name=', 0, match_start) != -1 and after_match.rfind('|', 0) != -1:
                continue

            if before_match.rfind('{{Commonscat|', 0, match_start) != -1 and after_match.rfind('|', 0) != -1:
                continue

            if before_match.rfind('{{CLH-ECHA', 0, match_start) != -1 and after_match.rfind('}}', 0) != -1:
                continue

            if before_match.rfind('{{CanJChem', 0, match_start) != -1 and after_match.rfind('}}', 0) != -1:
                continue

            if before_match.rfind('{{OrgSynth', 0, match_start) != -1 and after_match.rfind('}}', 0) != -1:
                continue

            if before_match.rfind('{{SORTIERUNG', 0, match_start) != -1 and after_match.rfind('}}', 0) != -1:
                continue

            if before_match.rfind('Strukturformel von', 0, match_start) != -1 and after_match.rfind(']]', 0) != -1:
                continue

            if before_match.rfind('===', 0, match_start) != -1 and after_match.rfind('===', 0) != -1:
                continue

            if after_match.rfind('.svg', 0) != -1 and (after_match.rfind('.svg', 0) < after_match.rfind('|', 0)):
                continue

            if after_match.rfind('.pdf', 0) != -1 and (after_match.rfind('.pdf', 0) < after_match.rfind('|', 0)):
                continue

            if after_match.rfind('.png', 0) != -1 and (after_match.rfind('.png', 0) < after_match.rfind('|', 0)):
                continue

            if before_match.endswith('<sup>'):
                continue

            if before_match.endswith('ante'):
                continue

            if before_match.endswith('\'\''):
                print("Warnung: " + page_title + ": " + line + "\n\n")
                continue

            if match.group(1):
                new_line = line.replace(before_match + match.group(0) + after_match, before_match + "(''" + match.group(1) + "'')-" + after_match)
            else: 
               if before_match.rfind('[[', 0, match_start) != -1 and after_match.rfind(']]', 0) != -1:
                   continue
               new_line = line.replace(before_match + match.group(0) + after_match, before_match + "''" + match.group(2) + "''-" + after_match)
            
            print(page_title + ": " + line + " ->\n " + new_line + "\n\n")
            new_text = new_text.replace(line, new_line)

    if (new_text != text):
        # print(page_title)
        page.text = new_text
        page.save(summary="ChemoBot: Kursivschreibung von Descriptoren", minor=True)
        global pages_changed
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
    
    special_excludes = ['Isopulegole']
    
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
                traceback.print_exc()
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
    site = pywikibot.Site('de', 'wikipedia')  

    pagenames = ["Esafoxolaner"]

    # Test on special page
    #for pagename in pagenames:
    #    page = pywikibot.Page(site, pagename)
    #    change_text_of_page(page) 
    # exit(1)
   
    category_names = ["Kategorie:Chemische Verbindung nach Element", "Kategorie:Chemische Verbindung nach Strukturelement"]  
    exclusion_category_names = ["Kategorie:Mineral", "Kategorie:Chemikaliengruppe", "Kategorie:Wirkstoffgruppe"]

    process_category(category_names, exclusion_category_names, site)
    print(f"\npages_checked = {pages_checked}, pages_changed = {pages_changed}")
    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))
