#!/usr/bin/env python

"""Check if a '(data page)' for a biomolecule exists"""

__author__ = "Kenny Billiau"
__copyright__ = "2014, GMD"
__credits__ = "Kenny Billiau"
__license__ = "GPL v2"
__version__ = "0.1"

import sys
import urllib2
import re
import downloadinchi as inchi
import openpyxl as px
import urllib

def get_molecules_from_xlsx(fn):
    workbook = px.load_workbook(fn)
    page = workbook.get_sheet_by_name(name='Wikipedia')

    res = []
    for row in page.range('A7:E208'):
        if row[4].value not in ('#N/A', None):
            res.append(row[0].value)

    return res

def main(argv):

    links = []
    if len(argv) == 0:
        lines = inchi.get_page('https://en.wikipedia.org/wiki/List_of_biomolecules')
        links = inchi.get_molecule_links(lines)
    else:
        links = get_molecules_from_xlsx(argv[0])

    pageid_re = re.compile('pageid')
    for title in links:
        print(title + ' '),
        url = urllib2.urlopen("https://en.wikipedia.org/w/api.php?action=query&format=yaml&titles=%s" % urllib.quote(title + '_(data_page)'))
        lines = url.read()

        if len(pageid_re.findall(lines)) > 0:
            print 'found'
        else:
            print 'NOT FOUND'

if __name__ == '__main__':
    main(sys.argv[1:])
