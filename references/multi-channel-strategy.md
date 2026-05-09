# Multi-Channel Posting Strategy

How to walk channel inventory, write platform-tuned captions, and avoid cross-post pollution.

## Inventory walk

Always start by listing what's actually connected:

```bash
curl -sS -b cookies.txt \
  -H "showorg: true" -H "User-Agent: Mozilla/5.0" \
  "https://postiz.example.com/api/integrations/list" \
  | jq '[.[] | {id, name, providerIdentifier, username}]'
```

You'll typically see a mix of:
- **Personal channels** — founder's own X, LinkedIn, IG, Threads, YouTube
- **Brand A channels** — the product you're launching
- **Brand B/C channels** — sibling products with their own audiences

Your launch wave should hit a deliberate subset. Don't post to all 17 connected channels — most of the time half are wrong-audience.

## Channel triage

For each connected channel, ask:

1. **Does the audience care about this launch?** A WC26 launch on a baby-monitor app's IG is noise.
2. **Is this channel ready to be associated with the new brand?** If brand B hasn't launched its own marketing yet, posting brand A's content on it is brand-dilution before brand B has a chance to define itself.
3. **Does the platform's algorithm favor or punish video format?** Pinterest + portrait video = good. LinkedIn + portrait = looks weird, use horizontal.
4. **Does the platform favor founder-narrative or product-focused?** LinkedIn = founder. TikTok = product. X = either, but keep it tight.

## Caption variants per platform

The same video gets a different caption per channel. Match tone, hashtag style, and length to platform norms:

### Personal X
> Built an AI travel concierge for the FIFA World Cup 2026 in 14 days using Claude Code + Remotion. Free at example.com. First 1,000 founders get Pro for $3.49/mo for life. 45-second demo:

Founder voice. Specific stack mention. Concrete pricing. Builds-in-public energy.

### Personal IG / Threads
> AI just planned my whole World Cup trip. 30 seconds. Free at example.com. Founders save 50% for life. #WC26 #WorldCup2026 #AItravel #BuildInPublic #FIFA

Personal, first-person. Hashtags front-load discovery. No links in caption (IG strips them anyway — link in bio).

### Personal LinkedIn
> Shipped example.com in 14 days using AI agents end-to-end. Stripe + iOS IAP wired in one session. Demo + lessons learned below.

Founder reflection. Specific technical achievement. Implies a thread of lessons in the comments. No emoji.

### Personal YouTube
> I built an AI World Cup concierge in 14 days. Demo:

Title-style. The video does the heavy lifting on YouTube; caption just confirms what they're about to watch.

### Personal Telegram
> Shipped: example.com — AI travel concierge for the World Cup. Free trip planner. First 1,000 founders get Pro for $3.49/mo lifetime.

Telegram audience is high-context (already opted in). Drop the marketing fluff, lead with the news.

### Brand YouTube
> Plan your World Cup 2026 trip in 30 seconds. AI concierge, full itinerary, ticket comparison, 16 host cities. Free at example.com. Pro $3.49/mo for the first 1,000 founders. #WC26 #WorldCup2026 #FIFA #SoccerTravel

Product framing (not founder voice). Bullet-list of features. SEO-friendly hashtags.

### Brand IG
> Plan your World Cup 2026 trip in 30 seconds 🌎⚽ AI concierge · Full itinerary · Ticket comparison · 16 host cities. Free at example.com. Pro $3.49/mo for the first 1,000 founders. #WC26 #WorldCup2026 #FIFA #SoccerTravel

Same content as YouTube but with emoji and middot separators (IG-native style).

### Brand FB
Same as YouTube. Facebook captions can be longer; people who scroll FB read more text.

### Brand Discord
> Hey @everyone — soft launch of WC26 Travel: free AI itinerary planner for the World Cup. Try example.com and tell me what breaks. Founders deal: $3.49/mo Pro for life, first 1,000.

Discord is a community space, not a feed. Use `@everyone` only when it genuinely warrants it (a launch does). Direct ask for feedback.

### Brand LinkedIn
NOTE: Postiz only handles personal LinkedIn. For LinkedIn Company Pages, you need Blotato or manual posting. Don't try to backdoor it through personal — it dilutes both.

## Schedule windows that worked

For our launch (US-centric audience, May 2026), these windows hit well:

| Window | Platform | Why |
|---|---|---|
| Fri 7:30 PM ET | Anton X / IG / Threads / YT | Friday evening discovery, audience scrolling for weekend plans |
| Fri 8:00 PM ET | Anton Telegram | Power-users in EU still online |
| Fri 8:30 PM ET | Brand Discord | Community engagement window |
| Sat 11:30 AM ET | Brand YT / IG / FB | Saturday morning brand-content browsing |
| Tue 9:00 AM ET | Anton LinkedIn | Tuesday morning is LinkedIn's peak — Mon is too back-to-work, mid-week dilutes |

If you're launching globally, stagger by primary audience timezone — don't force a single global drop.

## Cross-post pollution — the rule

**Do not post brand A's content to brand B's channel before brand B has launched its own marketing.**

Why this matters:
- Algorithms learn what each channel is "about" from its content. Mixing brands trains the algo to show your channel to the wrong audience permanently.
- Followers signed up for brand B, not brand A. You break the implicit contract.
- When brand B does launch later, its own content competes against the now-confused signal.

We made this mistake once (posted brand A launch content to brand B's YouTube). Caught it after the swap, deleted via `DELETE /api/posts/{group_uuid}`. Final scope went from 11 → 10 active posts.

## Cross-post pollution — the safe form

It's fine to **mention** another brand's launch on the founder's personal channels. Personal channels don't have algorithmic-purity concerns because they're already a melting pot of the founder's life. So: yes to "Anton's IG announcing brand A," no to "brand B's IG announcing brand A."

## Audience-fit checklist before posting

- [ ] Audience demographic matches (e.g. soccer fans for sports content, parents for family content)
- [ ] Channel has posted within the last 30 days (otherwise the algo treats your post as a re-awakening attempt and demotes)
- [ ] Caption length fits platform (X 280, IG/FB unlimited, LinkedIn 3000, YouTube unlimited)
- [ ] Hashtag count fits (X 1–2, IG 5–10, LinkedIn 3–5, FB 1–3, YT 5–10)
- [ ] Link strategy (IG/Threads can't link in caption — use link in bio; X/LinkedIn/FB allow direct links)
- [ ] Mentions handled (`@everyone` ok in Discord launch, never in regular posts)
- [ ] Video dimension matches platform's preferred (vertical for short-form mobile, horizontal for LinkedIn/YT preroll)
