# Postiz API — Field Notes

Distilled from a real launch run on a self-hosted Postiz instance (~v0.x, late-2025 build). Endpoints are stable; payload shapes have minor seasonal drift.

## Auth

`POST /api/auth/login` with JSON body:

```json
{
  "email": "you@example.com",
  "password": "redacted",
  "providerName": "LOCAL"
}
```

Response: HTTP 201, JWT delivered as a Set-Cookie named `auth`. Capture to a cookie jar — it expires in roughly 1 month so you can reuse for the duration of a campaign.

```bash
curl -sS -c /tmp/postiz-cookies.txt -X POST \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0" \
  "https://postiz.example.com/api/auth/login" \
  -d "{\"email\":\"$POSTIZ_EMAIL\",\"password\":\"$POSTIZ_PASSWORD\",\"providerName\":\"LOCAL\"}"
```

GitHub provider works too (`providerName: "GITHUB"`), but the OAuth callback dance is annoying for headless flows.

## The two REQUIRED headers

Every subsequent request needs:

| Header | Value | Why |
|---|---|---|
| `Cookie` | `auth=<jwt>` (auto with `-b cookiejar`) | Authenticates the user |
| `showorg` | `true` | **Org-scoped endpoints return empty arrays without this.** Posts, integrations, media — all of them. This is the single most non-obvious part of the API. |
| `User-Agent` | Any Mozilla-flavored UA | Cloudflare WAF blocks the default `curl/7.x` UA with HTTP 403 + error code 1010. The API behind CF is fine — you're getting blocked at the edge. |

Without `showorg`, channel listings come back as `[]` and look like the user has no integrations connected. Without `User-Agent`, you get a Cloudflare-branded HTML error page.

## Channel discovery

```bash
curl -sS -b cookies.txt \
  -H "showorg: true" \
  -H "User-Agent: Mozilla/5.0" \
  "https://postiz.example.com/api/integrations/list"
```

Returns an array of integrations, each with:

```json
{
  "id": "<integration uuid>",
  "name": "<channel display name>",
  "providerIdentifier": "youtube|x|instagram|threads|telegram|discord|linkedin|facebook|...",
  "username": "<handle>",
  "picture": "<avatar url>",
  "disabled": false
}
```

For Discord specifically, you need the channel id within the guild. Get it with:

```bash
curl -sS -b cookies.txt \
  -H "showorg: true" \
  -H "User-Agent: Mozilla/5.0" \
  -H "Content-Type: application/json" \
  -X POST "https://postiz.example.com/api/integrations/function" \
  -d '{"id":"<discord integration id>","name":"channels","data":{}}'
```

Returns the guild's channels. Pick the channel id and pass it in the post `settings.channel`.

## Media upload

`POST /api/media/upload-simple` with multipart form:

```bash
curl -sS -b cookies.txt \
  -H "showorg: true" \
  -H "User-Agent: Mozilla/5.0" \
  -F "file=@video.mp4" \
  "https://postiz.example.com/api/media/upload-simple"
```

Response:

```json
{
  "id": "<media uuid>",
  "name": "<random hash>.mp4",
  "path": "https://postiz.example.com/uploads/2026/05/09/<hash>.mp4",
  "originalName": "video.mp4"
}
```

Save the `id` and `path` — both are needed in the post payload.

## Schedule a post

`POST /api/posts` with JSON body. `type: "schedule"` queues for the given `date`; `type: "now"` publishes immediately.

```json
{
  "type": "schedule",
  "date": "2026-05-09T15:30:00.000Z",
  "posts": [
    {
      "integration": { "id": "<integration uuid>" },
      "value": [
        {
          "content": "Caption with line breaks and emoji.",
          "image": [
            {
              "id": "<media uuid>",
              "path": "https://.../uploads/.../<hash>.mp4",
              "name": "<hash>.mp4",
              "originalName": "video.mp4"
            }
          ]
        }
      ],
      "group": "<any uuid v4 you generate>",
      "settings": {}
    }
  ],
  "shortLink": false,
  "tags": []
}
```

`group` is a client-generated UUID that ties multiple posts together as a single "campaign group" in the UI. Generate one per post for independent posts, or share one across N posts to bundle them.

`settings` varies by provider:

| Provider | Required `settings` keys |
|---|---|
| `youtube` | `{ "title": "...", "type": "public", "category": "22" }` (22 = People & Blogs) |
| `discord` | `{ "channel": "<discord channel id>" }` |
| `linkedin` | `{ "post_as": "user" }` (user vs page) |
| `instagram-standalone` | `{ "post_type": "post" }` (NOT "reel" — even for video, Postiz/Meta auto-renders as Reel) |
| `instagram` (full) | Same — `post_type: "post"` |
| `x` | `{}` |
| `threads` | `{}` |
| `telegram` | `{}` |
| `facebook` | `{}` |

