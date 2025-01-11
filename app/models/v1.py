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
        role_id (int): The foreign key referencing the user's role, can be null.
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
    transfers = db.relationship('AssetTransfer', backref='user', lazy=True)
    tickets = db.relationship('Ticket', backref='user', lazy=True)


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


class Status(TimestampMixin, db.Model):
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
    assets = db.relationship('Asset', backref='status', lazy=True)


class Asset(TimestampMixin, db.Model):
    """
    Represents an asset within the system.

    Attributes:
        id (int): The unique identifier for the asset.
        asset_tag (str): The unique asset tag, required.
        name (str): The name of the asset, required.
        category_id (int):
            The foreign key referencing the asset's category, can be null.
        assigned_to (int):
            The foreign key referencing the user the asset is
            assigned to, can be null.
        location_id (int):
            The foreign key referencing the asset's location, can be null.
        status_id (int):
            The foreign key referencing the asset's status, can be null.
        purchase_date (date): The purchase date of the asset, can be null.
        warranty_expiry (date):
            The warranty expiry date of the asset, can be null.
        configuration (str): Configuration details of the asset.
        lifecycles (list):
            The list of asset lifecycle records associated with the asset.
        software (list): The list of software associated with the asset.
        tickets (list): The list of tickets associated with the asset.
        network_devices (list):
            The list of network devices associated with the asset.
    """
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey(
            'categories.id', ondelete="SET NULL"), nullable=True)
    assigned_to = db.Column(
        db.Integer, db.ForeignKey(
            'users.id', ondelete="SET NULL"), nullable=True)
    location_id = db.Column(
        db.Integer, db.ForeignKey(
            'locations.id', ondelete="SET NULL"), nullable=True)
    status_id = db.Column(
        db.Integer, db.ForeignKey(
            'statuses.id', ondelete="SET NULL"), nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    warranty_expiry = db.Column(db.Date, nullable=True)
    configuration = db.Column(db.Text)
    lifecycles = db.relationship(
        'AssetLifecycle',
        backref='asset',
        cascade="all, delete-orphan", lazy=True)
    software = db.relationship(
        'Software',
        backref='asset',
        cascade="all, delete-orphan", lazy=True)
    tickets = db.relationship(
        'Ticket',
        backref='asset',
        cascade="all, delete-orphan", lazy=True)
    network_devices = db.relationship(
        'NetworkDevice', backref='asset',
        cascade="all, delete-orphan", lazy=True)


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
        transferred_by (int):
            The foreign key referencing the user who initiated the transfer,
                can be null.
        transferred_to (int):
            The foreign key referencing the user receiving the asset,
                can be null.
        transfer_date (datetime):
            The date and time when the asset transfer occurred, required.
        notes (str): Any additional notes related to the transfer.
    """
    __tablename__ = 'asset_transfers'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(
        db.Integer, db.ForeignKey(
            'assets.id', ondelete="CASCADE"), nullable=False)
    from_location_id = db.Column(
        db.Integer, db.ForeignKey(
            'locations.id', ondelete="SET NULL"), nullable=True)
    to_location_id = db.Column(
        db.Integer, db.ForeignKey(
            'locations.id', ondelete="SET NULL"), nullable=True)
    transferred_by = db.Column(
        db.Integer, db.ForeignKey(
            'users.id', ondelete="SET NULL"), nullable=True)
    transferred_to = db.Column(
        db.Integer, db.ForeignKey(
            'users.id', ondelete="SET NULL"), nullable=True)
    transfer_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)


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
        asset_id (int):
            The foreign key referencing the asset associated with the software,
                required.
    """
    __tablename__ = 'software'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50), nullable=True)
    license_key = db.Column(db.String(255), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    asset_id = db.Column(
        db.Integer, db.ForeignKey(
            'assets.id', ondelete="CASCADE"), nullable=False)


class NetworkDevice(TimestampMixin, db.Model):
    """
    Represents a network device associated with an asset in the system.

    Attributes:
        id (int): The unique identifier for the network device.
        ip_address (str):
            The IP address of the network device, required and unique.
        mac_address (str):
            The MAC address of the network device, can be null and unique.
        configuration (str): Configuration details of the network device.
        asset_id (int):
            The foreign key referencing the asset associated with the network
                device, required.
    """
    __tablename__ = 'network_devices'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False, unique=True)
    mac_address = db.Column(db.String(17), nullable=True, unique=True)
    configuration = db.Column(db.Text)
    asset_id = db.Column(
        db.Integer, db.ForeignKey(
            'assets.id', ondelete="CASCADE"), nullable=False)


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
    event_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)


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
