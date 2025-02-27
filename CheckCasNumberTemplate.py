import pywikibot
import requests
import time
from pywikibot import pagegenerators
import traceback

def starts_with_digit(s):
    return s[0].isdigit() if s else False


def check_webpage_for_text(url, text):
    try:
        # Sende eine GET-Anfrage an die Webseite
        response = requests.get(url)
        
        # Prüfe, ob die Anfrage erfolgreich war (Statuscode 200)
        if response.status_code == 200:
            # Überprüfe, ob der Text auf der Seite vorkommt
            return text in response.text
        else:
            print(f"Fehler: Die Seite wurde nicht erfolgreich geladen. Statuscode: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Webseite: {e}")
        return False

def checkCASLink(CAS, pagename):
    # print (f"CAS = {CAS}")
    if (check_webpage_for_text("https://commonchemistry.cas.org/detail?ref="+CAS, "Get detail failed: Detail not found ")):
        print(f"############## invalid link found in page {pagename} for CAS {CAS} ############")
        return False
    return True

def AddNoCasLinkToTemplate(template, template_name, params, text):
    # Original-Template als Text zusammenbauen, um es im Text zu finden
    template_name = template_name.replace("Vorlage:", "")
    original_template_text = f"{{{{{template_name}"
    for p in params:
        original_template_text += f"|{p}"
    original_template_text += "}}"

    new_params = []
    for param in params:
        # Aufteilen in Namen und Wert des Parameters
        param_split = param.split("=", 1)
        current_name = param_split[0].strip()
        current_value = param_split[1].strip() if len(param_split) > 1 else ""
        new_params.append(param)

    # Falls der Parameter noch nicht existierte, hinzufügen
    new_params.append("KeinCASLink=1")
    
    # Die neue Vorlage als Textstring zusammensetzen
    new_template_text = f"{{{{{template_name}"
    for p in new_params:
        new_template_text += f"|{p}"
    new_template_text += "}}"

    print(original_template_text, " -> ", new_template_text)

    # Die alte Vorlage im Text durch die neue ersetzen
    text = text.replace(original_template_text, new_template_text)
    return text

def checkpage(page, template_name):
    try:
        # Extrahiere die Vorlagen und ihre Parameter auf der Seite
        templates = page.templatesWithParams()
        new_text = page.text
        
        # Durchlaufe alle Vorlagen und suche nach der gewünschten Vorlage        
        for template, params in templates:
            if template.title() == template_name:  # Prüfe, ob es die richtige Vorlage ist
                # print(f"  Gefundene Vorlage: {template.title()}")
                # print(f"  Parameter:")
                           
                # Durchlaufe die Parameter und gib sie aus
                CAS = ""
                KeinCasLink = False
                for param in params:
                    param_name, param_value = param.split('=', 1) if '=' in param else (param, '')
                    if CAS == "":
                        CAS = param_name.strip();
                        if (not starts_with_digit(CAS)):
                            print(f"####################  Error in CAS: ", CAS)
                    if (param_name.strip() == "KeinCASLink"):
                        KeinCasLink = True
                        if param_value.strip() != "1":
                            print(f"####################  Error in parameter for KeinCasLink: \"", param_value.strip(), "\" in page ", page.title())
                    # print(f"    {param_name.strip()} = {param_value.strip()}")
                
                if (not KeinCasLink):
                    if (not checkCASLink(CAS, page.title())):
                       new_text = AddNoCasLinkToTemplate(template, template_name, params, new_text)
                       if (new_text == page.text):
                            print(f"####################  nothing replaced: params =\n", params, "\n text = \n", page.text)

        if (page.text != new_text):
            print("old=\n", page.text, "\n\nnew=\n", new_text)
            page.text = new_text
            page.save(summary="ChemoBot: Vorlage CASRN mit KeinCasLink ersetzt für unbekannte CAS Nummern.", minor=True)

    except Exception as e:
        print(f"  Fehler beim Verarbeiten der Seite: {e}" + traceback.format_exc())

# @profile
def runsearch():
    template_name = 'Vorlage:CASRN'
    # Setze das Wiki, auf dem du arbeiten möchtest (Wikipedia in deutscher Sprache)
    site = pywikibot.Site('de', 'wikipedia')

    # page = pywikibot.Page(site, "Benutzer:ChemoBot/Test1")
    # checkpage(page, template_name)
    # exit(0)

    # Wähle die Vorlage, nach der du suchen möchtest
    template_page = pywikibot.Page(site, template_name)

    # Finde alle Seiten, die die Vorlage verwenden
    pages_with_template = template_page.embeddedin()

    start_time = time.time()  # Startzeit der Schleife
    interval = 60  # Intervall in Sekunden
    count = 0

    # Durchlaufe alle Seiten, die die Vorlage verwenden
    for page in pages_with_template:
        # print(f"Seite: {page.title()}")
        count = count + 1

        if page.namespace() != 0 or page.isRedirectPage():
            continue

        if time.time() - start_time >= interval:
            start_time = time.time()  # Reset der Startzeit für die nächste Nachricht
            print(f"{count}. Seite: {page.title()}")

        checkpage(page, template_name)

runsearch()

