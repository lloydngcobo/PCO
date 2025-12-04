# PCO AI Service - OpenShift Deployment Guide

Complete guide for deploying the PCO AI Service to OpenShift.

## Prerequisites

- OpenShift cluster access (4.x or later)
- `oc` CLI installed and configured
- PCO API Wrapper already deployed
- Ollama service deployed or accessible

## Architecture on OpenShift

```
┌─────────────────────────────────────────────┐
│           OpenShift Cluster                 │
│                                             │
│  ┌──────────────┐      ┌─────────────────┐│
│  │ PCO AI       │─────▶│ PCO API Wrapper ││
│  │ Service      │      │ Service         ││
│  │ (Port 5001)  │      │ (Port 5000)     ││
│  └──────┬───────┘      └─────────────────┘│
│         │                                  │
│         ▼                                  │
│  ┌──────────────┐                         │
│  │ Ollama       │                         │
│  │ Service      │                         │
│  │ (Port 11434) │                         │
│  └──────────────┘                         │
│                                             │
│  ┌──────────────┐                         │
│  │ Route (HTTPS)│                         │
│  └──────────────┘                         │
└─────────────────────────────────────────────┘
```

## Step 1: Deploy Ollama to OpenShift

### Option A: Deploy Ollama in OpenShift

Create `ollama-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  labels:
    app: ollama
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
        volumeMounts:
        - name: ollama-data
          mountPath: /root/.ollama
      volumes:
      - name: ollama-data
        persistentVolumeClaim:
          claimName: ollama-pvc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ollama-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: ollama
spec:
  type: ClusterIP
  ports:
  - port: 11434
    targetPort: 11434
  selector:
    app: ollama
```

Deploy:

```bash
oc apply -f ollama-deployment.yaml

# Wait for Ollama to be ready
oc wait --for=condition=ready pod -l app=ollama --timeout=300s

# Pull the model
oc exec -it deployment/ollama -- ollama pull llama3.1:8b
```

### Option B: Use External Ollama

If you have Ollama running externally, update the ConfigMap with the external URL.

## Step 2: Prepare the Project

```bash
# Login to OpenShift
oc login --server=https://your-openshift-cluster:6443

# Create or switch to project
oc new-project pco-system

# Or use existing project
oc project pco-system
```

## Step 3: Build the Container Image

### Option A: Build in OpenShift

```bash
# Create BuildConfig
oc new-build --name=pco-ai-service \
  --binary \
  --strategy=docker

# Start the build
oc start-build pco-ai-service \
  --from-dir=. \
  --follow

# Tag the image
oc tag pco-ai-service:latest pco-ai-service:v1.0.0
```

### Option B: Build Locally and Push

```bash
# Build locally
docker build -t pco-ai-service:latest .

# Tag for OpenShift registry
docker tag pco-ai-service:latest \
  default-route-openshift-image-registry.apps.your-cluster/pco-system/pco-ai-service:latest

# Login to OpenShift registry
docker login -u $(oc whoami) -p $(oc whoami -t) \
  default-route-openshift-image-registry.apps.your-cluster

# Push image
docker push default-route-openshift-image-registry.apps.your-cluster/pco-system/pco-ai-service:latest
```

## Step 4: Configure the Deployment

Edit `openshift/configmap.yaml` with your actual URLs:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pco-ai-config
data:
  # Update these with your actual service URLs
  pco_api_url: "http://pco-api-wrapper:5000"
  ollama_api_url: "http://ollama:11434/api/generate"
  ollama_model: "llama3.1:8b"
```

## Step 5: Deploy the AI Service

```bash
# Apply all configurations
oc apply -k openshift/

# Verify deployment
oc get pods -l app=pco-ai-service

# Check logs
oc logs -f deployment/pco-ai-service

# Get the route URL
oc get route pco-ai-service -o jsonpath='{.spec.host}'
```

## Step 6: Verify the Deployment

```bash
# Get the route URL
ROUTE_URL=$(oc get route pco-ai-service -o jsonpath='{.spec.host}')

# Test health endpoint
curl https://$ROUTE_URL/health

# Test AI query
curl -X POST https://$ROUTE_URL/api/ai/query/people \
  -H "Content-Type: application/json" \
  -d '{"query": "How many members do we have?"}'
```

## Configuration Management

### Update ConfigMap

```bash
# Edit ConfigMap
oc edit configmap pco-ai-config

# Or apply changes
oc apply -f openshift/configmap.yaml

# Restart deployment to pick up changes
oc rollout restart deployment/pco-ai-service
```

### Scale the Deployment

```bash
# Scale up
oc scale deployment/pco-ai-service --replicas=3

# Scale down
oc scale deployment/pco-ai-service --replicas=1
```

### Update the Image

```bash
# After building a new image
oc rollout latest deployment/pco-ai-service

