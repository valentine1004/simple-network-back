import pymysql
from app import app
from config import mysql
from flask import jsonify, request, make_response
from flask_cors import cross_origin
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-Access-Token' in request.headers:
            token = request.headers['X-Access-Token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM user WHERE id=%s", data['id'])
            current_user = cursor.fetchall()

        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user[0], *args, **kwargs)

    return decorated


@app.route('/user', methods=['GET'])
@cross_origin()
@token_required
def get_all_users(current_user):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM user")
        rows = cursor.fetchall()
        res = jsonify(rows)
        res.status_code = 200

        return res
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/user/<user_id>', methods=['GET'])
@cross_origin()
@token_required
def get_one_user(current_user, user_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM user WHERE id=%s", user_id)
        user = cursor.fetchall()
        user_profile = user[0]
        user_profile.pop('password', None)
        res = jsonify(user_profile)
        res.status_code = 200

        return res
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/user', methods=['POST'])
@cross_origin()
def create_user():
    try:
        data = request.get_json()
        _id = str(uuid.uuid4())
        _first_name = data['first_name']
        _last_name = data['last_name']
        _hashed_password = generate_password_hash(data['password'])
        _age = data['age']
        _email = data['email']
        _sex = data['sex']
        _username = data['username']
        _status = data['status']
        _address = data['address']

        sql = "INSERT INTO user(id, first_name, last_name, password, age, email, sex, username, status, address) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        sql_data = (_id, _first_name, _last_name, _hashed_password, _age, _email, _sex, _username, _status, _address)
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, sql_data)
        conn.commit()
        resp = jsonify('User added successfully!')
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/user/<user_id>', methods=['PUT'])
@cross_origin()
def promote_user():
    return ''


@app.route('/user/<user_id>', methods=['DELETE'])
@cross_origin()
def delete_user():
    return ''


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    auth = request.get_json()

    if not auth or not auth['username'] or not auth['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM user WHERE username=%s", auth['username'])
    user = cursor.fetchall()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user[0]['password'], auth['password']):
        token = jwt.encode({'id': user[0]['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')
        user_profile = user[0]
        user_profile.pop('password', None)
        return jsonify({'token': token.decode('UTF-8'), 'user': user_profile})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


if __name__ == '__main__':
    app.run(debug=True)