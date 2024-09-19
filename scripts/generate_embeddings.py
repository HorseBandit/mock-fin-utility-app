# scripts/generate_embeddings.py
import pandas as pd
from openai import OpenAI
from pinecone import Pinecone
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from config import Config
import os

# Initialize OpenAI
client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

myapikey = Config.PINECONE_API_KEY
pc = Pinecone(api_key=myapikey)
index = pc.list_indexes().names()

# Function to generate embeddings using the updated OpenAI API
def generate_embedding(text, model="text-embedding-3-small"):
    try:
        # Replace newlines in the text
        text = text.replace("\n", " ")
        # Call OpenAI's new API to generate embeddings
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding for text '{text}': {e}")
        return None

# Function to upsert data into Pinecone
def upsert_pinecone(data_df, data_type):
    vectors = []
    for idx, row in data_df.iterrows():
        if data_type == 'ferc':
            text = f"account number: {row['account_number']}, description: {row['account_description']}, debit: {row['debit']}, credit: {row['credit']}, period: {row['period']}, entity: {row['entity']}"
            metadata = {
                'data_type': 'ferc_trial_balance',
                'account_number': row['account_number'],
                'account_description': row['account_description'],
                'debit': float(row['debit']),
                'credit': float(row['credit']),
                'period': row['period'],
                'entity': row['entity']
            }
            unique_id = f"ferc_{row['account_number']}_{idx}"
        elif data_type == 'proforma':
            text = f"metric id: {row['metric_id']}, name: {row['metric_name']}, value: {row['value']}, period: {row['period']}, assumptions: {row['assumptions']}"
            metadata = {
                'data_type': 'proforma',
                'metric_id': int(row['metric_id']),
                'metric_name': row['metric_name'],
                'value': float(row['value']),
                'period': row['period'],
                'assumptions': row['assumptions']
            }
            unique_id = f"proforma_{row['metric_id']}_{idx}"
        elif data_type == 'debt':
            text = f"bond id: {row['bond_id']}, issuer: {row['issuer']}, principal amount: {row['principal_amount']}, interest rate: {row['interest_rate']}, maturity date: {row['maturity_date']}, lien position: {row['lien_position']}"
            metadata = {
                'data_type': 'debt_junior_lien_bonds',
                'bond_id': int(row['bond_id']),
                'issuer': row['issuer'],
                'principal_amount': float(row['principal_amount']),
                'interest_rate': float(row['interest_rate']),
                'maturity_date': row['maturity_date'].strftime('%Y-%m-%d'),
                'lien_position': row['lien_position']
            }
            unique_id = f"debt_{row['bond_id']}_{idx}"
        elif data_type == 'metric_definitions':
            text = f"metric name: {row['metric_name']}, formula: {row['formula']}, description: {row['description']}, components: {row['components']}"
            metadata = {
                'data_type': 'metric_definition',
                'metric_name': row['metric_name'],
                'formula': row['formula'],
                'description': row['description'],
                'components': row['components']
            }
            unique_id = f"metric_{row['metric_name'].replace(' ', '_')}_{idx}"
        else:
            continue  # Unknown data type

        # Generate embedding
        embedding = generate_embedding(text)
        if embedding is not None:
            vectors.append((unique_id, embedding, metadata))

    # Upsert in batches to Pinecone (e.g., 1000 at a time)
    batch_size = 1000
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"Upserted batch {i // batch_size + 1} / {len(vectors) // batch_size + 1}")
        except Exception as e:
            print(f"Error during Pinecone upsert: {e}")

    print(f"All {data_type} data upserted to Pinecone.")

def main():
    # Load data from CSV
    ferc_df = pd.read_csv('data/simulated_ferc_trial_balance.csv')
    proforma_df = pd.read_csv('data/simulated_proforma_data.csv')
    debt_df = pd.read_csv('data/simulated_debt_junior_lien_bonds.csv')
    metric_definitions_df = pd.read_csv('data/simulated_metric_definitions.csv')

    # Convert 'maturity_date' to datetime if not already
    debt_df['maturity_date'] = pd.to_datetime(debt_df['maturity_date'])

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
