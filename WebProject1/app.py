#!flask/bin/python
from flask import Flask, abort, flash, redirect,jsonify,redirect,request, make_response
from pymongo import MongoClient
from datetime import datetime,date,timedelta
from bson import json_util
import json
import hashlib

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017")
db = client.test

def check_category(case):
    case = case.lower(); 
    return {
    "python" : "python",
    "java" : "java",
    "c#" : "c#",
    "c++" : "c++",
    "php" : "php",
    }.get(case, False)

@app.route('/')
@app.route('/home')
def home():

     return ''

#Добавлення issues 
@app.route('/api/add_issues', methods=['POST'])
def add_issue():
    if not request.json:
        abort(400)
    if (not 'title' in request.json):
        return jsonify({'error': 'title not found'}),400
    if (not 'text' in request.json):
        return jsonify({'error': 'text not found'}),400
    if (not 'category' in request.json):
        return jsonify({'error': 'Category not found'}),400
    if (not check_category(request.json['category'])):
        return jsonify({'error': 'Category not exist'}),400
    id = db.issues.find( {}, { "_id": 1 } ).sort( [('_id', -1)] ).limit(1);
    id = id[0]["_id"] +1
    user={'_id':id,'title':request.json['title'],'text':request.json['text'],'category':check_category(request.json['category']),'date': datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')}
    db.issues.insert(user)
    return jsonify({'response': 'success'}), 201
    

#вивід усіх issues 
@app.route('/api/get_issues', methods=['GET'])
def get_issues():
        id = json.loads(json_util.dumps(db.issues.find()))
        return jsonify({'response': id}),200

#вивід issues з категорією 
@app.route('/api/get_issues/<string:category>', methods=['GET'])
def get_issue(category):
    if (not check_category(category)):
        return jsonify({'error': 'category not exist'}),400
    filter = {"category":check_category(category)}
    data = json.loads(json_util.dumps(db.issues.find(filter)))
    return jsonify({'response': data}),200

#оновлення issues 
@app.route('/api/update_issues/<int:_id>', methods=['PUT'])
def update_issues(_id):
    filter = {"_id":_id}
    data = json.loads(json_util.dumps(db.issues.find(filter)))
    if len(data) == 0:
        abort(404)
    if not request.json:
        abort(400)

    if (not 'title' in request.json):
        return jsonify({'error': 'title not found'}),400
    if (not 'text' in request.json):
        return jsonify({'error': 'text not found'}),400
    if (not 'category' in request.json):
        return jsonify({'error': 'Category not found'}),400
    if (not check_category(request.json['category'])):
        return jsonify({'error': 'Category not exist'}),400
    data = {'title':request.json['title'],'text':request.json['text'],'category':check_category(request.json['category'])}
    id = {"_id":_id}
    db.issues.update(id,data)
    return jsonify({'response': 'success'}), 200

#Видалення issues
@app.route('/api/delete_issues/<int:_id>', methods=['DELETE'])
def delete_issues(_id):
    filter = {"_id":_id}
    data = json.loads(json_util.dumps(db.issues.find(filter)))
    if len(data) == 0:
        abort(404)
    data = {"_id":_id}
    db.issues.remove(data)
    return jsonify({'response': 'success'}), 200


#ключа доступу до даних
@app.route('/api/register', methods=['POST'])
def register():
    if not request.json:
        abort(400)
    if (not 'login' in request.json):
        return jsonify({'error': 'login not found'}),400
    if (not 'password' in request.json):
        return jsonify({'error': 'password not found'}),400
    salt = "#sda$*(DAS".encode('utf-8')
    password = request.json['password'].encode('utf-8')
    password = hashlib.sha512(password + salt).hexdigest()
    data={'login':request.json['login'],'password':password}
    db.users.insert(data)
    return jsonify({'response': 'success'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    if not request.json:
        abort(400)
    if (not 'login' in request.json):
        return jsonify({'error': 'login not found'}),400
    if (not 'password' in request.json):
        return jsonify({'error': 'password not found'}),400
    salt = "#sda$*(DAS".encode('utf-8')
    password = request.json['password'].encode('utf-8')
    password = hashlib.sha512(password + salt).hexdigest()
    auth = {'login':request.json['login'],'password':password}
    result = json.loads(json_util.dumps(db.users.find(auth)))
    if len(result) == 0:
        return jsonify({'error': 'Unauthorized access'}), 401
    else:
        key_string = request.json['login'] + request.json['password']
        key_string = key_string.encode('utf-8')
        salt = "!2s@#".encode('utf-8')
        hash = hashlib.sha512( salt + key_string ).hexdigest()
        
        auth={'login':request.json['login'],'password':request.json['password'],'token': hash}
        login = {'login':request.json['login']}
        db.users.update(login,auth)
        return jsonify({'response': 'success'},{'token':hash}), 201




#Обробка стандартного 404
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(401)
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

if __name__ == '__main__':
    app.debug = True;
    app.run()

