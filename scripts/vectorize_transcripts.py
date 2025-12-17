import chromadb
import pandas as pd
from chromadb.utils import embedding_functions

# Initialize Chroma client
client = chromadb.PersistentClient(path="./rag/chroma_db")

# Use sentence transformers for embeddings (free, local)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Create collection for dialogic inquiry
collection = client.get_or_create_collection(
    name="dialogic_inquiry",
    embedding_function=sentence_transformer_ef
)

# Load your cleaned transcripts
df = pd.read_csv('assets/cleaned_chatgpt_history.csv')

print(f"Total messages in CSV: {len(df)}")

# Filter out rows with empty content
df = df.dropna(subset=['content'])  # Remove rows where content is NaN
df = df[df['content'].str.strip() != '']  # Remove rows where content is just whitespace

print(f"Messages with valid content: {len(df)}")

# Add to Chroma
print("Starting vectorization...")
for idx, row in df.iterrows():
    try:
        collection.add(
            documents=[str(row['content'])],  # Ensure it's a string
            metadatas=[{
                "timestamp": str(row['timestamp']), 
                "role": str(row['role']),
                "conversation_title": str(row['conversation_title'])
            }],
            ids=[f"msg_{idx}"]
        )
        
        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{len(df)} messages...")
    except Exception as e:
        print(f"Error on row {idx}: {e}")
        continue

print(f"✓ Vectorization complete! {len(df)} messages added to Chroma DB")
print(f"Database saved at: ./rag/chroma_db")