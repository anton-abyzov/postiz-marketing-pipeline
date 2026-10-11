---
name: postiz-marketing-pipeline
version: 2.5.0
description: Short-form video and ad production plus the Postiz internal-API mechanics behind it, for Anton's self-hosted Postiz (postiz.easychamp.com). Covers cookie-auth Postiz calls (showorg and User-Agent headers, upload, per-platform settings, in-place update and bulk media swap, delete-by-group, >100MB uploads over SSH, Instagram covers), rights-safe real-player imagery (CC Wikimedia photos, never ripped broadcast footage), fact checks before render, no-repeat B-roll, ElevenLabs Sarah voiceover, music licensing, ffmpeg mixing and loudness, Remotion and HyperFrames limits, the WC-26 visual system, YouTube Shorts metadata, Anton's posting schedule and founder voice, and the World Cup 2026 anti-patterns. Use when building TikTok/Reels/Shorts/LinkedIn ad creative, rendering or mixing promo videos, sourcing stock or player photos, timing a launch wave, or bulk-scheduling, swapping media on or deleting Postiz posts via the API. Routing, account IDs and approval live in social-media-posting.
license: MIT
keywords:
  - postiz
  - short-form-video
  - remotion
  - hyperframes
  - elevenlabs
  - ffmpeg
  - audio-mix
  - stock-footage
  - creative-commons
  - video-production
---

# Postiz Marketing Pipeline

Production playbook from the World Cup 2026 launch runs (WC-26 app and the @aabyzov bilingual football clips).

Load `social-media-posting` first. It owns routing (X and TikTok go through Blotato, everything else through Postiz), the Blotato and Postiz account IDs, YouTube channel routing (AI content goes to `@antonabyzov`, never the family channel), preview links and the per-post approval gate. Nothing in this skill relaxes that gate. For Kie image and video generation (`/api/v1/jobs/createTask`, GPT Image 2, Nano Banana Pro, Seedance), use `kie-gemini-omni`. Use `hyperframes*` and `remotion-best-practices` for general composition work.

Postiz also carries Bluesky, dev.to and Pinterest (business accounts only). Postiz-side YouTube channels include SkillUp Football `@skillupfootballapplication`. Out of scope: Postiz TikTok and X (removed; use Blotato), LinkedIn Company Pages (no route), long-form YouTube editing, and running paid ad campaigns.

Blotato dedup (used by `schedule_specs.py`): key TikTok posts under platform `tiktok`, not `twitter`; `GET /v2/accounts` returns 401, so derive accounts from `/v2/schedules`; `/v2/media` re-ingest returns a new UUID each call, so dedup by (account, caption), not media basename.

## Postiz internal API (cookie auth)

Use this API for bulk work the public API key can't do. Details are in `references/postiz-api.md`.

- Base `$POSTIZ_BASE_URL` (`https://postiz.easychamp.com`). Log in with `scripts/postiz-login.sh`: `POST /api/auth/login` with `{"email","password","provider":"LOCAL"}`. Since the June 2026 build the field is `provider`, not `providerName`. The JWT comes back as the `auth` cookie and lasts about a month. Credentials: vault note `Postiz creds.md`.
- Send `showorg: true` and a Mozilla User-Agent on every call. Without `showorg`, org-scoped endpoints return `[]` silently. Without the UA, Cloudflare WAF returns 403 with error 1010.
- `POST /api/posts` body: `type` (`schedule` or `now`), `date`, `shortLink: false`, top-level `tags: []` (not inside `posts[]`), and `posts: [{integration:{id}, value:[{content, image:[{id, path}]}], group:<uuid>, settings}]`. `image[]` items need both `id` and `path` (otherwise: "image.0.id must be a string").
- Platform settings (a missing required key gives a 400):

