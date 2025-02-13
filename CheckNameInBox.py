import pywikibot
import re
import time

def has_template(page_text, template_name):
    """Prüft, ob eine Vorlage im Seitentext enthalten ist."""
    return re.search(r'{{\s*' + re.escape(template_name) + r'\b', page_text, re.IGNORECASE) is not None

def extract_infobox_parameters(page_text, infobox_name):
    """Extrahiert die Parameter einer bestimmten Infobox aus dem Seitentext."""
    infobox_pattern = re.compile(r'{{\s*' + re.escape(infobox_name) + r'\s*(.*?)}}', re.DOTALL)
    match = infobox_pattern.search(page_text)
    if match:
        return match.group(1)
    return ""

def extract_name_parameter(infobox_text):
    """Extrahiert den Wert des 'Name'-Parameters aus der Infobox."""
    name_match = re.search(r'^\s*\|\s*Name\s*=\s*([^\n|]+)', infobox_text, re.MULTILINE)
    if name_match:
        return name_match.group(1).strip()
    return None

def extract_title_template(page_text, template_name):
    """Extrahiert den Wert aus SEITENTITEL oder DISPLAYTITLE."""
    title_match = re.search(r'{{\s*' + re.escape(template_name) + r'\s*\:\s*([^\n|}]+)', page_text, re.IGNORECASE)
    if title_match:
        return title_match.group(1).strip()
    return None

def human_readable_time_difference(start_time, end_time):
    """
    Gibt die Zeitdifferenz zwischen zwei datetime-Objekten in menschlich lesbarer Form zurück.

    :param start_time: Das Start-datetime-Objekt.
    :param end_time: Das End-datetime-Objekt.
    :return: Ein String, der die Zeitdifferenz in einer lesbaren Form darstellt.
    """
    # Berechne die Differenz
    delta = end_time - start_time
    
    # Extrahiere Tage, Stunden, Minuten und Sekunden
    days, seconds = divmod (delta, 3600*24)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    
    # Baue die menschlich lesbare Form auf
    result = []
    if days > 0:
        result.append(f"{days} Tage")
    if hours > 0:
        result.append(f"{hours} Stunden")
    if minutes > 0:
        result.append(f"{minutes} Minuten")
    if seconds > 0:
        result.append(f"{round(seconds,1)} Sekunden")
    
    return ', '.join(result)


def main():
    zeitanfang = time.time()	

    print("Start ...")

    site = pywikibot.Site('de', 'wikipedia')
    template_name = "Infobox Chemikalie"
    search_gen = site.search(f'hastemplate:"{template_name}"', namespaces=[0])

    print("Seiten, die {{SEITENTITEL}} oder {{DISPLAYTITLE}} enthalten, aber entweder keinen Name-Parameter in der Infobox haben oder deren Name-Parameter nicht mit dem Seitentitel übereinstimmt:")

    start_time = time.time()  # Startzeit der Schleife
    interval = 60  # Intervall in Sekunden
    pages_checked = 0

    for page in search_gen:

        # page = pywikibot.Page(site, "3,4-Methylendioxy-N-ethylamphetamin")

        pages_checked += 1

        if time.time() - start_time >= interval:
            start_time = time.time()  # Reset der Startzeit für die nächste Nachricht
            print(f"{pages_checked}. aktuelle Seite: {page.title()}")

        try:
            page_text = page.text
            infobox_text = extract_infobox_parameters(page_text, template_name)
            if not infobox_text:
                print("No infobox found")
            name_value = extract_name_parameter(infobox_text)
            title_value = extract_title_template(page_text, "SEITENTITEL") or extract_title_template(page_text, "DISPLAYTITLE")

            # print(infobox_text)
            # print(name_value)
            # exit(0)
            
            if title_value and (name_value is None or name_value.replace("[","(").replace("]",")") != title_value):
                print(f"* [[{page.title()}]] (Infobox-Name: {name_value if name_value else 'Nicht vorhanden'}, SEITENTITEL/DISPLAYTITLE: {title_value})")

        except Exception as e:
            print(f"Fehler beim Verarbeiten der Seite {page.title()}: {e}")

    print("\nLaufzeit: ",human_readable_time_difference(zeitanfang, time.time()))


if __name__ == "__main__":
    main()
