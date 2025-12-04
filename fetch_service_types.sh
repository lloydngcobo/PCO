#!/bin/bash
# Script to fetch and display service types from OpenShift deployment

echo "=========================================="
echo "Fetching Service Types from OpenShift"
echo "=========================================="
echo

URL="https://pco-api-wrapper-pco-api-wrapper.apps.homelab.home.nl/api/services/service-types"

echo "URL: $URL"
echo

# Fetch service types
echo "Fetching service types..."
echo

RESPONSE=$(curl -k -s "$URL")

# Check if curl was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to connect to the API"
    exit 1
fi

# Check if response contains error
if echo "$RESPONSE" | grep -q '"error"'; then
    echo "ERROR: API returned an error"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo
    echo "This is likely a 401 Unauthorized error."
    echo "Please run: ./update-pco-credentials.sh"
    exit 1
fi

# Pretty print the response
echo "Service Types:"
echo "=========================================="
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo
echo "=========================================="

# Count service types
COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', [])))" 2>/dev/null)

if [ -n "$COUNT" ]; then
    echo "Total Service Types: $COUNT"
else
    echo "Could not parse response"
fi

echo