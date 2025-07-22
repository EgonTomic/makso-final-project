from models.settings import db

class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    session_token = db.Column(db.String, nullable=True)
    email_address = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)