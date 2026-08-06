# DM Chat Log ETL Pipeline

A small data engineering project that takes a raw Discord DM export and turns it into a clean, normalized, queryable relational database.

## Project Goal

Discord DM exports are messy — nested edits, deletions, system messages, inconsistent timestamps, no relational structure. This project builds a simple ETL (Extract, Transform, Load) pipeline that:

1. **Extracts** raw message data from a Discord DM export
2. **Transforms** it — cleaning, normalizing timestamps, handling edits/deletions, anonymizing participants
3. **Loads** it into a normalized SQLite database
4. **Analyzes** it via SQL queries (message frequency, response times, activity patterns, etc.)

This was built for the WeThinkCode Data Engineering elective, covering data engineering fundamentals and relational database design.

## Schema

The database has three tables:

**`users`**

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Anonymized user ID |
| alias | TEXT | Anonymized display name (e.g. "User A") |

**`messages`**

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Message ID |
| sender_id | INTEGER FK → users.id | Who sent it |
| content | TEXT | Message text |
| timestamp | DATETIME | When it was sent |
| reply_to_id | INTEGER FK → messages.id, nullable | If it's a reply, which message |
| edited | BOOLEAN | Whether the message was edited |

**`attachments`**

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Attachment ID |
| message_id | INTEGER FK → messages.id | Which message it belongs to |
| type | TEXT | File type (image, video, file, etc.) |
| filename | TEXT | Original filename |

## Pipeline

```
raw export (JSON)
      │
      ▼
[extract.py]   → loads raw export into a dataframe
      │
      ▼
[clean.py]     → strips system messages, normalizes timestamps,
                  resolves edits/deletions, anonymizes users
      │
      ▼
[load.py]      → creates SQLite tables, inserts cleaned data
      │
      ▼
chatlog.db     → queryable relational database
      │
      ▼
[queries.sql]  → analysis queries
```

## How to Run

```bash
# 1. Clone the repo
git clone <git@github.com:Michael200612/Data-Engineering.git>
cd <Data-Engineering>

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python main.py

# 4. Explore the database
sqlite3 chatlog.db
```
