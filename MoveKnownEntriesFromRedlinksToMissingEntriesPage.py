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
            pattern = r"^\* (.*?)->\[\[(.*?)#(.*?)\]\]$"

            # Suche nach Übereinstimmungen
            match = re.match(pattern, line.strip())

            if match:
                short_name   = match.group(1).strip()  # Text nach "* " und vor dem ersten ">>"
                page_name    = match.group(2).strip()  # Text nach "* " und vor dem ersten ">>"
                section_name = match.group(3).strip()  # Text nach dem letzten ">>"
                abb_list[short_name] = {
                    "page": page_name,
                    "section": section_name
                }
                
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

def analyze_redlinks_section(site, section_title, abb_list):
    """
    Analysiert den Abschnitt "Rotlinks" einer Wikipedia-Seite und filtert Zeilen basierend auf bestimmten Kriterien.

    Args:
        page_title (str): Der Titel der Seite, die analysiert werden soll.
        section_title (str): Der Titel des Abschnitts, der analysiert werden soll.
        site (pywikibot.Site): Die Pywikibot-Site-Instanz.
    """
    redlink_list = []
    irrelevant_site_name_list = []
    intermediate_list = []
    intermediate_taxa_list = []
    intermediate_others_list = []
        
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Neuzugänge"
    #page_title = "Benutzer:ChemoBot/Tests/Neuzugänge"

    try:
        # Lade die Seite
        page = pywikibot.Page(site, page_title)
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
                        if section_short_name not in {"off", "offp", "irr", "ir2", "zzz", "zzt", "zzs"}:
                            # print("Name:", name, " cas_wd:", cas_wd, " Abkürzung:", section_short_name)
                            if ((section_short_name in abb_list) and (cas_wd != "")):
                                redlink_list.append([section_short_name, format_missing_page_string(name, cas_wd)])
                            else:
                                print(f"Abkürzung für \"{section_short_name}\" existiert nicht oder Inhalt leer -> Zeile wird ignoriert.")
                                filtered_lines.append(line)
                        elif (section_short_name == "ir2"):
                            irrelevant_site_name_list.append(site_name + " - ")
                        elif (section_short_name == "zzz"):
                            intermediate_list.append(line)
                        elif (section_short_name == "zzt"):
                            intermediate_taxa_list.append(line)
                        elif (section_short_name == "zzs"):
                            intermediate_others_list.append(line)
                        else:
                            redlink_list.append([section_short_name, name + " - "])
                    else:
                        filtered_lines.append(line)
                else:
                    filtered_lines.append(line)
            page.text = text.replace(section_content, "\n" + "\n".join(filtered_lines))
            if (text != page.text):
                page.save(summary=f"Lösche verschobene Einträge aus der Liste.")

    except Exception as e:
        print(f"Fehler beim Analysieren der Seite: {e}")
        
    # print(redlink_list)
    return {"redlink_list":redlink_list, "irrelevant_site_name_list":irrelevant_site_name_list, "intermediate_list": intermediate_list, "intermediate_taxa_list": intermediate_taxa_list, "intermediate_others_list": intermediate_others_list}
         

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
    # Pywikibot-Site initialisieren
    site = pywikibot.Site('de', 'wikipedia')
    
    print("Load abbreviation for sections list ...")

    abb_list = load_short_list(site)

    print("Load missing pages ...")

    pages = {}
    updated_pages = {}

    # Load all pages from abb_list
    for abbrev, info in abb_list.items():
        page_title = info["page"]
        if page_title not in pages:
            page = pywikibot.Page(site, page_title)
            if not page.exists():
                print(f"The page {page_title} does not exist!")
                continue
            pages[page_title] = page
            updated_pages[page_title] = page.text

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

    print("Load intermediate links list pages ...")

    # Seitentitel Zwischenlagerliste für Seiten deren relevanz nicht bekannt ist (eventuell Namensfehler oder nicht existent)
    intermediate_list_page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Neuzugänge/Zwischenlager"
    # intermediate_list_page_title = "Benutzer:ChemoBot/Tests/Neuzugänge/Zwischenlager"

    intermediate_list_page = pywikibot.Page(site, intermediate_list_page_title)
    if not intermediate_list_page.exists():
       print(f"Die Seite {intermediate_list_page_title} existiert nicht.")
       exit(0)

    updated_intermediate_list_text = intermediate_list_page.text

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

    result_red = analyze_redlinks_section(site, "Rotlinks", abb_list) 
    result_act = analyze_redlinks_section(site, "Substanzinfo", abb_list)
    redlink_list = result_red["redlink_list"] + result_act["redlink_list"]
    intermediate_list = result_red["intermediate_list"] + result_act["intermediate_list"]
    intermediate_taxa_list = result_red["intermediate_taxa_list"]
    intermediate_others_list = result_red["intermediate_others_list"]

    print("Analyze redlinks ...")

    # Eintrag hinzufügen
    for redlink in redlink_list:
        new_entry = redlink[1]
        if redlink[0] not in {"off", "offp", "irr"}:
            section_title = abb_list[redlink[0]]["section"]
            # print("\"" + new_entry + "\" " + section_title + "\n")
            page_title = abb_list[redlink[0]]["page"]
            section_title = abb_list[redlink[0]]["section"]
            updated_pages[page_title] = add_entry_to_section(updated_pages[page_title], section_title, new_entry)
        else:
            if (redlink[0] == "off"):
                # print("\"" + new_entry + "\" " + redlink[0] + "\n")
                updated_ignore_list_text = add_entry_to_exclusion_list(updated_ignore_list_text, "Ausschlussliste", new_entry)
            elif (redlink[0] == "offp"):
                # print("\"" + new_entry + "\" " + redlink[0] + "\n")
                updated_ignore_list_text = add_entry_to_exclusion_list(updated_ignore_list_text, "Personen", new_entry)
            else:
                # print("\"" + new_entry + "\" " + redlink[0] + "\n")
                updated_irrelevant_list_text = add_entry_to_exclusion_list(updated_irrelevant_list_text, "Ausschlussliste", new_entry)
    
    irrelevant_site_name_list = result_red["irrelevant_site_name_list"] + result_act["irrelevant_site_name_list"]
    # print("irrelevant_site_name_list=", irrelevant_site_name_list)
    for irrelevant_site_name in irrelevant_site_name_list:
        # print(f"irrelevant_site_name = {irrelevant_site_name}")
        updated_exclusion_list_text = add_entry_to_exclusion_list(updated_exclusion_list_text, "Ausschlussliste", irrelevant_site_name)

    for intermediate_entry in intermediate_list:
        # print(f"intermediate_entry = {intermediate_entry}")
        updated_intermediate_list_text = add_entry_to_intermediate_list(updated_intermediate_list_text, "Chemie", intermediate_entry)

    for intermediate_entry in intermediate_taxa_list:
        # print(f"intermediate_entry = {intermediate_entry}")
        updated_intermediate_list_text = add_entry_to_intermediate_list(updated_intermediate_list_text, "Biologie", intermediate_entry)

    for intermediate_entry in intermediate_others_list:
        # print(f"intermediate_entry = {intermediate_entry}")
        updated_intermediate_list_text = add_entry_to_intermediate_list(updated_intermediate_list_text, "Sonstiges", intermediate_entry)
             
    # diff = difflib.unified_diff(ignore_list_page.text.splitlines(), updated_ignore_list_text.splitlines(), lineterm='')
    # print("\n".join(diff))

    # diff = difflib.unified_diff(irrelevant_list_page.text.splitlines(), updated_irrelevant_list_text.splitlines(), lineterm='')
    # print("\n".join(diff))

    for page_title, updated_text in updated_pages.items():
        original_text = pages[page_title].text
        if updated_text != original_text:
            pages[page_title].text = updated_text
            pages[page_title].save(summary="Einträge aus Neuzugänge hinzugefügt.")
            print(f"Einträge erfolgreich auf Seite {page_title} gespeichert.")
        else:
            print(f"Keine Änderungen an Seite {page_title} vorgenommen.")

    save_exclusion_list(updated_ignore_list_text, ignore_list_page.text, ignore_list_page)
    save_exclusion_list(updated_irrelevant_list_text, irrelevant_list_page.text, irrelevant_list_page)
    save_exclusion_list(updated_exclusion_list_text, exclusion_list_page.text, exclusion_list_page)
    save_exclusion_list(updated_intermediate_list_text, intermediate_list_page.text, intermediate_list_page)
    