from pinecone import Pinecone
from pinecone import ServerlessSpec

def initialize_pinecone(api_key, index_name, cloud='Azure', region='eastus2'):
    pc = Pinecone(api_key=api_key)
    spec = ServerlessSpec(cloud=cloud, region=region)
    index = pc.Index(index_name)
    return index

def upsert_documents(index, embeddings, metadata_list):
    ids = [str(i) for i in range(len(embeddings))]
    vectors = list(zip(ids, embeddings, metadata_list))
    index.upsert(vectors=vectors)
