import pywikibot
import re

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

def has_name_parameter(infobox_text):
    """Prüft, ob die Infobox den Parameter 'Name' enthält."""
    return re.search(r'\|\s*Name\s*=\s*[^|]+', infobox_text, re.IGNORECASE) is not None

def main():
    site = pywikibot.Site('de', 'wikipedia')
    template_name = "Infobox Chemikalie"
    search_gen = site.search(f'hastemplate:"{template_name}"', namespaces=[0])

    print("Seiten, die {{SEITENTITEL}} oder {{DISPLAYTITLE}} enthalten, aber keinen Name-Parameter in der Infobox Chemikalie haben:")

    for page in search_gen:
        try:
            page_text = page.text
            infobox_text = extract_infobox_parameters(page_text, template_name)
            
            if (has_template(page_text, "SEITENTITEL") or has_template(page_text, "DISPLAYTITLE")) and not has_name_parameter(infobox_text):
                print(f"* [[{page.title()}]]")
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Seite {page.title()}: {e}")

if __name__ == "__main__":
    main()
