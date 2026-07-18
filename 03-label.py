"""
03-label.py
===========

Label every card in 02-cards.json against the taxonomy defined
below, in batches of 50, using any LLM of your choice.

Usage
-----
    python 03-label.py            # show progress + print next batch as a prompt
    python 03-label.py status     # progress only
    python 03-label.py merge      # merge 03-batch-*.json -> 04-labeled.json
    python 03-label.py done       # is everything labeled?

Workflow
--------
1. Run `python 03-label.py`. It reads 02-cards.json + every
   03-batch-*.json + 04-labeled.json, finds the next 50 unlabeled
   card ids, and prints a complete prompt to stdout.

2. Feed the prompt to an LLM (API, local model, or web UI). The
   LLM should respond with strict JSON, one entry per card id.

3. Save the LLM's response to `03-batch-YYYYMMDD-HHMMSS.json`.

4. Run `python 03-label.py merge` to roll all batch files into
   04-labeled.json. Batch files are auto-deleted on success.

The taxonomy
------------
14 labels, organized into 6 buckets (A–F). The numbers are stable
identifiers. The English names are the *defaults* in this file —
edit TAXONOMY and BUCKETS to match your own labels.

BUCKETS in 03-label.py and BUCKETS in browse.html must agree.
"""
import json
import glob
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

BATCH_SIZE = 50

# === 14 labels, 6 buckets ===
# (label_number, bucket_letter, short_description)
TAXONOMY = [
    (1,  "A", "intimate relationships, romantic life, sexuality"),
    (2,  "A", "family, friends, social dynamics"),
    (3,  "B", "physical body, health, sleep, energy"),
    (4,  "C", "jobs, applications, interviews, income"),
    (5,  "C", "product, MVP, PMF, business"),
    (6,  "C", "academic research, study, transition"),
    (7,  "C", "side projects, personal ventures, learning by doing"),
    (8,  "D", "programming, tools, AI, CS fundamentals"),
    (9,  "D", "reading, knowledge systems, second brain"),
    (10, "D", "writing, narrative, fiction, essays"),
    (11, "D", "typography, UI, visual taste, design"),
    (12, "D", "synesthesia, sound, motion, audiovisual"),
    (13, "E", "defense mechanisms, anxiety, self-worth, attachment"),
    (14, "E", "AI collaboration, memory, self-reflection via AI"),
    (15, "E", "spiritual practice, contemplative life, esoteric systems"),
    (16, "F", "cities, migration, housing, living alone"),
]

LABEL_LIST = [t[0] for t in TAXONOMY]  # [1, 2, ..., 16]

BUCKETS = {
    "A": [1, 2],
    "B": [3],
    "C": [4, 5, 6, 7],
    "D": [8, 9, 10, 11, 12],
    "E": [13, 14, 15],
    "F": [16],
}

PROMPT_TPL = """You are a careful, conservative conversation analyst. Below are {n} "turn" cards: each one is a user message paired with its assistant reply. Assign each card zero or more labels from the 14-label taxonomy.

## The 14 labels
1.  People — close (intimate relationships, romantic life, sexuality)
2.  People — social (family, friends, social dynamics)
3.  Body (physical body, health, sleep, energy)
4.  Work — survival (jobs, applications, interviews, income)
5.  Work — product (product, MVP, PMF, business)
6.  Work — research (academic research, study, transition)
7.  Work — side project (side projects, personal ventures, learning by doing)
8.  Tech (programming, tools, AI, CS fundamentals)
9.  Learning — systems (reading, knowledge systems, second brain)
10. Making — writing (writing, narrative, fiction, essays)
11. Making — design (typography, UI, visual taste, design)
12. Making — multisensory (synesthesia, sound, motion, audiovisual)
13. Self — mechanics (defense mechanisms, anxiety, self-worth, attachment)
14. Self — AI mirror (AI collaboration, memory, self-reflection via AI)
15. Self — spiritual (spiritual practice, contemplative life, esoteric systems)
16. Life — place (cities, migration, housing, living alone)

## Rules
- Read both the user message and the assistant reply.
- If nothing clearly matches, return an empty list. Do not guess.
- A card can carry multiple labels when the conversation covers several themes.
- Output label numbers as strings (e.g. "8", not 8) to match the JSON convention used elsewhere.

## Output format (strict JSON, nothing else)
```json
{{
  "batch_{batch_label}": {{
    "card_id_1": ["8", "13"],
    "card_id_2": ["1"],
    "card_id_3": []
  }}
}}
```

## Cards ({n})

{batch_text}
"""


# ---------- helpers ----------
def load_cards():
    return json.load(open("02-cards.json", encoding="utf-8"))["cards"]


def get_done_ids():
    """Return the set of card ids that have already appeared in
    some batch file (and therefore should not be re-emitted).

    Fallback: if no batch files exist, treat every id that already
    has a non-empty label in 04-labeled.json as done.
    """
    done = set()
    batch_files = sorted(glob.glob("03-batch-*.json"))
    for bf in batch_files:
        bd = json.load(open(bf, encoding="utf-8"))
        for inner in bd.values():
            if isinstance(inner, dict):
                for pid, ls in inner.items():
                    if isinstance(ls, list):
                        done.add(pid)
    if not batch_files and Path("04-labeled.json").exists():
        merged = json.load(open("04-labeled.json", encoding="utf-8"))
        for c in merged.get("cards", []):
            ls = c.get("labels") or []
            if ls:
                done.add(c["id"])
    return done


