import pywikibot
import re
import requests
from urllib.parse import quote

# Einstellungen
template_name = "Vorlage:Sigma-Aldrich"
site = pywikibot.Site("de", "wikipedia")

# Funktion zum Testen einer URL
def get_sigma_status_code(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, allow_redirects=True, timeout=10, stream=True, headers=headers)
        status = response.status_code
        response.close()
        print(status)
        return status
    except requests.RequestException as e:
        print(f"Fehler bei {url}: {e}")
        return None
        
        
# Finde alle Seiten, die die Vorlage verwenden
template_page = pywikibot.Page(site, template_name)
transclusions = list(template_page.getReferences(only_template_inclusion=True))

print(f"{len(transclusions)} Seiten mit {{Sigma-Aldrich}} gefunden.\n")

for page in transclusions:
    try:
        text = page.get()
        
        # Versuche, den Parameterwert aus der Vorlage zu extrahieren
        # z.B. {{Sigma-Aldrich|12345}} oder {{Sigma-Aldrich| id = 12345 }}
        match = re.search(r"\{\{\s*Sigma-Aldrich\s*\|(.*?)\|(.*?)\|.*?\}\}", text, re.IGNORECASE)
        
        if not match:
            print(f"❓ Vorlage auf Seite '{page.title()}' nicht erkennbar.")
            continue

        company = match.group(1).strip()
        substanz_id = match.group(2).strip()
        
        # Beispiel-URL konstruieren (dies anpassen an reales URL-Muster)
        url = f"https://www.sigmaaldrich.com/DE/de/product/{quote(company)}/{quote(substanz_id)}"
        
        if get_sigma_status_code(url):
            print(f"❌ 404-Fehler auf Seite '{page.title()}': {url}")
        else:
            print(f"✅ OK auf Seite '{page.title()}': {url}")

    except Exception as e:
        print(f"Fehler bei Seite '{page.title()}': {e}")
