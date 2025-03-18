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

def remove_brackets_except_roman_numerals(s):
    """
    Remove parentheses from the string except when they enclose Roman numerals.

    Args:
        s (str): The input string.

    Returns:
        str: The string with parentheses removed except those enclosing Roman numerals.
    """
    roman_numerals = {'0', 'I', 'V'}
    result = []
    index = 0
    length = len(s)
    
    while index < length:
        char = s[index]
        
        if char == '(':
            # Start collecting content within parentheses
            content = []
            index += 1
            while index < length and s[index] != ')' and s[index] != '(':
                content.append(s[index])
                index += 1
            
            # Skip the closing parenthesis
            if index < length and s[index] == ')':
                index += 1
            
            # Check if the content inside parentheses contains only Roman numerals
            if (content != []):
                content_str = ''.join(content)
                if set(content_str).issubset(roman_numerals):
                    result.append(f"({content_str})")
                else:
                    result.append(content_str)
        else:
            if (char != '(' and char != ')'):
                result.append(char)
            index += 1
    
    return ''.join(result)
    
def sort_patterns_to_end(s):
    """
    Verschiebt alle Teile des Strings, die den angegebenen Mustern entsprechen, ans Ende des Strings,
    wobei die Reihenfolge beibehalten wird.

    Args:
        s (str): Der Eingabestring.
        patterns (list of str): Eine Liste von Mustern, die ans Ende verschoben werden sollen.

    Returns:
        str: Der neu sortierte String.
    """
    # Platz für den Rest des Strings und die gefundenen Teile
    patterns = [r'Alpha-', r'Beta-', r'Gamma-', r'Trans-', r'Cis-', r'^[ONDZERSLαβ]-', r'^[ONDZERSLαβ][-,][ONDZERSLαβ]-', r"\d+", r'β', r'\(Z\)', r'-\(N-', r'\([omp]-', r'-f\)', r'-\dH-', r'-B1-', r'-[ONDZERSLαβ]-[ONDZERSLαβ]-', r'-[ONDZERSLαβ]-', r"\(0\)", r'^[tT]ert-', r'^[Ss]ec-', r'-tert-', r'-sec-']
    matches = []
    
    sorted_parts = []
    found=True
    while found:
        matches = []
        found=False
        # Durchsuche den String nach allen Übereinstimmungen und speichere sie in der Reihenfolge ihres Auftretens
        for pattern in patterns:
            regex = re.compile(pattern)
            # Iteriere über die Übereinstimmungen in der Reihenfolge des Auftretens
            for match in regex.finditer(s):
                found=True
                matches.append((match.start(), match.group()))

        # Sortiere die Übereinstimmungen nach ihrer ursprünglichen Position
        matches.sort(key=lambda x: x[0])
    
        # Entferne die Übereinstimmungen aus dem ursprünglichen Text
        for _, match in matches:
            s = s.replace(match, '', 1)
            sorted_parts.append(match)
            break

    if (''.join(sorted_parts) != ''):
        result = ''.join(s) + ''.join(sorted_parts)
        result = re.sub('[-,:.′]', '', ''.join(result))
        result = remove_brackets_except_roman_numerals(result)
        return result
    else:
        return s
    
    # Variant 2 -> Hält die Reihenfolge im String nicht ein
    # Suche nach allen Übereinstimmungen für jedes Pattern in der Liste
    # for pattern in patterns:
    #    regex = re.compile(pattern)
    #    # Finde alle Übereinstimmungen für das aktuelle Pattern
    #    found = regex.findall(s)
    #    matches.extend(found)  # Füge die gefundenen Übereinstimmungen zur Liste hinzu
        
    #    # Entferne die Übereinstimmungen aus dem ursprünglichen Text
    #    s = regex.sub('', s)

    # Sortiere die gefundenen Übereinstimmungen am Ende des Strings
    #result = s + ''.join(matches)
    #result = re.sub('[-,:.′]', '', ''.join(result))
    #result = remove_brackets_except_roman_numerals(result)
    #return result

    # Variant 1 -> Findet auch S- mitten im String, zum Beispiel in Naphthol-AS-MX-Phosphat
    
    # remaining_parts = []
    # sorted_parts = []

    # Durchlaufe alle Zeichen im String -> found also 
    #pos = 0
    #while pos < len(s):
    #    matched = False
    #    for pattern in patterns:
    #        # Suche nach Mustern an der aktuellen Position
    #        match = re.match(pattern, s[pos:])
    #        if match:
    #            # Füge das gefundene Muster zu den sortierten Teilen hinzu
    #            sorted_parts.append(match.group(0))
    #            # Bewege die Position nach dem Muster weiter
    #            pos += len(match.group(0))
    #            matched = True
    #            break
    #    if not matched:
    #        # Füge die verbleibenden Zeichen zum Rest des Strings hinzu
    #        remaining_parts.append(s[pos])
    #        pos += 1
    
    # Füge die sortierten Teile ans Ende des verbleibenden Strings
    #if (''.join(sorted_parts) != ''):
    #    result = ''.join(remaining_parts) + ''.join(sorted_parts)
    #    result = re.sub('[-,:.′]', '', ''.join(result))
    #    result = remove_brackets_except_roman_numerals(result)
    #    return result
    #else:
    #    return s

