import pywikibot
from pywikibot import pagegenerators
import re
import itertools
import time
import traceback

pages_checked = 0
pages_changed = 0

# Funktion, um die externen Links von einer Wikipedia-Seite zu extrahieren
def extract_external_names(site, page_title):
    page = pywikibot.Page(site, page_title)
    content = page.text
    # Extrahiere Links, die mit "http" oder "https" beginnen
    links = set()
    for line in content.split('\n'):
        if line.startswith('* '):
            line = line.replace("* ", "")
            links.add(line.strip())
    return links

# Funktion, um Referenzen aus dem Wikitext zu extrahieren
def extract_references(wikitext):
    """
    Extrahiert die Referenzen aus dem Wikitext einer Seite.
    """
    references = re.findall(r"<ref[ >](.*?)(?:<\/ref>|\/>)", wikitext, re.DOTALL)
    return references

# Funktion, um zu prüfen, ob ein externer Name in den Referenzen vorkommt
def check_names_in_references(references, external_names):
    """
    Überprüft, ob externe Links in den Referenzen vorhanden sind.

    Args:
        references: Liste von Referenzen (als Text).
        external_names: Menge von externen Namen.

    Returns:
        Eine Liste von gefundenen Namen.
    """
    found_names = []
    for reference in references:
        for name in external_names:
            # print(name, " ===> ", reference)
            if name in reference:
                if name == "RIDE" and (("HYDRIDE" in reference) or ("TRIDE" in reference) or ("TELLURIDE" in reference) or ("FLUORIDE" in reference) or ("CHLORIDE" in reference) or ("TRIDENT" in reference)): 
                    continue
                if name == "Journal of Chemistry" and (("Canadian Journal of Chemistry" in reference) or ("Asian Journal of Chemistry" in reference) or ("Arabian Journal of Chemistry" in reference) or ("New Journal of Chemistry" in reference) or ("Australian Journal of Chemistry" in reference) or ("Israel Journal of Chemistry" in reference) or ("Turkish Journal of Chemistry" in reference) or ("Indian Journal of Chemistry" in reference) or ("Chinese Journal of Chemistry" in reference) or ("European Journal of Chemistry" in reference) or ("Journal of Chemistry and Applied Chemical Engineering" in reference) or ("Oriental Journal of Chemistry" in reference)): 
                    continue
                if name == "Journal of Energy" and "Journal of Energy Engineering" in reference: 
                    continue
                if name == "Scientific World" and "The Scientific World Journal" in reference: 
                    continue
                if name == "Applied Microbiology" and (("Applied Microbiology and Biotechnology" in reference) or ("Journal of Applied Microbiology" in reference)): 
                    continue
                if name == "Engineering Sciences" and "Mathematical, Physical and Engineering Sciences" in reference: 
                    continue
                if name == "Pharmacognosy Research" and "Journal of Pharmacy & Pharmacognosy Research" in reference: 
                    continue
                if name == "BioChem" and "ChemBioChem" in reference: 
                    continue
                if name == "RICA" and (("AMERICA" in reference) or ("AFRICA" in reference) or ("LYRICA" in reference) or ("TRICA" in reference)): 
                    continue
                if name == "IPP" and (("DIPP" in reference) or ("CIPPH" in reference) or ("NIPPON" in reference) or ("-IPP" in reference) or ("IPPN" in reference) or ("TIPP" in reference)): 
                    continue
                if name == "Journal of Tropical Medicine" and "The American Journal of Tropical Medicine and Hygiene" in reference: 
                    continue
                if name == "BioMed" and (("BioMed Central" in reference) or ("BioMed research international")): 
                    continue
                if name == "Journal of Toxicology" and (("Journal of Toxicology and Environmental Health" in reference) or ("International Journal of Toxicology" in reference)): 
                    continue
                if name == "ECI" and "PRECI" in reference: 
                    continue
                if name == "AMJ" and "SAMJ" in reference: 
                    continue
                if name == "RECI" and "PRECISION" in reference: 
                    continue
                if name == "JIM" and (("JIMD" in reference) or ("JIMO" in reference)): 
                    continue
                if name == "MCA" and (("MCAT" in reference) or ("DIMCARB" in reference) or ("MCAC" in reference)): 
                    continue
                if name == "CSJ" and (("/CSJ" in reference) or ("BCSJ") in reference): 
                    continue
                if name == "JOP" and "JOPSS" in reference: 
                    continue
                if name == "CAE" and "CAESIUM" in reference: 
                    continue
                if name == "ABP" and "ABPA" in reference: 
                    continue
                if name == "IJP" and "Indian Journal of Plastic Surgery" in reference: 
                    continue
                if name == "JHP" and "AJHP" in reference: 
                    continue
                if name == "JMC" and "name=\"JMC" in reference: 
                    continue
                if name == "JPR" and (("WJPR" in reference) or ("Journal of Pain Research" in reference)): 
                    continue
                if name == "BioChem" and "BioChemica" in reference: 
                    continue
                if name == "Journal of Nanotechnology" and "Beilstein Journal of Nanotechnology" in reference: 
                    continue
                if name == "Medical Sciences" and "Journal of Experimental Physiology and Cognate Medical Sciences" in reference: 
                    continue
                if name == "Forensic Sciences" and "Journal of Forensic Sciences" in reference: 
                    continue
                if name == "Horticulturae" and (("Scientia Horticulturae" in reference) or ("Acta Horticulturae") in reference): 
                    continue
                if name == "International Journal of Food Science" and "International Journal of Food Science & Technology" in reference: 
                    continue
                if name == "International Journal of Environment" and "International Journal of Environmental Science & Technology" in reference: 
                    continue
                if name == "Science International" and "Forensic Science International" in reference: 
                    continue
                if name == "Journal of Nutrition and Metabolism" and "Mediterranean Journal of Nutrition and Metabolism" in reference: 
                    continue
                if name == "Journal of Science" and "Journal of Science Education" in reference: 
                    continue
                if name == "Geriatrics" and "Geriatrics & Gerontology International" in reference: 
                    continue
                if name == "Journal of Sports Medicine" and "British Journal of Sports Medicine" in reference: 
                    continue
                if name == "Physiologia" and "Physiologia Plantarum" in reference: 
                    continue
                found_names.append(name)
                found_names = list(set(found_names))                
    return found_names


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


