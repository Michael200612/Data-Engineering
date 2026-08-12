import pandas as pd
import json

def extract_json(path:str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    df = pd.json_normalize(raw_data["messages"])
    return df

    
if __name__ == "__main__":
    extract_json("export.json")
