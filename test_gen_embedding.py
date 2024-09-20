from routes.gpt import generate_embedding

def test_generate_embedding():
    test_text = "This is a test for embedding generation."
    embedding = generate_embedding(test_text)
    assert embedding is not None, "Embedding generation failed"
    assert isinstance(embedding, list), "Embedding is not a list"
    assert len(embedding) > 0, "Embedding list is empty"
    print("Embedding generation test passed!")

# Run the test
test_generate_embedding()
