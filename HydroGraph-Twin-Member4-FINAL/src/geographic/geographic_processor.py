#!/usr/bin/env python3
"""Build drainage node/line GeoJSON from the project CSVs."""
import argparse, csv, json

def feature_collection(features):
    return {"type":"FeatureCollection","features":features}

def main(nodes_csv, network_csv, nodes_geojson, lines_geojson):
    rows=list(csv.DictReader(open(nodes_csv,encoding="utf-8")))
    coords={r["node_id"]:(float(r["longitude"]),float(r["latitude"])) for r in rows if r.get("node_id")}
    nfeat=[]
    for r in rows:
        if not r.get("node_id"): continue
        nfeat.append({"type":"Feature","properties":r,
                      "geometry":{"type":"Point","coordinates":[float(r["longitude"]),float(r["latitude"])]}})
    lfeat=[]
    for r in csv.DictReader(open(network_csv,encoding="utf-8")):
        a,b=coords.get(r["source_node"]),coords.get(r["target_node"])
        if a and b:
            lfeat.append({"type":"Feature","properties":r,
                          "geometry":{"type":"LineString","coordinates":[list(a),list(b)]}})
    json.dump(feature_collection(nfeat),open(nodes_geojson,"w"),indent=2)
    json.dump(feature_collection(lfeat),open(lines_geojson,"w"),indent=2)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--nodes",default="data/01_velachery_nodes.csv")
    p.add_argument("--network",default="data/03_drainage_network.csv")
    p.add_argument("--nodes-out",default="data/drainage/drainage_nodes.geojson")
    p.add_argument("--lines-out",default="data/drainage/drainage_lines.geojson")
    a=p.parse_args(); main(a.nodes,a.network,a.nodes_out,a.lines_out)
