# Anti-Patterns — What Cost Us Time and Trust

Real failures from a real launch run. Each is a rule paid for in dollars or hours.

## 1. The fabricated tournament fact

### What happened
We rendered a v6 launch video that opened with "Argentina opens the World Cup at AT&T Stadium · June 11." Three claims, all wrong:
- Argentina did NOT open the tournament. **Mexico vs South Africa** opened it on June 11 at Estadio Azteca.
- AT&T Stadium did NOT host the opener. The opener was at Estadio Azteca in Mexico City.
- Argentina's first match was June 16 (not June 11), at Arrowhead Stadium in Kansas City (not AT&T).

Source of error: an LLM, asked to write copy for the video, produced these "facts" with no citations. We trusted them. Six creative variants got authored on top of those copy points before researcher A's verified-fact dump landed.

### Cost
- 5 of the 6 affected variants needed re-rendering or had their copy patched (V3, V5, V7, V8, V9).
- ~30 wall-minutes lost rendering, plus the morale hit of "we almost shipped this."
- One lesson burned: never trust LLM-claimed dates for marketing copy.

### Rule
**Cross-check tournament/release/event dates with at least 2 independent primary sources before they bake into a video.**

For our domain (World Cup 2026), the canonical sources are:
- FIFA — `fifa.com/en/tournaments/...`
- Wikipedia — `en.wikipedia.org/wiki/2026_FIFA_World_Cup`
- Major sports outlets — Al Jazeera, FOX Sports, MLSSoccer, ESPN
- Venue official pages — `metlifestadium.com`, `gehafieldatarrowhead.com`, etc.

For other domains, identify the primary 2–3 sources before any copy gets written. Make researcher pull facts FIRST, then writer second.

### How researcher should output

A facts dump with explicit verdict tags per claim:

```
| Field | Value | Verdict |
|---|---|---|
| Opening match date | June 11, 2026 | ✅ VERIFIED (FIFA + Wikipedia + AlJazeera + FOXSports) |
| Opening match teams | Mexico vs South Africa | ✅ VERIFIED |
| Opening venue | Estadio Azteca | ✅ VERIFIED |
| Final venue | MetLife Stadium | ✅ VERIFIED |
| ARG Match 1 kickoff time | 8 PM CT or 9 PM ET | ⚠ MINOR DRIFT (sources split) |
```

`✅ VERIFIED` requires ≥2 independent sources. `⚠ UNVERIFIED` if only 1 source. `❗ DISPUTED` if sources contradict.

Anything not VERIFIED does not enter the script.

## 2. Cross-post brand pollution

### What happened
Posted brand A's launch video to brand B's YouTube channel. Brand B was a sibling product not yet doing its own marketing. After scheduling, we realized the post would train brand B's algorithm with content unrelated to its own niche — risking that brand B's organic reach would skew wrong when it eventually launched.

### Cost
- Caught before it published, but it was already in QUEUE and the swap-or-delete logic had to handle it specially.
- API used: `DELETE /api/posts/{group_uuid}` (NOT the post ID — Postiz deletes by group). Response body `{"error":true}` was misleading; the deletion actually succeeded.

### Rule
**Don't post brand A content to brand B's channel until brand B has launched its own marketing.**

