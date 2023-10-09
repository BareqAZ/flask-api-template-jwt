# Python imports
import hashlib
import re
from functools import wraps
from typing import Callable, Optional, Tuple

# Flask imports
from flask import abort, jsonify, request

# Local imports
from app import log
from app.models import User

"""
Here are several functions intended for quick project prototyping.

It's important to note that these functions may not be considered production ready!
Please review them carefully or substitute them with more robust solutions when
transitioning to a production environment.

You can find examples illustrating how to use these functions in
the API routes "api/routes.py".
"""


def validate_email(email: str) -> bool:
    """
    This is as good as it gets.
    More information: https://emailregex.com/index.html
    """
    email_pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    return bool(email_pattern.match(email))


def get_api_user() -> Optional[User]:
    """
    A wrapper around _get_api_user() for cleaner usability.
    This will either return a user or None.
    """
    return _get_api_user()[0]


def api_key_required(f: Callable) -> Callable:
    """
    Simple API login required decorator
    Use this to enforce using a valid API key when accessing an endpoint.
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        _, error_message, error_code = _get_api_user()
        if error_message:
            return jsonify({"error": error_message}), error_code

        return f(*args, **kwargs)

    return decorator


def admin_required(f: Callable) -> Callable:
    """
    Custom admin login required decorator.

    Use this decorator to ensure that an endpoint can only be accessed by
    an admin user.
    Note: This decorator should be placed at the bottom of the decorator
    stack for an endpoint.
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        user, _, _ = _get_api_user()
        if user and user.is_admin:
            return f(*args, **kwargs)
        else:
            abort(403)

    return decorator


def get_source_addr() -> str:
    """
    The default flask "request.remote_addr" does not work when
    using a proxy or localhost.

    This function provides the source IP of the request,
    regardless of its origin. It should function properly with
    direct requests, local requests, and requests that have been proxied.

    If you are proxying traffic from another server, such as Nginx,
    be sure to enable the forwarded header.
    More information:
    https://www.nginx.com/resources/wiki/start/topics/examples/forwarded/
    """
    if "X-Forwarded-For" in request.headers:
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    else:
        return request.remote_addr or "127.0.0.1"


def _get_api_user() -> Tuple[Optional[User], Optional[str], Optional[int]]:
    """
    This function validates the authorization token then returns
    the user database object if valid.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, "Missing or invalid Authorization header", 401

    api_key = auth_header.split("Bearer ")[1].strip()
    if not api_key:
        return None, "A valid authorization token is required", 400

    try:
        hashed_api_key = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        user = User.query.filter_by(hashed_api_key=hashed_api_key).first()
        if not user:
            return None, "A valid authorization token is required", 403

        if not user.is_active:
            return None, "Inactive account", 403

    except Exception as err:
        log.error("API auth error: %s", err)
        return None, "Internal server error", 500

    return user, None, None
