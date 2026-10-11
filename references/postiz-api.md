# Postiz internal API (cookie auth)

Self-hosted build at `$POSTIZ_BASE_URL` (`https://postiz.easychamp.com`). This is the cookie-auth API the web UI uses. The API-key public API (`/api/public/v1/...`) and the `postiz` CLI are covered in `social-media-posting`.

Every call below needs these headers. The examples abbreviate them as `$H`:

```bash
H=(-b /tmp/postiz-cookies.txt -H "showorg: true" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
```

## Auth

```bash
curl -sS -c /tmp/postiz-cookies.txt -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" \
  -X POST "$POSTIZ_BASE_URL/api/auth/login" \
  -d "{\"email\":\"$POSTIZ_EMAIL\",\"password\":\"$POSTIZ_PASSWORD\",\"provider\":\"LOCAL\"}"
```

A 201 response sets the JWT as the `auth` cookie, valid about a month. The June 2026 build wants `provider`; older notes and builds used `providerName`. `scripts/postiz-login.sh` wraps this call.

## Channels

`GET /api/integrations/list` returns `[{id, name, providerIdentifier, username, picture, disabled}]`. Without `showorg`, it returns `[]`. Discord channel IDs come from `POST /api/integrations/function` with `{"id":"<discord integration id>","name":"channels","data":{}}`.

## Media upload

`POST /api/media/upload-simple` (multipart, `-F file=@video.mp4`) returns `{id, name, path, originalName}`. Keep `id` and `path`; posts need both.

## Create or schedule

`POST /api/posts`:

```json
{
  "type": "schedule",
  "date": "2026-05-09T15:30:00.000Z",
  "shortLink": false,
  "tags": [],
  "posts": [{
    "integration": {"id": "<integration id>"},
    "value": [{"content": "Caption", "image": [{"id": "<media id>", "path": "<cdn url>", "name": "<hash>.mp4", "originalName": "video.mp4", "thumbnailTimestamp": 4200}]}],
    "group": "<uuid v4; one per independent post, shared to bundle posts>",
    "settings": {}
  }]
}
```

`type: "now"` publishes immediately. The settings table per platform is in SKILL.md.

## Update in place (no PUT)

Post the same body again with `value[0].id` = the existing post ID, the existing `group`, the existing `date` and `settings`, plus the new content or `image`. The response is `[{postId, integration}]` with the same ID. Use `GET /api/posts/{id}` to get the group first. `scripts/postiz-swap-media.py --post-ids a,b --media-id ... --media-path ... --media-name ... --original-name ...` does this in bulk.

## Delete

`DELETE /api/posts/{group_uuid}` (by group, not post ID). The body always says `{"error":true}`, even on success. Confirm with `GET /api/posts/{post_id}`: a 500 means the post is gone. QUEUE and DRAFT posts can be deleted; PUBLISHED ones have to be removed on the platform itself.

## Read back

- `GET /api/posts/{id}` returns `{group, posts:[{state, releaseURL, publishDate, ...}]}`. This is the reliable check. `state: "PUBLISHED"` plus `releaseURL` is the live link.
- `GET /api/posts?startDate=...&endDate=...` lists a window (its query params are finicky).
- States: `QUEUE`, `PUBLISHED`, `ERROR` (cron retries after you fix the cause), `DRAFT`.

## Files over ~100MB

The Cloudflare Tunnel returns an HTML `413 Payload Too Large`. Proven 2026-06-10 with a 372MB YouTube upload, published within 2 minutes:

1. `scp` the file to the Postiz host. The host and SSH key are in vault note `Postiz on Hetzner`.
2. From the host: `curl -X POST http://localhost:4242/api/media/upload-simple -H "Cookie: auth=$AUTH" -H 'showorg: true' -H 'User-Agent: Mozilla/5.0' -F 'file=@/tmp/video.mp4;type=video/mp4'`. `$AUTH` is the normal `auth` cookie. Port 4242 is `postiz-proxy` and mirrors the public `/api/` paths; 3000 is the raw backend.
3. Create the post from anywhere, since the JSON is small. YouTube settings: `{title, type:"public", thumbnail:{id,path,name}}`. Upload the thumbnail through the public endpoint.

## Errors

| Symptom | Fix |
|---|---|
| 403, Cloudflare error 1010 | Add a Mozilla User-Agent |
| `[]` from list endpoints | Add `showorg: true` |
| `post_type=reel` validation error | Use `post_type: "post"`; video becomes a Reel anyway |
| `image.0.id must be a string` | Send `{id, path}`, not just `path` |
| Discord `channel required` | `settings.channel` = numeric channel ID |
| Discord publish fails on size | Re-encode under 25 MB (`scripts/discord-encode.sh`) |
| `PUT /api/posts/{id}` 404 | Use update in place |
| `DELETE /api/posts/{post_id}` 404 | Delete by group UUID |
| 413 HTML page on upload | Use the SSH route above |
| Login 400 | Use `provider`, not `providerName` (or the other way round on older builds) |
