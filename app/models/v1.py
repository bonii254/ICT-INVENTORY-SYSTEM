from app.extensions import db


class TimestampMixin(object):
    """
    Adds automatic timestamp fields for creation and last update tracking.
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


class Domain(TimestampMixin, db.Model):
    """
    Represents the management domain (e.g., ICT, Engineering).
    """
    __tablename__ = 'domains'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))

    assets = db.relationship('Asset', backref='domain', lazy=True)
    users = db.relationship('User', backref='domain', lazy=True)
    software = db.relationship('Software', backref='domain', lazy=True)
    asset_transfers = db.relationship(
        'AssetTransfer', 
        backref='domain', 
        lazy=True
    )
    tickets = db.relationship('Ticket', backref='domain', lazy=True)
    consumables = db.relationship('Consumables', backref='domain', lazy=True)
    alerts = db.relationship('Alert', backref='domain', lazy=True)
    lifecycles = db.relationship('AssetLifecycle', backref='domain', lazy=True)
    stock_transactions = db.relationship(
        'StockTransaction', 
        backref='domain', 
        lazy=True
    )


class Role(TimestampMixin, db.Model):
    """
    Represents a user role in the system.
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    permissions = db.Column(db.Text, nullable=True)

    users = db.relationship('User', backref='role', lazy=True)


class Department(TimestampMixin, db.Model):
    """
    Represents a department within the organization.
    """
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    users = db.relationship('User', backref='department', lazy=True)
    assets = db.relationship('Asset', backref='department', lazy=True)
    transactions = db.relationship(
        'StockTransaction',
        backref='department',
        cascade="all, delete-orphan"
    )


class Location(TimestampMixin, db.Model):
    """
    Represents a physical location of assets.
    """
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(255))

    assets = db.relationship(
        'Asset',
        backref='location',
        cascade="all, delete-orphan",
        lazy=True
    )
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


