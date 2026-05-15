---
name: postiz-marketing-pipeline
version: 2.3.0
description: End-to-end short-form marketing pipeline for self-hosted Postiz - covers Postiz API automation (auth, scheduling, in-place media swap, multi-channel inventory), Remotion + HyperFrames video production (app demos and stock-footage overlays), AI video generation (Veo 2.0/3.0, Imagen 4), free-license stock sourcing (Pexels/Pixabay), ElevenLabs Sarah voice, 3-input and 6-input ffmpeg audio mixing, WC-26 branded design system, YouTube description optimization, cross-platform description adaptation, personal brand integration, publishing schedule templates, quality rules for professional output, and the anti-patterns we learned the hard way (cross-posting brand pollution, Right of Publicity violations, LLM-fabricated tournament facts). Use when scheduling posts via the Postiz REST API, building short-form ad creative for TikTok/Reels/Shorts/X/LinkedIn, crafting YouTube descriptions and metadata, producing video with HyperFrames or Remotion, or coordinating multi-channel launch waves.
license: MIT
keywords:
  - postiz
  - social-media-scheduling
  - remotion
  - short-form-video
  - elevenlabs
  - ffmpeg
  - kie-ai
  - launch-pipeline
  - multi-channel
  - automation
  - youtube-description
  - cross-platform
  - personal-brand
  - hyperframes
  - veo
  - imagen
  - video-production
  - publishing-schedule
---

# Postiz Marketing Pipeline

Reusable playbook for shipping short-form video ads end-to-end through a self-hosted Postiz instance, distilled from a real World Cup 2026 launch run (10 channels, v5->v8 media swap, multiple paid-placement variants).

## When to use this skill

Activate when the user wants to:

- Schedule, update, swap-media, or delete posts via the **Postiz REST API** (the UI is fine for one-off edits, but anything bulk benefits from this).
- Build **short-form video ads** (TikTok/Reels/Shorts/X/LinkedIn) using Remotion with layered stock footage, AI voiceover, and platform-specific cuts.
- Source **free, commercially-licensable stock footage and B-roll** (Pexels/Pixabay) without falling into paid-only sources.
- Produce **video with HyperFrames** (stock B-roll backgrounds with animated overlays, stat pills, vendor tags).
- Generate **AI assets** (images via KIE AI / Nano Banana / Imagen 4, photorealistic B-roll via Veo 2.0/3.0, VO via ElevenLabs Sarah voice).
- **Mix audio** for short-form (VO + music + crowd ambience + SFX with sidechain ducking and broadcast-safe limiting).
- Coordinate a **multi-channel launch wave** with channel-appropriate captions and an avoid-list of cross-pollinating channels.
- Craft **YouTube video descriptions** with SEO-optimized metadata, timestamps, tags, and hashtags.
- Adapt **descriptions across platforms** (YouTube vs Instagram vs X vs LinkedIn vs Threads).
- Integrate **personal brand narrative** into product launches (founder story vs product-first framing).

## What this skill does NOT cover

- Hosted Postiz SaaS at `postiz.com` (this skill is tuned for self-hosted, but the API surface is identical -- only the base URL changes).
- LinkedIn Company Pages -- Postiz only handles personal LinkedIn. Use Blotato or post manually.
- TikTok scheduling -- Postiz cannot schedule TikTok directly. **Use Blotato API** (`POST /v2/posts` with `targetType: "tiktok"`); the `tiktokpost` browser-skill is the legacy fallback only.
- **X / Twitter scheduling -- Postiz X support was removed (2026-05-15). All X/Twitter posts MUST go through Blotato API** (`POST /v2/posts` with `targetType: "twitter"`). See "Platform routing matrix" below.
- Long-form (>3 min) YouTube -- this skill is short-form only.
- Paid-ad campaign management (Google/Meta Ads Manager). The video assets are paid-placement-ready; the ops are out of scope.

## Confirmation workflow (MANDATORY)

**NEVER auto-publish any content.** Every piece of content -- descriptions, captions, posts, videos -- MUST go through this workflow:

1. **Draft**: Generate the content (description, caption, metadata) and present it to the user in full.
2. **Review**: Wait for explicit user approval. Highlight anything that needs fact-checking (dates, prices, URLs, claims).
3. **Revise**: If the user requests changes, apply them and present the updated draft.
4. **Approve**: Only after the user says "approved", "looks good", "ship it", or similar explicit confirmation, proceed to publish/schedule.
5. **Confirm**: After publishing, report back with the post URL/ID and final state.

**Anti-pattern**: "I've scheduled your post for 7:30 PM ET" without showing the draft first. NEVER do this.

**Exception**: If the user explicitly says "just publish it" or "auto-publish without review", you may skip the review step -- but log a warning that the confirmation was bypassed.

## Hard-won anti-patterns (read these first)

