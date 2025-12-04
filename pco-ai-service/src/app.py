"""
PCO AI Service - Flask REST API
Provides AI-powered endpoints for PCO data analysis and chatbot
"""

from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from typing import Optional
from ollama_client import get_ollama_client
from query_processor import QueryProcessor
from chatbot import PCOChatbot

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Configuration
PCO_API_URL = os.getenv("PCO_API_URL", "http://localhost:5000")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

# Initialize components
ollama_client = get_ollama_client()
query_processor = QueryProcessor(PCO_API_URL)
chatbot = PCOChatbot(PCO_API_URL)

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        'service': 'PCO AI Service',
        'version': '1.0.0',
        'description': 'AI-powered microservice for Planning Center Online data analysis',
        'endpoints': {
            'health': '/health',
            'models': '/api/ai/models',
            'query_people': '/api/ai/query/people (POST)',
            'query_services': '/api/ai/query/services (POST)',
            'analyze': '/api/ai/analyze (POST)',
            'chat': '/api/ai/chat (POST)',
            'chat_context': '/api/ai/chat/context/{session_id} (GET/DELETE)',
            'chat_sessions': '/api/ai/chat/sessions (GET)',
            'generate': '/api/ai/generate (POST)'
        },
        'documentation': 'See README.md for detailed API documentation',
        'status': 'running'
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    ollama_healthy = ollama_client.check_health()
    
    return jsonify({
        'status': 'healthy' if ollama_healthy else 'degraded',
        'service': 'PCO AI Service',
        'version': '1.0.0',
        'ollama_status': 'connected' if ollama_healthy else 'disconnected',
        'ollama_url': OLLAMA_API_URL,
        'ollama_model': OLLAMA_MODEL,
        'pco_api_url': PCO_API_URL
    })


@app.route('/api/ai/models', methods=['GET'])
def list_models():
    """List available Ollama models"""
    try:
        models = ollama_client.list_models()
        return jsonify({
            'success': True,
            'models': models,
            'current_model': OLLAMA_MODEL
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ai/query/people', methods=['POST'])
def query_people():
    """
    Process natural language query about people.
    
    Request Body:
        {
            "query": "How many members do we have?",
            "role": "Member",  // Optional
            "status": "active",  // Optional
            "campus_id": "123"  // Optional
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'query field is required'
            }), 400
        
        query = data['query']
        role = data.get('role')
        status = data.get('status')
        campus_id = data.get('campus_id')
        
        result = query_processor.process_people_query(
            query=query,
            role=role,
            status=status,
            campus_id=campus_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ai/query/services', methods=['POST'])
def query_services():
    """
    Process natural language query about services.
    
    Request Body:
        {
            "query": "What services are coming up this week?"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'query field is required'
            }), 400
        
        query = data['query']
        result = query_processor.process_services_query(query)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ai/analyze', methods=['POST'])
def analyze_data():
    """
    Perform AI-powered analysis on PCO data.
    
    Request Body:
        {
            "data_type": "people"  // or "services"
        }
    """
    try:
        data = request.get_json()
        data_type = data.get('data_type', 'people') if data else 'people'
        
        if data_type not in ['people', 'services']:
            return jsonify({
                'success': False,
                'error': 'data_type must be "people" or "services"'
            }), 400
        
        result = query_processor.analyze_data(data_type)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ai/chat', methods=['POST'])
def chat():
    """
    Chat with AI assistant about PCO data.
    
    Request Body:
        {
            "message": "How many members do we have?",
            "session_id": "user123",  // Optional, defaults to "default"
            "fetch_data": true  // Optional, defaults to true
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'message field is required'
            }), 400
        
        message = data['message']
        session_id = data.get('session_id', 'default')
        fetch_data = data.get('fetch_data', True)
        
        result = chatbot.chat(
            message=message,
            session_id=session_id,
            fetch_data=fetch_data
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ai/chat/context/<session_id>', methods=['GET'])
def get_chat_context(session_id: str):
    """Get conversation context for a session"""
    context = chatbot.get_context(session_id)
    
    if context:
        return jsonify({
            'success': True,
            'session_id': session_id,
            'context': context
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404


@app.route('/api/ai/chat/context/<session_id>', methods=['DELETE'])
def clear_chat_context(session_id: str):
    """Clear conversation context for a session"""
    success = chatbot.clear_context(session_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': f'Context cleared for session {session_id}'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404


@app.route('/api/ai/chat/sessions', methods=['GET'])
def list_chat_sessions():
    """List all active chat sessions"""
    sessions = chatbot.list_sessions()
    
    return jsonify({
        'success': True,
        'sessions': sessions,
        'count': len(sessions)
    })


@app.route('/api/ai/chat/sessions/<session_id>', methods=['DELETE'])
def delete_chat_session(session_id: str):
    """Delete a chat session"""
    success = chatbot.delete_session(session_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': f'Session {session_id} deleted'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404


@app.route('/api/ai/generate', methods=['POST'])
def generate():
    """
    Generate AI response with custom prompt.
    
    Request Body:
        {
            "prompt": "Your prompt here",
            "system_prompt": "Optional system prompt",
            "temperature": 0.7  // Optional, 0.0 to 1.0
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'prompt field is required'
            }), 400
        
        prompt = data['prompt']
        system_prompt = data.get('system_prompt')
        temperature = data.get('temperature', 0.7)
        
        response = ollama_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        return jsonify({
            'success': True,
            'response': response,
            'model': OLLAMA_MODEL
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == "__main__":
    # Get configuration from environment
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.getenv("FLASK_PORT", "5001"))
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    
    print(f"Starting PCO AI Service on {host}:{port}")
    print(f"Debug mode: {debug_mode}")
    print(f"PCO API URL: {PCO_API_URL}")
    print(f"Ollama URL: {OLLAMA_API_URL}")
    print(f"Ollama Model: {OLLAMA_MODEL}")
    
    # Check Ollama connection
    if ollama_client.check_health():
        print("✓ Ollama connection successful")
        models = ollama_client.list_models()
        print(f"✓ Available models: {', '.join(models)}")
    else:
        print("✗ Warning: Cannot connect to Ollama service")
        print(f"  Make sure Ollama is running at {OLLAMA_API_URL}")
    
    app.run(host=host, port=port, debug=debug_mode)