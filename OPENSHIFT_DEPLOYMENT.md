# OpenShift Deployment Guide

Complete guide for deploying the PCO API Wrapper to OpenShift.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Deployment](#quick-deployment)
3. [Detailed Deployment Steps](#detailed-deployment-steps)
4. [Configuration](#configuration)
5. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
6. [Scaling](#scaling)
7. [CI/CD Integration](#cicd-integration)

## Prerequisites

### Required Tools

- OpenShift CLI (`oc`) installed and configured
- Docker or Podman for building images
- Access to an OpenShift cluster
- PCO API credentials (Application ID and Secret)

### Verify OpenShift Access

```bash
# Login to OpenShift
oc login <your-openshift-cluster-url>

# Verify connection
oc whoami
oc version
```

## Quick Deployment

### Option 1: Using oc apply (Recommended)

```bash
# 1. Create a new project
oc new-project pco-api-wrapper

# 2. Create secret with your PCO credentials
oc create secret generic pco-credentials \
  --from-literal=app-id=17a7ab500fe6692d63426b9737711c6f8bb3066e25926891739d796266394066 \
  --from-literal=secret=537e7ab54b9df81ce7e8f4087d55ba67d2c320c9db24630b96f6993113db1b34

# 3. Build and push the image
docker build -t pco-api-wrapper:latest .
docker tag pco-api-wrapper:latest <your-registry>/pco-api-wrapper:latest
docker push <your-registry>/pco-api-wrapper:latest

# 4. Deploy all resources
oc apply -f openshift/configmap.yaml
oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml

# 5. Verify deployment
oc get pods
oc get route
```

### Option 2: Using Kustomize

```bash
# Deploy using kustomize
oc apply -k openshift/

# Verify
oc get all -l app=pco-api-wrapper
```

### Option 3: Using OpenShift Source-to-Image (S2I)

```bash
# Create new app from source
oc new-app python:3.11~https://github.com/your-repo/pco-api-wrapper.git \
  --name=pco-api-wrapper

# Create secret
oc create secret generic pco-credentials \
  --from-literal=app-id=YOUR_PCO_APP_ID \
  --from-literal=secret=YOUR_PCO_SECRET

# Set environment variables from secret
oc set env deployment/pco-api-wrapper \
  --from=secret/pco-credentials

# Expose the service
oc expose svc/pco-api-wrapper

# Verify
oc get route pco-api-wrapper
```

## Detailed Deployment Steps

### Step 1: Create OpenShift Project

```bash
# Create a new project (namespace)
oc new-project pco-api-wrapper \
  --display-name="PCO API Wrapper" \
  --description="Planning Center Online API Wrapper Service"

# Verify project
oc project
```

### Step 2: Build Container Image

#### Option A: Build Locally and Push

```bash
# Build the image
docker build -t pco-api-wrapper:v1.0.0 .

# Tag for your registry
docker tag pco-api-wrapper:v1.0.0 \
  quay.io/your-org/pco-api-wrapper:v1.0.0

# Push to registry
docker push quay.io/your-org/pco-api-wrapper:v1.0.0
```

#### Option B: Build in OpenShift

```bash
# Create BuildConfig
oc new-build --name=pco-api-wrapper \
  --binary \
  --strategy=docker

# Start build from local directory
oc start-build pco-api-wrapper \
  --from-dir=. \
  --follow

# Verify build
oc get builds
oc logs -f build/pco-api-wrapper-1
```

### Step 3: Create Secrets

```bash
# Create secret for PCO credentials
oc create secret generic pco-credentials \
  --from-literal=app-id=YOUR_PCO_APP_ID \
  --from-literal=secret=YOUR_PCO_SECRET

# Verify secret
oc get secret pco-credentials
oc describe secret pco-credentials
```

### Step 4: Deploy Application

```bash
# Apply ConfigMap
oc apply -f openshift/configmap.yaml

# Apply Deployment
oc apply -f openshift/deployment.yaml

# Apply Service
oc apply -f openshift/service.yaml

# Apply Route
oc apply -f openshift/route.yaml

# Verify deployment
oc get all
```

### Step 5: Verify Deployment

```bash
# Check pod status
oc get pods -l app=pco-api-wrapper

# Check logs
oc logs -f deployment/pco-api-wrapper

# Get route URL
oc get route pco-api-wrapper -o jsonpath='{.spec.host}'

# Test the application
ROUTE_URL=$(oc get route pco-api-wrapper -o jsonpath='{.spec.host}')
curl https://$ROUTE_URL/health
```

## Configuration

### Environment Variables

The application uses the following environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PCO_APP_ID` | PCO Application ID | - | Yes |
| `PCO_SECRET` | PCO Application Secret | - | Yes |
| `FLASK_HOST` | Flask bind address | 0.0.0.0 | No |
| `FLASK_PORT` | Flask port | 8080 | No |
| `FLASK_DEBUG` | Debug mode | False | No |
| `LOG_LEVEL` | Logging level | INFO | No |

### Update Configuration

```bash
# Update ConfigMap
oc edit configmap pco-api-wrapper-config

# Update Secret
oc create secret generic pco-credentials \
  --from-literal=app-id=NEW_APP_ID \
  --from-literal=secret=NEW_SECRET \
  --dry-run=client -o yaml | oc apply -f -

# Restart deployment to pick up changes
oc rollout restart deployment/pco-api-wrapper
```

### Resource Limits

Adjust resource limits in `openshift/deployment.yaml`:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

Apply changes:

```bash
oc apply -f openshift/deployment.yaml
```

## Monitoring & Troubleshooting

### Check Application Health

```bash
# Get route URL
ROUTE_URL=$(oc get route pco-api-wrapper -o jsonpath='{.spec.host}')

# Health check
curl https://$ROUTE_URL/health

# Test API endpoint
curl https://$ROUTE_URL/api/people
```

### View Logs

```bash
# View current logs
oc logs deployment/pco-api-wrapper

# Follow logs
oc logs -f deployment/pco-api-wrapper

# View logs from specific pod
oc logs <pod-name>

# View previous pod logs (if crashed)
oc logs <pod-name> --previous
```

### Debug Pod Issues

```bash
# Describe pod
oc describe pod <pod-name>

# Get pod events
oc get events --sort-by='.lastTimestamp'

# Execute command in pod
oc exec -it <pod-name> -- /bin/bash

# Check pod status
oc get pods -l app=pco-api-wrapper -o wide
```

### Common Issues

#### Issue: Pods not starting

```bash
# Check pod status
oc describe pod <pod-name>

# Common causes:
# 1. Image pull errors - verify image exists
# 2. Secret not found - verify secret exists
# 3. Resource limits - check cluster resources
```

#### Issue: Application crashes

```bash
# Check logs
oc logs <pod-name> --previous

# Common causes:
# 1. Missing environment variables
# 2. Invalid PCO credentials
# 3. Network connectivity issues
```

#### Issue: Route not accessible

```bash
# Verify route
oc get route pco-api-wrapper

# Check service
oc get svc pco-api-wrapper

# Test from within cluster
oc run test-pod --image=curlimages/curl --rm -it -- \
  curl http://pco-api-wrapper:8080/health
```

## Scaling

### Manual Scaling

```bash
# Scale to 3 replicas
oc scale deployment/pco-api-wrapper --replicas=3

# Verify scaling
oc get pods -l app=pco-api-wrapper
```

### Horizontal Pod Autoscaler (HPA)

```bash
# Create HPA
oc autoscale deployment/pco-api-wrapper \
  --min=2 \
  --max=10 \
  --cpu-percent=80

# Verify HPA
oc get hpa
oc describe hpa pco-api-wrapper
```

### Update Deployment

```bash
# Update image
oc set image deployment/pco-api-wrapper \
  pco-api-wrapper=quay.io/your-org/pco-api-wrapper:v1.1.0

# Check rollout status
oc rollout status deployment/pco-api-wrapper

# Rollback if needed
oc rollout undo deployment/pco-api-wrapper
```

## CI/CD Integration

### Using OpenShift Pipelines (Tekton)

Create a pipeline for automated builds and deployments:

```yaml
# pipeline.yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: pco-api-wrapper-pipeline
spec:
  params:
    - name: git-url
      type: string
    - name: image-name
      type: string
  tasks:
    - name: fetch-repository
      taskRef:
        name: git-clone
      params:
        - name: url
          value: $(params.git-url)
    
    - name: build-image
      taskRef:
        name: buildah
      params:
        - name: IMAGE
          value: $(params.image-name)
      runAfter:
        - fetch-repository
    
    - name: deploy
      taskRef:
        name: openshift-client
      params:
        - name: SCRIPT
          value: |
            oc apply -f openshift/
            oc rollout status deployment/pco-api-wrapper
      runAfter:
        - build-image
```

### Using GitHub Actions

```yaml
# .github/workflows/deploy-openshift.yml
name: Deploy to OpenShift

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Login to OpenShift
        uses: redhat-actions/oc-login@v1
        with:
          openshift_server_url: ${{ secrets.OPENSHIFT_SERVER }}
          openshift_token: ${{ secrets.OPENSHIFT_TOKEN }}
      
      - name: Build and Push Image
        run: |
          docker build -t pco-api-wrapper:${{ github.sha }} .
          docker push pco-api-wrapper:${{ github.sha }}
      
      - name: Deploy to OpenShift
        run: |
          oc apply -f openshift/
          oc set image deployment/pco-api-wrapper \
            pco-api-wrapper=pco-api-wrapper:${{ github.sha }}
```

## Security Best Practices

### 1. Use Secrets for Sensitive Data

```bash
# Never commit secrets to git
# Always use OpenShift secrets
oc create secret generic pco-credentials \
  --from-literal=app-id=$PCO_APP_ID \
  --from-literal=secret=$PCO_SECRET
```

### 2. Enable Security Context Constraints

The deployment already includes security contexts:

```yaml
securityContext:
  allowPrivilegeEscalation: false
  runAsNonRoot: true
  capabilities:
    drop:
    - ALL
```

### 3. Use Network Policies

```bash
# Create network policy to restrict traffic
oc apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pco-api-wrapper-netpol
spec:
  podSelector:
    matchLabels:
      app: pco-api-wrapper
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 8080
EOF
```

### 4. Enable TLS

The route configuration already enables TLS:

```yaml
tls:
  termination: edge
  insecureEdgeTerminationPolicy: Redirect
```

## Backup and Disaster Recovery

### Backup Configuration

```bash
# Export all resources
oc get all,configmap,secret,route -l app=pco-api-wrapper -o yaml > backup.yaml

# Backup to git
git add openshift/
git commit -m "Backup OpenShift configuration"
git push
```

### Restore from Backup

```bash
# Restore from backup file
oc apply -f backup.yaml

# Or restore from git
git pull
oc apply -f openshift/
```

## Performance Tuning

### 1. Adjust Worker Processes

For production, consider using Gunicorn:

```dockerfile
# Add to Dockerfile
RUN pip install gunicorn

# Update CMD
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "src.app:app"]
```

### 2. Enable Caching

Add Redis for caching:

```bash
# Deploy Redis
oc new-app redis:6

# Update application to use Redis
```

### 3. Database Connection Pooling

The pypco library already handles connection pooling via requests.Session.

## Monitoring with Prometheus

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: pco-api-wrapper
spec:
  selector:
    matchLabels:
      app: pco-api-wrapper
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

## Summary

Your PCO API Wrapper is now ready for OpenShift deployment with:

✅ Multi-stage Docker build for optimization  
✅ Non-root user for security  
✅ Health checks and readiness probes  
✅ Resource limits and requests  
✅ Secrets management  
✅ TLS-enabled routes  
✅ Horizontal scaling support  
✅ CI/CD integration examples  

For questions or issues, refer to the main [README.md](README.md) or OpenShift documentation.

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-18