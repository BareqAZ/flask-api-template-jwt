# Flask imports
from flask import jsonify

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
