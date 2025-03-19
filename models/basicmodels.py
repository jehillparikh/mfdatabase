### Install Required Libraries
#Before running this code, ensure you have Flask and SQLAlchemy installed:
#pip install Flask SQLAlchemy psycopg2-binary

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


# Validators (Regex Patterns)
PAN_REGEX = r'^[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}$'
DOB_REGEX = r'^[0-9]{2}/[0-9]{2}/[0-9]{4}$'
PINCODE_REGEX = r'^\d{6}$'
PHONE_REGEX = r'^\d{10}$'
ACCOUNT_NUMBER_REGEX = r'^\d{9,16}$'
IFSC_CODE_REGEX = r'^[A-Za-z]{4}0[A-Za-z0-9]{6}$'
MICR_CODE_REGEX = r'^\d{9}$'

# Models

class Info(db.Model):
    """
    Internal User table.
    """
    __tablename__ = 'info'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)


class KycDetail(db.Model):
    """
    Stores KYC details of a user.
    """
    __tablename__ = 'kyc_detail'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('info.id'), nullable=False, unique=True)

    # Enums
    OCCUPATION_CHOICES = {'01': 'Business', '02': 'Services'}
    GENDER_CHOICES = {'M': 'Male', 'F': 'Female'}
    STATE_CHOICES = {
        'AN': 'Andaman & Nicobar', 'AP': 'Andhra Pradesh', 'AR': 'Arunachal Pradesh', 'AS': 'Assam', 'BR': 'Bihar',
        'CH': 'Chandigarh', 'CG': 'Chhattisgarh', 'DL': 'Delhi', 'GA': 'Goa', 'GJ': 'Gujarat', 'HR': 'Haryana',
        'HP': 'Himachal Pradesh', 'JK': 'Jammu & Kashmir', 'JH': 'Jharkhand', 'KA': 'Karnataka', 'KL': 'Kerala',
        'MP': 'Madhya Pradesh', 'MH': 'Maharashtra', 'MN': 'Manipur', 'ML': 'Meghalaya', 'MZ': 'Mizoram',
        'NL': 'Nagaland', 'OD': 'Odisha', 'PB': 'Punjab', 'RJ': 'Rajasthan', 'SK': 'Sikkim', 'TN': 'Tamil Nadu',
        'TG': 'Telangana', 'TR': 'Tripura', 'UP': 'Uttar Pradesh', 'UT': 'Uttarakhand', 'WB': 'West Bengal'
    }
    INCOME_SLAB_CHOICES = {31: 'Below 1 Lakh', 32: '> 1 <=5 Lacs', 33: '>5 <=10 Lacs', 34: '>10 <= 25 Lacs', 
                           35: '> 25 Lacs < = 1 Crore', 36: 'Above 1 Crore'}

    # Fields
    pan = db.Column(db.String(10), nullable=False)
    tax_status = db.Column(db.String(2), default='01')
    occ_code = db.Column(db.String(2), default='02')
    first_name = db.Column(db.String(70), nullable=False)
    middle_name = db.Column(db.String(70), nullable=True)
    last_name = db.Column(db.String(70), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(35), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    phone = db.Column(db.String(10), nullable=True)
    income_slab = db.Column(db.Integer, nullable=False)

    # Relationships
    user = relationship("Info", backref="kyc_detail")


class BankRepo(db.Model):
    """
    Repository of bank names for user's bank details.
    """
    __tablename__ = 'bank_repo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class BranchRepo(db.Model):
    """
    Repository of branch details for user's bank details.
    """
    __tablename__ = 'branch_repo'
    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('bank_repo.id'), nullable=False)
    branch_name = db.Column(db.String(100), nullable=False)
    branch_city = db.Column(db.String(35), nullable=False)
    branch_address = db.Column(db.String(250), nullable=True)
    ifsc_code = db.Column(db.String(11), unique=True, nullable=False)
    micr_code = db.Column(db.String(9), nullable=True)

    bank = relationship("BankRepo", backref="branches")


