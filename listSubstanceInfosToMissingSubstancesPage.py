import pywikibot
from pywikibot import pagegenerators
from collections import defaultdict
import re
import time
import traceback

pages_checked = 0
pages_changed = 0

def get_ignore_list(site):
    """
    Extrahiert die Liste fehlender Substanzen von der angegebenen Seite.

    Args:
        site (pywikibot.Site): Die Site-Instanz für Wikipedia.

    Returns:
        list: Eine Liste mit den Namen der fehlenden Substanzen.
    """
    
    substances = []

    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Ausschlussliste"
    print(f"Analysiere die Seite '{page_title}'...")
    page = pywikibot.Page(site, page_title)

    try:
        # Lade den Seiteninhalt
        content = page.text

        # Suche nach Listeneinträgen (Elemente in einer wikitext-Liste)
        # Annahme: Die Substanzen stehen in Zeilen, die mit einem "*" beginnen
        matches = re.findall(r'^\[\[(.*)\]\] ', content, re.MULTILINE)

        # Entferne mögliche Kommentare oder Formatierungen (z.B. Links)
        for match in matches:
            # Entferne [[ und ]] von Links und trimme Leerzeichen
            substances.append(match)
            # print(match)

    except Exception as e:
        traceback.print_exc()
        print(f"Fehler beim Abrufen oder Analysieren der Seite: {e}")

    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Varianten"
    print(f"Analysiere die Seite '{page_title}'...")
    page = pywikibot.Page(site, page_title)

    try:
        # Lade den Seiteninhalt
        content = page.text

        # Suche nach Listeneinträgen (Elemente in einer wikitext-Liste)
        # Annahme: Die Substanzen stehen in Zeilen, die mit einem "*" beginnen
        matches = re.findall(r'^\[\[(.*)\]\] ', content, re.MULTILINE)

        # Entferne mögliche Kommentare oder Formatierungen (z.B. Links)
        for match in matches:
            # Entferne [[ und ]] von Links und trimme Leerzeichen
            substances.append(match)
            # print(match)

    except Exception as e:
        traceback.print_exc()
        print(f"Fehler beim Abrufen oder Analysieren der Seite: {e}")

    return substances


def get_missing_substances_list(site):
    """
    Extrahiert die Liste fehlender Substanzen von der angegebenen Seite.

    Args:
        site (pywikibot.Site): Die Site-Instanz für Wikipedia.

    Returns:
        list: Eine Liste mit den Namen der fehlenden Substanzen.
    """
    
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen"
    print(f"Analysiere die Seite '{page_title}'...")
    page = pywikibot.Page(site, page_title)
    substances = []
    wikidata = []

    try:
        # Lade den Seiteninhalt
        content = page.text

        # Suche nach Listeneinträgen (Elemente in einer wikitext-Liste)
        # Annahme: Die Substanzen stehen in Zeilen, die mit einem "*" beginnen
        matches = re.findall(r'^\[\[(.*?)\]\] \(.*?(\[\[:d:.*?\|wd\]\])?\)', content, re.MULTILINE)

        # Entferne mögliche Kommentare oder Formatierungen (z.B. Links)
        for match in matches:
            substances.append(match[0])
            if match[1]:
                wikidata.append(match[1].replace("[[:d:", "").replace("|wd]]", ""))
            # print(match[0], " ", match[1].replace("[[:d:", "").replace("|wd]]", ""))

        return substances, wikidata
    except Exception as e:
        traceback.print_exc()
        print(f"Fehler beim Abrufen oder Analysieren der Seite: {e}")
        return [], []

