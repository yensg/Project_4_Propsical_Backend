# routes/uploads.py
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import cloudinary.uploader as uploader

from marshmallow import ValidationError
from validators.tools import Validate_UUID_id

from db.db_pool import get_cursor, release_connection
import psycopg2

from flask_jwt_extended import jwt_required

uploads = Blueprint("uploads", __name__)

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename: str) -> bool: # so only True of False answer as below are using ... in ...
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@uploads.route("/upload", methods=["POST"])
@jwt_required()
def upload_image():
    # Ensure a file is present
    if "image" not in request.files:
        return jsonify(msg="no file provided (field: image)"), 400

    f = request.files["image"] # this is where we
    if f.filename == "":
        return jsonify(msg="empty filename"), 400
    if not allowed_file(f.filename): # allowed_file() is here
        return jsonify(msg="unsupported file type"), 400

    listing_id = request.form.get("listing_id")  # optional

    public_id_base = f"listings/{listing_id}/{secure_filename(f.filename).split('.')[0]}" if listing_id else None

    folder = os.getenv("CLOUDINARY_UPLOAD_FOLDER", "propsical/listings")

    # Upload to Cloudinary
    result = uploader.upload(
        f,
        folder=folder,                 # groups assets in Cloudinary
        public_id=public_id_base,      # optional deterministic id
        overwrite=True,                # replace if same public_id
        resource_type="image",         # or "auto"
        transformation=[               # optional on-the-fly eager transforms
            {"quality": "auto", "fetch_format": "auto"}
        ]
    )

    conn = None
    try:
        conn, cursor = get_cursor()
        cursor.execute('INSERT INTO cloudinary ('
                       'image, listing_id) VALUES ('
                       '%s, %s);',
                       (result['secure_url'], listing_id))
        conn.commit()

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

    # Return the secure URL + metadata you care about
    return jsonify(
        status="ok",
        public_id=result["public_id"],
        secure_url=result["secure_url"],
        width=result.get("width"),
        height=result.get("height"),
        format=result.get("format"),
        bytes=result.get("bytes"),
        msg="listing added"
    ), 200

@uploads.route("/findImages", methods=["POST"])
def find_images_by_listing_id():
    conn = None
    try:
        data = request.get_json()
        try:
            inputs = Validate_UUID_id().load(data)
        except ValidationError as err:
            return jsonify(err.messages)
        conn, cursor = get_cursor()
        cursor.execute(
            'SELECT image FROM cloudinary WHERE listing_id = %s',
            (inputs['listing_id'],))
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
