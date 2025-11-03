import pywikibot
import re

def extract_links(text):
    """Extrahiert alle Artikelnamen aus [[…]]-Links."""
    return set(re.findall(r"\[\[([^\]|#]+)", text))

def normalize_titles(site, titles):
    """Normalisiert Seitentitel (z. B. Redirects/Kanonisierung) mithilfe von pywikibot.Page.title()."""
    normed = set()
    cache = {}
    for t in titles:
        t = t.strip()
        if not t:
            continue
        if t in cache:
            normed.add(cache[t])
        else:
            p = pywikibot.Page(site, t)
            norm = p.title()
            cache[t] = norm
            normed.add(norm)
    return normed

def normalize_title(site, title, cache):
    """Normalisiert einen einzelnen Titel mit Cache-Dict."""
    title = title.strip()
    if title in cache:
        return cache[title]
    p = pywikibot.Page(site, title)
    norm = p.title()
    cache[title] = norm
    return norm

def process_lines_preserve_headings(site, lines, substanzen_links, skip_headings):
    """
    Iteriert zeilenweise, erhält alle Überschriften (= beliebige Anzahl '='),
    schützt Abschnitte, deren Überschrift in skip_headings steht (case-insensitive, exakter Titelvergleich),
    und löscht in anderen Abschnitten Zeilen, die Artikel enthalten, die in substanzen_links sind.
    """
    # Regex: heading (z. B. "== Titel ==" oder "=== Untertitel ===")
    re_heading = re.compile(r'^(?P<equals>=+)\s*(?P<title>.+?)\s*(?P=equals)\s*$')
    # Regex: Vorlage Artikelwunsch-Wikidata, mit möglich führendem -, –, *
    re_vorlage = re.compile(r'^\s*[-–*]?\s*\{\{\s*Artikelwunsch-Wikidata\s*\|\s*([^|}]+)\s*\|[^}]*\}\}', flags=re.IGNORECASE)
    # Regex für erste link-präfix (nicht mehr ausschließlich verwendet, wir sammeln alle Links in der Zeile)
    re_any_link = re.compile(r'\[\[([^\]|#]+)')

    new_lines = []
    removed = []
    protected_level = None   # None oder int (Level der geschützten Überschrift)
    title_norm_cache = {}    # Cache für normalize_title

    for line in lines:
        # Erkennen einer Überschrift
        m_head = re_heading.match(line)
        if m_head:
            level = len(m_head.group('equals'))  # z.B. "==" -> 2
            title = m_head.group('title').strip()

            # Wenn wir uns in einem geschützten Abschnitt befinden und diese Überschrift
            # gleich oder höher (kleiner/equal level) ist, endet der geschützte Abschnitt
            if protected_level is not None and level <= protected_level:
                protected_level = None

            # Überschrift immer erhalten (damit Struktur bleibt)
            new_lines.append(line)

            # Prüfen, ob diese Überschrift in der Skip-Liste steht -> dann schützen wir den Abschnitt
            # Vergleich: case-insensitive und exakter Titel (ohne '=')
            for skip in skip_headings:
                if skip.strip().lower() == title.lower():
                    protected_level = level
                    break

            # weiter zur nächsten Zeile
            continue

        # Wenn wir uns aktuell in einem geschützten Abschnitt befinden -> Zeile unverändert übernehmen
        if protected_level is not None:
            new_lines.append(line)
            continue

        # Nicht-Überschrift und nicht geschützt: prüfen, ob die Zeile Artikel-Links enthält, die entfernt werden sollen.

        # 1) Prüfen auf Vorlage {{Artikelwunsch-Wikidata|Titel|...}}
        m_vor = re_vorlage.match(line)
        remove_line = False
        if m_vor:
            artikel_raw = m_vor.group(1).strip()
            artikel_norm = normalize_title(site, artikel_raw, title_norm_cache)
            # print(line)
            if artikel_norm in substanzen_links:
                removed.append(artikel_norm)
                remove_line = True
        else:
            # 2) Alle [[...]]-Links in der Zeile extrahieren und prüfen (wenn einer davon in substanzen_links ist => Zeile löschen)
            links = re_any_link.findall(line)
            # print(line)
            for link_raw in links:
                artikel_norm = normalize_title(site, link_raw, title_norm_cache)
                if artikel_norm in substanzen_links:
                    removed.append(artikel_norm)
                    remove_line = True
                    break

        if remove_line:
            # Zeile wird nicht übernommen (also gelöscht)
            continue
        else:
            new_lines.append(line)

    return new_lines, removed


def main():
    site = pywikibot.Site("de", "wikipedia")

    # Seiten laden
    page_substanzen = pywikibot.Page(site, "Wikipedia:Redaktion Chemie/Fehlende Substanzen")
    page_artikel = pywikibot.Page(site, "Wikipedia:Redaktion Chemie/Fehlende Artikel")
#    page_artikel = pywikibot.Page(site, "Benutzer:Rjh/Test")

    text_substanzen = page_substanzen.text
    text_artikel = page_artikel.text
    original_artikel = text_artikel

    # Alle Links aus der Substanzen-Seite sammeln und normalisieren
    substanzen_links_raw = extract_links(text_substanzen)
    substanzen_links = normalize_titles(site, substanzen_links_raw)
    print(f"{len(substanzen_links)} Substanzen-Artikel gefunden (normalisiert).")

    # Überschriften, die nicht verändert werden sollen (exakter Titelvergleich, case-insensitive)
    skip_headings = [
        "Top-Vorschläge zum Erstellen neuer Artikel",
        "Vorschläge mit hoher Priorität",
        "Am häufigsten verlinkte fehlende Artikel",
        "Lebensmittelzusatzstoffe ([[Liste der Lebensmittelzusatzstoffe|Liste]])",
        "Pflanzenschutzmittel",
        "Chemische Verbindungen, Reagenzien, Reste und funktionelle Gruppen mit geläufigen Abkürzungen ([[Liste der Abkürzungen in der organischen Chemie|Liste]])",
        "Benzodiazepine ([[Benzodiazepine|Liste]])",
        "Zulassungspflichtige Stoffe ([[Verzeichnis der zulassungspflichtigen Stoffe nach Anhang XIV der REACH-Verordnung|Liste]])",
        "Besonders besorgniserregenden Stoffe ([[Liste der besonders besorgniserregenden Stoffe|Liste]])",
        "CoRAP-Stoffe ([[Liste der CoRAP-Stoffe|Liste]])",
        "Chemikalienliste der Redaktion Chemie ([[Wikipedia:Redaktion Chemie/Chemikalienliste|Liste]])",
        "Aus dem Nekrolog"
        # Weitere Überschriften hier hinzufügen
    ]

    lines = text_artikel.splitlines()
    new_lines, removed = process_lines_preserve_headings(site, lines, substanzen_links, skip_headings)

    # Zusammenfügen und Leerzeilen aufräumen (mehr als 2 → 2)
    new_text = "\n".join(new_lines)
    new_text = re.sub(r"\n{3,}", "\n\n", new_text).strip() + "\n"

    # Seite speichern, falls geändert
    if new_text != original_artikel:
        print(f"{len(removed)} Artikel entfernt: {removed[:20]}{'...' if len(removed) > 20 else ''}")
        page_artikel.text = new_text
        page_artikel.save(
            summary=f"Entferne {len(removed)} Artikel, die bereits in 'Fehlende Substanzen' gelistet sind (außer geschützte Abschnitte)"
        )
    else:
        print("Keine Änderungen erforderlich.")


if __name__ == "__main__":
    main()
