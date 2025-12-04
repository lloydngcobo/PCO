# PCO AI Service

AI-powered microservice for Planning Center Online (PCO) data analysis, natural language queries, and chatbot interface using Ollama.

## Features

- 🤖 **Natural Language Queries**: Ask questions about your PCO data in plain English
- 💬 **Conversational Chatbot**: Interactive AI assistant with conversation context
- 📊 **Data Analysis**: AI-powered insights and analytics on church data
- 🔍 **Smart Filtering**: Query people by role, status, campus with natural language
- 🚀 **Ollama Integration**: Uses local Ollama models for privacy and performance
- 🐳 **Container Ready**: Docker and OpenShift deployment configurations included

## Architecture

```
┌─────────────────┐
│   User/Client   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PCO AI Service │ (Port 5001)
│   Flask API     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ Ollama  │ │ PCO API      │
│ (Local) │ │ Wrapper      │
│         │ │ (Port 5000)  │
└─────────┘ └──────────────┘
```

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) installed and running
- PCO API Wrapper service running
- Planning Center Online API credentials (configured in PCO API Wrapper)

## Quick Start

### 1. Install Ollama

```bash
# Download and install Ollama from https://ollama.ai/

# Pull a model (e.g., llama3.1)
ollama pull llama3.1:8b

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### 2. Setup Environment

```bash
# Clone or navigate to the project
cd pco-ai-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

### 3. Configure Environment Variables

Edit `.env`:

```env
# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=False

# PCO API Wrapper URL
PCO_API_URL=http://localhost:5000

# Ollama Configuration
OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.1:8b
```

### 4. Run the Service

```bash
# Make sure PCO API Wrapper is running on port 5000
# Make sure Ollama is running

# Start the AI service
python src/app.py
```

The service will be available at `http://localhost:5001`

## API Endpoints

### Health Check

```bash
GET /health
```

Returns service health status and Ollama connection status.

**Example:**
```bash
curl http://localhost:5001/health
```

### List Available Models

```bash
GET /api/ai/models
```

Lists all available Ollama models.

**Example:**
```bash
curl http://localhost:5001/api/ai/models
```

### Natural Language Query - People

```bash
POST /api/ai/query/people
Content-Type: application/json

{
  "query": "How many members do we have?",
  "role": "Member",      // Optional
  "status": "active",    // Optional
  "campus_id": "123"     // Optional
}
```

**Example:**
```bash
curl -X POST http://localhost:5001/api/ai/query/people \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many active members do we have in the youth group?",
    "role": "Member",
    "status": "active"
  }'
```

### Natural Language Query - Services

```bash
POST /api/ai/query/services
Content-Type: application/json

{
  "query": "What services are coming up this week?"
}
```

**Example:**
```bash
curl -X POST http://localhost:5001/api/ai/query/services \
  -H "Content-Type: application/json" \
  -d '{"query": "What services are scheduled for next Sunday?"}'
```

### Data Analysis

```bash
POST /api/ai/analyze
Content-Type: application/json

{
  "data_type": "people"  // or "services"
}
```

**Example:**
```bash
curl -X POST http://localhost:5001/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"data_type": "people"}'
```

### Chat with AI Assistant

```bash
POST /api/ai/chat
Content-Type: application/json

{
  "message": "How many members joined last month?",
  "session_id": "user123",  // Optional, defaults to "default"
  "fetch_data": true        // Optional, defaults to true
}
```

**Example:**
```bash
# Start a conversation
curl -X POST http://localhost:5001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you tell me about our church members?",
    "session_id": "user123"
  }'

# Continue the conversation
curl -X POST http://localhost:5001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How many are in the youth group?",
    "session_id": "user123"
  }'
```

### Get Chat Context

```bash
GET /api/ai/chat/context/{session_id}
```

**Example:**
```bash
curl http://localhost:5001/api/ai/chat/context/user123
```

### Clear Chat Context

```bash
DELETE /api/ai/chat/context/{session_id}
```

**Example:**
```bash
curl -X DELETE http://localhost:5001/api/ai/chat/context/user123
```

### List Chat Sessions

```bash
GET /api/ai/chat/sessions
```

**Example:**
```bash
curl http://localhost:5001/api/ai/chat/sessions
```

### Delete Chat Session

```bash
DELETE /api/ai/chat/sessions/{session_id}
```

**Example:**
```bash
curl -X DELETE http://localhost:5001/api/ai/chat/sessions/user123
```

### Custom AI Generation

```bash
POST /api/ai/generate
Content-Type: application/json

{
  "prompt": "Your custom prompt",
  "system_prompt": "Optional system prompt",
  "temperature": 0.7  // Optional, 0.0 to 1.0
}
```

