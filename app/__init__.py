from flask import Flask
from flask_cors import CORS
from app.extensions import db, migrate, bcrypt, jwt, ma
from app.blueprints.blueprint import register_blueprints
from instance.config import app_config


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    CORS(app)

    register_blueprints(app)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    return app
