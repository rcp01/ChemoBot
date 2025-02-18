import pywikibot
import re
import time
from pywikibot import pagegenerators

def human_readable_time_difference(start_time, end_time):
    """
    Gibt die Zeitdifferenz zwischen zwei Zeitpunkten in menschlich lesbarer Form zurück.

    Args:
        start_time: Startzeit.
        end_time: Endzeit.

    Returns:
        String: Zeitdifferenz in lesbarer Form.
    """
    delta = end_time - start_time
    days, seconds = divmod(delta, 3600 * 24)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    result = []
    if days > 0:
        result.append(f"{days} Tage")
    if hours > 0:
        result.append(f"{hours} Stunden")
    if minutes > 0:
        result.append(f"{minutes} Minuten")
    if seconds > 0:
        result.append(f"{round(seconds, 1)} Sekunden")

    return ', '.join(result)

start_time = time.time()  # Startzeit der Schleife
interval = 60  # Intervall in Sekunden
pages_checked = 0

# Einstellungen
site = pywikibot.Site("de", "wikipedia")  # Wikipedia in deutscher Sprache

template_name = "Infobox Protein"  # Name der Vorlage

# Generator für Seiten mit der Vorlage
search_gen = site.search(f'hastemplate:"{template_name}"', namespaces=[0])

# Muster für den AltSymbols-Parameter
alt_symbols_pattern = re.compile(r'(\|\s*AltSymbols\s*=)([^\n\r]*)')

for page in search_gen:
    if time.time() - start_time >= interval:
        start_time = time.time()  # Reset der Startzeit für die nächste Nachricht
        print(f"{pages_checked}, aktuelle Seite: {page.title()}")

    pages_checked += 1
    text = page.text
    
    # Suche nach AltSymbols
    match = alt_symbols_pattern.search(text)
    if match:
        
        original_alt = match.group(1).strip()
        original_value = match.group(2).strip()
        
        # Bearbeitung: Entferne führendes Komma, ersetze ";" durch ","
        new_value = re.sub(r'^[,;]\s*', '', original_value.replace('&nbsp;', ' ').strip())
        new_value = new_value.replace(';', ',')
        
        # Falls sich etwas geändert hat, ersetze den Wert
        if new_value != original_value:
            new_text = alt_symbols_pattern.sub(f'{original_alt} {new_value}', text)
            
            # Speichern der Änderung
            page.text = new_text
            print(f"{page.title()}: old= \"{original_value}\" -> new= \"{new_value}\"")
            page.save(summary="Bot: AltSymbols-Parameter formatiert (führendes Komma entfernt, ; durch , ersetzt)")

print("Fertig!")
print("\nLaufzeit: ", human_readable_time_difference(start_time, time.time()))
