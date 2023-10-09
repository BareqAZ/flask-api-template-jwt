# Flask imports
from flask import jsonify, request, url_for

# Local imports
from app import db, log
from app.libs.utils import admin_required, api_key_required, validate_email
from app.models import User
from app.v1.users import users


@users.route("", methods=["GET"])
@api_key_required
@admin_required
def get_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    max_per_page = 1000

    if per_page > max_per_page:
        return (
            jsonify(
                {
                    "error": f"Max items per page is {max_per_page}, "
                    f"provided value is {per_page}"
                }
            ),
            400,
        )
    # db.paginate will automatically read and parse the request page arguments
    # "per_page" then it will return the results accordingly
    users = db.paginate(db.select(User).order_by(User.created_at))

    next_url = (
        None
        if not users.has_next
        else f"{request.base_url}?page={page + 1}&per_page={per_page}"
    )
    prev_url = (
        None
        if not users.has_prev
        else f"{request.base_url}?page={page - 1}&per_page={per_page}"
    )

    return (
        jsonify(
            {
                "users": [
                    {
                        "id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "is_active": user.is_active,
                        "is_admin": user.is_admin,
                    }
                    for user in users
                ],
                "total_pages": users.pages,
                "total_items": users.total,
                "items_per_page": per_page,
                "next_page": next_url,
                "prev_page": prev_url,
            }
        ),
        200,
    )


@users.route("", methods=["POST"])
@api_key_required
@admin_required
def create_user():
    data = request.get_json()

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")

    if not (email and first_name and last_name):
        return jsonify({"error": "Missing required parameters"}), 400

    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"error": "user already exists"}), 400

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        is_active=data.get("is_active", True),
        is_admin=data.get("is_admin", False),
    )

    if data.get("api_key"):
        new_user_api_key = data.get("api_key")
        new_user.set_api_key(new_user_api_key)
    else:
        new_user_api_key = new_user.gen_api_key()

    try:
        db.session.add(new_user)
        db.session.commit()
        log.info('User "%s" has been added', new_user.email)
        return (
            jsonify(
                {
                    "id": new_user.id,
                    "first_name": new_user.first_name,
                    "last_name": new_user.last_name,
                    "email": new_user.email,
                    "is_active": new_user.is_active,
                    "is_admin": new_user.is_admin,
                    "api_key": new_user_api_key,
                }
            ),
            201,
        )
    except Exception as err:
        db.session.rollback()
        log.error(f"Error occurred: {str(err)}")
        return jsonify({"error": "Could not process your request"}), 500
    finally:
        db.session.close()


@users.route("/<user_id>", methods=["GET"])
@api_key_required
@admin_required
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found!"}), 404

    return (
        jsonify(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "actions": {
                    "regen-api-key": {
                        "uri": request.host_url.rstrip("/")
                        + url_for("users.gen_user_api_key", user_id=user.id),
                        "method": "POST",
                        "description": "Regenerate the user API token and return "
                        "the newely generated token",
                    },
                    "get-user-info": {
                        "uri": request.host_url.rstrip("/")
                        + url_for("users.modify_user", user_id=user.id),
                        "method": "DELETE",
                        "description": "Return the user info",
                    },
                    "delete-user": {
                        "name": "delete",
                        "uri": request.host_url.rstrip("/")
                        + url_for("users.modify_user", user_id=user.id),
                        "method": "DELETE",
                        "description": "Delete the user user",
                    },
                    "modify-user": {
                        "name": "modify",
                        "uri": request.host_url.rstrip("/")
                        + url_for("users.modify_user", user_id=user.id),
                        "method": "PATCH",
                        "description": "Edit the user information",
                    },
                },
            }
        ),
        200,
    )


@users.route("/<user_id>", methods=["PATCH"])
@api_key_required
@admin_required
def modify_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found!"}), 404

    data = request.get_json()

    existing_email = User.query.filter_by(email=data.get("email", user.email)).first()
    if existing_email and existing_email != user:
        return jsonify({"error": "Email already exists"}), 400

    new_api_key = data.get("api_key")
    if new_api_key:
        user.set_api_key(new_api_key)

    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.email = data.get("email", user.email)
    user.is_active = data.get("is_active", user.is_active)
    user.is_admin = data.get("is_admin", user.is_admin)

    try:
        db.session.commit()
        log.info('User "%s" has been modified', user.email)
        return (
            jsonify({"message": "User has been updated", "user": user.email}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        log.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Could not process your request"}), 500
    finally:
        db.session.close()


@users.route("/<user_id>", methods=["DELETE"])
@api_key_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found!"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        log.info('User "%s" has been deleted', user.email)
        return jsonify({"message": "User has been deleted"}), 200
    except Exception as e:
        db.session.rollback()
        log.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Could not process your request"}), 500
    finally:
        db.session.close()


@users.route("/<user_id>/gen-api-key", methods=["POST"])
@api_key_required
@admin_required
def gen_user_api_key(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found!"}), 404

    user_new_api_key = user.gen_api_key()

    try:
        db.session.commit()
        log.info('User "%s" API key has been regenerated', user.email)
        return (
            jsonify(
                {
                    "message": "New API key has been generated, "
                    "be sure to save this now. "
                    "It cannot be recovered once lost!",
                    "api_key": user_new_api_key,
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        log.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "Could not process your request"}), 500
    finally:
        db.session.close()
