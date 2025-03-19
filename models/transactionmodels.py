
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


# Define the models based on `transactions.py`
class TransactionStatus(db.Model):
    """
    Status for transactions (purchase, redemption, switch, etc.)
    """
    __tablename__ = 'transaction_status'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)


class TransactionType(db.Model):
    """
    Type of transactions (purchase, redemption, switch, etc.)
    """
    __tablename__ = 'transaction_type'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)