# Or set a specific image
oc set image deployment/pco-ai-service \
  pco-ai-service=pco-ai-service:v1.0.1
```

## Monitoring and Troubleshooting

### View Logs

```bash
# Current logs
oc logs deployment/pco-ai-service

# Follow logs
oc logs -f deployment/pco-ai-service

# Previous container logs
oc logs deployment/pco-ai-service --previous
```

### Check Pod Status

```bash
# Get pod details
oc get pods -l app=pco-ai-service

# Describe pod
oc describe pod -l app=pco-ai-service

# Get events
oc get events --sort-by='.lastTimestamp'
```

### Debug Pod Issues

```bash
# Get into the pod
oc rsh deployment/pco-ai-service

# Run commands in pod
oc exec deployment/pco-ai-service -- python --version

# Check environment variables
oc exec deployment/pco-ai-service -- env | grep -E 'PCO|OLLAMA'
```

### Check Service Connectivity

```bash
# Test PCO API Wrapper connection
oc exec deployment/pco-ai-service -- \
  curl -s http://pco-api-wrapper:5000/health

# Test Ollama connection
oc exec deployment/pco-ai-service -- \
  curl -s http://ollama:11434/api/tags
```

## Resource Management

### Set Resource Limits

Edit `openshift/deployment.yaml`:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "200m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

Apply changes:

```bash
oc apply -f openshift/deployment.yaml
```

### Monitor Resource Usage

```bash
# Get resource usage
oc adm top pods -l app=pco-ai-service

# Get node resource usage
oc adm top nodes
```

## Security

### Create Service Account

```bash
# Create service account
oc create serviceaccount pco-ai-sa

# Update deployment to use it
oc set serviceaccount deployment/pco-ai-service pco-ai-sa
```

### Add Network Policies

Create `network-policy.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pco-ai-service-policy
spec:
  podSelector:
    matchLabels:
      app: pco-ai-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 5001
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: pco-api-wrapper
    ports:
    - protocol: TCP
      port: 5000
  - to:
    - podSelector:
        matchLabels:
          app: ollama
    ports:
    - protocol: TCP
      port: 11434
```

Apply:

```bash
oc apply -f network-policy.yaml
```

## Backup and Recovery

### Backup Configuration

```bash
# Export all resources
oc get all,configmap,secret,route -l app=pco-ai-service -o yaml > pco-ai-backup.yaml

# Backup ConfigMap
oc get configmap pco-ai-config -o yaml > configmap-backup.yaml
```

### Restore from Backup

```bash
# Restore resources
oc apply -f pco-ai-backup.yaml
```

## CI/CD Integration

### Using OpenShift Pipelines (Tekton)

Create a pipeline for automated deployments:

```yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: pco-ai-service-pipeline
spec:
  params:
  - name: git-url
    type: string
  - name: git-revision
    type: string
    default: main
  tasks:
  - name: build
    taskRef:
      name: buildah
    params:
    - name: IMAGE
      value: image-registry.openshift-image-registry.svc:5000/pco-system/pco-ai-service:latest
  - name: deploy
    taskRef:
      name: openshift-client
    params:
    - name: SCRIPT
      value: |
        oc rollout latest deployment/pco-ai-service
        oc rollout status deployment/pco-ai-service
```

## Production Checklist

- [ ] Resource limits configured
- [ ] Health checks configured
- [ ] Monitoring and alerting set up
- [ ] Backup strategy in place
- [ ] Security policies applied
- [ ] Network policies configured
- [ ] SSL/TLS certificates configured
- [ ] Logging configured
- [ ] Auto-scaling configured (if needed)
- [ ] Disaster recovery plan documented

## Common Issues

### Pod CrashLoopBackOff

```bash
# Check logs
oc logs deployment/pco-ai-service --previous

# Common causes:
# - Cannot connect to PCO API Wrapper
# - Cannot connect to Ollama
# - Missing environment variables
```

### Service Unavailable

```bash
# Check if pods are running
oc get pods -l app=pco-ai-service

# Check service endpoints
oc get endpoints pco-ai-service

# Check route
oc get route pco-ai-service
```

### Slow Response Times

```bash
# Check resource usage
oc adm top pods -l app=pco-ai-service

# Scale up if needed
oc scale deployment/pco-ai-service --replicas=3

# Check Ollama performance
oc logs deployment/ollama
```

## Support

For issues:
1. Check logs: `oc logs deployment/pco-ai-service`
2. Check events: `oc get events`
3. Verify connectivity to dependencies
4. Review resource usage

## Next Steps

1. Set up monitoring with Prometheus/Grafana
2. Configure auto-scaling
3. Implement CI/CD pipeline
4. Add authentication/authorization
5. Set up backup automation