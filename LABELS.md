# Taxonomy

The default taxonomy in this project is **14 labels, organized
into 6 buckets.** The numbers are stable identifiers — the names
are yours to edit.

When you change the names, update three places and they must
agree:

1. `03-label.py` — `TAXONOMY` and `BUCKETS` dicts
2. `browse.html` — the `BUCKETS` constant near the top of `<script>`
3. `LABELS.md` — this file (so humans can read what the numbers mean)


## Default mapping

The numbers below are the labels as they appear in the JSON
files and the HTML. The English names are the *default* — they
are not the only valid choice.

| #   | Bucket | Default name (English)            | Default description                                         |
| --- | ------ | --------------------------------- | ----------------------------------------------------------- |
| 1   | A      | People — close                    | intimate relationships, romantic life, sexuality            |
| 2   | A      | People — social                   | family, friends, roommates, social anxiety                  |
| 3   | B      | Body                              | fitness, sleep, pain, weight, hormonal cycles               |
| 4   | C      | Work — survival                   | job search, interviews, offers, quitting, income            |
| 5   | C      | Work — product                    | product, MVP, PMF, fundraising                              |
| 6   | C      | Work — research                   | papers, PhD, postdoc, study abroad, academic transition    |
| 7   | C      | Work — side project               | personal ventures, learning-by-doing, cohort programs       |
| 8   | D      | Tech                              | programming, tools, AI engineering, CS fundamentals         |
| 9   | D      | Learning — systems                | reading, knowledge systems, second brain                    |
| 10  | D      | Making — writing                  | fiction, scripts, essays, narrative craft                  |
| 11  | D      | Making — design                   | typography, UI, visual taste, minimalism                    |
| 12  | D      | Making — multisensory             | synesthesia, sound, motion, audiovisual                     |
| 13  | E      | Self — mechanics                  | defense mechanisms, attachment style, anxiety, self-worth  |
| 14  | E      | Self — AI mirror                  | collaboration with AI, memory, self-reflection             |
| 15  | E      | Self — spiritual                  | tarot, astrology, meditation, contemplative practice       |
| 16  | F      | Life — place                      | cities, migration, housing, living alone                    |


## Buckets (sidebar groups)

```
A  People               1, 2
B  Body                 3
C  Work · Money         4, 5, 6, 7
D  Learning · Making    8, 9, 10, 11, 12
E  Self                 13, 14, 15
F  Life                 16
```

A card with no label is shown under the special bucket
`uncategorized`. It is not counted in any of A–F.


## Editing the taxonomy

1. Decide what you want to rename or regroup.
2. Open `03-label.py`. Find `TAXONOMY` and `BUCKETS`. The
   `TAXONOMY` rows are `(number, bucket_letter, description)`.
   `BUCKETS` is `{letter: [numbers]}`.
3. Open `browse.html`. Find the `BUCKETS` constant in the
   `<script>` block. It uses the *bucket name* (e.g. `"People"`)
   as the key and the label *numbers* as the values — the same
   shape as `03-label.py` but with human-readable names.
4. Update `LABELS.md` (this file) to match.
5. Re-run `python 03-label.py merge` to refresh `04-labeled.json`
   if you changed which labels exist (renaming is safe; removing
   or renumbering is not, because the numbers are persisted in
   the JSON files).
