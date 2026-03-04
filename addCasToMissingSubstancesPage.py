#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import pywikibot

CAS_PROPERTY = "P231"


def get_cas_from_wikidata(repo, qid):
    """Liest CAS-Nummer (P231) aus Wikidata."""
    try:
        item = pywikibot.ItemPage(repo, qid)
        item.get()

        if CAS_PROPERTY in item.claims:
            claim = item.claims[CAS_PROPERTY][0]
            return claim.getTarget()

    except Exception as e:
        print(f"Fehler bei {qid}: {e}")

    return None


def process_page():
    site = pywikibot.Site("de", "wikipedia")
    repo = site.data_repository()

    page = pywikibot.Page(site, "Wikipedia:Redaktion Chemie/Fehlende Substanzen")
    #page = pywikibot.Page(site, "Benutzer:ChemoBot/Tests/Fehlende Substanzen")
    
    text = page.text

    changed = False
    total_checked = 0
    total_added = 0

    pattern = re.compile(
        r"(\[\[[^\]]+\]\])\s*"
        r"\(\s*"
        r"(?:(\d{2,7}-\d{2}-\d)\s*,\s*)?"
        r"\[\[:d:(Q\d+)\|wd\]\]"
        r"\s*\)",
        re.UNICODE
    )

    def replace_entry(match):
        nonlocal changed, total_checked, total_added

        total_checked += 1

        article = match.group(1)
        cas = match.group(2)
        qid = match.group(3)

        print(f"{total_checked}. Prüfe {article} ({qid})")

        # Wenn CAS bereits vorhanden → nichts tun
        if cas:
            print("   → CAS bereits vorhanden")
            return match.group(0)

        cas_from_wd = get_cas_from_wikidata(repo, qid)

        if cas_from_wd:
            print(f"   → CAS ergänzt: {cas_from_wd}")
            changed = True
            total_added += 1
            return f"{article} ({cas_from_wd}, [[:d:{qid}|wd]])"
        else:
            print("   → Keine CAS in Wikidata gefunden")
            return match.group(0)

    new_text = pattern.sub(replace_entry, text)

    print("\n--- Zusammenfassung ---")
    print(f"Geprüft: {total_checked}")
    print(f"Ergänzt: {total_added}")

    if changed:
        summary = f"Ergänze {total_added} fehlende CAS-Nummern aus Wikidata (P231)"
        page.text = new_text
        page.save(summary=summary)
        print("Seite gespeichert.")
    else:
        print("Keine Änderungen notwendig.")


if __name__ == "__main__":
    process_page()