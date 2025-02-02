#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pywikibot

if __name__ == "__main__":
    site = pywikibot.Site('de', 'wikipedia')  
    page = pywikibot.Page(site, "Benutzer:Rjh/Test")
    # page.save(summary="ChemoBot: Test of Botflag on change ", minor=False)
    # page.save(summary="ChemoBot: Test of Botflag on change", minor=False, bot=False)
    page.text = page.text + " Bot Change "
    page.save(summary="ChemoBot: Test of Botflag on change", minor=True, bot=True)
