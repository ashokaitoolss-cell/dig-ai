# dig.ai — design moodboard

*Phase 2 design direction.*

---

## REVISION 2 — Sazabi theme (current direction)

Owner directive: theme the app like [sazabi.com](https://www.sazabi.com/)
("just the theme" — app structure unchanged). Tokens extracted directly from
Sazabi's shipped CSS (`--background`, `--card-dark`, `--primary`, etc.).

### Thesis (revised)

dig.ai is a tactical launch console: a green-cast near-black surface where
every launch reads like an incoming signal. Condensed uppercase display type
(Teko) carries the headline, monospace uppercase labels (JetBrains Mono) carry
all metadata, and one signal red — Sazabi's `#FF0027` — is rationed to what's
new, hot, or active. Cards are hairline-framed panels with a chamfered corner,
HUD-style: felt as instrumentation, not decoration.

### Color tokens (from sazabi.com CSS)

```css
--bg:            #010401;   /* page — near-black, faint green cast */
--card:          #080c0b;   /* card panel (Sazabi --card-dark) */
--card-2:        #0d1110;   /* chips, badges, inputs (--card-secondary) */
--hairline:      rgba(255,255,255,0.10);  /* --border */
--border-solid:  #4f5553;   /* rare emphasized edge */

--text-high:     #fafafa;   /* headlines (--foreground) */
--text-body:     #b8c6c2;   /* summaries — sage gray (--card-foreground) */
--text-meta:     #808987;   /* datelines, quiet labels (--muted) */

--red:           #ff0027;   /* THE accent (--primary): active chip, NEW,
                               relevance ≥ 8, wordmark dot */
--red-dim:       #710515;   /* pressed red (--primary-dimmed) */
--sage:          #dce8e4;   /* secondary accent, sparing (--secondary-accent) */
--success:       #00d294;   /* status only */
```

Per-category accent hues from Revision 1 are dropped — the Sazabi theme is
monochrome + red. Categories differentiate by emoji + mono label only.

### Typography (Sazabi stack, Google Fonts)

| Role | Face | Size / line | Weight | Case |
|---|---|---|---|---|
| Headline | Teko | 38px / 1.02 | 500 | UPPERCASE |
| Summary | Spline Sans | 15.5px / 1.6 | 400 | sentence |
| Meta / chips / badges | JetBrains Mono | 11px / 1.2 | 500 | UPPERCASE, +0.06em |
| Wordmark | JetBrains Mono | 18px | 700 | `dig` white + `.` red |

### Surface language

- Cards: `--card` fill, 1px `--hairline` frame, **18px chamfer cut on the
  top-right corner** (clip-path), radius 4px elsewhere — Sazabi's cut-corner
  signature. No shadows.
- Unread cards get a 6px red corner dot beside the chamfer + mono `NEW`.
- Relevance badge: mono `REL 08`, red at ≥ 8, muted otherwise.
- Chips: rectangular, `--card-2` fill, hairline frame, small chamfer; active
  chip = red fill, `#fafafa` text.
- Everything else from Revision 1 still stands: elevation by lightness, no
  gradients/glass/blur, ≤300ms motion, generous dark gutters, whole card =
  one tap target.

---

## REVISION 1 — editorial DM Sans (superseded, kept for reference)

*Note: `moodboard/` was empty at research time, so this direction came from
the web research below.*

## Design thesis

dig.ai is a private editorial wire service for one reader: every launch gets a
full dark screen where **type does all the design work** — one big confident
headline, two quiet sentences, and a whisper of metadata. Color is rationed to
a single desaturated category accent per card, so after a week of use you read
the category from the corner of your eye before you read a word. Nothing on
the card competes with the news.

---

## Research observations (what informed this)

1. **Inshorts card anatomy** — one story per full card, hard separation between
   headline / summary / metadata zones; its known failures are small touch
   targets and banner clutter (puzzle/quote-of-the-day), so dig.ai has zero
   non-content elements on cards. *([Inshorts UI/UX case study](https://medium.com/design-bootcamp/inshorts-app-ui-ux-case-study-d94e0047b015))*
2. **Inshorts usability finding** — body text "needed to be a bit bigger";
   don't go below ~15px body on a phone. *(same case study)*
3. **Artifact** — black-and-white as the brand, deliberately "bland" iconography,
   the content IS the interface; its dark theme is high-contrast and total
   (every surface turns dark). dig.ai copies the restraint, not the grayscale —
   one accent hue per category. *([Artifact guide](https://interestingengineering.com/culture/the-artifact-news-app-guide), [Artifact homepage redesign](https://medium.com/artifact-news/our-new-artifact-homepage-c3e3a8cfecae))*
4. **Perplexity Discover** — near-black surface + a single distinctive accent;
   cards link straight to the source, no engagement traps; reads "serious and
   trustworthy". Same posture here: tap = go to the launch, nothing else.
   *([Perplexity design tokens](https://www.designmd.co/d/perplexity), [XDA on Discover](https://www.xda-developers.com/ways-i-use-perplexity-that-have-nothing-to-do-with-research/))*
5. **Never pure black** — #000 kills elevation (you can't cast light on it)
   and smears on OLED scroll; use near-black (#0A0A0B) with surfaces raised by
   *lightness*, not shadows. *([Material dark theme guidance via Uxcel](https://uxcel.com/blog/12-principles-of-dark-mode-design-627), [Netguru dark mode tips](https://www.netguru.com/blog/tips-dark-mode-ui))*
6. **Never pure white text** — soft white (~92% opacity) for headlines, ~60%
   for body prevents the "glowing text" harshness of #FFF on dark.
   *([accessible dark mode](https://medium.com/@tundehercules/how-to-design-accessible-dark-mode-interfaces-17f38ecea2e9))*
7. **Elevation = +lightness** — each z-level gets a slightly lighter surface
   (bg → card → chip), roughly a 5–8% white overlay per step; no drop shadows
   anywhere. *(same dark-mode sources)*
8. **Filter chips** — horizontally scrollable single row pinned at top is the
   proven pattern (Google Maps); ≤20-char labels, ~32px tall with 12px side
   padding, fully rounded, ≥48px touch targets with ≥8px gaps.
   *([Material 3 chips](https://m3.material.io/components/chips/guidelines), [Mobbin chip glossary](https://mobbin.com/glossary/chip))*
9. **Touch targets** — Inshorts users repeatedly mis-tapped adjacent
   categories; every interactive element here is ≥44×44px with real gaps.
   *(case study + Material guidance)*
10. **Headline scale** — 28–30px is the natural mobile display size in a 3:4
    modular scale (12/16/21/28); display type wants tight leading (~1.15–1.2)
    and slightly negative letter-spacing; body wants 1.5–1.6.
    *([type scale guide](https://www.pacgie.com/guides/what-is-type-scale), [font size guidelines](https://www.learnui.design/blog/mobile-desktop-website-font-size-guidelines.html))*
11. **Dark themes avoid flatness via hierarchy, not decoration** — with
    shadows gone, contrast steps in text opacity + surface lightness carry all
    depth. The design should survive a grayscale screenshot. *(dark-mode sources above)*
12. **Metadata as tiny caps** — small, letter-spaced, uppercase labels
    (source · time · score) read as editorial furniture rather than UI chrome —
    the newspaper "dateline" convention. *(observed across Artifact/Perplexity
    treatments in sources above)*

---

## Color tokens

```css
/* Surfaces — elevation by lightness, no shadows */
--bg:            #0A0A0B;   /* app background, near-black */
--surface:       #131316;   /* card */
--surface-2:     #1B1B1F;   /* chips, badges, pressed states */
--hairline:      rgba(255,255,255,0.07);  /* rare 1px separators */

/* Text — never pure white */
--text-high:     rgba(255,255,255,0.92);  /* headlines */
--text-body:     rgba(255,255,255,0.60);  /* summaries */
--text-meta:     rgba(255,255,255,0.38);  /* datelines, labels */

/* Category accents — one per card, desaturated & editorial.
   All sit ~65-70% lightness so contrast on --bg is uniform. */
--acc-video:     #D6A35C;   /* 🎬 amber       */
--acc-image:     #C88DA1;   /* 🎨 dusty rose  */
--acc-3d:        #8FB6CE;   /* 🧊 ice blue    */
--acc-audio:     #A395D8;   /* 🎵 soft violet */
--acc-editing:   #D08B72;   /* ✂️ clay        */
--acc-avatar:    #7FBFB2;   /* 🗣 sea teal    */
--acc-platform:  #93A3CE;   /* 🛠 slate blue  */
--acc-infra:     #9C968B;   /* ⚙️ warm gray   */
--acc-other:     #8E8E93;   /* 📡 neutral     */

/* Semantics */
--new-marker:    var(--acc-video);  /* single warm signal color for NEW dots */
```

Accent usage is rationed: the category chip text/dot, the relevance badge of
that card, and nothing else. No accent-colored headlines, borders, or fills.

## Typography — DM Sans everywhere

Loaded weights: 400, 500, 700 (variable, with optical sizing axis where
supported). Hierarchy must survive with color turned off.

| Role | Size / line | Weight | Tracking | Case |
|---|---|---|---|---|
| Headline | 30px / 1.15 | 700 | −0.02em | sentence |
| Summary | 15.5px / 1.6 | 400 | 0 | sentence |
| Meta / dateline | 11px / 1.2 | 500 | +0.08em | UPPERCASE |
| Chip label | 13px / 1 | 500 | +0.01em | sentence |
| Score badge | 11px / 1 | 700 | +0.02em | tabular numerals |
| Wordmark "dig." | 20px / 1 | 700 | −0.03em | lowercase |

Long headlines (2 lines max at 30px) truncate never — the classifier caps at
10 words, which fits.

## Spacing system

4px base unit. Working set: **8 / 12 / 16 / 24 / 32 / 48**.

- Card inner padding: 24px sides, content vertically centered in the snap viewport
- Headline → summary gap: 16px
- Summary → dateline gap: 24px (metadata visibly belongs to a different zone)
- Chip row: 12px vertical padding, 8px between chips, 16px leading inset
- Card corner radius: 20px; chips fully rounded

## Card anatomy

```
┌──────────────────────────────────────┐
│  filter bar (pinned, scrolls ⟷)      │  ← bg, hairline below
│  [All] [🎬 Video] [🎨 Image] [🧊 3D]…│     + "7+" relevance toggle at right
├──────────────────────────────────────┤
│                                      │
│   ┌──────────────────────────────┐   │  ← card: --surface, r20, no border
│   │                              │   │
│   │  🎬 VIDEO-GEN     ● NEW   8  │   │  ← chip (accent text) · new dot · score
│   │                              │   │     badge (--surface-2 pill)
│   │  Kling 3.5 adds native       │   │  ← headline, 30/700/−0.02em,
│   │  multi-shot audio            │   │     --text-high, max 2 lines
│   │                              │   │
│   │  Two-sentence summary set    │   │  ← 15.5/1.6, --text-body
│   │  in quiet 60% white, relaxed │   │
│   │  line height, ~52ch max.     │   │
│   │                              │   │
│   │  FAL.AI · 2H AGO             │   │  ← dateline, 11px caps, --text-meta
│   │                              │   │
│   └──────────────────────────────┘   │
│                                      │  ← generous --bg gutters do the
│            (next card peeks)         │     separation — no borders/shadows
└──────────────────────────────────────┘
```

Whole card is one tap target → opens launch URL in a new tab. No buttons on
the card.

## Interaction notes

- **Snap scroll:** `scroll-snap-type: y mandatory`, one card per viewport;
  wheel-friendly on desktop. Next card peeks ~24px to teach the gesture.
- **Entrance:** card content fades in + rises 8px, 240ms ease-out, only on
  first reveal. Felt, not seen.
- **Chip press:** background steps to --surface-2, 0.97 scale, 120ms. Active
  chip: accent-colored text + 1px hairline in accent at 30% (only allowed
  accent border in the app).
- **Unread:** localStorage set of seen card IDs; unseen cards show a 6px
  accent dot + "NEW" in the meta row; app opens at the newest unread card.
- **Pull-to-refresh:** overscroll at top re-fetches feed.json; subtle
  "digging…" text indicator, no spinner theatrics.
- **Reduced motion:** all transforms gated behind `prefers-reduced-motion`.

## What is banned

Gradients, glassmorphism, blur blobs, neon, drop shadows, borders on cards,
pure #FFF / #000, more than one accent hue visible per card, icons that
aren't the category emoji, anything animated longer than 300ms.
