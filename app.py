from flask import Flask, render_template, request
from utils.data_loader import generate_financial_data
from utils.pinecone_utils import initialize_pinecone, upsert_documents, prepare_metadata
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
index = initialize_pinecone(api_key=pinecone_api_key, index_name=index_name)

# Generate financial data
df = generate_financial_data()

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

# Upsert to Pinecone
#upsert_documents(index, embeddings, metadata_list)

# Define routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    prompt = request.form['prompt']

    # Get the embedding of the prompt
    embedding_model = OpenAIEmbeddings()
    prompt_embedding = embedding_model.embed_query(prompt)

    # Query Pinecone for relevant documents (set k=12 for all months)
    results = index.query(vector=prompt_embedding, top_k=12, include_metadata=True)

    # Extract metadata for debugging and selecting relevant months
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
            {"role": "system", "content": "You are a financial analysis assistant. You will be provided with financial data from a vector database. Use this data to answer the user's question. Perform any necessary computations."},
            {"role": "user", "content": f"Financial Data:\n{data_str}\nQuestion:\n{prompt}"}
        ]
    )
    answer = completion.choices[0].message.content

    return render_template('index.html', prompt=prompt, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
