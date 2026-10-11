# Audio mix: VO + ducked music + stadium ambience

The 6-input recipe for paid placement. For organic posts, the 3-input mix in SKILL.md is enough.

```bash
ffmpeg -y -i vo-sarah.mp3 -i music-bed.mp3 -i stadium-roar-1.wav -i stadium-roar-2.wav -i stadium-cheer.wav -i goal-celebration.wav \
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
ffmpeg -y -i video-silent.mp4 -i mixed.aac -c:v copy -c:a aac -shortest video-final.mp4
```

- The music sits at 0.25 and ducks 8:1 while the VO speaks. Attack 20ms catches consonants; release 400ms avoids pumping. As written, `sidechaincompress` keys off its second input; if your ffmpeg build behaves the other way, swap the input order.
- Place the ambience drops (`adelay` in ms) on the visual high points, between VO clauses, never mid-sentence. Keep their volume at 0.4–0.7.
- `duration=first` trims to the VO+music length. Always keep both `alimiter` and `loudnorm`.
- Every target here is -14 LUFS / -1.5 dBTP (TikTok, Reels, Shorts, LinkedIn, X, YouTube). Podcast cuts use `I=-16`.
- Mix too loud: drop the music to 0.20 or raise the ratio to 12.

Check the result:

```bash
ffmpeg -i mixed.aac -af "loudnorm=print_format=summary" -f null - 2>&1 | grep -E "Input|Output"
ffmpeg -i mixed.aac -af astats=metadata=1:reset=1 -f null - 2>&1 | grep -E "Peak level|Crest"
```

The integrated loudness should read about -14 LUFS with no clipping.
