# Audio Mix Recipe — VO + Music + Stadium Ambience

The 6-input ffmpeg pattern for short-form ad audio. Produces a broadcast-safe mix that sounds professional on phone speakers without clipping when normalized by social platforms.

## The full recipe

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

Then mux:

```bash
ffmpeg -y -i video-silent.mp4 -i mixed.aac -c:v copy -c:a aac -shortest video-final.mp4
```

## Stage-by-stage explanation

### Stage 1: Music ducking (sidechain compression)

```
[1:a]volume=0.25,sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[duck1];
[duck1][0:a]amix=inputs=2:duration=longest:weights=1 1[mix1];
```

- `volume=0.25` — drops the music bed to 25% of source level so it sits behind the VO.
- `sidechaincompress` — when the VO (sidechain key) goes above the threshold, the compressor squeezes the music. Think: music auto-dips whenever Sarah talks, comes back up between sentences.
  - `threshold=0.05` — VO threshold for triggering ducking
  - `ratio=8` — aggressive 8:1 compression when triggered
  - `attack=20` — 20ms attack — fast enough to catch consonants
  - `release=400` — 400ms release — slow enough that the music doesn't pump audibly between words
- `amix` then sums the ducked music with the VO at equal weights.

**Note**: The `sidechaincompress` filter in modern ffmpeg actually keys off the second input by default. If your version inverts that, swap the input order.

### Stage 2: Time-stamped ambience drops

```
[2:a]adelay=8000|8000,volume=0.6[s1];
[3:a]adelay=22000|22000,volume=0.5[s2];
[4:a]adelay=35000|35000,volume=0.6[s3];
[5:a]adelay=42000|42000,volume=0.7[s4];
```

Four stadium-ambience drops at specific times in the video:
- `s1` at 8s — first stadium-roar drop, after the hook
- `s2` at 22s — second roar, mid-demo
- `s3` at 35s — cheer, during feature reveal
- `s4` at 42s — goal celebration, at the CTA

`adelay=8000|8000` delays both stereo channels by 8000ms (8s). Volume normalizes so each drop sits comfortably.

Adjust drop times to match your beat sheet. The pattern: drop ambience on every visual high point so the audio reinforces what the eye sees.

### Stage 3: Final sum

```
[mix1][s1][s2][s3][s4]amix=inputs=5:duration=first[premix];
```

5-way amix: VO+music + 4 ambience drops. `duration=first` truncates to the VO+music length so trailing silence doesn't pad out the video.

### Stage 4: Mastering

```
[premix]alimiter=limit=0.95,loudnorm=I=-14:LRA=7:tp=-1.5[out]
```

- `alimiter=limit=0.95` — brick-wall limiter so peaks never exceed -0.5 dBFS
- `loudnorm=I=-14:LRA=7:tp=-1.5` — EBU R128 normalization to -14 LUFS integrated, 7 LU range, -1.5 dBTP true peak. This is the industry-standard target for streaming and matches what Spotify/YouTube/TikTok normalize to internally.

## Loudness targets per platform

| Platform | Target LUFS | True Peak |
|---|---|---|
| TikTok / Reels / Shorts | -14 LUFS | -1.5 dBTP |
| LinkedIn / X | -14 LUFS | -1.5 dBTP |
| YouTube long-form | -14 LUFS | -1.5 dBTP |
| Spotify (if cross-posting podcast cuts) | -14 LUFS | -1.0 dBTP |

The above recipe is tuned for -14 LUFS. If you need -16 LUFS (some podcast networks), change `I=-14` to `I=-16`.

## Common mixing mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Music too loud | VO gets buried, viewer turns off audio | Drop `volume=0.25` to `0.20` or harden the sidechain ratio to `12` |
| No ducking | Music + VO compete, both feel muddy | Add the sidechaincompress as in Stage 1 |
| Ambience drops too loud | Ambience feels foreground, fights with VO | Drop ambience volumes to 0.4–0.5 |
| Skipping limiter | Peaks clip when platform normalizes | Always include `alimiter` in the chain |
| Skipping loudnorm | Mix is quieter than other ads, gets ignored | Always include `loudnorm` |
| Mismatched ambience timing | Ambience hits while VO is mid-sentence | Move drops to fit between VO clauses (read the VO transcript, place between commas/periods) |

## Quick-validate the output

```bash
# Check loudness
ffmpeg -i mixed.aac -af "loudnorm=print_format=summary" -f null - 2>&1 | grep -E "Input|Output"

# Look for clipping
ffmpeg -i mixed.aac -af astats=metadata=1:reset=1 -f null - 2>&1 | grep -E "Peak level|Crest"
```

If `Input Integrated` is around -14 LUFS and no clipping is reported, you're good.

## When to skip the audio mix

For a quick organic post that's not paid placement, use just VO + music with `amix` at default weights. Skip the ambience drops and the loudnorm — the platform's auto-normalization will be fine.

For paid placement (where the ad runs against premium content), do the full recipe. Audience listens muted on auto-play but unmutes good ones, and the difference in mix quality is what makes them unmute.
