from flask import Flask, render_template, request
from utils.data_loader import generate_financial_data
from utils.pinecone_utils import initialize_pinecone, upsert_documents
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
texts = []
metadata_list = []
for idx, row in df.iterrows():
    text = f"Date: {row['Date'].strftime('%Y-%m-%d')}, Revenue: {row['Revenue']}, Cost of Goods Sold: {row['Cost of Goods Sold']}, Operating Expenses: {row['Operating Expenses']}, Gross Profit: {row['Gross Profit']}, Net Income: {row['Net Income']}"
    texts.append(text)
    metadata_list.append({'Date': row['Date'].strftime('%Y-%m-%d')})

# Get embeddings
embeddings = get_embeddings(texts)

# Upsert to Pinecone
upsert_documents(index, embeddings, metadata_list)

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

    # Query Pinecone for relevant documents
    results = index.query(vector=prompt_embedding, top_k=5, include_metadata=True)

    # Extract matched indices
    matched_indices = [int(match.id) for match in results.matches]

    # Get the relevant data from df
    relevant_data = df.iloc[matched_indices]

    # Convert relevant_data to CSV string
    data_str = relevant_data.to_csv(index=False)

    # Use OpenAI GPT to generate a response
    client = openai.OpenAI(api_key=openai_api_key)
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial analysis assistant. You will be provided with financial data in CSV format. Use this data to answer the user's question. Perform any necessary computations."},
            {"role": "user", "content": f"Financial Data:\n{data_str}\nQuestion:\n{prompt}"}
        ]
    )
    answer = completion.choices[0].message.content

    return render_template('index.html', prompt=prompt, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
