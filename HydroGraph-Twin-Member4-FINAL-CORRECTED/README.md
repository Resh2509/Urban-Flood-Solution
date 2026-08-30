# HydroGraph-Twin — Member 4 Final Corrected Delivery

This package is the corrected Member 4 data foundation for the Velachery prototype.

## Key correction
`data/04_terrain_features.csv` is now sourced directly from the supplied Copernicus-derived terrain file, so its terrain values are consistent with the included TIFF rasters in `data/dem/`. `data/processed/integrated_dataset.csv` was updated with the same terrain values.

## Included
- Core six CSV datasets
- Rainfall files
- Copernicus-derived DEM, slope, flow direction, flow accumulation and low-lying-area TIFFs
- Roads and drainage GeoJSON/CSV
- Velachery boundary
- Integrated dataset
- Validation report
- Member 4 processing-script placeholders/contracts

## Important
The TIFFs and terrain CSV are prototype geospatial products derived from the supplied Copernicus DEM. They should be treated as prototype analysis data, not survey-grade engineering data.
