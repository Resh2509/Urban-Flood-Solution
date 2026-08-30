#!/usr/bin/env python3
"""Terrain processing helper for a GeoTIFF DEM.

Requires rasterio and numpy. Slope is calculated in percent. Flow-direction
and flow-accumulation are best reproduced with WhiteboxTools/GRASS/QGIS;
this script provides the reproducible DEM/slope preprocessing step.
"""
import argparse, rasterio, numpy as np

def slope_percent(src_path, out_path):
    with rasterio.open(src_path) as src:
        z=src.read(1).astype("float32")
        nodata=src.nodata
        xres=abs(src.transform.a); yres=abs(src.transform.e)
        gy,gx=np.gradient(z, yres, xres)
        # Approximate metres-per-degree conversion for EPSG:4326
        lat=float(src.bounds.bottom+src.bounds.top)/2
        mx=111320*np.cos(np.deg2rad(lat)); my=110540
        slope=np.sqrt((gx/mx)**2+(gy/my)**2)*100
        if nodata is not None: slope[z==nodata]=nodata
        prof=src.profile.copy(); prof.update(dtype="float32",count=1,compress="deflate")
        with rasterio.open(out_path,"w",**prof) as dst: dst.write(slope.astype("float32"),1)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("dem"); p.add_argument("slope")
    a=p.parse_args(); slope_percent(a.dem,a.slope)
