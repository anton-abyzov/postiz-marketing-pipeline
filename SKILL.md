---
name: postiz-marketing-pipeline
version: 1.0.0
description: End-to-end short-form marketing pipeline for self-hosted Postiz - covers Postiz API automation (auth, scheduling, in-place media swap, multi-channel inventory), Remotion-based video composition with stock-footage layering, free-license stock sourcing (Pexels/Pixabay), AI asset generation (KIE AI, ElevenLabs Sarah voice), 6-input ffmpeg audio mixing, and the anti-patterns we learned the hard way (cross-posting brand pollution, Right of Publicity violations, LLM-fabricated tournament facts). Use when scheduling posts via the Postiz REST API, building short-form ad creative for TikTok/Reels/Shorts/X/LinkedIn, or coordinating multi-channel launch waves.
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
---

# Postiz Marketing Pipeline

Reusable playbook for shipping short-form video ads end-to-end through a self-hosted Postiz instance, distilled from a real World Cup 2026 launch run (10 channels, v5→v8 media swap, multiple paid-placement variants).

## When to use this skill

Activate when the user wants to:

- Schedule, update, swap-media, or delete posts via the **Postiz REST API** (the UI is fine for one-off edits, but anything bulk benefits from this).
- Build **short-form video ads** (TikTok/Reels/Shorts/X/LinkedIn) using Remotion with layered stock footage, AI voiceover, and platform-specific cuts.
- Source **free, commercially-licensable stock footage and B-roll** (Pexels/Pixabay) without falling into paid-only sources.
- Generate **AI assets** (images via KIE AI / Nano Banana, motion clips via Veo 3, VO via ElevenLabs Sarah voice).
- **Mix audio** for short-form (VO + music + crowd ambience + SFX with sidechain ducking and broadcast-safe limiting).
- Coordinate a **multi-channel launch wave** with channel-appropriate captions and an avoid-list of cross-pollinating channels.

## What this skill does NOT cover

- Hosted Postiz SaaS at `postiz.com` (this skill is tuned for self-hosted, but the API surface is identical — only the base URL changes).
- LinkedIn Company Pages — Postiz only handles personal LinkedIn. Use Blotato or post manually.
- TikTok scheduling — Postiz cannot schedule TikTok directly. Use the `tiktokpost` skill for browser-driven posting.
- Long-form (>3 min) YouTube — this skill is short-form only.
- Paid-ad campaign management (Google/Meta Ads Manager). The video assets are paid-placement-ready; the ops are out of scope.

## Hard-won anti-patterns (read these first)

1. **DON'T cross-post brand-A content to brand-B channels.** Even when it would technically reach more eyeballs, it pollutes the algorithmic signal of the off-brand channel. We shipped 11 launch posts and had to delete one when it landed on a sibling channel that wasn't ready to be associated with the new brand. Rule of thumb: if the channel hasn't yet launched its own marketing, never seed it with adjacent content.
2. **DON'T use celebrity likenesses without authorization.** Even AI-generated likenesses violate Right of Publicity (state-level, US) and Article 8 ECHR (EU). For sports content this means no real player faces, no team kits if you're representing them as players, and no announcer voices. Use generic personas (`Marcus, fan from Brooklyn`) and stylized stadium shots.
3. **DON'T trust LLM-claimed dates without 2-source verification.** We shipped a creative variant claiming "Argentina opens the World Cup at AT&T Stadium on June 11" — the actual opener was Mexico vs South Africa at Estadio Azteca, and Argentina's first match was June 16 in Kansas City. Both facts were trivially verifiable with one curl to Wikipedia or FIFA. The cost: re-rendering 5 variants under deadline pressure. **Always cross-check tournament/release/event dates with at least 2 independent primary sources before they bake into a video.** See `references/anti-patterns.md` for the full incident write-up.
4. **DON'T amend a published Postiz post via PUT** — the endpoint returns 404. Update is an idempotent `POST /api/posts` with the existing `id` inside `value[0].id`. See `references/postiz-api.md`.
5. **DON'T forget the `showorg` and `User-Agent` headers** on every Postiz API call. Without `showorg: true`, org-scoped endpoints return empty arrays silently. Without a Mozilla-style UA, Cloudflare WAF returns HTTP 403 with error 1010 — the API itself is reachable, you're just blocked at the edge.
6. **DON'T assume a 35 MB MP4 will publish to Discord.** Discord's non-Nitro upload limit is 25 MB. Re-encode for Discord specifically: `-c:v libx264 -preset slow -b:v 3500k -c:a aac -b:a 128k` brings a 45-second 1080×1920 video from 33 MB to ~21 MB without visible quality loss.

## Quick start: schedule one post via Postiz API

```bash
# 1. Auth — JWT lives in Set-Cookie, capture to a cookie jar
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

- `references/postiz-api.md` — Auth, channels, media upload, scheduling, in-place update, deletion, common errors, the `showorg` discovery story.
- `references/remotion-recipes.md` — Multi-layer composition, OffthreadVideo for inline stock, word-by-word VO reveals, glassmorphism cards, Lucide icons inlined, platform dimensions.
- `references/stock-sourcing.md` — Pexels/Pixabay license rules, what to skip (Pond5/Getty/Shutterstock/Adobe Stock), search heuristics, attribution rules.
- `references/ai-assets.md` — KIE AI gpt4o-image and Veo 3 prompts and pricing notes, ElevenLabs Sarah voice (`EXAVITQu4vr4xnSDxMaL`) settings, where API keys live.
- `references/audio-mix.md` — The 6-input ffmpeg recipe explained, loudness targets, sidechain ducking parameters, alimiter tuning.
- `references/multi-channel-strategy.md` — Channel inventory walk, caption variants per platform, the cross-post-pollution rule, audience-fit checklist.
- `references/anti-patterns.md` — Full write-up of the LLM-fabricated-fact incident, the cross-pollination delete, Right of Publicity, Discord size limit.

## Helper scripts

- `scripts/postiz-login.sh` — Login + cookie capture
- `scripts/postiz-list-channels.sh` — Channel inventory
- `scripts/postiz-swap-media.py` — In-place media swap across N posts
- `scripts/discord-encode.sh` — Re-encode 1080×1920 video to <25 MB for Discord

## Configuration

The skill expects these env vars (or equivalents in your secret store):

| Variable | Purpose |
|---|---|
| `POSTIZ_BASE_URL` | e.g. `https://postiz.yourdomain.com` |
| `POSTIZ_EMAIL` / `POSTIZ_PASSWORD` | Local auth (or use `provider=GITHUB`) |
| `KIE_AI_API_KEY` | For image and motion clip generation |
| `ELEVENLABS_API_KEY` | For Sarah voice TTS |
| `PEXELS_API_KEY` | Optional — for programmatic stock search |
| `PIXABAY_API_KEY` | Optional — same |

Never log or echo these values. Use `grep -q` to check existence; never `cat .env`.
