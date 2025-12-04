# Troubleshooting 401 Unauthorized Error

## Problem

You're getting a 401 error when calling the API:
```json
{
  "error": "An error occurred: (401, '401 Client Error: Unauthorized for url: https://api.planningcenteronline.com/people/v2/campuses?offset=0&per_page=25')"
}
```

This means the PCO API credentials (PCO_APP_ID and PCO_SECRET) are either:
1. Not set in the OpenShift deployment
2. Set incorrectly
3. Not being loaded by the application

---

## Solution Steps

### Step 1: Verify Secret Exists in OpenShift

```bash
# Check if the secret exists
oc get secret pco-credentials -n pco-api-wrapper

# View the secret (base64 encoded)
oc get secret pco-credentials -n pco-api-wrapper -o yaml
```

### Step 2: Check Secret Content

```bash
# Decode and check the PCO_APP_ID
oc get secret pco-credentials -n pco-api-wrapper -o jsonpath='{.data.PCO_APP_ID}' | base64 -d
echo

# Decode and check the PCO_SECRET
oc get secret pco-credentials -n pco-api-wrapper -o jsonpath='{.data.PCO_SECRET}' | base64 -d
echo
```

**Expected Output:**
- PCO_APP_ID should be a long alphanumeric string
- PCO_SECRET should be a long alphanumeric string
- Both should NOT be empty or contain placeholder text

### Step 3: Verify Deployment Environment Variables

```bash
# Check if environment variables are set in the deployment
oc get deployment pco-api-wrapper -n pco-api-wrapper -o yaml | grep -A 10 "env:"
```

**Expected Output:**
```yaml
env:
- name: PCO_APP_ID
  valueFrom:
    secretKeyRef:
      name: pco-credentials
      key: PCO_APP_ID
- name: PCO_SECRET
  valueFrom:
    secretKeyRef:
      name: pco-credentials
      key: PCO_SECRET
```

### Step 4: Check Pod Environment Variables

```bash
# Get the pod name
POD_NAME=$(oc get pods -n pco-api-wrapper -l app=pco-api-wrapper -o jsonpath='{.items[0].metadata.name}')

# Check environment variables in the running pod
oc exec -n pco-api-wrapper $POD_NAME -- env | grep PCO
```

**Expected Output:**
```
PCO_APP_ID=your_actual_app_id
PCO_SECRET=your_actual_secret
```

If these are empty or show placeholder values, the secret is not configured correctly.

---

## Fix: Update the Secret

### Option 1: Update Existing Secret

1. **Get your PCO credentials from local .env file:**
   ```bash
   cat .env | grep PCO
   ```

2. **Update the secret in OpenShift:**
   ```bash
   # Replace YOUR_APP_ID and YOUR_SECRET with actual values
   oc create secret generic pco-credentials \
     --from-literal=PCO_APP_ID=YOUR_APP_ID \
     --from-literal=PCO_SECRET=YOUR_SECRET \
     --dry-run=client -o yaml | oc apply -f -
   ```

3. **Restart the deployment to pick up new credentials:**
   ```bash
   oc rollout restart deployment/pco-api-wrapper -n pco-api-wrapper
   ```

4. **Wait for the new pod to be ready:**
   ```bash
   oc rollout status deployment/pco-api-wrapper -n pco-api-wrapper
   ```

### Option 2: Create Secret from File

1. **Create a temporary file with your credentials:**
   ```bash
   cat > /tmp/pco-creds.env << EOF
   PCO_APP_ID=your_actual_app_id_here
   PCO_SECRET=your_actual_secret_here
   EOF
   ```

2. **Create the secret from the file:**
   ```bash
   oc create secret generic pco-credentials \
     --from-env-file=/tmp/pco-creds.env \
     -n pco-api-wrapper \
     --dry-run=client -o yaml | oc apply -f -
   ```

3. **Clean up the temporary file:**
   ```bash
   rm /tmp/pco-creds.env
   ```

4. **Restart the deployment:**
   ```bash
   oc rollout restart deployment/pco-api-wrapper -n pco-api-wrapper
   ```

### Option 3: Use the Provided Script

I've created a script to help you update the credentials:

```bash
# Make the script executable
chmod +x update-pco-credentials.sh

# Run the script (it will prompt for credentials)
./update-pco-credentials.sh
```

