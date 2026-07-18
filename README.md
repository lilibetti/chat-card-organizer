# Chat Card Organizer

A quiet tool for turning a long, scattered conversation history into
something you can browse, tag, collect, and write from — all local,
no accounts, no cloud.

## Try it

These live pages show the tool with sample data. Nothing is simulated.

- [Browse by theme →](https://lilibetti.github.io/chat-card-organizer/browse.html)
- [Browse by time →](https://lilibetti.github.io/chat-card-organizer/conversation.html)
- [Curated collections →](https://lilibetti.github.io/chat-card-organizer/collections.html)

## What it does

You talk to an AI assistant for months. Thousands of messages,
dozens of threads, ideas scattered across weeks. You know you said
something important somewhere, but you can't find it.

This tool gives those conversations a shape:

- Extracts every exchange into a card (one prompt + one reply).
- Labels each card across a 16-label taxonomy — body, work, self,
  love, code, sound, place…
- Lets you browse by theme, by day, or by search.
- Lets you gather cards into collections, reorder them, and export
  everything to Markdown — ready to be turned into an essay, a
  talk, or a record you keep.

It does not write for you. It puts your own words back where you
can reach them, so you can do the writing.

## How it works

Four steps, all local:

1. **Extract** — a Python script reads your chat database and
   produces a clean JSON file of cards.
2. **Label** — you (or an LLM you bring) assign each card to one
   or more categories. The taxonomy is yours to edit.
3. **Merge** — one command rolls all labels into the final dataset.
4. **Browse** — three self-contained HTML pages open directly in
   your browser. No server, no build step, no framework.

Your data never leaves your machine. The LLM is a tool you bring,
not a service the tool depends on.

## Who this is for

People who have long, substantive conversations with AI assistants
and want to revisit, organize, and write from their own history.
Writers, researchers, product thinkers, and anyone who treats their
conversation archive as raw material rather than a black box.

## Why it's built this way

Zero dependencies in the frontend. The HTML pages are plain files —
CSS and JavaScript live inside them. You can open them on any
computer, ten years from now, and they will still work.

The pipeline is a handful of scripts under 150 lines each. If
something breaks, you can read the code in one sitting and fix it.

## Project layout

```
chat-card-organizer/
├── README.md
├── LABELS.md                ← the taxonomy, in plain language
├── WORKFLOW.md              ← step-by-step for developers
├── 00-data-template.json    ← schema and sample data
├── 01-extract.py            ← database → cards
├── 03-label.py              ← batch labeling
├── 05-serve.py              ← local server
├── browse.html              ← view by theme
├── conversation.html        ← view by time
└── collections.html         ← your curated sets
```

## License

MIT.

Built from a personal workflow that outgrew a notes app.
If you fork it and make it yours, that's the point.
