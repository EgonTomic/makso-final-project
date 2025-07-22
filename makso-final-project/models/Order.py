from models.settings import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    service = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False, default="scheduled")
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    customer = relationship("Customer", backref="orders")