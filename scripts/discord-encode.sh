#!/usr/bin/env bash
# Re-encode a vertical 1080x1920 video to under 25 MB for Discord (non-Nitro upload limit).
# Tested for 30-60s clips. For >60s, lower -b:v to 2500k.
# Usage: ./discord-encode.sh source.mp4 [output.mp4]
set -euo pipefail

SRC="${1:?source mp4 path required}"
OUT="${2:-${SRC%.*}-discord.mp4}"

if [[ ! -f "$SRC" ]]; then
  echo "Source file not found: $SRC" >&2
  exit 1
fi

ffmpeg -y -i "$SRC" \
  -c:v libx264 -preset slow -b:v 3500k \
  -c:a aac -b:a 128k \
  "$OUT"

size_mb=$(du -m "$OUT" | cut -f1)
echo "Encoded: $OUT (${size_mb} MB)"
if (( size_mb >= 25 )); then
  echo "WARNING: still ${size_mb} MB, exceeds Discord 25 MB non-Nitro limit. Lower -b:v and re-run." >&2
  exit 1
fi
