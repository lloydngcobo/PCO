# Quick Start Guide

Get up and running with PCO API Wrapper in 5 minutes!

## Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Credentials

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Get your PCO credentials:
   - Go to https://planning.center/settings/developer
   - Create a new Personal Access Token
   - Copy the Application ID and Secret

3. Edit `.env` and add your credentials:
```env
PCO_APP_ID=your_application_id_here
PCO_SECRET=your_application_secret_here
```

## Step 3: Start the API Server

```bash
python src/app.py
```

The server will start on http://localhost:5000

## Step 4: Test the API

### Health Check
```bash
curl http://localhost:5000/health
```

### Get All People
```bash
curl http://localhost:5000/api/people
```

### Get People by Role
```bash
curl "http://localhost:5000/api/people?role=member"
```

### Create a Person
```bash
curl -X POST http://localhost:5000/api/people \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","gender":"Male"}'
```

## Step 5: Use Utility Functions

Create a Python script:

```python
from src.pco_helpers import get_pco_client, create_or_update_person

# Initialize client
pco = get_pco_client()

# Create or update a person
person = create_or_update_person(
    pco,
    first_name="Jane",
    last_name="Smith",
    gender="Female",
    email="jane@example.com"
)

print(f"Person ID: {person['id']}")
```

## Common Operations

### Find a Person
```python
from src.pco_helpers import get_pco_client, find_person_by_name

pco = get_pco_client()
person = find_person_by_name(pco, "John", "Doe")
```

### Update Person
```python
from src.pco_helpers import get_pco_client, update_person_attribute

pco = get_pco_client()
update_person_attribute(pco, "123456", "gender", "Male")
```

### Add Email
```python
from src.pco_helpers import get_pco_client, add_email_to_person

pco = get_pco_client()
add_email_to_person(pco, "123456", "john@example.com", "Work")
```

## Run Examples

```bash
python examples/example_usage.py
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore all available [API endpoints](README.md#api-endpoints)
- Check out [utility functions](README.md#utility-functions)
- Review [error handling](README.md#error-handling) best practices

## Troubleshooting

### "ModuleNotFoundError: No module named 'pypco'"
```bash
pip install -r requirements.txt
```

### "ValueError: PCO_APP_ID and PCO_SECRET must be set"
- Check that `.env` file exists
- Verify credentials are correct
- Make sure `.env` is in the project root

### "401 Unauthorized"
- Verify PCO credentials are correct
- Check token hasn't expired
- Ensure proper permissions in PCO

## Need Help?

- Check [README.md](README.md) for full documentation
- Review [examples/example_usage.py](examples/example_usage.py)
- Visit [pypco documentation](https://pypco.readthedocs.io/)
- Check [PCO API docs](https://developer.planning.center/docs/)

---

Happy coding! 🚀