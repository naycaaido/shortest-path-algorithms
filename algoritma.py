import heapq
import math
from typing import List, Tuple, Dict, Any, Optional

# Tipe data custom
Coord = Tuple[float, float]
Path = List[int]
GeometryLine = List[Coord]

def calculate_path_distance(graph: Any, path: Path) -> float:
    """Menghitung total jarak jalur dalam meter."""
    if not path:
        return 0.0
    total_dist = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        edge_data = graph.get_edge_data(u, v)[0]
        total_dist += edge_data.get('length', 0.0)
    return total_dist

def _heuristic(graph: Any, u: int, v: int) -> float:
    """Menghitung Euclidean Distance antara dua node."""
    x1, y1 = graph.nodes[u]['x'], graph.nodes[u]['y']
    x2, y2 = graph.nodes[v]['x'], graph.nodes[v]['y']
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def _get_edge_geometry(graph: Any, u: int, v: int) -> GeometryLine:
    """Mengambil koordinat garis antara dua node."""
    edge_data = graph.get_edge_data(u, v)[0]
    if 'geometry' in edge_data:
        xs, ys = edge_data['geometry'].xy
        return list(zip(xs, ys))
    else:
        p1 = (graph.nodes[u]['x'], graph.nodes[u]['y'])
        p2 = (graph.nodes[v]['x'], graph.nodes[v]['y'])
        return [p1, p2]

def run_dijkstra(graph: Any, start: int, target: int) -> Tuple[Optional[Path], List[GeometryLine]]:
    """Implementasi murni Algoritma Dijkstra."""
    open_list = [(0, start)]
    g_score = {node: float('inf') for node in graph.nodes()}
    g_score[start] = 0
    parent_map = {}
    explored_visuals = []

    while open_list:
        current_g, current = heapq.heappop(open_list)
        if current == target:
            path = []
            while current in parent_map:
                path.append(current)
                current = parent_map[current]
            path.append(start)
            return path[::-1], explored_visuals

        for neighbor in graph.neighbors(current):
            weight = graph.get_edge_data(current, neighbor)[0].get('length', 1.0)
            new_g = g_score[current] + weight
            if new_g < g_score[neighbor]:
                parent_map[neighbor] = current
                g_score[neighbor] = new_g
                heapq.heappush(open_list, (new_g, neighbor))
                explored_visuals.append(_get_edge_geometry(graph, current, neighbor))
    return None, explored_visuals

def run_a_star(graph: Any, start: int, target: int) -> Tuple[Optional[Path], List[GeometryLine]]:
    """Implementasi murni Algoritma A*."""
    open_list = [(0, start)]
    g_score = {node: float('inf') for node in graph.nodes()}
    g_score[start] = 0
    parent_map = {}
    explored_visuals = []

    while open_list:
        current_f, current = heapq.heappop(open_list)
        if current == target:
            path = []
            while current in parent_map:
                path.append(current)
                current = parent_map[current]
            path.append(start)
            return path[::-1], explored_visuals

        for neighbor in graph.neighbors(current):
            weight = graph.get_edge_data(current, neighbor)[0].get('length', 1.0)
            temp_g = g_score[current] + weight
            if temp_g < g_score[neighbor]:
                parent_map[neighbor] = current
                g_score[neighbor] = temp_g
                f_score = temp_g + _heuristic(graph, neighbor, target)
                heapq.heappush(open_list, (f_score, neighbor))
                explored_visuals.append(_get_edge_geometry(graph, current, neighbor))
    return None, explored_visuals