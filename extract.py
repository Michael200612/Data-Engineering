import pandas as pd
import json

def extract_json(path:str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    df = pd.json_normalize(raw_data["messages"])
    return df

    
if __name__ == "__main__":
    df = extract_json("export.json")
    print(df.shape)          # how many messages, how many columns
    print(df.columns)        # what fields exist
    print(df.dtypes)         # what pandas thinks each column's type is
    print(df.head(3))        # eyeball a few rows
    print(df.isnull().sum())
