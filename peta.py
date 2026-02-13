import osmnx as ox
from typing import Tuple, Any

def load_street_graph(center_point: Tuple[float, float], dist: int = 2000, network_type: str = 'drive') -> Tuple[Any, Any]:
    print(f"--- Loading Map Data ({dist}m radius) ---")
    try:
        graph = ox.graph_from_point(center_point, dist=dist, network_type=network_type)
        
        graph_proj = ox.project_graph(graph)
        
        return graph, graph_proj
    
    except Exception as e:
        print(f"Error saat mendownload peta: {e}")
        return None, None

def find_start_end_nodes(graph: Any, start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Tuple[int, int]:
    
    start_node = ox.distance.nearest_nodes(graph, start_coords[1], start_coords[0])
    end_node = ox.distance.nearest_nodes(graph, end_coords[1], end_coords[0])
    
    return start_node, end_node
