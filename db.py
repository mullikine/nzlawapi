from util import CustomException
import psycopg2
import psycopg2.extras
from flask import g, current_app
from lxml import etree


def get_db():
    if not hasattr(g, 'db') or g.db.closed:
        g.db = connect_db()
    return g.db


def connect_db():
    conn = psycopg2.connect(
        database=current_app.config['DB'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PW'],
        host=current_app.config['DB_HOST'])
    return conn


def connect_db_config(config):
    conn = psycopg2.connect(
            database=config.DB,
            user=config.DB_USER,
            password=config.DB_PW)
    return conn


def init_db():
    pass


def get_document_from_title(title, db=None):
    with (db or get_db()).cursor() as cur:
        cur.execute("""
            select title as name, q.type, document from
                ((select trim(full_citation) as title, 'case' as type, null as document_id from cases
            where trim(full_citation) = %(title)s
                )
                union
                (select trim(title) as title, 'act' as type, document_id from acts
            where title = %(title)s
            order by version desc limit 1
                )
                union
                (select trim(title) as title, 'regulation' as type, document_id from regulations
            where title = %(title)s
            order by version desc limit 1
                )) q
            left outer join documents d on q.document_id = d.id
            """, {'title': title})
        return cur.fetchone()
