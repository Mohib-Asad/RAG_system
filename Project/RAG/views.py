from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
import os
import json

# Initialize the RAG system
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
Settings.llm = Groq(model="llama3-70b-8192", api_key="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")

# Get the absolute path to the data directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)  # This is the Project directory
data_path = os.path.join(project_dir, 'data')

print(f"Looking for data in: {data_path}")

# List all files in the data directory
if os.path.exists(data_path):
    print("Files in data directory:")
    for file in os.listdir(data_path):
        print(f"- {file}")
else:
    print(f"Data directory not found at: {data_path}")
    os.makedirs(data_path)

try:
    print("Attempting to load documents...")
    documents = SimpleDirectoryReader(data_path).load_data()
    print(f"Loaded {len(documents)} documents")
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    print("RAG system initialized successfully")
except Exception as e:
    print(f"Detailed error initializing RAG system: {str(e)}")
    query_engine = None

def home(request):
    """Render the chat interface."""
    return render(request, 'RAG/chat.html')

@csrf_exempt
def chat(request):
    """Handle chat requests."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not query_engine:
                print("Query engine is not initialized")
                return JsonResponse({
                    'message': 'RAG system is not initialized. Please check server logs.',
                    'status': 'error'
                })
            
            print(f"Processing query: {user_message}")
            response = query_engine.query(user_message)
            print(f"Response generated: {str(response)}")
            
            return JsonResponse({
                'message': str(response),
                'status': 'success'
            })
                
        except Exception as e:
            print(f"Error in chat view: {str(e)}")
            return JsonResponse({
                'message': f'Error processing request: {str(e)}',
                'status': 'error'
            })
    
    return JsonResponse({
        'message': 'Invalid request method',
        'status': 'error'
    })

def index(request):
    return HttpResponse("Hello World")