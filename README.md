# PCO API Wrapper

A Python-based REST API wrapper for Planning Center Online (PCO) that provides easy-to-use endpoints for managing people and their data.

## Features

✅ **pypco Integration** - Built on top of the pypco library for robust PCO API interaction  
✅ **Automatic Rate Limiting** - Handles API rate limits transparently  
✅ **Pagination Support** - Automatically handles large datasets  
✅ **Error Recovery** - Automatic retry logic with configurable attempts  
✅ **RESTful API** - Clean REST endpoints for CRUD operations  
✅ **Utility Functions** - Reusable helper functions for common operations  
✅ **Comprehensive Error Handling** - Detailed error messages and logging  

## Project Structure

```
pco-api-wrapper/
├── src/
│   ├── app.py              # Flask REST API application
│   └── pco_helpers.py      # Reusable utility functions
├── tests/                  # Test files (to be added)
├── config/                 # Configuration files
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Planning Center Online account with API access

### Setup Steps

1. **Clone or download this project**

```bash
cd pco-api-wrapper
```

2. **Create a virtual environment (recommended)**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your PCO credentials
```

5. **Get your PCO API credentials**

- Log in to [Planning Center Online](https://planning.center)
- Navigate to **Settings → Developer**
- Click **New Personal Access Token**
- Copy the Application ID and Secret
- Add them to your `.env` file

## Configuration

Edit the `.env` file with your credentials:

```env
# Planning Center Online API Credentials
PCO_APP_ID=your_application_id_here
PCO_SECRET=your_application_secret_here

# Flask Configuration
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

## Usage

### Starting the API Server

```bash
python src/app.py
```

The server will start on `http://localhost:5000` by default.

### Using the Utility Functions

```python
from src.pco_helpers import get_pco_client, create_or_update_person

# Initialize PCO client
pco = get_pco_client()

# Create or update a person
person = create_or_update_person(
    pco,
    first_name="John",
    last_name="Doe",
    gender="Male",
    email="john.doe@example.com"
)

print(f"Person ID: {person['id']}")
```

## API Endpoints

### Health Check

```http
GET /health
```

Returns the API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "PCO API Wrapper",
  "version": "1.0.0"
}
```

### Get All People

```http
GET /api/people
```

**Query Parameters:**
- `role` (optional): Filter by membership role
- `status` (optional): Filter by status (active, inactive)
- `campus_id` (optional): Filter by campus ID
- `format` (optional): Response format (json or text, default: json)

**Exampl
```

**Response:**
```json
{
  "count": 2,
  "filters": {
    "role": "member",
    "status": null,
    "campus_id": null
  },
  "data": [
    {
      "id": "123456",
      "first_name": "John",
      "last_name": "Doe",
      "gender": "Male",
      "birthdate": "1990-01-01",
      "membership": "Member",
      "status": "active",
      "campuses": "Main Campus",
      "emails": [
        {
          "address": "john@example.com",
          "location": "Work"
        }
      ],
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-06-01T00:00:00Z"
    }
  ]
}
```

### Get Person by ID

```http
GET /api/people/{person_id}
```

**Example:**
```bash
curl "http://localhost:5000/api/people/123456"
```

### Create Person

```http
POST /api/people
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "gender": "Female",
  "birthdate": "1985-05-15"
}
```

**Example:**
```bash
curl -X POST "http://localhost:5000/api/people" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Jane","last_name":"Smith","gender":"Female"}'
```

### Update Person

```http
PATCH /api/people/{person_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "gender": "Male",
  "birthdate": "1990-01-01"
}
```

**Example:**
```bash
curl -X PATCH "http://localhost:5000/api/people/123456" \
  -H "Content-Type: application/json" \
  -d '{"gender":"Male"}'
```

### Delete Person

```http
DELETE /api/people/{person_id}
```

**Example:**
```bash
curl -X DELETE "http://localhost:5000/api/people/123456"
```

