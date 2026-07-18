"""
01-extract.py
=============

Read a SQLite database of chat messages and emit one card per
user / assistant pair (a "card" = 1 user message + 1 assistant
message sharing the same `prompt_id`).

Output: 02-cards.json with the shape described in
00-data-template.json.

Expected schema
---------------
The default SQLite schema this script reads from is:

    CREATE TABLE messages (
        id          INTEGER PRIMARY KEY,
        prompt_id   TEXT,        -- groups user + assistant replies
        role        TEXT,        -- 'user' | 'assistant' | other
        content     TEXT,
        created_at  TEXT         -- ISO 8601, e.g. '2025-01-15T10:00:00.000Z'
    );

If your schema is different, edit the SELECT statements below
or build 02-cards.json directly from your own pipeline.

Usage
-----
    python 01-extract.py

Reads:  your-chat.db (or change DB below)
Writes: 02-cards.json
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB = "your-chat.db"
OUT = "02-cards.json"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 1. Group messages by prompt_id; keep only groups with both user and assistant.
cur.execute(
    """
    SELECT
      prompt_id,
      MAX(CASE WHEN role='user'      THEN content END) AS user_text,
      MAX(CASE WHEN role='assistant' THEN content END) AS assistant_text,
      MIN(created_at) AS ts,
      COUNT(*)        AS n
    FROM messages
    WHERE prompt_id IS NOT NULL
    GROUP BY prompt_id
    ORDER BY MIN(created_at)
    """
)
rows = cur.fetchall()

cards = []
skipped = []
for prompt_id, user_text, asst_text, ts, n in rows:
    # A card requires both sides. Anything incomplete is recorded
    # separately so the rest of the pipeline can show what was lost.
    if not user_text or not asst_text:
        skipped.append(
            {
                "prompt_id": prompt_id,
                "ts": ts,
                "n_msgs": n,
                "has_user": bool(user_text),
                "has_assistant": bool(asst_text),
            }
        )
        continue
    cards.append(
        {
            "id": prompt_id,
            "ts": ts,
            "user": user_text,
            "assistant": asst_text,
        }
    )

# 2. Assistant messages with no matching user (deletions, partial
# writes, messages that landed in the table but lost their pair).
cur.execute(
    """
    SELECT id, created_at, content
    FROM messages
    WHERE role='assistant'
      AND (prompt_id IS NULL
           OR prompt_id NOT IN (SELECT prompt_id FROM messages WHERE role='user'))
    ORDER BY created_at
    """
)
orphans = [
    {"id": r[0], "ts": r[1], "content": r[2]} for r in cur.fetchall()
]

# 3. Meta.
cur.execute("SELECT MIN(created_at), MAX(created_at) FROM messages")
date_min, date_max = cur.fetchone()

meta = {
    "source_db": DB,
    "n_messages": sum(1 for _ in conn.execute("SELECT id FROM messages")),
    "n_cards": len(cards),
    "n_skipped_incomplete": len(skipped),
    "n_orphan_assistants": len(orphans),
    "date_range": [date_min, date_max],
    "extracted_at": datetime.now().isoformat(timespec="seconds"),
    "note": "card = 1 user message + 1 assistant message (same prompt_id). No labels yet.",
}

out = {
    "meta": meta,
    "cards": cards,
    "orphan_assistants": orphans,
    "skipped_incomplete": skipped,
}

Path(OUT).write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
size_kb = Path(OUT).stat().st_size / 1024
print(f"-> {OUT}  ({size_kb:.1f} KB)")
print(f"  cards:           {len(cards)}")
print(f"  orphan asst:     {len(orphans)}")
print(f"  skipped:         {len(skipped)}")
print(f"  date range:      {date_min} -> {date_max}")
