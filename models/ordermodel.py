# Define the models
from datetime import datetime
import re
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Enum, Integer, Float
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/your_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Order(db.Model):
    """
    Orders table for tracking purchase/redemption orders.
    """
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    transaction_type_id = db.Column(db.Integer, db.ForeignKey('transaction_type.id'), nullable=False)
    mutual_fund_id = db.Column(db.Integer, db.ForeignKey('mutual_fund.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('transaction_status.id'), nullable=False)

    amount = db.Column(db.Float, nullable=False)
    units = db.Column(db.Float, nullable=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    transaction_type = relationship("TransactionType", backref="orders")
    mutual_fund = relationship("MutualFund", backref="orders")
    status = relationship("TransactionStatus", backref="orders")


class SIPOrder(db.Model):
    """
    Systematic Investment Plan (SIP) orders.
    """
    __tablename__ = 'sip_order'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    frequency = db.Column(db.String(10), nullable=False)  # Frequency like monthly, quarterly, etc.
    sip_start_date = db.Column(db.Date, nullable=False)
    sip_end_date = db.Column(db.Date, nullable=True)
    
    order = relationship("Order", backref="sip_orders")


class SwitchOrder(db.Model):
    """
    Switch orders for switching between different mutual fund schemes.
    """
    __tablename__ = 'switch_order'
    id = db.Column(db.Integer, primary_key=True)
    from_fund_id = db.Column(db.Integer, db.ForeignKey('mutual_fund.id'), nullable=False)
    to_fund_id = db.Column(db.Integer, db.ForeignKey('mutual_fund.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    
    from_fund = relationship("MutualFund", foreign_keys=[from_fund_id], backref="from_switch_orders")
    to_fund = relationship("MutualFund", foreign_keys=[to_fund_id], backref="to_switch_orders")
    order = relationship("Order", backref="switch_orders")


class RedemptionOrder(db.Model):
    """
    Redemption orders for selling units back to the mutual fund.
    """
    __tablename__ = 'redemption_order'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    amount = db.Column(db.Float, nullable=True)
    units = db.Column(db.Float, nullable=True)
    
    order = relationship("Order", backref="redemption_orders")
