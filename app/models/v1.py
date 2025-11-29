from flask import g
from app.extensions import db
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query
from datetime import datetime, timezone


class TimestampMixin:
    """
    Adds automatic timestamp fields for creation and last update tracking.
    """
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, 
        server_default=db.func.now(), 
        server_onupdate=db.func.now()
    )

class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(128), nullable=False, unique=True)
    token_type = db.Column(db.String(20), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    revoked_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class DomainQuery(Query):
    """
    Custom Query class that automatically filters records by the
    current user's domain (set in flask.g.domain_id).
    """

    def _domain_filter(self):
        """Apply automatic domain scoping if g.domain_id is set."""
        domain_id = getattr(g, "domain_id", None)
        if (
            domain_id is not None
            and self.column_descriptions
            and hasattr(self.column_descriptions[0]["entity"], "domain_id")
        ):
            return super(DomainQuery, self).filter_by(domain_id=domain_id)
        return self

    def __iter__(self):
        """Ensure domain scoping applies to all iterations."""
        return super(DomainQuery, self._domain_filter()).__iter__()

    def get(self, ident):
        """Ensure domain scoping applies when fetching by ID."""
        obj = super(DomainQuery, self).get(ident)
        if obj and getattr(g, "domain_id", None) and getattr(obj, "domain_id", None) != g.domain_id:
            return None
        return obj

    def all(self):
        return super(DomainQuery, self._domain_filter()).all()

    def first(self):
        return super(DomainQuery, self._domain_filter()).first()

    def count(self):
        return super(DomainQuery, self._domain_filter()).count()

    def paginate(self, *args, **kwargs):
        return super(DomainQuery, self._domain_filter()).paginate(*args, **kwargs)


class BaseModel(TimestampMixin, db.Model):
    """Abstract Base class providing timestamps and domain scoping."""
    __abstract__ = True
    query_class = DomainQuery

    id = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def domain_id(cls):
        """Every model inherits a domain_id foreign key."""
        return db.Column(
            db.Integer, db.ForeignKey("domains.id"), nullable=True)

    def save(self):
        """Save model with current user's domain automatically assigned."""
        if not self.domain_id and getattr(g, "domain_id", None):
            self.domain_id = g.domain_id
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete record from the database."""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """Generic serializer (override per model)."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Domain(BaseModel):
    """Represents a management domain (e.g., ICT, Engineering)."""
    __tablename__ = 'domains'

    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))

    assets = db.relationship('Asset', backref='domain', lazy=True)
    users = db.relationship('User', backref='domain', lazy=True)
    software = db.relationship('Software', backref='domain', lazy=True)
    tickets = db.relationship('Ticket', backref='domain', lazy=True)
    categories = db.relationship('Category', backref='domain', lazy=True)
    location = db.relationship('Location', backref='domain', lazy=True)
    department = db.relationship('Department', backref='domain', lazy=True)
    statuses = db.relationship(
        'Status', backref='domain', lazy=True)
    consumables = db.relationship(
        'Consumables', backref='domain', lazy=True)
    alerts = db.relationship(
        'Alert', backref='domain', lazy=True)
    lifecycles = db.relationship(
        'AssetLifecycle', backref='domain', lazy=True)
    asset_transfers = db.relationship(
        'AssetTransfer', backref='domain', lazy=True)
    stock_transactions = db.relationship(
        'StockTransaction', backref='domain', lazy=True)


class Role(BaseModel):
    __tablename__ = 'roles'
    name = db.Column(db.String(50), nullable=False)
    permissions = db.Column(db.Text)
    users = db.relationship('User', backref='role', lazy=True)


class Department(BaseModel):
    __tablename__ = 'departments'
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', backref='department', lazy=True)
    assets = db.relationship('Asset', backref='department', lazy=True)
    transactions = db.relationship(
        'StockTransaction', backref='department', cascade="all, delete-orphan")


class Location(BaseModel):
    __tablename__ = 'locations'
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    assets = db.relationship(
        'Asset', backref='location', cascade="all, delete-orphan", lazy=True)
    consumables = db.relationship(
        'Consumables', 
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


class User(BaseModel):
    __tablename__ = 'users'
    fullname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    payroll_no = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)
    password_changed_by = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True)
    password_changed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    role_id = db.Column(
        db.Integer, 
        db.ForeignKey('roles.id', ondelete="SET NULL")
    )
    department_id = db.Column(
        db.Integer, 
        db.ForeignKey('departments.id', ondelete="SET NULL")
    )

    assets = db.relationship('Asset', backref='user', lazy=True)
    tickets = db.relationship('Ticket', backref='user', lazy=True)


class Category(BaseModel):
    __tablename__ = 'categories'
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    assets = db.relationship(
        'Asset', 
        backref='category', 
        cascade="all, delete-orphan", 
        lazy=True
    )


