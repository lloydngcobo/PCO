# Docker Build Troubleshooting Guide

This guide helps resolve network connectivity issues when building the Docker image.

## Problem: Network Connectivity Issues

If you're seeing errors like:
- `Temporary failure resolving 'deb.debian.org'`
- `Temporary failure in name resolution`
- `Failed to establish a new connection`

This means Docker can't reach external repositories during the build.

## Solutions

### Solution 1: Fix Docker DNS (Recommended)

#### On Linux:
```bash
# Edit Docker daemon config
sudo nano /etc/docker/daemon.json

# Add DNS servers
{
  "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]
}

# Restart Docker
sudo systemctl restart docker
```

#### On Windows (Docker Desktop):
1. Open Docker Desktop
2. Go to Settings → Docker Engine
3. Add DNS configuration:
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```
4. Click "Apply & Restart"

#### On macOS (Docker Desktop):
1. Open Docker Desktop
2. Go to Preferences → Docker Engine
3. Add DNS configuration (same as Windows)
4. Click "Apply & Restart"

### Solution 2: Use Offline Build

If you have persistent network issues, use the offline build method:

```bash
# Step 1: Download packages on your host (where network works)
cd pco-api-wrapper
mkdir wheels
pip download -r requirements.txt -d ./wheels

# Step 2: Build using offline Dockerfile
docker build -f Dockerfile.offline -t pco-api-wrapper:latest .
```

### Solution 3: Use Proxy

If you're behind a corporate proxy:

```bash
# Build with proxy
docker build \
  --build-arg HTTP_PROXY=http://proxy.company.com:8080 \
  --build-arg HTTPS_PROXY=http://proxy.company.com:8080 \
  --build-arg NO_PROXY=localhost,127.0.0.1 \
  -t pco-api-wrapper:latest .
```

### Solution 4: Use Host Network

```bash
# Build using host network (Linux only)
docker build --network=host -t pco-api-wrapper:latest .
```

### Solution 5: Use Pre-built Base Image

Create a custom base image with dependencies pre-installed:

```bash
# Step 1: Create base image (when network works)
docker pull python:3.11-slim
docker run -it python:3.11-slim bash
# Inside container:
pip install pypco flask python-dotenv requests
exit

# Step 2: Commit the container
docker commit <container-id> pco-base:latest

# Step 3: Update Dockerfile to use your base
# Change FROM python:3.11-slim to FROM pco-base:latest
```

### Solution 6: Build on Different Machine

If your local machine has network issues:

1. **Build on a cloud VM:**
   ```bash
   # On a cloud VM with good connectivity
   git clone your-repo
   cd pco-api-wrapper
   docker build -t pco-api-wrapper:latest .
   docker save pco-api-wrapper:latest > pco-api-wrapper.tar
   
   # Transfer to your machine
   scp pco-api-wrapper.tar your-machine:/path/
   
   # On your machine
   docker load < pco-api-wrapper.tar
   ```

2. **Use GitHub Actions or GitLab CI:**
   - Let CI/CD build the image
   - Push to container registry
   - Pull on your machine

### Solution 7: Use OpenShift S2I (Source-to-Image)

Skip Docker entirely and let OpenShift build the image:

```bash
# Login to OpenShift
oc login your-cluster

# Create new app from source
oc new-app python:3.11~https://github.com/your-repo/pco-api-wrapper.git

# Or from local directory
oc new-app python:3.11~. --name=pco-api-wrapper

# OpenShift will build the image for you
```

## Verification Steps

After trying any solution, verify:

### 1. Test DNS Resolution
```bash
# Test if Docker can resolve DNS
docker run --rm alpine nslookup pypi.org
docker run --rm alpine ping -c 3 8.8.8.8
```

### 2. Test Network Connectivity
```bash
# Test if Docker can reach PyPI
docker run --rm python:3.11-slim pip install --dry-run pypco
```

### 3. Check Docker Network
```bash
# List Docker networks
docker network ls

