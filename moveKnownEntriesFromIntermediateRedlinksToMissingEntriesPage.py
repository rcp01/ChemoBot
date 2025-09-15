import pywikibot
import re
import difflib
import time
from helperfunctions import human_readable_time_difference

def load_short_list(site):
    """
    Analysiert den Abschnitt "Rotlinks" einer Wikipedia-Seite und filtert Zeilen basierend auf bestimmten Kriterien.

    Args:
        page_title (str): Der Titel der Seite, die analysiert werden soll.
        section_title (str): Der Titel des Abschnitts, der analysiert werden soll.
        site (pywikibot.Site): Die Pywikibot-Site-Instanz.
    """    

    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Mapping"
    # page_title = "Benutzer:ChemoBot/Tests/Mapping"
    
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

def check_if_redlink_exists(site, target_title):
    target_page = pywikibot.Page(site, target_title)

    # check if page exists
    if target_page.exists():
        print(f"Die Seite '{target_title}' existiert bereits.")
        return False
    else:
        # Wenn nicht: nach Links auf diese Seite im Artikelnamensraum suchen
        backlinks = target_page.backlinks(namespaces=[0], filter_redirects=False)
        backlinks_list = list(backlinks)

        if backlinks_list:
            print(f"Die Seite '{target_title}' existiert nicht, wird aber auf folgenden Seiten verlinkt:")
            for page in backlinks_list:
                print(f"- {page.title()}")
            return True
        else:
            print(f"Die Seite '{target_title}' existiert nicht und wird im Artikelnamensraum nicht verlinkt.")
            return False

def analyze_intermediate_redlinks_section(site, section_title, abb_list):
    """
    Analysiert den Abschnitt "Rotlinks" einer Wikipedia-Seite und filtert Zeilen basierend auf bestimmten Kriterien.

    Args:
        page_title (str): Der Titel der Seite, die analysiert werden soll.
        section_title (str): Der Titel des Abschnitts, der analysiert werden soll.
        site (pywikibot.Site): Die Pywikibot-Site-Instanz.
    """
    redlink_list = []
    exclude_site_name_list = []
        
    intermediate_list_page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Neuzugänge/Zwischenlager"
    # intermediate_list_page_title = "Benutzer:ChemoBot/Tests/Neuzugänge/Zwischenlager"

    try:
        # Lade die Seite
        page = pywikibot.Page(site, intermediate_list_page_title)
        # Ursprünglichen Seiteninhalt laden
        text = page.text

        # Finde den Abschnitt anhand des Titels
        section_pattern = rf'(==+\s*{re.escape(section_title)}\s*==+)(.*?)(?=\n==|\Z)'
        match = re.search(section_pattern, text, re.DOTALL)

        if not match:
            print(f"Abschnitt mit Titel '{section_title}' nicht gefunden.")
        else:
            # Abschnitt und Inhalt extrahieren
            section_header, section_content = match.groups()
            # print(section_header)
            # print(section_content)

            # Zeilen filtern, die mit "* " anfangen und die Kriterien erfüllen
            filtered_lines = []
            for line in section_content.strip().split("\n"):
                # Regulärer Ausdruck
                # * [[1,2-Cyclohexylendiacetat]] >> [[Blei(IV)-acetat]] >>1759-71-3,Q72459700  >>cyc
                pattern = r"^\* (.*?) >>(.*?)>>(.*?)>>(.*)$"

                # Suche nach Übereinstimmungen
                match = re.match(pattern, line)

                if match:
                    name = match.group(1).strip()  # Text nach "* " und vor dem ersten ">>"
                    site_name = match.group(2).strip() # Text zwischen erstem und dem zweiten ">>"
                    cas_wd = match.group(3).strip()  # Text zwischen dem zweiten und dem dritten ">>"
                    section_short_name = match.group(4).strip()  # Text nach dem letzten ">>"
                    
                    if (section_short_name != ""):
                        if not (section_short_name == "off" or section_short_name == "irr" or section_short_name == "ir2" or section_short_name == "zzz" or section_short_name == "zzt"):
                            # print("Name:", name, " cas_wd:", cas_wd, " Abkürzung:", section_short_name)
                            if ((section_short_name in abb_list) and (cas_wd != "")):
                                redlink_list.append([section_short_name, format_missing_page_string(name, cas_wd)])
                            else:
                                print(f"Abkürzung für \"{section_short_name}\" existiert nicht oder Inhalt leer -> Zeile wird ignoriert.")
                                filtered_lines.append(line)
                        elif (section_short_name == "ir2"):
                            exclude_site_name_list.append(site_name + " - ")
                        elif (section_short_name == "zzz" or section_short_name == "zzt"):
                            # same as before, therefore ignore line
                            if check_if_redlink_exists(site, name.replace("[[", "").replace("]]", "")):
                                filtered_lines.append(line)
                            else:
                                print(f"Rotlink auf {name} existiert nicht mehr -> wird aus Liste entfernt.")
                        else:
                            redlink_list.append([section_short_name, name + " - "])
                    else:
                        if check_if_redlink_exists(site, name.replace("[[", "").replace("]]", "")):
                            filtered_lines.append(line)
                        else:
                            print(f"Rotlink auf {name} existiert nicht mehr -> wird aus Liste entfernt.")
                else:
                    filtered_lines.append(line)
            page.text = text.replace(section_content, "\n" + "\n".join(filtered_lines))
            if (text != page.text):
                page.save(summary=f"Lösche verschobene Einträge aus der Liste.")

    except Exception as e:
        print(f"Fehler beim Analysieren der Seite: {e}")
        
    # print(redlink_list)
    return {"redlink_list":redlink_list, "exclude_site_name_list":exclude_site_name_list}
         

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

    #if ("Tripropylzinn-Verbindungen" in text):
    #    print("wiki_links=", wiki_links)

    # Prüfen, ob der neue Eintrag schon existiert
    if new_entry.startswith("[[") and new_entry.strip() not in wiki_links:
        wiki_links.append(new_entry)
        wiki_links = sorted(wiki_links, key=str.casefold)

        # Zusammenfügen des Abschnitts
        updated_section_content = "\n".join(other_lines + wiki_links)
        updated_section_content = re.sub(r'\n\n', '\n', updated_section_content)

        # Aktualisieren des Textes
        updated_text = text[:match.start(2)] + updated_section_content + text[match.end(2):]
        return updated_text
    else:
        return text

