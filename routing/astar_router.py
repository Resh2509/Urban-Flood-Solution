import networkx as nx
from routing.road_network import haversine_distance

def heuristic(u: str, v: str, G: nx.Graph) -> float:
    lat1, lon1 = G.nodes[u]["lat"], G.nodes[u]["lon"]
    lat2, lon2 = G.nodes[v]["lat"], G.nodes[v]["lon"]
    return haversine_distance(lat1, lon1, lat2, lon2)

def find_flood_aware_route(G: nx.Graph, source: str, target: str):
    """
    Computes standard shortest path vs flood-aware safe alternate path using A*.
    """
    try:
        # Standard Shortest Route (Ignoring Flood Risk)
        standard_path = nx.astar_path(G, source, target, heuristic=lambda u, v: heuristic(u, v, G), weight="base_distance")
        standard_dist = sum(G[u][v]["base_distance"] for u, v in zip(standard_path[:-1], standard_path[1:]))

        # Flood-Aware Route (Penalizing Inundated Segments)
        safe_path = nx.astar_path(G, source, target, heuristic=lambda u, v: heuristic(u, v, G), weight="cost")
        safe_dist = sum(G[u][v]["base_distance"] for u, v in zip(safe_path[:-1], safe_path[1:]))
        
        max_flood_encountered = max(
            [G[u][v].get("flood_depth_cm", 0.0) for u, v in zip(safe_path[:-1], safe_path[1:])] or [0.0]
        )

        return {
            "source": source,
            "target": target,
            "standard_path": " -> ".join(standard_path),
            "safe_path": " -> ".join(safe_path),
            "safe_distance_m": round(safe_dist, 2),
            "max_flood_depth_cm": round(max_flood_encountered, 2),
            "route_status": "Alternative Safe Route" if safe_path != standard_path else "Direct Route"
        }
    except nx.NetworkXNoPath:
        return {
            "source": source,
            "target": target,
            "standard_path": "None",
            "safe_path": "No accessible safe route",
            "safe_distance_m": 0.0,
            "max_flood_depth_cm": 999.0,
            "route_status": "Blocked"
        }