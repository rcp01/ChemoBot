import pywikibot
import re
import difflib

def load_short_list(site):
    """
    Analysiert den Abschnitt "Rotlinks" einer Wikipedia-Seite und filtert Zeilen basierend auf bestimmten Kriterien.

    Args:
        page_title (str): Der Titel der Seite, die analysiert werden soll.
        section_title (str): Der Titel des Abschnitts, der analysiert werden soll.
        site (pywikibot.Site): Die Pywikibot-Site-Instanz.
    """
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Mapping"
        
    # Lade die Seite
    page = pywikibot.Page(site, page_title)
    abb_list = {}

    try:
        # Ursprünglichen Seiteninhalt laden
        text = page.text

        # Zeilen filtern, die mit "* " anfangen und die Kriterien erfüllen
        filtered_lines = []
        for line in text.strip().split("\n"):
            # Regulärer Ausdruck
            # Beispiel: * arz->[[Wikipedia:Redaktion Chemie/Fehlende Substanzen#Arzneistoffe]]
            pattern = r"^\* (.*?)->\[\[Wikipedia:Redaktion Chemie/Fehlende Substanzen#(.*?)\]\]$"

            # Suche nach Übereinstimmungen
            match = re.match(pattern, line.strip())

            if match:
                short_name = match.group(1).strip()  # Text nach "* " und vor dem ersten ">>"
                section_name = match.group(2).strip()  # Text nach dem letzten ">>"
                abb_list[short_name] = section_name;
                
                # print("shortname:", short_name, " Überschrift:", section_name)
            
        # print(abb_list)
        
    except Exception as e:
        print(f"Fehler beim Analysieren der Seite: {e}")
    
    return abb_list

def format_missing_page_string(name, cas_wd):
    """
    Formatiert den String ins Ausgabeformat

    Args:
        page_title (str): Der Titel der Seite, die analysiert werden soll.
        section_title (str): Der Titel des Abschnitts, der analysiert werden soll.
        site (pywikibot.Site): Die Pywikibot-Site-Instanz.
    """
    
    # Beispiel: [[1,4-Heptonolacton]] (89-67-8, [[:d:Q27282913|wd]]) -
    cas_wd = re.sub(r",Q(\d+)", r", [[:d:Q\1|wd]]", cas_wd)
    cas_wd = re.sub(r"^Q(\d+)", r"[[:d:Q\1|wd]]", cas_wd)
    
    return name + " (" + cas_wd + ") -"

def analyze_redlinks_section(site, section_title):
    """
    Analysiert den Abschnitt "Rotlinks" einer Wikipedia-Seite und filtert Zeilen basierend auf bestimmten Kriterien.

    Args:
        page_title (str): Der Titel der Seite, die analysiert werden soll.
        section_title (str): Der Titel des Abschnitts, der analysiert werden soll.
        site (pywikibot.Site): Die Pywikibot-Site-Instanz.
    """
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Neuzugänge"
        
    # Lade die Seite
    page = pywikibot.Page(site, page_title)
    
    redlink_list = []

    try:
        # Ursprünglichen Seiteninhalt laden
        text = page.text

        # Finde den Abschnitt anhand des Titels
        section_pattern = rf'(==+\s*{re.escape(section_title)}\s*==+)(.*?)(?=\n==|\Z)'
        match = re.search(section_pattern, text, re.DOTALL)

        if not match:
            print(f"Abschnitt mit Titel '{section_title}' nicht gefunden.")
            return

        # Abschnitt und Inhalt extrahieren
        section_header, section_content = match.groups()
        # print(section_header)
        # print(section_content)


        # Zeilen filtern, die mit "* " anfangen und die Kriterien erfüllen
        filtered_lines = []
        for line in section_content.strip().split("\n"):
            # Regulärer Ausdruck
            # * [[1,2-Cyclohexylendiacetat]] >> [[Blei(IV)-acetat]] >>1759-71-3,Q72459700  >>cyc
            pattern = r"^\* (.*?) >>.*?>>(.*?)>>(.*)$"

            # Suche nach Übereinstimmungen
            match = re.match(pattern, line)

            if match:
                name = match.group(1).strip()  # Text nach "* " und vor dem ersten ">>"
                cas_wd = match.group(2).strip()  # Text zwischen dem zweiten und dem dritten ">>"
                section_short_name = match.group(3).strip()  # Text nach dem letzten ">>"
                
                if (not section_short_name == ""):
                    if (not section_short_name == "off" and not section_short_name == "irr"):
                        # print("Name:", name, " cas_wd:", cas_wd, " Abkürzung:", section_short_name)
                        redlink_list.append([section_short_name, format_missing_page_string(name, cas_wd)])
                    else:
                        redlink_list.append([section_short_name, name + " - "])
        
        print(redlink_list)
        return redlink_list
         
    except Exception as e:
        print(f"Fehler beim Analysieren der Seite: {e}")

