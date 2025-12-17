import chromadb
from chromadb.utils import embedding_functions

# Connect to your database
client = chromadb.PersistentClient(path="./rag/chroma_db")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Get your collection
collection = client.get_collection(
    name="dialogic_inquiry",
    embedding_function=sentence_transformer_ef
)

# Check how many items are stored
print(f"Total documents in collection: {collection.count()}")
print("\n" + "="*60 + "\n")

# Test query - replace with something relevant to your conversations
test_query = "data visualization"  # Change this to match your content

print(f"Testing query: '{test_query}'")
print("\n" + "="*60 + "\n")

results = collection.query(
    query_texts=[test_query],
    n_results=3  # Get top 3 most relevant results
)

# Display results
for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    print(f"Result {i+1}:")
    print(f"Role: {metadata['role']}")
    print(f"Conversation: {metadata['conversation_title']}")
    print(f"Timestamp: {metadata['timestamp']}")
    print(f"Content preview: {doc[:200]}...")  # First 200 chars
    print("\n" + "-"*60 + "\n")