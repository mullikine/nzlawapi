import urllib, urllib2
from bs4 import BeautifulSoup
import re
import datetime
from multiprocessing.dummy import Pool as ThreadPool
import threading
import sys
import importlib
from os import path
import os
from collections import defaultdict

"""
This script scrapes https://www.comlaw.gov.au

It starts on the browse index table, uses asp.net form submission to handle pagination.
For each result, finds the document series, then the for each in the series finds
dates and download links.

"""


start = 'https://www.comlaw.gov.au/Browse/'
series = 'https://www.comlaw.gov.au/Series/%s'
download = 'https://www.comlaw.gov.au/Details/%s/Download'
top_level_sel = '#ctl00_MainContent_pnlBrowse a font'

THREAD_MAX = 10


thread_limiter = [
    threading.BoundedSemaphore(THREAD_MAX),
    threading.BoundedSemaphore(THREAD_MAX),
    threading.BoundedSemaphore(THREAD_MAX)
    ]


def thread_limit(index):
    def apply_decorator(func):
        def func_wrapper(*args, **kwargs):
            thread_limiter[index].acquire()
            try:
                return func(*args, **kwargs)
            finally:
                thread_limiter[index].release()
        return func_wrapper
    return apply_decorator


def get_indices():
    req = urllib2.Request(start)
    response = urllib2.urlopen(req)
    page = response.read()
    soup = BeautifulSoup(page, 'lxml')
    return [start + el.parent['href'] for el in soup.select(top_level_sel)]


@thread_limit(2)
def table_loop(url, headers=None):
    """ Find the 'next' button the asp.net table, recursively yields on each page """
    print 'Open ', url
    if headers:
        data = urllib.urlencode(headers)
        req = urllib2.Request(url, data)
    else:
        req = url
    response = urllib2.urlopen(req)
    soup = BeautifulSoup(response.read(), 'lxml')
    yield soup
    next_button = soup.find('input', class_='rgPageNext')
    if next_button and 'onclick' not in next_button.attrs:
        headers = {}
        for header in soup.find('form', id="aspnetForm").find_all('input'):
            if 'name' in header.attrs and header['type'] != 'submit':
                headers[header['name']] = header.get('value', '')
        headers[next_button['name']] = next_button['value']
        for page in table_loop (url, headers):
            yield page


@thread_limit(1)
def get_document_info(id):
    """ will contain dates before 1900, so must do manually """
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def date(date_string):
        (day, month, year) = date_string.split()
        return datetime.datetime(int(year), months.index(month)+1, int(day))

    req = urllib2.Request(download % id)
    response = urllib2.urlopen(req)
    page = BeautifulSoup(response.read(), 'lxml')
    page.find('ctl00_MainContent_ucItemPane_tdRight')
    result = defaultdict(lambda: None)
    result['id'] = id,
    result['links'] = map(lambda x: x['href'], page.find_all('a', onclick=re.compile("Primary Document Icon")))
    try:
        result['superseded'] = page.select('#ctl00_MainContent_ucItemPane_lblStatus')[0].text == 'Superseded'
    except AttributeError:
        pass
    try:
        result['prepared_date'] = date(page.select('#ctl00_MainContent_ucItemPane_trPreparedDate td:nth-of-type(2)')[0].text.strip())
    except IndexError:
        pass
    try:
        result['published_date'] = date(page.select('#ctl00_MainContent_ucItemPane_trPublished td:nth-of-type(2)')[0].text.strip())
    except IndexError:
        pass
    try:
        result['start_date'] = date(page.select('#ctl00_MainContent_ucItemPane_trStartDate td:nth-of-type(2)')[0].text.strip())
    except IndexError:
        pass
    try:
        result['end_date'] = date(page.select('#ctl00_MainContent_ucItemPane_trEndDate td:nth-of-type(2)')[0].text.strip())
    except IndexError:
        pass

    print 'Document Info: ', result

    return result

def add_to_db(result):
    db = connect_db_config(config)
    with db.cursor() as cur:
        cur.execute('delete from comlaw_info where id = %(id)s', result)
        cur.execute("""insert into comlaw_info """
            """(id, superseded, prepared_date, published_date, start_date, end_date, links, series) values"""
            """(%(id)s, %(superseded)s, %(prepared_date)s, %(published_date)s, %(start_date)s, %(end_date)s, %(links)s, %(series)s)""",
            result)
    db.commit()
    db.close()


@thread_limit(0)
def get_series(id):
    results = []
    for page in table_loop(series % id):
        ids = map(lambda x: x.text, page.select('#ctl00_MainContent_SeriesCompilations_RadGrid1_ctl00 > tbody > tr > td:nth-of-type(2)'))
        """ If has no previous versions, will not have table """
        if not len(ids):
            ids = [id]
        print "Series", ids
        pool = ThreadPool(THREAD_MAX)
        _results = pool.map(get_document_info, ids)
        pool.close()
        pool.join()
        for _result in _results:
            _result['series'] = id
            add_to_db(_result)
            results.append(_result)
    return results


def open_index(url):
    results = []
    for page in table_loop(url):
        buttons = page.find_all('input', id=re.compile('_btnSeries$'))
        ids = map(lambda x: x['onclick'].split(',')[4].split('/')[-1].replace('"', ''), buttons)
        print 'Found %d ids' % len(ids), ids
        pool = ThreadPool(THREAD_MAX)
        _results = pool.map(get_series, ids)
        pool.close()
        pool.join()
        results += _results
    return results


if __name__ == '__main__':
    if not len(sys.argv) > 1:
        raise Exception('Missing configuration file')
    sys.path.append(os.getcwd())
    config = importlib.import_module(sys.argv[1].replace('.py', ''), 'parent')
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from db import connect_db_config
    #indices = [get_indices()]
    indices = ['https://www.comlaw.gov.au/Browse/Results/ByTitle/Acts/Current/Wo/0']
    try:
        for index in indices:
            print open_index(index)
    except KeyboardInterrupt:
        print 'Exiting early'
        sys.exit()
