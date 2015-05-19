
import psycopg2

import sys
from psycopg2 import extras
import importlib
import os
from lxml import etree
from collections import defaultdict
import re

p = etree.XMLParser(huge_tree=True)

def id_lookup(db):
    with db.cursor(cursor_factory=extras.RealDictCursor) as cur:
        cur.execute(""" delete from id_lookup""")
    with db.cursor(cursor_factory=extras.RealDictCursor, name="law_cursor") as cur, db.cursor() as out:
        cur.execute("""SELECT d.id, title, document FROM instruments i join documents d on i.id = d.id """)
        results = cur.fetchmany(1)
        count = 0
        id_results = []
        while len(results):
            for result in results:
                if count % 10 == 0:
                    print count, len(id_results)
                count += 1
                for el in etree.fromstring(result['document'], parser=p).xpath('//*[@id]'):
                    new_id = el.attrib.get('id')
                    id_results.append( (new_id, result['id'], generate_path_string(el, title=unicode(result['title'].decode('utf-8')))[0]))
            results = cur.fetchmany(1)
            if len(id_results) > 100000:
                args_str = ','.join(cur.mogrify("(%s,%s,%s)", x) for x in id_results)
                out.execute("INSERT INTO id_lookup(govt_id, parent_id, repr) VALUES " + args_str)
                id_results[:] = []

        if len(id_results):
            args_str = ','.join(cur.mogrify("(%s,%s,%s)", x) for x in id_results)
            out.execute("INSERT INTO id_lookup(govt_id, parent_id, repr) VALUES " + args_str)
            id_results[:] = []
    db.commit()




def refs_and_subs(db, do_references, do_subordinates):
    from acts import links

    with db.cursor(cursor_factory=extras.RealDictCursor) as cur:
        if do_references:
            cur.execute(""" delete from document_references""")
            cur.execute(""" delete from section_references""")
        if do_subordinates:
            cur.execute(""" delete from subordinates""")

    with db.cursor(cursor_factory=extras.RealDictCursor, name="law_cursor") as cur:
        cur.execute('select count(*) as count from instruments')
        total = cur.fetchone()['count']

    id_lookup = links.get_all_ids(db)

    links = links.get_links(db)

    with db.cursor(cursor_factory=extras.RealDictCursor, name="law_cursor") as cur, db.cursor() as out:
        count = 0
        cur.execute("""SELECT document, d.id, title from instruments i join documents d on i.id = d.id
            """)
        documents = cur.fetchmany(1)

        while len(documents):
            for document in documents:
                count += 1
                if count % 100 == 0:
                    print count
                tree = etree.fromstring(document['document'], parser=p)
                source_id = document['id']
                title = unicode(document['title'].decode('utf-8'))

                tree = links.remove_ignored_tags(tree)

                if do_references:
                    document_refs, section_refs = links.find_references(tree, source_id, title, id_lookup)

                    if len(document_refs):
                        args_str = ','.join(cur.mogrify("(%s,%s,%s)", x) for x in document_refs)
                        out.execute("INSERT INTO document_references (source_id, target_id, count) VALUES " + args_str)

                        args_str = ','.join(cur.mogrify("(%s,%s,%s,%s, %s, %s)", x) for x in section_refs)
                        out.execute("INSERT INTO section_references (source_document_id, target_govt_id, source_repr, source_url, link_text, target_document_id) VALUES " + args_str)

                if do_subordinates:
                    ids = links.find_parent_instrument(tree, source_id, title, id_lookup, links)
                    if len(ids):
                        args_str = ','.join(cur.mogrify("(%s, %s)", (x, source_id)) for x in ids)
                        out.execute("INSERT INTO subordinates (parent_id, child_id) VALUES " + args_str)

            documents = cur.fetchmany(1)
    db.commit()
    with db.cursor(cursor_factory=extras.RealDictCursor) as cur:
        # lets make the interpretation act the parent of everything

        cur.execute("""
            INSERT INTO subordinates (parent_id, child_id)
            SELECT
                (select id from instruments where title = 'Interpretation Act 1999' AND version = 19) as parent_id,
                id as child_id  FROM instruments WHERE
                title != 'Interpretation Act 1999'
                """)
        cur.execute("""
            INSERT INTO subordinates (parent_id, child_id)
                (select null as parent_id, id as child_id from instruments where title = 'Interpretation Act 1999' AND version = 19)
                """)

    links.fix_cycles(db)


def analyze_links(db):
    from acts import traversal
    from acts import links
    with db.cursor(cursor_factory=extras.RealDictCursor) as cur:
        cur.execute('select count(*) as count from latest_instruments')
        total = cur.fetchone()['count']
    with db.cursor(cursor_factory=extras.RealDictCursor, name="law_cursor") as cur:

        cur.execute("""SELECT document, id, title, govt_id from latest_instruments""")
        results = cur.fetchmany(10)
        inserts = []
        deletes = []
        count = 0.0
        while len(results):
            for result in results:
                count += 1
                tree = etree.fromstring(document['document'], parser=p)
                ins, dels = links.get_reparse_link_texts(tree, result.get('id'), result.get('govt_id'), db=db)
                inserts += ins
                dels += dels
                sys.stdout.write("%d%%\r" % (count/total*100))
                sys.stdout.flush()

            results = cur.fetchmany(10)

    with db.cursor() as out:
        for insert in inserts:
            out.execute(insert)
        for delete in deletes:
            out.execute(delete)

    db.commit()


def run(db, config, do_id_lookup=True, do_references=True, do_subordinates=True, do_links=True):
    if do_id_lookup:
        id_lookup(db)

    if do_references or do_subordinates:
        refs_and_subs(db, do_references, do_subordinates)

    if do_links:
        analyze_links(db)


if __name__ == "__main__":
    if not len(sys.argv) > 1:
        raise Exception('Missing configuration file')
    sys.path.append(os.getcwd())
    config = importlib.import_module(sys.argv[1].replace('.py', ''), 'parent')
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
    from util import generate_path_string, get_path
    db = psycopg2.connect(
            database=config.DB,
            user=config.DB_USER,
            host=config.DB_HOST,
            password=config.DB_PW)
    # poor mans switches
    with db.cursor(cursor_factory=extras.RealDictCursor) as cur:
        cur.execute(""" refresh materialized view latest_instruments """)
    run(db, config,
    do_id_lookup=('skip_ids' not in sys.argv[1:]),
    do_references=('skip_references' not in sys.argv[1:]),
    do_subordinates=('skip_subordinates' not in sys.argv[1:]),
    do_links=('skip_links' not in sys.argv[1:]))

    db.close()