def get_exclusion_list(site):
    """
    Extrahiert die Liste der zu ignorierenden Seite von der angegebenen Seite.

    Args:
        site (pywikibot.Site): Die Site-Instanz für Wikipedia.

    Returns:
        list: Eine Liste mit den Namen der fehlenden Substanzen.
    """
    
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Gruppenausschluss"
    substances = []
    print(f"Analysiere die Seite '{page_title}'...")
    page = pywikibot.Page(site, page_title)

    try:
        # Lade den Seiteninhalt
        content = page.text

        # Suche nach Listeneinträgen (Elemente in einer wikitext-Liste)
        # Annahme: Die Substanzen stehen in Zeilen, die mit einem "*" beginnen
        matches = re.findall(r'^\[\[(.*)\]\] ', content, re.MULTILINE)

        # Entferne mögliche Kommentare oder Formatierungen (z.B. Links)
        for match in matches:
            # Entferne [[ und ]] von Links und trimme Leerzeichen
            substances.append(match)
            # print(match)

    except Exception as e:
        traceback.print_exc()
        print(f"Fehler beim Abrufen oder Analysieren der Seite: {e}")

    # print(substances)
    return substances


def extract_template_parameters(page_text, template_name):
    template_pattern = re.compile(r"{{\s*Substanzinfo.*?}}", re.DOTALL)
    matches = template_pattern.findall(page_text)

    parameters_list = []
    for match in matches:
        parameters = {'Name': None, 'Wikidata': None}
        
        name_match = re.search(r'\bName\s*=\s*(.+?)(?=\||}})', match, re.DOTALL)
        if name_match:
            parameters['Name'] = name_match.group(1).strip()

        wikidata_match = re.search(r'\bWikidata\s*=\s*(.+?)(?=\||}})', match, re.DOTALL)
        if wikidata_match:
            parameters['Wikidata'] = wikidata_match.group(1).strip()

        cas_match = re.search(r'\bCAS\s*=\s*(.*?)(?=\||}})', match, re.DOTALL)
        if cas_match:
            cas = cas_match.group(1).strip()
            if not cas == "":
                parameters['CAS'] = cas_match.group(1).strip()

        parameters_list.append(parameters)

    return parameters_list

def human_readable_time_difference(start_time, end_time):
    delta = end_time - start_time
    days, seconds = divmod(delta, 3600 * 24)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    result = []
    if days > 0:
        result.append(f"{int(days)} Tage")
    if hours > 0:
        result.append(f"{int(hours)} Stunden")
    if minutes > 0:
        result.append(f"{int(minutes)} Minuten")
    if seconds > 0:
        result.append(f"{round(seconds, 1)} Sekunden")

    return ', '.join(result)


def update_wikipedia_page(site, new_entries):
    page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Neuzugänge"
    # page_title = "Benutzer:Rjh/Test4"
    page = pywikibot.Page(site, page_title)
    
    try:
        text = page.text
        section_pattern = r'(==+\s*Substanzinfo\s*==+)(.*?)(?=\n==|\Z)'
        match = re.search(section_pattern, text, re.DOTALL)
        
        if not match:
            print("Abschnitt 'Substanzinfo' nicht gefunden.")
            return
        
        section_header, section_content = match.groups()
        new_section_content = "\n" + "\n".join(new_entries)
        new_text = text.replace(section_content, new_section_content)
        
        if new_text != text:
            page.text = new_text
            page.save(f"Automatische Aktualisierung des Abschnitts 'Substanzinfo' ({len(new_entries)} Einträge)")
            print("Seite aktualisiert.")
        else:
            print("Keine Änderungen notwendig.")
    except Exception as e:
        traceback.print_exc()

