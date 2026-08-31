import csv
import os

# ============================================================
# 1. PROJECT AND FILE PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(
    BASE_DIR,
    "hydro_twin_Data"
)

# Your current input file
input_file = os.path.join(
    DATA_DIR,
    "velachery_nodes.csv"
)

# Cleaned output file for the HydroGraph-Twin project
output_file = os.path.join(
    DATA_DIR,
    "01_velachery_nodes.csv"
)


# ============================================================
# 2. CHECK INPUT FILE
# ============================================================

print("\nReading original node data...")
print("Input file:")
print(input_file)

if not os.path.exists(input_file):
    print("\nERROR: File not found!")
    print("Please check the exact file name.")
    exit()


# ============================================================
# 3. READ CSV AND SHOW ACTUAL COLUMN NAMES
# ============================================================

with open(input_file, "r", encoding="utf-8-sig") as file:

    reader = csv.DictReader(file)

    print("\nCSV columns found:")
    print(reader.fieldnames)

    # Stop here if the file has no readable columns
    if not reader.fieldnames:
        print("\nERROR: No CSV columns were found.")
        exit()

    # Clean spaces from column names
    reader.fieldnames = [
        column.strip()
        for column in reader.fieldnames
    ]

    print("\nCleaned column names:")
    print(reader.fieldnames)

    # Check which format your CSV has
    if "@id" in reader.fieldnames:

        id_column = "@id"
        name_column = "name"
        latitude_column = "@lat"
        longitude_column = "@lon"

    elif "node_id" in reader.fieldnames:

        id_column = "node_id"
        name_column = "location_name"
        latitude_column = "latitude"
        longitude_column = "longitude"

    else:

        print("\nERROR: This CSV format is not recognised.")
        print("\nPlease send me the output of:")
        print("CSV columns found:")
        print(reader.fieldnames)

        exit()


    # ========================================================
    # 4. CREATE CLEANED NODES
    # ========================================================

    cleaned_nodes = []

    for index, row in enumerate(reader, start=1):

        # Maximum 20 nodes
        if index > 20:
            break

        # Get location name safely
        location_name = row.get(
            name_column,
            ""
        ).strip()

        # If location name is empty, use the ID
        if not location_name:
            location_name = row.get(
                id_column,
                f"Location {index}"
            ).strip()

        # Get node type safely
        node_type = "location_node"

        # Check OpenStreetMap-related columns if available
        if row.get("highway", "").strip():
            node_type = "road_node"

        elif row.get("railway", "").strip():
            node_type = "railway_node"

        elif row.get("amenity", "").strip():
            node_type = row.get(
                "amenity"
            ).strip()

        elif row.get("public_transport", "").strip():
            node_type = "transport_node"


        # Add cleaned node
        cleaned_nodes.append({

            "node_id": f"N{index:03d}",

            "location_name": location_name,

            "latitude": row.get(
                latitude_column,
                ""
            ).strip(),

            "longitude": row.get(
                longitude_column,
                ""
            ).strip(),

            "node_type": node_type
        })


# ============================================================
# 5. SAVE CLEANED CSV
# ============================================================

fieldnames = [
    "node_id",
    "location_name",
    "latitude",
    "longitude",
    "node_type"
]

with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(cleaned_nodes)


# ============================================================
# 6. SUCCESS MESSAGE
# ============================================================

print("\n" + "=" * 50)
print("SUCCESS!")
print("=" * 50)

print("\nCleaned node CSV created successfully!")

print("\nOutput file:")
print(output_file)

print(f"\nTotal nodes created: {len(cleaned_nodes)}")

print("\nYou can now use this file:")
print("01_velachery_nodes.csv")