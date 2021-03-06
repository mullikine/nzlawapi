# -*- coding: utf-8 -*-
from __future__ import division
from bs4 import BeautifulSoup, Tag, NavigableString
import re
import sys
import datetime
from tempfile import mkdtemp
import shutil
from flask import current_app
from util import indexsplit
import copy
from pdfs import generate_parsable_xml
from transform.intituling import generate_intituling
from transform.body import generate_body, generate_footer, tweak_intituling_interface
from transform.common import remove_empty_elements
from lxml import etree

# source
"""https://forms.justice.govt.nz/solr/jdo/select?q=*:*&rows=500000&fl=FileNumber%2C%20Jurisdiction%2C%20MNC%2C%20Appearances%2C%20JudicialOfficer%2C%20CaseName%2C%20JudgmentDate%2C%20Location%2C%20DocumentName%2C%20id&wt=json&json.wrf=json%22%22%22"""


def join_adjacent_styles(soup):
    for el in soup.find_all(['strong', 'emphasis'])[:-1][::-1]:
        if isinstance(el.next_sibling, Tag) and el.next_sibling.name == el.name:
            for content in el.next_sibling.contents:
                last = el.contents[-1]
                if isinstance(content, NavigableString) and isinstance(last, NavigableString):
                    last.replace_with('%s%s' % (last, content))
                else:
                    el.append(content)
            el.next_sibling.decompose()

    return soup


def massage_xml(soup, debug):
    if debug:
        print soup.prettify().encode('utf-8')
    soup = remove_empty_elements(soup)
    soup = join_adjacent_styles(soup)
    soup = tweak_intituling_interface(soup)
    intituling = generate_intituling(soup)
    body = generate_body(soup)
    footer = generate_footer(soup)
    case = soup.new_tag('case')
    case.append(intituling)
    if body:
        case.append(body)
    if footer:
        case.append(footer)
    case = remove_empty_elements(case)
    if debug:
        print case.prettify().encode('utf-8')
    return case


def process_case(path, debug=False):
    tmp = mkdtemp()
    xml = generate_parsable_xml(path, tmp)
    soup = BeautifulSoup(xml, features='lxml-xml')
    results = massage_xml(soup, debug)
    shutil.rmtree(tmp)
    return re.sub(' +', ' ', results.encode())


def validate_case(case):
    validation_errors = []
    if case.find('.//court-file') is None:
        validation_errors.append('No Court-file')
    if case.find('.//parties') is None and case.find('.//matters') is None:
        validation_errors.append('No Parties or Matters')

    if case.find('.//full-citation') is None:
        validation_errors.append('No full Citation')

    elif len(case.find('.//full-citation').text) < 20:
        validation_errors.append('Full Citation too short')
    if case.find('.//waistband') is None:
        validation_errors.append('No Waistband')
    label = 1
    if case.find('body') is not None:
        for p in case.findall('body/paragraph'):
            # can reset to 1, in appendixes
            if p.find('label').text == '1':
                label = 1
            if p.find('label').text != ('%d' % label):
                validation_errors.append('Odd ordering of paragraphs')
                break
            label += 1
    return validation_errors


if __name__ == '__main__':
    import sys
    import importlib
    import os
    from os import listdir
    import os.path as path
    from os.path import isfile, join
    if not len(sys.argv) > 1:
        raise Exception('Missing configuration file')
    sys.path.append(os.getcwd())
    config = importlib.import_module(sys.argv[1].replace('.py', ''), 'parent')
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    offset = 71
    for i, f in enumerate(listdir(config.CASE_DIR)[offset:]):
        if isfile(join(config.CASE_DIR, f)) and f.endswith('.pdf'):
            try:
                result = process_case(join(config.CASE_DIR, f))
                errors = validate_case(etree.fromstring(result))
                if errors:
                    print 'Error: (%d) ' % (i + offset), f
                    print errors
            except Exception, e:
                print 'Error: (%d) ' % (i + offset), f
                print 'Cant process'