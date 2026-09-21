import pandas as pd
import json

def extract_json(path:str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    df = pd.json_normalize(raw_data["messages"])
    return df

    
if __name__ == "__main__":
    df = extract_json("export.json")
    df = strip_non_default_messages(df)

    users_df = build_users_table(df)   
    attachments_df = extract_attachments(df) 

    df = select_relevant_columns(df)
    df = normalize_timestamps(df)
    df = flag_edited(df)
    df = rename_reply_column(df)
