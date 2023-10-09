from flask import Blueprint

users = Blueprint("users", __name__)

from app.v1.users import routes  # noqa: F401, E402
