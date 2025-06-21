from flask import Flask, jsonify
from flask_cors import CORS # type: ignore
from app.extensions import db, migrate, bcrypt, jwt, ma
from app.blueprints.blueprint import register_blueprints
from instance.config import app_config


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    CORS(app, resources={
        r"/*": {"origins": "http://localhost:3000"}},
        supports_credentials=True)

    register_blueprints(app)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({"error": "Authentication required"}), 401

    return app
