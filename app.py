from flask import Flask, Blueprint, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:zemoGED220823+@localhost:5432/recommendadsdb'
app.config['SQLALCHEMY_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '53Kr37Wt'
jwt = JWTManager(app)
db = SQLAlchemy(app)
#app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'encoding': 'utf-8'}
migrate = Migrate(app, db)


class Ad(db.Model):
    __tablename__ = 'ads'

    id = db.Column(db.Integer, primary_key=True)
    ad_copy = db.Column(db.String(255), nullable=False)
    target_audiences = db.Column(db.String(255), nullable=False)
    keyword_recommendations = db.Column(db.String(255), nullable=False)
    clicks_number = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, ad_copy, target_audiences, keyword_recommendations, clicks_number):
        self.ad_copy = ad_copy
        self.target_audiences = target_audiences
        self.keyword_recommendations = keyword_recommendations
        self.clicks_number = clicks_number

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'interactor' or 'manager'
    interactions = db.relationship('UserInteraction', backref='user', lazy=True)

    def __init__(self, username, password, role):
        self.username = username
        self.set_password(password)
        self.role = role

    def set_password(self, password):
        self.password = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class UserInteraction(db.Model):
    __tablename__ = 'user_interactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ad_id = db.Column(db.Integer, db.ForeignKey('ads.id'), nullable=False)
    clicked = db.Column(db.Boolean, default=False)


add = Blueprint('ad_blueprint', __name__)

@add.route('/')
def get_ads():
    try:
        ads = Ad.query.all()
        ads_data = []

        for ad in ads:
            ad_data = {
                'id': ad.id,
                'ad': ad.ad_copy,
                'audiences': ad.target_audiences,
                'recommendations': ad.keyword_recommendations,
                'clicks': ad.clicks_number
            }
            ads_data.append(ad_data)

        return jsonify(ads_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@add.route('/read/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    try:
        ad = Ad.query.get(ad_id)
        if ad:
            ad_data = {
                'id': ad.id,
                'ad': ad.ad_copy,
                'audiences': ad.target_audiences,
                'recommendations': ad.keyword_recommendations,
                'clicks': ad.clicks_number
            }
            return jsonify(ad_data)
        else:
            return jsonify({"error": "Ad not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@add.route('/create', methods=['POST'])
def create_ad():
    try:
        data = request.get_json()

        ad_copy = data.get('ad')
        target_audiences = data.get('audiences')
        keyword_recommendations = data.get('recommendations')
        clicks_number = data.get('clicks')

        new_ad = Ad(ad_copy=ad_copy, target_audiences=target_audiences,
                    keyword_recommendations=keyword_recommendations, clicks_number=clicks_number)

        db.session.add(new_ad)
        db.session.commit()

        return jsonify({"message": "Ad created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@add.route('/update/<int:ad_id>', methods=['PUT'])
def update_ad(ad_id):
    try:
        print('Updating...')
        ad = Ad.query.get(ad_id)
        if not ad:
            return jsonify({"error": "Ad not found"}), 404

        data = request.get_json()

        ad.ad_copy = data.get('ad')
        ad.target_audiences = data.get('audiences')
        ad.keyword_recommendations = data.get('recommendations')
        ad.clicks_number = data.get('clicks')

        db.session.commit()

        return jsonify({"message": "Ad updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@add.route('/delete/<int:ad_id>', methods=['DELETE'])
def delete_ad(ad_id):
    try:
        ad = Ad.query.get(ad_id)
        if not ad:
            return jsonify({"error": "Ad not found"}), 404

        db.session.delete(ad)
        db.session.commit()

        return jsonify({"message": "Ad deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@add.route('/recommend', methods=['GET'])
def recommend_ads():
    try:
        # Genera recomendaciones basadas en el número de clics
        recommended_ads = []

        # Ordena los anuncios por número de clics en orden descendente
        popular_ads = Ad.query.order_by(Ad.clicks_number.desc()).limit(5).all()

        for ad in popular_ads:
            recommended_ads.append({
                'id': ad.id,
                'ad': ad.ad_copy,
                'audiences': ad.target_audiences,
                'recommendations': ad.keyword_recommendations,
                'clicks': ad.clicks_number
            })

        return jsonify(recommended_ads)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
user = Blueprint('user_blueprint', __name__)
@user.route('/', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        users_data = []

        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
            users_data.append(user_data)

        return jsonify(users_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user.route('/read/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }

        return jsonify(user_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user.route('/create', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'interactor') 
        new_user = User(username=username, password=password, role=role)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user.route('/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        username = data.get('username')
        role = data.get('role')

        user.username = username
        user.role = role

        db.session.commit()

        return jsonify({"message": "User updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):

        access_token = create_access_token(identity=user.id)

        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@user.route('/secure', methods=['GET'])
@jwt_required()
def secure_route():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Hello, user {current_user}!"})

app.register_blueprint(add, url_prefix='/api/ads')
app.register_blueprint(user, url_prefix='/api/users')


def page_not_found(error):
    return '<h1>Page not found!😖</h1>', 404
app.register_error_handler(404, page_not_found)

if __name__ == '__main__':
    app.run(debug=True)
