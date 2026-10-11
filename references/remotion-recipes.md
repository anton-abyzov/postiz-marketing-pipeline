# Remotion notes for short-form cuts

General Remotion practice is in the `remotion-best-practices` skill. These notes are the settings this pipeline relies on.

## Dimension presets (30 fps)

| Placement | Size | Length that worked |
|---|---|---|
| TikTok For You | 1080x1920 | 3s hook or 15s punch |
| Instagram Reels / Facebook Reels | 1080x1920 | 30s |
| Instagram Story | 1080x1920 | 15s, keep clear of the sticker zone |
| YouTube Shorts | 1080x1920 | ≤60s |
| YouTube pre-roll | 1920x1080 | 15s, brand promise in under 5s |
| X native | 1080x1080 | 45s |
| LinkedIn | 1920x1080 | 60s |
| Pinterest Idea Pin | 1080x1920 | 15s, heavy text overlay |

Register one `<Composition>` per variant in `Root.tsx`.

## Gotchas

- Use `OffthreadVideo` for stock layers. Plain `<video>` doesn't seek correctly during render; `Video` is only for short clips whose audio must stay in sync.
- Load fonts through `@remotion/google-fonts` with `delayRender`/`continueRender`, or the render falls back to a system font.
- Ken Burns: scale 1.0 → 1.08 over the beat, nothing more.
- If `backdropFilter` slows a render, switch to a flat `rgba(24,24,27,0.92)`.
- Inline Lucide icon SVG paths instead of mounting the components.
- To time word-by-word reveals, render the VO first and align each word's start frame to the Whisper word timestamps.
- `npx remotion render src/index.ts <Comp> out/x.mp4 --concurrency=4` (M-series; 8 on a workstation). Use `npx remotion still ... --frame=120` to preview a frame.
- The default h264 output for 45s at 1080x1920 is 30–35 MB; use `scripts/discord-encode.sh` to bring it under 25 MB for Discord.
