# cURL Testing Guide for PCO API Wrapper

This guide provides curl commands to test all endpoints of the PCO API Wrapper deployed on OpenShift.

## Your Deployment URL
```
https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl
```

## SSL Certificate Issue

Your OpenShift cluster uses a self-signed certificate. For testing, you can bypass SSL verification using the `-k` or `--insecure` flag:

⚠️ **WARNING**: Only use `-k` for testing in development environments. Never use it in production!

---

## Quick Test Commands

### 1. Health Check
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/health
```

### 2. Create a Person (Your Example)
```bash
curl -k -X POST https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Nokwazi",
    "last_name": "Mdoda",
    "email": "Nokwazi.mdoda@example.com"
  }'
```

**Note**: The email field will be ignored by the API as it's not a direct parameter. The person will be created without an email.

### 3. Get the Test User
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people/182133595
```

---

## Complete API Endpoint Tests

### People Endpoints

#### Get All People
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people
```

#### Get People with Filters

**Filter by Status:**
```bash
curl -k -X GET "https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people?status=active"
```

**Filter by Campus:**
```bash
curl -k -X GET "https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people?campus_id=123"
```

#### Get People in Text Format
```bash
curl -k -X GET "https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people?format=text"
```

#### Get Person by ID
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people/182133595
```

#### Create a New Person
```bash
curl -k -X POST https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "gender": "Male",
    "birthdate": "1990-01-15"
  }'
```

**Minimal Data:**
```bash
curl -k -X POST https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith"
  }'
```

#### Update a Person
```bash
curl -k -X PATCH https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people/182133595 \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Male"
  }'
```

**Update Multiple Attributes:**
```bash
curl -k -X PATCH https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people/182133595 \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Female",
    "birthdate": "1995-06-20"
  }'
```

#### Delete a Person
```bash
# Create a test person first, then delete using their ID
curl -k -X DELETE https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people/PERSON_ID
```

---

### Campus Endpoints

#### Get All Campuses
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/campuses
```

---

## Services Module Endpoints

### Service Types

#### Get All Service Types
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types
```

#### Get Service Type by ID
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID
```

---

### Plans

#### Get Plans for a Service Type
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans
```

#### Get Plans with Filters

**Future Plans:**
```bash
curl -k -X GET "https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans?filter=future"
```

**Past Plans:**
```bash
curl -k -X GET "https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans?filter=past"
```

#### Get Specific Plan
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans/PLAN_ID
```

#### Create a Plan
```bash
curl -k -X POST https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sunday Service",
    "dates": "January 15, 2024",
    "series_title": "New Year Series"
  }'
```

#### Update a Plan
```bash
curl -k -X PATCH https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans/PLAN_ID \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Sunday Service"
  }'
```

#### Delete a Plan
```bash
curl -k -X DELETE https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans/PLAN_ID
```

---

### Teams

#### Get Teams for a Service Type
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/teams
```

#### Get Team by ID
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/teams/TEAM_ID
```

#### Get Team Positions
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/teams/TEAM_ID/positions
```

---

### Plan People (Team Members)

#### Get People in a Plan
```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans/PLAN_ID/team-members
```

#### Add Person to Plan
```bash
curl -k -X POST https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans/PLAN_ID/team-members \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "182133595",
    "team_position_id": "POSITION_ID",
    "status": "C"
  }'
```

**Status Codes:**
- `C` = Confirmed
- `U` = Unconfirmed
- `D` = Declined

#### Update Person Status in Plan
```bash
curl -k -X PATCH https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans/PLAN_ID/team-members/TEAM_MEMBER_ID \
  -H "Content-Type: application/json" \
  -d '{
    "status": "C"
  }'
```

#### Remove Person from Plan
```bash
curl -k -X DELETE https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans/PLAN_ID/team-members/TEAM_MEMBER_ID
```

---

### Utility Endpoints

#### Get Upcoming Plans
```bash
curl -k -X GET "https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans/upcoming?days=30"
```

#### Get Past Plans
```bash
curl -k -X GET "https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans/past?days=30"
```

#### Find Plan by Date
```bash
curl -k -X GET "https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types/SERVICE_TYPE_ID/plans/find-by-date?date=2024-01-15"
```

---

## Fixing SSL Certificate Issues (Permanent Solution)

### Option 1: Add Certificate to System Trust Store (Recommended)

1. **Download the OpenShift Router CA Certificate:**
   ```bash
   echo | openssl s_client -showcerts -servername pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl -connect pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl:443 2>/dev/null | openssl x509 -outform PEM > openshift-router-ca.crt
   ```

2. **Add to System Trust Store:**
   
   **On Linux:**
   ```bash
   sudo cp openshift-router-ca.crt /usr/local/share/ca-certificates/
   sudo update-ca-certificates
   ```
   
   **On Windows:**
   - Double-click the `openshift-router-ca.crt` file
   - Click "Install Certificate"
   - Select "Local Machine"
   - Choose "Place all certificates in the following store"
   - Browse and select "Trusted Root Certification Authorities"
   - Click "Finish"

3. **Test without `-k` flag:**
   ```bash
   curl -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/health
   ```

### Option 2: Use Certificate with curl

```bash
curl --cacert openshift-router-ca.crt -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/health
```

---

## Testing Workflow Example

Here's a complete workflow to test the API:

```bash
# 1. Check health
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/health

# 2. Get all people
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people

# 3. Get the test user
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people/182133595

# 4. Create a new person
curl -k -X POST https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "gender": "Male"
  }'

# 5. Update the test user
curl -k -X PATCH https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people/182133595 \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Female"
  }'

# 6. Get service types
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types

# 7. Get campuses
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/campuses
```

---

## Pretty Print JSON Responses

To make the JSON responses more readable, pipe them through `jq`:

```bash
curl -k -X GET https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/people/182133595 | jq '.'
```

If you don't have `jq` installed:
- **Linux**: `sudo apt-get install jq` or `sudo yum install jq`
- **macOS**: `brew install jq`
- **Windows**: Download from https://stedolan.github.io/jq/download/

---

## Troubleshooting

### Error: "Connection refused"
- Check if the application is running
- Verify the URL is correct
- Check OpenShift route status: `oc get route`

### Error: "SSL certificate problem"
- Use `-k` flag for testing
- Or follow the permanent solution above

### Error: "404 Not Found"
- Verify the endpoint path is correct
- Check if the route is properly configured

### Error: "500 Internal Server Error"
- Check application logs: `oc logs deployment/pco-api-wrapper`
- Verify PCO credentials are set correctly in the secret

---

## Summary

**Quick Command Template:**
```bash
curl -k -X [METHOD] https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/[ENDPOINT] \
  -H "Content-Type: application/json" \
  -d '[JSON_DATA]'
```

**Your Test User:**
- ID: `182133595`
- Name: `api test`
- Use this ID for testing GET, PATCH, and DELETE operations

**Remember:** Always use `-k` flag when testing with self-signed certificates!