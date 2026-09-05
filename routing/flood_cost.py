import networkx as nx

def update_flood_costs(G: nx.Graph, node_flood_depths: dict) -> nx.Graph:
    """
    Applies dynamic cost penalties to road edges based on water accumulation depth.
    - Safe road (< 5cm): normal cost (weight = distance)
    - Warning road (5 - 15cm): 3x cost penalty
    - Critical road (> 15cm): 50x penalty / Avoid
    """
    for u, v, data in G.edges(data=True):
        d_u = node_flood_depths.get(u, 0.0)
        d_v = node_flood_depths.get(v, 0.0)
        max_depth = max(d_u, d_v)
        data["flood_depth_cm"] = max_depth

        if max_depth >= 15.0:
            data["cost"] = data["base_distance"] * 50.0  # Severely avoid
            data["risk_level"] = "Critical"
        elif max_depth >= 5.0:
            data["cost"] = data["base_distance"] * 3.0   # High friction
            data["risk_level"] = "Moderate"
        else:
            data["cost"] = data["base_distance"] * 1.0   # Safe road
            data["risk_level"] = "Safe"

    return G