def main():
    zeitanfang = time.time()

    # Wikipedia-Site definieren (deutsche Wikipedia)
    site = pywikibot.Site('de', 'wikipedia')

    # Lade liste der zu ignorierenden Seite
    ignore_list = get_ignore_list(site)

    # Lade liste der zu ignorierenden Seite
    exclusion_list = get_exclusion_list(site)

    # fehlende Substanzen Seite auswerten 
    missing_substances_list, missing_substances_list_wikidata = get_missing_substances_list(site)

    # Vorlage, nach der gesucht werden soll
    template_name = "Substanzinfo"

    print(f"Suche nach Seiten, die das Template {template_name} enthalten ...")
    # Generator für Seiten, die die Vorlage verwenden
    pages = list(site.search(f'hastemplate:"{template_name}"'))
       
    # Dictionary, um Seiten nach 'Name' und 'Wikidata' zu gruppieren
    data_to_pages = defaultdict(list)
    cas_to_pages = defaultdict(list)

    start_time = time.time()  # Startzeit der Schleife
    interval = 60  # Intervall in Sekunden
    count = 0

    new_entries = []

    new_entries.append(f"Seiten, die die Vorlage '{template_name}' enthalten und die nicht auf [[Wikipedia:Redaktion Chemie/Fehlende Substanzen]] genannt sind:")
    new_entries.append(f"")

    print(f"Analysiere {len(pages)} gefundene Seiten ...")

    # Seiten mit der Vorlage auflisten und Parameter extrahieren
    for page in pages:
        # if not page.isRedirectPage() and ((page.namespace() == 0) or (page.title() == "Benutzer:Anagkai/Substanzinfos")):
        if not page.isRedirectPage() and ((page.namespace() == 0) and not page.title() in exclusion_list):
            global pages_checked
            pages_checked += 1

            count += 1
            if time.time() - start_time >= interval:
                start_time = time.time()
                print(f"{count}. Seite: {page.title()}")

            try:
                page_text = page.text
                parameters_list = extract_template_parameters(page_text, template_name)

                # Gruppiere nach 'Name' und 'Wikidata' für alle Matches
                for parameters in parameters_list:
                    name = parameters['Name']
                    name = name.replace("[", "(").replace("]", ")")
                    name = name.replace("{", "(").replace("}", ")")
                    name = name.replace("<sup>", "(").replace("</sup>", ")")
                    name = name.replace("<sub>", "(").replace("</sub>", ")")
                    name = name.replace("<nowiki>", "").replace("</nowiki>", "").replace("<nowiki />", "")
                    name = name.replace("<small>", "").replace("</small>", "")
                    name = name.replace("''", "")
                    wikidata = parameters['Wikidata']
                    # print(wikidata)
                    if name or wikidata:
                        if (name not in missing_substances_list) and (name not in ignore_list) and (not wikidata or (wikidata not in missing_substances_list_wikidata)):
                            key = (name, wikidata)
                            data_to_pages[key].append("[[" + page.title() + "]]")
                            if 'CAS' in parameters:
                                cas_to_pages[key] = parameters['CAS']
                                # print(cas_to_pages[key], " ", name, " ", wikidata)
                                  
            except Exception as e:
                traceback.print_exc()
                print(f"Fehler beim Verarbeiten der Seite '{page.title()}': {e}")

    # Sortiere nach Namen und gib die Ergebnisse aus
    for (name, wikidata), pages in sorted(data_to_pages.items(), key=lambda x: (x[0][0] or "").lower()):
        key = (name, wikidata)
        cas = cas_to_pages[key]
        # print(cas)
        name_output = f"{name}" if name else "Name: (keiner)"
        wikidata_output = f"{wikidata}" if wikidata else "(keiner)"
        entry = ""
        # write_output(f"* [[{name_output}]], ({', '.join(pages)}, [[d:{wikidata_output}]])")
        if cas:
            entry = f"* [[{name_output}]] >> {', '.join(pages)} >> {cas},{wikidata_output} >>"
        else:
            entry = f"* [[{name_output}]] >> {', '.join(pages)} >> {wikidata_output} >>"
        new_entries.append(entry)

    update_wikipedia_page(site, new_entries)

    print(f"\npages_checked = {pages_checked}, pages_changed = {pages_changed}, entries = {len(new_entries)}")
    print("\nLaufzeit: " + human_readable_time_difference(zeitanfang, time.time()))


if __name__ == "__main__":
    main()