def add_entry_to_section(text, section_title, new_entry):
    # print(text)

    # Abschnitt finden
    section_pattern = rf'(==+\s*{re.escape(section_title)}\s*==+)(.*?)(?=\n==|\Z)'
    match = re.search(section_pattern, text, re.DOTALL)
    
    if not match:
        print(f"Der Abschnitt '{section_title}' wurde auf der Seite nicht gefunden.")
        return

    header, section_content = match.groups()

    # Aufteilen der Zeilen des Abschnitts
    lines = section_content.split("\n")

    # Trennen von Einträgen, die mit [[ beginnen
    wiki_links = sorted([line if line.strip().endswith(" -") or line.strip().endswith(" –") or line.strip().endswith(" –") else line.strip() + " -" for line in lines if line.startswith("[[") or line.startswith("* [[") or line.startswith("- [[")], key=str.casefold)
    other_lines = [line for line in lines if not (line.startswith("[[") or line.startswith("* [[") or line.startswith("- [["))]

    # Prüfen, ob der neue Eintrag schon existiert
    if new_entry.startswith("[[") and new_entry not in wiki_links:
        wiki_links.append(new_entry)
        wiki_links = sorted(wiki_links, key=str.casefold)

    # Zusammenfügen des Abschnitts
    updated_section_content = "\n".join(other_lines + wiki_links)
    updated_section_content = re.sub(r'\n\n', '\n', updated_section_content)

    # Aktualisieren des Textes
    updated_text = text[:match.start(2)] + updated_section_content + text[match.end(2):]
    return updated_text

def save_missing_articels_page(page, updated_text, text):
    # Änderungen speichern
    if updated_text != text:
        page.text = updated_text
        print(f"Eintrag 'Einträge wurden erfolgreich hinzugefügt und sortiert.")
        page.save(f"Einträge aus Neuzugänge hinzugefügt.")
    else:
        print("Keine Änderungen an fehlenden Artikel Seite vorgenommen.")

def add_entry_to_exclusion_list(text, section_title, new_entry):
    """
    Fügt einen neuen Eintrag alphabetisch sortiert in den Abschnitt "Ausschlussliste" ein.

    Args:
        section_title (str): Der Titel des Abschnitts, in den der Eintrag eingefügt werden soll.
        new_entry (str): Der neue Eintrag, der hinzugefügt werden soll.
    """

    try:
        # Finde den Abschnitt anhand des Titels
        section_pattern = rf'(==+\s*{re.escape(section_title)}\s*==+)(.*?)(?=\n==|\Z)'
        match = re.search(section_pattern, text, re.DOTALL)

        if not match:
            print(f"Abschnitt mit Titel '{section_title}' nicht gefunden.")
            return text

        # Abschnitt und Inhalt extrahieren
        section_header, section_content = match.groups()

        # Zeilen in der Ausschlussliste filtern
        lines = section_content.split("\n")
        exclusion_list = [line for line in lines if line.startswith("[[")]

        # Neuen Eintrag alphabetisch einfügen
        if new_entry in exclusion_list:
            print(f"Der Eintrag '{new_entry}' ist bereits in der Ausschlussliste.")
            return text

        exclusion_list.append(f"{new_entry}")
        exclusion_list = sorted(exclusion_list, key=lambda x: x.lower())

        # Aktualisierter Abschnittstext
        updated_section_content = "\n".join(exclusion_list)

        # Aktualisierten Abschnitt im Seiteninhalt ersetzen
        updated_text = re.sub(
            section_pattern,
            rf'\1\n{updated_section_content}\n',
            text,
            flags=re.DOTALL
        )
        
        return updated_text
        
    except Exception as e:
        print(f"Fehler beim Bearbeiten der Seite: {e}")
        return text

