#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pywikibot
import re

SOURCE_PAGE = "Benutzer:Rjh/Test"
OK_PAGE = "Benutzer:Rjh/Valid_Redirects"
NOK_PAGE = "Benutzer:Rjh/Critical_Redirects"

def extract_marked_entries(text):
    """Extrahiert OK- und NOK-Einträge"""

    ok_entries = []
    nok_entries = []
    remaining_lines = []

    for line in text.splitlines():

        line_stripped = line.strip()
        lower = line_stripped.lower()

        if ": ok" in lower or ": nok" in lower:

            cleaned = line_stripped

            # führendes "* " entfernen
            if cleaned.startswith("*"):
                cleaned = cleaned[1:].strip()

            # OK oder NOK erkennen + entfernen
            if ": ok" in lower:
                cleaned = re.sub(r":\s*ok\s*$", "", cleaned, flags=re.IGNORECASE)
                ok_entries.append(cleaned)

            elif ": nok" in lower:
                cleaned = re.sub(r":\s*nok\s*$", "", cleaned, flags=re.IGNORECASE)
                nok_entries.append(cleaned)

        else:
            remaining_lines.append(line)

    return ok_entries, nok_entries, "\n".join(remaining_lines)


def load_existing(text):
    """Vorhandene Einträge laden"""

    existing = set()

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("*"):
            line = line[1:].strip()

        existing.add(line)

    return existing


def append_entries(old_text, new_entries):
    """Hängt neue Einträge an bestehenden Text an"""

    if not new_entries:
        return old_text

    text = old_text.strip()

    if text:
        text += "\n"

    text += "\n".join(new_entries)

    return text


def main():

    site = pywikibot.Site("de", "wikipedia")

    source_page = pywikibot.Page(site, SOURCE_PAGE)
    ok_page = pywikibot.Page(site, OK_PAGE)
    nok_page = pywikibot.Page(site, NOK_PAGE)

    print("Lese Quellseite...")
    source_text = source_page.get()

    print("Extrahiere markierte Einträge...")
    ok_entries, nok_entries, new_source_text = extract_marked_entries(source_text)

    if not ok_entries and not nok_entries:
        print("Keine OK/NOK-Einträge gefunden.")
        return

    print(f"{len(ok_entries)} OK, {len(nok_entries)} NOK gefunden")

    # Bestehende Seiten laden
    try:
        exception_text = ok_page.get()
    except:
        exception_text = ""

    try:
        nok_text = nok_page.get()
    except:
        nok_text = ""

    existing_exceptions = load_existing(exception_text)
    existing_nok = load_existing(nok_text)

    # Duplikate vermeiden
    new_ok = [e for e in ok_entries if e not in existing_exceptions]
    new_nok = [e for e in nok_entries if e not in existing_nok]

    print(f"{len(new_ok)} neue OK, {len(new_nok)} neue NOK")

    # Seiten aktualisieren
    updated_exception_text = append_entries(exception_text, new_ok)
    updated_nok_text = append_entries(nok_text, new_nok)

    print("Speichere Ausnahmeseite...")
    ok_page.text = updated_exception_text
    ok_page.save(summary="Übernehme bestätigte Redirects (: ok)")

    print("Speichere NOK-Seite...")
    nok_page.text = updated_nok_text
    nok_page.save(summary="Übernehme abgelehnte Redirects (: nok)")

    print("Aktualisiere Quellseite...")
    source_page.text = new_source_text
    source_page.save(summary="Entferne bearbeitete Redirects (: ok / : nok)")

    print("Fertig.")


if __name__ == "__main__":
    main()