def save_missing_articles_page(page, updated_text, text):
    # Änderungen speichern
    if updated_text != text:
        page.text = updated_text
        print(f"Einträge wurden erfolgreich auf {page.title()} hinzugefügt und sortiert.")
        page.save(f"Einträge aus Neuzugänge hinzugefügt.")
    else:
        print(f"Keine Änderungen an fehlenden Artikel Seite {page.title()} vorgenommen.")

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

        # print("new_entry = " ,new_entry, " ,Exclusionlist = ", exclusion_list, "\n\n")

        # Neuen Eintrag alphabetisch einfügen
        if new_entry in exclusion_list or new_entry.strip() in exclusion_list :
            # print(f"Der Eintrag '{new_entry}' ist bereits in der Ausschlussliste.")
            return text
        else:
            # print(f"Der Eintrag '{new_entry}' ist noch nicht in der Ausschlussliste {exclusion_list}.")            

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


def add_entry_to_intermediate_list(text, section_title, new_entry):
    """
    Fügt einen neuen Eintrag alphabetisch sortiert in den Abschnitt "Rotlinks" ein.

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
        exclusion_list = [line for line in lines if line.startswith("* ")]

        # print("new_entry = " ,new_entry, " ,Exclusionlist = ", exclusion_list, "\n\n")

        # Neuen Eintrag alphabetisch einfügen
        if new_entry in exclusion_list or new_entry.strip() in exclusion_list :
            # print(f"Der Eintrag '{new_entry}' ist bereits in der Ausschlussliste.")
            return text
        else:
            # print(f"Der Eintrag '{new_entry}' ist noch nicht in der Ausschlussliste {exclusion_list}.")            

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
            print(f"Keine Änderungen an Ausschlusslistenseite {page.title()} vorgenommen.")

    except Exception as e:
        print(f"Fehler beim Bearbeiten der Seite: {e}")


if __name__ == "__main__":
    start_time = time.time()
    # Pywikibot-Site initialisieren
    site = pywikibot.Site('de', 'wikipedia')
    
    print("Load abbreviation for sections list ...")

    abb_list = load_short_list(site)

    print("Load missing pages ...")

    # Seitentitel fehlende Substanzen 
    missing_pages_page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen"
    # missing_pages_page_title = "Benutzer:ChemoBot/Tests/Fehlende Substanzen"

    # Lade den aktuellen Inhalt der fehlende Substanz Seite
    missing_pages_page = pywikibot.Page(site, missing_pages_page_title)
    if not missing_pages_page.exists():
       print(f"Die Seite {missing_pages_page_title} existiert nicht.")
       exit(0)

    updated_missing_pages_text = missing_pages_page.text

    print("Load ignore links list pages ...")

    # Seitentitel Ausschlussliste
    ignore_list_page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Ausschlussliste"
    #ignore_list_page_title = "Benutzer:ChemoBot/Tests/Ausschlussliste"

    ignore_list_page = pywikibot.Page(site, ignore_list_page_title)
    if not ignore_list_page.exists():
       print(f"Die Seite {ignore_list_page_title} existiert nicht.")
       exit(0)

    updated_ignore_list_text = ignore_list_page.text

    print("Load irrelevant links list pages ...")

    # Seitentitel Ausschlussliste für irrelevante Seiten wie Hydride
    irrelevant_list_page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Varianten"
    # irrelevant_list_page_title = "Benutzer:ChemoBot/Tests/Varianten"

    irrelevant_list_page = pywikibot.Page(site, irrelevant_list_page_title)
    if not irrelevant_list_page.exists():
       print(f"Die Seite {irrelevant_list_page_title} existiert nicht.")
       exit(0)

    updated_irrelevant_list_text = irrelevant_list_page.text

    print("Load exclusion site list pages ...")

    # Seitentitel Ausschlussliste für auszuschließende Seiten wie Linksammlungen
    exclusion_list_page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Gruppenausschluss"
    # exclusion_list_page_title = "Benutzer:ChemoBot/Tests/Gruppenausschluss"

    exclusion_list_page = pywikibot.Page(site, exclusion_list_page_title)
    if not exclusion_list_page.exists():
       print(f"Die Seite {exclusion_list_page_title} existiert nicht.")
       exit(0)

    updated_exclusion_list_text = exclusion_list_page.text

    print("Load redlinks ...")

    result_red = analyze_intermediate_redlinks_section(site, "Chemie", abb_list) 
    redlink_list = result_red["redlink_list"]

    print("Analyze redlinks ...")

    # Eintrag hinzufügen
    for redlink in redlink_list:
        new_entry = redlink[1]
        if not (redlink[0] == "off" or redlink[0] == "irr"):
            section_title = abb_list[redlink[0]]
            # print("\"" + new_entry + "\" " + section_title + "\n")
            updated_missing_pages_text = add_entry_to_section(updated_missing_pages_text, section_title, new_entry)
        else:
            if (redlink[0] == "off"):
                # print("\"" + new_entry + "\" " + redlink[0] + "\n")
                updated_ignore_list_text = add_entry_to_exclusion_list(updated_ignore_list_text, "Ausschlussliste", new_entry)
            else:
                # print("\"" + new_entry + "\" " + redlink[0] + "\n")
                updated_irrelevant_list_text = add_entry_to_exclusion_list(updated_irrelevant_list_text, "Ausschlussliste", new_entry)
    
    exclude_site_name_list = result_red["exclude_site_name_list"]
    # print("exclude_site_name_list=", exclude_site_name_list)
    for exclude_site_name in exclude_site_name_list:
        # print(f"exclude_site_name = {exclude_site_name}")
        updated_exclusion_list_text = add_entry_to_exclusion_list(updated_exclusion_list_text, "Ausschlussliste", exclude_site_name)
 
    # print("Show diff ...")
    # print(missing_pages_page.text == updated_missing_pages_text)

    # diff = difflib.unified_diff(missing_pages_page.text.splitlines(), updated_missing_pages_text.splitlines(), lineterm='')
    # print("\n".join(diff))
            
    # diff = difflib.unified_diff(ignore_list_page.text.splitlines(), updated_ignore_list_text.splitlines(), lineterm='')
    # print("\n".join(diff))

    # diff = difflib.unified_diff(irrelevant_list_page.text.splitlines(), updated_irrelevant_list_text.splitlines(), lineterm='')
    # print("\n".join(diff))

    save_missing_articles_page(missing_pages_page, updated_missing_pages_text, missing_pages_page.text)
    save_exclusion_list(updated_ignore_list_text, ignore_list_page.text, ignore_list_page)
    save_exclusion_list(updated_irrelevant_list_text, irrelevant_list_page.text, irrelevant_list_page)
    save_exclusion_list(updated_exclusion_list_text, exclusion_list_page.text, exclusion_list_page)
    
    print("\nLaufzeit: ", human_readable_time_difference(start_time, time.time()))
