# 🚀 PCO Services Startup Guide

This guide explains how to automatically start and manage all PCO services.

## Quick Start

### Option 1: Automatic Startup (Recommended)

Simply double-click the startup script:
```
start-all-services.bat
```

This will:
1. ✅ Check if Ollama is running
2. ✅ Start PCO API Wrapper (port 5000)
3. ✅ Start PCO AI Service (port 5001)
4. ✅ Verify all services are healthy

### Option 2: Manual Startup

If you prefer to start services individually:

**Terminal 1 - PCO API Wrapper:**
```bash
cd pco-api-wrapper
python src/app.py
```

**Terminal 2 - PCO AI Service:**
```bash
cd pco-api-wrapper/pco-ai-service
python src/app.py
```

## Prerequisites

Before starting the services, ensure:

1. **Ollama is running:**
   ```bash
   ollama serve
   ```
   Or check if it's already running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Environment variables are configured:**
   - `pco-api-wrapper/.env` - PCO API credentials
   - `pco-api-wrapper/pco-ai-service/.env` - AI service configuration

3. **Python dependencies are installed:**
   ```bash
   pip install -r requirements.txt
   ```

## Service Management

### Start All Services
```bash
start-all-services.bat
```

### Stop All Services
```bash
stop-all-services.bat
```

### Check Service Status

**PCO API Wrapper:**
```bash
curl http://localhost:5000/health
```

**PCO AI Service:**
```bash
curl http://localhost:5001/health
```

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| PCO API Wrapper | 5000 | http://localhost:5000 |
| PCO AI Service | 5001 | http://localhost:5001 |
| Ollama | 11434 | http://localhost:11434 |

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

1. **Check what's using the port:**
   ```bash
   netstat -ano | findstr :5000
   netstat -ano | findstr :5001
   ```

2. **Stop the services:**
   ```bash
   stop-all-services.bat
   ```

3. **Or manually kill the process:**
   ```bash
   taskkill /F /PID <process_id>
   ```

### Ollama Not Running

If you see "Ollama is not running":

1. **Start Ollama:**
   ```bash
   ollama serve
   ```

2. **Or check if it's already running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Service Won't Start

1. **Check the logs** in the service window
2. **Verify environment variables** are set correctly
3. **Ensure Python dependencies** are installed
4. **Check firewall settings** aren't blocking the ports

## Automatic Startup on Windows Boot

To make services start automatically when Windows boots:

### Method 1: Task Scheduler (Recommended)

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name: "Start PCO Services"
4. Trigger: **At log on**
5. Action: **Start a program**
6. Program: `C:\Users\lloyd.ngcobo\Documents\PCO\Projects\pco-api-wrapper\start-all-services.bat`
7. Click **Finish**

### Method 2: Startup Folder

1. Press `Win + R`
2. Type: `shell:startup`
3. Create a shortcut to `start-all-services.bat` in this folder

### Method 3: Windows Service (Advanced)

For production environments, consider using NSSM (Non-Sucking Service Manager):

```bash
# Install NSSM
choco install nssm

# Create service for API Wrapper
nssm install PCOAPIWrapper "C:\Python312\python.exe" "C:\Users\lloyd.ngcobo\Documents\PCO\Projects\pco-api-wrapper\src\app.py"

# Create service for AI Service
nssm install PCOAIService "C:\Python312\python.exe" "C:\Users\lloyd.ngcobo\Documents\PCO\Projects\pco-api-wrapper\pco-ai-service\src\app.py"

# Start services
nssm start PCOAPIWrapper
nssm start PCOAIService
```

## Monitoring Services

### View Logs

Services run in separate command windows. To view logs:
- Keep the service windows open
- Or redirect output to log files (modify the batch script)

### Health Checks

Create a monitoring script to check service health:

```bash
# check-services.bat
@echo off
echo Checking PCO Services...
curl -s http://localhost:5000/health
echo.
curl -s http://localhost:5001/health
```

## Development vs Production

### Development Mode
- Use `start-all-services.bat` for easy debugging
- Services run in visible command windows
- Easy to stop and restart

### Production Mode
- Use Windows Services (NSSM)
- Services run in background
- Automatic restart on failure
- Logs to files

## Next Steps

After starting the services:

1. **Test the API Wrapper:**
   ```bash
   curl http://localhost:5000/people
   ```

2. **Test the AI Service:**
   ```bash
   curl http://localhost:5001/api/ai/models
   ```

3. **Use the Interactive Chat:**
   ```bash
   cd pco-api-wrapper/pco-ai-service
   python interactive_chat.py
   ```

## Support

For issues or questions:
- Check the logs in the service windows
- Review the main README.md
- Check TROUBLESHOOTING.md for common issues