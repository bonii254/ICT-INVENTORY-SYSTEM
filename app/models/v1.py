from app.extensions import db


class TimestampMixin(object):
    """
    Mixin class that adds timestamp fields for tracking creation and
    last update times.

    Attributes:
        created_at (datetime): The timestamp when the record was created.
        updated_at (datetime): The timestamp when the record was last updated.
    """
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now()
    )


class AssetTransfer(TimestampMixin, db.Model):
    """
    Represents a transfer record for an asset within the system.

    Attributes:
        id (int): The unique identifier for the asset transfer.
        asset_id (int):
            The foreign key referencing the asset being transferred, required.
        from_location_id (int):
            The foreign key referencing the asset's
                origin location, can be null.
        to_location_id (int):
            The foreign key referencing the asset's
                destination location, can be null.
        transferred_from (int):
            The foreign key referencing the user who initiated the transfer,
                can be null.
        transferred_to (int):
            The foreign key referencing the user receiving the asset,
                can be null.
        notes (str): Any additional notes related to the transfer.
    """
    __tablename__ = 'asset_transfers'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(
        db.Integer, db.ForeignKey(
            'assets.id', ondelete="CASCADE"), nullable=False)
    from_location_id = db.Column(
        db.Integer, db.ForeignKey(
            'locations.id', ondelete="SET NULL"), nullable=False)
    to_location_id = db.Column(
        db.Integer, db.ForeignKey(
            'locations.id', ondelete="SET NULL"), nullable=False)
    transferred_from = db.Column(
        db.Integer, db.ForeignKey(
            'users.id', ondelete="SET NULL"), nullable=False)
    transferred_to = db.Column(
        db.Integer, db.ForeignKey(
            'users.id', ondelete="SET NULL"), nullable=False)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "asset": self.asset.name if self.asset else None,
            "from_location": self.from_location.name if \
                self.from_location else None,
            "to_location": self.to_location.name if self.to_location else None,
            "transferred_from": self.sender.fullname if self.sender else None,
            "transferred_to": self.receiver.fullname if self.receiver else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Category(TimestampMixin, db.Model):
    """
    Represents a category to which assets can be assigned.

    Attributes:
        id (int): The unique identifier for the category.
        name (str): The name of the category, unique and required.
        description (str): A brief description of the category.
        assets (list): The list of assets associated with this category,
        with cascading delete.
    """
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    assets = db.relationship(
        'Asset', backref='category', cascade="all, delete-orphan", lazy=True)


class User(TimestampMixin, db.Model):
    """
    Represents a user in the system.
    Attributes:
        id (int): The unique identifier for the user.
        username (str): The unique username of the user, required.
        email (str): The unique email of the user, required.
        role_id (int): The foreign key referencing the user's role,
            can be null.
        department_id (int): The foreign key referencing the user's department.
        assets (list): The list of assets associated with this user.
        transfers (list): The list of asset transfers involving this user.
        tickets (list): The list of tickets raised by or assigned to this user.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    role_id = db.Column(
        db.Integer, db.ForeignKey(
            'roles.id', ondelete="SET NULL"), nullable=True)
    department_id = db.Column(
        db.Integer, db.ForeignKey(
            'departments.id', ondelete="SET NULL"), nullable=True)
    assets = db.relationship('Asset', backref='user', lazy=True)
    tickets = db.relationship('Ticket', backref='user', lazy=True)
    sent_transfers = db.relationship(
        'AssetTransfer',
        foreign_keys='AssetTransfer.transferred_from',
        backref='sender'
    )
    received_transfers = db.relationship(
        'AssetTransfer',
        foreign_keys='AssetTransfer.transferred_to',
        backref='receiver'
    )
    stock_transactions = db.relationship(
        'StockTransaction',
        backref='user',
        cascade="all, delete-orphan"
    )

class Role(TimestampMixin, db.Model):
    """
    Represents a user role in the system.

    Attributes:
        id (int): The unique identifier for the role.
        name (str): The name of the role, unique and required.
        permissions (str):
            A text field storing the permissions associated with the role.
        users (list): The list of users assigned to this role.
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    permissions = db.Column(db.Text, nullable=True)
    users = db.relationship('User', backref='role', lazy=True)


