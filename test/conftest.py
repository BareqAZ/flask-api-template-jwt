import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from app import create_app, db
from app.models import User

users = {
        'admin' : {'first_name': 'admin',
                   'last_name': 'admin',
                   'email': 'admin@local',
                   'is_admin': True,
                   'api_key': 'admin_api_key'},

        'user' :  {'first_name': 'user',
                   'last_name': 'user',
                   'email': 'user@local',
                   'is_admin': False,
                   'api_key': 'user_api_key'},
        }

@pytest.fixture()
def app():
    app = create_app(database_uri="sqlite://")
    with app.app_context():
        db.create_all()

        for user in users.values():
            new_user =  User(first_name=user['first_name'],
                             last_name=user['last_name'],
                            email=user['email'],
                            is_admin=user['is_admin'],
                        )
            new_user.set_api_key(user['api_key'])
            db.session.add(new_user)
            db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