The `instagram*` `post_type=reel` rejection is undocumented — it returns a generic validation error. Always use `post`.

## In-place update — the secret pattern

`PUT /api/posts/{id}` returns 404. There is no PUT.

The actual update path: `POST /api/posts` again, but include the existing `id` inside `value[0].id` AND include the existing `group` UUID:

```json
{
  "type": "schedule",
  "date": "<existing publishDate>",
  "posts": [{
    "integration": { "id": "<existing integration id>" },
    "value": [{
      "id": "<EXISTING POST ID>",
      "content": "<existing or new caption>",
      "image": [{ /* new media here for swap */ }]
    }],
    "group": "<EXISTING GROUP UUID>",
    "settings": { /* existing settings */ }
  }],
  "shortLink": false,
  "tags": []
}
```

Postiz treats this as update-in-place: same post id, same group, schedule preserved. Response is `[{ "postId": "<same id>", "integration": "<same id>" }]`.

To find the existing post's group UUID, fetch it first: `GET /api/posts/{post_id}`.

## Delete a post

`DELETE /api/posts/{group_uuid}` — note: by **group UUID**, not post ID. Postiz routes deletion by group.

```bash
curl -sS -b cookies.txt \
  -H "showorg: true" \
  -H "User-Agent: Mozilla/5.0" \
  -X DELETE "https://postiz.example.com/api/posts/<group_uuid>"
```

The response body is `{"error":true}` — **this is misleading**. The deletion succeeded. Verify with `GET /api/posts/<post_id>` — you'll get HTTP 500 if the post no longer exists.

## Post states

A post moves through these states in Postiz:

| State | Meaning |
|---|---|
| `QUEUE` | Scheduled and waiting for its publish window |
| `PUBLISHED` | Successfully published to the destination |
| `ERROR` | Failed during publish (the orchestrator hit an error — token expired, file too large, provider rate-limit, etc.) |
| `DRAFT` | Saved but not scheduled |

When a post is `ERROR`, you can fix the root cause (e.g. swap a smaller media file) and Postiz's cron will retry on the next tick. If the underlying reason persists (expired OAuth token, persistent provider issue), it'll go back to `ERROR` immediately.

## Common errors

| Symptom | Cause | Fix |
|---|---|---|
| HTTP 403, Cloudflare error 1010 page | Default `curl` UA blocked by CF WAF | Add `User-Agent: Mozilla/5.0 ...` |
| `[]` empty response from `/api/integrations/list` | Missing `showorg: true` header | Add the header |
| `post_type=reel` validation error | Postiz/Meta restriction | Use `post_type=post` — video auto-renders as Reel server-side |
| `channel required, got null` for Discord | Missing `settings.channel` | Use `/api/integrations/function` with `name: channels` to list, then pick |
| Discord publish error, message mentions size | File >25 MB and no Nitro | Re-encode for Discord with `-b:v 3500k` (see `discord-encode.sh`) |
| X publish `bad_body, nonRetryable` | Provider-level X media upload bug, often after token refresh | Re-authorize the X integration in the Postiz UI |
| `PUT /api/posts/{id}` returns 404 | Endpoint doesn't exist | Use `POST /api/posts` with id-in-value (see "In-place update") |
| `DELETE /api/posts/{post_id}` returns 404 | Wrong path | Use `DELETE /api/posts/{group_uuid}` |

## Verify a queued post

After scheduling, confirm in the calendar:

```bash
curl -sS -b cookies.txt \
  -H "showorg: true" \
  -H "User-Agent: Mozilla/5.0" \
  "https://postiz.example.com/api/posts?startDate=2026-05-09T00:00:00.000Z&endDate=2026-05-15T00:00:00.000Z"
```

Returns posts in the date window. Check `state: "QUEUE"` and verify `image[0].originalName` matches your upload.

## The `/api/posts` GET shape

```json
[{
  "id": "cmoxb...",
  "publishDate": "2026-05-09T15:30:00.000Z",
  "state": "QUEUE",
  "image": [{ "id": "...", "originalName": "video.mp4" }],
  "content": "...",
  "group": "<group uuid>",
  "integration": { "id": "...", "providerIdentifier": "youtube", "name": "..." }
}]
```

Use `id` for fetching/swapping, `group` for deletion.
