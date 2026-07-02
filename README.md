# dig.ai

A personal radar for launches in visual & creative AI — video gen, image gen,
3D, audio/music, editing tools, creative platforms.

- **Phase 1 — engine:** a GitHub Actions job runs every 3 hours, watches model
  registries (fal.ai, Replicate, Hugging Face), Hacker News, Reddit, Product
  Hunt, and official blogs, classifies every new item with Claude, and pushes
  instant notifications to your phone via [ntfy](https://ntfy.sh).
- **Phase 2 — app:** an Inshorts-style swipeable PWA served from `docs/` via
  GitHub Pages, reading `docs/feed.json`. *(Built after Phase 1 is verified.)*

## Repo layout

```
dig/                  engine package (fetchers, classifier, notifier, pipeline)
sources.yaml          what to watch — add/disable sources here
config.yaml           thresholds, model, batch sizes
prompts/classifier.md the taste criteria — tune relevance scoring here
state/seen.json       dedupe state (committed back by the workflow)
state/log.jsonl       full run log incl. filtered-out items, for tuning
docs/feed.json        every classified launch, newest first (Phase 2 data source)
moodboard/            drop UI reference screenshots here before Phase 2
.github/workflows/dig.yml   the scheduled workflow
test_ping.py          sends a test notification to your topic
```

## Setup

### 1. Push this repo to GitHub

```bash
git remote add origin git@github.com:<you>/dig-ai.git
git push -u origin main
```

Keep the repo **private** if you don't want your feed public (GitHub Pages on
a private repo requires a paid plan; a public repo is fine too — the only
secret-ish thing, your ntfy topic name, never appears in the repo).

### 2. Install ntfy and subscribe to your private topic

1. Install the **ntfy** app — [Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) / [iOS](https://apps.apple.com/us/app/ntfy/id1625396347).
2. Pick a long random topic name nobody can guess, e.g. `dig-ai-8fk2x91q`
   (anyone who knows the name can read your pings — treat it like a password).
3. In the app: **+ → Subscribe to topic** → enter your topic name.
4. On iOS, allow notifications when prompted.

### 3. Add the GitHub secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Anthropic API key |
| `NTFY_TOPIC` | your topic name, e.g. `dig-ai-8fk2x91q` |
| `REPLICATE_API_TOKEN` | *(optional)* free Replicate token, only if the public listing 401s |

### 4. Test the notification path

```bash
pip install requests
python3 test_ping.py dig-ai-8fk2x91q
```

You should get a "dig.ai online 🟢" push within seconds.

### 5. Enable Actions and run the seed run

1. Repo → **Actions** tab → enable workflows if prompted.
2. Open **dig.ai radar** → **Run workflow** → set `seed` to `1` → run.
   This marks everything currently visible as already-seen **without sending
   notifications**, so you don't get 500 pings on day one.

### 6. Run a normal run

**Run workflow** again with `seed` left at `0` (or just wait — the cron fires
every 3 hours). From now on, anything genuinely new gets classified and, if
relevant enough, lands on your phone.

### 7. GitHub Pages (for Phase 2)

Repo → **Settings → Pages** → Source: *Deploy from a branch* → branch `main`,
folder `/docs`. The feed is then live at
`https://<you>.github.io/dig-ai/feed.json`, and the app (once built) at
`https://<you>.github.io/dig-ai/`.

## Local testing

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# fetch + dedupe only (no API key needed):
python3 -m dig.main --dry-run

# fetch + classify, print would-be notifications, write nothing:
ANTHROPIC_API_KEY=sk-ant-... python3 -m dig.main --dry-run
```

## Tuning

- **Too noisy / too quiet:** raise or lower `relevance_threshold` in
  [config.yaml](config.yaml), or edit the scoring rubric in
  [prompts/classifier.md](prompts/classifier.md).
- **Add a source:** append to [sources.yaml](sources.yaml) — `rss` for feeds,
  `html` with a `link_pattern` for blogs without RSS.
- **See what was filtered out and why:** read `state/log.jsonl` — every
  classified item is logged with its scores, including non-launches.
- **Failing sources:** after 5 consecutive failures a ⚠️ warning rides along
  on your next notification. Check `state/log.jsonl` for the error.

## Troubleshooting

- **Reddit 403 in Actions:** Reddit sometimes blocks datacenter IPs. The run
  continues without it (fail-soft); HN and the registries cover most of the
  same launches.
- **Replicate 401:** add the optional `REPLICATE_API_TOKEN` secret.
- **An `html` source returns junk:** tighten its `link_pattern`, or set
  `enabled: false`.

## The app (Phase 2)

The PWA lives in `docs/` (vanilla HTML/CSS/JS, no build step) and reads
`feed.json` from the same folder. Theme derived from sazabi.com — see
[design/MOODBOARD.md](design/MOODBOARD.md), Revision 2.

- **Local preview:** `python3 -m http.server 8642 --directory docs`, then open
  `http://localhost:8642/?demo=1` (`?demo=1` loads `demo-feed.json` sample
  cards; without it the app reads the real `feed.json`).
- **Install on your phone:** open `https://<you>.github.io/dig-ai/` — iOS
  Safari: Share → *Add to Home Screen*; Android Chrome: menu → *Install app*.
- Unread state is per-device (localStorage). Pull down to refresh the feed.

## Local mode (no API key)

The engine can run on a Claude subscription instead of an API key:
`classifier_backend: claude-cli` in config.yaml shells out to a logged-in
`claude -p`. On this machine the radar runs via launchd
(`~/Library/LaunchAgents/com.dig-ai.radar.plist`, every 3 h) → `~/.dig-ai/run.sh`
(env in `~/.dig-ai/env`), which commits state + feed and pushes; GitHub Pages
serves the app. The cloud workflow is disabled but kept for API-key use.
`python -m dig.main --backfill` fills an empty feed once, without notifications.
