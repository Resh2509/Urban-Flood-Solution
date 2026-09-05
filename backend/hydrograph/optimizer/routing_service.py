import osmnx as ox
import networkx as nx
import json
import sys


# ============================================================
# FLOOD PENALTY
# ============================================================

def flood_penalty(depth_cm):

    if depth_cm <= 10:
        return 1.0

    elif depth_cm <= 30:
        return 3.0

    elif depth_cm <= 50:
        return 10.0

    else:
        # More than 50 cm = road is blocked
        return None


# ============================================================
# GET OSM ROAD NETWORK
# ============================================================

def get_road_graph(latitude, longitude):

    print(
        "Downloading OSM road network...",
        file=sys.stderr
    )

    G = ox.graph.graph_from_point(
        (latitude, longitude),
        dist=3000,
        network_type="drive",
        simplify=True
    )

    print(
        "Road network downloaded.",
        file=sys.stderr
    )

    return G


# ============================================================
# FIND NEAREST ROAD NODE
# ============================================================

def find_nearest_node(G, latitude, longitude):

    return ox.distance.nearest_nodes(
        G,
        X=longitude,
        Y=latitude
    )


# ============================================================
# CALCULATE FLOOD-AWARE EDGE COST
# ============================================================

def calculate_edge_cost(edge_data):

    length = float(
        edge_data.get(
            "length",
            1
        )
    )

    flood_depth = float(
        edge_data.get(
            "flood_depth_cm",
            0
        )
    )

    penalty = flood_penalty(
        flood_depth
    )

    if penalty is None:
        return None

    return length * penalty


# ============================================================
# ADD FLOOD INFORMATION TO ROAD NETWORK
# ============================================================

def add_flood_weights(G, flooded_edges):

    flooded_lookup = {}

    for edge in flooded_edges:

        u = int(edge["u"])
        v = int(edge["v"])

        depth = float(
            edge["depth_cm"]
        )

        flooded_lookup[(u, v)] = depth


    print(
        "Flooded road segments:",
        file=sys.stderr
    )


    for u, v, key, data in G.edges(
        keys=True,
        data=True
    ):

        depth = flooded_lookup.get(
            (u, v),
            0
        )

        data["flood_depth_cm"] = depth

        data["flood_cost"] = (
            calculate_edge_cost(data)
        )

        if depth > 0:

            print(
                f"{u} -> {v} | "
                f"Depth: {depth} cm",
                file=sys.stderr
            )


# ============================================================
# A* WEIGHT FUNCTION
# ============================================================

def flood_aware_weight(u, v, data):

    if "flood_cost" in data:

        return data["flood_cost"]

    return data.get(
        "length",
        1
    )


# ============================================================
# GET FLOODED ROAD COORDINATES
# ============================================================

def get_flooded_segments(
    G,
    flooded_edges
):

    flooded_segments = []


    for flooded_edge in flooded_edges:

        u = int(
            flooded_edge["u"]
        )

        v = int(
            flooded_edge["v"]
        )

        depth = float(
            flooded_edge["depth_cm"]
        )


        if not G.has_edge(u, v):

            continue


        edge_collection = G.get_edge_data(
            u,
            v
        )


        for key, data in edge_collection.items():

            coordinates = []


            if "geometry" in data:

                geometry = data["geometry"]

                coordinates = [
                    [lat, lon]
                    for lon, lat
                    in geometry.coords
                ]

            else:

                u_data = G.nodes[u]

                v_data = G.nodes[v]

                coordinates = [

                    [
                        u_data["y"],
                        u_data["x"]
                    ],

                    [
                        v_data["y"],
                        v_data["x"]
                    ]

                ]


            flooded_segments.append({

                "u": u,

                "v": v,

                "key": key,

                "depth_cm": depth,

                "coordinates":
                    coordinates

            })


    return flooded_segments


# ============================================================
# CONVERT ROUTE NODES TO LATITUDE/LONGITUDE
# ============================================================

def route_to_coordinates(
    G,
    route
):

    coordinates = []


    for node in route:

        node_data = G.nodes[node]

        coordinates.append([
            node_data["y"],
            node_data["x"]
        ])


    return coordinates


# ============================================================
# CALCULATE FLOOD-AWARE ROUTE
# ============================================================

def calculate_route(

    worker_latitude,
    worker_longitude,

    task_latitude,
    task_longitude,

    flooded_edges

):

    # Download road network

    G = get_road_graph(
        worker_latitude,
        worker_longitude
    )


    # Find worker road node

    origin = find_nearest_node(
        G,
        worker_latitude,
        worker_longitude
    )


    # Find destination road node

    destination = find_nearest_node(
        G,
        task_latitude,
        task_longitude
    )


    print(
        f"Origin node: {origin}",
        file=sys.stderr
    )


    print(
        f"Destination node: {destination}",
        file=sys.stderr
    )


    # Add flood information

    add_flood_weights(
        G,
        flooded_edges
    )


    # Get flooded road geometry

    flooded_segments = (
        get_flooded_segments(
            G,
            flooded_edges
        )
    )


    # Run A*

    route = nx.astar_path(

        G,

        origin,

        destination,

        weight=flood_aware_weight

    )


    # Convert route to coordinates

    route_coordinates = route_to_coordinates(
        G,
        route
    )


    print(
        "Flood-aware route found:",
        file=sys.stderr
    )


    print(
        route,
        file=sys.stderr
    )


    return (
        route,
        route_coordinates,
        flooded_segments
    )


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        # Read JSON from Node.js

        input_text = sys.stdin.read()


        if not input_text.strip():

            raise ValueError(
                "No input received."
            )


        data = json.loads(
            input_text
        )


        # Worker data

        worker = data["worker"]


        # Task data

        task = data["task"]


        # Flood data

        flooded_edges = data.get(
            "flooded_edges",
            []
        )


        # Calculate route

        route, route_coordinates, flooded_segments = calculate_route(

            float(
                worker["latitude"]
            ),

            float(
                worker["longitude"]
            ),

            float(
                task["latitude"]
            ),

            float(
                task["longitude"]
            ),

            flooded_edges

        )


        # Final response

        result = {

            "success": True,

            "worker_id":
                worker["worker_id"],

            "task_id":
                task["task_id"],

            "route":
                route,

            "route_coordinates":
                route_coordinates,

            "flooded_segments":
                flooded_segments

        }


        # IMPORTANT:
        # Only JSON goes to stdout

        print(
            json.dumps(result)
        )


    except Exception as error:

        print(
            str(error),
            file=sys.stderr
        )


        print(
            json.dumps({

                "success": False,

                "error":
                    str(error)

            })
        )


        sys.exit(1)


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()