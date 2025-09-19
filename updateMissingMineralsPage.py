import pywikibot
import re
import time
import mwparserfromhell
from collections import defaultdict
from helperfunctions import human_readable_time_difference


def extract_all_minerals(site, mainpage_title):
    """Holt alle Mineralnamen aus den Unterseiten der 'Liste der Minerale'."""
    mainpage = pywikibot.Page(site, mainpage_title)
    text = mainpage.text

    subpages = re.findall(r"\{\{:(Liste der Minerale/[A-Z])\}\}", text)

    all_minerals = []
    seen = set()

    for sub in subpages:
        page = pywikibot.Page(site, sub)
        lines = page.text.splitlines()

        for line in lines:
            if line.startswith("|") and "||" in line:
                code = mwparserfromhell.parse(line)
                for link in code.filter_wikilinks():
                    title = str(link.title).strip()
                    if title not in seen:
                        all_minerals.append(title)
                        seen.add(title)

    return all_minerals


def count_article_links(site, title):
    """
    Zählt, wie viele Links auf eine Seite aus dem Artikelnamensraum (NS=0) zeigen.
    """
    page = pywikibot.Page(site, title)
    total = 0
    try:
        for _ in page.getReferences(namespaces=[0], follow_redirects=False):
            total += 1
    except Exception as e:
        print(f"Fehler bei {title}: {e}")
    return total


def group_by_thresholds(results, thresholds=(30, 25, 20, 15)):
    """
    Gruppiert die Ergebnisse nach Schwellwerten, behält die Reihenfolge der Eingabe.
    """
    grouped = defaultdict(list)
    for mineral, count in results:
        for t in thresholds:
            if count >= t:
                grouped[t].append(mineral)
                break
    return grouped


def update_list_block(site, page_title, block_title, grouped):
    """
    Ersetzt nur den Block, der mit `; block_title:` beginnt,
    und schreibt neue ≥x-Links-Zeilen hinein.
    """
    page = pywikibot.Page(site, page_title)
    lines = page.text.splitlines()

    new_lines = []
    in_block = False

    for i, line in enumerate(lines):
        if line.strip().startswith(f"; {block_title}:"):
            in_block = True
            new_lines.append(line)  # Titelzeile bleibt erhalten
            # Neue Auswertung einfügen
            new_lines.append(
                "Die am häufigsten verlinkten Minerale (siehe auch [https://missingtopics.toolforge.org/?language=de&project=wikipedia&article=&category=Mineralogie&depth=5&wikimode=0&notemplatelinks=1&nosingles=1&limitnum=1&doit=Run Missingtopics in der Kategorie:Mineralogie] einschließlich Unterkategorien) sind:"
            )
            new_lines.append("")
            for t in sorted(grouped.keys(), reverse=True):
                minerals = " – ".join(f"[[{m}]]" for m in grouped[t])
                new_lines.append(f"* ≥ {t} Links: {minerals}")
            continue

        if in_block:
            # Block-Ende: nächste nicht-eingerückte Zeile oder neue Definition (; ...)
            if not (line.startswith(" ") or line.strip().startswith("* ≥") or line.startswith("Die am häufigsten") or line == ""):
                in_block = False
                new_lines.append(line)
            else:
                # alte "≥"-Zeilen werden übersprungen
                continue
        else:
            new_lines.append(line)

    new_text = "\n".join(new_lines)

    if new_text != page.text:
        page.text = new_text
        page.save(summary=f"Aktualisiere '{block_title}' mit fehlenden Mineralartikeln")
    else:
        print("Keine Änderungen erforderlich.")


def main():
    start_time = time.time()

    site = pywikibot.Site("de", "wikipedia")
    minerals = extract_all_minerals(site, "Liste der Minerale")
    total = len(minerals)
    print(f"{total} Minerale gesammelt.")

#    missing = [("test30", 35), ("test15", 15)]
        
    missing = []
    for i, mineral in enumerate(minerals, start=1):
        page = pywikibot.Page(site, mineral)
        if not page.exists():
            count = count_article_links(site, mineral)
            if count > 0:
                missing.append((mineral, count))
                print(f"[{i}/{total}] {mineral}: {count} Links im Artikelnamensraum")
        else:
            print(f"[{i}/{total}] {mineral} existiert bereits")

    grouped = group_by_thresholds(missing)

    update_list_block(
        site,
        "Wikipedia:WikiProjekt Minerale/Artikelwünsche",
#        "Benutzer:Rjh/Test",
        "Minerale und Mineralgruppen",
        grouped,
    )

    print("\nLaufzeit: ", human_readable_time_difference(start_time, time.time()))


if __name__ == "__main__":
    main()