### Get All Campuses

```http
GET /api/campuses
```

**Example:**
```bash
curl "http://localhost:5000/api/campuses"
```

## Utility Functions

The `pco_helpers.py` module provides reusable functions:

### Person Management

- `get_pco_client()` - Initialize PCO client
- `find_person_by_name(pco, first_name, last_name)` - Search for person
- `add_person(pco, first_name, last_name, gender, birthdate)` - Create person
- `update_person_attribute(pco, person_id, attribute_name, value)` - Update single attribute
- `update_person_attributes(pco, person_id, attributes)` - Update multiple attributes
- `create_or_update_person(pco, ...)` - Create or update person
- `delete_person(pco, person_id)` - Delete person
- `get_person_by_id(pco, person_id)` - Get person by ID

### Email Management

- `add_email_to_person(pco, person_id, email, location)` - Add email
- `update_email(pco, person_id, email_id, email, location)` - Update email
- `get_person_emails(pco, person_id)` - Get all emails
- `delete_email(pco, person_id, email_id)` - Delete email

## Examples

### Example 1: Create Person with Email

```python
from src.pco_helpers import get_pco_client, create_or_update_person

pco = get_pco_client()

person = create_or_update_person(
    pco,
    first_name="Alice",
    last_name="Johnson",
    gender="Female",
    birthdate="1992-03-15",
    email="alice.johnson@example.com",
    email_location="Work"
)

print(f"Created person: {person['id']}")
```

### Example 2: Update Person Attributes

```python
from src.pco_helpers import get_pco_client, update_person_attributes

pco = get_pco_client()

updated = update_person_attributes(
    pco,
    person_id="123456",
    attributes={
        "gender": "Male",
        "birthdate": "1990-01-01"
    }
)

print(f"Updated person: {updated['id']}")
```

### Example 3: Manage Emails

```python
from src.pco_helpers import (
    get_pco_client,
    add_email_to_person,
    get_person_emails
)

pco = get_pco_client()

# Add email
add_email_to_person(pco, "123456", "work@example.com", "Work")

# Get all emails
emails = get_person_emails(pco, "123456")
for email in emails:
    print(f"{email['address']} ({email['location']})")
```

## Error Handling

The API provides detailed error messages:

```json
{
  "error": "Person not found"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (missing required fields)
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Planning Center Online enforces rate limits:
- **Limit:** 100 requests per 20 seconds
- **Handling:** pypco automatically handles rate limiting by sleeping and retrying

No action required - the wrapper handles this automatically!

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
flake8 src/
```

### Type Checking

```bash
mypy src/
```

## Troubleshooting

### Authentication Errors

**Problem:** `401 Unauthorized`

**Solution:**
- Verify `PCO_APP_ID` and `PCO_SECRET` in `.env`
- Check credentials haven't expired
- Ensure proper permissions in PCO

### Connection Errors

**Problem:** Cannot connect to PCO API

**Solution:**
- Check internet connectivity
- Verify PCO API status
- Check firewall settings

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'pypco'`

**Solution:**
```bash
pip install -r requirements.txt
```

## Security Best Practices

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use environment variables** - Don't hardcode API keys
3. **Rotate tokens regularly** - Update PCO tokens periodically
4. **Use HTTPS** - Always use secure connections (pypco uses HTTPS by default)
5. **Limit permissions** - Only grant necessary PCO permissions

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for use with Planning Center Online.

## Support

For issues related to:
- **This wrapper:** Create an issue in this repository
- **pypco library:** Visit [pypco documentation](https://pypco.readthedocs.io/)
- **PCO API:** Visit [PCO Developer Docs](https://developer.planning.center/docs/)

## Acknowledgments

- Built with [pypco](https://github.com/billdeitrick/pypco) by Bill Deitrick
- Uses [Flask](https://flask.palletsprojects.com/) web framework
- Powered by [Planning Center Online](https://planning.center) API

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-18