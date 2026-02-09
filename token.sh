#!/usr/bin/env bash
# strava_refresh_token_env_nosjq.sh
# Usage:
#   ./strava_refresh_token_env_nosjq.sh
# Reads CLIENT_ID and CLIENT_SECRET from .env and prints a new refresh token.

ENV_FILE=".env"
REDIRECT_URI="http://localhost"  # Must match what you registered on Strava
SCOPE="read_all,activity:read_all"

# Load .env
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found."
    exit 1
fi

export $(grep -v '^#' "$ENV_FILE" | xargs)

if [ -z "$STRAVA_CLIENT_ID" ] || [ -z "$STRAVA_CLIENT_SECRET" ]; then
    echo "Error: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set in $ENV_FILE"
    exit 1
fi

echo "Open this URL in your browser and approve access:"
echo "https://www.strava.com/oauth/authorize?client_id=${STRAVA_CLIENT_ID}&response_type=code&redirect_uri=${REDIRECT_URI}&approval_prompt=force&scope=${SCOPE}"
echo
read -p "After approving, copy the 'code=' value from the redirect URL in the browser: " CODE

# Exchange code for access/refresh token
RESPONSE=$(curl -s -X POST https://www.strava.com/oauth/token \
    -d client_id="${STRAVA_CLIENT_ID}" \
    -d client_secret="${STRAVA_CLIENT_SECRET}" \
    -d code="${CODE}" \
    -d grant_type=authorization_code)

# Extract and print refresh token using grep/sed
REFRESH_TOKEN=$(echo "$RESPONSE" | grep -o '"refresh_token":"[^"]*"' | sed 's/"refresh_token":"\(.*\)"/\1/')

echo
echo "Copy this refresh token and replace the value in your .env file:"
echo "$REFRESH_TOKEN"
