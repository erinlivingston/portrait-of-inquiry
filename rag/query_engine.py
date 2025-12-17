import chromadb
from chromadb.utils import embedding_functions
import openai  # or use a local model like llama

client = chromadb.PersistentClient(path="./rag/chroma_db")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def query_rag(user_prompt, n_results=5):
    # Query both collections
    dialogic = client.get_collection("dialogic_inquiry", embedding_function=sentence_transformer_ef)
    intellectual = client.get_collection("intellectual_inquiry", embedding_function=sentence_transformer_ef)
    
    dialogic_results = dialogic.query(query_texts=[user_prompt], n_results=n_results)
    intellectual_results = intellectual.query(query_texts=[user_prompt], n_results=n_results)
    
    # Combine context
    context = "Dialogic Context:\n" + "\n".join(dialogic_results['documents'][0])
    context += "\n\nIntellectual Context:\n" + "\n".join(intellectual_results['documents'][0])
    
    # Generate response (using OpenAI or local model)
    # This is where you'd call your LLM with the context + user prompt
    
    return context  # For now, return raw context for prototype