class BankDetail(db.Model):
    """
    Stores bank details of a user.
    """
    __tablename__ = 'bank_detail'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('info.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch_repo.id'), nullable=True)
    account_number = db.Column(db.String(20), nullable=False)
    account_type_bse = db.Column(db.String(2), nullable=False)

    # Relationships
    user = relationship("Info", backref="bank_details")
    branch = relationship("BranchRepo", backref="bank_details")


class Mandate(db.Model):
    """
    Stores mandates registered in BSE for a user.
    """
    __tablename__ = 'mandate'
    id = db.Column(db.String(10), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('info.id'), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('bank_detail.id'), nullable=False)

    # Enums
    STATUS_CHOICES = {
        '0': 'Created', '1': 'Cancelled', '2': 'Registered in BSE', '3': 'Form submitted to BSE',
        '4': 'Received by BSE', '5': 'Accepted by BSE', '6': 'Rejected by BSE', '7': 'Exhausted'
    }

    # Fields
    status = db.Column(db.String(1), nullable=False, default='0')
    amount = db.Column(db.Float, nullable=True)

    # Relationships
    user = relationship("Info", backref="mandates")
    bank = relationship("BankDetail", backref="mandates")

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


class MutualFund(db.Model):
    """
    Mutual Fund master table.
    """
    __tablename__ = 'mutual_fund'
    id = db.Column(db.Integer, primary_key=True)
    amc_name = db.Column(db.String(100), nullable=False)  # Asset Management Company Name
    fund_name = db.Column(db.String(100), nullable=False)
    # Other fields related to the mutual fund


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


    
# Models

class Amc(db.Model):
    """
    Asset Management Company (AMC) table.
    """
    __tablename__ = 'amc'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    short_name = db.Column(db.String(20), nullable=False)
    fund_code = db.Column(db.String(10), nullable=True)
    bse_code = db.Column(db.String(10), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)

    funds = relationship("Fund", back_populates="amc")


