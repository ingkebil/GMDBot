#!/usr/bin/env python

"""Download the InChi keys for the biomolecules listed on wikipedia"""

__author__ = "Kenny Billiau"
__copyright__ = "2014, GMD"
__license__ = "GPL v2"
__version__ = "0.1"

import sys
import urllib2
import re
import time
import argparse
import os, errno

cache = True
cache_dir = './cache'
verbal = True
base_url = ''

def msg(msg, nl=True):
    if (verbal):
        if (nl):
            print msg
        else:
            print(msg),

def mkdir_p(path):
    try:
        os.makedirs(path)
        msg('Made "%s"' % path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def save_page(path, filename, lines):
    msg('Saving %s line to "%s" in "%s"' % (len(lines), filename, path))
    mkdir_p(path)
    fh = open('%s/%s' % (path, filename), 'w')
    fh.writelines( "%s\n" % line for line in lines )
    fh.close()

def read_page(path):
    msg('Reading page from "%s"' % path)
    lines = []
    try:
        fh = open(path)
        lines = fh.read().split("\n")
    except:
        sys.stderr.write(sys.exc_info()[0])
        return False
    finally:
        fh.close()
    return lines

def download_page(url):
    msg('Downloading page "%s"' % url, False)
    lines = []
    try:
        res = urllib2.urlopen(url)
        lines = res.read().split("\n")
        msg('... Got %s lines' % len(lines))

        if cache:
            save_page(cache_dir, unurlify(url), lines)
    except:
        sys.stderr.write(sys.exc_info()[0])

    return lines

def unurlify(url):
    return url.replace('/', '_')

def get_page(url):
    path = '%s/%s' % (cache_dir, unurlify(url))
    if cache and os.path.isfile(path):
        lines = read_page(path)
        if lines:
            return lines
    return download_page(url)

def get_molecule_links(lines):
    link_re  = re.compile('href="(.*?)"', re.IGNORECASE)
    title_re = re.compile('title="(.*?)"', re.IGNORECASE)

    res = []

    ulstarted = False
    for line in lines:
        if line == '<ul>':
            ulstarted = True
            continue
        if ulstarted:
            if line == '</ul>':
                ulstarted = False
                continue

            try:
                # get the link
                link = link_re.findall(line)[0]
                title = title_re.findall(line)[0]
            except IndexError:
                continue

            # end of list
            if title == 'Chemical compound':
                break

            res.append( (title, link) )
    return res

def process(lines):
    inchi_re = re.compile('InChi=(.*?)<', re.IGNORECASE)
    inchikey_re = re.compile('Key: *(.*?)<')

    outlines = []

    for title, link in get_molecule_links(lines):

        # skip anchors
        # skip the special pages
        if link.startswith('#') or link.startswith('/w/'):
            continue

        mol_lines = get_page(base_url + link)

        inchi = []
        inchi_key = []
        for mol_line in mol_lines:
            if not len(inchi) > 0:
                inchi = inchi_re.findall(mol_line)
            else:
                inchi_key = inchikey_re.findall(mol_line)
            if len(inchi_key) > 0:
                msg(title + ':' + inchi_key[0])
                outlines.append( (title, inchi_key[0]) )
                break
        time.sleep(1) # wait a sec ...
    return outlines

def main(argv):
    parser = argparse.ArgumentParser(description='Download InChI Keys from Wikipedia')
    parser.add_argument('--url', type=str, dest='wiki_url', help='https://en.wikipedia.org/wiki/List_of_biomolecules', default='https://en.wikipedia.org/wiki/List_of_biomolecules')
    parser.add_argument('--base_url', type=str, dest='base_url', help='https://en.wikipedia.org', default='https://en.wikipedia.org')
    parser.add_argument('--cache', type=bool, dest='cache', help='cache the downloaded pages', default=True)
    parser.add_argument('--cache_dir', type=str, dest='cache_dir', help='cache location', default='./cache')
    parser.add_argument('--out_file', type=str, dest='out_file', help='name of output file', default='keys.txt')
    parser.add_argument('--verbal', type=bool, dest='verbal', help='explain what is happening', default=True)
    args = parser.parse_args(argv)

    # some admin
    global cache
    cache = args.cache
    global cache_dir
    cache_dir = args.cache_dir
    global verbal
    verbal = args.verbal
    global base_url
    base_url = args.base_url


    #try:
    lines = get_page(args.wiki_url)
    processed_lines = process(lines)

    #finally:
    out_path, out_file = os.path.split(args.out_file)
    save_page(out_path, out_file, ("%s:%s" % (line[0], line[1]) for line in processed_lines))


if __name__ == '__main__':
    main(sys.argv[1:])