def status():
    cards = load_cards()
    all_ids = [c["id"] for c in cards]
    done = get_done_ids()
    todo = [pid for pid in all_ids if pid not in done]
    n_done = len(all_ids) - len(todo)
    print("=== progress ===")
    print(f"  total:  {len(all_ids)}")
    print(f"  done:   {n_done}")
    print(f"  todo:   {len(todo)}")
    if not todo:
        print("  ✓ all done")
        return None
    next_batch = todo[:BATCH_SIZE]
    print(f"  next:   {len(next_batch)} cards")
    print(f"    first: {next_batch[0]}")
    print(f"    last:  {next_batch[-1]}")
    return next_batch


def format_batch(card_ids):
    cards_by_id = {c["id"]: c for c in load_cards()}
    parts = []
    for cid in card_ids:
        c = cards_by_id.get(cid)
        if not c:
            print(f"  WARN: card not found: {cid}", file=sys.stderr)
            continue
        parts.append(
            f"### card {c['id']}  ({c['ts']})\nuser: {c['user']}\nassistant: {c['assistant']}\n"
        )
    return "\n---\n\n".join(parts)


def make_prompt(card_ids, batch_label):
    batch_text = format_batch(card_ids)
    return PROMPT_TPL.format(
        n=len(card_ids),
        batch_label=batch_label,
        batch_text=batch_text,
    )


def next_batch():
    card_ids = status()
    if not card_ids:
        return
    batch_label = datetime.now().strftime("%Y%m%d-%H%M%S")
    print(f"\n=== suggested filename: 03-batch-{batch_label}.json ===\n")
    print(make_prompt(card_ids, batch_label))


def merge_batches():
    """Merge every 03-batch-*.json into 04-labeled.json, then delete the batch files."""
    cards = load_cards()
    batch_files = sorted(glob.glob("03-batch-*.json"))
    print(f"Found {len(batch_files)} batch file(s)")

    labels = {}
    for bf in batch_files:
        d = json.load(open(bf, encoding="utf-8"))
        for batch_key, inner in d.items():
            if not isinstance(inner, dict):
                continue
            for prompt_id, ls in inner.items():
                if not isinstance(ls, list):
                    continue
                clean = []
                for raw in ls:
                    # Accept both int and string label ids; normalize to string.
                    try:
                        n = int(raw)
                    except (TypeError, ValueError):
                        continue
                    if n in LABEL_LIST and n not in clean:
                        clean.append(n)
                labels[prompt_id] = [str(n) for n in clean]

    labeled = 0
    no_label = 0
    by_bucket = Counter()
    by_label = Counter()
    out_cards = []
    for c in cards:
        cid = c["id"]
        ls = labels.get(cid, [])
        if ls:
            labeled += 1
        else:
            no_label += 1
        buckets = []
        for b, lbls in BUCKETS.items():
            if any(int(x) in lbls for x in ls):
                buckets.append(b)
        for x in ls:
            by_label[x] += 1
        for b in buckets:
            by_bucket[b] += 1
        out_cards.append({**c, "labels": ls, "buckets": buckets})

    meta = {
        "n_cards": len(cards),
        "n_labeled": labeled,
        "n_no_label": no_label,
        "by_label": dict(by_label),
        "by_bucket": dict(by_bucket),
        "merged_at": datetime.now().isoformat(timespec="seconds"),
        "batch_files": batch_files,
    }
    Path("04-labeled.json").write_text(
        json.dumps(
            {"meta": meta, "cards": out_cards}, ensure_ascii=False, indent=2
        ),
        encoding="utf-8",
    )
    print("-> 04-labeled.json")
    print(f"  total:   {len(cards)}")
    print(f"  labeled: {labeled}")
    print(f"  no_label:{no_label}")
    print(f"  by_bucket: {dict(by_bucket)}")
    print(f"  by_label (top 5): {by_label.most_common(5)}")

    # Clean up intermediate products. 04-labeled.json is the
    # authoritative source; the HTML views read from it, not from
    # the batch files.
    deleted = 0
    failed = 0
    for bf in batch_files:
        try:
            Path(bf).unlink()
            deleted += 1
        except OSError as e:
            print(f"  WARN: failed to delete {bf}: {e}", file=sys.stderr)
            failed += 1
    print(
        f"  cleanup: deleted {deleted}/{len(batch_files)} batch file(s)"
        + (f" (failed: {failed})" if failed else "")
    )


def check_done():
    cards = load_cards()
    done = get_done_ids()
    print(f"done: {len(done)}/{len(cards)}")
    if len(done) >= len(cards):
        print("✓ all done")
    else:
        print(f"remaining: {len(cards) - len(done)}")


# ---------- entry point ----------
def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            status()
        elif cmd == "merge":
            merge_batches()
        elif cmd == "done":
            check_done()
        else:
            print(f"unknown command: {cmd}", file=sys.stderr)
            print("usage: python 03-label.py [status|merge|done]", file=sys.stderr)
            sys.exit(1)
    else:
        next_batch()


if __name__ == "__main__":
    main()
