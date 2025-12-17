from flask import Flask, request, jsonify, send_from_directory
import chromadb
from chromadb.utils import embedding_functions
import ollama  # ADD THIS LINE
import os

# Get the parent directory (portrait-of-inquiry root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Initialize Chroma client
chroma_path = os.path.join(BASE_DIR, 'rag', 'chroma_db')
client = chromadb.PersistentClient(path=chroma_path)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Get collections
dialogic = client.get_collection("dialogic_inquiry", embedding_function=sentence_transformer_ef)
intellectual = client.get_collection("intellectual_inquiry", embedding_function=sentence_transformer_ef)

# API routes
@app.route('/api/query', methods=['POST'])
def query():  # REPLACE THIS ENTIRE FUNCTION
    try:
        print(f"=== QUERY ENDPOINT HIT ===")
        
        user_input = request.json['prompt']
        n_results = request.json.get('n_results', 3)
        
        print(f"Query received: {user_input}")
        
        # Query both collections
        dialogic_results = dialogic.query(
            query_texts=[user_input], 
            n_results=n_results
        )
        intellectual_results = intellectual.query(
            query_texts=[user_input], 
            n_results=n_results
        )
        
        # Combine all sources into context
        context_parts = []
        
        # Add dialogic sources
        context_parts.append("=== From Your ChatGPT Conversations ===")
        for i, doc in enumerate(dialogic_results['documents'][0]):
            meta = dialogic_results['metadatas'][0][i]
            context_parts.append(f"[Conversation: {meta['conversation_title']}]\n{doc}\n")
        
        # Add intellectual sources
        context_parts.append("\n=== From Your Class Notes ===")
        for i, doc in enumerate(intellectual_results['documents'][0]):
            context_parts.append(f"[Note {i+1}]\n{doc}\n")
        
        full_context = "\n".join(context_parts)
        
        # Create the prompt for local LLM
        system_prompt = """You are analyzing personal inquiry by combining ChatGPT conversation history, with class notes from Critical AI Studies and Data Bias courses.

This is a self-reflective digital project called "Portrait of Inquiry" that offers an alternative to homogeneous big-box AI models through deep consideration of personal sources, desires for information, and embodied materiality.

Synthesize the provided sources into a thoughtful, coherent response that:
- Directly addresses their question
- Weaves together insights from both dialogic (ChatGPT conversations) and intellectual (class notes) source
- References key concepts naturally without rigid citation format
- Explores connections and tensions between lived inquiry and theoretical frameworks
- Honors the specificity of their personal intellectual trajectory

Do not simply list sources. Create a narrative synthesis that represents their unique "portrait of inquiry"."""

        user_prompt = f"""Question: {user_input}

Relevant sources from my inquiry:

{full_context}

Synthesize these sources to answer my question:"""

        print("Generating response with local LLM...")
        
        # Generate with Ollama
        response = ollama.chat(
            model='llama3.2',  # Change local model here
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
        )
        
        generated_response = response['message']['content']
        
        print(f"Generated response length: {len(generated_response)} chars")
        
        # Return both the generated answer and the sources
        response_data = {
            "query": user_input,
            "generated_answer": generated_response,
            "dialogic_sources": [],
            "intellectual_sources": []
        }
        
        # Include sources for transparency
        for i in range(len(dialogic_results['documents'][0])):
            response_data["dialogic_sources"].append({
                "content": dialogic_results['documents'][0][i],
                "metadata": dialogic_results['metadatas'][0][i]
            })
        
        for i in range(len(intellectual_results['documents'][0])):
            response_data["intellectual_sources"].append({
                "content": intellectual_results['documents'][0][i],
                "metadata": intellectual_results['metadatas'][0][i]
            })
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error in query route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    print("=== HEALTH ENDPOINT HIT ===")
    return jsonify({
        "status": "ok",
        "dialogic_count": dialogic.count(),
        "intellectual_count": intellectual.count()
    })

# Static file routes
@app.route('/')
def index():
    print("=== ROOT / HIT ===")
    return send_from_directory(BASE_DIR, 'mainpage.html')

@app.route('/<path:path>')
def serve_static(path):
    print(f"=== STATIC FILE REQUEST: {path} ===")
    # Block api routes from being served as static
    if path.startswith('api'):
        return "Not found", 404
    
    try:
        return send_from_directory(BASE_DIR, path)
    except:
        return "File not found", 404

if __name__ == '__main__':
    print("Starting RAG API server with static file serving...")
    print(f"Base directory: {BASE_DIR}")
    print(f"Dialogic inquiry: {dialogic.count()} documents")
    print(f"Intellectual inquiry: {intellectual.count()} documents")
    print("Access your site at: http://localhost:5000")
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule}")
    app.run(host='127.0.0.1', port=5000, debug=True)