def save_exclusion_list(updated_text, text, page):
    """
    Fügt einen neuen Eintrag alphabetisch sortiert in den Abschnitt "Ausschlussliste" ein.

    Args:
        page (): Die Seite, die bearbeitet werden soll.
        updated_text (str): Der geänderte Text.
        text (str): Der originale Text.
    """
    try:
        # Änderungen speichern
        if updated_text != text:
            page.text = updated_text
            page.save(summary=f"Einträge aus Neuzugangsliste in der Ausschlussliste hinzugefügt.")
            print(f"Einträge erfolgreich hinzugefügt.")
        else:
            print("Keine Änderungen an Ausschlusslistenseite vorgenommen.")

    except Exception as e:
        print(f"Fehler beim Bearbeiten der Seite: {e}")


def save_irrelevant_list(updated_text, text, page):
    """
    Fügt einen neuen Eintrag alphabetisch sortiert in den Abschnitt "Ausschlussliste" ein.

    Args:
        page (): Die Seite, die bearbeitet werden soll.
        updated_text (str): Der geänderte Text.
        text (str): Der originale Text.
    """
    try:
        # Änderungen speichern
        if updated_text != text:
            page.text = updated_text
            page.save(summary=f"Einträge aus Neuzugangsliste in der Ausschlussliste hinzugefügt.")
            print(f"Einträge erfolgreich hinzugefügt.")
        else:
            print("Keine Änderungen an Ausschlusslistenseite vorgenommen.")

    except Exception as e:
        print(f"Fehler beim Bearbeiten der Seite: {e}")

def count_backlinks(site, page_title):
    page = pywikibot.Page(site, page_title)
    
    backlinks = list(page.backlinks(namespaces=[0]))  # Nur Artikel (Namensraum 0) zählen
    print(f"Die Seite '{page_title}' hat {len(backlinks)} eingehende Links aus Artikeln.")

    return len(backlinks)

def has_german_wikipedia_link(site, wikidata_id):
    repo = site.data_repository()  # Daten-Repository für Wikidata
    item = pywikibot.ItemPage(repo, wikidata_id)  # Wikidata-Item laden
    
    try:
        item.get()  # Daten abrufen
        if 'dewiki' in item.sitelinks:
            print(f"{wikidata_id} hat einen Link zu: {item.sitelinks['dewiki'].title}")
            return True
        else:
            print(f"{wikidata_id} hat KEINEN Link zu einer deutschen Wikipedia-Seite.")
            return False
    except Exception as e:
        print(f"Fehler beim Abrufen von {wikidata_id}: {e}")
        return None

def count_wikipedia_languages(site, wikidata_id):
    repo = site.data_repository()  # Daten-Repository für Wikidata
    item = pywikibot.ItemPage(repo, wikidata_id)  # Wikidata-Item laden

    try:
        item.get()  # Daten abrufen
        # Filtere nur Wikipedia-Sprachlinks (die Endung '.wikipedia.org' haben)

        language_count = len(item.sitelinks)  # Anzahl der Sprachlinks zählen
        print(f"{wikidata_id} hat {language_count} Links zu Wikipedia-Artikeln.")
 
        wikipedia_links = [site for site in item.sitelinks if (site.endswith('wiki') and not site == "commonswiki" )]
        language_count = len(wikipedia_links)  # Anzahl der Wikipedia-Sprachlinks

        print(f"{wikidata_id} hat Wikipedia-Artikel in {language_count} Sprachen.")
        return language_count
    except Exception as e:
        print(f"Fehler beim Abrufen von {wikidata_id}: {e}")
        return None


