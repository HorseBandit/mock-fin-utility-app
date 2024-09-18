# scripts/data_simulation.py
import pandas as pd
import numpy as np
from faker import Faker
import os

fake = Faker()
Faker.seed(0)
np.random.seed(0)

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Parameters
num_entries = 10000
periods = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024']
entities = ['Entity A', 'Entity B', 'Entity C']

# --- Simulate FERC Trial Balance Data ---
def simulate_ferc_trial_balance():
    data = {
        'Account_Number': np.random.randint(1000, 9999, size=num_entries),
        'Account_Description': [fake.bs().capitalize() for _ in range(num_entries)],
        'Debit': np.round(np.random.uniform(1000, 100000, size=num_entries), 2),
        'Credit': np.round(np.random.uniform(1000, 100000, size=num_entries), 2),
        'Period': np.random.choice(periods, size=num_entries),
        'Entity': np.random.choice(entities, size=num_entries)
    }
    ferc_df = pd.DataFrame(data)
    ferc_df.to_csv('data/simulated_ferc_trial_balance.csv', index=False)
    print("FERC Trial Balance data generated.")

# --- Simulate ProForma Wholesale Data ---
def simulate_proforma():
    num_proforma_entries = 5000
    proforma_metrics = ['Revenue', 'Operating Expenses', 'Net Income', 'Gross Margin', 'EBITDA']
    periods_proforma = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Year-to-Date 2023']

    proforma_data = {
        'Metric_ID': np.arange(1, num_proforma_entries + 1),
        'Metric_Name': np.random.choice(proforma_metrics, size=num_proforma_entries),
        'Value': np.round(np.random.uniform(10000, 1000000, size=num_proforma_entries), 2),
        'Period': np.random.choice(periods_proforma, size=num_proforma_entries),
        'Assumptions': [fake.sentence() for _ in range(num_proforma_entries)]
    }
    proforma_df = pd.DataFrame(proforma_data)
    proforma_df.to_csv('data/simulated_proforma_data.csv', index=False)
    print("ProForma data generated.")

# --- Simulate Debt Junior Lien Bonds Data ---
def simulate_debt_junior_lien_bonds():
    num_bonds = 1000
    lien_positions = ['Junior', 'Senior']

    debt_data = {
        'Bond_ID': np.arange(1, num_bonds + 1),
        'Issuer': [fake.company() for _ in range(num_bonds)],
        'Principal_Amount': np.round(np.random.uniform(50000, 500000, size=num_bonds), 2),
        'Interest_Rate': np.round(np.random.uniform(1.5, 10.0, size=num_bonds), 2),
        'Maturity_Date': [fake.date_between(start_date='+1y', end_date='+10y') for _ in range(num_bonds)],
        'Lien_Position': np.random.choice(lien_positions, size=num_bonds, p=[0.7, 0.3])  # More junior liens
    }
    debt_df = pd.DataFrame(debt_data)
    debt_df.to_csv('data/simulated_debt_junior_lien_bonds.csv', index=False)
    print("Debt Junior Lien Bonds data generated.")

# --- Simulate Metric Definitions Data ---
def simulate_metric_definitions():
    metric_definitions = [
        {
            'Metric_Name': 'Gross Margin',
            'Formula': '(Revenue - Cost of Goods Sold) / Revenue',
            'Description': 'Gross Margin measures the financial health by revealing the percentage of money left over from revenues after accounting for the cost of goods sold (COGS).',
            'Components': 'Revenue, Cost of Goods Sold'
        },
        {
            'Metric_Name': 'Net Power Cost',
            'Formula': 'Total Power Cost - Subsidies',
            'Description': 'Net Power Cost represents the actual cost incurred for power after accounting for any subsidies received.',
            'Components': 'Total Power Cost, Subsidies'
        },
        # Add more metric definitions as needed
    ]
    metric_definitions_df = pd.DataFrame(metric_definitions)
    metric_definitions_df.to_csv('data/simulated_metric_definitions.csv', index=False)
    print("Metric Definitions data generated.")

if __name__ == "__main__":
    simulate_ferc_trial_balance()
    simulate_proforma()
    simulate_debt_junior_lien_bonds()
    simulate_metric_definitions()
    print("All simulated data generated successfully.")
