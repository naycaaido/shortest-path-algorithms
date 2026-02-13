import time
import peta       
import algoritma  
from visualizer import GraphVisualizer 

COORDS_SATE = (-6.9025, 107.6188)
COORDS_UNIKOM = (-6.8865, 107.6153)

def run_benchmark(name, algo_function, graph, start, end):
    print(f"--- Menjalankan {name} ---")
    start_time = time.time()
    route, explored_lines = algo_function(graph, start, end)
    duration = time.time() - start_time
    distance = algoritma.calculate_path_distance(graph, route)
    
    stats = {'time': duration, 'distance': distance, 'explored': len(explored_lines)}
    print(f"✅ {name} Selesai: {duration:.4f}s | Jarak: {distance:.2f}m")
    return route, explored_lines, stats

def main():
    graph_latlong, graph_proj = peta.load_street_graph(COORDS_SATE) 
    if not graph_latlong or not graph_proj: return

    start_node, end_node = peta.find_start_end_nodes(graph_latlong, COORDS_SATE, COORDS_UNIKOM)
    viz = GraphVisualizer(graph_proj, start_node, end_node)

    # Memanggil run_dijkstra dari algoritma.py
    path_d, expl_d, stats_d = run_benchmark("Dijkstra", algoritma.run_dijkstra, graph_proj, start_node, end_node)
    viz.register_algorithm("Dijkstra", path_d, expl_d, '#ff00ff', stats_d)

    # Memanggil run_a_star dari algoritma.py
    path_a, expl_a, stats_a = run_benchmark("A-Star", algoritma.run_a_star, graph_proj, start_node, end_node)
    viz.register_algorithm("A-Star", path_a, expl_a, '#00ffff', stats_a)

    viz.show_animation()

if __name__ == "__main__":
    main()