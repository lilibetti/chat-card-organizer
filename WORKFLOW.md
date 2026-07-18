# WORKFLOW

> A reference for AI agents and contributors picking up this project.
> If you are an agent: read this file first, in full, before doing anything.


## Goal

Take a SQLite database of chat messages, turn them into a stream
of "cards" (one user message + one assistant reply), label each
card against the 14-label taxonomy, and surface the result in
three HTML views.


## File roles

| File | Role | Writable | Deletable |
| --- | --- | --- | --- |
| `01-extract.py` | SQLite → `02-cards.json` | by hand | no |
| `02-cards.json` | the cards, no labels yet | by `01-extract.py` | yes, regenerable |
| `03-label.py` | batching, prompt generation, merge | by hand | no |
| `03-batch-*.json` | per-batch LLM output (intermediate) | by the LLM | yes, auto-deleted on merge |
| `04-labeled.json` | cards + labels, the canonical truth | by `03-label.py merge` | no |
| `05-serve.py` | local HTTP server (port 8000) | by hand | no |
| `05-serve.bat` | Windows launcher for `05-serve.py` | by hand | no |
| `browse.html` | browse by topic | by hand | no |
| `collections.html` | manage user-curated collections | by hand | no |
| `conversation.html` | full timeline view | by hand | no |
| `LABELS.md` | taxonomy reference for humans | by hand | no |
| `00-data-template.json` | schema + 5 sample cards | by hand | no |


## The four commands

```bash
# 1. Status (always safe to run)
python 03-label.py status

# 2. Find the next 50 unlabeled cards, print as a prompt
python 03-label.py
#   → stdout is a prompt. Feed it to any LLM. Save the LLM's
#     response to 03-batch-YYYYMMDD-HHMMSS.json.

# 3. Merge every 03-batch-*.json into 04-labeled.json
python 03-label.py merge
#   → batch files are deleted on success.

# 4. Open the result in a browser
python 05-serve.py
#   → http://localhost:8000/browse.html
```

`BATCH_SIZE` is in `03-label.py` near the top. Change it if you
want bigger or smaller batches.


## Step-by-step (continuing an existing dataset)

### Step 1. See where you are

```bash
python 03-label.py status
```

Output:

```
=== progress ===
  total:  5
  done:   3
  todo:   2
  next:   2 cards
    first: prompt_xxx
    last:  prompt_yyy
```

### Step 2. Generate the prompt

```bash
python 03-label.py
```

This prints the full prompt (status header + the cards formatted
for the LLM + the expected output shape). Redirect to a file
for convenience:

```bash
python 03-label.py > next-prompt.txt
```

The script will suggest a filename for the LLM's response:
`03-batch-YYYYMMDD-HHMMSS.json`.

### Step 3. Label with your LLM

Paste the prompt into your LLM (API, local model, web UI).
Ask for strict JSON in the documented shape. Save the response
to the suggested filename.

If the LLM drifts (extra prose, wrong key names, wrong type for
label numbers), edit the response before saving. The expected
output is:

```json
{
  "batch_20250115-183000": {
    "prompt_aaa": ["8", "13"],
    "prompt_bbb": ["1"]
  }
}
```

- Outer key: the batch label the script suggested (a timestamp).
- Inner keys: card ids.
- Values: arrays of label numbers as **strings** (`"8"`, not `8`).
  Empty array `[]` means the card has no labels.

### Step 4. Merge

```bash
python 03-label.py merge
```

This scans every `03-batch-*.json`, normalizes the labels, recomputes
`by_label` and `by_bucket` counts, and rewrites `04-labeled.json`.
On success, every batch file is deleted.

If you only want to check progress, run `status` (no merge, no
side effects).

### Step 5. View

```bash
python 05-serve.py
```

Opens `http://localhost:8000/browse.html`. The three views:

- `browse.html` — sidebar of buckets + labels, main column of cards.
- `conversation.html` — full timeline, day by day, every message.
- `collections.html` — your curated collections, drag-to-reorder, export to Markdown.

If the browser shows stale numbers, hard-refresh (Ctrl+Shift+R
on Windows / Linux, Cmd+Shift+R on macOS). See *localStorage
priority* below.


## Adding new conversations to an existing dataset

> **Don't start from scratch.** If you have new messages to add,
> do an *incremental* sync, not a full re-extract.