# Inspect default bridge
docker network inspect bridge
```

## Alternative: Deploy Without Docker

If Docker build continues to fail, you can deploy directly to OpenShift without Docker:

### Method 1: OpenShift Binary Build

```bash
# Create build config
oc new-build python:3.11 --name=pco-api-wrapper --binary=true

# Start build from local directory
oc start-build pco-api-wrapper --from-dir=. --follow

# Create deployment
oc new-app pco-api-wrapper

# Expose service
oc expose svc/pco-api-wrapper
```

### Method 2: Use Podman Instead of Docker

Podman often has better network handling:

```bash
# Install Podman
# On RHEL/CentOS: sudo dnf install podman
# On Ubuntu: sudo apt install podman

# Build with Podman
podman build -t pco-api-wrapper:latest .

# Save and load to Docker if needed
podman save pco-api-wrapper:latest > image.tar
docker load < image.tar
```

### Method 3: Use Buildah

```bash
# Install Buildah
sudo dnf install buildah  # or apt install buildah

# Build with Buildah
buildah bud -t pco-api-wrapper:latest .

# Push directly to OpenShift registry
buildah push pco-api-wrapper:latest \
  docker://image-registry.openshift-image-registry.svc:5000/your-project/pco-api-wrapper:latest
```

## Common Network Issues

### Issue 1: Corporate Firewall
**Symptom:** Timeouts when accessing external sites  
**Solution:** Use proxy settings (Solution 3)

### Issue 2: VPN Interference
**Symptom:** Intermittent connectivity  
**Solution:** Disconnect VPN during build or configure split tunneling

### Issue 3: DNS Resolution Failure
**Symptom:** "Temporary failure resolving"  
**Solution:** Configure Docker DNS (Solution 1)

### Issue 4: IPv6 Issues
**Symptom:** Connection timeouts  
**Solution:** Disable IPv6 in Docker:
```json
{
  "ipv6": false
}
```

## Quick Diagnostic Script

Save this as `diagnose-docker-network.sh`:

```bash
#!/bin/bash

echo "=== Docker Network Diagnostics ==="
echo ""

echo "1. Testing DNS resolution..."
docker run --rm alpine nslookup pypi.org

echo ""
echo "2. Testing internet connectivity..."
docker run --rm alpine ping -c 3 8.8.8.8

echo ""
echo "3. Testing HTTPS connectivity..."
docker run --rm alpine wget -O- https://pypi.org/simple/ | head -n 5

echo ""
echo "4. Docker daemon DNS settings..."
cat /etc/docker/daemon.json 2>/dev/null || echo "No daemon.json found"

echo ""
echo "5. Docker network list..."
docker network ls

echo ""
echo "=== Diagnostics Complete ==="
```

Run it:
```bash
chmod +x diagnose-docker-network.sh
./diagnose-docker-network.sh
```

## Still Having Issues?

If none of these solutions work:

1. **Check your environment:**
   - Are you behind a corporate firewall?
   - Is your network blocking Docker Hub or PyPI?
   - Do you have antivirus software interfering?

2. **Try a different approach:**
   - Use OpenShift S2I (no Docker needed)
   - Build on a different machine
   - Use pre-built images from Docker Hub

3. **Contact your network administrator:**
   - Request access to PyPI (pypi.org)
   - Request access to Docker Hub (docker.io)
   - Get proxy settings if applicable

## Success Indicators

You'll know it's working when:
- ✅ `docker run --rm alpine nslookup pypi.org` succeeds
- ✅ `docker build` completes without network errors
- ✅ `pip install` inside container works
- ✅ Image builds successfully

## Next Steps After Successful Build

Once your image builds successfully:

```bash
# Test the image
docker run -p 8080:8080 \
  -e PCO_APP_ID=your_id \
  -e PCO_SECRET=your_secret \
  pco-api-wrapper:latest

# Push to registry
docker tag pco-api-wrapper:latest your-registry/pco-api-wrapper:latest
docker push your-registry/pco-api-wrapper:latest

# Deploy to OpenShift
oc apply -f openshift/
```

---

**Need more help?** Check the main [OPENSHIFT_DEPLOYMENT.md](OPENSHIFT_DEPLOYMENT.md) for deployment options that don't require local Docker builds.