from flask import Blueprint

auth = Blueprint("auth", __name__)

from app.v1.auth import routes
