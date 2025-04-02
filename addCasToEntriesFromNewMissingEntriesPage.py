import pywikibot
import requests
import re
from deep_translator import GoogleTranslator

def translate_substance_name_to_englisch(substance_name):
    if bool(re.search(r"e$" , substance_name)) and not re.search(r"(säure|ose|ase)$", substance_name):
        substance_name += "s"
    elif re.search(r"(on|id|en|din|mid|dol)$", substance_name):
        substance_name += "e"
#    else:
#        print("nothing")
    substance_name = substance_name.replace("essigsäure", "acetic acid")
    substance_name = substance_name.replace("benzoesäure", "benzoic acid")
    substance_name = substance_name.replace("propansäure", "propanoic acid")
    substance_name = substance_name.replace("andelsäure", "andelic acid")
    substance_name = substance_name.replace("salicylsäure", "salicylic acid")
    substance_name = substance_name.replace("catechusäure", "catechuic acid")
    substance_name = substance_name.replace("allussäure", "allic acid")
    substance_name = substance_name.replace("phthalsäure", "phthalic acid")
    substance_name = substance_name.replace("uttersäure", "utyric acid")
    substance_name = substance_name.replace("hosphonsäure", "hosphorous acid")
    substance_name = substance_name.replace("cyansäure", "cyanic acid")
    substance_name = substance_name.replace("diensäure", "dienoic acid")
    substance_name = substance_name.replace("weinsäure", "tartaric acid")
    substance_name = substance_name.replace("ylsäure", "ylic acid")
    substance_name = substance_name.replace("insäure", "inic acid")
    substance_name = substance_name.replace("ilsäure", "ilic acid")
    substance_name = substance_name.replace("onsäure", "onic acid")
    substance_name = substance_name.replace("olsäure", "olic acid")
    substance_name = substance_name.replace("oesäure", "oic acid")
    substance_name = substance_name.replace("säure", " acid")
    substance_name = substance_name.replace("naphthalin", "naphthalene")
    substance_name = substance_name.replace("chinone", "quinone")
    substance_name = substance_name.replace("chinon", "quinone")
    substance_name = substance_name.replace("cumarin", "coumarin")
    substance_name = substance_name.replace("Natrium", "Sodium ")
    substance_name = substance_name.replace("natrium", "sodium ")
    substance_name = substance_name.replace("Kalium", "Potassium ")
    substance_name = substance_name.replace("kalium", "potassium ")
    substance_name = substance_name.replace("Mangan", "Manganese ")
    substance_name = substance_name.replace("mangan", "manganese ")
    substance_name = substance_name.replace("enzol", "enzene")
    substance_name = substance_name.replace("oxazol", "oxazole")
    substance_name = substance_name.replace("azetat", "acetate")
    substance_name = substance_name.replace("aldehyd", "aldehyde")
    substance_name = substance_name.replace("azin", "azine")
    substance_name = substance_name.replace("pikryl", "picryl")
    substance_name = substance_name.replace("zucker", " sugar")
    substance_name = substance_name.replace("ethinyl", "ethynyl")
    substance_name = substance_name.replace("citrat", "citrate")
    substance_name = substance_name.replace("laurin", "laurine")
    substance_name = substance_name.replace("phosphat", "phosphate")
    substance_name = substance_name.replace("phenolat", "phenolate")
    substance_name = substance_name.replace("silicat", "silicate")
    substance_name = substance_name.replace("than", "thane")
    substance_name = substance_name.replace("phthalat", "phthalate")
    substance_name = substance_name.replace("oluol", "oluene")
    substance_name = substance_name.replace("resorcin", "resorcinol")
    substance_name = substance_name.replace("imonen-", "imonene-")
    substance_name = substance_name.replace("Brenzcatechin", "Catechol")
    substance_name = substance_name.replace("brenzcatechin", "catechol")
    substance_name = substance_name.replace("farbstoff", " dye")
    substance_name = substance_name.replace(" (Chemie)", "")
    substance_name = substance_name.replace("Salz", "Salt")
    substance_name = substance_name.replace("salz", "salt")
    substance_name = substance_name.replace("harz", "resin")
    substance_name = substance_name.replace("blei", "lead ")
    substance_name = substance_name.replace("Blei", "Lead ")
    substance_name = substance_name.replace("Eisen", "Iron ")
    substance_name = substance_name.replace("eisen", "iron ")
    substance_name = substance_name.replace("Titan", "Titanium ")
    substance_name = substance_name.replace("titan", "titanium ")
    substance_name = substance_name.replace("Zink", "Zinc ")
    substance_name = substance_name.replace("zink", "zinc ")
    substance_name = substance_name.replace("Wolfram", "Tungsten ")
    substance_name = substance_name.replace("wolfram", "tungsten ")
    substance_name = substance_name.replace("Zinn", "Tin ")
    substance_name = substance_name.replace("zinn", "tin ")
    substance_name = substance_name.replace("Quecksilber", "Mercury ")
    substance_name = substance_name.replace("quecksilber", "mercury ")
    substance_name = substance_name.replace("Silber", "Silver ")
    substance_name = substance_name.replace("silber", "silver ")
    substance_name = substance_name.replace("molybdän", "molybdenum ")
    substance_name = substance_name.replace("Molybdän", "Molybdenum ")
   
    if not "bromid" in substance_name.lower():
        substance_name = substance_name.replace("brom", "bromo")    
        substance_name = substance_name.replace("Brom", "bromo")

    if "fluoranthen" in substance_name.lower():
        substance_name = substance_name.replace("fluoranthen", "fluoranthene")        
        substance_name = substance_name.replace("fluoranthenee", "fluoranthene")        
    elif "fluoranthen" in substance_name.lower(): 
        substance_name = substance_name.replace("fluoriden", "fluorene")
    elif "fluorenon" in substance_name.lower(): 
        substance_name = substance_name.replace("fluorenon", "fluorenone")
    else:
        if not "fluorid" in substance_name.lower() and not "fluoren" in substance_name.lower():
            substance_name = substance_name.replace("fluor", "fluoro")
            substance_name = substance_name.replace("Fluor", "fluoro")

    if not "chlorid" in substance_name.lower():
        substance_name = substance_name.replace("chlor", "chloro")
        substance_name = substance_name.replace("Chlor", "chloro")

    if not "iodid" in substance_name.lower() and not "iodo" in substance_name.lower():
        substance_name = substance_name.replace("iod", "iodo")
        substance_name = substance_name.replace("Iod", "Iodo")

    return substance_name

