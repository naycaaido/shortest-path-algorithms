import osmnx as ox
import matplotlib.pyplot as plt
import heapq
import time  # Import module time untuk menghitung durasi
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection

# ==========================================
# STEP 1: PENGAMBILAN DATA
# ==========================================
print("--- STEP 1: PENGAMBILAN DATA ---")
coords_sate = (-6.9025, 107.6188)
coords_unikom = (-6.8865, 107.6153)

# Download peta (menggunakan network_type='drive' agar jalan raya saja)
graph = ox.graph_from_point(coords_sate, dist=2000, network_type='drive')

# Mapping titik koordinat ke Node terdekat
start_node = ox.distance.nearest_nodes(graph, coords_sate[1], coords_sate[0])
end_node = ox.distance.nearest_nodes(graph, coords_unikom[1], coords_unikom[0])

graph_proj = ox.project_graph(graph)

# Global lists untuk menyimpan geometri jalan
lines_astar = []
lines_dijkstra = []

# Fungsi Tambahan: Menghitung Total Jarak (Akurasi) dalam Meter
def calculate_path_distance(G, path):
    if not path: return 0
    total_dist = 0
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        # Mengambil data edge (jalan) antar dua node
        edge_data = G.get_edge_data(u, v)[0]
        total_dist += edge_data.get('length', 0)
    return total_dist

# ==========================================
# STEP 2: ALGORITMA A* (HEURISTIC)
# ==========================================
print("--- STEP 2: MENJALANKAN ALGORITMA A* ---")

def a_star(G, start, target):
    g_score = {node: float('inf') for node in G.nodes()}
    g_score[start] = 0
    open_list = [(0, start)]
    parent_map = {}

    def h(u, v):
        return ((G.nodes[u]['x'] - G.nodes[v]['x'])**2 + 
                (G.nodes[u]['y'] - G.nodes[v]['y'])**2)**0.5

    while open_list:
        current_f, current = heapq.heappop(open_list)
        if current == target:
            path = []
            while current in parent_map:
                path.append(current)
                current = parent_map[current]
            path.append(start)
            return path[::-1]

        for neighbor in G.neighbors(current):
            edge_data = G.get_edge_data(current, neighbor)[0]
            weight = edge_data.get('length', 1)
            temp_g = g_score[current] + weight

            if temp_g < g_score[neighbor]:
                parent_map[neighbor] = current
                g_score[neighbor] = temp_g
                f_score = temp_g + h(neighbor, target)
                heapq.heappush(open_list, (f_score, neighbor))
                
                if 'geometry' in edge_data:
                    xs, ys = edge_data['geometry'].xy
                    lines_astar.append(list(zip(xs, ys)))
                else:
                    lines_astar.append([(G.nodes[current]['x'], G.nodes[current]['y']), 
                                        (G.nodes[neighbor]['x'], G.nodes[neighbor]['y'])])
    return None

# --- EKSEKUSI & PENGUKURAN A* ---
start_time_astar = time.time()  # Mulai Timer
route_astar = a_star(graph_proj, start_node, end_node)
end_time_astar = time.time()    # Stop Timer

time_astar = end_time_astar - start_time_astar
dist_astar = calculate_path_distance(graph_proj, route_astar)
explored_astar = len(lines_astar)

print(f"A* Selesai: {time_astar:.4f} detik | Jarak: {dist_astar:.2f} m | Eksplorasi: {explored_astar} segmen")

# ==========================================
# STEP 3: ALGORITMA DIJKSTRA (BLIND)
# ==========================================
print("--- STEP 3: MENJALANKAN ALGORITMA DIJKSTRA ---")

def dijkstra(G, start, target):
    g_score = {node: float('inf') for node in G.nodes()}
    g_score[start] = 0
    open_list = [(0, start)] 
    parent_map = {}

    while open_list:
        current_g, current = heapq.heappop(open_list)
        if current == target:
            path = []
            while current in parent_map:
                path.append(current)
                current = parent_map[current]
            path.append(start)
            return path[::-1]

        for neighbor in G.neighbors(current):
            edge_data = G.get_edge_data(current, neighbor)[0]
            weight = edge_data.get('length', 1)
            temp_g = g_score[current] + weight

            if temp_g < g_score[neighbor]:
                parent_map[neighbor] = current
                g_score[neighbor] = temp_g
                heapq.heappush(open_list, (temp_g, neighbor))
                
                if 'geometry' in edge_data:
                    xs, ys = edge_data['geometry'].xy
                    lines_dijkstra.append(list(zip(xs, ys)))
                else:
                    lines_dijkstra.append([(G.nodes[current]['x'], G.nodes[current]['y']), 
                                           (G.nodes[neighbor]['x'], G.nodes[neighbor]['y'])])
    return None

