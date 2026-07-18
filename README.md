# Chat Card Organizer

> A local-first pipeline for turning raw chat exports into a
> browsable, taggable, exportable archive of your conversations.

No cloud. No accounts. No data leaves your machine. Just SQLite,
JSON, and three HTML pages that open in any browser.


## What it does

You have a SQLite database of conversations with an AI assistant.
Thousands of messages, mixed with system events, no way to find
anything. This tool gives them shape:

1. **Extracts** every user / assistant pair into a "card" — one row of JSON.
2. **Labels** each card against a 14-label taxonomy, six buckets deep.
3. **Browses** the result in three HTML views: by topic, by collection, or as a full timeline.
4. **Exports** any subset to Markdown for writing, archiving, or sharing.


## The pipeline

```
      your chat.db
           │
           ▼
      01-extract.py
           │
           ▼
       02-cards.json          ←  one card per entry, no labels yet
           │
           ▼
       03-label.py            ←  50 cards / batch → LLM → merge
           │
           ▼
      04-labeled.json         ←  the same cards + their labels
           │
           ▼
       05-serve.py            ←  http://localhost:8000
           │
     ┌─────┴──────┬──────────────┐
     ▼            ▼              ▼
  browse    conversation    collections
```


## Quick start

```bash
git clone https://github.com/your-name/chat-card-organizer
cd chat-card-organizer

# 1. Point 01-extract.py at your SQLite database
#    (or build 02-cards.json directly — see 00-data-template.json)

python 01-extract.py

# 2. Label, in batches of 50, with any LLM
python 03-label.py
#   → prints a prompt → feed to an LLM → save the JSON to 03-batch-<timestamp>.json
python 03-label.py merge

# 3. Open in browser
python 05-serve.py
#   → http://localhost:8000/browse.html
```

On Windows you can also double-click `05-serve.bat`.


## The taxonomy

14 labels, organized into 6 buckets.

```
   A   People                1, 2
   B   Body                  3
   C   Work · Money          4, 5, 6, 7
   D   Learning · Making     8, 9, 10, 11, 12
   E   Self                  13, 14, 15
   F   Life                  16
```

A card can carry multiple labels. A card with none lands in
`uncategorized`. The numbers are stable identifiers; the
human-readable names live in [`LABELS.md`](./LABELS.md) and are
yours to edit.

To change the taxonomy: edit `TAXONOMY` and `BUCKETS` in
`03-label.py` and the matching `BUCKETS` constant in
`browse.html`. The two must stay in sync.


## Data format

The pipeline speaks one format: a JSON file with this shape.

```json
{
  "meta": {
    "n_cards": 5,
    "n_messages": 10,
    "date_range": ["2025-01-01T00:00:00Z", "2025-01-31T23:59:59Z"]
  },
  "cards": [
    {
      "id": "prompt_xxxxxxxxxxxxx_xxxxx",
      "ts": "2025-01-01T10:00:00.000Z",
      "user": "...",
      "assistant": "..."
    }
  ],
  "orphan_assistants": [],
  "skipped_incomplete": []
}
```

See [`00-data-template.json`](./00-data-template.json) for a
complete example with five sample cards. If your chat history
isn't in SQLite, build this JSON yourself and skip `01-extract.py` —
the rest of the pipeline doesn't care where the data came from.


## The three views

- **`browse.html`** — sidebar of every bucket → label. Main column
  is a stream of cards. Click to expand. Click labels to filter.
  Check cards and add them to a collection.

- **`collections.html`** — a grid of your curated sets. Each tile
  shows its title, card count, and a note preview. Click in to
  see the cards (collapsed by default, click to expand). Drag to
  reorder. Export to Markdown.

- **`conversation.html`** — the full timeline, day by day, every
  message. Search by keyword. Jump to a specific message by ID.
  Same checkbox + collection workflow as `browse.html`.

All three views store state in `localStorage`. Nothing is
persisted to disk by the browser. Export often.


## Design notes

A few choices worth knowing:

- **Plain files, no build step.** The HTML pages are
  self-contained. CSS and JS live inside them. Open in any
  browser, no compilation, no bundler, no dependencies.
- **No frontend framework.** Vanilla JavaScript. The whole
  interface is three files under 700 lines each. Cognitive load
  stays low; the code is the docs.
- **localStorage for state, JSON files for truth.** The browser
  stores your collections, your label edits, your selection.
  The JSON files on disk are the canonical source.
- **The LLM is a tool, not a service.** Bring your own — API
  key, local model, web UI. The script's job is to format the
  prompt and parse the output.
- **Bilingual by default.** UI strings are English. The data
  is yours, in whatever language you wrote it. Replace the
  strings in the HTML if you want Chinese, Japanese, anything.


## Project layout

```
chat-card-organizer/
├── README.md                ← you are here
├── LABELS.md                ← taxonomy reference
├── WORKFLOW.md              ← for AI agents / contributors
├── 00-data-template.json    ← schema + 5 sample cards
├── 01-extract.py            ← SQLite → 02-cards.json
├── 02-cards.json            ← sample, replace with your data
├── 03-label.py              ← batch labeling workflow
├── 04-labeled.json          ← sample, run merge to populate
├── 05-serve.py              ← local HTTP server, port 8000
├── 05-serve.bat             ← Windows launcher
├── browse.html              ← by topic
├── conversation.html        ← full timeline
└── collections.html         ← your curated sets
```


## License

MIT.


## Acknowledgments

Built in the open, from a personal workflow that grew too large
for a notes app. If you fork it and make it yours, that's the
point.