def sort_umlaute_and_numbers(text):
    """
    Sorts all umlauts and numbers to the end of the string and removes spaces, hyphens, commas, and parentheses.

    Args:
        text: The input string.

    Returns:
        A modified string with umlauts and numbers at the end and specified characters removed.
    """
    # Define sets of umlauts and numbers
    umlauts = "β"
    numbers = "0123456789"
    
    # Separate characters into two lists
    main_part = []
    umlaut_and_number_part = []
    
    for char in text:
        if char in numbers or char in umlauts:
            umlaut_and_number_part.append(char)
        else:
            main_part.append(char)
    
    # Combine the two parts
    if (''.join(umlaut_and_number_part) != ""):
        main_part = re.sub('[-,():.′]', '', ''.join(main_part))
    result = ''.join(main_part) + ''.join(umlaut_and_number_part)
    return result

def add_text_to_page(page):
    """
    Adds text to the end of a Wikipedia page.

    Args:
        page: The Wikipedia page to which text is to be added.
    """
    page_title = page.title()
    sorted = sort_patterns_to_end(page_title)
    
    if (sorted != page_title):
        # Load the current content of the page
        original_text = page.text

        if ((original_text.find("{{SORTIERUNG:") == -1) and (original_text.find("{{DEFAULTSORT:") == -1)):

            text_to_add = "{{SORTIERUNG:" + sorted + "}}"

            # Suchen nach Kategorien, die mit [[Kategorie: beginnen
            categories_pos = original_text.find('[[Kategorie:')
            
            if categories_pos != -1:
                # Text unmittelbar vor den Kategorien einfügen
                new_content = original_text[:categories_pos] + text_to_add + "\n" + original_text[categories_pos:]
            else:
                # Text am Ende der Seite hinzufügen
                new_content = original_text + "\n" + text_to_add
            
            # Die Seite mit dem neuen Inhalt speichern
            try:
                
                global pages_changed
                pages_changed = pages_changed + 1
                print(pages_changed, ". ", page_title, " -> ", sorted)
                # print(f"{new_content}")
                page.text = new_content
                page.save(summary="ChemoBot: Ergänze Sortierschlüssel im Artikel", minor=False)
                # print(f"Text erfolgreich zu {page_title} hinzugefügt.")
                
                # vorzeitiger exit im ersten Testlauf
                #if pages_changed >= 20:
                #    exit(1)
                
                # Test for script
                # Testpage = pywikibot.Page(site, "Benutzer:Rjh/Test")
                # TestpageText = Testpage.text
                # Testpage.text = original_text
                # Testpage.save(summary="ChemoBot: Orginaltext des Artikels für Änderungsvergleich setzen", minor=False)
                # Testpage.text = new_content
                # Testpage.save(summary="ChemoBot: Ergänze Sortierschlüssel im Artikel", minor=True)
                # Testpage.text = TestpageText
                # Testpage.save(summary="ChemoBot: Stelle Originalinhalt der Testseite wieder her", minor=False)
                
                # exit(1)
                # replace_section_title_when_with_references_found(page, "Quellen", "Einzelnachweise")
                # return

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

def filter_pages(target_pages_gen, exclusion_pages_gen):
    """
    Filters pages that are in target_pages but not in exclusion_pages.

    Args:
        target_pages_gen: A generator for pages in the target category.
        exclusion_pages_gen: A generator for pages in the exclusion category.

    Yields:
        Pages that are in target_pages_gen but not in exclusion_pages_gen.
    """
    
    special_excludes = ['T-2-Toxin', 'Fura-2AM', 'H12MDI', 'Biotin-PEG2-Amin', 'Cy5-Succinimidylester', 'HFPO-DA', 'Naphthol-AS-MX-Phosphat', 'L-Selektrid']
    
    exclusion_titles = {page.title() for page in exclusion_pages_gen}

    for page in target_pages_gen:
        title = page.title()
        numbers = re.findall(r'\d+', title)
        if title not in exclusion_titles and not re.search(r'\d+$', title) and not page.isRedirectPage() and (not any(int(num) > 20 for num in numbers) and (' ' not in title)) and (title not in special_excludes):
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
                add_text_to_page(page)
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
    exclusion_category_names = ["Kategorie:Mineral", "Kategorie:Stoffgruppe", "Kategorie:Chemikaliengruppe", "Kategorie:Wirkstoffgruppe", "Kategorie:Proteinkomplex", "Kategorie:Stoffgemisch"]

    process_category(category_names, exclusion_category_names, site)
    print(f"\npages_checked = {pages_checked}, pages_changed = {pages_changed}")
    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))
