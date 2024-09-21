import time
import pandas as pd
import os
import sys
from pinecone import Pinecone
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import ServerlessSpec




# Initialize Pinecone using the new import and methods
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

cloud = 'Azure'
region = 'eastus2'
index_name = "sept-index"
spec = ServerlessSpec(cloud=cloud, region=region)
#if index_name not in pc.list_indexes():
    #pc.create_index(index_name, dimension=1536)



# connect to index
index = pc.Index(index_name)
# view index stats
print(index.describe_index_stats())

vector_ids = ['0', '1', '2','11', '12']  # Replace with actual vector IDs you want to inspect
result = index.fetch(ids=vector_ids)
print(result)