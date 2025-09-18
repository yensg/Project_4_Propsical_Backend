from flask import request, jsonify, Blueprint
from db.db_pool import get_cursor, release_connection
import psycopg2

from marshmallow import ValidationError
from validators.tools import ValidateCreateListing

from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo



calendar = Blueprint('calendar', __name__)

@calendar.route('/blockCalendar', methods=['POST'])
@jwt_required()
def block_calendar_dates():
    conn = None

    # try:
    #     data = request.get_json()
    #     inputs = ValidateCreateListing().load(data)
    # except ValidationError as err:
    #     return jsonify(err.messages), 400

    try:
        inputs = request.get_json()
        dates = inputs["dates"]
        print(dates)
        timezone = ZoneInfo(inputs["timezone"])
        def to_time_zone_iso(dt):
            if isinstance(dt, datetime):
                return dt.astimezone(timezone).isoformat(timespec="seconds")
            return dt

        conn, cursor = get_cursor()
        appointments = []
        for d in dates:
            dtstart = datetime.fromisoformat(d).astimezone(timezone)
            dtend = dtstart + timedelta(days=1)

            cursor.execute('INSERT INTO appointments (dtstart, dtend, timeslot_is_blocked, date_is_blocked, summary, description, listing_id, timeZone, account_id)'
                           'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *',
                           (dtstart, dtend, False , True, inputs['summary'], inputs['description'], inputs['listing_id'], inputs['timezone'],inputs['account_id']))
            each = cursor.fetchone()
            for k in ("dtstart", "dtend", "dtstamp"):
                if k in each:
                    each[k] = to_time_zone_iso(each[k])
            appointments.append(each)

        conn.commit()

        # Method 2:
        # cursor.execute('SELECT * FROM appointments WHERE listing_id = %s', (inputs['listing_id'],))
        # appointments = cursor.fetchall()
        # for each in appointments:
        #     for k in ("dtstart", "dtend", "dtstamp"):
        #         if k in each:
        #             each[k] = to_time_zone_iso(each[k])

        return jsonify({"status": 'ok', "msg": 'listing added', "appointments":appointments}), 200 #

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

@calendar.route('/calendar', methods=['POST'])
def create_calendar():
    conn = None

    # try:
    #     data = request.get_json()
    #     inputs = ValidateCreateListing().load(data)
    # except ValidationError as err:
    #     return jsonify(err.messages), 400

    try:
        inputs = request.get_json()
        date = inputs["dtstart"]
        print(inputs)
        timezone = ZoneInfo(inputs['timezone'])
        def to_time_zone_iso(dt):
            # dt is a Python datetime (psycopg2 gives you aware datetimes for TIMESTAMPTZ)
            if isinstance(dt, datetime):
                return dt.astimezone(timezone).isoformat(timespec="seconds")  # e.g. 2025-06-12T11:15:00+08:00
            return dt

        dtstart = datetime.fromisoformat(date).astimezone(timezone)
        dtend = dtstart + timedelta(minutes=15)

        conn, cursor = get_cursor()
        cursor.execute('INSERT INTO appointments (dtstart, dtend, timeslot_is_blocked, summary, description, listing_id, status, timeZone, account_id)'
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *',
                       (dtstart, dtend, inputs['timeslot_is_blocked'], inputs['summary'], inputs['description'], inputs['listing_id'], inputs['status'], inputs['timezone'], inputs['account_id']))

        appointment = cursor.fetchone()
        # cols = [desc[0] for desc in cursor.description] Dont have to do this please RealDictCursor already done the job
        # appt = dict(zip(cols, row))
        for k in ("dtstart", "dtend", "dtstamp"):
            if k in appointment:
                appointment[k] = to_time_zone_iso(appointment[k])
        conn.commit()
        return jsonify({"status": 'ok', "msg": 'listing added', "appointment":appointment}), 200 #

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

@calendar.route('/appointments', methods=['POST'])
def find_appointments_by_listing_id():
    conn = None

    # try:
    #     data = request.get_json()
    #     inputs = ValidateCreateListing().load(data)
    # except ValidationError as err:
    #     return jsonify(err.messages), 400

    try:
        inputs = request.get_json()

        conn, cursor = get_cursor()
        cursor.execute('SELECT * FROM appointments WHERE listing_id = %s', (inputs['listing_id'],))

        appointments = cursor.fetchall()
        for each in appointments:
            timezone = ZoneInfo(each['timezone'])

            def to_time_zone_iso(dt):
                if isinstance(dt, datetime):
                    return dt.astimezone(timezone).isoformat(timespec="seconds")  # e.g. 2025-06-12T11:15:00+08:00
                return dt

            for k in ("dtstart", "dtend", "dtstamp"):
                if k in each:
                    each[k] = to_time_zone_iso(each[k])

        conn.commit()
        return jsonify(appointments), 200 #

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

@calendar.route('/deleteBlockedDates', methods=['DELETE'])
@jwt_required()
def delete_blocked_date_by_uid():
    conn = None
    # try:
    #     data = request.get_json()
    #     inputs = Validate_UUID_id().load(data)
    # except ValidationError as err:
    #     return jsonify(err.messages), 400

    try:
        inputs = request.get_json()
        conn, cursor = get_cursor()
        cursor.execute('DELETE FROM appointments WHERE uid = %s', (inputs['uid'],))
        conn.commit()
        return jsonify(status='ok', msg='dates unblocked'), 200

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

@calendar.route('/deleteAppointments', methods=['DELETE'])
@jwt_required()
def delete_appointment_by_uid():
    conn = None
    # try:
    #     data = request.get_json()
    #     inputs = Validate_UUID_id().load(data)
    # except ValidationError as err:
    #     return jsonify(err.messages), 400

    try:
        inputs = request.get_json()
        conn, cursor = get_cursor()
        cursor.execute('DELETE FROM appointments WHERE uid = %s', (inputs['uid'],))
        conn.commit()
        return jsonify(status='ok', msg='dates deleted'), 200

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