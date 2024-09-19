from pinecone import Pinecone, ServerlessSpec
from config import Config

import os
from dotenv import load_dotenv
load_dotenv()

def test_pinecone():
    try:
        # Fetch API key from environment variables (loaded via load_dotenv)
        #api_key = os.getenv("PINECONE_API_KEY")

        #if not api_key:
            #raise ValueError("PINECONE_API_KEY not found in environment variables.")
        myapikey = Config.PINECONE_API_KEY
        # Pass the correct API key to Pinecone
        pc = Pinecone(api_key=myapikey)

        print("Pinecone initialized successfully.")
        indexes = pc.list_indexes().names()
        print(f"Available indexes: {indexes}")
    except Exception as e:
        print(f"Pinecone initialization failed: {e}")

if __name__ == "__main__":
    test_pinecone()
