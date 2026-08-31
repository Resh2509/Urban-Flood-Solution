import os
import math
import csv

# ============================================================
# 1. PATH CONFIGURATION
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "hydro_twin_Data")
NODES_FILE = os.path.join(DATA_DIR, "01_velachery_nodes.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "03_drainage_network.csv")

print("\nReading node file...")
print(f"File: {NODES_FILE}")

if not os.path.exists(NODES_FILE):
    print("\n[ERROR] File not found.")
    exit()

# ============================================================
# 2. RAW TEXT PARSER (Bypasses bad CSV header formatting)
# ============================================================
nodes = []

with open(NODES_FILE, "r", encoding="utf-8-sig") as f:
    lines = [line.strip() for line in f if line.strip()]

if len(lines) < 2:
    print("\n[ERROR] File is empty or has no data rows.")
    exit()

# Split the first line to get headers
raw_header = lines[0].replace('"', '').replace("'", "")
headers = [h.strip().lower() for h in raw_header.split(",")]
print(f"Cleaned Headers: {headers}")

# Find index positions
def get_idx(targets):
    for t in targets:
        if t in headers:
            return headers.index(t)
    return None

id_idx = get_idx(["@id", "node_id", "id", "node"])
name_idx = get_idx(["name", "location_name", "location"])
lat_idx = get_idx(["@lat", "latitude", "lat", "y"])
lon_idx = get_idx(["@lon", "longitude", "lon", "lng", "x"])
type_idx = get_idx(["node_type", "type", "highway", "amenity"])

print(f"Column Indices -> ID: {id_idx}, Lat: {lat_idx}, Lon: {lon_idx}")

# Parse rows
for row_num, line in enumerate(lines[1:], start=1):
    cleaned_line = line.replace('"', '').replace("'", "")
    parts = [p.strip() for p in cleaned_line.split(",")]
    
    if len(parts) <= max(filter(lambda x: x is not None, [lat_idx, lon_idx])):
        continue

    try:
        lat = float(parts[lat_idx])
        lon = float(parts[lon_idx])
    except (ValueError, TypeError, IndexError):
        continue

    node_id = parts[id_idx] if (id_idx is not None and id_idx < len(parts) and parts[id_idx]) else f"N{row_num:03d}"
    loc_name = parts[name_idx] if (name_idx is not None and name_idx < len(parts) and parts[name_idx]) else node_id
    node_type = parts[type_idx] if (type_idx is not None and type_idx < len(parts) and parts[type_idx]) else "drainage_node"

    nodes.append({
        "node_id": node_id,
        "location_name": loc_name,
        "latitude": lat,
        "longitude": lon,
        "node_type": node_type
    })

print(f"Total valid nodes parsed: {len(nodes)}")

if len(nodes) < 2:
    print("\n[ERROR] Not enough valid coordinates found.")
    exit()

# ============================================================
# 3. HYDRAULICS & DISTANCE CALCULATIONS
# ============================================================
def haversine(lat1, lon1, lat2, lon2):
    r = 6371000  # meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return round(r * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))), 2)

def manning_capacity(diameter_m=0.8, slope=0.004, n=0.013):
    area = math.pi * (diameter_m ** 2) / 4
    hydraulic_radius = diameter_m / 4
    flow_m3s = (1.0 / n) * area * (hydraulic_radius ** (2/3)) * (slope ** 0.5)
    return round(flow_m3s * 1000, 2)  # L/s

# ============================================================
# 4. NETWORK GENERATION & EXPORT
# ============================================================
network = []
diameter_cycle = [0.6, 0.8, 1.0]

for i in range(len(nodes) - 1):
    src, dst = nodes[i], nodes[i + 1]
    dist = max(haversine(src["latitude"], src["longitude"], dst["latitude"], dst["longitude"]), 1.0)
    diam = diameter_cycle[i % len(diameter_cycle)]
    cap = manning_capacity(diameter_m=diam, slope=0.004, n=0.013)

    network.append({
        "pipe_id": f"P{i + 1:03d}",
        "source_node": src["node_id"],
        "target_node": dst["node_id"],
        "pipe_length_m": dist,
        "pipe_diameter_m": diam,
        "pipe_slope": 0.004,
        "roughness_coefficient": 0.013,
        "pipe_capacity_lps": cap,
        "data_source": "manning_formulation"
    })

fieldnames = [
    "pipe_id", "source_node", "target_node", "pipe_length_m",
    "pipe_diameter_m", "pipe_slope", "roughness_coefficient",
    "pipe_capacity_lps", "data_source"
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(network)

print("\n" + "=" * 50)
print("SUCCESS: 03_drainage_network.csv generated successfully!")
print(f"Total pipes created: {len(network)}")
print(f"Output: {OUTPUT_FILE}")
print("=" * 50)