from db import get_db
from util import CustomException, tohtml, etree_to_dict
from definitions import populate_definitions, process_definitions
from traversal import cull_tree, find_definitions, find_part_node, find_section_node, find_schedule_node, find_node_by_query, find_document_id_by_govt_id
from lxml import etree
from copy import deepcopy
import json
import os


class Act(object):
    def __init__(self, id, tree):
        self.id = id
        self.tree = tree
        self.title = get_title(self.tree)
        self.hook_match = '/*/*/*/*/*'
        self.parts = {}

    def calculate_hooks(self):
        html = tohtml(self.tree)
        i = 0
        for e in html.xpath(self.hook_match):
            length = len(etree.tostring(e))
            if length > 1000:
                e.attrib['data-hook'] = '%d' % i
                e.attrib['data-hook-length'] = '%d' % length
                self.parts[e.attrib['data-hook']] = deepcopy(e)
                e[:] = []
                i += 1
        self.skeleton = etree_to_dict(html.getroot())

    def select(self, requested):
        return [self.parts[i] for i in requested]


def get_title(tree):
    return etree.tostring(tree.xpath('/act/cover/title|/regulation/cover/title')[0], method="text")


def get_act(act, db=None):
    with (db or get_db()).cursor() as cur:
        query = """select document from latest_instruments where
        where lower(replace(title, ' ', '')) = lower(%(act)s) """
        cur.execute(query, {'act': act})
        try:
            return etree.fromstring(cur.fetchone()[0])
        except:
            raise CustomException("Act not found")


def get_act_exact(act, id=None, db=None):
    with (db or get_db()).cursor() as cur:
        query = """
            select document from latest_instruments
            where (%(act)s is  null or title = %(act)s) and (%(id)s is null or id =  %(id)s)
             """
        cur.execute(query, {'act': act, 'id': id})
        try:
            result = cur.fetchone()
            return etree.fromstring(result[0])
        except:
            raise CustomException("Act not found")


import re
from xml.dom import minidom
#TODO finish
def process_act_links(tree, db=None):
    return tree
    with (db or get_db()).cursor() as cur:
        query = """
            SELECT title, source_id FROM
                acts WHERE latest_version = True
                UNION
            SELECT title, source_id
                regulations WHERE latest_version = True
            """
        cur.execute(query)
        results = {v[1]: v[0] for v in cur.fetchall()}
        regex = re.compile('(%s)' % results.values().join('|'))
        domxml = minidom.parseString(etree.tostring(tree, encoding='UTF-8', method="html"))
        nodes = tree.xpath('//*[text()]')
        for node in nodes:
            if node.text.matches(regex):
                pass

    return tree


def update_definitions(act_name, id=None, db=None):
    tree = get_act_exact(act_name, id, db)
    _, definitions = populate_definitions(get_act_exact('Interpretation Act 1999'))
    tree = process_act_links(tree, db)
    tree, definitions = process_definitions(tree, definitions)
    with (db or get_db()).cursor() as cur:
        query = """UPDATE documents d SET processed_document =  %(doc)s
                    FROM latest_instruments s
                    WHERE d.id = s.id and (%(act)s is null or title = %(act)s) and (%(id)s is null or d.id =  %(id)s) returning d.id"""
        cur.execute(query, {
            'act': act_name,
            'id': id,
            'doc': etree.tostring(tree, encoding='UTF-8', method="html"),
        })
        id = cur.fetchone()[0]
        args_str = ','.join(cur.mogrify("(%s,%s,%s)", (id, x[0], json.dumps(x[1]))) for x in definitions.render().items())
        cur.execute("DELETE FROM definitions where document_id = %(id)s", {'id': id})
        cur.execute("INSERT INTO definitions (document_id, key, data) VALUES " + args_str)

        (db or get_db()).commit()
    return tree, definitions.render()


