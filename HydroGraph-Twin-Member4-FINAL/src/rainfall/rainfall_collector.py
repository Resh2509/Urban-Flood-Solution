#!/usr/bin/env python3
"""Fetch hourly rainfall/weather data for Velachery from Open-Meteo.

Usage:
  python rainfall_collector.py --start 2025-01-01 --end 2026-08-25 \
      --lat 12.978625 --lon 80.22158 --output data/02_rainfall_timeseries.csv
"""
import argparse, requests, pandas as pd

def collect(lat, lon, start, end):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start, "end_date": end,
        "hourly": ",".join([
            "precipitation", "temperature_2m", "relative_humidity_2m",
            "surface_pressure", "wind_speed_10m", "cloud_cover", "weather_code"
        ]),
        "timezone": "Asia/Kolkata"
    }
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    h = r.json()["hourly"]
    df = pd.DataFrame(h).rename(columns={"time":"timestamp","precipitation":"rainfall_mm"})
    return df

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--lat", type=float, default=12.978625)
    p.add_argument("--lon", type=float, default=80.22158)
    p.add_argument("--start", default="2025-01-01")
    p.add_argument("--end", default="2026-08-25")
    p.add_argument("--output", default="data/02_rainfall_timeseries.csv")
    a=p.parse_args()
    df=collect(a.lat,a.lon,a.start,a.end)
    df.to_csv(a.output,index=False)
    print(f"Wrote {len(df)} hourly rows to {a.output}")
