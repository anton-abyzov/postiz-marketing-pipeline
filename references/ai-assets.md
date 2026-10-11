# AI assets: voice, and where image and video generation lives

Images and video clips come from Kie via the `kie-gemini-omni` skill (`/api/v1/jobs/createTask` + `/recordInfo`; GPT Image 2 for frames with text, Nano Banana Pro for text-free frames, Seedance 2.0 for video). Model choice for social posts is in `social-media-posting`. Never prompt for real names, celebrity likenesses, copyrighted characters or trademarked logos.

## ElevenLabs voiceover

Sarah, `EXAVITQu4vr4xnSDxMaL`, is the default narrator for every launch video.

```bash
curl -sS -X POST "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -H "Accept: audio/mpeg" \
  -d '{"text":"...","model_id":"eleven_turbo_v2_5",
       "voice_settings":{"stability":0.55,"similarity_boost":0.75,"style":0.15,"use_speaker_boost":true}}' \
  -o vo.mp3
```

- Russian: `model_id: eleven_multilingual_v2` (turbo garbles Russian).
- Alternatives: Adam `pNInz6obpgDQGcFmaJgB` (deeper male, "founder log"), Antoni `ErXwobaYiN019PkySvjV` (casual male). Confirm the IDs with `GET /v1/voices` on the account.
- Music bed: `POST /v1/music` with `{prompt, music_length_ms}`, instrumental, ducked about 0.16 under the VO.

## Keys

`ELEVENLABS_API_KEY`, `KIE_API_KEY`, `PEXELS_API_KEY` come from the env or a personal `.env`, the Obsidian vault, or the macOS Keychain (`security find-generic-password -s <name> -w`). Check they exist with `grep -q` or `test -n`; never `cat .env` or echo a value. The Higgsfield AI (video generation) Full Access key is in the Obsidian vault. If a key is missing, ask Anton before generating.

A full 10-variant launch (about 30 stills, 6 clips, 10 one-minute VOs) cost under $10 in 2026-05.