**Example:**
```bash
curl -X POST http://localhost:5001/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain the importance of church community",
    "temperature": 0.5
  }'
```

## Docker Deployment

### Build Image

```bash
docker build -t pco-ai-service:latest .
```

### Run Container

```bash
docker run -d \
  --name pco-ai-service \
  -p 5001:5001 \
  -e PCO_API_URL=http://host.docker.internal:5000 \
  -e OLLAMA_API_URL=http://host.docker.internal:11434/api/generate \
  pco-ai-service:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  pco-ai-service:
    build: .
    ports:
      - "5001:5001"
    environment:
      - PCO_API_URL=http://pco-api-wrapper:5000
      - OLLAMA_API_URL=http://ollama:11434/api/generate
      - OLLAMA_MODEL=llama3.1:8b
    depends_on:
      - pco-api-wrapper
      - ollama
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama-data:
```

Run with:
```bash
docker-compose up -d
```

## OpenShift Deployment

### Prerequisites

- OpenShift cluster access
- `oc` CLI installed
- PCO API Wrapper deployed
- Ollama service deployed (or accessible externally)

### Deploy to OpenShift

```bash
# Login to OpenShift
oc login

# Create or switch to project
oc new-project pco-system

# Update ConfigMap with your URLs
# Edit openshift/configmap.yaml

# Apply configurations
oc apply -k openshift/

# Check deployment status
oc get pods -l app=pco-ai-service

# Get the route URL
oc get route pco-ai-service
```

### Update Configuration

```bash
# Edit ConfigMap
oc edit configmap pco-ai-config

# Restart deployment to pick up changes
oc rollout restart deployment/pco-ai-service
```

## Development

### Project Structure

```
pco-ai-service/
├── src/
│   ├── app.py              # Flask application and API endpoints
│   ├── ollama_client.py    # Ollama API client
│   ├── query_processor.py  # Natural language query processing
│   └── chatbot.py          # Chatbot with conversation context
├── tests/
│   └── test_ollama_client.py
├── openshift/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── route.yaml
│   ├── configmap.yaml
│   └── kustomization.yaml
├── config/
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=src tests/
```

### Code Formatting

```bash
# Install formatter
pip install black flake8

# Format code
black src/ tests/

# Check code style
flake8 src/ tests/
```

## Use Cases

### 1. Member Queries

```bash
# Find members by criteria
curl -X POST http://localhost:5001/api/ai/query/people \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all youth group members who joined this year"}'
```

### 2. Service Planning

```bash
# Get service information
curl -X POST http://localhost:5001/api/ai/query/services \
  -H "Content-Type: application/json" \
  -d '{"query": "What services need volunteers next month?"}'
```

### 3. Data Insights

```bash
# Analyze membership trends
curl -X POST http://localhost:5001/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"data_type": "people"}'
```

### 4. Interactive Assistant

```bash
# Have a conversation
curl -X POST http://localhost:5001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need help planning our next outreach event",
    "session_id": "pastor-john"
  }'
```

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check Ollama logs
ollama logs

# Restart Ollama
ollama serve
```

### PCO API Wrapper Connection Issues

```bash
# Check if PCO API Wrapper is running
curl http://localhost:5000/health

# Check logs
# (depends on how you're running it)
```

### Service Not Starting

```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list

# Run with debug mode
FLASK_DEBUG=True python src/app.py
```

### Memory Issues

If you encounter memory issues with Ollama:

```bash
# Use a smaller model
ollama pull llama3.1:7b

# Update .env
OLLAMA_MODEL=llama3.1:7b
```

## Performance Tuning

### Ollama Model Selection

- **llama3.1:8b** - Good balance of performance and quality (recommended)
- **llama3.1:7b** - Faster, less memory
- **llama2:13b** - Better quality, more memory

### Temperature Settings

- **0.0-0.3** - More factual, deterministic (good for data queries)
- **0.4-0.7** - Balanced (good for general chat)
- **0.8-1.0** - More creative (good for suggestions)

### Caching

The service maintains conversation context in memory. For production:

- Consider using Redis for session storage
- Implement session timeout
- Add conversation history limits

## Security Considerations

1. **API Access**: Add authentication/authorization
2. **Rate Limiting**: Implement rate limiting for API endpoints
3. **Input Validation**: Validate all user inputs
4. **HTTPS**: Use HTTPS in production
5. **Secrets Management**: Use OpenShift secrets for sensitive data

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- Create an issue in the repository
- Contact the development team

## Roadmap

- [ ] Add authentication and authorization
- [ ] Implement Redis-based session storage
- [ ] Add more AI models support
- [ ] Create web UI for chatbot
- [ ] Add voice interface
- [ ] Implement advanced analytics
- [ ] Add multi-language support