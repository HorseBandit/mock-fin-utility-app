from pinecone import Pinecone
from pinecone import ServerlessSpec

def initialize_pinecone(api_key, index_name, cloud='Azure', region='eastus2'):
    pc = Pinecone(api_key=api_key)
    spec = ServerlessSpec(cloud=cloud, region=region)
    index = pc.Index(index_name)
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

