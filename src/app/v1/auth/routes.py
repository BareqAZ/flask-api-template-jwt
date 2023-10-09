# Flask imports
from flask import jsonify
from flask_jwt_extended import create_access_token

# Local imports
from app.libs.utils import api_key_required, get_api_user
from app.v1.auth import auth


@auth.route("/auth", methods=["POST"])
@api_key_required
def login():
    user = get_api_user()
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)