class Fund(db.Model):
    """
    Mutual Fund table.
    """
    __tablename__ = 'fund'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(20), nullable=True)
    amc_id = db.Column(db.Integer, db.ForeignKey('amc.id'), nullable=False)
    rta_code = db.Column(db.String(10), nullable=True)
    bse_code = db.Column(db.String(10), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    direct = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    amc = relationship("Amc", back_populates="funds")
    schemes = relationship("FundScheme", back_populates="fund")


class FundScheme(db.Model):
    """
    Different schemes under a mutual fund.
    """
    __tablename__ = 'fund_scheme'
    id = db.Column(db.Integer, primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('fund.id'), nullable=False)
    scheme_code = db.Column(db.String(10), nullable=False)
    plan = db.Column(db.String(10), nullable=False)  # e.g., "G" for Growth, "ID" for Dividend  "Direct"
    option = db.Column(db.String(10), nullable=True)  # e.g., "Payout" or "Reinvestment"
    bse_code = db.Column(db.String(10), nullable=True)

    fund = relationship("Fund", back_populates="schemes")
    details = relationship("FundSchemeDetail", back_populates="scheme", cascade="all, delete-orphan")


class FundSchemeDetail(db.Model):
    """
    Details of each scheme under a mutual fund.
    """
    __tablename__ = 'fund_scheme_detail'
    id = db.Column(db.Integer, primary_key=True)
    scheme_id = db.Column(db.Integer, db.ForeignKey('fund_scheme.id'), nullable=False)
    nav = db.Column(db.Float, nullable=False)  # Net Asset Value
    expense_ratio = db.Column(db.Float, nullable=True)  # Expense Ratio
    fund_manager = db.Column(db.String(100), nullable=True)
    aum = db.Column(db.Float, nullable=True)  # Assets Under Management
    risk_level = db.Column(db.String(10), nullable=True)  # Risk category like "Low", "Moderate", etc.
    benchmark = db.Column(db.String(100), nullable=True)  # Benchmark index

    scheme = relationship("FundScheme", back_populates="details")

# Define the MutualFunds table
class MutualFund(db.Model):
    __tablename__ = 'mutual_funds'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amc = db.Column(db.String, nullable=False)
    code = db.Column(db.Integer, nullable=False)
    scheme_name = db.Column(db.String, nullable=False)
    scheme_type = db.Column(db.String, nullable=False)
    scheme_category = db.Column(db.String, nullable=False)
    scheme_nav_name = db.Column(db.String, nullable=True)
    scheme_minimum_amount = db.Column(db.Integer, nullable=True)
    launch_date = db.Column(db.Date, nullable=True)
    closure_date = db.Column(db.Date, nullable=True)
    isin_div_payout_growth = db.Column(db.String, nullable=True)
    isin_div_reinvestment = db.Column(db.String, nullable=True)



class DividendPayout(db.Model):
    """
    Records for dividend payouts.
    """
    __tablename__ = 'dividend_payout'
    id = db.Column(db.Integer, primary_key=True)
    scheme_id = db.Column(db.Integer, db.ForeignKey('fund_scheme.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payout_date = db.Column(db.Date, nullable=False)

    scheme = relationship("FundScheme", backref="dividends")


class NavHistory(db.Model):
    """
    Historical NAV (Net Asset Value) for funds.
    """
    __tablename__ = 'nav_history'
    id = db.Column(db.Integer, primary_key=True)
    scheme_id = db.Column(db.Integer, db.ForeignKey('fund_scheme.id'), nullable=False)
    nav = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

    scheme = relationship("FundScheme", backref="nav_history")

class Returns(db.Model):
    """
    Historical returns for mutual fund schemes.
    """
    __tablename__ = 'returns'
    id = db.Column(db.Integer, primary_key=True)
    scheme_id = db.Column(db.Integer, db.ForeignKey('fund_scheme.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # Date of return calculation
    return_1m = db.Column(db.Float, nullable=True)  # 1-month return
    return_3m = db.Column(db.Float, nullable=True)  # 3-month return
    return_6m = db.Column(db.Float, nullable=True)  # 6-month return
    return_ytd = db.Column(db.Float, nullable=True)  # Year-to-date return
    return_1y = db.Column(db.Float, nullable=True)  # 1-year return
    return_3y = db.Column(db.Float, nullable=True)  # 3-year return
    return_5y = db.Column(db.Float, nullable=True)  # 5-year return
    scheme_code = db.Column(db.String(20), nullable=False)  # Unique scheme code

    scheme = relationship("FundScheme", backref="returns")

    __table_args__ = (
        db.Index('idx_scheme_date', 'scheme_id', 'date'),  # Optimize queries
        db.CheckConstraint('return_1m >= -100', name='check_return_1m'),  # Ensure reasonable return values
        db.CheckConstraint('return_3m >= -100', name='check_return_3m'),
        db.CheckConstraint('return_6m >= -100', name='check_return_6m'),
        db.CheckConstraint('return_ytd >= -100', name='check_return_ytd'),
        db.CheckConstraint('return_1y >= -100', name='check_return_1y'),
        db.CheckConstraint('return_3y >= -100', name='check_return_3y'),
        db.CheckConstraint('return_5y >= -100', name='check_return_5y'),
    )


class FundHolding(db.Model):
    """
    Represents the holdings of a mutual fund scheme.
    """
    __tablename__ = 'fund_holdings'
    id = db.Column(db.Integer, primary_key=True)
    scheme_id = db.Column(db.Integer, db.ForeignKey('fund_scheme.id'), nullable=False)  # Reference to mutual fund scheme
    security_name = db.Column(db.String(255), nullable=False)  # Name of the security (Stock/Bond/etc.)
    isin = db.Column(db.String(20), nullable=True)  # ISIN code of the security
    sector = db.Column(db.String(100), nullable=True)  # Sector classification
    asset_type = db.Column(db.String(50), nullable=False)  # Equity, Debt, REITs, etc.
    weightage = db.Column(db.Float, nullable=False)  # Percentage allocation in the scheme
    holding_value = db.Column(db.Float, nullable=True)  # Value of holding in the scheme
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Auto-update timestamp

    scheme = relationship("FundScheme", backref="fund_holdings")

    __table_args__ = (
        db.Index('idx_scheme_security', 'scheme_id', 'security_name'),  # Optimized lookup
        db.CheckConstraint('weightage >= 0', name='check_weightage'),  # No negative weightage
    )


class FundFactSheet(db.Model):
    """
    Represents the fact sheet details of a mutual fund scheme.
    """
    __tablename__ = 'fund_factsheet'
    id = db.Column(db.Integer, primary_key=True)
    scheme_id = db.Column(db.Integer, db.ForeignKey('fund_scheme.id'), nullable=False, unique=True)  # One fact sheet per scheme
    fund_manager = db.Column(db.String(255), nullable=True)  # Fund manager's name
    fund_house = db.Column(db.String(255), nullable=False)  # AMC or Fund House
    inception_date = db.Column(db.Date, nullable=True)  # Fund inception date
    expense_ratio = db.Column(db.Float, nullable=True)  # Expense ratio in percentage
    benchmark_index = db.Column(db.String(255), nullable=True)  # Benchmark index (e.g., NIFTY 50)
    category = db.Column(db.String(100), nullable=False)  # Fund category (e.g., Large Cap, Debt)
    risk_level = db.Column(db.String(50), nullable=True)  # Risk level (e.g., Low, Moderate, High)
    aum = db.Column(db.Float, nullable=True)  # Assets Under Management (AUM)
    exit_load = db.Column(db.String(50), nullable=True)  # Exit load details
    holdings_count = db.Column(db.Integer, nullable=True)  # Number of holdings in the fund
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Auto-update timestamp

    scheme = relationship("FundScheme", backref="fund_factsheet")

    __table_args__ = (
        db.Index('idx_factsheet_scheme', 'scheme_id'),  # Optimized lookup
    )


class Portfolio(db.Model):
    """
    User portfolio containing mutual fund holdings.
    """
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Reference to user
    scheme_id = db.Column(db.Integer, db.ForeignKey('fund_scheme.id'), nullable=False)  # Reference to mutual fund scheme
    scheme_code = db.Column(db.String(20), nullable=False)  # Scheme code
    units = db.Column(db.Float, nullable=False)  # Number of units held
    purchase_nav = db.Column(db.Float, nullable=False)  # NAV at purchase time
    current_nav = db.Column(db.Float, nullable=True)  # Latest NAV
    invested_amount = db.Column(db.Float, nullable=False)  # Total amount invested
    current_value = db.Column(db.Float, nullable=True)  # Current portfolio value
    date_invested = db.Column(db.Date, nullable=False)  # Date of investment
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Auto-update timestamp

    user = relationship("User", backref="portfolio")
    scheme = relationship("FundScheme", backref="portfolio")

    __table_args__ = (
        db.Index('idx_user_scheme', 'user_id', 'scheme_id'),  # Optimize user portfolio lookups
        db.CheckConstraint('units >= 0', name='check_units'),  # No negative units
        db.CheckConstraint('invested_amount >= 0', name='check_invested_amount'),  # No negative investments
    )


class FundRating(db.Model):
    """
    Ratings of mutual funds.
    """
    __tablename__ = 'fund_rating'
    id = db.Column(db.Integer, primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('fund.id'), nullable=False)
    rating_agency = db.Column(db.String(50), nullable=True)  # e.g., Morningstar
    rating_value = db.Column(db.Integer, CheckConstraint('rating_value >= 1 AND rating_value <= 5'), nullable=True)
    last_updated = db.Column(db.Date, nullable=False)

    fund = relationship("Fund", backref="ratings")


# Create all tables
with app.app_context():
    db.create_all()
