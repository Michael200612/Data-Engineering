import sqlite3
import pandas as pd

from extract import extract_json
from clean import (
    strip_non_message_types,
    build_users_table,
    extract_attachments,
    select_relevant_columns,
    normalize_timestamps,
    flag_edited,
    rename_reply_column,
)


def create_tables(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT UNIQUE NOT NULL,
        alias TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id TEXT UNIQUE NOT NULL,
        sender_id INTEGER NOT NULL,
        content TEXT,
        timestamp DATETIME NOT NULL,
        reply_to_id INTEGER,
        edited BOOLEAN,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (reply_to_id) REFERENCES messages(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER NOT NULL,
        type TEXT,
        filename TEXT,
        FOREIGN KEY (message_id) REFERENCES messages(id)
    )
    """)


def load_users(cursor: sqlite3.Cursor, users_df: pd.DataFrame) -> None:
    for _, row in users_df.iterrows():
        cursor.execute(
            "INSERT OR IGNORE INTO users (discord_id, alias) VALUES (?, ?)",
            (row["discord_id"], row["alias"])
        )


def load_messages(cursor: sqlite3.Cursor, df: pd.DataFrame) -> None:
    # build a lookup: discord author id -> our internal user id
    cursor.execute("SELECT id, discord_id FROM users")
    user_lookup = {discord_id: internal_id for internal_id, discord_id in cursor.fetchall()}

    for _, row in df.iterrows():
        sender_id = user_lookup[row["author.id"]]
        cursor.execute(
            """INSERT OR IGNORE INTO messages
               (discord_id, sender_id, content, timestamp, edited)
               VALUES (?, ?, ?, ?, ?)""",
            (row["id"], sender_id, row["content"], str(row["timestamp"]), bool(row["edited"]))
        )

    # second pass: now that all messages exist, resolve reply_to_id
    cursor.execute("SELECT id, discord_id FROM messages")
    message_lookup = {discord_id: internal_id for internal_id, discord_id in cursor.fetchall()}

    for _, row in df.iterrows():
        reply_to_discord_id = row["reply_to_id"]  # from rename_reply_column
        if pd.notnull(reply_to_discord_id):
            internal_reply_id = message_lookup.get(reply_to_discord_id)
            if internal_reply_id:
                cursor.execute(
                    "UPDATE messages SET reply_to_id = ? WHERE discord_id = ?",
                    (internal_reply_id, row["id"])
                )


def load_attachments(cursor: sqlite3.Cursor, attachments_df: pd.DataFrame) -> None:
    if attachments_df.empty:
        return

    cursor.execute("SELECT id, discord_id FROM messages")
    message_lookup = {discord_id: internal_id for internal_id, discord_id in cursor.fetchall()}

    for _, row in attachments_df.iterrows():
        message_id = message_lookup.get(row["message_discord_id"])
        if message_id:
            cursor.execute(
                "INSERT INTO attachments (message_id, type, filename) VALUES (?, ?, ?)",
                (message_id, row["type"], row["filename"])
            )


def run_pipeline():
    conn = sqlite3.connect("discord_logs.db")
    cursor = conn.cursor()

    create_tables(cursor)

    # extract
    df = extract_json("export.json")

    # clean
    df = strip_non_message_types(df)
    users_df = build_users_table(df)
    attachments_df = extract_attachments(df)
    df = select_relevant_columns(df)
    df = normalize_timestamps(df)
    df = flag_edited(df)
    df = rename_reply_column(df)

    # load
    load_users(cursor, users_df)
    load_messages(cursor, df)
    load_attachments(cursor, attachments_df)

    conn.commit()
    conn.close()
    print("Pipeline complete — data loaded into discord_logs.db")


if __name__ == "__main__":
    run_pipeline()