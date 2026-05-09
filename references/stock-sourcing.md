# Stock Footage Sourcing — Free + Commercial-Safe

For short-form ads we need footage we can use commercially without attribution baggage or licensing fees. Two sources hit that bar; everything else is paid.

## Use these (FREE + commercial)

### Pexels — https://www.pexels.com
- License: Pexels License — free for personal AND commercial use, no attribution required.
- Strong on: B-roll travel, urban, lifestyle, sports stadiums (mid-shots), product tabletop.
- Weak on: very specific events (e.g. "MetLife Stadium 2026"), celebrities (and good — we don't want them).
- API: free with key. `https://api.pexels.com/videos/search?query=stadium+aerial&per_page=20`.

### Pixabay — https://pixabay.com
- License: Pixabay Content License — free for personal AND commercial use, no attribution required.
- Strong on: motion graphics elements (intros/outros), abstract loops, drone city flyovers.
- Weak on: human faces (smaller library than Pexels).
- API: free with key. `https://pixabay.com/api/videos/?key=$KEY&q=stadium`.

**Both licenses cover modification, layering with brand graphics, paid-ad placement, and re-encoding.**

## Skip these (PAID, not worth it for short-form)

| Source | Why we skip |
|---|---|
| Pond5 | Per-clip pricing $20–$200. Better quality but the cost compounds across 10+ variants. |
| Getty Images / iStock | Subscription is fine if you already have one; pay-per-clip is brutal. Watermarks on previews are aggressive. |
| Shutterstock | Same model. Editorial-only footage of sports events is a TRAP — you can't use it for ads. |
| Adobe Stock | Subscription model. Quality is great but you'll burn through the monthly quota fast on multi-variant launches. |
| Storyblocks | Subscription, "unlimited" but with hidden per-format limits. Only if you already pay for it. |

## Editorial vs Commercial — important footnote

Stock libraries flag clips as "editorial only" when they show real branded venues, real player faces, real team kits in match. **Editorial clips cannot be used in advertising** even if you've paid the license fee. The video gets pulled (or you get sued).

Heuristics for "is this clip commercial-safe":
- ✅ Generic stadium architecture from outside, no logos visible
- ✅ Crowd shots from far enough that no individual is recognizable
- ✅ Generic sports field action with no team kits / faces in focus
- ⚠ Drone shots over a city — usually OK if no recognizable buildings dominate
- ❌ Identifiable logos or team kits
- ❌ Recognizable players or coaches
- ❌ Branded vehicles, branded merchandise close-up
- ❌ Anything labeled "editorial only"

When in doubt, blur or layer over the questionable element.

## Search heuristics that worked

For our World Cup launch, these query patterns produced the best results on Pexels/Pixabay:

| Need | Search query |
|---|---|
| Generic stadium aerial | "stadium aerial" / "soccer stadium aerial" |
| Crowd reaction (anonymous) | "stadium crowd cheering" / "fans cheering generic" |
| City flyover | "[city name] aerial drone" — Toronto, LA, NYC all have good Pexels coverage |
| Stadium ambience (audio) | "soccer crowd ambience" on Freesound (separate skill) |
| Travel: airport scene | "airport terminal walking" |
| Travel: subway/metro | "subway train interior" / "metro station" |
| Tabletop/lifestyle | "phone in hands" / "laptop on desk" |

Most queries return 50+ results. Filter by orientation (vertical for TikTok/Reels, horizontal for LinkedIn/YouTube preroll).

## Asset organization

Drop downloaded clips into `video/public/stock/` with naming convention:

```
video/public/stock/
├── stadium-aerial-pexels-12345.mp4
├── crowd-cheering-pixabay-67890.mp4
├── airport-terminal-pexels-22222.mp4
└── city-flyover-LA-pexels-33333.mp4
```

Source-suffix in the filename (`-pexels-` or `-pixabay-`) makes attribution lookup trivial later if you ever want to re-license, even though neither requires it.

## Audio: stadium ambience for the mix

Pexels and Pixabay are video-only. For audio (the 4 stadium-ambience drops in the audio mix recipe), use:

- **Freesound** — https://freesound.org — CC0 / CC-BY clips. Good for crowd roar, single-cheer, goal celebration.
- **Pixabay Audio** — https://pixabay.com/sound-effects — same license as Pixabay video, free for commercial.

Search "soccer crowd," "stadium roar," "goal celebration." Grab CC0-licensed clips when possible to avoid attribution requirements.
