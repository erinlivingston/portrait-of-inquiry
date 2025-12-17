import chromadb
from chromadb.utils import embedding_functions

# Initialize Chroma client
client = chromadb.PersistentClient(path="./rag/chroma_db")

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Create collection for intellectual inquiry
collection = client.get_or_create_collection(
    name="intellectual_inquiry",
    embedding_function=sentence_transformer_ef
)

# Read your notes file
with open('assets/fall25class_notes.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Total characters in notes: {len(content)}")

# Smart chunking - split by double newlines (paragraphs) but keep chunks reasonable
chunks = []
current_chunk = ""
paragraphs = content.split('\n\n')

for para in paragraphs:
    para = para.strip()
    if not para:
        continue
    
    # If adding this paragraph would make chunk too long, save current chunk
    if len(current_chunk) + len(para) > 1000:  # ~1000 chars per chunk
        if current_chunk:
            chunks.append(current_chunk)
        current_chunk = para
    else:
        current_chunk += "\n\n" + para if current_chunk else para

# Add the last chunk
if current_chunk:
    chunks.append(current_chunk)

print(f"Created {len(chunks)} chunks from notes")
print("Starting vectorization...")

# Add to Chroma
for idx, chunk in enumerate(chunks):
    collection.add(
        documents=[chunk],
        metadatas=[{"source": "class_notes", "chunk_id": idx}],
        ids=[f"note_{idx}"]
    )
    
    if (idx + 1) % 50 == 0:
        print(f"Processed {idx + 1}/{len(chunks)} chunks...")

print(f"✓ Notes vectorization complete! {len(chunks)} chunks added")
print(f"Database saved at: ./rag/chroma_db")