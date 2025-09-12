from flask import request, jsonify, Blueprint
from db.db_pool import get_cursor, release_connection
import psycopg2

from marshmallow import ValidationError
from validators.tools import ValidateCreateListing
from validators.tools import Validate_find_all_listings_by_username
from validators.tools import Validate_UUID_id

from flask_jwt_extended import jwt_required

tools = Blueprint('tools', __name__)

@tools.route('/listings', methods=['PUT']) #active
@jwt_required()
def find_all_listings_by_username():
    conn = None
    try:
        data = request.get_json()
        try:
         inputs =  Validate_find_all_listings_by_username().load(data)
        except ValidationError as err:
            return jsonify(err.messages)
        conn, cursor = get_cursor()
        cursor.execute('SELECT * FROM accounts JOIN listings ON accounts.id = listings.account_id WHERE accounts.username = %s', (inputs['username'],))
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

@tools.route('/deleteListing', methods=['DELETE'])
@jwt_required()
def delete_listing_by_listing_id():
    conn = None
    try:
        data = request.get_json()
        try:
         inputs =  Validate_UUID_id().load(data)
        except ValidationError as err:
            return jsonify(err.messages)
        conn, cursor = get_cursor()
        cursor.execute('DELETE FROM listings WHERE id = %s', (inputs['listing_id'],))
        conn.commit()
        return jsonify(status='ok', msg='tool delete'), 200

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

@tools.route('/eachListing', methods=['PUT'])
def find_one_listings_by_listing_id():
    conn = None
    try:
        data = request.get_json()
        try:
            inputs = Validate_UUID_id().load(data)
        except ValidationError as err:
            return jsonify(err.messages)
        conn, cursor = get_cursor()
        cursor.execute('SELECT id, asking_price, floor_size, land_size, bedroom, toilet, type, location, geo_lat, geo_lon, summary, description, tenure FROM listings WHERE id = %s', (inputs['listing_id'],))
        results = cursor.fetchone()

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

@tools.route('/username', methods=['POST'])
def find_one_account_by_username():
    data = request.get_json()
    conn, cursor = get_cursor()
    cursor.execute('SELECT * FROM accounts JOIN listings ON accounts.id = listings.account_id WHERE username = %s', (data['username'],))
    results = cursor.fetchone()
    release_connection(conn)

    return jsonify(results), 200

@tools.route('/createListing', methods=['PUT'])
def create_listing():
    conn = None
    try:
        data = request.get_json()
        try:
            ValidateCreateListing().load(data)
        except ValidationError as err:
            return jsonify(err.messages)
        conn, cursor = get_cursor()
        cursor.execute('INSERT INTO listings ('
                       'asking_price, floor_size, land_size, bedroom, toilet, type, tenure, unit_number, location, geo_lat, geo_lon, summary, description, account_id) VALUES ('
                       '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
                       (data['asking_price'], data['floor_size'], data['land_size'], data['bedroom'], data['toilet'], data['type'], data['tenure'], data['unit_number'], data['location'], data['geo_lat'], data['geo_lon'], data['summary'], data['description'], data['account_id']))
        conn.commit()
        return jsonify({"status": 'ok', "msg": 'listing added'}), 200

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


@tools.route('/tools/<tool_id>', methods=['DELETE'])
def delete_one_tool_by_id(tool_id):
    conn, cursor = get_cursor()
    cursor.execute('DELETE FROM tools WHERE id = %s', (tool_id,))
    conn.commit()
    release_connection(conn)

    return jsonify(status='ok', msg='tool delete'), 200

@tools.route('/tools', methods=['PATCH'])
def update_one_tool():
    tool_id = request.json.get('id')
    name = request.json.get('name')
    description = request.json.get('description')

    conn, cursor = get_cursor()
    cursor.execute("SELECT * FROM tools WHERE id = %s", (tool_id,))
    results = cursor.fetchone()

    cursor.execute('UPDATE tools'
                   'SET name=COALESCE(%s, %s),'
                   'description=COALESCE(%s, %s)'
                   'WHERE id=%s',
                   (name, results['name'], description, results['description'], tool_id))

    conn.commit()
    release_connection(conn)

    return jsonify(status='ok', msg='tool update'), 200

@tools.route('/tools/methods', methods=['GET','POST'])
def tools_endpoints():
    conn, cursor = get_cursor()
    return_value = None

    if request.method == 'GET':
        cursor.execute('SELECT * FROM tools ORDER by id')
        return_value = cursor.fetchall()

    elif request.method == 'POST':
        data = request.get_json()
        cursor.execute('SELECT * FROM tools WHERE id = %s', (data['id'],))
        return_value = cursor.fetchone()

    release_connection(conn)

    return jsonify(return_value), 200
