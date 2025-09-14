This is the repository for the ChemoBot PyWiki sources.

See https://de.wikipedia.org/wiki/Benutzer:ChemoBot for documentation and actions.

Installation and usage of the scripts

* Install python (>=3.13) and make sure python and pip directories are added to the paths
* install git
* clone chemobot (git clone https://github.com/rcp01/ChemoBot.git)
* download necessary side packages 
	pip install certifi charset-normalizer idna importlib_metadata jq mwparserfromhell packaging pip pywikibot regex requests urllib3 wcwidth wikitextparser zipp
* run scripts (you need a pywikibot login)
* update regularly the packets
	pip install --upgrade certifi charset-normalizer idna importlib_metadata jq mwparserfromhell packaging pip pywikibot regex requests urllib3 wcwidth wikitextparser zipp

The scripts can directly be started after installing the necessary packets and adding a `user-password.py` file (see pywikibot documentation).

Current scripts:
* `change_reference_header_in_articles.py`: Replaces section name "Quellen" with "Einzelnachweise".
* `add_order_entry_in_articles.py`: Adds order entry for articles in categories if not available and the page name contains special chemical characters.
* `correct_category_name_of_compound_group_articles.py`: Adds a space in category naming if the article is about compound groups.
* `change_minus_sign_in_articles.py`: Replaces the normal minus sign with the correct one in the names of chemicals for special isomers "(-)-".
* `change_descriptors_in_articles.py`: Changes chemical descriptors to italic.
* `checkCasNumberTemplate.py`: Adds "KeinCasLink" to the template "CASRN" if the compound is not available at "commonchemistry.org".
* `checkPredatory.py`: Checks if sites link to predatory journals.
* `checkPredatoryNames.py`: Checks if sites use predatory journal names as references.
* `checkNameInBox.py`: Lists articles that have a special article name template but no entry for the name in the chemobox template.
* `correctAltSymbolsInProteinBox.py`: Corrects alternative symbols in protein box templates.

Current scripts for management of missing substances:
* `listSubstanceInfosToMissingSubstancesPage.py`: Adds articles containing the "substanzinfo" template to "new articles" if not on the missing or ignore page.
* `listUnknownRedLinksToMissingSubstancesPage.py`: Lists unknown red links to the "missing substances" page.
* `addWikidataToMissingSubstancesPage.py`: Adds Wikidata information to the "missing substances" page.
* `addCasToEntriesFromNewMissingEntriesPage.py`: Adds CAS numbers to entries from the "new missing entries" page.
* `createAdditionalInfoPageForMissingSubstances.py`: Fills additional information about missing articles from the "missing article" page to the "additional info" page.
* `moveKnownEntriesFromRedlinksToMissingEntriesPage.py`: Adds new articles from "new articles" to "missing articles", "ignore articles", or the "variants page".
