import osmnx as ox
from typing import Tuple, Any

def load_street_graph(center_point: Tuple[float, float], dist: int = 2000, network_type: str = 'drive') -> Tuple[Any, Any]:
    """
    Mendownload data jalan.
    
    Returns:
        (graph_latlong, graph_projected)
        - graph_latlong: Untuk mencari node berdasarkan koordinat GPS.
        - graph_projected: Untuk menghitung jarak akurat dalam meter (A*/Dijkstra).
    """
    print(f"--- Loading Map Data ({dist}m radius) ---")
    try:
        # 1. Download graph mentah (Satuan: Derajat/LatLong)
        graph = ox.graph_from_point(center_point, dist=dist, network_type=network_type)
        
        # 2. Proyeksi graph (Satuan: Meter)
        graph_proj = ox.project_graph(graph)
        
        # Kembalikan keduanya
        return graph, graph_proj
    
    except Exception as e:
        print(f"Error saat mendownload peta: {e}")
        return None, None

def find_start_end_nodes(graph: Any, start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Tuple[int, int]:
    """
    Mencari node terdekat.
    PENTING: Gunakan graph yang belum diproyeksikan (Lat/Long)!
    """
    # ox.nearest_nodes butuh (X, Y) -> (Longitude, Latitude)
    
    start_node = ox.distance.nearest_nodes(graph, start_coords[1], start_coords[0])
    end_node = ox.distance.nearest_nodes(graph, end_coords[1], end_coords[0])
    
    return start_node, end_node
