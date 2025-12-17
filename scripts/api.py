from flask import Flask, request, jsonify, send_from_directory
import chromadb
from chromadb.utils import embedding_functions
import ollama  # ADD THIS LINE
import os

from PIL import Image
import random
import io
import base64

def create_collage_for_query(drawing_files, output_size=(700, 350), num_pieces=10):
    """Create a unique collage from random pieces of drawings"""
    
    # Create blank canvas with slight off-white
    collage = Image.new('RGB', output_size, (250, 248, 245))
    
    for _ in range(num_pieces):
        # Pick random drawing
        drawing_path = random.choice(drawing_files)
        try:
            img = Image.open(drawing_path).convert('RGBA')
        except:
            continue
        
        # Random crop size
        crop_w = random.randint(80, 250)
        crop_h = random.randint(80, 250)
        
        # Random position in source image
        max_x = max(0, img.width - crop_w)
        max_y = max(0, img.height - crop_h)
        x = random.randint(0, max_x) if max_x > 0 else 0
        y = random.randint(0, max_y) if max_y > 0 else 0
        
        # Crop piece
        piece = img.crop((x, y, x + crop_w, y + crop_h))
        
        # Random rotation
        angle = random.choice([0, 90, 180, 270, 45, -45])
        piece = piece.rotate(angle, expand=True, fillcolor=(250, 248, 245, 0))
        
        # Random position on canvas
        if piece.width < output_size[0] and piece.height < output_size[1]:
            paste_x = random.randint(0, output_size[0] - piece.width)
            paste_y = random.randint(0, output_size[1] - piece.height)
            
            # Apply transparency for layering
            if piece.mode == 'RGBA':
                alpha = piece.split()[3]
                alpha = alpha.point(lambda p: int(p * random.uniform(0.6, 0.9)))
                piece.putalpha(alpha)
                collage.paste(piece, (paste_x, paste_y), piece)
    
    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    collage.save(buffer, format='JPEG', quality=85)
    img_data = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/jpeg;base64,{img_data}"




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
def query():
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
        system_prompt = """This is an art piece, a conceptual digital project that considers intellectual journey, 
        and the way knowledge layers and combines with itself. It's called hallucinations of personal inquriy. Using RAG (Retrieval Augmented Generation) methods,
        the model combines personal and school ChatGPT conversation history, with class notes from Critical AI Studies and Data Bias courses.
        Above the query box to prompt, the user meets this dialogue: Here lies an open opportunity to query a proxy knowledge base of my mode of thought. 
        Consider the hallucinated response a starting point for your own inquiry, as an invitation to seek more elsewhere.

        This self-reflective digital project offers an alternative to homogeneous big-box AI models 
        through deep consideration of personal sources, desires for information, and embodied materiality.

        Synthesize the provided sources into a thoughtful, coherent response that:
            - Directly addresses the question and weaves together insights from both dialogic (ChatGPT conversations) and intellectual (class notes) sources
            - References key concepts naturally without a rigid citation format, consider a playful, narrative tone that asks questions and 
                encourages sensory experiences or engagement to leave more thoughts with the user
            - Honor some of the specificity in the chatGPT transcripts, or even the back-and-forth nature of the dialogue if it's relevant, for example
                referencing a particular conversation that sparked insight or developed ideas bu the end. 
            - Explores connections and tensions between lived inquiry maybe revealed in the transcripts and the theoretical frameworks 
                presented in outlines of the class notes which often reference theorists and critical historians and data studies authors.
            - Honors the specificity of their personal intellectual trajectory

        Do not simply list sources. Create a narrative synthesis that encourages further inquiry, especially non-text based."""

        user_prompt = f"""Question: {user_input}

                Relevant sources from my inquiry:

{full_context}

Synthesize these sources to answer my question:"""

        print("Generating response with local LLM...")
        
        # Generate with Ollama
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ], 
            options={
                'num_predict': 300, 
                'temperature': 0.7
            }
        )
        
        generated_response = response['message']['content']
        
        print(f"Generated response length: {len(generated_response)} chars")
        
        # ============ ADD THIS SECTION HERE ============
        # Generate unique collage for this query
        drawing_files = [
            os.path.join(BASE_DIR, 'assets/atdrawings/8.12.25.jpeg'),
            os.path.join(BASE_DIR, 'assets/atdrawings/9.18.25.jpeg'),
            os.path.join(BASE_DIR, 'assets/atdrawings/9.25.25.jpeg'),
            os.path.join(BASE_DIR, 'assets/atdrawings/10.9.25.jpeg'),
            os.path.join(BASE_DIR, 'assets/atdrawings/10.16.25.jpeg'),
            os.path.join(BASE_DIR, 'assets/atdrawings/10.23.25.jpeg'),
            os.path.join(BASE_DIR, 'assets/atdrawings/11.6.25.jpeg'),
            os.path.join(BASE_DIR, 'assets/atdrawings/11.13.25.jpeg'),
            os.path.join(BASE_DIR, 'assets/atdrawings/11.20.25.jpeg'),
            os.path.join(BASE_DIR, 'assets/atdrawings/12.11.25.jpeg')
        ]
        
        collage_data = create_collage_for_query(drawing_files)
        print("Generated unique collage for this query")
        # ============ END NEW SECTION ============
        
        # Return both the generated answer and the sources
        response_data = {
            "query": user_input,
            "generated_answer": generated_response,
            "collage": collage_data,  # ← ADD THIS LINE
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
    app.run(host='127.0.0.1', port=5001, debug=True)