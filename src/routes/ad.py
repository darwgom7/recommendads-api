from src.models.models import db, Ad, User, UserInteraction
from flask import Blueprint, jsonify, request
from sqlalchemy.sql import func
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import cross_origin

ad = Blueprint('add_blueprint', __name__)
@ad.route('/<int:user_id>', methods=['GET'])
def get_ads_by_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        ads = Ad.query.filter_by(user_id=user_id).all()
        ads_data = []

        for ad in ads:
            ad_data = {
                'id': ad.id,
                'ad': ad.ad_copy,
                'audiences': ad.target_audiences,
                'recommendations': ad.keyword_recommendations,
                'clicks': ad.clicks_number,
                'approved': ad.approved,
                'userid': ad.user_id
            }
            ads_data.append(ad_data)

        return jsonify(ads_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ad.route('/', methods=['GET'])
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
                'clicks': ad.clicks_number,
                'approved': ad.approved,
                'userid': ad.user_id
            }
            ads_data.append(ad_data)

        return jsonify(ads_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ad.route('read/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    try:
        ad = Ad.query.get(ad_id)
        if ad:
            ad_data = {
                'id': ad.id,
                'ad': ad.ad_copy,
                'audiences': ad.target_audiences,
                'recommendations': ad.keyword_recommendations,
                'clicks': ad.clicks_number,
                'approved': ad.approved,
                'userid': ad.user_id
            }
            return jsonify(ad_data)
        else:
            return jsonify({"error": "Ad not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ad.route('create', methods=['POST'])
def create_ad():
    try:
        data = request.get_json()

        ad_copy = data.get('ad')
        target_audiences = data.get('audiences')
        keyword_recommendations = data.get('recommendations')
        clicks_number = data.get('clicks')
        approved = data.get('approved')
        user_id=data.get('userid')
        new_ad = Ad(ad_copy=ad_copy, target_audiences=target_audiences,
                    keyword_recommendations=keyword_recommendations, clicks_number=clicks_number, approved=approved, user_id=user_id)

        db.session.add(new_ad)
        db.session.commit()

        return jsonify({"message": "Ad created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cross_origin
@ad.route('update/<int:ad_id>', methods=['PUT'])
def update_ad(ad_id):
    try:
        ad = Ad.query.get(ad_id)
        if not ad:
            return jsonify({"error": "Ad not found"}), 404

        data = request.get_json()

        ad.ad_copy = data.get('ad')
        ad.target_audiences = data.get('audiences')
        ad.keyword_recommendations = data.get('recommendations')
        ad.clicks_number = data.get('clicks')
        ad.approved = data.get('approved')
        db.session.commit()

        return jsonify({"message": "Ad updated successfully"}), 200
    except Exception as e:
        print('Error:', e) 
        return jsonify({"error": str(e)}), 500

@ad.route('/update-all', methods=['PUT'])
def update_all_ads():
    try:
        data = request.get_json()

        ad_copy = data.get('ad')
        target_audiences = data.get('audiences')
        keyword_recommendations = data.get('recommendations')
        clicks_number = data.get('clicks')
        approved = data.get('approved')

        ads = Ad.query.all()

        for ad in ads:
            ad.ad_copy = ad_copy
            ad.target_audiences = target_audiences
            ad.keyword_recommendations = keyword_recommendations
            ad.clicks_number = clicks_number
            ad.approved = approved

        db.session.commit()

        return jsonify({"message": "All ads updated successfully"}), 200
    except Exception as e:
        print('Error:', e) 
        return jsonify({"error": str(e)}), 500

@ad.route('/update-all/<int:user_id>', methods=['PUT'])
def update_all_ads_user(user_id):
    try:
        data = request.get_json()

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        for ad_data in data:
            ad = Ad.query.filter_by(id=ad_data.get('id'), user_id=user_id).first()
            if not ad:
                return jsonify({"error": f"Ad not found for User {user_id}"}), 404

            ad.ad_copy = ad_data.get('ad')
            ad.target_audiences = ad_data.get('audiences')
            ad.keyword_recommendations = ad_data.get('recommendations')
            ad.clicks_number = ad_data.get('clicks')
            ad.approved = ad_data.get('approved')

        db.session.commit()

        return jsonify({"message": f"All ads for User {user_id} updated successfully"}), 200
    except Exception as e:
        print('Error:', e)
        return jsonify({"error": str(e)}), 500



from flask_cors import cross_origin

@ad.route('/click/<int:ad_id>', methods=['PUT'])
@cross_origin()
@jwt_required()
def update_ad_click(ad_id):
    try:
        user_id = get_jwt_identity()

        interaction = UserInteraction.query.filter_by(user_id=user_id, ad_id=ad_id).first()

        if interaction:
            interaction.clicked = True
        else:
            new_interaction = UserInteraction(user_id=user_id, ad_id=ad_id, clicked=True)
            db.session.add(new_interaction)

        ad = Ad.query.get(ad_id)
        ad.clicks_number += 1

        db.session.commit()

        return jsonify({
            "message": "Ad updated successfully",
            "clicks": ad.clicks_number
        }), 200
    except Exception as e:
        print('Error:', e)
        return jsonify({"error": str(e)}), 500

@ad.route('/approve/<int:ad_id>', methods=['PUT'])
def approve_ad(ad_id):
    try:
        ad = Ad.query.get(ad_id)
        if not ad:
            return jsonify({"error": "Ad not found"}), 404

        data = request.get_json()
        
        ad.ad_copy = data.get('ad')
        ad.target_audiences = data.get('audiences')
        ad.keyword_recommendations = data.get('recommendations')
        ad.clicks_number = data.get('clicks')
        ad.approved = data.get('approved')
        db.session.commit()

        return jsonify({"message": "Ad approved successfully"}), 200
    except Exception as e:
        print('Error:', e) 
        return jsonify({"error": str(e)}), 500

@ad.route('delete/<int:ad_id>', methods=['DELETE'])
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


from sqlalchemy.sql import exists

@ad.route('/popular/<int:user_id>', methods=['GET'])
def popular_ads_for_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        popular_ads_data = []

        users_with_more_than_one_click_subquery = db.session.query(
            Ad.user_id
        ).group_by(Ad.user_id).having(func.count(Ad.id) > 1).subquery()

        popular_ads = Ad.query.filter_by(user_id=user_id).filter(Ad.clicks_number > 0).order_by(Ad.clicks_number.desc()).limit(5).all()

        for ad in popular_ads:
            ad_data = {
                'id': ad.id,
                'ad': ad.ad_copy,
                'audiences': ad.target_audiences,
                'recommendations': ad.keyword_recommendations,
                'clicks': ad.clicks_number,
                'approved': ad.approved
            }
            popular_ads_data.append(ad_data)

        return jsonify(popular_ads_data)
    except Exception as e:
        print('Error: ', e)
        return jsonify({"error": str(e)}), 500



@ad.route('/popular/<int:user_id>', methods=['GET'])
def popular_ads_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        popular_ads_data = []
        
        users_with_more_than_one_click = db.session.query(
            Ad.user_id,
            func.count(Ad.id).label("click_count")
        ).group_by(Ad.user_id).having(func.count(Ad.id) > 1).subquery()

        popular_ads = db.session.query(Ad).\
            join(users_with_more_than_one_click, users_with_more_than_one_click.c.user_id == Ad.user_id).\
            filter_by(user_id=user_id).order_by(Ad.clicks_number.desc()).limit(5).all()

        for ad in popular_ads:
            ad_data = {
                'id': ad.id,
                'ad': ad.ad_copy,
                'audiences': ad.target_audiences,
                'recommendations': ad.keyword_recommendations,
                'clicks': ad.clicks_number,
                'approved': ad.approved
            }
            popular_ads_data.append(ad_data)

        return jsonify(popular_ads_data)
    except Exception as e:
        print('Error: ', e)
        return jsonify({"error": str(e)}), 500


@ad.route("interactions", methods=["POST"])
def create_user_interaction():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        ad_id = data.get("ad_id")
        clicked = data.get("clicked")

        # Verificar si el anuncio existe
        ad = db.session.get(Ad, ad_id)
        if not ad:
            return jsonify({"error": "Ad not found"}), 404

        # Crear una nueva instancia de UserInteraction y establecer los valores
        interaction = UserInteraction(user_id=user_id, ad_id=ad_id, clicked=clicked)

        # Agregar la instancia a la sesión y confirmar los cambios
        db.session.add(interaction)
        db.session.commit()

        return jsonify({"message": "User interaction recorded successfully"}), 201
    except Exception as e:
        print("Error recording user interaction:", e)
        return jsonify({"error": "An error occurred"}), 500
    
@ad.route('interactions', methods=['GET'])
def get_interactions():
    try:
        interactions = UserInteraction.query.all()

        interaction_data = []
        added_ad_ids = set()  

        for interaction in interactions:
            user = User.query.get(interaction.user_id)
            ad = Ad.query.get(interaction.ad_id)

            if ad.id not in added_ad_ids:
                interaction_entry = {
                    'interaction_id': interaction.id,
                    'user': {
                        'user_id': user.id,
                        'username': user.username,
                        'role': user.role
                    },
                    'ad': {
                        'ad_id': ad.id,
                        'ad_copy': ad.ad_copy,
                        'target_audiences': ad.target_audiences,
                        'keyword_recommendations': ad.keyword_recommendations,
                        'clicks_number': ad.clicks_number,
                        'approved': ad.approved
                    },
                    'clicked': interaction.clicked
                }
                interaction_data.append(interaction_entry)

                added_ad_ids.add(ad.id)

        return jsonify({'interactions': interaction_data})

    except Exception as e:
        print('error ', e)
        return jsonify({'error': str(e)})

@ad.route("/recommended/<int:user_id>", methods=["GET"])
def get_recommended_ads(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        interactions = user.interactions

        keywords = set()

        interacted_ad_ids = set()

        for interaction in interactions:
            ad_id = interaction.ad_id
            interacted_ad_ids.add(ad_id)
            ad = Ad.query.get(ad_id)
            if ad:
                recommendations = ad.keyword_recommendations.split(", ")
                keywords.update(recommendations)

        unique_recommended_ads = set()

        for keyword in keywords:
            ads_with_keyword = Ad.query.filter(Ad.keyword_recommendations.contains(keyword)).all()
            for ad in ads_with_keyword:
                if ad.id not in interacted_ad_ids:
                    unique_recommended_ads.add(ad)

        recommended_ads_data = [
            {
                "ad": ad.ad_copy,
                "audiences": ad.target_audiences,
                "clicks": ad.clicks_number,
                "approved": ad.approved,
                "id": ad.id,
                "recommendations": ad.keyword_recommendations
            }
            for ad in unique_recommended_ads
        ]

        return jsonify(list(recommended_ads_data)), 200
    except Exception as e:
        print("Error getting recommended ads:", e)
        return jsonify({"error": "An error occurred"}), 500


@ad.route('/reset/<int:user_id>', methods=['PUT'])
def reset(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404
        print(':::reseting:::', user_id)
        for ad in user.ads:
            ad.clicks_number = 0
            ad.approved = False

        UserInteraction.query.filter_by(user_id=user_id).delete()

        db.session.commit()

        return jsonify({"message": f"Clicks and user interactions reset for User {user_id}"}), 200
    except Exception as e:
        print('Error:', e)
        return jsonify({"error": str(e)}), 500


@ad.route('/create-all', methods=['POST'])
def create_all_ads():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({"error": "Invalid data format"}), 400

        for ad_data in data:
            ad_copy = ad_data.get('ad')
            target_audiences = ad_data.get('audiences')
            keyword_recommendations = ad_data.get('recommendations')
            clicks_number = ad_data.get('clicks')
            approved = ad_data.get('approved')
            user_id=ad_data.get('userid')
            new_ad = Ad(ad_copy=ad_copy, target_audiences=target_audiences,
                        keyword_recommendations=keyword_recommendations, clicks_number=clicks_number, approved=approved, user_id=user_id)

            db.session.add(new_ad)

        db.session.commit()

        return jsonify({"message": "Ads created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500