---

## Verification

After updating the secret and restarting the deployment:

### 1. Check Pod Logs
```bash
# Get the latest pod
POD_NAME=$(oc get pods -n pco-api-wrapper -l app=pco-api-wrapper -o jsonpath='{.items[0].metadata.name}')

# Check logs for any errors
oc logs -n pco-api-wrapper $POD_NAME
```

**Look for:**
- No errors about missing PCO_APP_ID or PCO_SECRET
- Application should start successfully

### 2. Test the Health Endpoint
```bash
curl -k https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. Test a PCO API Call
```bash
curl -k https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people/182133595
```

**Expected Response:**
```json
{
  "id": "182133595",
  "type": "Person",
  "attributes": {
    "first_name": "api",
    "last_name": "test",
    ...
  }
}
```

If you still get a 401 error, the credentials are incorrect.

---

## Common Issues

### Issue 1: Credentials Have Spaces or Special Characters

**Problem:** Credentials copied with extra spaces or line breaks

**Solution:** Ensure credentials are trimmed:
```bash
# Trim spaces when creating secret
PCO_APP_ID=$(cat .env | grep PCO_APP_ID | cut -d '=' -f2 | tr -d ' \n\r')
PCO_SECRET=$(cat .env | grep PCO_SECRET | cut -d '=' -f2 | tr -d ' \n\r')

oc create secret generic pco-credentials \
  --from-literal=PCO_APP_ID=$PCO_APP_ID \
  --from-literal=PCO_SECRET=$PCO_SECRET \
  --dry-run=client -o yaml | oc apply -f -
```

### Issue 2: Secret Not Mounted in Pod

**Problem:** Secret exists but not referenced in deployment

**Solution:** Check deployment.yaml has correct secret reference:
```yaml
env:
- name: PCO_APP_ID
  valueFrom:
    secretKeyRef:
      name: pco-credentials
      key: PCO_APP_ID
- name: PCO_SECRET
  valueFrom:
    secretKeyRef:
      name: pco-credentials
      key: PCO_SECRET
```

### Issue 3: Old Pod Still Running

**Problem:** Deployment not restarted after secret update

**Solution:** Force restart:
```bash
oc delete pod -l app=pco-api-wrapper -n pco-api-wrapper
```

### Issue 4: Wrong PCO Credentials

**Problem:** Credentials are set but are invalid or expired

**Solution:** 
1. Log into Planning Center Online
2. Go to https://api.planningcenteronline.com/oauth/applications
3. Create a new Personal Access Token
4. Update the secret with new credentials

---

## Quick Diagnostic Script

Run this to diagnose the issue:

```bash
#!/bin/bash
echo "=== PCO API Wrapper Diagnostics ==="
echo

echo "1. Checking if secret exists..."
oc get secret pco-credentials -n pco-api-wrapper
echo

echo "2. Checking secret keys..."
oc get secret pco-credentials -n pco-api-wrapper -o jsonpath='{.data}' | jq 'keys'
echo

echo "3. Checking deployment environment variables..."
oc get deployment pco-api-wrapper -n pco-api-wrapper -o yaml | grep -A 15 "env:"
echo

echo "4. Checking pod status..."
oc get pods -n pco-api-wrapper -l app=pco-api-wrapper
echo

echo "5. Checking pod environment variables..."
POD_NAME=$(oc get pods -n pco-api-wrapper -l app=pco-api-wrapper -o jsonpath='{.items[0].metadata.name}')
echo "Pod: $POD_NAME"
oc exec -n pco-api-wrapper $POD_NAME -- env | grep PCO
echo

echo "6. Checking recent pod logs..."
oc logs -n pco-api-wrapper $POD_NAME --tail=20
echo

echo "=== Diagnostics Complete ==="
```

Save this as `diagnose-pco.sh`, make it executable, and run it:
```bash
chmod +x diagnose-pco.sh
./diagnose-pco.sh
```

---

## Summary

The 401 error means your PCO credentials are not properly configured in OpenShift. Follow these steps:

1. ✅ Verify secret exists and has correct values
2. ✅ Update secret with correct credentials from your .env file
3. ✅ Restart the deployment
4. ✅ Test the API endpoints

After fixing the credentials, all API calls should work correctly!