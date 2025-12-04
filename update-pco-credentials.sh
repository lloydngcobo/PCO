#!/bin/bash
# Script to update PCO credentials in OpenShift

set -e

echo "=========================================="
echo "PCO Credentials Update Script"
echo "=========================================="
echo

# Check if oc is installed
if ! command -v oc &> /dev/null; then
    echo "ERROR: 'oc' command not found. Please install OpenShift CLI."
    exit 1
fi

# Check if logged in to OpenShift
if ! oc whoami &> /dev/null; then
    echo "ERROR: Not logged in to OpenShift. Please run 'oc login' first."
    exit 1
fi

# Set namespace
NAMESPACE="pco-api-wrapper"

echo "Current namespace: $NAMESPACE"
echo

# Option 1: Read from .env file
if [ -f ".env" ]; then
    echo "Found .env file. Would you like to use credentials from .env? (y/n)"
    read -r USE_ENV
    
    if [ "$USE_ENV" = "y" ] || [ "$USE_ENV" = "Y" ]; then
        echo "Reading credentials from .env file..."
        PCO_APP_ID=$(grep PCO_APP_ID .env | cut -d '=' -f2 | tr -d ' \n\r"')
        PCO_SECRET=$(grep PCO_SECRET .env | cut -d '=' -f2 | tr -d ' \n\r"')
        
        if [ -z "$PCO_APP_ID" ] || [ -z "$PCO_SECRET" ]; then
            echo "ERROR: Could not read credentials from .env file"
            exit 1
        fi
        
        echo "✓ Credentials loaded from .env"
    else
        # Manual input
        echo "Please enter your PCO credentials:"
        echo -n "PCO_APP_ID: "
        read -r PCO_APP_ID
        echo -n "PCO_SECRET: "
        read -rs PCO_SECRET
        echo
    fi
else
    # Manual input
    echo "No .env file found. Please enter your PCO credentials:"
    echo -n "PCO_APP_ID: "
    read -r PCO_APP_ID
    echo -n "PCO_SECRET: "
    read -rs PCO_SECRET
    echo
fi

# Validate credentials are not empty
if [ -z "$PCO_APP_ID" ] || [ -z "$PCO_SECRET" ]; then
    echo "ERROR: Credentials cannot be empty"
    exit 1
fi

echo
echo "Credentials loaded. Length check:"
echo "  PCO_APP_ID: ${#PCO_APP_ID} characters"
echo "  PCO_SECRET: ${#PCO_SECRET} characters"
echo

# Confirm before proceeding
echo "Ready to update credentials in OpenShift namespace: $NAMESPACE"
echo "Continue? (y/n)"
read -r CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

echo
echo "Step 1: Creating/updating secret..."

# Create or update the secret
oc create secret generic pco-credentials \
  --from-literal=PCO_APP_ID="$PCO_APP_ID" \
  --from-literal=PCO_SECRET="$PCO_SECRET" \
  -n $NAMESPACE \
  --dry-run=client -o yaml | oc apply -f -

if [ $? -eq 0 ]; then
    echo "✓ Secret updated successfully"
else
    echo "✗ Failed to update secret"
    exit 1
fi

echo
echo "Step 2: Restarting deployment..."

# Restart the deployment
oc rollout restart deployment/pco-api-wrapper -n $NAMESPACE

if [ $? -eq 0 ]; then
    echo "✓ Deployment restart initiated"
else
    echo "✗ Failed to restart deployment"
    exit 1
fi

echo
echo "Step 3: Waiting for rollout to complete..."

# Wait for rollout to complete
oc rollout status deployment/pco-api-wrapper -n $NAMESPACE --timeout=5m

if [ $? -eq 0 ]; then
    echo "✓ Rollout completed successfully"
else
    echo "✗ Rollout failed or timed out"
    exit 1
fi

echo
echo "Step 4: Verifying credentials in pod..."

# Get the new pod name
POD_NAME=$(oc get pods -n $NAMESPACE -l app=pco-api-wrapper -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD_NAME" ]; then
    echo "✗ Could not find pod"
    exit 1
fi

echo "Pod: $POD_NAME"

# Check environment variables
echo "Checking environment variables..."
ENV_CHECK=$(oc exec -n $NAMESPACE $POD_NAME -- env | grep PCO | wc -l)

if [ "$ENV_CHECK" -ge 2 ]; then
    echo "✓ Environment variables are set in pod"
else
    echo "✗ Environment variables not found in pod"
    exit 1
fi

echo
echo "=========================================="
echo "✓ Credentials updated successfully!"
echo "=========================================="
echo
echo "Next steps:"
echo "1. Test the health endpoint:"
echo "   curl -k https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/health"
echo
echo "2. Test a PCO API call:"
echo "   curl -k https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people/182133595"
echo
echo "If you still get 401 errors, verify your PCO credentials are correct at:"
echo "https://api.planningcenteronline.com/oauth/applications"
echo