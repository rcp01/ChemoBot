import pywikibot
from pywikibot import pagegenerators
import re
import itertools
import time
import traceback
import requests

pages_checked = 0
pages_changed = 0


# Funktion, um die externen Links von einer Wikipedia-Seite zu extrahieren
def extract_external_links(site, page_title):
    page = pywikibot.Page(site, page_title)
    content = page.text
    # Extrahiere Links, die mit "http" oder "https" beginnen
    links = set()
    for line in content.split('\n'):
        if line.startswith('* http://') or line.startswith('* https://'):
            line = line.replace("* ", "")
            links.add(line.strip())
    return links

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
    
    special_excludes = ['']
    
    exclusion_titles = {page.title() for page in exclusion_pages_gen}

    for page in target_pages_gen:
        title = page.title()
        if title not in exclusion_titles and not page.isRedirectPage() and (title not in special_excludes):
            yield page

def get_external_links(page: pywikibot.Page):
    site = page.site
    api_url = site.base_url(site.apipath())

    headers = {
        "User-Agent": "ChemoBot/1.0 (https://de.wikipedia.org/wiki/Benutzer:ChemoBot)"
    }

    params = {
        "action": "parse",
        "page": page.title(),
        "prop": "externallinks",
        "format": "json"
    }

    response = requests.get(api_url, params=params, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data.get("parse", {}).get("externallinks", [])


def process_category(category_names, exclusion_category_names, predatory_links, site):
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

    start_time = time.time()  # Startzeit der Schleife
    interval = 60  # Intervall in Sekunden
    count = 0

    print("process pages")
    for page in filtered_pages:

        count = count + 1
        if time.time() - start_time >= interval:
            start_time = time.time()  # Reset der Startzeit für die nächste Nachricht
            print(f"{count}. Seite: {page.title()}")

        # print(page.title())
        global pages_checked
        pages_checked = pages_checked + 1
        if page.namespace() == 0 and not page.isRedirectPage():  # Only process articles (namespace 0)
            try:
                external_links = get_external_links(page)

                page_text = page.text
                # print(f"Überprüfe Seite: {page.title()}")
                for ext in external_links:
                    for pred in predatory_links:
                        if pred in ext:
                            print(f"  -> Link gefunden: {pred} in {page.title()}")
                    # else:
                    #    print(f"  -> Link NICHT gefunden: {link}")

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


# Hauptfunktion
def main():
    zeitanfang = time.time()
    # Verbinde mit der Wikipedia-Seite
    site = pywikibot.Site('de', 'wikipedia')  # Achte darauf, dass du 'de' und 'wikipedia' korrekt konfigurierst

    # Extrahiere die externen Links von der Seite "Benutzer:Rjh/predatory"
    predatory_links = extract_external_links(site, "Benutzer:Rjh/predatory")
    print(f"Gefundene externe Links: {len(predatory_links)} Links")

    # Überprüfe, ob diese Links in den Seiten einer bestimmten Kategorie vorhanden sind
    category_names = ["Kategorie:Chemische Verbindung nach Element", "Kategorie:Chemische Verbindung nach Strukturelement"]  
    #exclusion_category_names = ["Kategorie:Mineral" , "Kategorie:Chemikaliengruppe", "Kategorie:Wirkstoffgruppe"]
    exclusion_category_names = ["Kategorie:Mineral"]

    process_category(category_names, exclusion_category_names, predatory_links, site)
    print(f"\npages_checked = {pages_checked}, pages_changed = {pages_changed}")
    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))
 
if __name__ == "__main__":
    main()
