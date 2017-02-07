#!/usr/bin/env python
import flask
from flask import g, request
import sqlite3


DATABASE = '../test.sqlite3'
app = flask.Flask(__name__)


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/', methods=['GET'])
def index():
    '''
    Retrieve two lists of judgements: (1) all non-manual mappings where
    `judgement` is TRUE - these are the judgements we want our user to
    review manually, and (2) all manual mappings of any status - we
    want to give our user the opportunity to review these again.
    '''
    query = '''SELECT tm.left_uid AS left_uid, te_left.name AS left_name,
    		   te_left.origin as left_origin,
    		   tm.right_uid AS right_uid, te_right.name AS right_name,
    		   te_right.origin AS right_origin,
               tm.judgement AS judgement,
    		   tm.judgement_attribution AS attribution
               FROM test_mappings tm
               INNER JOIN test_entities te_left
               ON (tm.left_uid=te_left.uid %s)
               INNER JOIN test_entities te_right
               ON tm.right_uid=te_right.uid '''
    # Everything that is a mapping, but hasn't already been manually reviewed.
    q_auto = "AND (tm.judgement_attribution IS NULL "
    q_auto += "OR tm.judgement_attribution!='manual') AND judgement=1"
    automatic_mappings = query_db(query % q_auto)
    # Everything that was judged to be a mapping after manual review.
    q_manual = "AND tm.judgement_attribution='manual'"
    manual_mappings = query_db(query % q_manual)
    return flask.render_template('index.html',
    	                         automatic_mappings=automatic_mappings,
                                 manual_mappings=manual_mappings)


@app.route('/update', methods=['POST'])
def update_mapping():
    '''
    Actions from the page. Either approve or reject a mapping,
    or move an already-reviewed mapping back to the approval queue.
    TODO:
    - Error handling
    - Use emit_judgement instead of raw SQL
    '''
    left_uid = request.form['left_uid']
    right_uid = request.form['right_uid']
    action = request.form['action']
    conn = get_db()
    if action == 'approve':
        query = '''
            UPDATE test_mappings
            SET judgement_attribution='manual'
        	WHERE left_uid=? AND right_uid=?
        '''
    elif action == 'reject':
        query = '''
        	UPDATE test_mappings
        	SET judgement_attribution='manual', judgement=0
        	WHERE left_uid=? AND right_uid=?
        '''
    else:
        query = '''
            UPDATE test_mappings
            SET judgement_attribution='automatic', judgement=1
            WHERE left_uid=? AND right_uid=?
        '''
    get_db().execute(query, (left_uid, right_uid))
    conn.commit()
    conn.close()
    return '', 200


if __name__ == '__main__':
    app.debug = True
    app.run()
