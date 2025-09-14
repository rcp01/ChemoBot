import pywikibot
from pywikibot import pagegenerators
import time
import re
from helperfunctions import translate_substance_name_to_englisch, human_readable_time_difference

def get_all_pages_in_category(cat, recurse=True):
    """Rekursiv alle Seiten in einer Kategorie sammeln, mit Fortschrittsanzeige."""
    pages = set()
    catgen = cat.subcategories(recurse=recurse)
    subcats = list(catgen)
    print(f"🔄 {len(subcats)} Unterkategorien gefunden...")

    for i, subcat in enumerate(subcats, 1):
        print(f"[{i}/{len(subcats)}] Unterkategorie: {subcat.title()}")
        subpages = list(subcat.articles(namespaces=[0]))
        print(f"  → {len(subpages)} Seiten")
        pages.update(subpages)

    main_pages = list(cat.articles(namespaces=[0]))
    print(f"Hauptkategorie: {cat.title()} mit {len(main_pages)} Seiten")
    pages.update(main_pages)

    print(f"Gesamtseiten gesammelt: {len(pages)}")
    return pages

def main(kategoriename):
    start_time = time.time()
    print(f"Untersuche Kategorien in '{kategoriename}'...\n")

    site = pywikibot.Site("de", "wikipedia")
    cat = pywikibot.Category(site, kategoriename)

    # Lade alle verwaisten Seiten
    lonely_pages = pagegenerators.LonelyPagesPageGenerator(site=site, total=None)

    print("\nLaufzeit verwaist: ", human_readable_time_difference(start_time, time.time()))

    # 🔍 Effizient alle Artikel (Namensraum 0) in Kategorie + Unterkategorien
    all_pages_gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True, namespaces=[0])
    all_pages = list(all_pages_gen)
    print(f"Gesamtanzahl Artikel: {len(all_pages)}")

    print("\nLaufzeit Kats: ", human_readable_time_difference(start_time, time.time()))
    
    preloaded_pages = pagegenerators.PreloadingGenerator(all_pages, groupsize=50)

    unlinked_pages = []

    for i, page in enumerate(preloaded_pages, 1):
        if page.isRedirectPage():
            continue

        backlinks = list(page.backlinks(filter_redirects=False, namespaces=[0]))
        backlinks = [bl for bl in backlinks if bl.title() != page.title()]
        
        print(f"{i}. {len(backlinks)} für {page.title()} ")

        if not backlinks:
            unlinked_pages.append(page.title())

    # 📋 Wikitext vorbereiten
    unlinked_pages.sort(key=lambda title: title.lower())

    output_lines = []

    current_letter = ""
    for title in unlinked_pages:
        first_char = title[0].upper()
        group = first_char if first_char.isalpha() else "0–9 / Sonderzeichen"

        if group != current_letter:
            current_letter = group
            output_lines.append(f"\n== {current_letter} ==")
        output_lines.append(f"* [[{title}]]")

    new_output = "\n".join(output_lines)

    # 📝 Bestehenden Seiteninhalt laden
    page_title = "Wikipedia:WikiProjekt_Verwaiste_Seiten/Kategorien/Chemie"
    page = pywikibot.Page(site, page_title)

    try:
        old_text = page.get()
    except Exception as e:
        print(f"Fehler beim Laden der Seite: {e}")
        return

    # 🔎 Zeilen vor der ersten Überschrift erhalten
    match = re.search(r'^==.*$', old_text, flags=re.MULTILINE)
    if match:
        header_index = match.start()
        preserved_text = old_text[:header_index].rstrip()
    else:
        preserved_text = old_text.strip()

    # 🆕 Neuen Inhalt zusammenbauen
    new_text = preserved_text + "\n\n" + new_output.strip()

    # 💾 Seite speichern
    if new_text != old_text:
        page.text = new_text
        page.save(summary=f"Liste der nicht verlinkten Seiten in Chemie-Kategorie aktualisiert ({len(unlinked_pages)} Seiten)", minor=False)
        print("Seite erfolgreich aktualisiert.")
    else:
        print("Keine Änderungen notwendig.")

    print("\nLaufzeit: ", human_readable_time_difference(start_time, time.time()))

if __name__ == "__main__":
    # main("Kategorie:Chemie")  # Beispiel
    main("Kategorie:Chemische Verbindung nach Element")
