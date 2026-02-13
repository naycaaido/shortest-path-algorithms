import time
import peta       
import algoritma  
from visualizer import GraphVisualizer 

# Konfigurasi
COORDS_SATE = (-6.9025, 107.6188)
COORDS_UNIKOM = (-6.8865, 107.6153)

def run_benchmark(name, algo_function, graph, start, end):
    print(f"--- Menjalankan {name} ---")
    start_time = time.time()
    
    route, explored_lines = algo_function(graph, start, end)
    
    duration = time.time() - start_time
    distance = algoritma.calculate_path_distance(graph, route)
    
    stats = {
        'time': duration,
        'distance': distance,
        'explored': len(explored_lines)
    }
    
    print(f"✅ {name} Selesai: {duration:.4f}s | Jarak: {distance:.2f}m | Eksplorasi: {len(explored_lines)}")
    return route, explored_lines, stats

def main():
    # 1. Load Data
    # PERBAIKAN DI SINI: Kita unpack menjadi 2 variabel
    graph_latlong, graph_proj = peta.load_street_graph(COORDS_SATE) 
    
    # Cek jika salah satu gagal (None)
    if not graph_latlong or not graph_proj: 
        return

    # 2. Cari Node (Gunakan graph_latlong karena koordinat inputnya Lat/Long)
    start_node, end_node = peta.find_start_end_nodes(graph_latlong, COORDS_SATE, COORDS_UNIKOM)

    # 3. Inisialisasi Visualizer (Gunakan graph_proj untuk visualisasi & hitung jarak meter)
    viz = GraphVisualizer(graph_proj, start_node, end_node)

    # 4. Jalankan Dijkstra (Pakai graph_proj)
    path_d, expl_d, stats_d = run_benchmark(
        "Dijkstra", algoritma.run_dijkstra, graph_proj, start_node, end_node
    )
    viz.register_algorithm("Dijkstra", path_d, expl_d, '#ff00ff', stats_d)

    # 5. Jalankan A* (Pakai graph_proj)
    path_a, expl_a, stats_a = run_benchmark(
        "A-Star", algoritma.run_a_star, graph_proj, start_node, end_node
    )
    viz.register_algorithm("A-Star", path_a, expl_a, '#00ffff', stats_a)

    # 6. Tampilkan Hasil
    viz.show_animation()

if __name__ == "__main__":
    main()