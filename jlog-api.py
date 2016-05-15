from flask import Flask, request, jsonify
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

@app.route('/add_post/<user>/<collection>', methods=['POST'])
def add_post(user, collection):
    if request.method == 'POST':
        text = request.form['text']
        category = request.form['category']
        oid = addPost(text,user,collection, category)
        app.logger.info('Added post: ' + oid+' '+ text)
        return "Added post {}".format(oid)

# @app.route('/query/', methods=['POST'])
# def queryPost():
#     if request.method =='POST':
#         query = json.loads(equest.form['query'])
#         posts.find(query,)


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
    num_re = re.compile(r'^[\-]?[1-9][0-9]*\.?[0-9]+([eE][0-9])?$')
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
