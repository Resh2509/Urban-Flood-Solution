# HydroGraph-Twin — Member 4 Final Delivery

This package follows the requested Member 4 folder structure.

## Final deliverables

- Rainfall/weather time series
- Raw Copernicus-derived DEM and terrain rasters
- Terrain feature CSV
- Velachery nodes
- Drainage network + GeoJSON
- OSM road network + CSV
- Study-area boundary
- Integrated dataset
- Validation report
- Reproducibility/helper scripts

## Folder structure

```text
HydroGraph-Twin/
├── data/
│   ├── 01_velachery_nodes.csv
│   ├── 02_rainfall_timeseries.csv
│   ├── 02_velachery_weather_timeseries.csv
│   ├── 03_drainage_network.csv
│   ├── 04_terrain_features.csv
│   ├── 05_hydraulic_observations.csv
│   ├── 06_flood_blockage_labels.csv
│   ├── rainfall/
│   │   ├── latest_rainfall.json
│   │   └── rainfall_forecast.csv
│   ├── dem/
│   │   ├── raw_dem.tif
│   │   ├── slope.tif
│   │   ├── flowdirection.tif
│   │   ├── flowaccumulation.tif
│   │   ├── low_lying_areas.tif
│   │   └── terrain_features_from_copernicus.csv
│   ├── roads/
│   ├── drainage/
│   └── processed/
│       ├── velachery_boundary.geojson
│       ├── integrated_dataset.csv
│       └── validation_report.txt
├── src/
│   ├── rainfall/rainfall_collector.py
│   ├── dem/terrain_processor.py
│   ├── geographic/geographic_processor.py
│   └── processing/data_cleaner.py
└── README.md
```

## Status

**Structurally complete for Member 4 delivery.**

One important scientific/data-integrity note: the existing team
`04_terrain_features.csv` is not numerically identical to values sampled from
the Copernicus-derived TIFFs. The package preserves both instead of silently
overwriting the team's source data. See `data/processed/validation_report.txt`.

The core integrated dataset remains the team's validated 10,000-row dataset.
