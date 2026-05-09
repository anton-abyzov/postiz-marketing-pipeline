# AI-Generated Assets — Images, Motion, Voice

For short-form ads we generate three categories of assets with AI: still images (personas, scenes), motion clips (3–10s b-roll filler), and voiceover.

## Stills — KIE AI gpt4o-image (Nano Banana Pro)

KIE AI is a paid wrapper around `gpt-image-1` and Google's Nano Banana Pro (Gemini 3 Pro Image). The wrapper handles upscaling, retries, and seed pinning.

Pricing as of 2026-05: ~$0.04 per 1080×1920 image. Cheap enough that you can iterate prompt → result → re-prompt 5 times for under a quarter.

```bash
curl -sS -X POST "https://api.kie.ai/v1/images/generate" \
  -H "Authorization: Bearer $KIE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt4o-image",
    "prompt": "Documentary photo of a 30-year-old man in a navy USA soccer jersey, sitting at a kitchen table in a Brooklyn apartment, looking at his phone, soft golden-hour lighting from a window. Mid-shot, eye-level. Realistic skin texture, no cartoon style.",
    "size": "1024x1792",
    "quality": "hd",
    "n": 1
  }'
```

### Prompt patterns that worked

For personas (the "Marcus" character):
- `Documentary photo of a [age] [demographic] in [outfit], [location], [pose/action], [lighting]. Mid-shot, eye-level. Realistic skin texture, no cartoon style.`

For scenes (stadium, hotel, transit):
- `Cinematic [time-of-day] photo of [location], [weather], [composition framing]. No text, no logos.`

For UI mockups (when screenshots aren't available):
- `Phone screen mockup, dark mode app interface, [feature description]. Inter font, rose-red primary color (#e11d48), gold accents (#fbbf24). Minimal, modern.`

### What NOT to prompt

- Specific celebrity names or "in the style of [celebrity]" — both Right of Publicity issues and KIE will quietly refuse or generate uncanny-valley near-misses
- Specific copyrighted characters (Mickey Mouse, Pokemon, etc.)
- Real player names — generates uncanny-valley faces, plus rights issues
- Trademarked logos — same

### Iteration loop

1. Generate 4 variants at quality `standard` (~$0.02 each, $0.08 total)
2. Pick the closest match
3. Re-generate at quality `hd` with the winner's seed (`seed` field in the response)
4. Optionally upscale to 2160×3840 with `model: "upscale"` if you need it for big-screen rendering

## Motion clips — Veo 3 (via KIE AI)

Google's Veo 3 model generates 5–10s motion clips at 1080p. Routed through KIE AI for billing convenience.

Pricing: ~$0.50 per 8-second clip. Used sparingly — one or two motion-cap inserts per variant.

```bash
curl -sS -X POST "https://api.kie.ai/v1/video/generate" \
  -H "Authorization: Bearer $KIE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "veo-3",
    "prompt": "Camera flying low over a packed stadium crowd at night. Floodlights bright, confetti falling. Slow forward motion, cinematic anamorphic look.",
    "duration": 8,
    "aspect_ratio": "9:16"
  }'
```

Veo 3 is strong on:
- Architectural fly-throughs (stadium, city)
- Generic crowd dynamics (cheering, raising arms)
- Object motion (ball, plane, train)

Veo 3 is weak on:
- Specific human faces — they morph between frames
- Text on screen — hallucinated and changes
- Brand logos — same

For anything with a recognizable face, use a Pexels stock clip instead. Veo for atmosphere, stock for people.

## Voiceover — ElevenLabs Sarah voice

The Sarah voice (`EXAVITQu4vr4xnSDxMaL`) is ElevenLabs' default-female narrator. Warm, trustworthy, "tech podcast host" energy. Lands well on launch videos.

```bash
curl -sS -X POST "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: audio/mpeg" \
  -d '{
    "text": "The World Cup is here. Forty-eight teams. Sixteen cities. Five weeks.",
    "model_id": "eleven_turbo_v2_5",
    "voice_settings": {
      "stability": 0.55,
      "similarity_boost": 0.75,
      "style": 0.15,
      "use_speaker_boost": true
    }
  }' \
  -o vo-sarah.mp3
```

### Voice settings dial-in

| Setting | What it does | Sweet spot for ads |
|---|---|---|
| `stability` | Lower = more expressive, higher = more consistent | 0.5–0.6 for ads (some emotion, but reliable) |
| `similarity_boost` | How closely to match the trained voice | 0.7–0.8 |
| `style` | Stylistic exaggeration | 0.1–0.2 (subtle for narration) |
| `use_speaker_boost` | Adds presence | true |

### Other voices worth trying

- **Adam** (`pNInz6obpgDQGcFmaJgB`) — male narrator, deeper. Good for "founder log" tone.
- **Antoni** (`ErXwobaYiN019PkySvjV`) — male, casual, podcast energy.
- **Bella** (`EXAVITQu4vr4xnSDxMaL` — same as Sarah in some accounts) — confirm voice ID by listing `/v1/voices` in your account.

### Pricing

Eleven Turbo v2.5: ~$0.30 per 1000 characters generated. A 60-second VO is ~120 words ≈ 800 chars ≈ $0.24. Cheap.

## Where to find API keys

User keeps API keys in:
- An Obsidian vault (PARA structure under "Resources/API Keys" or similar)
- A `.env` file at repo root (NOT for project secrets — for personal AI keys: `KIE_AI_API_KEY`, `ELEVENLABS_API_KEY`, `PEXELS_API_KEY`)
- macOS Keychain via `security find-generic-password -s "kieai" -w`

Always check existence with `grep -q` (never `grep` without `-q`, never `cat .env`). If a key isn't found in the expected place, ASK the user — don't generate without confirmation.

## Cost ceiling for a typical 10-variant launch

| Asset type | Quantity | Unit cost | Total |
|---|---|---|---|
| KIE AI stills (personas + scenes) | 30 | $0.04 | $1.20 |
| Veo 3 motion clips | 6 | $0.50 | $3.00 |
| ElevenLabs VO | 10 × 60s | $0.24 | $2.40 |
| **TOTAL** | | | **~$6.60** |

Add ~$0.50 buffer for re-rolls. The full creative budget for a 10-variant launch wave fits inside a $10 ceiling. The bulk of the cost is your time, not the AI.
