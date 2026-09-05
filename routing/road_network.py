import math
import networkx as nx

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0  # meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def build_velachery_road_network() -> nx.Graph:
    """Builds a connected graph for Velachery road network with coordinates."""
    G = nx.Graph()
    
    # Velachery Node Coordinates
    nodes = {
        "N001": (12.978625, 80.221580, "Velachery Vijaya Nagar"),
        "N002": (12.977460, 80.223450, "Tansi Nagar"),
        "N003": (12.967299, 80.219571, "Velachery Main Canal"),
        "N004": (12.982980, 80.221970, "Dhandeeswaram"),
        "N005": (12.980170, 80.222850, "Velachery Main Road"),
        "N006": (12.967299, 80.219571, "Velachery Railway Station"),
        "N007": (12.965273, 80.207104, "Ram Nagar"),
        "N008": (12.978550, 80.225360, "Tansi Nagar Bus Stop"),
        "N009": (12.975951, 80.221066, "Velachery Bus Terminus"),
        "N010": (12.975950, 80.221070, "Vijaynagar Area"),
        "N011": (12.985790, 80.220750, "Velachery Lake"),
        "N012": (12.965356, 80.211813, "Ram Nagar Canal"),
        "N013": (12.965129, 80.202854, "Sadasiva Nagar"),
        "N014": (12.981010, 80.206669, "Andal Nagar"),
        "N015": (12.985279, 80.204976, "Subramanya Temple"),
        "N016": (12.983521, 80.192115, "Guruvayurappan temple"),
        "N017": (12.989388, 80.201710, "Vinayaka Temple"),
        "N018": (12.967300, 80.219570, "Velachery Station Area"),
        "N019": (12.982870, 80.222010, "Dhandeeswaram Extension"),
        "N020": (12.975951, 80.221066, "Vijayanagar Velachery")
    }

    for nid, (lat, lon, name) in nodes.items():
        G.add_node(nid, lat=lat, lon=lon, name=name)

    # Road Segments connecting intersections and streets
    road_edges = [
        ("N001", "N002"), ("N002", "N008"), ("N001", "N004"), ("N004", "N005"),
        ("N005", "N009"), ("N009", "N010"), ("N010", "N020"), ("N009", "N003"),
        ("N003", "N006"), ("N006", "N018"), ("N006", "N012"), ("N012", "N007"),
        ("N007", "N013"), ("N013", "N016"), ("N004", "N011"), ("N011", "N015"),
        ("N015", "N017"), ("N015", "N014"), ("N014", "N001"), ("N004", "N019"),
        ("N019", "N020"), ("N010", "N012"), ("N005", "N010"), ("N008", "N009")
    ]

    for u, v in road_edges:
        lat1, lon1 = G.nodes[u]["lat"], G.nodes[u]["lon"]
        lat2, lon2 = G.nodes[v]["lat"], G.nodes[v]["lon"]
        dist = haversine_distance(lat1, lon1, lat2, lon2)
        G.add_edge(u, v, base_distance=dist, flood_depth_cm=0.0, blocked=False)

    return G