# ChemoBot
This is the repository for the ChemoBot PyWiki sources.

The scripts can directly started after installation of the pywikibot (via "pip install pywikibot") and adding an "user-password.py" file (see pywikibot documentation).

Current scripts:
* change_reference_header_in_articles.py : replaces section name "Quellen" by "Einzelnachweise"
* add_order_entry_in_articles.py : Add order entry for articles in categories if not available and page name contains special chemical characters
* correct_category_name_of_compound_group_articles.py : Add space in category naming, if this is an article about compound groups
* change_minus_sign_in_articles.py : replace normal minus sign by correct one in name of chemicals for special isomers "(-)-"
* change_descriptors_in_articles.py : change chemical descriptors to italic
* CheckCasNumberTemplate.py : Add "KeinCasLink" to template "CASRN" if compound is not available at "commonchemistry.org"
* CheckPredatory.py : Check if sites links to predatory journals
* CheckPredatoryNames.py : Check if sites uses predatory journal names as reference
* MoveKnownEntriesFromRedlinksToMissingEntriesPage.py : add new articles from "new articels" to "missing articles", "ignore articles" or "variants page"
* WorkOnSubstanceInfos.py : Add articles which contains "substanzinfo" template to "new articles" if not on missing or ignore page
* CheckNameInBox.py : Lists articles which have special article name template but no entry for name in chemobox template
* list_red_links.py : Add missing articles (redlinks) to "new article" page
* create_hot_list.py : Fill additional information about missing articles from "missing article" page to "additional info" page