class Status(BaseModel):
    __tablename__ = 'statuses'
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    assets = db.relationship('Asset', backref='status', lazy=True)


software_asset_association = db.Table(
    'software_asset_association',
    db.Column(
        'software_id', 
        db.Integer, 
        db.ForeignKey('software.id', ondelete="CASCADE"), 
        primary_key=True),
    db.Column(
        'asset_id', 
        db.Integer, 
        db.ForeignKey('assets.id', ondelete="CASCADE"), 
        primary_key=True)
)


class Asset(BaseModel):
    __tablename__ = 'assets'
    asset_tag = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    model_number = db.Column(db.String(50))
    serial_number = db.Column(db.String(50), unique=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey('categories.id', ondelete="SET NULL"))
    assigned_to = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete="SET NULL"))
    location_id = db.Column(
        db.Integer, db.ForeignKey('locations.id', ondelete="SET NULL"))
    status_id = db.Column(
        db.Integer, db.ForeignKey('statuses.id', ondelete="SET NULL"))
    department_id = db.Column(
        db.Integer, db.ForeignKey('departments.id', ondelete="SET NULL"))
    purchase_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    configuration = db.Column(db.Text)

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

    def to_dict(self):
        return {
            "id": self.id,
            "asset_tag": self.asset_tag,
            "name": self.name,
            "serial_number": self.serial_number,
            "model_number": self.model_number,
            "category": self.category.name if self.category else None,
            "assigned_to": self.user.fullname if self.user else None,
            "location": self.location.name if self.location else None,
            "status": self.status.name if self.status else None,
            "department": self.department.name if self.department else None,
            "domain": self.domain.name if self.domain else None,
        }


class Software(BaseModel):
    __tablename__ = 'software'
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50))
    license_key = db.Column(db.String(255))
    expiry_date = db.Column(db.Date)
    assets = db.relationship(
        'Asset', 
        secondary=software_asset_association, 
        back_populates='software'
    )
    
    
class AssetLifecycle(BaseModel): 
    """ Tracks lifecycle events of assets. """ 
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
    
    
class AssetTransfer(BaseModel): 
    """ Represents transfer records for assets. """ 
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
    asset = db.relationship("Asset", backref="transfers")
    sender = db.relationship(
        "User", 
        foreign_keys=[transferred_from], 
        backref="sent_transfers")
    receiver = db.relationship(
        "User", 
        foreign_keys=[transferred_to], 
        backref="received_transfers")
    
    def to_dict(self): 
        return { 
                "id": self.id, 
                "asset": self.asset.name if self.asset else None, 
                "from_location": self.from_location.name if \
                    self.from_location else None, 
                "to_location": self.to_location.name if \
                    self.to_location else None, 
                "transferred_from": self.sender.fullname if \
                    self.sender else None, 
                "transferred_to": self.receiver.fullname if \
                    self.receiver else None, 
                "domain": self.domain.name if self.domain else None, 
                "notes": self.notes, 
                "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"), 
                "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }


class Ticket(BaseModel):
    __tablename__ = 'tickets'
    asset_id = db.Column(
        db.Integer, 
        db.ForeignKey('assets.id', ondelete="CASCADE"), 
        nullable=False
    )
    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete="SET NULL")
    )
    status = db.Column(db.String(50), nullable=False, default="Open")
    description = db.Column(db.Text, nullable=False)
    resolution_notes = db.Column(db.Text)


class Consumables(BaseModel):
    __tablename__ = 'consumables'
    name = db.Column(db.String(150), nullable=False, unique=True)
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    unit_of_measure = db.Column(db.String(50))
    reorder_level = db.Column(db.Integer, default=10)
    quantity = db.Column(db.Integer, default=0)
    location_id = db.Column(
        db.Integer, 
        db.ForeignKey('locations.id', 
                      ondelete="SET NULL")
    )


class StockTransaction(BaseModel):
    __tablename__ = 'stock_transactions'
    consumable_id = db.Column(
        db.Integer, 
        db.ForeignKey('consumables.id'), 
        nullable=False
    )
    department_id = db.Column(
        db.Integer, 
        db.ForeignKey('departments.id'), 
        nullable=False
    )
    transaction_type = db.Column(
        db.Enum('IN', 'OUT', name="transaction_type"), 
        nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Alert(BaseModel):
    __tablename__ = 'alerts'
    consumable_id = db.Column(
        db.Integer, 
        db.ForeignKey('consumables.id'), 
        nullable=False
    )
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(
        'PENDING', 
        'RESOLVED', 
        name="alert_status"
    ), default='PENDING')
   

