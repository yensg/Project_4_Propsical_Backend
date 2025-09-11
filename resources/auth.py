import bcrypt
from flask import request, jsonify, Blueprint
from db.db_pool import get_cursor, release_connection
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    inputs = request.get_json()
    conn, cursor = get_cursor()
    cursor.execute('SELECT id FROM accounts WHERE username = %s', (inputs['username'],))
    results = cursor.fetchone()

    if results:
        return jsonify(status='error', msg='duplicate username'), 400

    hash = bcrypt.hashpw(inputs['password'].encode('utf-8'), bcrypt.gensalt())

    cursor.execute('INSERT INTO accounts (username, email, name, hash, role, subscription_plan)'
                   ' VALUES (%s, %s, %s, %s, %s, %s)',
                   (inputs['username'], inputs['email'], inputs['name'],hash.decode('utf-8'), inputs['role'], inputs['subscription_plan'] ))
    conn.commit()
    release_connection(conn)

    return jsonify(status='ok', msg='registration done'), 200

@auth.route('/login', methods=['POST'])
def login():
    inputs = request.get_json()
    conn, cursor = get_cursor()
    cursor.execute('SELECT * FROM auth WHERE email = %s', (inputs['email'],))
    results = cursor.fetchone()
    release_connection(conn)

    if not results:
        return jsonify(status='error', msg='email or password incorrect'), 401

    access = bcrypt.checkpw(inputs['password'].encode('utf-8'), results['hash'].encode('utf-8'))

    if not access:
        return jsonify(status='error', msg='email or password incorrect'), 401


    claims = {'name': results['name']}
    access_token = create_access_token(results['email'], additional_claims=claims)
    refresh_token = create_refresh_token(results['email'], additional_claims=claims)

    return jsonify(access=access_token, refresh=refresh_token), 200

@auth.route('/refresh')
def refresh():
    identity = get_jwt_identity()
    claims = get_jwt()

    access_token = create_access_token(identity, additional_claims=claims)

    return jsonify(access=access_token), 200