import os
from flask import Flask, jsonify
from flask_cors import CORS
from resources.tools import tools
from resources.auth import auth
from flask_jwt_extended import JWTManager
from resources.uploads import uploads
from resources.calendar import calendar


app = Flask(__name__)
# CORS(app, origins=["http://localhost:5173"])
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
CORS(app, resources={r"/*": {"origins": frontend_origin}})

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
jwt = JWTManager(app)
@jwt.expired_token_loader
@jwt.invalid_token_loader
@jwt.unauthorized_loader
@jwt.needs_fresh_token_loader
@jwt.revoked_token_loader
def my_jwt_error_callback_chicken(*args):
    return jsonify(msg='access denied'), 200

app.register_blueprint(tools, url_prefix='/api')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(uploads, url_prefix="/api")
app.register_blueprint(calendar, url_prefix="/api")

print(app.url_map)

if __name__ == '__main__':
    app.run()
    # app.run(port=5001, debug=os.getenv('DEBUG', False))