class Department(TimestampMixin, db.Model):
    """
    Represents a department within the organization.

    Attributes:
        id (int): The unique identifier for the department.
        name (str): The name of the department, unique and required.
        users (list): The list of users associated with this department.
    """
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    users = db.relationship('User', backref='department', lazy=True)
    assets = db.relationship('Asset', backref='department', lazy=True)
    transactions = db.relationship(
        'StockTransaction',
        backref='department',
        cascade="all, delete-orphan")


class Location(TimestampMixin, db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(255))
    assets = db.relationship(
        'Asset',
        backref='location',
        cascade="all, delete-orphan", lazy=True)
    transfers_from = db.relationship(
        'AssetTransfer',
        foreign_keys='AssetTransfer.from_location_id',
        backref='from_location',
        lazy=True
    )
    transfers_to = db.relationship(
        'AssetTransfer',
        foreign_keys='AssetTransfer.to_location_id',
        backref='to_location',
        lazy=True
    )


class Status(db.Model):
    """
    Represents the status of an asset in the system.

    Attributes:
        id (int): The unique identifier for the status.
        name (str): The name of the status, unique and required.
        assets (list): The list of assets associated with this status.
    """
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))
    assets = db.relationship('Asset', backref='status', lazy=True)


software_asset_association = db.Table(
    'software_asset_association',
    db.Column(
        'software_id', db.Integer,
        db.ForeignKey(
            'software.id',
            ondelete="CASCADE"), primary_key=True),
    db.Column(
        'asset_id', db.Integer,
        db.ForeignKey(
            'assets.id',
            ondelete="CASCADE"), primary_key=True)
)


class Asset(TimestampMixin, db.Model):
    """
    Represents an asset within the system.

    Attributes:
        id (int): The unique identifier for the asset.
        asset_tag (str): The unique asset tag, required.
        name (str): The name of the asset, required.
        category_id (int):
            The foreign key referencing the asset's category.
        assigned_to (int):
            The foreign key referencing the user the asset is
            assigned to.
        location_id (int):
            The foreign key referencing the asset's location.
        status_id (int):
            The foreign key referencing the asset's status.
        purchase_date (date): The purchase date of the asset.
        warranty_expiry (date):
            The warranty expiry date of the asset, can be null.
        configuration (str): Configuration details of the asset.
        lifecycles (list):
            The list of asset lifecycle records associated with the asset.
        software (list): The list of software associated with the asset.
        tickets (list): The list of tickets associated with the asset.
    """
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True, unique=True)
    mac_address = db.Column(db.String(17), nullable=True, unique=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey(
            'categories.id', ondelete="SET NULL"))
    assigned_to = db.Column(
        db.Integer, db.ForeignKey(
            'users.id', ondelete="SET NULL"))
    location_id = db.Column(
        db.Integer, db.ForeignKey(
            'locations.id', ondelete="SET NULL"))
    status_id = db.Column(
        db.Integer, db.ForeignKey(
            'statuses.id', ondelete="SET NULL"))
    purchase_date = db.Column(db.Date, nullable=True)
    warranty_expiry = db.Column(db.Date, nullable=True)
    configuration = db.Column(db.Text)
    lifecycles = db.relationship(
        'AssetLifecycle',
        backref='asset',
        cascade="all, delete-orphan", lazy=True)
    software = db.relationship(
        'Software',
        secondary=software_asset_association,
        back_populates='assets'
    )
    tickets = db.relationship(
        'Ticket',
        backref='asset',
        cascade="all, delete-orphan", lazy=True)
    department_id = db.Column(
        db.Integer, db.ForeignKey(
            'departments.id', ondelete="SET NULL"), nullable=True)
    transfers = db.relationship(
        'AssetTransfer',
        backref='asset',
        cascade="all, delete-orphan", lazy=True)