Specifically:
- Personal channels are a free-for-all (the founder's life is naturally heterogeneous).
- Brand A → brand A channels: yes.
- Brand A → brand B channels (when brand B is dormant): no.
- Brand A → brand B channels (when brand B is actively marketing): only with cross-promo agreement, framed as "we love what these folks are building."

### Indicator
If the channel hasn't posted in 30+ days, treat it as dormant. Don't seed it with someone else's content.

## 3. Right of Publicity / celebrity likenesses

### What happened
Considered using a real soccer player's face on the demo's "user" character. We didn't ship it, but we caught ourselves mid-prompt to KIE AI.

### Why this is a real problem
- **State Right of Publicity** (US) — 35+ states, varying. Even AI-generated likenesses count if recognizable. Damages can be statutory ($1k–$50k per violation in some states) plus disgorgement of profits.
- **Article 8 ECHR** (EU) — right to private life extends to image. GDPR Article 9 treats biometric data as special category.
- **NIL (Name, Image, Likeness) regimes** — for athletes specifically, NIL contracts mean using their likeness without authorization is a clear contract-tortious-interference path.
- **Platform terms** — TikTok, Instagram, YouTube all explicitly ban unauthorized likenesses in ads. Detection has gotten very good with face-recognition models.

### Rule
**No real player faces, no team kits if implying current-roster representation, no announcer voices.** Use generic personas (`Marcus, fan from Brooklyn`) with neutral kit colors that aren't a real team's primary palette. For voiceover, use ElevenLabs synthetic voices, not voice clones of real people.

### Safe pattern
- Persona: fictional, generic name, generic demographic, generic outfit
- Voice: ElevenLabs Sarah (`EXAVITQu4vr4xnSDxMaL`) or Adam — neither is trained on a recognizable real person
- Stadium shots: generic angles, no logos, no recognizable players
- Crowd shots: from far enough that no individual is recognizable

## 4. Discord 25 MB upload limit

### What happened
v8 video was 33 MB at 1080×1920, 45 seconds. Scheduled to Discord. Failed at publish time with a Discord-side error (cryptically reported as a generic publish failure in Postiz).

### Cost
- One round-trip to discover Discord's non-Nitro upload limit is 25 MB (Nitro raises to 100 MB).
- Re-encode + media swap to fix.

### Rule
**For Discord posts, always re-encode to <25 MB before scheduling.**

Recipe (1080×1920, 45s):
```bash
ffmpeg -y -i source.mp4 \
  -c:v libx264 -preset slow -b:v 3500k \
  -c:a aac -b:a 128k \
  source-discord.mp4
```

Brings 33 MB → ~19 MB with no perceptible quality loss. See `scripts/discord-encode.sh`.

For longer videos (60–90s), drop `-b:v` to 2500k.

## 5. The `showorg` header silence

### What happened
First Postiz API exploration: hit `/api/integrations/list`, got `[]` back. Spent 20 minutes wondering if the user's account had no integrations connected.

The actual issue: the endpoint is org-scoped and requires `showorg: true` to return the org's data. Without it, returns empty array silently — no 401, no "missing header" warning.

### Cost
- 20 wall-minutes of wrong-direction debugging.

### Rule
**Always include `showorg: true` on every Postiz API call.**

Bake it into your script's default headers; never optional.

## 6. Cloudflare WAF default-UA block

### What happened
Hit the Postiz API with `curl` (default UA `curl/7.x`). Got HTTP 403 with a Cloudflare-branded error 1010 page.

The API itself was fine; CF's WAF rule blocked the default UA before the request reached Postiz.

### Cost
- 5 minutes to recognize the error 1010 vs an actual auth issue.

### Rule
**Always send a Mozilla-style User-Agent on Postiz API calls.**

```
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

Bake this into your script defaults too.

## 7. Postiz `PUT /api/posts/{id}` 404

### What happened
Tried to amend a queued post via `PUT /api/posts/{id}`. Got 404. Spent 10 minutes wondering if the post had been deleted or if the route was wrong.

Actual issue: the route doesn't exist. Postiz updates are `POST /api/posts` again with the existing `id` inside `value[0].id`.

### Cost
- 10 minutes confused.

### Rule
**Postiz has no PUT for posts. Update is `POST /api/posts` with `value[0].id`.**

Document this in any client wrapper you write.

## 8. Assuming "fail-fast" tools mean what they say

### What happened
`DELETE /api/posts/{group_uuid}` returns `{"error":true}` in the body. Looked like a failure. Assumed deletion failed.

Actual: deletion succeeded. The response body just always says that. Verify by `GET /api/posts/<post_id>` — you'll get HTTP 500 if the post no longer exists.

### Rule
**Don't trust response bodies as the sole signal of success. Verify state via a separate fetch.**

This is a general rule beyond Postiz: when an API gives you a confusing response, write a verification call.

---

## Compounding lesson

Each of these on its own is a small loss (5–30 minutes). Compounded across a tight launch deadline, they become the difference between "shipped clean" and "shipped with bugs." This skill exists so future runs catch them in advance — research first, ducks-in-row, then render and ship.
