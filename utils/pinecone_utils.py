from pinecone import Pinecone
from pinecone import ServerlessSpec
from utils.embedding_utils import get_embeddings
import os

def initialize_pinecone(api_key, index_name, namespace='default', cloud='Azure', region='eastus2'):
    pc = Pinecone(api_key=api_key)
    spec = ServerlessSpec(cloud=cloud, region=region)
    index = pc.Index(index_name)
    index.describe_index_stats(namespace=namespace)  # Ensure the namespace is handled properly
    return index

def prepare_metadata(df):
    # Convert each row of the DataFrame into a dictionary to use as metadata
    metadata_list = []
    for _, row in df.iterrows():
        metadata = {
            'Date': str(row['Date']),
            'Revenue': row['Revenue'],
            'Cost of Goods Sold': row['Cost of Goods Sold'],
            'Operating Expenses': row['Operating Expenses'],
            'Gross Profit': row['Gross Profit'],
            'Net Income': row['Net Income']
        }
        metadata_list.append(metadata)
    return metadata_list

def upsert_documents(index, embeddings, metadata_list):
    ids = [str(i) for i in range(len(embeddings))]
    vectors = list(zip(ids, embeddings, metadata_list))
    index.upsert(vectors=vectors)

def chunk_text(text, chunk_size=500):
    """Split text into chunks of a specified size."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def upsert_ppa_documents(index, get_embeddings, ppa_file_path, chunk_size=500):
    try:
        with open(ppa_file_path, 'r', encoding='utf-8') as file:
            ppa_text = file.read()
        
        # Break the document into chunks
        chunks = [ppa_text[i:i + chunk_size] for i in range(0, len(ppa_text), chunk_size)]
        
        # Add metadata including company name, counterparty, and chunk text
        metadata_list = []
        for idx, chunk in enumerate(chunks):
            metadata_list.append({
                'chunk_id': idx,
                'description': 'Power Purchase Agreement Document',
                'document_type': 'PPA',
                'file_name': 'POWER PURCHASE AGREEMENT (PPA).txt',
                'company_name': 'Gnarly Desert Utility District',
                'counterparty': 'GigaWatt Power Broker Inc.',
                'text_chunk': chunk
            })

        # Generate embeddings for each chunk of text
        embeddings = get_embeddings(chunks)

        # Prepare the data for upsert
        vectors_to_upsert = [
            {
                'id': f"PPA-{ppa_file_path}-{idx}",
                'values': embedding,
                'metadata': metadata
            }
            for idx, (embedding, metadata) in enumerate(zip(embeddings, metadata_list))
        ]

        # Upsert the vectors to the Pinecone index
        index.upsert(vectors=vectors_to_upsert, namespace='PPAs')

        print(f"Successfully upserted the PPA document from {ppa_file_path}")

    except FileNotFoundError:
        print(f"Error: The file {ppa_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while upserting the PPA document: {e}")

