#!/usr/bin/env python

"""Bot to do assisted editing of a list of biomolecules on wikipedia"""

__author__ = "Kenny Billiau"
__copyright__ = "2014, GMD"
__license__ = "GPL v2"
__version__ = "0.1"

import sys
import re
import openpyxl as px
import mwclient


bot_name = 'GMDBot'


gmd_link = 'http://gmd.mpimp-golm.mpg.de/Spectrums/%s.aspx'
gmd_title = '%s MS Spectrum'
wiki_markup = '* [%s %s]'  # wiki-link + descr
wiki_external_links = '==External links==\r\n'

regexp_ab = re.compile(r'\{\{(nobots|bots\|(allow=none|deny=.*?' + bot_name + r'.*?|optout=all|deny=all))\}\}')
 
def allow_bots(text):
    return not regexp_ab.search(text)

def get_molecules_from_xlsx(fn):
    workbook = px.load_workbook(fn)
    page = workbook.get_sheet_by_name(name='Wikipedia')

    res = []
    for row in page.range('A7:E208'):
        if row[4].value not in ('#N/A', None):
            res.append( (row[0].value, row[4].value) ) # add the metabolite name, GMD spectrum id

    return res

def main(argv):

    links = []
    if len(argv) != 0:
        links = get_molecules_from_xlsx(argv[0])

    # compile some regex's
    ref_list_re = re.compile(r'==\s*References\s*==.*?\n\n', re.I | re.S) # dotall so we newlines match with .
    ext_links_re = re.compile(r'==\s*External links.*?==', re.I)


    # log into wikipedia
    site = mwclient.Site('en.wikipedia.org')
    #site.login(bot_name, argv[1])

    for metabolite in links:
        title = metabolite[0]
        metabolite_id = metabolite[1].lower()
        print(title + ' '),

        # Edit page
        page = site.Pages[title].resolve_redirect()
        text = page.edit()

        if not allow_bots(text): # skip when we find this page doesn't allow edits by bots
            continue

        # ok, let's try to add this
        link_m = re.search(metabolite_id, text, re.I)
        if link_m is None:
            ext_links_m = ext_links_re.search(text)
            if ext_links_m is None:
                ref_list_m = ref_list_re.search(text)
                if ref_list_m is not None:
                    # add External Links
                    text = text[:ref_list_m.end()] + \
                           wiki_external_links + \
                           wiki_markup % (gmd_link % metabolite_id, gmd_title % title) + \
                           '\r\n' + \
                           text[ref_list_m.end():] + \
                           '\r\n'

            else:
                # add link
                # TODO might be the case that there is or is not a list. We presume now there is a list and we add an item
                text = text[:ext_links_m.end()] + \
                       '\r\n' + \
                       wiki_markup % (gmd_link % metabolite_id, gmd_title % title) + \
                       text[ext_links_m.end():] + \
                       '\r\n'
            
            print text
            ch = sys.stdin.readline()
            if ch.rstrip().lower() == 'y':
                print page.save(text, summary = 'Added Mass Spectrometry link to the Golm Metabolome Database')
                print 'SAVED'
            else:
                print 'SKIPPED'
        else:
            print 'ALREADY PRESENT'

if __name__ == '__main__':
    main(sys.argv[1:])
