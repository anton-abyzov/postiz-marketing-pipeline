#!/usr/bin/env bash
# List Postiz integrations (channels) for the authenticated org.
# Requires: a populated cookie jar (run postiz-login.sh first).
# Usage: POSTIZ_BASE_URL=... ./postiz-list-channels.sh
set -euo pipefail

: "${POSTIZ_BASE_URL:?POSTIZ_BASE_URL is required}"
COOKIE_JAR="${POSTIZ_COOKIE_JAR:-/tmp/postiz-cookies.txt}"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

if [[ ! -f "$COOKIE_JAR" ]]; then
  echo "Cookie jar not found at $COOKIE_JAR. Run postiz-login.sh first." >&2
  exit 1
fi

curl -sS -b "$COOKIE_JAR" \
  -H "showorg: true" \
  -H "User-Agent: $UA" \
  "$POSTIZ_BASE_URL/api/integrations/list" \
  | jq '[.[] | {id, name, providerIdentifier, username, disabled}]'
