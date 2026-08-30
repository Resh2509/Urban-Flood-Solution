HydroGraph-Twin — Velachery DEM TIFF deliverables

These GeoTIFFs were generated from the uploaded Copernicus DEM, clipped to the project study area 12.955–12.995 N, 80.205–80.235 E.

Files:
- raw_dem.tif — elevation in metres
- slope.tif — slope in percent
- flowdirection.tif — D8 flow direction using ESRI codes (1=E, 2=SE, 4=S, 8=SW, 16=W, 32=NW, 64=N, 128=NE)
- flowaccumulation.tif — D8 upstream-cell accumulation
- low_lying_areas.tif — binary low-lying/flood-prone mask
- terrain_features_from_copernicus.csv — current node CSV sampled from these rasters

Important: these rasters are derived from the uploaded Copernicus DEM and therefore are internally consistent with raw_dem.tif. They are not numerically identical to the older Day-2 synthetic DEM package; that older package is a separate prototype.
