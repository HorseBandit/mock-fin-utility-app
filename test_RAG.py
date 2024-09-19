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
print(index.describe_index_stats())