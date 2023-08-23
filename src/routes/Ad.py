from flask import Blueprint, jsonify

main = Blueprint('ad_blueprint', __name__)

# @main.route('/')


@main.route('/')
def get_ads():
    # Simulate dummy ad data
    ads = [{"id": 1, "text": "Ad 1"}, {"id": 2, "text": "Ad 2"}]
    return jsonify(ads)
