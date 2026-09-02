def strip_non_default_messages(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["type"] == "Default"].copy()

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