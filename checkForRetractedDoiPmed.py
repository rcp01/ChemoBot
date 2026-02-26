import aiohttp
import asyncio
import csv
import re
import pywikibot
from pywikibot import pagegenerators
import itertools
import time
from helperfunctions import human_readable_time_difference
import traceback

pages_checked = 0
pages_found = 0


URL = (
    "https://gitlab.com/api/v4/projects/"
    "crossref%2Fretraction-watch-data/"
    "repository/files/retraction_watch.csv/raw?ref=main"
)


CHUNK_SIZE = 1024 * 64
MAX_RETRIES = 10


# --------------------------------------------------
# Robust streaming reader with resume
# --------------------------------------------------
async def stream_with_resume(session, url):

    downloaded = 0
    total = None
    retries = 0

    while True:
        headers = {}
        if downloaded:
            headers["Range"] = f"bytes={downloaded}-"
            print(f"\nReconnect bei Byte {downloaded}")

        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()

                if total is None:
                    total = response.content_length
                    print("Gesamtgröße:", total or "unbekannt")

                async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                    downloaded += len(chunk)

                    if total:
                        percent = downloaded / total * 100
                        print(f"\rDownload {percent:6.2f}% ", end="")

                    yield chunk

            break

        except Exception as e:
            retries += 1
            if retries > MAX_RETRIES:
                raise RuntimeError("Zu viele Verbindungsabbrüche") from e

            wait = min(30, 2 ** retries)
            print(f"\nVerbindung verloren → retry in {wait}s")
            await asyncio.sleep(wait)


