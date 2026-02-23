from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pytz

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DryFruit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, default=0)  # Lower number = higher priority

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column(db.Boolean, default=False)
    text = db.Column(db.String(200), nullable=True)
    discount = db.Column(db.Integer, default=0)  # percentage from 1 to 100
    min_order = db.Column(db.Integer, default=0)  # minimum cart total required


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    user_address = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    items = db.Column(db.JSON, nullable=False) # store cart items as JSON
    status = db.Column(db.String(20), default="Pending") # Pending, Approved, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def created_at_ist(self):
        """Convert UTC time to India Standard Time (IST) for display."""
        ist = pytz.timezone("Asia/Kolkata")
        return self.created_at.replace(tzinfo=pytz.utc).astimezone(ist)