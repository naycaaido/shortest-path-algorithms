import osmnx as ox
import matplotlib.pyplot as plt
import heapq
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

# Global lists untuk menyimpan geometri jalan (agar garisnya melengkung indah)
lines_astar = []
lines_dijkstra = []

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
        # Heuristik Euclidean
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
                
                # PERBAIKAN: Mengambil geometri lekukan jalan
                if 'geometry' in edge_data:
                    xs, ys = edge_data['geometry'].xy
                    points = list(zip(xs, ys))
                    lines_astar.append(points)
                else:
                    # Fallback jika jalan lurus
                    lines_astar.append([(G.nodes[current]['x'], G.nodes[current]['y']), 
                                        (G.nodes[neighbor]['x'], G.nodes[neighbor]['y'])])
    return None

route_astar = a_star(graph_proj, start_node, end_node)

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
                
                # PERBAIKAN: Mengambil geometri lekukan jalan
                if 'geometry' in edge_data:
                    xs, ys = edge_data['geometry'].xy
                    points = list(zip(xs, ys))
                    lines_dijkstra.append(points)
                else:
                    lines_dijkstra.append([(G.nodes[current]['x'], G.nodes[current]['y']), 
                                           (G.nodes[neighbor]['x'], G.nodes[neighbor]['y'])])
    return None

route_dijkstra = dijkstra(graph_proj, start_node, end_node)

# ==========================================
# STEP 4: VISUALISASI PERBANDINGAN
# ==========================================
print("--- STEP 4: VISUALISASI ---")

# Setup Figure dengan warna Hitam Pekat
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), facecolor='black')

# Setup Tampilan Peta
for ax, title in zip([ax1, ax2], ["DIJKSTRA (Blind Search)", "A-STAR (Heuristic)"]):
    # Paksa background axes menjadi hitam
    ax.set_facecolor('black') 
    
    # Plot graf jalan raya (warna abu-abu gelap agar kontras dengan rute)
    ox.plot_graph(graph_proj, ax=ax, show=False, close=False, 
                  edge_color='#333333', bgcolor='black', node_size=0, edge_linewidth=0.5)
    
    ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=10)
    
    # Marker Lokasi
    ax.scatter(graph_proj.nodes[start_node]['x'], graph_proj.nodes[start_node]['y'], 
               c='red', s=50, zorder=10, label='Start') # Zorder tinggi agar di atas garis
    ax.scatter(graph_proj.nodes[end_node]['x'], graph_proj.nodes[end_node]['y'], 
               c='green', s=50, zorder=10, label='Finish')

# Container Garis Animasi (Eksplorasi)
# zorder=3 memastikan garis ini digambar DI ATAS jalanan (zorder=1), tapi DI BAWAH titik lokasi
lc_dijkstra = LineCollection([], colors='#ff00ff', linewidths=1.0, alpha=0.6, zorder=3)
lc_astar = LineCollection([], colors='#00ffff', linewidths=1.0, alpha=0.6, zorder=3)

ax1.add_collection(lc_dijkstra)
ax2.add_collection(lc_astar)

# Container Garis Final (Kuning)
path_dijkstra, = ax1.plot([], [], c='yellow', lw=3, zorder=5)
path_astar, = ax2.plot([], [], c='yellow', lw=3, zorder=5)

def update(frame):
    # Percepatan: 50 segmen per frame
    step = frame * 50 
    
    # Update Dijkstra (Kiri)
    if step < len(lines_dijkstra):
        lc_dijkstra.set_segments(lines_dijkstra[:step])
    elif route_dijkstra:
        # Gambar rute final jika eksplorasi selesai
        rx = [graph_proj.nodes[n]['x'] for n in route_dijkstra]
        ry = [graph_proj.nodes[n]['y'] for n in route_dijkstra]
        path_dijkstra.set_data(rx, ry)
        
        lc_dijkstra.set_segments([])

    # Update A* (Kanan)
    if step < len(lines_astar):
        lc_astar.set_segments(lines_astar[:step])
    elif route_astar:
        # Gambar rute final jika eksplorasi selesai
        rx = [graph_proj.nodes[n]['x'] for n in route_astar]
        ry = [graph_proj.nodes[n]['y'] for n in route_astar]
        path_astar.set_data(rx, ry)
        
        lc_astar.set_segments([])

    return lc_dijkstra, lc_astar, path_dijkstra, path_astar

# Hitung frame agar animasi tidak kepanjangan/kependekan
max_frames = max(len(lines_dijkstra), len(lines_astar)) // 50 + 20

print("Memulai animasi window...")
ani = FuncAnimation(fig, update, frames=max_frames, interval=30, blit=True, repeat=False)

plt.tight_layout()
plt.show()