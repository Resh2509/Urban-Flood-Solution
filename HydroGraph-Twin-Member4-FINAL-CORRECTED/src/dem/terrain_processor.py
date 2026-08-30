"""Documented DEM processing contract for Member 4.
The final package contains the supplied Copernicus-derived rasters.
Use rasterio/GDAL/WhiteboxTools to reproduce or update them from a new DEM.
"""
from pathlib import Path
RASTERS=["raw_dem.tif","slope.tif","flowdirection.tif","flowaccumulation.tif","low_lying_areas.tif"]
if __name__=="__main__":
    for name in RASTERS: print(Path("data/dem")/name)