| Platform | `settings` |
|---|---|
| Instagram / instagram-standalone | `{"post_type":"post"}` (or `"story"`). Never `"reel"`: it fails with a generic error, and video becomes a Reel anyway |
| YouTube | `{"title":"<≤60 chars>","type":"public"\|"private"\|"unlisted","tags":[{label,value}]}`, optional `category` (`22` People & Blogs, `27` Education, `28` Sci & Tech, `17` Sports), optional `thumbnail:{id,path,name}` |
| Discord | `{"channel":"<numeric channel id>"}`. List channels with `POST /api/integrations/function` `{"id":"<integration>","name":"channels","data":{}}` |
| Pinterest | `{"title":"...","board":"<board>"}` |
| LinkedIn | `{}` or `{"post_as":"user"}` |
| Facebook, Threads, Telegram | `{}` |

- No PUT; `PUT /api/posts/{id}` returns 404. To update in place, `POST /api/posts` again with the existing post `id` in `value[0].id` and the existing `group`; the schedule is kept. `scripts/postiz-swap-media.py` does this for N posts. Get the group first with `GET /api/posts/{id}`.
- Delete with `DELETE /api/posts/{group_uuid}` (the group UUID, not the post ID). The `{"error":true}` reply is misleading: the delete worked. Confirm with `GET /api/posts/{id}`, which returns 500 once the post is gone. Published posts cannot be deleted through Postiz.
- Files over ~100MB get a 413 from the Cloudflare Tunnel. Upload them from the Postiz host to `http://localhost:4242/api/media/upload-simple` over SSH; the host and SSH key are in vault note `Postiz on Hetzner`. See `references/postiz-api.md`.
- An ERROR post is retried on the next cron tick once the cause is fixed, for example after swapping in a smaller file.

## Instagram covers (mandatory, 2026-10-02)

Postiz publishes a reel with `thumb_offset = image[0].thumbnailTimestamp || 0`. If unset, frame 0 (a grey fade, black, or a shared template) lands on the profile grid.

1. Pick a sharp, finished frame that says what the reel is about, with the hook text inside the centre 3:4, and not used as a cover elsewhere on the account.
2. Send it as `"image":[{"id":...,"path":...,"thumbnailTimestamp":<ms>}]`.
3. `instagram` channels (Facebook Login) honour the offset. `instagram-standalone` channels (Instagram Login, e.g. @aabyzov) ignore it and show frame 0, so put the cover in frame 0 there.
4. After scheduling, run `python3 ~/Projects/github/marketing/scripts/covers/covers.py check` (must report 0 failing); `covers.py sheet <postId>` shows labelled frames and `covers.py set <postId>=<ms>` fixes a queued post. After publishing, run `covers.py verify`. `check` alone does not prove the cover is right.

## Rights and facts (hard rules)

