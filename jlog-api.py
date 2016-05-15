from flask import Flask, request
import re
import datetime
import logging
from pymongo import MongoClient

#init the db client
client = MongoClient("mongo", 27017)
db = client['logbook_db']
#collection
posts = db.posts


#flask init
app = Flask("logbook_api")
app.secret_key='ciaociao'

@app.route('/add_post', methods=['POST'])
def add_post():
    if request.method == 'POST':
        text = request.form['text']
        oid = addPost(text)
        app.logger.info('Added post: ' + oid+ text)
        return "Added post {}".format(oid)



def addPost(text):
    post = {
        "text": text,
        "timestamp": datetime.datetime.utcnow(),
        "tags" : []
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
    oid = posts.insert_one(post).inserted_id
    return str(oid)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
