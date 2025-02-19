import pywikibot
import re
import time
from pywikibot import pagegenerators

def split_at_first_comma(s):
    """Teilt den String am ersten Komma auf und entfernt Leerzeichen an den Rändern."""
    if ',' in s:
        part1, part2 = s.split(',', 1)
        return part1.strip(), part2.strip()
    return s.strip(), ''  # Falls kein Komma vorhanden ist, bleibt der zweite Teil leer

def extract_infoboxes(text):
    """
    Sucht nach allen Abschnitten im Text, die zwischen zwei Vorkommen des Delimiters oder zwischen einem Vorkommen und dem Ende des Strings liegen.

    Args:
        text (str): Der Eingabetext.

    Returns:
        list: Eine Liste mit den gefundenen Abschnitten.
    """
    delimiter = "{{Infobox Protein"
    infoboxes = []
    parts = text.split(delimiter)
    for i in range(1, len(parts)):
        infoboxes.append((delimiter + parts[i]))
    return infoboxes

def correct_symbols_in_infobox(box_text):

    # Muster für den Symbols-Parameter
    symbols_pattern = re.compile(r'(\|\s*Symbol\s*=)([^\n\r]*)')
    match = symbols_pattern.search(box_text)

    # Muster für den AltSymbols-Parameter
    alt_symbols_pattern = re.compile(r'(\|\s*AltSymbols\s*=)([^\n\r]*)')
    alt_match = alt_symbols_pattern.search(box_text)

    part2 = ""
    if match:
        # print(match)
        
        original_param = match.group(1).strip()
        original_value = match.group(2).strip()
        
        if "[" in original_value:
            print(f'######## Warning: Weblink found -> don\'t change {original_value}')
            return box_text
        
        # Bearbeitung: Entferne führendes Komma, ersetze ";" durch ","
        new_value = re.sub(r'^[,;]\s*|\s*[,;]$', '', original_value.replace('&nbsp;', ' ').strip())
        new_value = new_value.replace(';', ',')
        
        part1, part2 = split_at_first_comma(new_value)
        
        # print(f'part1={part1}, part2={part2}')
        
        # Falls sich etwas geändert hat, ersetze den Wert
        if part1 != original_value:
            if not alt_match:
                # alt symbols entry do not exists, we have to create it
                
                original_alt_param = replace_key_with_padding(original_param, "Symbol", "AltSymbols")
                part1 += f"\n{original_alt_param} {part2}"
                
                print("original_param:     ", original_param)
                print("original_alt_param: ", original_alt_param)
                                
            box_text = symbols_pattern.sub(f'{original_param} {part1.strip()}', box_text)
            print(f"Symbols= {page.title()}: old= \"{original_value}\" -> new= \"{part1.strip()}\"")
                
    # Suche nach AltSymbols
    if alt_match:
        # print(match)
        
        original_alt_param = alt_match.group(1).strip()
        original_alt_value = alt_match.group(2).strip()
        
        # Bearbeitung: Entferne führendes Komma, ersetze ";" durch ","
        new_value = re.sub(r'^[,;]\s*|\s*[,;]$', '', original_alt_value.replace('&nbsp;', ' ').strip())
        new_value = new_value.replace(';', ',')
        
        if part2 != "":
            if (new_value != ""):
                new_value += f', {part2}'
            else:
                new_value = part2                
            
        # Falls sich etwas geändert hat, ersetze den Wert
        if new_value != original_alt_value:
            box_text = alt_symbols_pattern.sub(f'{original_alt_param} {new_value}', box_text)
            print(f"AltSymbol= {page.title()}: old= \"{original_alt_value}\" -> new= \"{new_value}\"")

    return box_text

def replace_key_with_padding(text, old_key, new_key):
    """
    Ersetzt old_key durch new_key, während die Anzahl der Zeichen erhalten bleibt.

    Args:
        text (str): Der Eingabetext.
        old_key (str): Der zu ersetzende Schlüssel.
        new_key (str): Der neue Schlüssel.

    Returns:
        str: Der modifizierte Text mit angepassten Leerzeichen.
    """
    pattern = re.compile(rf'({re.escape(old_key)})(\s*)=')
    
    def replacement(match):
        key, spaces = match.groups()
        padding = max(len(key) - len(new_key) + len(spaces), 1)
        return new_key + ' ' * padding + '='

    return pattern.sub(replacement, text)


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

for page in search_gen:
    
    # page = pywikibot.Page(site, "Benutzer:ChemoBot/Test1")    
    
    if time.time() - start_time >= interval:
        start_time = time.time()  # Reset der Startzeit für die nächste Nachricht
        print(f"{pages_checked}, aktuelle Seite: {page.title()}")

    pages_checked += 1
    text = page.text
 
    result = extract_infoboxes(text)
    
    for i, section in enumerate(result, 1):
        # print(f"Abschnitt {i}: {section}")
 
        new_section = correct_symbols_in_infobox(section)
        if new_section != section:
            text = text.replace(section, new_section)

    if text != page.text:
        # Speichern der Änderung
        # print(text)
        page.text = text
        page.save(summary="Bot: Symbols und AltSymbols-Parameter formatiert (führendes Komma entfernt, ; durch , ersetzt)")

    # break
    
print("Fertig!")
print("\nLaufzeit: ", human_readable_time_difference(start_time, time.time()))