1. **DON'T cross-post brand-A content to brand-B channels.** Even when it would technically reach more eyeballs, it pollutes the algorithmic signal of the off-brand channel. We shipped 11 launch posts and had to delete one when it landed on a sibling channel that wasn't ready to be associated with the new brand. Rule of thumb: if the channel hasn't yet launched its own marketing, never seed it with adjacent content.
2. **DON'T use celebrity likenesses without authorization.** Even AI-generated likenesses violate Right of Publicity (state-level, US) and Article 8 ECHR (EU). For sports content this means no real player faces, no team kits if you're representing them as players, and no announcer voices. Use generic personas (`Marcus, fan from Brooklyn`) and stylized stadium shots.
3. **DON'T trust LLM-claimed dates without 2-source verification.** We shipped a creative variant claiming "Argentina opens the World Cup at AT&T Stadium on June 11" -- the actual opener was Mexico vs South Africa at Estadio Azteca, and Argentina's first match was June 16 in Kansas City. Both facts were trivially verifiable with one curl to Wikipedia or FIFA. The cost: re-rendering 5 variants under deadline pressure. **Always cross-check tournament/release/event dates with at least 2 independent primary sources before they bake into a video.** See `references/anti-patterns.md` for the full incident write-up.
4. **DON'T amend a published Postiz post via PUT** -- the endpoint returns 404. Update is an idempotent `POST /api/posts` with the existing `id` inside `value[0].id`. See `references/postiz-api.md`.
5. **DON'T forget the `showorg` and `User-Agent` headers** on every Postiz API call. Without `showorg: true`, org-scoped endpoints return empty arrays silently. Without a Mozilla-style UA, Cloudflare WAF returns HTTP 403 with error 1010 -- the API itself is reachable, you're just blocked at the edge.
6. **DON'T assume a 35 MB MP4 will publish to Discord.** Discord's non-Nitro upload limit is 25 MB. Re-encode for Discord specifically: `-c:v libx264 -preset slow -b:v 3500k -c:a aac -b:a 128k` brings a 45-second 1080x1920 video from 33 MB to ~21 MB without visible quality loss.

## YouTube description template

Use this structure for all YouTube Shorts and short-form video uploads. The template is SEO-optimized based on real launch data from the WC26 campaign.

### Structure

```
[LINE 1: Hook sentence with primary keyword + product URL -- MUST be under 150 chars]
[LINE 2: CTA or value prop -- this is the last line visible before "Show More"]

---

[TIMESTAMPS -- even for Shorts, helps SEO and accessibility]
0:00 [Beat label]
0:XX [Beat label]
...

---

[LINKS SECTION]
[Product URL]
[Social profiles with handles]

---

[ABOUT SECTION -- who you are, what the product does, 2-3 sentences]

---

[SUBSCRIBE CTA -- one line]

---

[HASHTAGS -- 3-5 at the END, YouTube shows first 3 above the title]

---

[Hidden tags line -- comma-separated, for YouTube Studio "Tags" field]
```

### Template rules

1. **First 150 characters are critical** -- they show in search results and suggested video cards. Front-load the hook + URL.
2. **Product URL in line 1 or 2** -- always above the fold (before "Show More").
3. **Timestamps** -- even for 30-45 second videos. YouTube indexes these for search and creates chapter markers. They also signal quality content to the algorithm.
4. **Hashtags at the END** -- YouTube renders the first 3 hashtags above the video title as clickable links. Place them at the bottom of the description. Max 15, but 3-5 is optimal. More than 15 and YouTube may ignore ALL of them.
5. **Tags** (YouTube Studio field, separate from description) -- comma-separated keywords, max 500 chars total. Mix broad ("World Cup 2026") with specific ("AI travel planner") and long-tail ("how to plan World Cup trip").
6. **Subscribe CTA** -- one sentence, not pushy. "Subscribe for more [topic]" works.
7. **No emoji in title** -- YouTube's own data shows titles without emoji get higher CTR in most niches. Emoji in description body is fine.

### Example (WC26 launch, Anton's channel)

**Title options** (pick best fit):
- `I Built an AI Travel App for the World Cup in 2 Months`
- `AI Plans Your World Cup 2026 Trip in 30 Seconds`

**Description**:
```
I built an AI travel concierge for FIFA World Cup 2026. Plan your trip free at https://wc-26.net
First 1,000 founders get Pro for $3.49/mo for life. 45-second demo below.

0:00 Hook
0:03 The Problem
0:08 Meet the AI Concierge
0:15 Trip Planning Demo
0:25 Ticket Comparison
0:30 Real Match Data
0:35 Pricing
0:40 Get Started

Try it free: https://wc-26.net

Connect with me:
X (Twitter): https://x.com/aabyzov
Instagram: https://instagram.com/aabyzov
Threads: https://threads.net/@aabyzov
LinkedIn: https://linkedin.com/in/antonabyzov
YouTube: https://youtube.com/@AntonAbyzov
Telegram: https://t.me/antonaipower

I'm Anton Abyzov -- software engineer and builder. I shipped wc-26.net using Claude Code and AI agents end-to-end: an AI-powered travel companion for the FIFA World Cup 2026 with trip planning, ticket comparison across 5 vendors, real match data for all 48 teams, and 16 host city guides. Free tier covers everything you need. Pro unlocks unlimited AI concierge, saved trips, and ticket alerts.

Subscribe for more AI builds and dev tutorials: https://youtube.com/@AntonAbyzov

#WorldCup2026 #AITravel #WC26 #FIFA #BuildInPublic
```

