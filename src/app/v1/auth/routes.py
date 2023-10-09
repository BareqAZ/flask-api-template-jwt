# Flask imports
from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

# Local imports
from app import jwt
from app.libs.utils import api_key_required, get_api_user
from app.v1.auth import auth

blacklist = set()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blacklist


@auth.route("/auth", methods=["POST"])
@api_key_required
def login():
    user = get_api_user()
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=False)
def refresh():
    user_id = get_jwt_identity()
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    access_token = create_access_token(identity=user_id, fresh=False)
    return jsonify(access_token=access_token)


@auth.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200
