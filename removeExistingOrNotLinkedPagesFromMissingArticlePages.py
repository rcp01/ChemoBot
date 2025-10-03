import pywikibot
import re
import time
from helperfunctions import human_readable_time_difference

# Liste der zu bearbeitenden Seiten
PAGES = [
    "Wikipedia:Redaktion Chemie/Fehlende Substanzen",
    "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Taxa",
    "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Journals",
    "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Fehlende Unternehmen",
]

# Regex: Artikelname + optionale QID ([[:d:Qxxxxx|wd]])
ENTRY_RE = re.compile(r"\[\[([^\]|#]+)\]\].*?\[\[:d:(Q\d+)\|")

def should_remove(site, title, qid, cache, repo):
    """
    Prüft, ob die Zeile entfernt werden soll:
    1. Artikel im Hauptnamensraum existiert -> löschen
    2. Artikel existiert nicht + keine Backlinks + keine dewiki-Sitelink im Wikidata -> löschen
    """
    key = (title, qid)
    if key in cache:
        return cache[key]

    page = pywikibot.Page(site, title)

    # Nur Hauptnamensraum
    if page.namespace() != 0:
        cache[key] = False
        return False

    if page.exists():
        # Artikel existiert -> löschen
        print(f"delete entry for existing page {title}")
        cache[key] = True
        return True

    # Artikel existiert nicht, prüfen ob Backlinks existieren
    refs = page.getReferences(namespaces=[0], total=1)
    has_refs = any(refs)
    if has_refs:
        cache[key] = False
        return False

    # Keine Backlinks → Wikidata prüfen
    if qid:
        item = pywikibot.ItemPage(repo, qid)
        try:
            item.get()
            if "dewiki" in item.sitelinks:
                cache[key] = True
                print(f"delete entry for not linked page {title} with german page")
                return True
        except Exception as e:
            print(f"Fehler beim Laden von {qid}: {e}")
            cache[key] = False
            return False

    cache[key] = False
    return False


def process_page(site, repo, page_title):
    page = pywikibot.Page(site, page_title)
    original_text = page.text
    lines = original_text.splitlines()
    new_lines = []
    removed = []
    cache = {}

    total = len(lines)
    print(f"Starte Verarbeitung von {page_title} ({total} Zeilen)")

    for i, line in enumerate(lines, start=1):
        m = ENTRY_RE.search(line)
        if not m:
            new_lines.append(line)
        else:
            title, qid = m.groups()
            if should_remove(site, title.strip(), qid, cache, repo):
                removed.append(title.strip())
            else:
                new_lines.append(line)

        # Fortschritt ausgeben
        print(f"  Fortschritt {i}/{total} ({(i/total)*100:.1f}%)")

    new_text = "\n".join(new_lines).strip() + "\n"

    if new_text != original_text:
        print(f"  {len(removed)} Links entfernt aus {page_title}: {removed[:15]}{'...' if len(removed) > 15 else ''}")
        page.text = new_text
        page.save(summary=f"Entferne {len(removed)} erledigte/verwaiste Einträge aus der Liste")
    else:
        print(f"  Keine Änderungen in {page_title}")


def main():
    start_time = time.time()    
    site = pywikibot.Site("de", "wikipedia")
    repo = site.data_repository()
    for title in PAGES:
        process_page(site, repo, title)
    print("\nLaufzeit: ", human_readable_time_difference(start_time, time.time()))


if __name__ == "__main__":
    main()