**Tags** (for YouTube Studio):
```
World Cup 2026, FIFA World Cup, WC26, AI travel, travel planner, AI concierge, trip planning, World Cup trip, soccer travel, football World Cup, host cities, ticket comparison, build in public, indie hacker, AI app demo, Claude Code, World Cup 2026 app, travel companion, Mexico City World Cup, MetLife Stadium
```

## YouTube Shorts best practices

Distilled from real campaign performance data and YouTube creator documentation.

### Hooks (first 1-3 seconds)

The hook determines whether viewers stay or swipe. Patterns that work for product demos:

| Pattern | Example | When to use |
|---|---|---|
| **Problem statement** | "Going to the World Cup? Don't drive." | Pain point the product solves |
| **Bold claim** | "AI plans your entire trip in 30 seconds." | Demonstrable capability |
| **Countdown/urgency** | "34 days to kickoff. Got a plan?" | Time-sensitive products |
| **Personal story** | "I shipped this app in 14 days." | Founder narrative / build-in-public |
| **Question** | "How much would you pay to plan a World Cup trip?" | Engagement bait (use sparingly) |

**Anti-pattern**: Starting with "Hey guys" or a logo animation. You have 1 second before the swipe.

### Timestamps for Shorts

Even though YouTube Shorts autoplay in a loop, adding timestamps in the description:
- Helps YouTube understand the content structure for search indexing
- Creates chapter markers that appear if users tap the progress bar
- Signals high-quality content to the recommendation algorithm
- Improves accessibility for screen readers

For a 45-second video, aim for 6-8 timestamp entries. For 30 seconds, 4-6.

### CTAs that convert on Shorts

- **In-video text overlay** at the final 3-5 seconds with the URL
- **Description line 1** must contain the URL (Shorts description is truncated aggressively)
- **Pinned comment** with the link (Shorts comments are often more visible than descriptions)
- **Audio CTA** in the last 5 seconds: keep it to one sentence ("Free at wc-26.net")
- **Never** ask viewers to "click the link in bio" -- that is Instagram language, not YouTube

### Shorts-specific metadata

- **Title**: Under 70 chars. No emoji. Include primary keyword.
- **Category**: Match your content (22 = People & Blogs, 27 = Education, 28 = Science & Tech, 17 = Sports)
- **Visibility**: Public for organic reach. Unlisted only for embed/share-only use.
- **Made for Kids**: Set to NO unless your content is specifically for children. Getting this wrong restricts comments and recommendations.

## Cross-platform description optimization

Each platform has different description behavior, character limits, and SEO rules. Always adapt -- never copy-paste the YouTube description to other platforms.

### Platform comparison

| Platform | Visible before fold | Max length | Hashtag behavior | Link behavior | Key difference |
|---|---|---|---|---|---|
| **YouTube** | ~150 chars + title | 5,000 chars | First 3 shown above title | Clickable in description | Timestamps = chapters |
| **Instagram Reels** | ~125 chars | 2,200 chars | Up to 30, but 3-5 optimal | NOT clickable (link in bio only) | Hashtags drive discovery |
| **X (Twitter)** | Full post visible | 280 chars (text) | 1-2 max, inline | Clickable | Brevity is everything |
| **LinkedIn** | ~140 chars | 3,000 chars | 3-5 at end | Clickable | Professional tone required |
| **Threads** | ~100 chars | 500 chars | 3-5 inline | Clickable | Casual, conversational |
| **TikTok** | ~80 chars | 2,200 chars | 3-5 | Link in bio only | Trending sounds > copy |
| **Telegram** | Full message | 4,096 chars | Optional | Clickable | Direct, informational |
| **Discord** | Full message | 2,000 chars | None | Clickable + embeds | Community voice |

### Adaptation rules

1. **YouTube**: Full description with timestamps, links, about section, hashtags at end. Most SEO-rich.
2. **Instagram**: Lead with hook. No links in caption (put URL in bio). Use 3-5 relevant hashtags. Emoji OK.
3. **X (Twitter)**: One punchy sentence + URL. 1-2 hashtags max. Mention build-in-public angle if relevant.
4. **LinkedIn**: Professional framing. Lead with business insight or lesson. Link inline. 3-5 hashtags at end.
5. **Threads**: Conversational, short. Same hook as IG but more casual. Links work here.
6. **Telegram**: Informational, direct. Full URLs. No hashtags needed. Community announcement tone.
7. **Discord**: Casual, community-first. "@everyone" for announcements. Ask for feedback.

