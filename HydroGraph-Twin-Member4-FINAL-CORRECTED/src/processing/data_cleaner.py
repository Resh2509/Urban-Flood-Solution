"""Basic validation helpers for Member 4 datasets."""
import pandas as pd
def validate_node_ids(*frames):
    sets=[set(f["node_id"].dropna().astype(str)) for f in frames if "node_id" in f.columns]
    return len({tuple(sorted(s)) for s in sets}) <= 1