class Provider(BaseModel):
    __tablename__ = 'providers'

    name = db.Column(db.String(255), nullable=False, unique=True)
    contact_person = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(100))
    address = db.Column(db.String(255))
    provider_type = db.Column(
        db.Enum('COMPANY', 'INDIVIDUAL', name='provider_type'), 
        default='COMPANY'
    )

    maintenance_records = db.relationship(
        'ExternalMaintenance', 
        back_populates='provider', 
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact_person": self.contact_person,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "provider_type": self.provider_type,
            "domain": self.domain.name if self.domain else None
        } 


class ExternalMaintenance(BaseModel):
    __tablename__ = 'external_maintenance'

    asset_id = db.Column(
        db.Integer,
        db.ForeignKey('assets.id', ondelete="CASCADE"), 
        nullable=False
    )
    parent_asset_id = db.Column(
        db.Integer, 
        db.ForeignKey('assets.id', ondelete="SET NULL"), 
        nullable=True
    )
    provider_id = db.Column(
        db.Integer, 
        db.ForeignKey('providers.id', ondelete="SET NULL"), 
        nullable=True
    )

    maintenance_type = db.Column(
        db.Enum(
            'REPAIR', 
            'REFURBISH', 
            'CALIBRATION', 
            'UPGRADE', 
            'OTHER', 
            name="maintenance_type"
        ),
        nullable=False
    )
    description = db.Column(db.Text, nullable=True)

    sent_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    expected_return_date = db.Column(db.DateTime, nullable=True)
    actual_return_date = db.Column(db.DateTime, nullable=True)

    cost_estimate = db.Column(db.Float, nullable=True)
    actual_cost = db.Column(db.Float, nullable=True)

    status = db.Column(
        db.Enum(
            'SENT', 
            'IN_PROGRESS', 
            'RETURNED', 
            'CANCELLED', 
            name="maintenance_status"
        ),
        default='SENT', nullable=False
    )

    receipt_number = db.Column(db.String(50), unique=True, nullable=False)
    collected_by = db.Column(db.String(255), nullable=True)
    received_by = db.Column(db.String(255), nullable=True)

    asset = db.relationship(
        'Asset', 
        foreign_keys=[asset_id], 
        backref='maintenance_records'
    )
    parent_asset = db.relationship(
        'Asset', 
        foreign_keys=[parent_asset_id], 
        backref='child_maintenance_records'
    )
    provider = db.relationship(
        'Provider', 
        back_populates='maintenance_records', 
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "asset": self.asset.name if self.asset else None,
            "parent_asset": self.parent_asset.name if self.parent_asset else None,
            "provider": self.provider.to_dict() if self.provider else None,
            "maintenance_type": self.maintenance_type,
            "description": self.description,
            "sent_date": self.sent_date,
            "expected_return_date": self.expected_return_date,
            "actual_return_date": self.actual_return_date,
            "cost_estimate": self.cost_estimate,
            "actual_cost": self.actual_cost,
            "status": self.status,
            "receipt_number": self.receipt_number,
            "collected_by": self.collected_by,
            "received_by": self.received_by,
            "domain": self.domain.name if getattr(self, "domain", None) else None,
        }


class AssetLoan(BaseModel):
    """
    Represents a short-term loan of an asset 
    (e.g., a laptop borrowed temporarily).
    Tracks who borrowed it, when, and whether it has been returned.
    """
    __tablename__ = 'asset_loans'

    asset_id = db.Column(
        db.Integer,
        db.ForeignKey('assets.id', ondelete="CASCADE"),
        nullable=False
    )

    borrower_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="SET NULL"),
        nullable=True
    )

    loan_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    expected_return_date = db.Column(db.DateTime, nullable=True)
    actual_return_date = db.Column(db.DateTime, nullable=True)

    status = db.Column(
        db.Enum('BORROWED', 'RETURNED', 'OVERDUE', name='loan_status'),
        nullable=False,
        default='BORROWED'
    )

    condition_before = db.Column(db.Text, nullable=True)
    condition_after = db.Column(db.Text, nullable=True)
    remarks = db.Column(db.Text, nullable=True)

    asset = db.relationship('Asset', backref='loans', lazy=True)
    borrower = db.relationship('User', backref='asset_loans', lazy=True)

    def mark_returned(self, condition_after=None):
        """Mark loan as returned and update asset status."""
        self.actual_return_date = datetime.now(timezone.utc)
        self.status = 'RETURNED'
        if condition_after:
            self.condition_after = condition_after
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "asset": self.asset.name if self.asset else None,
            "borrower": self.borrower.fullname if self.borrower else None,
            "loan_date": self.loan_date,
            "expected_return_date": self.expected_return_date,
            "actual_return_date": self.actual_return_date,
            "status": self.status,
            "condition_before": self.condition_before,
            "condition_after": self.condition_after,
            "remarks": self.remarks,
            "domain": self.domain.name if self.domain else None
        }