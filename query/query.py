from acts.acts import query_instrument
from acts.queries import get_references, get_versions, get_section_references
from cases.cases import get_full_case, get_case_info, case_search
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from util import CustomException
from security.auth import require_auth
from db import get_db
import psycopg2
import re


Query = Blueprint('query', __name__, template_folder='templates')


@Query.route('/article_auto_complete')
@require_auth
def article_auto_complete():
    try:
        db = get_db()
        with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                select name, id, type, find, query  from titles
                   where name ilike '%%'||%(query)s||'%%' order by year desc limit 50;
                """, {'query': request.args.get('query')})
            return jsonify({'results': cur.fetchall()})
    except Exception, e:
        return jsonify(error=str(e))


@Query.route('/act_search_id/<string:query>')
@require_auth
def search_by_id(query):
    status = 200
    try:
        result = get_act_node_by_id(query)
    except Exception, e:
        result = {'error': str(e)}
        status = 500
    return jsonify(result), status


@Query.route('/definition/<int:document_id>/<string:key>')
@require_auth
def get_definition_route(document_id, key):
    status = 200
    try:
        result = get_definition(document_id, key)
    except Exception, e:
        result = {'error': str(e)}
        status = 500
    return jsonify(result), status


@Query.route('/link/<string:key>')
@Query.route('/link/<string:doc_type>/<string:key>')
@require_auth
def get_link_route(doc_type=None, key=None):
    status = 200
    try:
        if doc_type is None or doc_type == 'instrument':
            result = query_instrument({'find': 'preview', 'id': key})
        else:
            raise CustomException("Can't locate link information")
    except Exception, e:
        result = {'error': str(e)}
        status = 500
    return jsonify(result), status


@Query.route('/references/<int:document_id>')
@require_auth
def get_references_route(document_id):
    status = 200
    try:
        result = get_references(document_id)
    except Exception, e:
        result = {'error': str(e)}
        status = 500
    return jsonify(result), status


@Query.route('/section_references')
@require_auth
def get_section_references_route():
    status = 200
    try:
        result = get_section_references(request.args.getlist('govt_ids[]'))
    except Exception, e:
        result = {'error': str(e)}
        status = 500
    return jsonify(result), status


@Query.route('/versions/<int:document_id>')
@require_auth
def get_versions_route(document_id):
    status = 200
    try:
        result = get_versions(document_id)
    except Exception, e:
        result = {'error': str(e)}
        status = 500
    return jsonify(result), status


def get_definition(document_id, key):
    with get_db().cursor() as cur:
        cur.execute('SELECT data FROM definitions WHERE document_id=%(id)s and key=%(key)s', {
            'id': document_id,
            'key': key
        })
        return cur.fetchone()[0]





def query_case(args):
    case = args.get('title')
    if case and args.get('validator'):
        return get_case_info(case)
    if case:
        return get_full_case(case)
    # TODO id
    if args.get('id'):
        return get_full_case(id=args.get('id'))
    raise CustomException('Invalid search type')


def query_cases(args):
    query = args.get('query')
    if args.get('find') == 'id':
        return get_full_case(id=query)
    if not query:
        raise CustomException('Query missing')
    results = case_search(re.escape(args.get('query', '')))
    return {'results': results, 'title': 'Search: %s' % query}


def year_query(args):
    if '-' in args.get('year'):
        years = args.get('year').split('-')
        return {
            "range": {
                "year": {
                    "gte": years[0].strip(),
                    "lte": years[1].strip()
                }
            }}
    else:
        return {
            "query_string": {
                "query": args.get('year'),
                "fields": ['year']
            }
        }


def contains_query(args):
    if args.get('contains_type') == 'all_words':
        return {
            "simple_query_string": {
                "query": args.get('contains'),
                "fields": ['document'],
                "default_operator": 'AND'
            }}
    if args.get('contains_type') == 'any_words':
        return {
            "simple_query_string": {
                "query": args.get('contains'),
                "fields": ['document'],
                "default_operator": 'OR'
            }}
    if args.get('contains_type') == 'exact':
        return {
            "match_phrase": {
                "document": args.get('contains')
            }}


def query_all(args):
    query = args.get('query')
    es = current_app.extensions['elasticsearch']
    offset = args.get('offset')
    results = es.search(
        index="legislation",
        body={
            "from": offset, "size": 25,
            "fields": ["id", "title", "full_citation"],
            "sort": [
                "_score",
            ],
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "full_citation^3", "document"]
                }
            },
            "highlight": {
                "pre_tags": ["<span class='search_match'>"],
                "post_tags": ["</span>"],
                "fields": {
                    "document": {},
                    "full_citation": {},
                    "title": {}
                }
            }
        })
    return {'type': 'search', 'search_results': results['hits'], 'title': 'Search: %s' % query}


def query_case_fields(args):
    must = []
    fields = {}
    try:
        if args.get('full_citation'):
            must.append({"simple_query_string": {
                "query": args.get('full_citation'),
                "fields": ['full_citation'],
                "default_operator": 'AND'}
            })
        if args.get('contains'):
            fields['document'] = {}
            must.append(contains_query(args))
        if args.get('year'):
            must.append(year_query(args))


        """'neutral_citation', 'courtfile', , 'year', 'court', 'bench', 'parties', 'matter', 'charge']"""
        es = current_app.extensions['elasticsearch']
        offset = args.get('offset', 0)
        results = es.search(
            index="legislation",
            doc_type="case",
            body={
                "from": offset, "size": 25,
                "fields": ["id", "full_citation"],
                "sort": [
                    "_score",
                ],
                "query": {
                    "bool": {
                        "must": must
                    }
                },
                "highlight": {
                    "pre_tags": ["<span class='search_match'>"],
                    "post_tags": ["</span>"],
                    "fields": fields
                }
            })
        return {'type': 'search', 'search_results': results['hits'], 'title': 'Advanced Search'}
    except Exception, e:
        print e
        raise CustomException('There was a problem with your query')


def query_instrument_fields(args):
    must = []
    fields = {}
    try:
        if args.get('title'):
            must.append({"simple_query_string": {
                "query": args.get('title'),
                "fields": ['title'],
                "default_operator": 'AND'}
            })
        if args.get('contains'):
            fields['document'] = {}
            must.append(contains_query(args))
        if args.get('year'):
            must.append(year_query(args))

        es = current_app.extensions['elasticsearch']
        offset = args.get('offset', 0)
        results = es.search(
            index="legislation",
            doc_type="instrument",
            body={
                "from": offset, "size": 25,
                "fields": ["id", "title"],
                "sort": [
                    "_score",
                ],
                "query": {
                    "bool": {
                        "must": must
                    }
                },
                "highlight": {
                    "pre_tags": ["<span class='search_match'>"],
                    "post_tags": ["</span>"],
                    "fields": fields
                }
            })
        return {'type': 'search', 'search_results': results['hits'], 'title': 'Advanced Search'}
    except Exception, e:
        print e
        raise CustomException('There was a problem with your query')


@Query.route('/case/file/<path:filename>')
@require_auth
def case_file(filename):
    case_path = current_app.config['CASE_DIR']
    return send_from_directory(case_path, filename)


@Query.route('/query')
@require_auth
def query():
    args = request.args
    query_type = args.get('doc_type')
    status = 200
    try:
        if query_type == 'all':
            result = query_all(args)
        elif query_type in ['act', 'regulation',  'sop', 'bill', 'instrument']:
            result = query_instrument(args)
        elif query_type in ['instruments']:
            result = query_instrument_fields(args)
        elif query_type == 'case':
            result = query_case(args)
        elif query_type == 'cases':
            if args.get('search') == 'advanced':
                result = query_case_fields(args)
            else:
                result = query_cases(args)
        else:
            raise CustomException('Badly formed query')
    except CustomException, e:
        result = {'error': str(e)}
        status = 500
    return jsonify(result), status
