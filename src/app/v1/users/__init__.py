from flask import Blueprint

users = Blueprint("users", __name__)

from app.v1.users import routes
