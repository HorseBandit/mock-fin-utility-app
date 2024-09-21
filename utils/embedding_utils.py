from langchain_openai import OpenAIEmbeddings

def get_embeddings(texts):
    embedding_model = OpenAIEmbeddings()
    embeddings = embedding_model.embed_documents(texts)
    return embeddings
