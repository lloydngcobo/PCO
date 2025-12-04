# PCO AI Service - Quick Start Guide

Get up and running with the PCO AI Service in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] PCO API Wrapper running on port 5000
- [ ] Ollama installed and running

## Step 1: Install Ollama (5 minutes)

### Windows/Mac/Linux

1. Download Ollama from [https://ollama.ai/](https://ollama.ai/)
2. Install and start Ollama
3. Pull a model:

```bash
ollama pull llama3.1:8b
```

4. Verify it's running:

```bash
curl http://localhost:11434/api/tags
```

## Step 2: Setup the AI Service (2 minutes)

```bash
# Navigate to the AI service directory
cd Projects/pco-api-wrapper/pco-ai-service

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

## Step 3: Configure (1 minute)

Edit `.env` file (or use defaults):

```env
PCO_API_URL=http://localhost:5000
OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.1:8b
```

## Step 4: Start the Service (30 seconds)

```bash
python src/app.py
```

You should see:
```
Starting PCO AI Service on 0.0.0.0:5001
✓ Ollama connection successful
✓ Available models: llama3.1:8b
```

## Step 5: Test It! (1 minute)

### Test 1: Health Check

```bash
curl http://localhost:5001/health
```

### Test 2: Ask a Question

```bash
curl -X POST http://localhost:5001/api/ai/query/people \
  -H "Content-Type: application/json" \
  -d '{"query": "How many members do we have?"}'
```

### Test 3: Chat with AI

```bash
curl -X POST http://localhost:5001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about our church members", "session_id": "test"}'
```

## Common Issues

### "Cannot connect to Ollama"

```bash
# Make sure Ollama is running
ollama serve

# Check if it's accessible
curl http://localhost:11434/api/tags
```

### "Cannot connect to PCO API"

```bash
# Make sure PCO API Wrapper is running
curl http://localhost:5000/health
```

### "Module not found"

```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. Read the full [README.md](README.md) for all features
2. Try the chatbot with different questions
3. Explore data analysis endpoints
4. Deploy to OpenShift (see README.md)

## Example Queries to Try

```bash
# Member statistics
curl -X POST http://localhost:5001/api/ai/query/people \
  -H "Content-Type: application/json" \
  -d '{"query": "How many active members do we have?"}'

# Service information
curl -X POST http://localhost:5001/api/ai/query/services \
  -H "Content-Type: application/json" \
  -d '{"query": "What services are coming up?"}'

# Data analysis
curl -X POST http://localhost:5001/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"data_type": "people"}'

# Interactive chat
curl -X POST http://localhost:5001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me understand our membership demographics", "session_id": "demo"}'
```

## Success! 🎉

You now have an AI-powered assistant for your PCO data!

For more advanced usage, see [README.md](README.md)