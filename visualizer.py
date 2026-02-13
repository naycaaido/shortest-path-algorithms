import matplotlib.pyplot as plt
import osmnx as ox
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection

class GraphVisualizer:
    def __init__(self, graph, start_node, end_node):
        self.graph = graph
        self.start_node = start_node
        self.end_node = end_node
        
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(14, 7), facecolor='black')
        self.ax_map = {
            'Dijkstra': self.ax1,
            'A-Star': self.ax2
        }
        self.data_store = {}
        
    def setup_axis(self, algo_name, stats):
        """Menyiapkan tampilan awal peta dan teks statistik."""
        if algo_name not in self.ax_map: return
        
        ax = self.ax_map[algo_name]
        ax.set_facecolor('black')
        
        ox.plot_graph(self.graph, ax=ax, show=False, close=False, 
                      edge_color='#333333', bgcolor='black', node_size=0, edge_linewidth=0.5)
        
        ax.set_title(algo_name, color='white', fontsize=14, fontweight='bold', pad=10)
        ax.scatter(self.graph.nodes[self.start_node]['x'], self.graph.nodes[self.start_node]['y'], 
                   c='red', s=50, zorder=10, label='Start')
        ax.scatter(self.graph.nodes[self.end_node]['x'], self.graph.nodes[self.end_node]['y'], 
                   c='green', s=50, zorder=10, label='Finish')

        info_text = (
            f"Time: {stats['time']:.4f} s\n"
            f"Explored: {stats['explored']} segmen\n"
            f"Distance: {stats['distance']/1000:.2f} km"
        )
        ax.text(0.03, 0.03, info_text, transform=ax.transAxes, 
                color='white', fontsize=10, verticalalignment='bottom',
                bbox=dict(facecolor='black', alpha=0.7, edgecolor='white', boxstyle='round,pad=0.5'))

    def register_algorithm(self, name, path, explored_lines, color, stats):
        self.setup_axis(name, stats)
        
        lc = LineCollection([], colors=color, linewidths=1.0, alpha=0.6, zorder=3)
        self.ax_map[name].add_collection(lc)
        
        path_line, = self.ax_map[name].plot([], [], c='yellow', lw=3, zorder=5)
        
        self.data_store[name] = {
            'explored': explored_lines,
            'path': path,
            'lc': lc,
            'path_line': path_line
        }

    def _update_frame(self, frame):
        step = frame * 50
        artists = []
        
        for name, data in self.data_store.items():
            explored = data['explored']
            final_path = data['path']
            lc = data['lc']
            path_line = data['path_line']
            
            
            if step < len(explored):
                lc.set_segments(explored[:step])
            
            elif final_path:
                rx = [self.graph.nodes[n]['x'] for n in final_path]
                ry = [self.graph.nodes[n]['y'] for n in final_path]
                path_line.set_data(rx, ry)
                lc.set_segments([]) 
            
            artists.extend([lc, path_line])
            
        return artists

    def show_animation(self):
        max_len = 0
        for data in self.data_store.values():
            max_len = max(max_len, len(data['explored']))
            
        total_frames = max_len // 50 + 20
        print("--- Memulai Visualisasi Window ---")
        ani = FuncAnimation(self.fig, self._update_frame, frames=total_frames, 
                            interval=30, blit=True, repeat=False)
        plt.tight_layout()
        plt.show()