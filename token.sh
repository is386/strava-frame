#!/usr/bin/env bash
# Usage:
#   ./token.sh
# Reads CLIENT_ID and CLIENT_SECRET from config.toml and prints a new refresh token.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.toml"
REDIRECT_URI="http://localhost"  # Must match what you registered on Strava
SCOPE="read_all,activity:read_all"

# Load values from config.toml using Python
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: config.toml not found at $CONFIG_FILE"
    exit 1
fi

read -r STRAVA_CLIENT_ID STRAVA_CLIENT_SECRET <<< $(python3 - <<EOF
import tomllib
with open("$CONFIG_FILE", "rb") as f:
    config = tomllib.load(f)
print(config["strava"]["client_id"], config["strava"]["client_secret"])
EOF
)

if [ -z "$STRAVA_CLIENT_ID" ] || [ -z "$STRAVA_CLIENT_SECRET" ]; then
    echo "Error: client_id and client_secret must be set in config.toml"
    exit 1
fi

echo "Open this URL in your browser and approve access:"
echo "https://www.strava.com/oauth/authorize?client_id=${STRAVA_CLIENT_ID}&response_type=code&redirect_uri=${REDIRECT_URI}&approval_prompt=force&scope=${SCOPE}"
echo
read -p "After approving, copy the 'code=' value from the redirect URL in the browser and paste it here: " CODE

# Exchange code for access/refresh token
RESPONSE=$(curl -s -X POST https://www.strava.com/oauth/token \
    -d client_id="${STRAVA_CLIENT_ID}" \
    -d client_secret="${STRAVA_CLIENT_SECRET}" \
    -d code="${CODE}" \
    -d grant_type=authorization_code)

# Extract and print refresh token using grep/sed
REFRESH_TOKEN=$(echo "$RESPONSE" | grep -o '"refresh_token":"[^"]*"' | sed 's/"refresh_token":"\(.*\)"/\1/')

echo
echo "Copy this refresh token and replace the value in your config.toml file:"
echo "$REFRESH_TOKEN"