# --- EKSEKUSI & PENGUKURAN DIJKSTRA ---
start_time_dijkstra = time.time() # Mulai Timer
route_dijkstra = dijkstra(graph_proj, start_node, end_node)
end_time_dijkstra = time.time()   # Stop Timer

time_dijkstra = end_time_dijkstra - start_time_dijkstra
dist_dijkstra = calculate_path_distance(graph_proj, route_dijkstra)
explored_dijkstra = len(lines_dijkstra)

print(f"Dijkstra Selesai: {time_dijkstra:.4f} detik | Jarak: {dist_dijkstra:.2f} m | Eksplorasi: {explored_dijkstra} segmen")

# ==========================================
# STEP 4: VISUALISASI DENGAN STATISTIK
# ==========================================
print("--- STEP 4: VISUALISASI ---")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), facecolor='black')

# Loop untuk setup tampilan dasar
for ax, title, stats in zip(
    [ax1, ax2], 
    ["DIJKSTRA (Blind Search)", "A-STAR (Heuristic)"],
    [
        (time_dijkstra, explored_dijkstra, dist_dijkstra), # Data Dijkstra
        (time_astar, explored_astar, dist_astar)           # Data A*
    ]
):
    ax.set_facecolor('black')
    ox.plot_graph(graph_proj, ax=ax, show=False, close=False, 
                  edge_color='#333333', bgcolor='black', node_size=0, edge_linewidth=0.5)
    
    ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=10)
    
    ax.scatter(graph_proj.nodes[start_node]['x'], graph_proj.nodes[start_node]['y'], 
               c='red', s=50, zorder=10, label='Start')
    ax.scatter(graph_proj.nodes[end_node]['x'], graph_proj.nodes[end_node]['y'], 
               c='green', s=50, zorder=10, label='Finish')

    # --- MENAMPILKAN TEXT STATISTIK DI LAYAR ---
    t_exec, n_exp, d_total = stats
    info_text = (
        f"Time: {t_exec:.4f} s\n"
        f"Explored: {n_exp} segmen\n"
        f"Distance: {d_total/1000:.2f} km"
    )
    # Menempatkan text box di pojok kiri bawah (coordinate 0.03, 0.03 relative to axes)
    ax.text(0.03, 0.03, info_text, transform=ax.transAxes, 
            color='white', fontsize=10, verticalalignment='bottom',
            bbox=dict(facecolor='black', alpha=0.7, edgecolor='white', boxstyle='round,pad=0.5'))

lc_dijkstra = LineCollection([], colors='#ff00ff', linewidths=1.0, alpha=0.6, zorder=3)
lc_astar = LineCollection([], colors='#00ffff', linewidths=1.0, alpha=0.6, zorder=3)

ax1.add_collection(lc_dijkstra)
ax2.add_collection(lc_astar)

path_dijkstra, = ax1.plot([], [], c='yellow', lw=3, zorder=5)
path_astar, = ax2.plot([], [], c='yellow', lw=3, zorder=5)

def update(frame):
    step = frame * 50 
    
    # Update Dijkstra
    if step < len(lines_dijkstra):
        lc_dijkstra.set_segments(lines_dijkstra[:step])
    elif route_dijkstra:
        rx = [graph_proj.nodes[n]['x'] for n in route_dijkstra]
        ry = [graph_proj.nodes[n]['y'] for n in route_dijkstra]
        path_dijkstra.set_data(rx, ry)
        lc_dijkstra.set_segments([])

    # Update A*
    if step < len(lines_astar):
        lc_astar.set_segments(lines_astar[:step])
    elif route_astar:
        rx = [graph_proj.nodes[n]['x'] for n in route_astar]
        ry = [graph_proj.nodes[n]['y'] for n in route_astar]
        path_astar.set_data(rx, ry)
        lc_astar.set_segments([])

    return lc_dijkstra, lc_astar, path_dijkstra, path_astar

max_frames = max(len(lines_dijkstra), len(lines_astar)) // 50 + 20
print("Memulai animasi window...")
ani = FuncAnimation(fig, update, frames=max_frames, interval=30, blit=True, repeat=False)

plt.tight_layout()
plt.show()