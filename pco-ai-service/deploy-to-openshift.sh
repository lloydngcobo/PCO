#!/bin/bash
# Deploy PCO AI Service to OpenShift
# Run this script from your jump server

set -e  # Exit on error

echo "🚀 Deploying PCO AI Service to OpenShift"
echo "=========================================="

# Configuration
PROJECT_NAME="pco-system"
APP_NAME="pco-ai-service"
IMAGE_NAME="pco-ai-service"

# Step 1: Login to OpenShift (if not already logged in)
echo ""
echo "📝 Step 1: Checking OpenShift login..."
if ! oc whoami &> /dev/null; then
    echo "❌ Not logged in to OpenShift. Please login first:"
    echo "   oc login --server=https://your-cluster:6443"
    exit 1
fi
echo "✅ Logged in as: $(oc whoami)"

# Step 2: Switch to project
echo ""
echo "📝 Step 2: Switching to project ${PROJECT_NAME}..."
if ! oc project ${PROJECT_NAME} &> /dev/null; then
    echo "⚠️  Project ${PROJECT_NAME} doesn't exist. Creating it..."
    oc new-project ${PROJECT_NAME}
fi
echo "✅ Using project: ${PROJECT_NAME}"

# Step 3: Create ImageStream first
echo ""
echo "📝 Step 3: Creating ImageStream..."
if ! oc get imagestream/${APP_NAME} &> /dev/null; then
    oc create imagestream ${APP_NAME}
    echo "✅ ImageStream created"
else
    echo "✅ ImageStream already exists"
fi

# Step 4: Build the image in OpenShift
echo ""
echo "📝 Step 4: Building container image..."
echo "   This will take a few minutes..."

# Check if BuildConfig exists
if oc get bc/${APP_NAME} &> /dev/null; then
    echo "   BuildConfig exists, starting new build..."
    oc start-build ${APP_NAME} --from-dir=. --follow
else
    echo "   Creating new BuildConfig..."
    oc new-build --name=${APP_NAME} \
        --binary \
        --strategy=docker \
        --to=${APP_NAME}:latest
    echo "   Starting build..."
    oc start-build ${APP_NAME} --from-dir=. --follow
fi

echo "✅ Image built successfully"

# Step 4: Update ConfigMap
echo ""
echo "📝 Step 4: Updating ConfigMap..."
oc apply -f openshift/configmap.yaml
echo "✅ ConfigMap updated"

# Step 5: Deploy the application
echo ""
echo "📝 Step 5: Deploying application..."

# Check if deployment exists
if oc get deployment/${APP_NAME} &> /dev/null; then
    echo "   Deployment exists, updating..."
    oc apply -f openshift/deployment.yaml
    oc rollout restart deployment/${APP_NAME}
else
    echo "   Creating new deployment..."
    oc apply -f openshift/deployment.yaml
fi

# Apply service and route
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml

echo "✅ Application deployed"

# Step 6: Wait for deployment
echo ""
echo "📝 Step 6: Waiting for deployment to be ready..."
oc rollout status deployment/${APP_NAME} --timeout=5m
echo "✅ Deployment ready"

# Step 7: Get the route
echo ""
echo "📝 Step 7: Getting application URL..."
ROUTE_URL=$(oc get route ${APP_NAME} -o jsonpath='{.spec.host}')
echo "✅ Application URL: https://${ROUTE_URL}"

# Step 8: Test the deployment
echo ""
echo "📝 Step 8: Testing deployment..."
sleep 5  # Wait a bit for the app to be fully ready
if curl -k -s https://${ROUTE_URL}/health | grep -q "healthy"; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed. Check logs with: oc logs deployment/${APP_NAME}"
fi

# Summary
echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo "Application URL: https://${ROUTE_URL}"
echo ""
echo "Useful commands:"
echo "  View logs:    oc logs -f deployment/${APP_NAME}"
echo "  Get pods:     oc get pods -l app=${APP_NAME}"
echo "  Describe:     oc describe deployment/${APP_NAME}"
echo "  Delete:       oc delete all -l app=${APP_NAME}"
echo ""
echo "Test the service:"
echo "  curl -k https://${ROUTE_URL}/health"
echo ""