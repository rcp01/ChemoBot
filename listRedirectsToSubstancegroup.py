#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import time

SOURCE_PAGE = "Benutzer:Rjh/Test"
OK_PAGE = "Benutzer:Rjh/Test3"
NOK_PAGE = "Benutzer:Rjh/Test4"

def load_exceptions(site, title):
    """Lädt Ausnahmen exakt im Ausgabeformat"""

    page = pywikibot.Page(site, title)

    try:
        text = page.get()
    except Exception as e:
        print(f"Fehler beim Laden der Ausnahmen: {e}")
        return set()

    exceptions = set()

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Falls jemand doch "*" davor schreibt → entfernen
        if line.startswith("*"):
            line = line[1:].strip()

        exceptions.add(line)

    print(f"{len(exceptions)} Ausnahmen geladen")

    return exceptions

def get_articles(site):
    """Alle Artikel aus Kategorie Stoffgruppe und Unterkategorien holen"""

    cat = pywikibot.Category(site, "Kategorie:Stoffgruppe")

    gen = pagegenerators.CategorizedPageGenerator(
        cat,
        recurse=True,
        namespaces=[0]
    )

    pages = []
    seen = set()

    for page in gen:
        if page.title() not in seen:
            pages.append(page)
            seen.add(page.title())

    return pages


def process_article(page, exceptions):

    results = []
    problems = []

    try:

        refs = page.getReferences(
            follow_redirects=False,
            filter_redirects=True,
            namespaces=[0]
        )

        for r in refs:

            try:

                target = r.getRedirectTarget()

                # 👉 String wie in Ausgabe erzeugen
                output_line = f"[[{r.title()}]] → [[{target.title()}]]"

                # 👉 IGNORIEREN wenn in Ausnahmen
                if output_line in exceptions:
                    continue

                if target.title() != page.title():

                    problems.append(
                        f"* {output_line} (zeigt nicht auf [[{page.title()}]])"
                    )

                else:

                    results.append(
                        f"* [[{r.title()}]] → [[{page.title()}]]"
                    )

                if target.isRedirectPage():

                    problems.append(
                        f"* {output_line} (Redirect-Kette)"
                    )

                if not target.exists():

                    problems.append(
                        f"* {output_line} (Ziel existiert nicht)"
                    )

            except Exception as e:

                problems.append(
                    f"* [[{r.title()}]] Fehler beim Prüfen: {e}"
                )

    except Exception as e:

        problems.append(
            f"* Fehler bei [[{page.title()}]]: {e}"
        )

    return results, problems

def main():

    start = time.time()

    site = pywikibot.Site("de", "wikipedia")

    known_redirects = load_exceptions(site, OK_PAGE) + load_exceptions(site, NOK_PAGE)

    print("Lade Artikel aus Kategoriebaum...")

    articles = get_articles(site)

    print(f"{len(articles)} Artikel gefunden")

    all_redirects = []
    all_problems = []

    print("Prüfe Redirects...")

    for i, page in enumerate(articles, start=1):

        redirects, problems = process_article(page, known_redirects)

        all_redirects.extend(redirects)
        all_problems.extend(problems)

        if i % 20 == 0:
            print(f"{i}/{len(articles)} Artikel geprüft")

    all_redirects = sorted(set(all_redirects))
    all_problems = sorted(set(all_problems))

    print("Erstelle Wikipedia-Ausgabe...")

    text = "__TOC__\n== Redirects auf Stoffgruppenartikel ==\n\n"

    text += "\n".join(all_redirects)

    text += "\n\n== Problematische Redirects ==\n\n"

    if all_problems:
        text += "\n".join(all_problems)
    else:
        text += "Keine gefunden."

    page = pywikibot.Page(site, "Benutzer:Rjh/Test")

    page.text = text

    page.save(summary="Liste von Redirects auf Stoffgruppenartikel (Bot)")

    print("Fertig.")

    runtime = round(time.time() - start, 1)

    print(f"Laufzeit: {runtime} Sekunden")


if __name__ == "__main__":
    main()