def process_category(category_names, exclusion_category_names, external_names, site):
    """
    Processes all pages in the specified category and checks for external links in references.

    Args:
        category_names: List of category names to process.
        exclusion_category_names: List of category names to exclude.
        external_links: Set of external links to check.
        site: The pywikibot.Site object representing the Wikipedia site.
    """
    target_pages = []
    # Get all pages in the inclusion categories
    for inclusion_category_name in category_names:
        print(f"Get pages in category {inclusion_category_name}")
        target_pages = itertools.chain(target_pages, get_pages_in_category(inclusion_category_name, site))

    # Get all pages in the exclusion categories
    print("Get pages in exclusion categories")
    exclusion_pages = []
    for exclusion_category_name in exclusion_category_names:
        print(f"Exclude pages from {exclusion_category_name}")
        exclusion_pages = itertools.chain(exclusion_pages, get_pages_in_category(exclusion_category_name, site))

    # Subtract exclusion pages from target pages
    print("Filter out exclusion category pages from category pages")
    filtered_pages = filter_pages(target_pages, exclusion_pages)

    start_time = time.time()  # Startzeit der Schleife
    interval = 60  # Intervall in Sekunden
    count = 0

    print("Process pages")
    for page in filtered_pages:
        count += 1
        if time.time() - start_time >= interval:
            start_time = time.time()  # Reset der Startzeit für die nächste Nachricht
            print(f"{count}. Seite: {page.title()}")

        global pages_checked
        pages_checked += 1

        if page.namespace() == 0 and not page.isRedirectPage():  # Only process articles (namespace 0)
            try:
                page_text = page.text
                # Extrahiere Referenzen aus dem Wikitext
                references = extract_references(page_text)

                # Prüfe, ob externe Links in den Referenzen vorkommen
                found_names = check_names_in_references(references, external_names)

                if found_names:
                    print(f"* [[{page.title()}]]: {', '.join(found_names)}")
            except Exception as e:
                traceback.print_exc()
                print(f"Failed to process page {page.title()}: {e}")


def human_readable_time_difference(start_time, end_time):
    """
    Gibt die Zeitdifferenz zwischen zwei datetime-Objekten in menschlich lesbarer Form zurück.
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


# Hauptfunktion
def main():
    zeitanfang = time.time()
    site = pywikibot.Site('de', 'wikipedia')  # Stelle sicher, dass du 'de' und 'wikipedia' korrekt konfigurierst

    # Extrahiere die Namen von der Seite "Benutzer:Rjh/predatory_names"
    external_names = extract_external_names(site, "Benutzer:Rjh/predatory_names")
    print(f"Gefundene externe Namen: {len(external_names)} Namen")

    # Test on special page
    # page = pywikibot.Page(site, "Anhalinin")
    # refs = extract_references(page.text)
    # print(f"{refs}")
    # found_names = check_names_in_references(refs, external_names)
    # if found_names:
    #    print(f"* [[{page.title()}]]: {', '.join(found_names)}")
    # exit(1)

    # Kategorie- und Ausschlusskategorien festlegen
    category_names = ["Kategorie:Chemische Verbindung nach Element", "Kategorie:Chemische Verbindung nach Strukturelement"]
    exclusion_category_names = ["Kategorie:Mineral"]

    # Prozess starten
    process_category(category_names, exclusion_category_names, external_names, site)
    print(f"\npages_checked = {pages_checked}, pages_changed = {pages_changed}")
    print("\nLaufzeit: ", human_readable_time_difference(zeitanfang, time.time()))


if __name__ == "__main__":
    main()
