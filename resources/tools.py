from flask import request, jsonify, Blueprint
from db.db_pool import get_cursor, release_connection
import psycopg2

from marshmallow import ValidationError
from validators.tools import ValidateCreateListing
from validators.tools import Validate_username
from validators.tools import Validate_UUID_id
from validators.tools import Validate_find_account_id_by_username

from flask_jwt_extended import jwt_required

tools = Blueprint('tools', __name__)

@tools.route('/listings', methods=['PUT']) #active_ListingSummary
@jwt_required()
def find_all_listings_by_username():
    conn = None
    try:
        data = request.get_json()
        inputs = Validate_username().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    try:
        conn, cursor = get_cursor()
        cursor.execute('SELECT * FROM accounts JOIN listings ON accounts.id = listings.account_id WHERE accounts.username = %s', (inputs['username'],))
        results = cursor.fetchall()

        return jsonify(results), 200

    except psycopg2.IntegrityError as e:
        print(f'Constraint violated: {e}')
        return jsonify({'error': 'Constraints broken'}), 400
    except psycopg2.ProgrammingError as e:
        print(f'SQL syntax error: {e}')
        return jsonify({'error': 'SQL syntax error'}), 400
    except psycopg2.Error as e:
        print(f'Other database error: {e}')
        return jsonify({'error': 'Other database error'}), 400
    except Exception as e:
        print(f'unknown error: {e}')
        return jsonify({'error': 'Unknown error'}), 500
    finally:
        release_connection(conn)

@tools.route('/deleteListing', methods=['DELETE']) #active_ListingEach
@jwt_required()
def delete_listing_by_listing_id():
    conn = None
    try:
        data = request.get_json()
        inputs = Validate_UUID_id().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    try:
        conn, cursor = get_cursor()
        cursor.execute('DELETE FROM listings WHERE id = %s', (str(inputs['listing_id']),))
        conn.commit()
        return jsonify(status='ok', msg='tool delete'), 200

    except psycopg2.IntegrityError as e:
        print(f'Constraint violated: {e}')
        return jsonify({'error': 'Constraints broken'}), 400
    except psycopg2.ProgrammingError as e:
        print(f'SQL syntax error: {e}')
        return jsonify({'error': 'SQL syntax error'}), 400
    except psycopg2.Error as e:
        print(f'Other database error: {e}')
        return jsonify({'error': 'Other database error'}), 400
    except Exception as e:
        print(f'unknown error: {e}')
        return jsonify({'error': 'Unknown error'}), 500
    finally:
        release_connection(conn)

@tools.route('/eachListing', methods=['POST']) #active_ListingEachPage
def find_one_listings_by_listing_id():
    conn = None
    try:
        data = request.get_json()
        inputs = Validate_UUID_id().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    try:
        conn, cursor = get_cursor()
        cursor.execute('SELECT id, asking_price, floor_size, land_size, bedroom, toilet, unit_number, type, location, geo_lat, geo_lon, summary, description, tenure FROM listings WHERE id = %s', (str(inputs['listing_id']),)) # this command is a string but not in postgreSQL
        results = cursor.fetchone()

        return jsonify(results), 200

    except psycopg2.IntegrityError as e:
        print(f'Constraint violated: {e}')
        return jsonify({'error': 'Constraints broken'}), 400
    except psycopg2.ProgrammingError as e:
        print(f'SQL syntax error: {e}')
        return jsonify({'error': 'SQL syntax error'}), 400
    except psycopg2.Error as e:
        print(f'Other database error: {e}')
        return jsonify({'error': 'Other database error'}), 400
    except Exception as e:
        print(f'unknown error: {e}')
        return jsonify({'error': 'Unknown error'}), 500
    finally:
        release_connection(conn)

@tools.route('/allListings', methods=['GET'])
def find_all_listings():
    conn = None
    try:
        conn, cursor = get_cursor()
        cursor.execute('SELECT * FROM listings')
        results = cursor.fetchall()

        return jsonify(results), 200

    except psycopg2.IntegrityError as e:
        print(f'Constraint violated: {e}')
        return jsonify({'error': 'Constraints broken'}), 400
    except psycopg2.ProgrammingError as e:
        print(f'SQL syntax error: {e}')
        return jsonify({'error': 'SQL syntax error'}), 400
    except psycopg2.Error as e:
        print(f'Other database error: {e}')
        return jsonify({'error': 'Other database error'}), 400
    except Exception as e:
        print(f'unknown error: {e}')
        return jsonify({'error': 'Unknown error'}), 500
    finally:
        release_connection(conn)

@tools.route('/username', methods=['PUT']) #active_ListingEach
def find_username_by_listing_id():
    conn = None
    try:
        data = request.get_json()
        inputs = Validate_UUID_id().load(data)
    except ValidationError as err:
        return jsonify(err.messages)
    try:
        conn, cursor = get_cursor()
        cursor.execute('SELECT name, username, phone FROM accounts JOIN listings ON accounts.id = listings.account_id WHERE listings.id = %s', (str(inputs['listing_id']),))
        results = cursor.fetchone()

        return jsonify(results), 200

    except psycopg2.IntegrityError as e:
        print(f'Constraint violated: {e}')
        return jsonify({'error': 'Constraints broken'}), 400
    except psycopg2.ProgrammingError as e:
        print(f'SQL syntax error: {e}')
        return jsonify({'error': 'SQL syntax error'}), 400
    except psycopg2.Error as e:
        print(f'Other database error: {e}')
        return jsonify({'error': 'Other database error'}), 400
    except Exception as e:
        print(f'unknown error: {e}')
        return jsonify({'error': 'Unknown error'}), 500
    finally:
        release_connection(conn)

