#!/bin/bash

# Load the API key from file
API_KEY=$(cat private-api-key.txt)

# Test endpoint - create a simple campaign with minimal structure
echo "Creating a test campaign..."

# Create a timestamp for tomorrow
TOMORROW=$(date -v+1d -u +"%Y-%m-%dT%H:%M:%SZ")

# Attempt approach #1 - Simplified payload
curl -s -X POST "https://a.klaviyo.com/api/campaigns/" \
  -H "accept: application/json" \
  -H "revision: 2025-04-15" \
  -H "content-type: application/json" \
  -H "Authorization: Klaviyo-API-Key $API_KEY" \
  -d '{
    "data": {
      "type": "campaign",
      "attributes": {
        "name": "CURL_TEST_1",
        "send_strategy": {
          "method": "static"
        }
      }
    }
  }' | python -m json.tool

echo -e "\n\n"
echo "Waiting 2 seconds before next attempt..."
sleep 2

# Attempt approach #2 - With send_time in options_static
echo "Attempt #2 - With send_time in options_static"
curl -s -X POST "https://a.klaviyo.com/api/campaigns/" \
  -H "accept: application/json" \
  -H "revision: 2025-04-15" \
  -H "content-type: application/json" \
  -H "Authorization: Klaviyo-API-Key $API_KEY" \
  -d "{
    \"data\": {
      \"type\": \"campaign\",
      \"attributes\": {
        \"name\": \"CURL_TEST_2\",
        \"send_strategy\": {
          \"method\": \"static\",
          \"options_static\": {
            \"send_time\": \"$TOMORROW\"
          }
        }
      }
    }
  }" | python -m json.tool

echo -e "\n\n"
echo "Waiting 2 seconds before next attempt..."
sleep 2

# Attempt approach #3 - With campaign-message info but no audience
echo "Attempt #3 - With campaign message but no audience"
curl -s -X POST "https://a.klaviyo.com/api/campaigns/" \
  -H "accept: application/json" \
  -H "revision: 2025-04-15" \
  -H "content-type: application/json" \
  -H "Authorization: Klaviyo-API-Key $API_KEY" \
  -d "{
    \"data\": {
      \"type\": \"campaign\",
      \"attributes\": {
        \"name\": \"CURL_TEST_3\",
        \"send_strategy\": {
          \"method\": \"static\",
          \"options_static\": {
            \"send_time\": \"$TOMORROW\"
          }
        },
        \"campaign-messages\": {
          \"data\": [
            {
              \"type\": \"campaign-message\",
              \"attributes\": {
                \"channel\": \"email\",
                \"label\": \"Test Message\",
                \"content\": {
                  \"subject\": \"[TEST] CURL Test\",
                  \"preview_text\": \"Test campaign\",
                  \"from_email\": \"clara@clarathecoach.com\",
                  \"from_label\": \"CTC\"
                }
              }
            }
          ]
        }
      }
    }
  }" | python -m json.tool
