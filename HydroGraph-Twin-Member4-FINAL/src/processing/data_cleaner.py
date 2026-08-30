#!/usr/bin/env python3
"""Validate key Member-4 datasets and report node/key consistency."""
import argparse, pandas as pd

def main(data_dir, out):
    d=data_dir
    nodes=pd.read_csv(f"{d}/01_velachery_nodes.csv").dropna(subset=["node_id"])
    terrain=pd.read_csv(f"{d}/04_terrain_features.csv")
    hyd=pd.read_csv(f"{d}/05_hydraulic_observations.csv")
    labels=pd.read_csv(f"{d}/06_flood_blockage_labels.csv")
    rain=pd.read_csv(f"{d}/02_rainfall_timeseries.csv")
    ids=set(nodes.node_id)
    checks=[]
    checks.append(("nodes",len(nodes)==nodes.node_id.nunique()))
    checks.append(("terrain_ids",set(terrain.node_id)<=ids))
    checks.append(("hydraulic_ids",set(hyd.node_id)<=ids))
    checks.append(("label_ids",set(labels.node_id)<=ids))
    checks.append(("hydraulic_label_keys",
                   hyd[["timestamp","node_id"]].equals(labels[["timestamp","node_id"]])))
    checks.append(("rainfall_missing",rain.isna().sum().sum()==0))
    checks.append(("hydraulic_missing",hyd.isna().sum().sum()==0))
    checks.append(("labels_missing",labels.isna().sum().sum()==0))
    with open(out,"w") as f:
        f.write("HydroGraph-Twin — Member 4 validation\n")
        f.write("="*45+"\n")
        for k,v in checks: f.write(f"{k}: {'PASS' if v else 'FAIL'}\n")
        f.write(f"nodes: {len(nodes)}\n")
        f.write(f"rainfall rows: {len(rain)}\n")
        f.write(f"hydraulic rows: {len(hyd)}\n")
        f.write(f"label rows: {len(labels)}\n")
    print("Validation report written to",out)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--data",default="data")
    p.add_argument("--output",default="data/processed/validation_report.txt")
    a=p.parse_args(); main(a.data,a.output)