1. Drop the new SQLite file in place (or point `01-extract.py` at it).
2. Compare the latest message timestamp in the database against
   the latest card timestamp in `02-cards.json`:

   ```python
   import json, sqlite3
   conn = sqlite3.connect('your-chat.db')
   cur = conn.cursor()
   cur.execute('SELECT MAX(created_at) FROM messages')
   db_max = cur.fetchone()[0]
   cards = json.load(open('02-cards.json', encoding='utf-8'))['cards']
   proto_max = max(c['ts'] for c in cards)
   print('db latest :', db_max)
   print('02 latest :', proto_max)
   ```

   - If they match, you have nothing new. Stop.
   - If `db_max` is later, you have new messages. Continue.

3. Re-run `python 01-extract.py`. It rewrites `02-cards.json`
   in place. New cards appear at the end; old cards are unchanged
   (as long as the old messages are still in the database).

4. Run `python 03-label.py`. It will compute `todo = all_cards −
   already_seen_ids` and print a prompt for the new cards only.
   Continue with Step 3 and 4 above.


## The taxonomy

14 labels, six buckets. See [`LABELS.md`](./LABELS.md) for the
full table. The numbers are stable identifiers — renaming is
safe (update `TAXONOMY` in `03-label.py` and the matching
`BUCKETS` constant in `browse.html`); renumbering is not (the
numbers are persisted in `04-labeled.json`).

The three places that must agree:

1. `03-label.py` → `TAXONOMY` and `BUCKETS`
2. `browse.html` → `BUCKETS` constant in `<script>`
3. `LABELS.md` → the human-readable table


## Notes for AI agents

- **Read this file first.** Don't assume the project state.
  `python 03-label.py status` is cheap; run it.

- **The LLM is not part of the pipeline.** The script only
  formats the prompt and parses the output. You bring the model.

- **Don't write code that "improves" the labeling.** The taxonomy
  is a personal choice. If a card feels mislabeled, the user
  can fix it in the browser. Don't auto-rewrite.

- **Don't delete `04-labeled.json` to "start fresh."** It is the
  canonical record. If you need to relabel a range, edit the
  cards in the browser (localStorage wins over the JSON file,
  see below) or re-merge after editing the relevant batch file.

- **Files you can freely create / delete:**
  - Create: `03-batch-*.json` (from LLM output)
  - Delete: any `03-batch-*.json` (the merge command does this)
  - Delete: `02-cards.json` (regenerable from the database)

- **Files you must not touch without asking:**
  - The three HTML files
  - `01-extract.py`, `03-label.py`, `05-serve.py`
  - `04-labeled.json` (the truth)
  - `LABELS.md`, `WORKFLOW.md`, `README.md`


## localStorage priority

`browse.html` and `conversation.html` read labels from two
places: the canonical `04-labeled.json` file, and the user's
local edits in `localStorage` (key: `chat-card-labels`).

When the two disagree, localStorage wins — the user's manual
edits are never overwritten by a re-merge.

This means: if the user has relabeled cards in the browser and
you re-run merge with new batch files, the old browser labels
stick. This is intentional.

If the user wants the merge to win, they need to clear that
localStorage key (DevTools → Application → Local Storage → delete
`chat-card-labels`), then hard-refresh.


## Failure modes

- **LLM returns invalid JSON** → fix the response, save again, re-merge.
- **LLM returns the right shape but wrong label numbers** → the merge
  silently filters unknown numbers. Check `by_label` in the new
  `04-labeled.json` to spot drift.
- **02-cards.json is corrupted** → re-run `01-extract.py`. The
  extraction is deterministic; if the database is unchanged, the
  output is unchanged. Existing `04-labeled.json` labels are
  preserved across this (since labels live keyed by id).
- **04-labeled.json is corrupted or wrong** → keep the batch files
  if you have any, delete `04-labeled.json`, then `python
  03-label.py merge` to rebuild from the batches. If no batch
  files survive, the labels are lost; the only path back is to
  re-label the cards.


## When the work is "done"

`04-labeled.json` `meta.n_labeled + meta.n_no_label == meta.n_cards`.

This is a stable state. The next interruption is "new conversations
to add" (see *Adding new conversations* above). The pipeline is
built for that loop, not for a single end.
