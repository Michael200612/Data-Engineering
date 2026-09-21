def strip_non_message_types(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["type"].isin(["Default", "Reply"])].copy()

def select_relevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "id", "author.id", "author.name", "content",
        "timestamp", "timestampEdited",
        "reference.messageId", "attachments"
    ]
    return df[keep].copy()

def normalize_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timestampEdited"] = pd.to_datetime(df["timestampEdited"])
    return df

def flag_edited(df: pd.DataFrame) -> pd.DataFrame:
    df["edited"] = df["timestampEdited"].notnull()
    return df

def rename_reply_column(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={"reference.messageId": "reply_to_id"})


def build_users_table(df: pd.DataFrame) -> pd.DataFrame:
    unique_authors = df[["author.id", "author.name"]].drop_duplicates().reset_index(drop=True)
    unique_authors["alias"] = ["User " + chr(65 + i) for i in range(len(unique_authors))]  # User A, User B, ...
    return unique_authors.rename(columns={"author.id": "discord_id"})[["discord_id", "alias"]]

def extract_attachments(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        for att in row["attachments"]:
            rows.append({
                "message_discord_id": row["id"],
                "type": att["fileName"].split(".")[-1],
                "filename": att["fileName"]
            })
    return pd.DataFrame(rows)