def get_act_object(act_name=None, id=None, db=None, replace=False):
    with (db or get_db()).cursor() as cur:
        query = """SELECT id, processed_document FROM latest_instruments
                where (%(act)s is null or title= %(act)s) and (%(id)s is null or id =  %(id)s)
            """
        if not replace:
            cur.execute(query, {'act': act_name, 'id': id})
            result = cur.fetchone()
            if not result:
                raise CustomException('Act not found')
        if replace or not result[1]:
            tree, _ = update_definitions(act_name, id, db=db)
        else:
            tree = etree.fromstring(result[1])

        return Act(id=result[0], tree=tree)


def act_skeleton_response(act):
    return {
        'skeleton': act.skeleton,
        'html_contents_page': etree.tostring(tohtml(act.tree, os.path.join('xslt', 'contents.xslt')), encoding='UTF-8', method="html"),
        'title': act.title,
        'parts': {},
        'id': act.id,
        'type': 'instrument',
        'partial': True
    }


def act_full_response(act):
    return {
        'html_content': etree.tostring(tohtml(act.tree), encoding='UTF-8', method="html"),
        'html_contents_page': etree.tostring(tohtml(act.tree, os.path.join('xslt', 'contents.xslt')), encoding='UTF-8', method="html"),
        'title': act.title,
        'id': act.id,
        'type': 'instrument'
    }


def act_fragment_response(act):
    return {
        'html': etree.tostring(tohtml(act.tree), encoding='UTF-8', method="html"),
        'title': act.title,
        'id': act.id,
    }

def act_response(act):
    if len(act.tree.xpath('.//*')) > 50000: # move magic number somewhere
        return act_skeleton_response(act)
    else:
        return act_full_response(act)


def act_part_response(act, parts):
    def render_inner(el):
        s = ''
        for node in el.xpath('node()'):
            if isinstance(node, basestring):
                s += node
            else:
                s += etree.tostring(node, encoding='UTF-8', method="html")
        return s

    return {
        'parts': {act.parts[e].attrib['data-hook']: render_inner(act.parts[e]) for e in parts or [] }
    }


def format_response(args, result):
    if args.get('format', 'html') == 'json':
        return {'content': result, 'act_name': args['act_name']}
    else:
        return {'html_content': etree.tostring(result, encoding='UTF-8', method="html"), 'act_name': args['act_name']}


def get_act_node_by_id(node_id):
    id = find_document_id_by_govt_id(node_id)
    act = get_act_object(id=id)
    """ if the node is root, just get cover """
    if act.tree.attrib['id'] == node_id:
        act.tree = cull_tree(act.tree.xpath('.//cover'))
    else:
        act.tree = cull_tree(act.tree.xpath('.//*[@id="' + node_id + '"]'))
    return act_fragment_response(act)


def query_act(args):
    act = get_act_object(act_name=args.get('act_name', args.get('title')), id=args.get('id'))
    act.calculate_hooks()
    search_type = args.get('find')
    if search_type == 'full':
        pass
    elif search_type == "more":
        return act_part_response(act, args.getlist('requested_parts[]'))
    else:
        query = args.get('query')
        if not query:
            raise CustomException('Query missing')
        if search_type == 'search':
            act.tree = find_node_by_query(act.tree, query)
        elif search_type == 'section':
            act.tree = find_section_node(act.tree, query)
        elif search_type == 'part':
            act.tree = find_part_node(act.tree, query)
        elif search_type == 'schedule':
            act.tree = find_schedule_node(act.tree, query)
        elif search_type == 'definitions':
            act.tree = find_definitions(act.tree, query)
        else:
            raise CustomException('Invalid search type')
        act.tree = cull_tree(act.tree)
    return act_response(act)


def query_acts(args):
    search_type = args.get('acts_find')
    #query = args.get('query')
    if search_type == 'contains':
        #result = act_full_search(query)
        raise CustomException('Not Implemented')
    elif search_type == 'definitions':
        raise CustomException('Not Implemented')
    else:
        raise CustomException('Invalid search type')
    return []
