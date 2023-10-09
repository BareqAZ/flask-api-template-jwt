# Python imports
import hashlib
import logging
import logging.handlers
import os
import sys

# Third-party imports
import toml

# Flask imports
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

# Load the settings TOML file dynamically regardless
# from where this code is being executed.
file_path = os.path.abspath(__file__)
install_path = os.path.dirname(os.path.dirname(file_path))
with open(f"{install_path}/settings.toml", "r", encoding="utf8") as file:
    settings = toml.load(file)


# Setup logging
DEBUG_MODE = settings["general"]["debug"]
log = logging.getLogger()

if DEBUG_MODE:
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter("App: %(levelname)s: [%(funcName)s] %(message)s")
else:
    log.setLevel(logging.INFO)
    formatter = logging.Formatter("App: %(levelname)s: %(message)s")

if os.path.exists("/dev/log"):
    handler = logging.handlers.SysLogHandler(address="/dev/log")
    handler.setFormatter(formatter)
    log.addHandler(handler)

# This checks if the code is running interactively from
# the terminal then prints the logs to standard out as well.
# Otherwise the logs are written to the syslog only.
if sys.stdout.isatty():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    log.addHandler(handler)

# Init database lib
db = SQLAlchemy()


def create_app(database_uri=settings["general"]["sqlite_database_uri"]):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings["general"]["secret_key"]
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    db.init_app(app)

    from app.v1.check import check
    from app.v1.users import users

    app.register_blueprint(check, url_prefix="/api/v1")
    app.register_blueprint(users, url_prefix="/api/v1/users")

    with app.app_context():
        db.create_all()
        from app.models import User

        if User.query.count() == 0:
            log.info("No users found, creating the initial superuser")
            superuser_username = settings["general"]["superuser_username"]
            superuser_api_key = settings["general"]["superuser_api_key"]
            hashed_api_key = hashlib.sha256(
                superuser_api_key.encode("utf-8")
            ).hexdigest()

            admin_user = User(
                email="superuser@localhost",
                is_admin=True,
                hashed_api_key=hashed_api_key if superuser_api_key else None,
            )

            try:
                db.session.add(admin_user)
                db.session.commit()
                log.info(f'Superuser account "{superuser_username}" has been created')
            except SQLAlchemyError as err:
                log.info("Failed creating the initial superuser, database err: %s", err)

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return jsonify({"error": err.description}), err.code

    return app
