import bcrypt
from flask import request, jsonify, Blueprint
from db.db_pool import get_cursor, release_connection
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import psycopg2

from marshmallow import ValidationError
from validators.tools import ValidateRegistration

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST']) #active
def register():
    data = request.get_json()
    try:
        inputs = ValidateRegistration().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    conn, cursor = get_cursor()
    cursor.execute('SELECT id FROM accounts WHERE username = %s', (inputs['username'],))
    results = cursor.fetchone()

    if results:
        return jsonify(status='error', msg='duplicate username'), 400

    hash = bcrypt.hashpw(inputs['password'].encode('utf-8'), bcrypt.gensalt())

    cursor.execute('INSERT INTO accounts (username, email, name, phone, hash, role, subscription_plan)'
                   ' VALUES (%s, %s, %s, %s, %s, %s, %s)',
                   (inputs['username'], inputs['email'], inputs['name'], inputs['phone'],hash.decode('utf-8'), inputs['role'], inputs['subscription_plan'] ))
    conn.commit()
    release_connection(conn)

    return jsonify(status='ok', msg='registration done'), 200

@auth.route('/getAllAccounts')
def find_all_accounts():
    conn = None
    try:
        conn, cursor = get_cursor()

        cursor.execute('SELECT * FROM accounts')
        results = cursor.fetchall()

        return jsonify(results), 200

    except psycopg2.Error as err:
        print(f'database error: {err}')
        return jsonify({'status': 'error'}), 400
    except SyntaxError as err:
        print(f'syntax error: {err}')
        return jsonify({'status': 'error'}), 400
    except Exception as err:
        print(f'unknown error: {err}')
        return jsonify({'status': 'error'}), 500
    finally:
        release_connection(conn)

@auth.route('/login', methods=['POST'])#active
def login():
    inputs = request.get_json()
    conn, cursor = get_cursor()
    cursor.execute('SELECT * FROM accounts WHERE username = %s', (inputs['username'],))
    results = cursor.fetchone()
    release_connection(conn)

    if not results:
        return jsonify(status='error', msg='username or password incorrect'), 401

    access = bcrypt.checkpw(inputs['password'].encode('utf-8'), results['hash'].encode('utf-8'))

    if not access:
        return jsonify(status='error', msg='username or password incorrect'), 401


    claims = {'username': results['username'], 'role': results['role']}
    access_token = create_access_token(results['username'], additional_claims=claims)
    refresh_token = create_refresh_token(results['username'], additional_claims=claims)

    return jsonify(access=access_token, refresh=refresh_token), 200

@auth.route('/refresh')
def refresh():
    identity = get_jwt_identity()
    claims = get_jwt()

    access_token = create_access_token(identity, additional_claims=claims)

    return jsonify(access=access_token), 200