def search_cas_number(chemical_name):
    """
    Ruft die Common Chemistry-Suchseite mit dem angegebenen Namen auf
    und prüft, ob eine CAS-Nummer enthalten ist.
    
    Args:
        chemical_name (str): Der Name der chemischen Verbindung.
    
    Returns:
        str: Gefundene CAS-Nummer oder leerer String, wenn keine gefunden wurde.
    """
    
    chemical_name_org = chemical_name
    chemical_name = translate_substance_name_to_englisch(chemical_name)
    
    url = f"https://commonchemistry.cas.org/results?q={chemical_name}"
    response = requests.get(url)

    if response.status_code == 200:
        match = re.search(r"(\d{2,8}-\d{2}-\d)", response.text)
        
        if match:
            print(f"\"{chemical_name_org}\" -> \"{chemical_name}\" : commonchemistry = {match.group(1)}")
            return match.group(1)
        else:
            url = f"https://www.chemicalbook.com/Search_EN.aspx?keyword={chemical_name}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Referer": "https://www.chemicalbook.com/" 
                }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                # print(response.text)
                match = re.search(r"(<table.*?</table>)", response.text, re.DOTALL)
                if match:
                    # print(match.group(1))
                    match = re.search(r"(\d{2,8}-\d{2}-\d)", match.group(1))
                    if match:
                        print(f"\"{chemical_name_org}\" -> \"{chemical_name}\" : chemicalbook = {match.group(1)}")
                        return match.group(1)
            else:
                print(f"Fehler: {response.status_code} für {chemical_name} {url}")
    else:
        print(f"Fehler: {response.status_code} für {chemical_name} {url}")

    print(f"\"{chemical_name_org}\" -> \"{chemical_name}\" : None")
    return ""

search_cas_number("Hafniumsilicat")
#exit(0)

# Verbindung zur deutschen Wikipedia
site = pywikibot.Site("de", "wikipedia")

# Zu bearbeitende Seite
page_title = "Wikipedia:Redaktion Chemie/Fehlende Substanzen/Neuzugänge"
#page_title = "Benutzer:ChemoBot/Tests/Neuzugänge"
page = pywikibot.Page(site, page_title)

# Seite abrufen
text = page.text

# Abschnitt "Rotlinks" finden
match = re.search(r"==\s*Rotlinks\s*==(.*?)(?:==|$)", text, re.DOTALL)

if match:
    rotlinks_text = match.group(1).strip()
    lines = rotlinks_text.split("\n")  # Zeilenweise Verarbeitung
    updated_lines = []

    all = 0
    for line in lines:
        link_match = re.search(r"\*\s*\[\[(.*?)\]\]", line)
        if link_match:
           all +=1
    
    count = 0
    for line in lines:       
        link_match = re.search(r"\*\s*\[\[(.*?)\]\]", line)
        
        if link_match:
            count += 1
            chemical_name = link_match.group(1).strip()
            cas_number = search_cas_number(chemical_name)
            print(f"{count}/{all}: {chemical_name} - {cas_number}")

            if cas_number and cas_number != "":
                line = line.replace(">>  >>", f">> {cas_number} >>")

        updated_lines.append(line)

    # Aktualisierte Rotlinks zurück in den Text einfügen
    new_rotlinks_text = "\n".join(updated_lines)
    new_text = text.replace(rotlinks_text, new_rotlinks_text)

    # Änderungen speichern, falls es Unterschiede gibt
    if text != new_text:
        page.text = new_text
        page.save("Bot: Ergänze wahrscheinliche CAS-Nummern in Rotlinks-Abschnitt")
        print("Änderungen gespeichert! ✅")
    else:
        print("Keine Änderungen erforderlich.")

else:
    print("Abschnitt 'Rotlinks' nicht gefunden.")

