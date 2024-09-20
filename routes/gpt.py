from flask import Blueprint, request, jsonify
import openai
from config import Config
from models import MetricDefinition
import re
from pinecone import Pinecone

gpt_bp = Blueprint('gpt', __name__)

# Initialize Pinecone
pc = Pinecone(api_key=Config.PINECONE_API_KEY)
index = pc.Index("starter-index")

# Initialize OpenAI
openai.api_key = Config.OPENAI_API_KEY

# Function to generate embeddings
def generate_embedding(text):
    try:
        response = openai.Embedding.create(
            input=text,
            model='text-embedding-ada-002'
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None

@gpt_bp.route('/', methods=['POST'])
def handle_query_rag():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Detect if the query is asking for a metric calculation explanation
        calc_explanation_pattern = re.compile(r'how\s+(?:is|was)\s+the\s+([\w\s]+?)\s+calculated', re.IGNORECASE)
        match = calc_explanation_pattern.search(user_query)
        if match:
            metric_name = match.group(1).strip()
            metric_definition = MetricDefinition.query.filter(
                MetricDefinition.metric_name.ilike(f"%{metric_name}%")
            ).first()

            if metric_definition:
                formula = metric_definition.formula
                description = metric_definition.description
                components = metric_definition.components
                explanation = f"**{metric_definition.metric_name} Calculation**\n\n**Formula:** {formula}\n\n**Description:** {description}\n\n**Components:** {components}"
                return jsonify({'query': user_query, 'answer': explanation})
            else:
                return jsonify({'query': user_query, 'answer': f"Sorry, I couldn't find the calculation details for '{metric_name}'."})

        # Step 1: Generate embedding for the user query
        query_embedding = generate_embedding(user_query)
        if query_embedding is None:
            return jsonify({'error': 'Failed to generate embeddings for the query.'}), 500

        # Step 2: Retrieve relevant documents from Pinecone
        try:
            top_k = 5
            response = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
        except Exception as e:
            print(f"Error querying Pinecone: {str(e)}")
            return jsonify({'error': f'Error querying Pinecone: {str(e)}'}), 500

        retrieved_docs = response.get('matches', [])
        if not retrieved_docs:
            return jsonify({'query': user_query, 'answer': 'No relevant data found in Pinecone.'})

        # Step 3: Format retrieved data for GPT-4
        context = ""
        for doc in retrieved_docs:
            metadata = doc['metadata']
            if metadata['data_type'] == 'ferc_trial_balance':
                context += f"Account Number: {metadata['account_number']}, Description: {metadata['account_description']}, Debit: {metadata['debit']}, Credit: {metadata['credit']}, Period: {metadata['period']}, Entity: {metadata['entity']}\n"
            elif metadata['data_type'] == 'proforma':
                context += f"Metric ID: {metadata['metric_id']}, Name: {metadata['metric_name']}, Value: {metadata['value']}, Period: {metadata['period']}, Assumptions: {metadata['assumptions']}\n"
            elif metadata['data_type'] == 'debt_junior_lien_bonds':
                context += f"Bond ID: {metadata['bond_id']}, Issuer: {metadata['issuer']}, Principal Amount: {metadata['principal_amount']}, Interest Rate: {metadata['interest_rate']}, Maturity Date: {metadata['maturity_date']}, Lien Position: {metadata['lien_position']}\n"
            elif metadata['data_type'] == 'metric_definition':
                context += f"Metric Name: {metadata['metric_name']}, Formula: {metadata['formula']}, Description: {metadata['description']}, Components: {metadata['components']}\n"

        # Step 4: Construct the prompt
        prompt = f"""
        You are an AI assistant specialized in financial data analysis for an Electric Utility Company.
        You have access to the following financial data:

        {context}

        Using the above data, answer the following question accurately and concisely:

        Question: {user_query}

        Answer:
        """

        # Step 5: Generate response with GPT-4
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI assistant specialized in financial data analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0
            )
        except Exception as e:
            print(f"Error generating GPT-4 response: {str(e)}")
            return jsonify({'error': f'Error generating GPT-4 response: {str(e)}'}), 500

        answer = completion.choices[0].message['content'].strip()
        return jsonify({'query': user_query, 'answer': answer})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
