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

def find_categories(text):
    """
    Findet alle Vorkommen von Texten, die mit "[[Kategorie:" beginnen und mit "]]" enden,
    aber nicht "|" enthalten.

    :param text: Der Eingabetext, in dem gesucht werden soll.
    :return: Eine Liste von gefundenen Kategorietexten.
    """
    # Definiere das reguläre Ausdrucksmuster
    pattern = r'\[\[Kategorie:[^|\]]+\]\]'
    
    # Verwende re.findall(), um alle Vorkommen des Musters zu finden
    matches = re.findall(pattern, text)
    
    return matches

def check_and_adopt_categories_in_page(page, subcategory_names):
    """
    Adds text to the end of a Wikipedia page.

    Args:
        page: The Wikipedia page to which text is to be added.
    """
    page_title = page.title()
    original_text = page.text
    new_content = original_text
    first_change = True
    # print(page_title)

    cat_list = find_categories(original_text)

    if cat_list:
        for cat in cat_list:
            if "|" in cat: 
                print("Warnung: Kategorie ", cat, " enthält \"|\" !")
            else:
                real_cat = cat.replace("[", "").replace("]", "")
                if real_cat in subcategory_names:
                    new_cat = cat.replace("]]", "| " + page_title + "]]")
                    if first_change == True:
                        first_change = False
                        print(page_title)
                        print(f"cats = {cat_list}")
                        print("found cat ", cat, " -> ", new_cat)                    
                    new_content = new_content.replace(cat, new_cat)

    if new_content != original_text:
        # Die Seite mit dem neuen Inhalt speichern
        try:
            global pages_changed
            pages_changed = pages_changed + 1
            print(pages_changed, ". ", page_title)
            # print(f"{new_content}")
            page.text = new_content
            page.save(summary="ChemoBot: Ergänze Strukturkategorien um Leerzeichen, um Stoffgruppe an den Anfang der Artikelliste in der Kategorie zu sortieren", minor=False)
            # print(f"Text erfolgreich zu {page_title} hinzugefügt.")

            # vorzeitiger exit im ersten Testlauf
            # if pages_changed >= 1:
            #    exit(1)
        
        except pywikibot.exceptions.OtherPageSaveError as e:
            print(f"Fehler beim Speichern der Seite {page_title}: {e}")


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

def get_all_subcategories(site, categories):
    """
    Recursively fetches all subcategories for each category in a given list of categories.

    :param categories: A list of category names (e.g., ['Category:Science', 'Category:Physics']).
    :param site: Pywikibot site object. Default is English Wikipedia.
    :return: A set of all unique subcategory names from all input categories.
    """
    
    all_subcategory_names = set()

    def fetch_subcategories(cat):
        for subcategory in cat.subcategories():
            if subcategory.title() not in all_subcategory_names:
                all_subcategory_names.add(subcategory.title())
                fetch_subcategories(subcategory)  # Recursively fetch subcategories

    for category_name in categories:
        category = pywikibot.Category(site, category_name)
        fetch_subcategories(category)

    return all_subcategory_names

def process_pages_in_category(pages):

    print("Hole Liste der Subkategorien")
    subcategory_names = get_all_subcategories(site, include_category_names)

    for page in pages:
        check_and_adopt_categories_in_page(page, subcategory_names)

if __name__ == "__main__":
    zeitanfang = time.time()	
   
    print("Baue Verbindung zu Wikipedia auf.")
    site = pywikibot.Site('de', 'wikipedia')  
    category_name = "Kategorie:Stoffgruppe"
    include_category_names = ["Kategorie:Chemische Verbindung nach Element", "Kategorie:Chemische Verbindung nach Strukturelement"]  
    inclusion_category_names = []
    exclude_pages = []

    # Test on special page
    # page = pywikibot.Page(site, "Lithium-Nickel-Cobalt-Aluminium-Oxide")
    # list_of_cats = ['Kategorie:Lithiumverbindung', 'Kategorie:Nickelverbindung', 'Kategorie:Cobaltverbindung', 'Kategorie:Aluminiumverbindung', 'Kategorie:Sauerstoffverbindung']
    # check_and_adopt_categories_in_page(page, list_of_cats) 
    # exit(1)
    
    print("Hole die Liste der Artikel")
    pages = get_pages_in_category(category_name, site)
    
    n = 0
    for page in pages:
        n=n+1
    print("Anzahl der Artikel = ", n)

    # iterator destroyed because of counting pages. Therefore get pages again.
    pages = get_pages_in_category(category_name, site)
       
    print("Bearbeite Liste der Artikel")
    process_pages_in_category(pages)
    
    print(f"\npages_checked = {pages_checked}, pages_changed = {pages_changed}")
    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))