# --------------------------------------------------
# CSV Parsing während Stream
# --------------------------------------------------
async def download_and_parse_csv(url):

    retraction_doi = []
    original_doi = []
    retraction_pmid = []
    original_pmid = []

    timeout = aiohttp.ClientTimeout(total=None)

    async with aiohttp.ClientSession(timeout=timeout) as session:

        buffer = ""
        header = None

        async for chunk in stream_with_resume(session, url):

            text = chunk.decode("utf-8", errors="ignore")
            buffer += text

            lines = buffer.split("\n")
            buffer = lines.pop()

            for line in lines:
                if not line.strip():
                    continue

                if header is None:
                    header = next(csv.reader([line]))
                    continue

                row = next(csv.reader([line]))
                data = dict(zip(header, row))

                doi = normalize_doi(data.get("RetractionDOI", "").strip())
                if doi and len(doi)>12: 
                    retraction_doi.append(doi)
                doi = normalize_doi(data.get("OriginalPaperDOI", "").strip())
                if doi and len(doi)>12: 
                    original_doi.append(doi)
                pmid = data.get("RetractionPubMedID", "").strip()
                if pmid and len(pmid) > 5:
                    retraction_pmid.append(pmid)
                pmid = data.get("OriginalPaperPubMedID", "").strip()
                if pmid and len(pmid) > 5:
                    original_pmid.append(pmid)

    print("\nDownload fertig")

    return retraction_doi, original_doi, retraction_pmid, original_pmid


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
    Filters pages that are in target_pages but not in exclusion_pages
    and prevents duplicate pages.
    """

    special_excludes = {''}

    exclusion_titles = {page.title() for page in exclusion_pages_gen}

    seen_titles = set()   # <-- HIER passiert die Magie

    for page in target_pages_gen:
        title = page.title()

        if title in seen_titles:
            continue  # Duplikat → überspringen

        seen_titles.add(title)

        if (
            title not in exclusion_titles
            and not page.isRedirectPage()
            and title not in special_excludes
        ):
            yield page


# --------------------------------------------------
# DOI normalisieren
# --------------------------------------------------
def normalize_doi(x):
    if not x:
        return ""
    x = x.strip().lower()
    x = x.replace("https://doi.org/", "")
    x = x.replace("http://doi.org/", "")
    x = x.replace("doi:", "")
    return x


# --------------------------------------------------
# Hauptfunktion
# --------------------------------------------------
def find_retracted_in_references(
    references,
    retraction_doi,
    original_doi,
    retraction_pmid,
    original_pmid
):
    """
    Prüft ob DOI oder PubMedID als Teilstring in references vorkommen.

    Rückgabe:
        dict mit Treffer-Sets
    """

    # ---------- Referenzen vorbereiten ----------
    reference_blob = normalize_doi("\n".join(references))

    # ---------- DOI Treffer ----------
    def find_doi_matches(doi_list):
        matches = set()

        for doi in doi_list:
            if doi in reference_blob:
                matches.add(doi)

        return matches

    # ---------- PubMed Treffer ----------
    # Wortgrenzen verhindern Teiltreffer (z.B. 123 in 12345)
    def find_pmid_matches(pmid_list):
        matches = set()
        for pmid in pmid_list:
            pattern = rf"\b{re.escape(str(pmid))}\b"
            if re.search(pattern, reference_blob):
                matches.add(pmid)
        return matches

    # ---------- Ergebnis ----------
    result = {
        "retraction_doi": find_doi_matches(retraction_doi),
        "original_doi": find_doi_matches(original_doi),
        "retraction_pmid": find_pmid_matches(retraction_pmid),
        "original_pmid": find_pmid_matches(original_pmid),
    }

    result["any_match"] = any(result.values())

    return result

# Funktion, um Referenzen aus dem Wikitext zu extrahieren
def extract_references(wikitext):
    """
    Extrahiert die Referenzen aus dem Wikitext einer Seite.
    """
    references = re.findall(
        r"<ref(?!erences)\b[^>/]*>(.*?)</ref>",
        wikitext,
        re.DOTALL | re.IGNORECASE
    )
    return references

def process_category(category_names, exclusion_category_names, r_doi, o_doi, r_pmid, o_pmid, site):
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
    found_links = []
    for page in filtered_pages:
        count += 1
        if time.time() - start_time >= interval:
            start_time = time.time()  # Reset der Startzeit für die nächste Nachricht
            print(f"{count}. Seite: {page.title()}")

        global pages_checked, pages_found
        pages_checked += 1

        if page.namespace() == 0 and not page.isRedirectPage():  # Only process articles (namespace 0)
            try:
                page_text = page.text
                # Extrahiere Referenzen aus dem Wikitext
                references = extract_references(page_text)                    
                
                result = find_retracted_in_references(references, r_doi, o_doi, r_pmid, o_pmid)
                
                if result and result["any_match"]:
                    print(f"Seite: {page.title()} -> {result}")
                    pages_found += 1
                    if pages_found > 200:
                        break
            except Exception as e:
                traceback.print_exc()
                print(f"Failed to process page {page.title()}: {e}")

    if found_links:
        write_results_to_page(site, found_links)


# --------------------------------------------------
async def main(site):
    r_doi, o_doi, r_pmid, o_pmid = await download_and_parse_csv(URL)
    
    print("\nErgebnis:")
    print("Retraction DOI:", len(r_doi))
    print("Original DOI:", len(o_doi))
    print("Retraction PubMedID:", len(r_pmid))
    print("Original PubMedID:", len(o_pmid))

    # optional: Listen selbst ausgeben
    print("\nBeispielwerte:")
    print("RetractionDOI:", r_doi[:5])
    print("OriginalPaperDOI:", o_doi[:5])
    print("RetractionPubMedID:", r_pmid[:5])
    print("OriginalPaperPubMedID:", o_pmid[:5])

    #references = ["Smith et al. (2020) https://doi.org/10.3892/ol.2024.14676", "Smith et al. (2022) PMID 39345721"];
    #testresult = find_retracted_in_references(references, r_doi, o_doi, r_pmid, o_pmid)
    #print(f"testresult = {testresult}")
    #exit(0)

    #page = pywikibot.Page(site, "Aliskiren")
    #references = extract_references(page.text)                    
    #testresult = find_retracted_in_references(references, r_doi, o_doi, r_pmid, o_pmid)
    #print(f"testresult = {testresult}")
    #exit(0)

    # Kategorie- und Ausschlusskategorien festlegen
    category_names = ["Kategorie:Chemische Verbindung nach Element", "Kategorie:Chemische Verbindung nach Strukturelement"]
    exclusion_category_names = ["Kategorie:Mineral"]
    
    process_category(category_names, exclusion_category_names, r_doi, o_doi, r_pmid, o_pmid, site)
    
if __name__ == "__main__":

    zeitanfang = time.time()
    site = pywikibot.Site('de', 'wikipedia')  # Stelle sicher, dass du 'de' und 'wikipedia' korrekt konfigurierst

    asyncio.run(main(site))

    print(f"\npages_checked = {pages_checked}, pages_found = {pages_found}")
    print("\nLaufzeit: ", human_readable_time_difference(zeitanfang, time.time()))
