Member 4 OSM road outputs
==========================
Source: uploaded roads.geojson obtained from OpenStreetMap via Overpass Turbo.
Original features: 2775
Features intersecting the study bbox: 2775
Routing-oriented road rows: 2731
Study bbox: south=12.9621, west=80.1891, north=12.9924, east=80.2284

roads_clipped.geojson is a TRUE geometric clip to the study bounding box.
roads.csv contains routing-oriented OSM attributes and WKT geometry; pedestrian/path-only
classes are excluded from this CSV but retained in the clipped GeoJSON.
node_road_alignment.csv compares the team's N001-N020 coordinates with the nearest
routing road. This is a proximity check, not a claim that every node is a road node.
