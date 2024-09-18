# scripts/load_data.py
import pandas as pd
from sqlalchemy import create_engine
from config import Config
from models import db, FERCTrialBalance, ProForma, DebtJuniorLienBond, MetricDefinition
import os

def create_database(app):
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")

def load_data_into_database():
    # Initialize database engine
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

    # Load CSV data
    ferc_df = pd.read_csv('data/simulated_ferc_trial_balance.csv')
    proforma_df = pd.read_csv('data/simulated_proforma_data.csv')
    debt_df = pd.read_csv('data/simulated_debt_junior_lien_bonds.csv')
    metric_definitions_df = pd.read_csv('data/simulated_metric_definitions.csv')

    # Load FERC Trial Balance Data
    ferc_records = ferc_df.to_dict(orient='records')
    with engine.connect() as connection:
        connection.execute(FERCTrialBalance.__table__.delete())  # Clear existing data
    with engine.begin() as connection:
        connection.execute(FERCTrialBalance.__table__.insert(), ferc_records)
    print("FERC Trial Balance data loaded.")

    # Load ProForma Data
    proforma_records = proforma_df.to_dict(orient='records')
    with engine.connect() as connection:
        connection.execute(ProForma.__table__.delete())
    with engine.begin() as connection:
        connection.execute(ProForma.__table__.insert(), proforma_records)
    print("ProForma data loaded.")

    # Load Debt Junior Lien Bonds Data
    debt_records = debt_df.to_dict(orient='records')
    with engine.connect() as connection:
        connection.execute(DebtJuniorLienBond.__table__.delete())
    with engine.begin() as connection:
        connection.execute(DebtJuniorLienBond.__table__.insert(), debt_records)
    print("Debt Junior Lien Bonds data loaded.")

    # Load Metric Definitions Data
    metric_definitions_records = metric_definitions_df.to_dict(orient='records')
    with engine.connect() as connection:
        connection.execute(MetricDefinition.__table__.delete())
    with engine.begin() as connection:
        connection.execute(MetricDefinition.__table__.insert(), metric_definitions_records)
    print("Metric Definitions data loaded.")

def main():
    from flask import Flask

    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    create_database(app)
    load_data_into_database()
    print("All data loaded into the database successfully.")

if __name__ == "__main__":
    main()
