# Changelog

## 2.4.0 — 2026-06-29

### Added — Rights-safe REAL-STAR pipeline (WC2026 @aabyzov run)

- **CC-photo lane for real players** — the legal answer to "use real footage." `fetch_cc_photos.py` pulls real player photos under free licenses (CC BY / CC BY-SA / PD) from Wikimedia Commons (skip `(cropped)` dupes, prioritize current-tournament titles, UA + ≥1.3s sleep to dodge 429). Attribution mandatory in caption. Right-of-publicity: editorial/nominative use only, never a real player's AI-generated face.
- **Hard copyright rules** — never rip broadcast/social match video (Content ID + Meta Rights Manager auto-match on upload; 3 strikes = channel termination; DOJ "Operation Offsides" seized ~400 domains Jun 2026). Labels-on-top doesn't cleanse it. Duet/Stitch/reshare is NOT monetizable (reshare ≠ license). Legal hierarchy: CC photos → licensed editorial stills (non-match) → own footage → AI b-roll → diagrams.
- **No-repeat-footage rule** — never reuse a b-roll bed across clips; generate unique fresh footage per clip even at higher cost (`gen_beds_v2.py` distinct-scene library).
- **Mixed video+photo+music** — Remotion `FootballPromo` now takes mixed video+photo beds + a `music` prop; intercut CC-photo Ken Burns with AI b-roll for real motion; ducked ElevenLabs Music bed (`POST /v1/music`); VO `eleven_multilingual_v2` for clean RU.
- **Verify-before-bake gate** — 2-source-verify every score/date/record before it enters a frame (caught "Canada home soil"→LA and "Messi 7th WC"→6th/19 goals this run).
- **Spec-driven pipeline** — `build_from_spec.py` + `schedule_specs.py`; trending-scout & spec-polish dynamic workflows.

### Gotchas documented
- Kie result URLs 403 on plain urllib (Cloudflare) → curl + browser UA.
- zsh doesn't word-split unquoted `$var` → explicit args in shell loops.
- Blotato dedup key is `tiktok` not `twitter`; `/v2/accounts` → 401 (use `/v2/schedules`); `/v2/media` re-ingest = new uuid (dedup by account+caption).
- Scheduled posts fire on real wall-clock → long async builds only let same-day swaps catch future slots.

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
