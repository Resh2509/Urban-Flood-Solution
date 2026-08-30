"""Prototype rainfall collector. Replace API calls/coordinates as needed.
Input/output contract: writes data/02_rainfall_timeseries.csv.
"""
from pathlib import Path
import pandas as pd

OUT=Path("data/02_rainfall_timeseries.csv")
def validate(df: pd.DataFrame)->pd.DataFrame:
    required={"timestamp","rainfall_mm"}
    missing=required-set(df.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    df=df.copy(); df["timestamp"]=pd.to_datetime(df["timestamp"], errors="coerce")
    df["rainfall_mm"]=pd.to_numeric(df["rainfall_mm"], errors="coerce")
    return df.dropna(subset=["timestamp","rainfall_mm"]).drop_duplicates("timestamp").sort_values("timestamp")

if __name__=="__main__":
    print(f"Validated rainfall file: {OUT}")
