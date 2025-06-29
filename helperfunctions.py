import re

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
    substance_name = substance_name.replace("folin", "foline")
   
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
        result.append(f"{int(days)} Tage")
    if hours > 0:
        result.append(f"{int(hours)} Stunden")
    if minutes > 0:
        result.append(f"{int(minutes)} Minuten")
    if seconds > 0:
        result.append(f"{round(seconds, 1)} Sekunden")

    return ', '.join(result)

