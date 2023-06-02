from db import db
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models import UserModel
from passlib.hash import pbkdf2_sha256
from schemas import (
    MessageOnlySchema,
    SelfEditSchema,
    UserGetSchema,
    UserRegisterSchema,
    UserSchema,
)

blp = Blueprint("Auth", "auth", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, description="Registers new user with unique email and username")
    @blp.alt_response(
        409, description="Returned if user with this email or username already exists."
    )
    def post(self, user_data):
        # current_app.logger.info(type(user_data))
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")

        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            abort(409, message="A user with that email already exists.")

        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            is_owner=user_data["is_owner"],
            shop_id=user_data["shop_id"],
            surname=user_data["surname"],
            name=user_data["name"],
            lastname=user_data["lastname"],
        )
        db.session.add(user)
        db.session.commit()

        return {"id": user.id, "message": "User created successfully."}


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200, UserGetSchema, description="Successfully log in.")
    @blp.alt_response(401, description="Invalid credentials.")
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            return user

        abort(401, message="Invalid credentials.")


@blp.route("/user/<int:user_id>")
class User(MethodView):
    """
    DEVELOPMENT ONLY
    """

    @blp.response(200, UserGetSchema)
    @blp.alt_response(404, description="User wasn't found")
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @blp.response(200, MessageOnlySchema)
    @blp.alt_response(404, description="User wasn't found")
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}


@blp.route("/<int:user_id>")
class UserActions(MethodView):
    @blp.arguments(SelfEditSchema)
    @blp.response(200, MessageOnlySchema, description="Successfully changed myself.")
    @blp.alt_response(401, description="Invalid credentials.")
    def put(self, user_data, user_id):
        user = UserModel.query.get_or_404(user_id)

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            user.password = pbkdf2_sha256.hash(user_data["new_password"])

            db.session.add(user)
            db.session.commit()

            return {"message": "User edited successfully"}

        abort(401, message="Invalid credentials.")
