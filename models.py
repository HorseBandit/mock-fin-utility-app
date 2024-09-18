# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FERCTrialBalance(db.Model):
    __tablename__ = 'ferc_trial_balance'
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.Integer, nullable=False)
    account_description = db.Column(db.String(255), nullable=False)
    debit = db.Column(db.Numeric(15, 2), nullable=False)
    credit = db.Column(db.Numeric(15, 2), nullable=False)
    period = db.Column(db.String(50), nullable=False)
    entity = db.Column(db.String(100), nullable=False)

class ProForma(db.Model):
    __tablename__ = 'proforma'
    metric_id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Numeric(15, 2), nullable=False)
    period = db.Column(db.String(50), nullable=False)
    assumptions = db.Column(db.Text, nullable=False)

class DebtJuniorLienBond(db.Model):
    __tablename__ = 'debt_junior_lien_bonds'
    bond_id = db.Column(db.Integer, primary_key=True)
    issuer = db.Column(db.String(255), nullable=False)
    principal_amount = db.Column(db.Numeric(15, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    maturity_date = db.Column(db.Date, nullable=False)
    lien_position = db.Column(db.String(50), nullable=False)

class MetricDefinition(db.Model):
    __tablename__ = 'metric_definitions'
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), unique=True, nullable=False)
    formula = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    components = db.Column(db.Text, nullable=False)
