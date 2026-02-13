import heapq
import math
from typing import List, Tuple, Dict, Any, Optional

# Tipe data custom untuk memudahkan pembacaan
Coord = Tuple[float, float]
Path = List[int]
GeometryLine = List[Coord]

def calculate_path_distance(graph: Any, path: Path) -> float:
    """
    Menghitung total jarak jalur dalam meter.
    """
    if not path:
        return 0.0
    
    total_dist = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        # Mengambil data edge pertama (0)
        edge_data = graph.get_edge_data(u, v)[0]
        total_dist += edge_data.get('length', 0.0)
        
    return total_dist

def _heuristic(graph: Any, u: int, v: int) -> float:
    """Menghitung Euclidean Distance antara dua node."""
    x1, y1 = graph.nodes[u]['x'], graph.nodes[u]['y']
    x2, y2 = graph.nodes[v]['x'], graph.nodes[v]['y']
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def _get_edge_geometry(graph: Any, u: int, v: int) -> GeometryLine:
    """Mengambil koordinat garis (geometry) antara dua node untuk visualisasi."""
    edge_data = graph.get_edge_data(u, v)[0]
    
    if 'geometry' in edge_data:
        xs, ys = edge_data['geometry'].xy
        return list(zip(xs, ys))
    else:
        # Jika tidak ada info geometri detail, buat garis lurus
        p1 = (graph.nodes[u]['x'], graph.nodes[u]['y'])
        p2 = (graph.nodes[v]['x'], graph.nodes[v]['y'])
        return [p1, p2]

def _search_algorithm(graph: Any, start: int, target: int, use_heuristic: bool = False) -> Tuple[Optional[Path], List[GeometryLine]]:
    """
    Fungsi inti pencarian jalur (Core Logic).
    Jika use_heuristic=True -> Berperilaku sebagai A*.
    Jika use_heuristic=False -> Berperilaku sebagai Dijkstra.
    
    Returns:
        (path, explored_lines_for_visualization)
    """
    # Priority Queue: (priority_score, current_node)
    open_list = [(0, start)]
    
    # Dictionary untuk melacak cost dan parent
    g_score = {node: float('inf') for node in graph.nodes()}
    g_score[start] = 0
    parent_map = {}
    
    # List lokal untuk menyimpan data visualisasi (pengganti global variable)
    explored_visuals = []

    while open_list:
        current_f, current = heapq.heappop(open_list)

        # Jika sampai tujuan
        if current == target:
            path = []
            while current in parent_map:
                path.append(current)
                current = parent_map[current]
            path.append(start)
            return path[::-1], explored_visuals

        for neighbor in graph.neighbors(current):
            edge_data = graph.get_edge_data(current, neighbor)[0]
            weight = edge_data.get('length', 1)
            temp_g = g_score[current] + weight

            if temp_g < g_score[neighbor]:
                parent_map[neighbor] = current
                g_score[neighbor] = temp_g
                
                # Kalkulasi Priority
                h_val = _heuristic(graph, neighbor, target) if use_heuristic else 0
                f_score = temp_g + h_val
                
                heapq.heappush(open_list, (f_score, neighbor))
                
                # Simpan geometri untuk animasi
                geom = _get_edge_geometry(graph, current, neighbor)
                explored_visuals.append(geom)
                
    return None, explored_visuals

# --- PUBLIC FUNCTIONS (Wrapper) ---

def run_dijkstra(graph: Any, start: int, target: int) -> Tuple[Optional[Path], List[GeometryLine]]:
    """Menjalankan algoritma Dijkstra (Blind Search)."""
    return _search_algorithm(graph, start, target, use_heuristic=False)

def run_a_star(graph: Any, start: int, target: int) -> Tuple[Optional[Path], List[GeometryLine]]:
    """Menjalankan algoritma A* (Heuristic Search)."""
    return _search_algorithm(graph, start, target, use_heuristic=True)