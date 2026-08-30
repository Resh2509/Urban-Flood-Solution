"""Geographic data outputs prepared for the Velachery prototype."""
from pathlib import Path
for p in ["data/drainage/drainage_nodes.geojson","data/drainage/drainage_lines.geojson","data/roads/roads.geojson","data/processed/velachery_boundary.geojson"]:
    print(Path(p))
