from app.api.auth import auth_bp
from app.api.department import dep_bp
from app.api.role import role_bp
from app.api.asset import asset_bp
from app.api.ticket import tic_bp
from app.api.status import status_bp
from app.api.software import sofware_bp
from app.api.location import loc_bp
from app.api.category import cat_bp
from app.api.assettransfer import at_bp
from app.api.assetlifecycle import alc_bp
from app.api.consumables.consumable import consumables_bp
from app.api.consumables.stocktransaction import stocktrans_bp
from app.api.assetLoan import asset_loan_bp
from app.api.extProvider import maintenance_bp
from app.api.provider import provider_bp

def register_blueprints(app):
    """
    Register all blueprints with the Flask application.
    """
    blueprints = [auth_bp, dep_bp, role_bp, asset_bp, tic_bp, status_bp,
                  sofware_bp, loc_bp, cat_bp, at_bp, alc_bp, consumables_bp,
                  stocktrans_bp, asset_loan_bp, maintenance_bp, provider_bp]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
