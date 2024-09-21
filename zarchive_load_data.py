# scripts/load_data.py
import pandas as pd
from sqlalchemy import create_engine
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from config import Config
from models import db, FERCTrialBalance, ProForma, DebtJuniorLienBond, MetricDefinition
import os

def create_database(app):
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")

def validate_data(df, required_columns):
    """
    This function ensures that all required columns are non-null in the DataFrame.
    It removes rows with missing data in the required columns and logs them.
    """
    initial_count = len(df)
    df_cleaned = df.dropna(subset=required_columns)
    removed_count = initial_count - len(df_cleaned)

    if removed_count > 0:
        print(f"Warning: {removed_count} records were removed due to missing required columns: {required_columns}")
    
    return df_cleaned

def load_data_into_database():
    # Initialize database engine
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

    # Load CSV data
    ferc_df = pd.read_csv('data/simulated_ferc_trial_balance.csv')

    # Inspect column names in the DataFrame
    print("FERC Trial Balance DataFrame Columns:", ferc_df.columns)

    proforma_df = pd.read_csv('data/simulated_proforma_data.csv')
    debt_df = pd.read_csv('data/simulated_debt_junior_lien_bonds.csv')
    metric_definitions_df = pd.read_csv('data/simulated_metric_definitions.csv')

    # Validate FERC Trial Balance Data (ensure all required columns are present)
    #ferc_df = validate_data(ferc_df, required_columns=['account_number', 'debit', 'credit', 'period', 'entity'])

    # Load FERC Trial Balance Data
    ferc_records = ferc_df.to_dict(orient='records')  # Ensure all columns are included in the dictionary
    with engine.connect() as connection:
        connection.execute(FERCTrialBalance.__table__.delete())  # Clear existing data
    with engine.begin() as connection:
        connection.execute(FERCTrialBalance.__table__.insert(), ferc_records)
    print("FERC Trial Balance data loaded.")

    # Validate and Load ProForma Data
    proforma_df = validate_data(proforma_df, required_columns=['metric_name', 'value', 'period'])
    proforma_records = proforma_df.to_dict(orient='records')
    with engine.connect() as connection:
        connection.execute(ProForma.__table__.delete())
    with engine.begin() as connection:
        connection.execute(ProForma.__table__.insert(), proforma_records)
    print("ProForma data loaded.")

    # Validate and Load Debt Junior Lien Bonds Data
    debt_df = validate_data(debt_df, required_columns=['issuer', 'principal_amount', 'maturity_date'])
    debt_records = debt_df.to_dict(orient='records')
    with engine.connect() as connection:
        connection.execute(DebtJuniorLienBond.__table__.delete())
    with engine.begin() as connection:
        connection.execute(DebtJuniorLienBond.__table__.insert(), debt_records)
    print("Debt Junior Lien Bonds data loaded.")

    # Validate and Load Metric Definitions Data
    metric_definitions_df = validate_data(metric_definitions_df, required_columns=['metric_name', 'formula'])
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
