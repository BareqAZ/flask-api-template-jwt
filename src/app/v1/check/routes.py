# Flask imports
from flask import jsonify
from flask_jwt_extended import jwt_required

# Local imports
from app.libs.utils import admin_required, api_key_required
from app.v1.check import check


@check.route("/status", methods=["GET"])
def health_check():
    return jsonify({"message": "Up and running"}), 200


@check.route("/check", methods=["GET"])
@api_key_required
def check_user_api():
    return jsonify({"message": "API token is valid"}), 200


@check.route("/admin-check", methods=["GET"])
@api_key_required
@admin_required
def check_admin_api():
    return jsonify({"message": "API token is valid"}), 200


@check.route("/jwt-check", methods=["GET"])
@jwt_required()
def check_jwt_token():
    return jsonify({"message": "JWT API token is valid"}), 200


@check.route("/jwt-admin-check", methods=["GET"])
@jwt_required()
@admin_required
def check_admin_jwt_token():
    return jsonify({"message": "JWT API token is valid"}), 200
