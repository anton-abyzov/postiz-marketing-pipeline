# Changelog

## 2.3.0 — 2026-05-15

### BREAKING: X/Twitter routing changed

Anton's self-hosted Postiz instance had the X integration removed on 2026-05-15. **All X/Twitter posts MUST now route through Blotato API** (`POST /v2/posts` with `targetType: "twitter"`). The `Anton X/Twitter (@aabyzov) — connected directly` line in Social Channel Inventory was wrong post-removal.

### Added
- **Platform routing matrix** — single decision table for every platform → service (Postiz vs Blotato vs not-connected). One-liner rule: `if platform in {tiktok, x/twitter}: use Blotato; else: use Postiz`.
- **Postiz schema gotchas section** — full payload structure documented after this run's debug cycle:
  - `tags: []` MUST be at top level (not inside `posts[]`)
  - `image[0]` MUST be `{id: <upload_id>, path: <url>}` — both fields required
  - X integration removed → routing falls back to Blotato
  - Per-platform `settings` requirements:
    - Instagram → `{post_type: "post"|"story"}`
    - Discord → `{channel: "#channel-name"}`
    - YouTube → `{title, type: "public"|"private"|"unlisted", tags: [{label, value}]}`
    - LinkedIn / Facebook / Threads / Telegram → `{}` (empty OK)
- **Updated TikTok routing** — Blotato is now the primary, not the `tiktokpost` browser-skill (which is legacy fallback).
- **Updated Social Channel Inventory** — split into "Connected via Postiz" vs "Routes via Blotato" vs "NOT connected"; called out Anton personal Facebook as missing.

### Removed
- `Anton X/Twitter (@aabyzov) — connected directly, NOT via Blotato` (no longer true)
- `TikTok — use 'tiktokpost' skill for browser-driven posting` as the primary routing (Blotato is)