### Caption variants template (from WC26 launch)

```
YouTube:  "I built an AI World Cup concierge in 14 days. Demo:"
X:        "I built an AI travel concierge for FIFA World Cup 2026 in 14 days using Claude Code + Remotion. Free at wc-26.net. First 1,000 founders get Pro for $3.49/mo for life."
IG:       "AI just planned my whole World Cup trip. 30 seconds. Free at wc-26.net. Founders save 50% for life. #WC26 #WorldCup2026 #AItravel #BuildInPublic #FIFA"
LinkedIn: "Shipped wc-26.net in 14 days using AI agents end-to-end. Stripe + iOS IAP wired in one session. Demo + lessons learned below."
Telegram: "Shipped: wc-26.net -- AI travel concierge for the World Cup. Free trip planner. First 1,000 founders get Pro for $3.49/mo lifetime."
Discord:  "Hey @everyone -- soft launch of WC26 Travel: free AI itinerary planner for the World Cup. Try wc-26.net and tell me what breaks."
```

## Personal brand integration

Guidelines for when to use founder narrative vs product-first framing, based on platform and audience.

### Decision matrix

| Context | Use founder narrative | Use product-first |
|---|---|---|
| **Personal channels** (Anton YT, X, IG, LinkedIn) | YES -- "I built this" | Secondary |
| **Product channels** (EasyChamp, SkillUp) | No | YES -- "Plan your trip" |
| **Build-in-public audience** (X, indie hackers, dev Twitter) | YES -- emphasize speed, stack, lessons | Light |
| **Consumer audience** (IG Reels, TikTok, YouTube Shorts) | Brief hook only ("I built this in X days") | YES -- show the product |
| **Professional network** (LinkedIn) | YES -- emphasize business outcomes, revenue | Support with product demo |
| **Community** (Discord, Telegram) | Authentic, casual | YES -- ask for feedback |

### Founder narrative elements (Anton Abyzov)

Use these when the founder story is the right frame:

