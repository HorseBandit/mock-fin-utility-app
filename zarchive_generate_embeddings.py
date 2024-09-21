import time
import pandas as pd
import os
import sys
from pinecone import Pinecone
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import ServerlessSpec

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from config import Config

os.environ['OPENAI_API_KEY'] = Config.OPENAI_API_KEY

# Initialize Pinecone using the new import and methods
pc = Pinecone(api_key=Config.PINECONE_API_KEY)

cloud = 'Azure'
region = 'eastus2'
index_name = "starter-index"
spec = ServerlessSpec(cloud=cloud, region=region)
#if index_name not in pc.list_indexes():
    #pc.create_index(index_name, dimension=1536)

# Use the index
import time

# check if index already exists (it shouldn't if this is first time)
if index_name not in pc.list_indexes().names():
    # if does not exist, create index
    pc.create_index(
        index_name,
        dimension=1536,  # dimensionality of text-embedding-ada-002
        metric='cosine',
        spec=spec
    )
    # wait for index to be initialized
    time.sleep(1)

# connect to index
index = pc.Index(index_name)
# view index stats

# LangChain OpenAI Embeddings model
embedding_model = OpenAIEmbeddings()

# Function to upsert data into Pinecone using LangChain
def upsert_pinecone(data_df, data_type, namespace="default", batch_size=200):
    vectors = []
    texts = []
    metadata_list = []
    unique_ids = []

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

        texts.append(text)
        metadata_list.append(metadata)
        unique_ids.append(unique_id)

        # Batch processing
        if len(texts) == batch_size:
            embeddings = embedding_model.embed_documents(texts)
            index.upsert(vectors=[{"id": unique_ids[i], "values": embeddings[i], "metadata": metadata_list[i]} for i in range(len(embeddings))], namespace=namespace)
            texts = []
            metadata_list = []
            unique_ids = []

    # Process remaining items after the loop
    if texts:
        embeddings = embedding_model.embed_documents(texts)
        index.upsert(vectors=[{"id": unique_ids[i], "values": embeddings[i], "metadata": metadata_list[i]} for i in range(len(embeddings))], namespace=namespace)
        print(f"Upserted {len(texts)} items to Pinecone.")

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