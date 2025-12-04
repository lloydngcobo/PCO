# How to Run PCO API Wrapper

## Quick Start

### On Linux/Mac (Jump Server)

```bash
cd /root/pco2025/pco-api-wrapper

# Option 1: Use the startup script (recommended)
chmod +x start.sh
./start.sh

# Option 2: Run directly
python src/app.py
```

### On Windows

```bash
cd Projects\pco-api-wrapper

# Run directly
python src\app.py
```

## What You Should See

When the application starts successfully, you'll see:

```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

## Testing the API

Once running, test with:

```bash
# Health check
curl http://localhost:5000/health

# Get all people
curl http://localhost:5000/api/people

# Get service types
curl http://localhost:5000/api/services/service-types
```

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution:** This has been fixed! All import statements have been updated to use relative imports instead of absolute imports with `src.` prefix.

**Fixed files:**
- `src/services_api.py` - Changed `from src.services_helpers` to `from services_helpers`
- `src/services_helpers.py` - Changed `from src.cache` to `from cache`
- `src/pco_helpers_cached.py` - Changed `from src.cache` to `from cache`

**How to run:**
```bash
# ✅ Correct way to start the application
python src/app.py

# Or use the startup script
./start.sh
```

**Note:** Don't run module files directly (like `services_api.py`). Always run `app.py` which imports the modules correctly.

### Issue: "PCO_APP_ID and PCO_SECRET must be set"

**Solution:** Create a `.env` file with your PCO credentials:

```bash
cp .env.example .env
# Edit .env and add your credentials
```

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution:** Install dependencies:

```bash
pip install -r requirements.txt
```

## Project Structure

```
pco-api-wrapper/
├── src/
│   ├── app.py              # ← Main application (run this!)
│   ├── services_api.py     # ← Services endpoints (imported by app.py)
│   ├── services_helpers.py # ← Helper functions
│   ├── pco_helpers.py      # ← PCO utility functions
│   └── cache.py            # ← Caching utilities
├── .env                    # ← Your credentials (create this)
├── requirements.txt        # ← Python dependencies
└── start.sh               # ← Startup script
```

## AI Service

The AI service is a separate component. To run it:

```bash
cd pco-ai-service
python src/app.py
```

See `pco-ai-service/QUICKSTART.md` for details.