- **Speed**: "Built in 14 days" / "Shipped end-to-end with AI agents"
- **Stack credibility**: "Claude Code + Remotion + Cloudflare Workers" / "18 years of coding experience"
- **Authenticity**: "I'll show you what broke" / honest about challenges
- **Social proof**: Multiple products shipped (EasyChamp, SkillUp Football, JobWeave, SpecWeave)
- **CTA style**: Energetic, confident, slightly pushy but authentic (per Anton's established voice)

### Product-first elements

Use these when the product should lead:

- **Value prop**: "Plan your World Cup trip in 30 seconds"
- **Feature highlights**: AI concierge, ticket comparison (5 vendors), 16 city guides, real match data
- **Pricing**: "Free tier covers everything. Pro $3.49/mo for founders."
- **Urgency**: Tournament countdown, limited founder spots
- **Social proof**: User count, trip plans created (when available)

### Tone by platform

| Platform | Tone | Example opener |
|---|---|---|
| YouTube | Energetic, demo-focused | "I built an AI travel concierge in 14 days." |
| X | Punchy, build-in-public | "Shipped wc-26.net. 14 days. Claude Code + Remotion." |
| Instagram | Visual-first, casual | "AI just planned my whole World Cup trip." |
| LinkedIn | Professional, insight-led | "Shipped wc-26.net in 14 days using AI agents end-to-end." |
| Threads | Conversational | "Just launched something cool for World Cup fans." |
| Telegram | Direct, informational | "Shipped: wc-26.net -- AI travel concierge for the World Cup." |
| Discord | Community, feedback-seeking | "Hey everyone -- soft launch. Try it and tell me what breaks." |

## Quick start: schedule one post via Postiz API

```bash
# 1. Auth -- JWT lives in Set-Cookie, capture to a cookie jar
curl -sS -c /tmp/postiz-cookies.txt \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  -H "Content-Type: application/json" \
  -X POST "https://postiz.example.com/api/auth/login" \
  -d '{"email":"you@example.com","password":"redacted","providerName":"LOCAL"}'

# 2. Discover channels (the showorg header is REQUIRED for org-scoped endpoints)
curl -sS -b /tmp/postiz-cookies.txt \
  -H "showorg: true" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  "https://postiz.example.com/api/integrations/list"

# 3. Upload media (multipart)
curl -sS -b /tmp/postiz-cookies.txt \
  -H "showorg: true" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  -F "file=@/path/to/video.mp4" \
  "https://postiz.example.com/api/media/upload-simple"
# response: { id, path, name, originalName }

# 4. Schedule a post
curl -sS -b /tmp/postiz-cookies.txt \
  -H "showorg: true" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  -H "Content-Type: application/json" \
  -X POST "https://postiz.example.com/api/posts" \
  -d @scripts/payload.json
```

See `references/postiz-api.md` for the full payload shape, the in-place update pattern, deletion-by-group-uuid quirk, and channel-discovery flow.

## Quick start: render a layered short-form ad

```tsx
// video/src/compositions/MyAd.tsx
import {AbsoluteFill, OffthreadVideo, useCurrentFrame, interpolate} from 'remotion';
import {staticFile} from 'remotion';

export const MyAd: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill>
      {/* Layer 1: stock B-roll background */}
      <OffthreadVideo src={staticFile('stock/stadium-aerial-pexels.mp4')} muted loop />

      {/* Layer 2: glassmorphism card on top */}
      <div style={{
        position: 'absolute', bottom: 200, left: 60, right: 60,
        background: 'rgba(24,24,27,0.85)', backdropFilter: 'blur(20px)',
        borderRadius: 24, padding: 32, opacity,
      }}>
        <h1 style={{color: '#fbbf24', fontSize: 84, fontWeight: 800}}>
          The World Cup is here.
        </h1>
      </div>
    </AbsoluteFill>
  );
};
```

Render: `npx remotion render src/index.ts MyAd out/my-ad.mp4 --concurrency=4`

See `references/remotion-recipes.md` for: word-by-word VO-timed reveals, Ken Burns zoom, Lucide stroke SVG icons inlined, multi-layer video-on-video composition, and platform-specific dimension presets (TikTok/Reels/Shorts/X/LinkedIn).

## Quick start: 6-input audio mix

```bash
ffmpeg -y \
  -i vo-sarah.mp3 \
  -i music-bed.mp3 \
  -i stadium-roar-1.wav \
  -i stadium-roar-2.wav \
  -i stadium-cheer.wav \
  -i goal-celebration.wav \
  -filter_complex "
    [1:a]volume=0.25,sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[duck1];
    [duck1][0:a]amix=inputs=2:duration=longest:weights=1 1[mix1];
    [2:a]adelay=8000|8000,volume=0.6[s1];
    [3:a]adelay=22000|22000,volume=0.5[s2];
    [4:a]adelay=35000|35000,volume=0.6[s3];
    [5:a]adelay=42000|42000,volume=0.7[s4];
    [mix1][s1][s2][s3][s4]amix=inputs=5:duration=first[premix];
    [premix]alimiter=limit=0.95,loudnorm=I=-14:LRA=7:tp=-1.5[out]
  " -map "[out]" -c:a aac -b:a 192k mixed.aac
```

Then mux with the silent video:
```bash
ffmpeg -y -i video-silent.mp4 -i mixed.aac -c:v copy -c:a aac -shortest video-final.mp4
```

See `references/audio-mix.md` for the recipe explained step-by-step, plus loudness targets per platform.

## Reference files

- `references/postiz-api.md` -- Auth, channels, media upload, scheduling, in-place update, deletion, common errors, the `showorg` discovery story.
- `references/remotion-recipes.md` -- Multi-layer composition, OffthreadVideo for inline stock, word-by-word VO reveals, glassmorphism cards, Lucide icons inlined, platform dimensions.
- `references/stock-sourcing.md` -- Full stock footage source guide (see Stock Footage Sources section below).
- `references/ai-assets.md` -- KIE AI gpt4o-image and Veo 3 prompts and pricing notes, ElevenLabs Sarah voice (`EXAVITQu4vr4xnSDxMaL`) settings, where API keys live.
- `references/audio-mix.md` -- The 6-input ffmpeg recipe explained, loudness targets, sidechain ducking parameters, alimiter tuning.
- `references/multi-channel-strategy.md` -- Channel inventory walk, caption variants per platform, the cross-post-pollution rule, audience-fit checklist.
- `references/anti-patterns.md` -- Full write-up of the LLM-fabricated-fact incident, the cross-pollination delete, Right of Publicity, Discord size limit.

## Helper scripts

- `scripts/postiz-login.sh` -- Login + cookie capture
- `scripts/postiz-list-channels.sh` -- Channel inventory
- `scripts/postiz-swap-media.py` -- In-place media swap across N posts
- `scripts/discord-encode.sh` -- Re-encode 1080x1920 video to <25 MB for Discord

## Configuration

The skill expects these env vars (or equivalents in your secret store):

| Variable | Purpose |
|---|---|
| `POSTIZ_BASE_URL` | e.g. `https://postiz.yourdomain.com` |
| `POSTIZ_EMAIL` / `POSTIZ_PASSWORD` | Local auth (or use `provider=GITHUB`) |
| `KIE_AI_API_KEY` | For image and motion clip generation |
| `ELEVENLABS_API_KEY` | For Sarah voice TTS |
| `PEXELS_API_KEY` | Optional -- for programmatic stock search |
| `PIXABAY_API_KEY` | Optional -- same |

Never log or echo these values. Use `grep -q` to check existence; never `cat .env`.

## Stock Footage Sources (ranked by quality + license)

### Tier 1 — Best Quality, Free Commercial Use, No Attribution

| Source | URL | Best for |
|--------|-----|----------|
| **Pexels Videos** | https://www.pexels.com/videos/ | Cinematic football crowds, stadium atmosphere, fans celebrating, drone shots, emotional edits. BEST overall. |
| **Pixabay Videos** | https://pixabay.com/videos/ | Sports clips, stadiums, crowd shots, transitions, slow motion. Huge library. |
| **Mixkit** | https://mixkit.co/free-stock-video/ | Modern reels/TikTok/Shorts style cinematic clips. Underrated. |

### Tier 2 — Free, Check License Per Clip

| Source | URL | Best for | License |
|--------|-----|----------|---------|
| **Videvo** | https://www.videvo.net/ | Sports clips, motion graphics | Some require attribution |
| **Videezy** | https://www.videezy.com/ | HD/4K sports and drone footage | Often requires attribution |
| **Coverr** | https://coverr.co/ | Stylish cinematic clips for intros/backgrounds | Free, no attribution |
| **Motion Places** | https://www.motionplaces.com/ | Travel/city atmosphere for host city edits | Free |
| **Mazwai** | https://mazwai.com/ | Artistic cinematic footage | Free |

### Premium (Paid)

| Source | URL | Notes |
|--------|-----|-------|
| **Getty Images Video** | https://www.gettyimages.com/videos | Real match footage, Messi/Ronaldo celebrations. Expensive. |
| **Pond5** | https://www.pond5.com/ | Cinematic edits, documentary vibe. Some free. |

### Search Terms for Football Star B-Roll

**Argentina / Messi**: "Argentina fans blue white", "Argentina celebration", "Messi fans", "albiceleste crowd", "Buenos Aires obelisk celebration"
**Portugal / Ronaldo**: "Portugal fans red green", "Ronaldo celebration", "Portuguese supporters", "selecao fans"
**General**: "World Cup final celebration", "stadium erupts goal", "fans jumping hugging", "trophy confetti", "stadium aerial night"

### Download Tools

```bash
# Pexels (no API key needed for individual clips — use CDN URL)
curl -L -o clip.mp4 "https://www.pexels.com/video/XXXXX/download/"

# yt-dlp (for reference clips from YouTube)
yt-dlp -f 'bestvideo[height<=1080]' "URL"

# Pexels API (if key available)
curl "https://api.pexels.com/videos/search?query=world+cup&per_page=10" -H "Authorization: $PEXELS_API_KEY"
```

### AI Video Generation (for custom star-style scenes)

| Service | Key available? | Best for |
|---------|---------------|----------|
| **Google Veo 2.0/3.0** | Yes (Gemini API key) | Photorealistic B-roll: stadium celebrations, fans, city aerials |
| **Google Imagen 4** | Yes (Gemini API key) | Professional icons, thumbnails, and social media thumbnails |
| **Higgsfield AI** | Yes (Full Access key in Obsidian) | AI video generation |
| **Pollinations.ai** | Yes | Image + video |

**Important**: Do NOT use real player likenesses without authorization (Right of Publicity). Use generic celebrations, fans in team colors, and stadium atmospheres. AI-generated "Ronaldo-style" celebrations with generic faces are OK if clearly not depicting the real person.

**Performance limits**: HyperFrames renders fail with 7+ video layers at 1920x1080 -- use max 3 simultaneous video layers for landscape compositions. Vertical (1080x1920) can handle more layers due to smaller visible area per frame.

## Video Production Pipeline

Two complementary tools for video production, selected based on content type:

### Remotion (app demo walkthroughs)

Use Remotion for screenshot-based compositions where the video shows the app UI:
- Phone frame mockups with app screenshots cycling through features
- Glassmorphism overlay cards with feature callouts
- Word-by-word VO-timed text reveals
- Platform-specific dimension presets (1080x1920 vertical, 1920x1080 landscape)

### HyperFrames (stock video with overlays)

Use HyperFrames for combining stock B-roll video backgrounds with animated overlays:
- Full-screen stock footage as base layer (stadium aerials, city shots, fan celebrations)
- Animated text overlays, stat pills, vendor tags on top of video
- Ken Burns zoom effects on still images
- Multi-clip sequencing with transitions

### WC-26 Design System Components

Branded components shared across both pipelines:
- **Phone frame**: iPhone mockup with rounded corners, notch, and app screenshots
- **Glass cards**: `rgba(24,24,27,0.85)` background + `blur(20px)` backdrop filter + 24px border radius
- **Vendor tags**: Real vendor logos sourced from apple-touch-icon URLs (e.g., `https://www.stubhub.com/apple-touch-icon.png`)
- **CTA overlay**: Gold (#fbbf24) text on dark glass, appears in final 3-5 seconds
- **Stat pills**: Rounded pill badges showing metrics (e.g., "48 Teams", "16 Cities", "5 Vendors")
- **Section headers**: Bold white text with Rose/Red (#e11d48) accent underline

### Stock Footage Rules

- **NEVER repeat clips across videos** -- each video gets unique B-roll
- **Context-match backgrounds to content** -- stadium clips for match features, city aerials for travel features, fans for social proof sections
- Maintain a clip inventory spreadsheet or list to track which clips have been used

### Voiceover

- **Voice**: ElevenLabs Sarah (ID: `EXAVITQu4vr4xnSDxMaL`, model: `turbo_v2_5`)
- **Settings**: Stability 0.5, Similarity Boost 0.75, Style 0.0
- Generate per-section VO clips for precise timing control

### Music

- **Track**: Skybound Circuits (or equivalent upbeat electronic)
- **Volume**: 14% (0.14) relative to VO
- **Fade out**: 2 seconds before video end
- **Fade in**: 0.5 seconds at start

### Audio Mix (3-input simplified pattern)

For most short-form videos, use this streamlined 3-input mix (video ambient + VO + music):

```bash
ffmpeg -y -i VIDEO -i VO -i MUSIC \
  -filter_complex "[0:a]volume=0.08[vid];[1:a]adelay=500|500,volume=1.0,apad[vo];[2:a]volume=0.14,afade=t=in:d=0.5,afade=t=out:st=28:d=2[music];[vid][vo][music]amix=inputs=3:duration=first[out]" \
  -map 0:v -map "[out]" -c:v copy -c:a aac -b:a 192k OUTPUT
```

Adjust `st=28` to match your video length minus 2 seconds for the music fade-out timing.

For the full 6-input mix with stadium SFX and sidechain ducking, see the "Quick start: 6-input audio mix" section above.

## Quality Rules

Hard-won rules from production experience. Violating any of these produces visibly amateur output.

### Visual quality

- **No black backgrounds** -- ALWAYS have video or image behind everything. Black screens look like render errors.
- **No cut faces** -- verify all screenshots show full player photos, not cropped at chin or forehead.
- **Minimum 80px margins** from all edges -- text or UI elements touching edges looks unprofessional.
- **Text shadow on everything**: `0 4px 20px rgba(0,0,0,0.9)` -- without shadows, white text disappears on light video frames.

### Content rules

- **No repeated B-roll** -- each video gets unique stock clips. Track usage in a clip inventory.
- **Real vendor logos only** -- source from vendor apple-touch-icon URLs, never use placeholder or AI-generated logos.
- **Labels appear for 3-5 seconds**, not the entire video duration. Persistent labels feel like watermarks.
- **Bullet points use emoji icons** (e.g., stadium, airplane, ticket, star), never plain text dash lists.

### Timing

- **Hook in first 1-3 seconds** -- no logo animations, no "hey guys"
- **CTA in final 3-5 seconds** -- URL + one sentence audio CTA
- **VO delay**: 500ms from video start (the `adelay=500|500` in the ffmpeg recipe)

## Publishing Schedule Template

Optimized posting schedule based on engagement data across 10 channels.

### Weekly cadence

| Day | Time (ET) | Platforms | Format | Notes |
|-----|-----------|-----------|--------|-------|
| **Saturday** | 2:00 PM | Instagram Reels + Threads | Vertical 30s | Peak weekend engagement window |
| **Saturday** | 6:00 PM | YouTube Shorts + Telegram | Vertical 30s | Evening scroll session |
| **Sunday** | 11:30 AM | Facebook + Discord + LinkedIn | Mixed format | Sunday morning catch-up browsing |
| **Tuesday** | 9:00 AM | LinkedIn | Landscape 30-45s | Professional audience, founder narrative framing |

### Format notes

- **Saturday drops** are product-first (demo, features, value prop)
- **Sunday drop** is community-oriented (ask for feedback, share behind-the-scenes)
- **Tuesday LinkedIn** is founder narrative (lessons learned, build-in-public, business insights)
- Stagger posts by 15+ minutes even within the same time slot to avoid API rate limits
- Schedule via Postiz API at least 2 hours before target time to allow for review

### Platform-specific timing overrides

- **X/Twitter**: Can post any day, engagement is less time-sensitive. Best: Tuesday-Thursday 9-11 AM ET. **Routes via Blotato (Postiz X removed 2026-05-15).**
- **TikTok**: Routes via Blotato (`POST /v2/posts`, `targetType:"tiktok"`). Best: Thursday-Saturday 7-9 PM ET.
- **Telegram**: Immediate delivery (no algorithm), so timing matters less. Batch with YouTube Shorts.

## Platform routing matrix (UPDATED 2026-05-15)

The single biggest gotcha in this pipeline: **which platform goes through which service.** Get this wrong and posts silently fail or hit the wrong account.

| Platform | Service | Endpoint | Why |
|---|---|---|---|
| LinkedIn (personal) | **Postiz** | `POST /api/public/v1/posts` w/ `who_can_reply_post` n/a; settings `{}` | OAuth working since 2026-05-03 |
| LinkedIn (Company Page) | manual / Blotato | n/a | Postiz only handles personal LI |
| **X / Twitter (all accounts)** | **Blotato (mandatory)** | `POST /v2/posts` w/ `targetType:"twitter"` | **Postiz X integration removed 2026-05-15.** Every X handle goes through Blotato. |
| Instagram (personal/business) | **Postiz** | `POST /api/public/v1/posts` w/ `settings: {post_type:"post"}` | Instagram-standalone or Instagram (FB Business) providers |
| Facebook Pages | **Postiz** | `POST /api/public/v1/posts` w/ `settings: {}` | Personal FB profile not supported — only Pages |
| Threads | **Postiz** | `POST /api/public/v1/posts` w/ `settings: {}` | OAuth tied to IG identity |
| **TikTok (all accounts)** | **Blotato (mandatory)** | `POST /v2/posts` w/ `targetType:"tiktok"` | Bypasses TikTok app-review approval. `tiktokpost` browser-skill is legacy fallback only |
| YouTube (Shorts + long-form) | **Postiz** | `POST /api/public/v1/posts` w/ `settings: {type:"public"\|"private"\|"unlisted", title:"...", tags:[]}` | Multi-channel inventory |
| Telegram | **Postiz** | `POST /api/public/v1/posts` w/ `settings: {}` | Anton AI Power channel |
| Discord | **Postiz** | `POST /api/public/v1/posts` w/ `settings: {channel:"#channel-name"}` | Requires `channel` field |
| Pinterest | **Postiz** | `POST /api/public/v1/posts` | Business accounts only |
| Bluesky | **Postiz** | `POST /api/public/v1/posts` | n/a |
| dev.to | **Postiz** | n/a | Long-form fallback |

**Quick decision rule:**
> If platform == "tiktok" OR platform == "x"/"twitter" → use **Blotato**.
> Everything else → use **Postiz**.

## Postiz schema gotchas (per-platform required `settings`)

Every Postiz `POST /api/public/v1/posts` payload MUST have:
- `type: "schedule"`
- `date: "ISO8601"`
- `shortLink: false`
- `tags: []` (top-level, NOT inside posts[].tags)
- `posts: [{integration: {id}, value: [{content, image:[{id, path}]}], settings: <platform-specific>}]`

Platform-specific `settings` (omit field → BadRequest 400):

| Platform | Required `settings` keys |
|---|---|
| LinkedIn | `{}` (empty OK) |
| Instagram (post or standalone) | `{"post_type": "post"}` (or `"story"`) |
| Facebook | `{}` (empty OK) |
| Threads | `{}` (empty OK) |
| Telegram | `{}` (empty OK) |
| Discord | `{"channel": "#channel-name"}` (required) |
| YouTube | `{"title": "<60chars", "type": "public"\|"private"\|"unlisted", "tags": [{label, value}, ...]}` |
| Pinterest | `{"title": "...", "board": "<board-name>"}` |

**For media:** `image[0]` MUST be `{id: <postiz_upload_id>, path: <postiz_cdn_url>}`. The `id` field is non-optional — Postiz rejects `{path: ...}` alone with "image.0.id must be a string".

## Social Channel Inventory

### Connected via Postiz (self-hosted at postiz.easychamp.com)
- Anton YouTube (@AntonAbyzov)
- Anton Instagram (@aabyzov)  *(instagram-standalone provider)*
- Anton LinkedIn (personal)
- Anton Telegram (@antonaipower)
- Anton Threads (@aabyzov)
- EasyChamp YouTube (@easychampinc)
- EasyChamp Instagram (@easychamp_inc)
- EasyChamp Facebook (page)
- EasyChamp Discord (channel TBD per post)
- Skillup Football YouTube (@skillupfootballapplication)
- Sketchmate IG / FB / YouTube
- Soothbee IG / FB / X(Soothbee) / YT / Pinterest

### Routes via Blotato (NOT Postiz)
- **Anton X/Twitter (@aabyzov)** — accountId `18001` (Postiz X removed 2026-05-15)
- EasyChamp X handles: `@EasyChampInc` (18005), `@EasyChampeSport` (18007), `@easychampfcpro` (18008)
- Anton TikTok (@antonabyzov, 40681)
- SkillUp Football TikTok (@footballskillup, 41891)
- EasyChamp TikTok (@easychamp_inc, 40691)
- Sketchmate TikTok (@sketchmate.net, 40690)
- SoothBee TikTok (@soothbee, 40825)
- Anton LinkedIn via Blotato (20855) — secondary/redundant; Postiz is the primary

### NOT connected (need OAuth or new app)
- Anton **personal Facebook** — NOT in Postiz. Connect via UI → +Add Channel → Facebook → OAuth.
- LinkedIn Company Pages — neither Postiz nor Blotato handles these
- Pinterest (Anton personal / EasyChamp) — only `babyanticry` (SoothBee) is connected