@tools.route('/username', methods=['POST']) #active_ListingEach
def find_account_id_by_username():
    conn = None
    try:
        data = request.get_json()
        inputs = Validate_username().load(data)
    except ValidationError as err:
        return jsonify(err.messages)
    try:
        conn, cursor = get_cursor()
        cursor.execute('SELECT id FROM accounts WHERE username = %s', (inputs['username'],))
        results = cursor.fetchone()

        return jsonify(results), 200

    except psycopg2.IntegrityError as e:
        print(f'Constraint violated: {e}')
        return jsonify({'error': 'Constraints broken'}), 400
    except psycopg2.ProgrammingError as e:
        print(f'SQL syntax error: {e}')
        return jsonify({'error': 'SQL syntax error'}), 400
    except psycopg2.Error as e:
        print(f'Other database error: {e}')
        return jsonify({'error': 'Other database error'}), 400
    except Exception as e:
        print(f'unknown error: {e}')
        return jsonify({'error': 'Unknown error'}), 500
    finally:
        release_connection(conn)

@tools.route('/createListing', methods=['PUT']) #active_ListingEachCreate
@jwt_required()
def create_listing():
    conn = None

    try:
        data = request.get_json()
        inputs = ValidateCreateListing().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    try:
        conn, cursor = get_cursor()
        cursor.execute('INSERT INTO listings (asking_price,floor_size,land_size,bedroom,toilet,type,tenure,unit_number,location,geo_lat,geo_lon,summary,description,account_id)'
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
                       (inputs['asking_price'], inputs['floor_size'], inputs['land_size'], inputs['bedroom'], inputs['toilet'], inputs['type'], inputs['tenure'], inputs['unit_number'], inputs['location'], inputs['geo_lat'], inputs['geo_lon'], inputs['summary'], inputs['description'], str(inputs['account_id'])))

        # new_listing_id = cursor.fetchone()[0]
        row = cursor.fetchone()
        new_listing_id = row["id"]
        conn.commit()
        return jsonify({"status": 'ok', "msg": 'listing added', "listing_id": str(new_listing_id)}), 200 #

    except psycopg2.IntegrityError as e:
        print(f'Constraint violated: {e}')
        return jsonify({'error': 'Constraints broken'}), 400
    except psycopg2.ProgrammingError as e:
        print(f'SQL syntax error: {e}')
        return jsonify({'error': 'SQL syntax error'}), 400
    except psycopg2.Error as e:
        print(f'Other database error: {e}')
        return jsonify({'error': 'Other database error'}), 400
    except Exception as e:
        print(f'unknown error: {e}')
        return jsonify({'error': 'Unknown error'}), 500
    finally:
        release_connection(conn)

@tools.route('/updateListing', methods=['PATCH'])
@jwt_required()
def update_listing_by_listing_id():
    conn = None
    try:
        listing_id = request.json.get('id')
        data = request.get_json()
        inputs = ValidateCreateListing().load(data)

        conn, cursor = get_cursor()
        cursor.execute("SELECT * FROM listings WHERE id = %s",
                       (listing_id,))
        results = cursor.fetchone()
        cursor.execute('UPDATE listings '
                      'SET asking_price=COALESCE(%s, %s),'
                       'floor_size = COALESCE(%s, %s),'
                       'land_size = COALESCE(%s, %s),'
                       'bedroom = COALESCE(%s, %s),'
                       'toilet = COALESCE(%s, %s),'
                       'type = COALESCE(%s, %s),'
                       'tenure = COALESCE(%s, %s),'
                       'unit_number = COALESCE(%s, %s),'
                       'location = COALESCE(%s, %s),'
                       'geo_lat = COALESCE(%s::numeric(9,6), %s),'
                       'geo_lon = COALESCE(%s::numeric(9,6), %s),'
                       'summary = COALESCE(%s, %s),'
                       'description = COALESCE(%s, %s),'
                       'account_id = COALESCE(%s::uuid, %s)  WHERE id = %s', (inputs['asking_price'], results['asking_price'],inputs['floor_size'],results['floor_size'],inputs['land_size'],    results['land_size'],inputs['bedroom'],results['bedroom'],inputs['toilet'],results['toilet'],inputs['type'],results['type'],inputs['tenure'],results['tenure'],inputs['unit_number'],results['unit_number'],inputs['location'],results['location'],inputs['geo_lat'],results['geo_lat'],inputs['geo_lon'],results['geo_lon'],inputs['summary'],results['summary'],inputs['description'],results['description'],str(inputs['account_id']),results['account_id'],listing_id))

        conn.commit()

        return jsonify(status='ok', msg='listing update'), 200

    except ValidationError as e:
        return jsonify(f'Validation Error: {e.messages}'), 400
    except psycopg2.IntegrityError as e:
        print(f'Constraint violated: {e}')
        return jsonify({'error': 'Constraints broken'}), 400
    except psycopg2.ProgrammingError as e:
        print(f'SQL syntax error: {e}')
        return jsonify({'error': 'SQL syntax error'}), 400
    except psycopg2.Error as e:
        print(f'Other database error: {e}')
        return jsonify({'error': 'Other database error'}), 400
    except Exception as e:
        print(f'unknown error: {e}')
        return jsonify({'error': 'Unknown error'}), 500
    finally:
        release_connection(conn)