- **Never rip broadcast or social match video**, even when Anton pushes for it ("it's on TikTok, just add labels"). FIFA owns it, and Content ID and Meta Rights Manager match it at upload. Three strikes in 90 days terminates the channel and every linked channel, with no reinstatement. Adding labels doesn't clean it. Duet, Stitch and reshares are not a monetized lane (reshare ≠ license, credit ≠ license).
- **Real players, legally:** `scripts/fetch_cc_photos.py "<name>" <slug>` pulls CC BY / CC BY-SA / PD photos from Wikimedia Commons (skips `(cropped)` duplicates, prefers current-tournament titles, sends a UA, sleeps ≥1.3s to avoid 429). Every caption that uses one carries `Photo: <author> / Wikimedia Commons, <license>`. Editorial commentary is fine; never use a likeness to sell a product, and never AI-generate a real player's face. Order of preference: animated CC photos → licensed editorial stills (non-match) → own footage → generic AI B-roll (no likeness, no logos) → diagrams.
- **No celebrity or announcer likeness or voice in ads**, AI-generated included (US right of publicity, ECHR Art. 8). Use generic personas ("Marcus, fan from Brooklyn") and kits that don't match a real team's colours.
- **Verify before you render.** Every score, date, venue or record needs two independent primary sources (FIFA, Wikipedia, major outlets, venue sites) before it goes into a frame. Real misses: "Argentina opens at AT&T Stadium June 11" (Mexico vs South Africa opened at Azteca; Argentina's first match was June 16 in Kansas City), "Canada won on home soil" (it was Los Angeles), "Messi's 7th World Cup" (6th, 19 goals). Fix the spec, delete the stale VO, re-render.
- **Never post brand A creative to a dormant brand B channel** (no posts in 30+ days). Personal channels can carry anything.

## Footage

- Never reuse a B-roll bed across clips; repeats look like mirrored images and hurt reach. Generate or source fresh footage per clip even when it costs more, and keep a clip inventory.
- Stills alone read as "no video". Intercut CC photos with Ken Burns (ffmpeg `zoompan`, alternating zoom in and out) with AI B-roll, under a ducked music bed.
- Stock: Pexels, Pixabay and Mixkit are free for commercial use with no attribution. Anything marked editorial-only can't be used in ads. More in `references/stock-sourcing.md`.
- Kie result URLs return 403 to plain urllib (Cloudflare). Download with `curl` and a browser UA.
- HyperFrames fails with 7+ simultaneous video layers at 1920x1080. Use at most 3 in landscape; vertical 1080x1920 handles more.
- Remotion: use `OffthreadVideo`, never `<video>`. Use `--concurrency=4` on M-series Macs. Presets are in `references/remotion-recipes.md`.
- zsh does not word-split an unquoted `$var`, so pass explicit arguments in shell loops.

Spec-driven football pipeline (marketing repo `generated-assets/aabyzov-football/`): trending-scout → polished spec → fact-verify → `build_from_spec.py` (VO EN+RU, Ken Burns photos, AI beds from `gen_beds_v2.py`, music) → Remotion `FootballPromo` (mixed video and photo beds, `music` prop) via `render_promo.py` → `schedule_specs.py` (Postiz Threads/YT/IG/LinkedIn + Blotato TikTok, per-platform captions, dedup guard). To add a storyline, add one spec entry. What goes viral at a World Cup is fan culture, memes and underdogs rather than highlights: bilingual RU+EN, the hook pays off in under a second, debate-bait CTA.

## Voice and music

- VO: ElevenLabs Sarah `EXAVITQu4vr4xnSDxMaL`. English with `eleven_turbo_v2_5`, Russian with `eleven_multilingual_v2`. Stability 0.5–0.55, similarity 0.75, style 0–0.15, speaker boost on. Generate one clip per section so timing is controllable. See `references/ai-assets.md`.
- Generated bed: ElevenLabs Music `POST /v1/music` with `{prompt, music_length_ms}`, ducked to about 0.16 under the VO. A library bed (e.g. Skybound Circuits) sits at 0.14 with a 0.5s fade-in and a 2s fade-out at the end.
- **Music selection:** for each destination account, shortlist from that account's actual eligible catalog or current trend evidence. Pick for the hook, the mood and speech clarity first, popularity second. A famous artist or a search hit proves neither availability, permission nor reach. Keep a clean master. Native catalog previews may be listened to but never ripped or baked into a cross-platform video. Embedded music needs a separate licence for the recording and the composition, covering that destination, territory and organic or paid use. Honour an explicit no-music request. Follow the [social music workflow](https://github.com/anton-abyzov/sw-easychamp/blob/develop/docs/15-marketing/social-music-workflow.md) (local: `~/Projects/sw-easychamp/docs/15-marketing/social-music-workflow.md`) and its `scripts/social-music/preflight.py`. If the checkout lacks them, read the authenticated GitHub source, and leave that checkout's active owners alone. Instagram API music needs supported Facebook Login and a single-video Reel; the native app's library can differ. For TikTok, YouTube or a track the API can't use, you need a verified connector, separately licensed embedded music, or an explicitly prepared native-app finish. Never send a payload that silently drops the selected music. The approval draft names the audio ID, title, artist, segment (or the platform's limitation), the mix, the rights scope and current account evidence. Re-check near publication, and after publishing confirm attribution and that the music is audible; "queued" or "uploaded" is not proof.

## Audio mix

Simple 3-input mix (video ambience + VO + music; set `st` to the video length minus 2s):

```bash
ffmpeg -y -i VIDEO -i VO -i MUSIC \
  -filter_complex "[0:a]volume=0.08[vid];[1:a]adelay=500|500,volume=1.0,apad[vo];[2:a]volume=0.14,afade=t=in:d=0.5,afade=t=out:st=28:d=2[music];[vid][vo][music]amix=inputs=3:duration=first[out]" \
  -map 0:v -map "[out]" -c:v copy -c:a aac -b:a 192k OUTPUT
```

Paid placement gets the 6-input recipe (VO + sidechain-ducked music + 4 timed stadium drops, then `alimiter=limit=0.95,loudnorm=I=-14:LRA=7:tp=-1.5`) in `references/audio-mix.md`. Every platform targets -14 LUFS / -1.5 dBTP.

## Delivery rules

- Discord (non-Nitro) caps uploads at 25 MB. Run `scripts/discord-encode.sh` (libx264 3500k, AAC 128k; 2500k for 60s+).
- Hook in the first 1–3s with no logo sting or "hey guys". URL and a one-sentence CTA in the last 3–5s. VO starts at 500ms.
- Visual style: never a black background, always footage or an image behind everything. 80px safe margins. `0 4px 20px rgba(0,0,0,0.9)` text shadow. Labels stay on screen 3–5s, not the whole clip. Bullets use emoji icons. No cropped faces. Vendor logos come from the vendor's `apple-touch-icon.png`, never generated.
- WC-26 system: glass card `rgba(24,24,27,0.85)` + `blur(20px)` + 24px radius; gold `#fbbf24` CTA; rose `#e11d48` accents; stat pills ("48 Teams", "16 Cities"); iPhone frame for app screens.
- YouTube Shorts metadata: title under 70 chars, primary keyword, no emoji. Description line 1 = hook + URL inside the first 150 characters; line 2 = CTA. Then sections separated by `---`: timestamps (even on Shorts: 4–6 for 30s, 6–8 for 45s; they become chapters and help search), links (product URL + social handles), 2–3 sentence about, one-line subscribe CTA, 3–5 hashtags at the end (over 15 and YouTube ignores all of them), and a comma-separated tags line for the Studio Tags field (≤500 chars). Put the link in a pinned comment too; never say "link in bio" on YouTube. Made for Kids = No.
- Framing: personal channels use founder narrative ("I built this in 14 days"), product channels lead with the product. Founder voice: speed ("built in 14 days", "shipped end-to-end with AI agents"), stack credibility ("Claude Code + Remotion + Cloudflare Workers", "18 years of coding experience"), honesty about what broke, social proof from shipped products (EasyChamp, SkillUp Football, JobWeave, SpecWeave). CTA style: energetic, confident, slightly pushy but authentic. Anton's links: x.com/aabyzov, instagram.com/aabyzov, threads.net/@aabyzov, linkedin.com/in/antonabyzov, youtube.com/@AntonAbyzov, t.me/antonaipower.
- Posting schedule (ET, from engagement data across 10 channels) is in `references/multi-channel-strategy.md`; schedule through Postiz at least 2h before the slot so there is time to review.

## Files

- `references/postiz-api.md`: auth, headers, upload, payloads, in-place update, delete, errors, large-file SSH route.
- `references/audio-mix.md`: 6-input recipe, loudness checks.
- `references/ai-assets.md`: ElevenLabs voices and settings, where keys live.
- `references/stock-sourcing.md`: licences, editorial vs commercial, audio sources.
- `references/remotion-recipes.md`: dimension presets and Remotion gotchas.
- `references/anti-patterns.md`: incident write-ups behind the hard rules.
- `references/multi-channel-strategy.md`: weekly schedule and launch windows, channel triage, caption tone by platform.
- Scripts: `postiz-login.sh`, `postiz-list-channels.sh`, `postiz-swap-media.py`, `discord-encode.sh`, `fetch_cc_photos.py`.

Env vars (check they exist with `grep -q`; never print them): `POSTIZ_BASE_URL`, `POSTIZ_EMAIL`, `POSTIZ_PASSWORD`, `ELEVENLABS_API_KEY`, `KIE_API_KEY`, optional `PEXELS_API_KEY` and `PIXABAY_API_KEY`.
