#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
"""
parse_medline
"""
from collections import OrderedDict

from bs4 import BeautifulSoup
import requests
import requests_cache
# import html5lib
requests_cache.install_cache()

def parse_medline(url):
    """
    parse a medline link, extracting useful data:
        * contraindications (?)
        * adverse effects
        * symptoms of overdose
    """

    page = requests.get(url)
    bs = BeautifulSoup(page.content)

    a = bs.find('a', {'name':'precautions'})
    precautions = a.find_next('ul')  # TODO
    precautions = precautions.find_all('li')
    precautions = [e.text.strip() for e in precautions]

    a = bs.find('a', {'name': 'side-effects'})
    side_effects = a.find_next('ul') # TODO
    side_effects = side_effects.find_all('li')
    side_effects = [e.text.strip() for e in side_effects]

    a = bs.find('a', {'name':'overdose'})
    overdose_indications = a.find_next('ul') # TODO
    overdose_indications = overdose_indications.find_all('li')
    overdose_indications = [e.text.strip() for e in overdose_indications]

    brand_names = bs.find('div', {'id': 'brand-name'})
    brand_names = brand_names.find_all('li')
    brand_names = [e.text.strip() for e in brand_names]

    brand_name_combs = bs.find('div', {'id': 'brand-name-comb'})
    brand_name_combs = brand_name_combs.find_all('li')
    brand_name_combs = [e.text.strip() for e in brand_name_combs]

    other_names = bs.find('div', {'id': 'other-name-id'})
    other_names = other_names.find_all('li')
    other_names = [e.text.strip() for e in other_names]

    return OrderedDict((
        ('precautions', precautions),
        ('side_effects', side_effects),
        ('overdose_indications', overdose_indications),
        ('brand_names', brand_names),
        ('brand_name_combs', brand_name_combs),
        ('other_names', other_names),
    ))


import unittest
class Test_parse_medline(unittest.TestCase):
    DRUG_INFO_URL = "http://www.nlm.nih.gov/medlineplus/druginfo/meds/a681004.html"
    def test_parse_medline(self):
        url = self.DRUG_INFO_URL
        output = parse_medline(url)
        import pprint
        print(pprint.pformat(output))
        self.assertTrue(output)
        keys = ['precautions', 'side_effects', 'overdose_indications',
                'brand_names', 'brand_name_combs', 'other_names']
        for key in keys:
            self.assertIn(key, output)
        raise NotImplementedError


def main(*args):
    import logging
    import optparse
    import sys

    prs = optparse.OptionParser(usage="%prog : args")

    prs.add_option('-v', '--verbose',
                    dest='verbose',
                    action='store_true',)
    prs.add_option('-q', '--quiet',
                    dest='quiet',
                    action='store_true',)
    prs.add_option('-t', '--test',
                    dest='run_tests',
                    action='store_true',)

    args = args and list(args) or sys.argv[1:]
    (opts, args) = prs.parse_args()

    if not opts.quiet:
        logging.basicConfig()

        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        sys.argv = [sys.argv[0]] + args
        import unittest
        sys.exit(unittest.main())

    if len(args) != 1:
        prs.error("Must specify a URL to parse")

    url = args[0]

    import json
    output = parse_medline(url)
    print( json.dumps( output, indent=2 ) )


if __name__ == "__main__":
    import sys
    sys.exit(main())