class Software(TimestampMixin, db.Model):
    """
    Represents software associated with an asset in the system.

    Attributes:
        id (int): The unique identifier for the software.
        name (str): The name of the software, required.
        version (str): The version of the software, can be null.
        license_key (str): The license key for the software, can be null.
        expiry_date (date):
            The expiry date of the software license, can be null.
        assets (list): List of assets associated with this software.
    """
    __tablename__ = 'software'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50), nullable=True)
    license_key = db.Column(db.String(255), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    assets = db.relationship(
        'Asset',
        secondary=software_asset_association,
        back_populates='software'
    )

    def to_dict(self):
        """
        Converts the Software instance into a dictionary for JSON serialization.
        """
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "license_key": self.license_key,
            "expiry_date": self.expiry_date.strftime("%Y-%m-%d"),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class AssetLifecycle(TimestampMixin, db.Model):
    """
    Represents the lifecycle events of an asset.
    Attributes:
        id (int): The unique identifier for the asset lifecycle event.
        asset_id (int):
            The foreign key referencing the asset related to the
                lifecycle event, required.
        event (str): A description of the lifecycle event, required.
        event_date (datetime):
            The date and time when the event occurred, required.
        notes (str): Any additional notes related to the lifecycle event.
    """
    __tablename__ = 'asset_lifecycles'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(
        db.Integer, db.ForeignKey(
            'assets.id', ondelete="CASCADE"), nullable=False)
    event = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)

    def to_dict(self):
        """Convert AssetLifecycle object to dictionary."""
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "event": self.event,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() \
                if self.created_at else None,
            "updated_at": self.updated_at.isoformat() \
                if self.updated_at else None
        }


class Ticket(TimestampMixin, db.Model):
    """
    Represents a support ticket related to an asset.

    Attributes:
        id (int): The unique identifier for the ticket.
        asset_id (int):
            The foreign key referencing the asset associated with the ticket,
                required.
        user_id (int): The foreign key referencing the user who created or
            is assigned to the ticket, can be null.
        status (str): The current status of the ticket, default is 'Open'.
        description (str): A description of the issue or request, required.
        resolution_notes (str): Notes describing the resolution of the ticket,
            an be null.
    """
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(
        db.Integer, db.ForeignKey(
            'assets.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey(
            'users.id', ondelete="SET NULL"), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="Open")
    description = db.Column(db.Text, nullable=False)
    resolution_notes = db.Column(db.Text)


class Consumables(TimestampMixin, db.Model):
    __tablename__ = 'consumables'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    unit_of_measure = db.Column(db.String(50))
    reorder_level = db.Column(db.Integer, default=10)
    quantity = db.Column(db.Integer, default=0)
    transactions = db.relationship(
        'StockTransaction', backref='consumable',
        cascade="all, delete-orphan")
    alerts = db.relationship(
        'Alert', backref='consumable',
        cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'brand': self.brand,
            'model': self.model,
            "quantity": self.quantity,
            'unit_of_measure': self.unit_of_measure,
            'reorder_level': self.reorder_level
        }


class StockTransaction(TimestampMixin, db.Model):
    __tablename__ = 'stock_transactions'

    id = db.Column(db.Integer, primary_key=True)
    consumable_id = db.Column(
        db.Integer, db.ForeignKey('consumables.id'), nullable=False)
    department_id = db.Column(
        db.Integer, db.ForeignKey('departments.id'), nullable=False)
    transaction_type = db.Column(
        db.Enum('IN', 'OUT', name="transaction_type"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'consumable_id': self.consumable_id,
            'department_id': self.department_id,
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class Alert(TimestampMixin, db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    consumable_id = db.Column(
        db.Integer, db.ForeignKey('consumables.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(
        'PENDING', 'RESOLVED', name="alert_status"), default='PENDING')
