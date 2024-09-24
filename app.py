from flask import Flask, render_template, request
from utils.data_loader import generate_financial_data
from utils.pinecone_utils import initialize_pinecone, prepare_metadata, upsert_ppa_documents
from utils.embedding_utils import get_embeddings
from langchain_openai import OpenAIEmbeddings
import openai
import os
import pandas as pd

app = Flask(__name__)

# Set your API keys
openai_api_key = os.environ.get('OPENAI_API_KEY')
pinecone_api_key = os.environ.get('PINECONE_API_KEY')

# Initialize Pinecone
index_name = "sept-index"


# Automatically upsert the PPA document once during initialization
ppa_file_path = r"C:\Users\jrodm\Desktop\POWER PURCHASE AGREEMENT (PPA).txt"
"""
try:
    # Commented out because you've already upserted this
    index = initialize_pinecone(api_key=pinecone_api_key, index_name=index_name, namespace='PPAs')
    upsert_ppa_documents(index, get_embeddings, ppa_file_path, chunk_size=500)
    print(f"Successfully upserted the PPA document from {ppa_file_path}")
except FileNotFoundError:
    print(f"Error: The file {ppa_file_path} was not found.")
except Exception as e:
    print(f"An error occurred while upserting the PPA document: {e}")
"""
# Generate financial data
df = generate_financial_data()
index = initialize_pinecone(api_key=pinecone_api_key, index_name=index_name)
# Prepare texts and metadata for embeddings and upsert
metadata_list = prepare_metadata(df)

# Generate embeddings for each row of data (each month)
texts = df.apply(lambda row: f"Date: {row['Date']}, Revenue: {row['Revenue']}, "
                             f"Cost of Goods Sold: {row['Cost of Goods Sold']}, "
                             f"Operating Expenses: {row['Operating Expenses']}, "
                             f"Gross Profit: {row['Gross Profit']}, "
                             f"Net Income: {row['Net Income']}", axis=1)

# Get embeddings
embeddings = get_embeddings(texts.tolist())

# Upsert financial data to Pinecone (You can enable this if it wasn't done already)
# upsert_documents(index, embeddings, metadata_list)

# Define routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    prompt = request.form['prompt']
    
    # Define keywords to detect query intent (you can expand this as needed)
    ppa_keywords = ['ppa', 'purchase agreement', 'energy contract', 'power purchase']
    financial_keywords = ['revenue', 'profit', 'expenses', 'financial', 'income']

    # Simple keyword-based detection (you can improve this with NLP models)
    if any(keyword in prompt.lower() for keyword in ppa_keywords):
        # PPA-related query, use the "PPAs" namespace
        namespace = 'PPAs'
    else:
        # Default to financial data query
        namespace = ''
    
    # Get the embedding of the prompt
    embedding_model = OpenAIEmbeddings()
    prompt_embedding = embedding_model.embed_query(prompt)

    # Query Pinecone in the appropriate namespace
    results = index.query(vector=prompt_embedding, top_k=12, include_metadata=True, namespace=namespace)

    # Extract metadata for debugging and selecting relevant information
    matched_metadata = [match.metadata for match in results.matches]

    # Filter out any matches that are not relevant to the prompt
    relevant_data = pd.DataFrame(matched_metadata)

    # Convert relevant data to CSV string for the GPT model
    data_str = relevant_data.to_csv(index=False)

    # Use OpenAI GPT to generate a response
    client = openai.OpenAI(api_key=openai_api_key)
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial analysis assistant. You will be provided with financial data from a vector database. Use this data to answer the user's question. Be concise; try to use only two sentences. Perform any necessary computations."},
            {"role": "user", "content": f"Financial Data:\n{data_str}\nQuestion:\n{prompt}"}
        ]
    )
    answer = completion.choices[0].message.content

    return render_template('index.html', prompt=prompt, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
