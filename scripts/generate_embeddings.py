# scripts/generate_embeddings.py
import pandas as pd
import openai
import pinecone
from config import Config
import os

# Initialize OpenAI
openai.api_key = Config.OPENAI_API_KEY

# Initialize Pinecone
pinecone.init(api_key=Config.PINECONE_API_KEY, environment=Config.PINECONE_ENVIRONMENT)
index = pinecone.Index(Config.PINECONE_INDEX)

# Function to generate embeddings
def generate_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model='text-embedding-ada-002'
    )
    return response['data'][0]['embedding']

# Function to upsert data into Pinecone
def upsert_pinecone(data_df, data_type):
    vectors = []
    for idx, row in data_df.iterrows():
        if data_type == 'ferc':
            text = f"Account Number: {row['Account_Number']}, Description: {row['Account_Description']}, Debit: {row['Debit']}, Credit: {row['Credit']}, Period: {row['Period']}, Entity: {row['Entity']}"
            metadata = {
                'data_type': 'ferc_trial_balance',
                'account_number': row['Account_Number'],
                'account_description': row['Account_Description'],
                'debit': float(row['Debit']),
                'credit': float(row['Credit']),
                'period': row['Period'],
                'entity': row['Entity']
            }
            unique_id = f"ferc_{row['Account_Number']}_{idx}"
        elif data_type == 'proforma':
            text = f"Metric ID: {row['Metric_ID']}, Name: {row['Metric_Name']}, Value: {row['Value']}, Period: {row['Period']}, Assumptions: {row['Assumptions']}"
            metadata = {
                'data_type': 'proforma',
                'metric_id': int(row['Metric_ID']),
                'metric_name': row['Metric_Name'],
                'value': float(row['Value']),
                'period': row['Period'],
                'assumptions': row['Assumptions']
            }
            unique_id = f"proforma_{row['Metric_ID']}_{idx}"
        elif data_type == 'debt':
            text = f"Bond ID: {row['Bond_ID']}, Issuer: {row['Issuer']}, Principal Amount: {row['Principal_Amount']}, Interest Rate: {row['Interest_Rate']}, Maturity Date: {row['Maturity_Date']}, Lien Position: {row['Lien_Position']}"
            metadata = {
                'data_type': 'debt_junior_lien_bonds',
                'bond_id': int(row['Bond_ID']),
                'issuer': row['Issuer'],
                'principal_amount': float(row['Principal_Amount']),
                'interest_rate': float(row['Interest_Rate']),
                'maturity_date': row['Maturity_Date'].strftime('%Y-%m-%d'),
                'lien_position': row['Lien_Position']
            }
            unique_id = f"debt_{row['Bond_ID']}_{idx}"
        elif data_type == 'metric_definitions':
            text = f"Metric Name: {row['Metric_Name']}, Formula: {row['Formula']}, Description: {row['Description']}, Components: {row['Components']}"
            metadata = {
                'data_type': 'metric_definition',
                'metric_name': row['Metric_Name'],
                'formula': row['Formula'],
                'description': row['Description'],
                'components': row['Components']
            }
            unique_id = f"metric_{row['Metric_Name'].replace(' ', '_')}_{idx}"
        else:
            continue  # Unknown data type

        embedding = generate_embedding(text)
        vectors.append((unique_id, embedding, metadata))

    # Upsert in batches to Pinecone (e.g., 1000 at a time)
    batch_size = 1000
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)
        print(f"Upserted batch {i//batch_size +1} / {len(vectors)//batch_size +1}")

    print(f"All {data_type} data upserted to Pinecone.")

def main():
    # Load data from CSV
    ferc_df = pd.read_csv('data/simulated_ferc_trial_balance.csv')
    proforma_df = pd.read_csv('data/simulated_proforma_data.csv')
    debt_df = pd.read_csv('data/simulated_debt_junior_lien_bonds.csv')
    metric_definitions_df = pd.read_csv('data/simulated_metric_definitions.csv')

    # Convert 'Maturity_Date' to datetime if not already
    debt_df['Maturity_Date'] = pd.to_datetime(debt_df['Maturity_Date'])

    # Upsert FERC Trial Balance
    upsert_pinecone(ferc_df, 'ferc')

    # Upsert ProForma
    upsert_pinecone(proforma_df, 'proforma')

    # Upsert Debt Junior Lien Bonds
    upsert_pinecone(debt_df, 'debt')

    # Upsert Metric Definitions
    upsert_pinecone(metric_definitions_df, 'metric_definitions')

    print("All embeddings generated and uploaded successfully.")

if __name__ == "__main__":
    main()
