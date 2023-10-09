from flask import Blueprint

check = Blueprint("check", __name__)

from app.v1.check import routes