if __name__ == "__main__":
    # Pywikibot-Site initialisieren
    site = pywikibot.Site('de', 'wikipedia')
    # wikidata_site = pywikibot.Site('wikidata', 'wikidata')  # Wikidata-Site

    # count_backlinks(site, "Wasser")
    # has_german_wikipedia_link(wikidata_site, "Q283")
    # count_wikipedia_languages(wikidata_site, "Q283")
    
    # exit(0)
    
    print("Load shortlist ...")

    abb_list = load_short_list(site)


    print("Load missing pages ...")

    # Seitentitel fehlende Substanzen 
    missing_pages_page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen"
    # missing_pages_page_title = "Benutzer:Rjh/Test"

    # Lade den aktuellen Inhalt der fehlnde Substanz Seite
    missing_pages_page = pywikibot.Page(site, missing_pages_page_title)
    if not missing_pages_page.exists():
       print(f"Die Seite {missing_pages_page_title} existiert nicht.")
       exit(0)

    updated_missing_pages_text = missing_pages_page.text

    print("Load ignore list pages ...")

    # Seitentitel Ausschlussliste
    ignore_list_page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Ausschlussliste"
    # ignore_list_page_title = "Benutzer:Rjh/Test3"

    ignore_list_page = pywikibot.Page(site, ignore_list_page_title)
    if not ignore_list_page.exists():
       print(f"Die Seite {ignore_list_page_title} existiert nicht.")
       exit(0)

    updated_ignore_list_text = ignore_list_page.text

    print("Load irrelevant list pages ...")

    # Seitentitel Ausschlussliste für irrelevante Seiten wie Hydride
    irrelevant_list_page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Varianten"
    # irrelevant_list_page_title = "Benutzer:Rjh/Test3"

    irrelevant_list_page = pywikibot.Page(site, irrelevant_list_page_title)
    if not irrelevant_list_page.exists():
       print(f"Die Seite {irrelevant_list_page_title} existiert nicht.")
       exit(0)

    updated_irrelevant_list_text = irrelevant_list_page.text

    print("Load redlinks ...")

    redlink_list = analyze_redlinks_section(site, "Rotlinks") + analyze_redlinks_section(site, "Aktuell")

    print("Analyze redlinks ...")

    # Eintrag hinzufügen
    for redlink in redlink_list:
        new_entry = redlink[1]
        if not (redlink[0] == "off" or redlink[0] == "irr"):
            section_title = abb_list[redlink[0]]
            print("\"" + new_entry + "\" " + section_title + "\n")
            updated_missing_pages_text = add_entry_to_section(updated_missing_pages_text, section_title, new_entry)
        else:
            if (redlink[0] == "off"):
                print("\"" + new_entry + "\" " + redlink[0] + "\n")
                updated_ignore_list_text = add_entry_to_exclusion_list(updated_ignore_list_text, "Ausschlussliste", new_entry)
            else:
                print("\"" + new_entry + "\" " + redlink[0] + "\n")
                updated_irrelevant_list_text = add_entry_to_exclusion_list(updated_irrelevant_list_text, "Ausschlussliste", new_entry)
    
    # print("Show diff ...")
    # print(missing_pages_page.text == updated_missing_pages_text)

    # diff = difflib.unified_diff(missing_pages_page.text.splitlines(), updated_missing_pages_text.splitlines(), lineterm='')
    # print("\n".join(diff))
            
    # diff = difflib.unified_diff(ignore_list_page.text.splitlines(), updated_ignore_list_text.splitlines(), lineterm='')
    # print("\n".join(diff))

    # diff = difflib.unified_diff(irrelevant_list_page.text.splitlines(), updated_irrelevant_list_text.splitlines(), lineterm='')
    # print("\n".join(diff))

    save_missing_articels_page(missing_pages_page, updated_missing_pages_text, missing_pages_page.text)
    save_exclusion_list(updated_ignore_list_text, ignore_list_page.text, ignore_list_page)
    save_irrelevant_list(updated_irrelevant_list_text, irrelevant_list_page.text, irrelevant_list_page)
    