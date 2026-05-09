# Remotion Recipes — Short-Form Marketing Cuts

Recipes from a real launch run with Remotion 4.0.457. All examples are pure JSX/CSS — no external libs beyond `@remotion/google-fonts` and `lucide-react` (and only for icon SVG paths, which we inline).

## Platform dimension presets

| Platform | Width × Height | FPS | Sweet-spot duration |
|---|---|---|---|
| TikTok For-You | 1080 × 1920 | 30 | 3s (hook) or 15s (punch) |
| Instagram Reels | 1080 × 1920 | 30 | 30s |
| Instagram Story | 1080 × 1920 | 30 | 15s (sticker zone aware) |
| YouTube Shorts | 1080 × 1920 | 30 | 60s max |
| YouTube Pre-Roll (skippable) | 1920 × 1080 | 30 | 15s, brand promise in <5s |
| X Native Video | 1080 × 1080 (square) | 30 | 45s |
| LinkedIn | 1920 × 1080 (horizontal) | 30 | 60s |
| Facebook Reels | 1080 × 1920 | 30 | 30s |
| Pinterest Idea Pin | 1080 × 1920 | 30 | 15s, text-overlay-heavy |

Register all of them in `Root.tsx`:

```tsx
<Composition id="V1TikTokHook"  component={V1TikTokHook}  durationInFrames={90}   fps={30} width={1080} height={1920} />
<Composition id="V8LinkedIn"     component={V8LinkedIn}     durationInFrames={1800} fps={30} width={1920} height={1080} />
{/* ... */}
```

## Multi-layer composition (video on video)

`OffthreadVideo` is the right primitive for inline stock B-roll — it streams from disk on demand, doesn't try to decode the whole clip into memory.

```tsx
import {AbsoluteFill, OffthreadVideo, Sequence, staticFile} from 'remotion';

export const Layered: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    {/* Layer 0: aerial stadium B-roll, full-bleed, looped */}
    <OffthreadVideo
      src={staticFile('stock/stadium-aerial.mp4')}
      muted
      style={{width: '100%', height: '100%', objectFit: 'cover'}}
    />

    {/* Layer 1: 12s of crowd reaction footage on top of the aerial */}
    <Sequence from={120} durationInFrames={360}>
      <OffthreadVideo
        src={staticFile('stock/crowd-reaction.mp4')}
        muted
        style={{
          position: 'absolute', bottom: 80, right: 80,
          width: 480, height: 320, borderRadius: 24,
          border: '4px solid rgba(255,255,255,0.2)',
          boxShadow: '0 20px 60px rgba(0,0,0,0.6)',
          objectFit: 'cover',
        }}
      />
    </Sequence>

    {/* Layer 2: glassmorphism caption card */}
    <Sequence from={60}>
      <CaptionCard text="The World Cup is here." />
    </Sequence>
  </AbsoluteFill>
);
```

Don't use `<video>` directly in Remotion — it doesn't seek correctly during render. Always `OffthreadVideo` (or `Video` for short audio-bearing clips that need synced audio).

## Word-by-word reveal timed to VO

Use `interpolate` with frame ranges per word. The trick is computing each word's start frame from a constant per-word duration:

```tsx
import {useCurrentFrame, interpolate} from 'remotion';

const WordReveal: React.FC<{words: string[]; startFrame: number; framesPerWord: number}> =
  ({words, startFrame, framesPerWord}) => {
  const frame = useCurrentFrame();
  return (
    <h1 style={{fontSize: 96, fontWeight: 800, color: 'white'}}>
      {words.map((w, i) => {
        const wordStart = startFrame + i * framesPerWord;
        const opacity = interpolate(
          frame,
          [wordStart, wordStart + 8],
          [0, 1],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
        );
        const y = interpolate(
          frame,
          [wordStart, wordStart + 12],
          [40, 0],
          {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
        );
        return (
          <span key={i} style={{display: 'inline-block', opacity, transform: `translateY(${y}px)`, marginRight: 18}}>
            {w}
          </span>
        );
      })}
    </h1>
  );
};
```

