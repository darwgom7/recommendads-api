from src.models.models import db, Ad, User, UserInteraction
from src.routes.user import user as user_blueprint
from src.routes.ad import ad as ad_blueprint
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
jwt = JWTManager(app)

migrate = Migrate(app, db)
db.init_app(app)

@app.before_request
def before_request():
    if request.method == 'OPTIONS' or request.method == 'options':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return jsonify(headers), 200

app.register_blueprint(user_blueprint, url_prefix='/api/users')
app.register_blueprint(ad_blueprint, url_prefix='/api/ads')
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int("5000"), debug=True)

