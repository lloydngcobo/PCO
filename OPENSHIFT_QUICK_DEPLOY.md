# OpenShift Quick Deployment Guide

## Fastest Way to Deploy (Using Docker Strategy)

Since you have a Dockerfile, use the Docker build strategy:

### Step 1: Login to OpenShift
```bash
oc login <your-cluster-url>
```

### Step 2: Create Project
```bash
oc new-project pco-api-wrapper
```

### Step 3: Create Secret
```bash
oc create secret generic pco-credentials \
  --from-literal=app-id=YOUR_PCO_APP_ID \
  --from-literal=secret=YOUR_PCO_SECRET
```

### Step 4: Deploy Using Docker Strategy
```bash
cd pco-api-wrapper

# Use Docker strategy (builds using your Dockerfile)
oc new-app . --name=pco-api-wrapper --strategy=docker
```

### Step 5: Set Environment Variables
```bash
oc set env deployment/pco-api-wrapper \
  --from=secret/pco-credentials
```

### Step 6: Expose the Service
```bash
oc expose svc/pco-api-wrapper
```

### Step 7: Check Status
```bash
# Watch the build
oc logs -f bc/pco-api-wrapper

# Check pods
oc get pods

# Get the route URL
oc get route pco-api-wrapper
```

### Step 8: Test the Application
```bash
# Get the URL
ROUTE_URL=$(oc get route pco-api-wrapper -o jsonpath='{.spec.host}')

# Test health endpoint
curl https://$ROUTE_URL/health
```

## Alternative: Use Existing Manifests

If the Docker build still has network issues in OpenShift, use the pre-created manifests:

### Option A: Apply All Manifests
```bash
# Make sure you're in the right project
oc project pco-api-wrapper

# Create secret first
oc create secret generic pco-credentials \
  --from-literal=app-id=YOUR_PCO_APP_ID \
  --from-literal=secret=YOUR_PCO_SECRET

# Apply all manifests
oc apply -f openshift/configmap.yaml
oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml
```

**Note:** You'll need to update the image reference in `openshift/deployment.yaml` to point to a pre-built image or build it separately.

### Option B: Use Kustomize
```bash
# Update secret in openshift/secret.yaml first
# Then apply everything
oc apply -k openshift/
```

## Alternative: Binary Build (No Network Issues!)

This method uploads your code directly to OpenShift, avoiding local Docker build:

### Step 1: Create Build Config
```bash
oc new-build --name=pco-api-wrapper \
  --binary=true \
  --strategy=docker
```

### Step 2: Start Build from Local Directory
```bash
# This uploads your local files to OpenShift
oc start-build pco-api-wrapper \
  --from-dir=. \
  --follow
```

### Step 3: Create Deployment
```bash
# Create deployment from the built image
oc new-app pco-api-wrapper

# Set environment variables
oc set env deployment/pco-api-wrapper \
  --from=secret/pco-credentials

# Expose service
oc expose svc/pco-api-wrapper
```

## Troubleshooting

### Build Fails with Network Issues

If the build fails in OpenShift due to network issues:

1. **Check if OpenShift can reach PyPI:**
   ```bash
   oc run test --image=python:3.11-slim --rm -it -- pip install pypco
   ```

2. **Use a different Python base image:**
   ```bash
   # Try UBI (Universal Base Image) which might have better connectivity
   oc new-app registry.access.redhat.com/ubi9/python-311~. \
     --name=pco-api-wrapper
   ```

3. **Configure HTTP proxy in BuildConfig:**
   ```bash
   oc set env bc/pco-api-wrapper \
     HTTP_PROXY=http://your-proxy:port \
     HTTPS_PROXY=http://your-proxy:port
   ```

### Pod Fails to Start

```bash
# Check pod logs
oc logs deployment/pco-api-wrapper

# Check pod events
oc describe pod <pod-name>

# Common issues:
# - Missing secret: Create pco-credentials secret
# - Image pull error: Check image reference
# - Crash loop: Check application logs
```

### Can't Access Application

```bash
# Check if route exists
oc get route

# Check if service is working
oc get svc

# Test from within cluster
oc run test --image=curlimages/curl --rm -it -- \
  curl http://pco-api-wrapper:8080/health
```

## Complete Example (Copy-Paste Ready)

```bash
# 1. Login
oc login <your-cluster-url>

# 2. Create project
oc new-project pco-api-wrapper

# 3. Navigate to project directory
cd pco-api-wrapper

# 4. Create secret (replace with your actual credentials)
oc create secret generic pco-credentials \
  --from-literal=app-id=YOUR_PCO_APP_ID \
  --from-literal=secret=YOUR_PCO_SECRET

# 5. Deploy using Docker strategy
oc new-app . --name=pco-api-wrapper --strategy=docker

# 6. Watch the build
oc logs -f bc/pco-api-wrapper

# 7. Once build completes, set environment variables
oc set env deployment/pco-api-wrapper \
  --from=secret/pco-credentials

# 8. Expose the service
oc expose svc/pco-api-wrapper

# 9. Get the URL
oc get route pco-api-wrapper

# 10. Test
ROUTE_URL=$(oc get route pco-api-wrapper -o jsonpath='{.spec.host}')
curl https://$ROUTE_URL/health
```

## Using Binary Build (Recommended if Network Issues Persist)

```bash
# 1-3. Same as above (login, create project, navigate)

# 4. Create secret
oc create secret generic pco-credentials \
  --from-literal=app-id=YOUR_PCO_APP_ID \
  --from-literal=secret=YOUR_PCO_SECRET

# 5. Create binary build
oc new-build --name=pco-api-wrapper \
  --binary=true \
  --strategy=docker

# 6. Upload and build
oc start-build pco-api-wrapper \
  --from-dir=. \
  --follow

# 7. Create deployment
oc new-app pco-api-wrapper

# 8. Set environment variables
oc set env deployment/pco-api-wrapper \
  --from=secret/pco-credentials

# 9. Expose service
oc expose svc/pco-api-wrapper

# 10. Get URL and test
oc get route pco-api-wrapper
ROUTE_URL=$(oc get route pco-api-wrapper -o jsonpath='{.spec.host}')
curl https://$ROUTE_URL/health
```

## Verification Checklist

After deployment, verify:

- [ ] Build completed successfully: `oc get builds`
- [ ] Pod is running: `oc get pods`
- [ ] Service exists: `oc get svc`
- [ ] Route is created: `oc get route`
- [ ] Health check passes: `curl https://<route-url>/health`
- [ ] API responds: `curl https://<route-url>/api/people`

## Cleanup

To remove everything:

```bash
# Delete the project (removes everything)
oc delete project pco-api-wrapper

# Or delete individual resources
oc delete all -l app=pco-api-wrapper
oc delete secret pco-credentials
oc delete route pco-api-wrapper
```

## Next Steps

Once deployed successfully:

1. **Scale the application:**
   ```bash
   oc scale deployment/pco-api-wrapper --replicas=3
   ```

2. **Enable autoscaling:**
   ```bash
   oc autoscale deployment/pco-api-wrapper --min=2 --max=10 --cpu-percent=80
   ```

3. **Monitor logs:**
   ```bash
   oc logs -f deployment/pco-api-wrapper
   ```

4. **Update the application:**
   ```bash
   # Make changes to code
   oc start-build pco-api-wrapper --from-dir=. --follow
   ```

---

**Need more help?** See [OPENSHIFT_DEPLOYMENT.md](OPENSHIFT_DEPLOYMENT.md) for detailed documentation.