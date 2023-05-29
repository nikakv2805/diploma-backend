from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel, BlocklistModel
from schemas import UserGetSchema, UserRegisterSchema, UserSchema, MessageOnlySchema, SelfEditSchema


blp = Blueprint("Auth", "auth", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, MessageOnlySchema,
                  description="Registers new user with unique email and username")
    @blp.alt_response(409, description='Returned if user with this email or username already exists.')
    def post(self, user_data):
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
            lastname=user_data["lastname"]
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200,
                  description='Successfully log in.',
                  example={"access_token": "string", "refresh_token": "string"})
    @blp.alt_response(401,
                      description='Invalid credentials.')
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}

        abort(401, message="Invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    @blp.response(200, MessageOnlySchema)
    def post(self):
        jti = get_jwt()["jti"]
        token = BlocklistModel(
            token=jti
        )
        db.session.add(token)
        db.session.commit()

        return {"message": "Successfully logged out"}


@blp.route("/user/<int:user_id>")
class User(MethodView):
    """
    DEVELOPMENT ONLY
    """

    @blp.response(200, UserGetSchema)
    @blp.alt_response(404, description='User wasn\'t found')
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @blp.response(200, MessageOnlySchema)
    @blp.alt_response(404, description='User wasn\'t found')
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200,
                  description='Successfully refreshed token.',
                  example={"access_token": "string"})
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)

        # Make it clear that when to add the refresh token to the blocklist will depend on the app design
        jti = get_jwt()["jti"]
        token = BlocklistModel(
            token=jti
        )
        db.session.add(token)
        db.session.commit()

        return {"access_token": new_token}


@blp.route("/validate")
class TokenValidate(MethodView):
    @jwt_required()
    @blp.response(200,
                  description="Returned if JWT is valid.",
                  example={"is_owner": "string", "shop_id": 1})
    def post(self):
        jwt = get_jwt()
        return {"is_owner": jwt.get("is_owner"), "shop_id": jwt.get("shop_id")}


@blp.route("/")
class UserActions(MethodView):
    @jwt_required()
    @blp.arguments(SelfEditSchema)
    @blp.response(200, MessageOnlySchema,
                  description='Successfully changed myself.')
    @blp.alt_response(401,
                      description='Invalid credentials.')
    def put(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            user.password = pbkdf2_sha256.hash(user_data["new_password"])

            db.session.add(user)
            db.session.commit()

            return {"message": "User edited successfully"}

        abort(401, message="Invalid credentials.")

