from flask import Flask, request, g
import os, time, sys
import sqlite3
import logging

scriptDir = os.path.dirname(__file__)
outputPath = './cache.db'
DATABASE = os.path.join(scriptDir, outputPath)

CREATE_CACHE =  "CREATE TABLE IF NOT EXISTS CACHE (id integer primary key, key text NOT NULL, value text NOT NULL);"
DELETE_CACHE = "DROP TABLE IF EXISTS CACHE;"
INSERT_SQL = "INSERT INTO CACHE(key,value) VALUES(?,?);"

app = Flask(__name__)

#get db connectuion
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
    
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
    try:
        cur = get_db().execute(query, args)
        get_db().commit()
    except Exception as E:
        print("error", E)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# put the cache of the item with the given value
@app.route('/put', methods=["POST"])
def putCache():
    """ updates the cache item """
    key = str(request.args.get('key'))
    value = str(request.args.get('value'))
    with app.app_context():
        #check if an item exists in the cache with the given key
        count = query_db('SELECT * FROM CACHE WHERE key=?', [key])
        if len(count) == 0:
            try:
                k = query_db('INSERT INTO CACHE(key, value) values(?, ?)', [key, value])
                print(k)
                return key
            except Exception as E:
                print(E)
                return {'value':"not found"}

# get the value of the key 
@app.route('/get', methods=["GET"])
def getCache():
    """ get the cache item """
    key = str(request.args.get('key'))
    #check if an item exists in the cache with the given key
    count = query_db('SELECT * FROM CACHE WHERE key = ?', [key])
    if len(count) == 1:
        try:
            value = query_db('SELECT value FROM CACHE WHERE key=?', [key], one=True)
            return value
        except Exception as E:
            return {'value':"not found"}
    else:
        return {'value':"not found"}

# erase the value of the key 
@app.route('/erase', methods=["DELETE"])
def eraseCache():
    """ erase the cache item """
    key = str(request.args.get('key'))
    with app.app_context():
        #check if an item exists in the cache with the given key
        count = query_db('SELECT * FROM CACHE WHERE key=?', [key])
        if len(count) == 1:
            try:
                query_db('DELETE FROM CACHE WHERE key=?', [key], one=True)
                return key
            except Exception as E:
                return {'value':"not found"}
        else:
            return {'value':"not found"}

if __name__ == "__main__":
    try:
        with app.app_context():
            cur = get_db().cursor()
            
            #create cache table
            cur.execute(DELETE_CACHE)
            cur.execute(CREATE_CACHE)

    except Exception as e:
        print(e)


    #start the flask app for cache server
    app.run(host='0.0.0.0', debug=True, port=8083, threaded = True)

