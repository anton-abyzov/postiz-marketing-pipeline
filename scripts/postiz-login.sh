#!/usr/bin/env bash
# Login to Postiz and capture JWT cookie to a jar.
# Usage: POSTIZ_BASE_URL=... POSTIZ_EMAIL=... POSTIZ_PASSWORD=... ./postiz-login.sh
# Output: writes cookie jar to $POSTIZ_COOKIE_JAR (default /tmp/postiz-cookies.txt)
set -euo pipefail

: "${POSTIZ_BASE_URL:?POSTIZ_BASE_URL is required}"
: "${POSTIZ_EMAIL:?POSTIZ_EMAIL is required}"
: "${POSTIZ_PASSWORD:?POSTIZ_PASSWORD is required}"
COOKIE_JAR="${POSTIZ_COOKIE_JAR:-/tmp/postiz-cookies.txt}"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

http_status=$(curl -sS -o /dev/null -w "%{http_code}" \
  -c "$COOKIE_JAR" \
  -H "User-Agent: $UA" \
  -H "Content-Type: application/json" \
  -X POST "$POSTIZ_BASE_URL/api/auth/login" \
  -d "{\"email\":\"$POSTIZ_EMAIL\",\"password\":\"$POSTIZ_PASSWORD\",\"providerName\":\"LOCAL\"}")

if [[ "$http_status" != "201" && "$http_status" != "200" ]]; then
  echo "Login failed: HTTP $http_status" >&2
  exit 1
fi

if ! grep -q "auth" "$COOKIE_JAR"; then
  echo "Login returned $http_status but no auth cookie was set" >&2
  exit 1
fi

echo "Logged in. Cookie jar: $COOKIE_JAR"
