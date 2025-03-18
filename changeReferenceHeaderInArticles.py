#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pywikibot
import time

cats_checked = 0
pages_checked = 0
pages_changed = 0

def replace_section_title_when_with_references_found(page, section_title, new_section_title):
    """
    Durchsucht den Text einer Seite in einem bestimmten Kapitel nach einem Suchtext.

    :param page: Die Seite, die durchsucht werden soll.
    :param section_title: Der Titel des Kapitels.
    :param new_section_title: Die neue Kapitelüberschrift.
    :return: True, wenn der Text gefunden wird, sonst False.
    """
    global pages_checked
    pages_checked = pages_checked + 1
    text = page.get()
    # print(text)
	
    # Suche nach dem Kapitel
    section_start = text.find(f'== {section_title} ==')
    if section_start == -1:
        return False
    
    # Suche nach dem Ende des Kapitels
    next_section_start = text.find('==', section_start + len(section_title) + 6)
    if next_section_start == -1:
        section_text = text[section_start:]
    else:
        section_text = text[section_start:next_section_start]
    
    # print(section_text)
	
    if ("<references />" in section_text) or ("<references>" in section_text and "</references>" in section_text):
        updated_text = text.replace(f'== {section_title} ==', f'== {new_section_title} ==')
        # print(updated_text)
        page.text = updated_text
        # page.save(summary=f'Ersetze Kapitelüberschrift "{section_title}" mit Inhalt "<references" durch Kapitelüberschrift "{new_section_title}"')
        global pages_changed
        pages_changed = pages_changed + 1
        print(pages_changed, ". Seite ", page.title(), " geändert, Seiten geprüft:", pages_checked, sep='')
        return True
    else:
        return False

def check_category_pages(category, depth=0):
    global cats_checked
    cats_checked = cats_checked + 1
    site = pywikibot.Site()
    cat = pywikibot.Category(site, category)
    print('.', end='', flush=True)

	# Test for script
    # page = pywikibot.Page(site, "Benutzer:Rjh/Test")
    # replace_section_title_when_with_references_found(page, "Quellen", "Einzelnachweise")
    # return

    # Listen alle Seiten in der Kategorie auf
    for page in cat.articles():
        try:
           replace_section_title_when_with_references_found(page, "Quellen", "Einzelnachweise")
 			  
        except Exception as e:
            # print(f'Fehler beim Lesen der Seite {page.title()}: {e}')
            print('-', end='', flush=True)

    # Rekursiv durch alle Unterkategorien
    for subcat in cat.subcategories():
        check_category_pages(subcat.title(), depth + 1)

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

def main():
    zeitanfang = time.time()	
    category_name = 'Chemie'
    check_category_pages(category_name)
    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))

if __name__ == "__main__":
    main()