# PCO API Wrapper - Project Overview

## What This Project Does

This is a **standalone Python project** that provides a REST API wrapper for Planning Center Online (PCO). It focuses exclusively on:

1. **pypco Integration** - Python wrapper for PCO API with automatic authentication, rate limiting, pagination, and error recovery
2. **Reusable Utility Functions** - Common CRUD operations for people and emails
3. **Flask REST API** - Programmatic access to PCO data via HTTP endpoints
4. **Comprehensive Error Handling** - Automatic retry logic and detailed error messages

## Key Features

✅ **Automatic Rate Limiting** - Handles PCO's 100 requests/20 seconds limit transparently  
✅ **Pagination Management** - Automatically iterates through large datasets  
✅ **Error Recovery** - Configurable retry logic (default: 3 attempts)  
✅ **RESTful API** - Clean HTTP endpoints for CRUD operations  
✅ **Utility Functions** - High-level helpers for common tasks  
✅ **Type Hints** - Full type annotations for better IDE support  
✅ **Environment-based Config** - Secure credential management via .env  

## Project Structure

```
pco-api-wrapper/
│
├── src/                          # Source code
│   ├── app.py                    # Flask REST API application
│   └── pco_helpers.py            # Reusable utility functions
│
├── examples/                     # Example usage scripts
│   └── example_usage.py          # Demonstrates all features
│
├── tests/                        # Test files (to be added)
│
├── config/                       # Configuration files
│
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── README.md                     # Full documentation
├── QUICKSTART.md                 # Quick start guide
└── PROJECT_OVERVIEW.md           # This file
```

## Core Components

### 1. Flask REST API (`src/app.py`)

A production-ready REST API with the following endpoints:

**Health & Status:**
- `GET /health` - Health check

**People Management:**
- `GET /api/people` - List all people (with filtering)
- `GET /api/people/{id}` - Get specific person
- `POST /api/people` - Create new person
- `PATCH /api/people/{id}` - Update person
- `DELETE /api/people/{id}` - Delete person

**Campus Management:**
- `GET /api/campuses` - List all campuses

**Features:**
- Query parameter filtering (role, status, campus)
- Multiple response formats (JSON, text)
- Automatic pagination handling
- Comprehensive error responses
- Includes related data (emails, phone numbers)

### 2. Utility Functions (`src/pco_helpers.py`)

High-level helper functions for common operations:

**Person Operations:**
- `get_pco_client()` - Initialize authenticated client
- `find_person_by_name()` - Search by name
- `add_person()` - Create new person
- `update_person_attribute()` - Update single field
- `update_person_attributes()` - Update multiple fields
- `create_or_update_person()` - Idempotent create/update
- `delete_person()` - Remove person
- `get_person_by_id()` - Fetch by ID

**Email Operations:**
- `add_email_to_person()` - Add email address
- `update_email()` - Modify email
- `get_person_emails()` - List all emails
- `delete_email()` - Remove email

### 3. Example Scripts (`examples/`)

Demonstrates all functionality:
- Creating people
- Finding people
- Updating attributes
- Managing emails
- Error handling
- Best practices

## Technology Stack

- **Python 3.7+** - Programming language
- **pypco 1.2.0+** - PCO API wrapper library
- **Flask 2.3.0+** - Web framework
- **python-dotenv 1.0.0+** - Environment management
- **requests 2.31.0+** - HTTP library

## Use Cases

### 1. Automated Data Management
```python
# Sync external data to PCO
for person_data in external_system:
    create_or_update_person(pco, **person_data)
```

### 2. Bulk Operations
```python
# Update all members
for person in pco.iterate('/people/v2/people'):
    if person['data']['attributes']['membership'] == 'Member':
        update_person_attribute(pco, person['data']['id'], 'status', 'active')
```

### 3. Integration with Other Systems
```bash
# REST API allows integration from any language
curl -X POST http://localhost:5000/api/people \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe"}'
```

### 4. Data Export
```python
# Export all people to CSV
people = []
for person in pco.iterate('/people/v2/people'):
    people.append(person['data']['attributes'])
# Convert to CSV...
```

## What This Project Does NOT Include

❌ Certificate generation (removed from original project)  
❌ PDF/DOCX manipulation  
❌ Document templates  
❌ Microsoft Word COM automation  
❌ Groq/Ollama AI integration  

This is a **focused, production-ready API wrapper** without the certificate generation features from the original project.

## Getting Started

### Quick Start (5 minutes)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure credentials:**
```bash
cp .env.example .env
# Edit .env with your PCO credentials
```

3. **Start the API:**
```bash
python src/app.py
```

4. **Test it:**
```bash
curl http://localhost:5000/health
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## Configuration

All configuration via environment variables in `.env`:

```env
# Required
PCO_APP_ID=your_app_id
PCO_SECRET=your_secret

# Optional
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

## Security

✅ Environment-based credentials (never hardcoded)  
✅ .env file excluded from git  
✅ HTTPS-only API communication  
✅ No sensitive data in logs  
✅ Configurable timeout and retry limits  

## Performance

- **Rate Limiting:** Automatically handled (100 req/20s)
- **Pagination:** Transparent iteration over large datasets
- **Timeouts:** Configurable (default: 60s)
- **Retries:** Automatic with exponential backoff
- **Connection Pooling:** Via requests.Session

## Error Handling

Comprehensive error handling at multiple levels:

1. **Network Errors:** Automatic retry with timeout
2. **Rate Limits:** Automatic sleep and retry
3. **API Errors:** Detailed error messages
4. **Validation Errors:** Clear HTTP 400 responses
5. **Server Errors:** Logged with stack traces

## Testing

```bash
# Run tests (when implemented)
pytest tests/

# Code quality
black src/
flake8 src/
mypy src/
```

## Deployment

### Local Development
```bash
python src/app.py
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.app:app
```

### Docker (example)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/app.py"]
```

## Monitoring

The API includes:
- Health check endpoint (`/health`)
- Detailed logging
- Error tracking
- Request/response logging (in debug mode)

## Roadmap

Potential future enhancements:
- [ ] Add comprehensive test suite
- [ ] Implement caching layer
- [ ] Add webhook support
- [ ] Create CLI tool
- [ ] Add Docker support
- [ ] Implement async/await
- [ ] Add GraphQL support
- [ ] Support more PCO modules (Services, Check-ins, etc.)

## Contributing

This is a standalone project. To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- **Documentation:** [README.md](README.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **Examples:** [examples/example_usage.py](examples/example_usage.py)
- **pypco Docs:** https://pypco.readthedocs.io/
- **PCO API Docs:** https://developer.planning.center/docs/

## License

This project is provided as-is for use with Planning Center Online.

## Comparison with Original Project

| Feature | Original Project | This Project |
|---------|-----------------|--------------|
| pypco wrapper | ✅ | ✅ |
| Utility functions | ✅ | ✅ |
| Flask REST API | ✅ | ✅ |
| Certificate generation | ✅ | ❌ |
| PDF/DOCX manipulation | ✅ | ❌ |
| Word COM automation | ✅ | ❌ |
| AI integration | ✅ | ❌ |
| Focus | Multi-purpose | API wrapper only |

## Summary

This is a **clean, focused, production-ready** Python project that:
- Wraps the Planning Center Online API
- Provides reusable utility functions
- Offers a REST API for programmatic access
- Handles authentication, rate limiting, and errors automatically
- Excludes certificate generation and document manipulation

Perfect for integrating PCO with other systems or building custom applications on top of PCO data.

---

**Version:** 1.0.0  
**Created:** 2025-11-18  
**Python:** 3.7+  
**License:** MIT-style (as-is)