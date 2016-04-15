#!flask/bin/python
from flask import Flask, jsonify, make_response
from pymongo import MongoClient
from bson import json_util
import json
import hashlib
import time
import random

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017")
db = client.test
const_timeleft=3600

def check_category(case):
    case = case.lower(); 
    return {
    "python" : "python",
    "java" : "java",
    "c#" : "c#",
    "c++" : "c++",
    "php" : "php",
    }.get(case, False)

def generate_token():
    acsess_key = random.random()
    acsess_key = str(acsess_key).encode('utf-8')
    acsess_key = hashlib.sha1(acsess_key).hexdigest()
    acsess_key = acsess_key[0:15]
    return acsess_key


def check_token(const_user):
    result = db.users.find(const_user)
    timeleft = result[0]['timeleft']
    if(timeleft == ''):
        timeleft = 0
    timeleft = (int(time.time())-timeleft)
    if(timeleft > 0):
        login = result[0]['login']
        key = generate_token()
        token = {'$set' :{'key': key, 'timeleft': int(time.time()+const_timeleft)}}
        login = {'login': login}
        db.users.update(login,token)
        return jsonify({'response': key}),201
    else:
       token = db.users.find(const_user)
       token = token[0]['key']
    return jsonify({'response': token}),201

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
    if (not 'key' in request.json):
        return jsonify({'error': 'key not found'}),400

    data = json.loads(json_util.dumps(db.users.find({'key':request.json['key']})))
    if len(data) == 0:
        abort(401)
    else:
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
    if not request.json:
      abort(400)
    filter = {"_id":_id}
    data = json.loads(json_util.dumps(db.issues.find(filter)))
    if len(data) == 0:
        abort(404)
    if (not 'title' in request.json):
        return jsonify({'error': 'title not found'}),400
    if (not 'text' in request.json):
        return jsonify({'error': 'text not found'}),400
    if (not 'category' in request.json):
        return jsonify({'error': 'Category not found'}),400
    if (not check_category(request.json['category'])):
        return jsonify({'error': 'Category not exist'}),400
    data = json.loads(json_util.dumps(db.users.find({'key':request.json['key']})))
    if len(data) == 0:
        abort(401)
    else:
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
    data = json.loads(json_util.dumps(db.users.find({'key':request.json['key']})))
    if len(data) == 0:
        abort(401)
    else:
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
    password = hashlib.sha1(password + salt).hexdigest()
    data={'login':request.json['login'],'password':password,'timeleft':0}
    check_user = {'login':request.json['login']}
    result =json.loads(json_util.dumps(db.users.find(check_user)))
    if(len(result) == 0):
       db.users.insert(data)
       return jsonify({'response': 'success'}), 201
    else: 
       return jsonify({'error': 'user exist'}), 400

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
    password = hashlib.sha1(password + salt).hexdigest()
    check_user = {'login':request.json['login'],'password':password}
    result =json.loads(json_util.dumps(db.users.find(check_user)))
    if(len(result) == 0):
       return jsonify({'error': 'user not found'}), 400
    else: 
        const_user = json.loads(json_util.dumps({'login':request.json['login']}))
        return check_token(const_user)


#Обробка стандартного 404
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

if __name__ == '__main__':
    app.run()

