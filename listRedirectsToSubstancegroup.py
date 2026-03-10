#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import time


MAX_THREADS = 10


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


def process_article(page):

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

                if target.title() != page.title():

                    problems.append(
                        f"* [[{r.title()}]] → [[{target.title()}]] (zeigt nicht auf [[{page.title()}]])"
                    )

                else:

                    results.append(
                        f"* [[{r.title()}]] → [[{page.title()}]]"
                    )

                if target.isRedirectPage():

                    problems.append(
                        f"* [[{r.title()}]] → [[{target.title()}]] (Redirect-Kette)"
                    )

                if not target.exists():

                    problems.append(
                        f"* [[{r.title()}]] → [[{target.title()}]] (Ziel existiert nicht)"
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

    print("Lade Artikel aus Kategoriebaum...")

    articles = get_articles(site)

    print(f"{len(articles)} Artikel gefunden")

    all_redirects = []
    all_problems = []

    print("Prüfe Redirects parallel...")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:

        futures = {
            executor.submit(process_article, page): page
            for page in articles
        }

        for i, future in enumerate(as_completed(futures), start=1):

            redirects, problems = future.result()

            all_redirects.extend(redirects)
            all_problems.extend(problems)

            if i % 20 == 0:
                print(f"{i}/{len(articles)} Artikel geprüft")

    all_redirects = sorted(set(all_redirects))
    all_problems = sorted(set(all_problems))

    print("Erstelle Wikipedia-Ausgabe...")

    text = "== Redirects auf Stoffgruppenartikel ==\n\n"

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