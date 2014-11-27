from bs4 import BeautifulSoup
import os
import json 
import re
import pprint

path = '/Users/josh/legislation_archive/justice_trial'
json_path = '/Users/josh/legislation_archive/justice.json'

with open(json_path) as f:
	json_data = json.loads(f.read())

def next_tag(el, name):
	el = el.next_sibling
	while  el.name != name:
		el = el.next_sibling
	return el

def prev_tag(el, name):
	el = el.previous_sibling
	while  el.name != name:
		el = el.previous_sibling
	return el


def get_info(doc_id, json_data):
	for j in json_data['response']['docs']:
		if j['DocumentName'] == doc_id + '.pdf':
			return j

def get_page_one(soup):
	return soup.select('body > a[name="1"]')[0]


def neutral_cite(soup):
	return neutral_cite_el(soup).contents[0]

def neutral_cite_el(soup):
	reg = re.compile(r'\[(\d){4}\] ([A-Z]+) (\d+)')
	el = next_tag(get_page_one(soup), 'div')
	el = [e for e in el.select('div  span') if reg.match(e.text)][0]
	return el


def court_file(soup):
	cite = neutral_cite_el(soup)
	el = prev_tag(cite.parent.parent, 'div')
	el = el.find('span')
	return el.contents[0]

def full_citation(soup):
	el = next_tag(get_page_one(soup), 'div').select('div')[0].find('span')
	return el.contents[0]

def court(soup):
	el = next_tag(get_page_one(soup), 'div')
	reg = re.compile(r'.*OF NEW ZEALAND$')
	el = [e for e in el.select('div  span') if reg.match(e.text)][0]
	next_el = next_tag(el.parent.parent, 'div').find('span')
	result = [el.text]
	if next_el.text != court_file(soup):
		result +=  [next_el.text]
	return result

def consecutive_align(el):
	results = []
	position = re.search(r'.*(left:\d+).*', el.attrs['style']).group(1)
	while position in el.attrs['style']:
		results.append(el.text)
		el = next_tag(el, 'div')
	return results

def parse_between(soup, el):
	between_el = [e for e in el.find_all('span') if e.text == 'BETWEEN'][0].parent.parent
	plantiff = []
	defendant = []
	between_el = next_tag(between_el, 'div')
	while between_el.text != 'AND':
		plantiff.append(between_el.text)
		between_el = next_tag(between_el, 'div')
		

	between_el = next_tag(between_el, 'div')
	defendant = consecutive_align(between_el)

	return {
		'plantiff': plantiff,
		'defendant': defendant
	}
			

def parse_versus(soup, el):
	# must be x v y
	plantiff = []
	defendant = []	
	v = [e for e in el.find_all('span') if e.text == 'v'][0].parent.parent
	# plantiff is every until neutral citation
	between_el = prev_tag(v, 'div')
	cite = neutral_cite(soup)
	while between_el.text != cite:
		plantiff = [between_el.text] + plantiff
		between_el = prev_tag(between_el, 'div')
	# defendant is everything until no more capitals
	between_el = next_tag(v, 'div')
	while between_el.text and between_el.text.upper() == between_el.text:
		defendant += [between_el.text]
		between_el = next_tag(between_el, 'div')
	return {
		'plantiff': plantiff,
		'defendant': defendant
	}


def parties(soup):
	el = next_tag(get_page_one(soup), 'div')
	if any([e for e in el.find_all('span') if e.text == 'BETWEEN']):
		return parse_between(soup, el)
	else:
		return parse_versus(soup, el)

def judgment_el(soup):
	judgement_strings = ['Judgment:', 'Sentence:']
	el = next_tag(get_page_one(soup), 'div')
	return next_tag([e for e in el.find_all('span') if e.text in judgement_strings][0].parent.parent, 'div')

def judgment(soup):
	return judgment_el(soup).text

def waistband(soup):
	return next_tag(judgment_el(soup), 'div').text

def counsel(soup):
	counsel_strings = ['Counsel:', 'Appearances:']
	el = next_tag(get_page_one(soup), 'div')
	counsel = next_tag([e for e in el.find_all('span') if e.text in counsel_strings][0].parent.parent, 'div')
	return consecutive_align(counsel)

def is_appeal(info):
	return re.compile('.*NZCA*').match(info['neutral_cite'])

def appeal_result(soup):
	el = next_tag(next_tag(judgment_el(soup), 'div'), 'div')
	results = {}
	position = re.search(r'.*(left:\d+).*', el.attrs['style']).group(1)
	text_re = re.compile('.*[a-zA-Z]+.*')
	while position in el.attrs['style']:
		key = el.text
		if not text_re.match(key):
			break
		el = next_tag(el, 'div')
		results[key] = el.text
		el = next_tag(el, 'div')
	return results	

def process_file(filename):
	#print get_info(filename.replace('.html', ''), json_data)
	with open(os.path.join(path, filename)) as f:
		soup = BeautifulSoup(f.read())

		results = {
			'neutral_cite': neutral_cite(soup),
			'court_file': court_file(soup),
			'court': court(soup),
			'full_citation': full_citation(soup),
			'parties': parties(soup),
			'counsel': counsel(soup),
			'judgment': judgment(soup),
			'waistband': waistband(soup)
		}
		if is_appeal(results):
			results['appeal_result'] = appeal_result(soup)
		pprint.pprint(results)
		print

for f in os.listdir(path):
	if f.endswith('.html'):
		process_file(f)
		#break