class User(TimestampMixin, db.Model):
    """
    Represents a system user.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

    role_id = db.Column(
        db.Integer, db.ForeignKey(
            'roles.id', 
            ondelete="SET NULL"), 
        nullable=True
    )
    department_id = db.Column(
        db.Integer, 
        db.ForeignKey('departments.id', ondelete="SET NULL"), 
        nullable=True
    )
    domain_id = db.Column(
        db.Integer, 
        db.ForeignKey('domains.id', ondelete="SET NULL"), 
        nullable=True
    )

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
    
    
class Category(TimestampMixin, db.Model):
    """
    Asset category.
    """
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))

    assets = db.relationship(
        'Asset', backref='category', cascade="all, delete-orphan", lazy=True
    )


class Status(TimestampMixin, db.Model):
    """
    Represents the status of an asset.
    """
    __tablename__ = 'statuses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))

    assets = db.relationship('Asset', backref='status', lazy=True)


software_asset_association = db.Table(
    'software_asset_association',
    db.Column('software_id', db.Integer,
              db.ForeignKey('software.id', ondelete="CASCADE"), 
              primary_key=True),
    db.Column('asset_id', db.Integer,
              db.ForeignKey('assets.id', ondelete="CASCADE"), primary_key=True)
)


class Asset(TimestampMixin, db.Model):
    """
    Represents a physical or digital asset.
    """
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    model_number = db.Column(db.String(45))
    serial_number = db.Column(db.String(45), unique=True)

    domain_id = db.Column(
        db.Integer, 
        db.ForeignKey('domains.id', ondelete="SET NULL"), 
        nullable=True
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey('categories.id', ondelete="SET NULL")
    )
    assigned_to = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete="SET NULL")
    )
    location_id = db.Column(
        db.Integer, db.ForeignKey('locations.id', ondelete="SET NULL")
    )
    status_id = db.Column(
        db.Integer, db.ForeignKey('statuses.id', ondelete="SET NULL")
    )
    department_id = db.Column(
        db.Integer, 
        db.ForeignKey('departments.id', ondelete="SET NULL"), 
        nullable=True
    )

    purchase_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    configuration = db.Column(db.Text)

    lifecycles = db.relationship(
        'AssetLifecycle',
        backref='asset',
        cascade="all, delete-orphan",
        lazy=True
    )
    software = db.relationship(
        'Software',
        secondary=software_asset_association,
        back_populates='assets'
    )
    tickets = db.relationship(
        'Ticket',
        backref='asset',
        cascade="all, delete-orphan",
        lazy=True
    )
    transfers = db.relationship(
        'AssetTransfer',
        backref='asset',
        cascade="all, delete-orphan",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "asset_tag": self.asset_tag,
            "serial_number": self.serial_number,
            "model": self.model_number,
            "category": self.category.name if self.category else None,
            "assigned_to": self.user.fullname if self.user else None,
            "location": self.location.name if self.location else None,
            "department": self.department.name if self.department else None,
            "status": self.status.name if self.status else None,
            "domain": self.domain.name if self.domain else None,
            "purchase_date": self.purchase_date.strftime(
                '%a, %d %b %Y') if self.purchase_date else None,
            "warranty_expiry": self.warranty_expiry.strftime(
                '%a, %d %b %Y') if self.warranty_expiry else None,
            "configuration": self.configuration,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class Software(TimestampMixin, db.Model):
    """
    Represents software associated with assets.
    """
    __tablename__ = 'software'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50))
    license_key = db.Column(db.String(255))
    expiry_date = db.Column(db.Date)

    domain_id = db.Column(
        db.Integer, 
        db.ForeignKey('domains.id', ondelete="SET NULL"), 
        nullable=True
    )

    assets = db.relationship(
        'Asset',
        secondary=software_asset_association,
        back_populates='software'
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "license_key": self.license_key,
            "expiry_date": self.expiry_date.strftime(
                "%Y-%m-%d") if self.expiry_date else None,
            "domain": self.domain.name if self.domain else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class AssetLifecycle(TimestampMixin, db.Model):
    """
    Tracks lifecycle events of assets.
    """
    __tablename__ = 'asset_lifecycles'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(
        db.Integer, 
        db.ForeignKey('assets.id', ondelete="CASCADE"), 
        nullable=False
    )
    event = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)

    domain_id = db.Column(
        db.Integer, 
        db.ForeignKey('domains.id', ondelete="SET NULL"), 
        nullable=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "event": self.event,
            "notes": self.notes,
            "domain": self.domain.name if self.domain else None,
            "created_at": self.created_at.isoformat() \
                if self.created_at else None,
            "updated_at": self.updated_at.isoformat() \
                if self.updated_at else None
        }


class AssetTransfer(TimestampMixin, db.Model):
    """
    Represents transfer records for assets.
    """
    __tablename__ = 'asset_transfers'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(
        db.Integer, 
        db.ForeignKey('assets.id', ondelete="CASCADE"), 
        nullable=True
    )
    from_location_id = db.Column(
        db.Integer, 
        db.ForeignKey('locations.id', ondelete="SET NULL"), 
        nullable=True
    )
    to_location_id = db.Column(
        db.Integer, 
        db.ForeignKey('locations.id', ondelete="SET NULL"), 
        nullable=True
    )
    transferred_from = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete="SET NULL"), 
        nullable=True
    )
    transferred_to = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete="SET NULL"), 
        nullable=True
    )
    notes = db.Column(db.Text)

    domain_id = db.Column(
        db.Integer, 
        db.ForeignKey('domains.id', ondelete="SET NULL"), 
        nullable=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "asset": self.asset.name if self.asset else None,
            "from_location": self.from_location.name \
                if self.from_location else None,
            "to_location": self.to_location.name \
                if self.to_location else None,
            "transferred_from": self.sender.fullname if self.sender else None,
            "transferred_to": self.receiver.fullname \
                if self.receiver else None,
            "domain": self.domain.name if self.domain else None,
            "notes": self.notes,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class Ticket(TimestampMixin, db.Model):
    """
    Represents a support ticket for an asset.
    """
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(
        db.Integer, 
        db.ForeignKey('assets.id', ondelete="CASCADE"), 
        nullable=False
    )
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete="SET NULL"), 
        nullable=True
    )
    status = db.Column(db.String(50), nullable=False, default="Open")
    description = db.Column(db.Text, nullable=False)
    resolution_notes = db.Column(db.Text)

    domain_id = db.Column(
        db.Integer, 
        db.ForeignKey('domains.id', ondelete="SET NULL"), 
        nullable=True
    )


class Consumables(TimestampMixin, db.Model):
    """
    Represents consumable inventory items.
    """
    __tablename__ = 'consumables'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    unit_of_measure = db.Column(db.String(50))
    reorder_level = db.Column(db.Integer, default=10)
    quantity = db.Column(db.Integer, default=0)

    domain_id = db.Column(
        db.Integer, 
        db.ForeignKey('domains.id', ondelete="SET NULL"), 
        nullable=True
    )

    transactions = db.relationship(
        'StockTransaction', backref='consumable',
        cascade="all, delete-orphan"
    )
    alerts = db.relationship(
        'Alert', backref='consumable',
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'brand': self.brand,
            'model': self.model,
            'unit_of_measure': self.unit_of_measure,
            'reorder_level': self.reorder_level,
            'quantity': self.quantity,
            'domain': self.domain.name if self.domain else None
        }


class StockTransaction(TimestampMixin, db.Model):
    """
    Logs stock movements for consumables.
    """
    __tablename__ = 'stock_transactions'

    id = db.Column(db.Integer, primary_key=True)
    consumable_id = db.Column(
        db.Integer, db.ForeignKey('consumables.id'), nullable=False
    )
    department_id = db.Column(
        db.Integer, db.ForeignKey('departments.id'), nullable=False
    )
    transaction_type = db.Column(
        db.Enum('IN', 'OUT', name="transaction_type"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )
    domain_id = db.Column(
        db.Integer, 
        db.ForeignKey('domains.id', ondelete="SET NULL"), 
        nullable=True
    )

    def to_dict(self):
        return {
            'id': self.id,
            'consumable': self.consumable.name if self.consumable else None,
            'department': self.department.name if self.department else None,
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'user': self.user.fullname if self.user else None,
            'domain': self.domain.name if self.domain else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class Alert(TimestampMixin, db.Model):
    """
    Represents an alert related to consumables.
    """
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    consumable_id = db.Column(
        db.Integer, db.ForeignKey('consumables.id'), nullable=False
    )
    message = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum('PENDING', 'RESOLVED', name="alert_status"), default='PENDING'
    )

    domain_id = db.Column(
        db.Integer, 
        db.ForeignKey('domains.id', ondelete="SET NULL"), 
           nullable=True
    )

    def to_dict(self):
        return {
            'id': self.id,
            'consumable': self.consumable.name if self.consumable else None,
            'message': self.message,
            'status': self.status,
            'domain': self.domain.name if self.domain else None
        }
