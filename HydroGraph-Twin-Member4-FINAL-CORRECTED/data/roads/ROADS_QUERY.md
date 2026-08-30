# Real Roads Data — Overpass Turbo Query

Member4's sandbox cannot reach the OpenStreetMap Overpass API directly, so
roads were NOT fabricated. Run this in https://overpass-turbo.eu (paste,
click Run, then Export -> GeoJSON) to get REAL road geometry clipped to the
exact study-area boundary used in velachery_boundary.geojson:

```
[out:json][timeout:25];
(
  way["highway"](12.9621,80.1891,12.9924,80.2284);
);
out geom;
```

Bounding box above = the (buffered) convex hull of the 20 real drainage
nodes in 01_velachery_nodes.csv (south,west,north,east).

After exporting, save as:
  data/roads/roads.geojson

To get a flat CSV (id, name, highway type, first/last coordinate) run:
  python3 src/geographic/roads_geojson_to_csv.py data/roads/roads.geojson data/roads/roads.csv
(a converter script is included in the delivered package)
