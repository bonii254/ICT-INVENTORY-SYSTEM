from app.api.auth import auth_bp
from app.api.department import dep_bp
from app.api.role import role_bp

def register_blueprints(app):
    """
    Register all blueprints with the Flask application.
    """
    blueprints = [auth_bp, dep_bp, role_bp]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
