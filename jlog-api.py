from flask import Flask, request, jsonify, Response
import re
import json
import datetime
import logging
from pymongo import MongoClient
from bson.json_util import dumps

#init the db client
client = MongoClient("mongo", 27017)
db = client['jlog_db']

#flask init
app = Flask("jlog-api")
app.secret_key='12345678'

@app.route('/journal/<collection>', methods=['POST'])
def add_post(collection):
    if request.method == 'POST':
        data = request.get_json()
        if data['action'] == 'add':
            text = data['text']
            user = data['user']
            print(text)
            category = data['category']
            oid = addPost(text,user,collection, category)
            app.logger.info('Added post: ' + oid+' '+ text)
            return jsonify({"post_created": oid})
        elif data['action'] == 'query':
            data = request.get_json()
            coll = db[collection]
            query_json = {}
            if "tags" in data:
                if len(data['tags'])>0:
                    query_json["tags"] = { "$all" : data['tags']}
            if "user" in data:
                query_json['user'] = data['user']
            if "properties" in data:
                for p in data['properties']:
                    query_json.update(p)
            if "category" in data:
                query_json = data['category']
            #getting limit of n. of items
            lim = data['limit']
            app.logger.info("Query: {}".format(query_json))
            #getting all documents in descending order
            docs = [doc for doc in coll.find(query_json,limit=lim)
                        .sort('timestamp',-1)]
            return Response(dumps(docs), mimetype='application/json')

@app.route('/journal', methods=['GET'])
def get_journals():
    return Response(dumps(db.collection_names()),
                          mimetype='application/json')

@app.route('/journal/<collection>', methods=['DELETE'])
def drop_collection(collection):
    db[collection].drop()
    return "Deleted: "+ collection

def addPost(text, user, collection, category):
    post = {
        "text": text,
        "timestamp": datetime.datetime.utcnow(),
        "tags" : [],
        "user" : user,
        "category": category
        }
    #reading metadata
    p_re = re.compile(r'@(?P<prop>.*?):(?P<value>.*?)(?=[\s#@]|$)')
    t_re = re.compile(r'#(?P<tag>.*?)(?=[\s@#]|$)')
    num_re = re.compile(r'^[\-]?[0-9]*\.?[0-9]+([eE][0-9]+)?$')
    #proprieties
    for m in p_re.finditer(text):
        prop = m.group('prop')
        value =  m.group('value')
        if num_re.match(value):
            value = float(value)
        post[prop] = value
        #proprieties are added also as tags
        post['tags'].append(prop)
    #tags
    for t in t_re.finditer(text):
        post['tags'].append(t.group('tag'))
    #inserting in the dictionary
    oid = db[collection].insert_one(post).inserted_id
    return str(oid)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