To time perfectly with VO: render the VO MP3 first, transcribe with `ffprobe -show_entries packet=pts_time` or read the Whisper word timestamps, then align `startFrame + i * framesPerWord` to the VO's word onsets.

## Glassmorphism card

Standard pattern for caption boxes that float over B-roll without burying it:

```tsx
const Card: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{
    background: 'rgba(24, 24, 27, 0.85)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    border: '1px solid rgba(225, 29, 72, 0.2)',
    borderRadius: 24,
    padding: '32px 40px',
    boxShadow: '0 40px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05)',
  }}>
    {children}
  </div>
);
```

If you hit perf issues during render (rare, but happens with large compositions), drop `backdropFilter` and use a flat `rgba(24,24,27,0.92)` — the visual difference is small.

## Lucide icons inlined

Import the icon components but read their SVG paths and inline them. This avoids the runtime cost of mounting React components for icons:

```tsx
// Inline the path data from `lucide-static` or copy from lucide.dev
const PlaneIcon: React.FC<{size?: number; color?: string}> = ({size = 32, color = '#fbbf24'}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>
  </svg>
);
```

For sets of icons, generate a barrel from `lucide-static/icons/*.svg` at build time.

## Ken Burns (slow-zoom)

For static image beats — gives them just enough motion to not feel dead:

```tsx
import {useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

const KenBurns: React.FC<{src: string}> = ({src}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const scale = interpolate(frame, [0, durationInFrames], [1.0, 1.08]);
  const x = interpolate(frame, [0, durationInFrames], [0, -20]);

  return (
    <img src={src} style={{
      width: '100%', height: '100%', objectFit: 'cover',
      transform: `scale(${scale}) translateX(${x}px)`,
      transformOrigin: 'center',
    }} />
  );
};
```

Subtle. 1.0 → 1.08 over the whole beat is the right amount. Anything more reads as "we don't have enough footage."

## Phone-frame mockup (for app demos)

```tsx
const PhoneFrame: React.FC<{children: React.ReactNode; scale?: number}> = ({children, scale = 1}) => (
  <div style={{
    transform: `scale(${scale})`,
    width: 600, height: 1280,
    border: '8px solid #18181b',
    borderRadius: 56,
    overflow: 'hidden',
    boxShadow: '0 40px 80px rgba(0,0,0,0.6)',
    position: 'relative',
  }}>
    {/* dynamic island */}
    <div style={{
      position: 'absolute', top: 16, left: '50%', transform: 'translateX(-50%)',
      width: 120, height: 32, borderRadius: 16, background: '#000', zIndex: 10,
    }} />
    <div style={{width: '100%', height: '100%', borderRadius: 48, overflow: 'hidden'}}>
      {children}
    </div>
  </div>
);
```

## Font loading

`@remotion/google-fonts` + `delayRender`:

```tsx
import {loadFont} from '@remotion/google-fonts/Inter';
import {delayRender, continueRender} from 'remotion';

const handle = delayRender();
const {fontFamily} = loadFont();
loadFont().then(() => continueRender(handle));

// then style={{fontFamily}}
```

If you forget this, type renders in a system fallback and looks generic.

## Render commands

```bash
# Single composition
npx remotion render src/index.ts MyComposition out/video.mp4 --concurrency=4

# All compositions
npx remotion render src/index.ts --all

# Preview frame at frame 120
npx remotion still src/index.ts MyComposition out/preview.png --frame=120

# Studio (interactive)
npx remotion studio
```

`--concurrency=4` is the safe default on M-series Macs. Bump to 8 on a workstation.

## Output sizes (45-second 1080×1920)

Without optimization, `--codec=h264` defaults give ~30–35 MB. To target Discord's 25 MB ceiling, pass through ffmpeg post-render:

```bash
ffmpeg -y -i out/source.mp4 \
  -c:v libx264 -preset slow -b:v 3500k \
  -c:a aac -b:a 128k \
  out/source-discord.mp4
```

This is the recipe in `scripts/discord-encode.sh`. Visual quality drop at 3500k for 1080×1920 is imperceptible to the audience.
