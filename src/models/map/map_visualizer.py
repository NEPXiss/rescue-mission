# src/models/map/map_visualizer.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
from src.constants import CellType

class MapVisualizer:    
    def __init__(self, world, coordinator=None):
        self.world = world
        self.coordinator = coordinator
        
        # Color scheme
        self.colors = {
            CellType.NORMAL: '#FFFFFF',      # White
            CellType.OBSTACLE: '#333333',    # Dark gray
            CellType.DANGER: '#FFB366',      # Orange
            CellType.SURVIVOR: '#FF3333',    # Red
            CellType.DRONE: '#3366FF'        # Blue
        }
        
    def plot_static_map(self, show_pheromone=False, show_grid=True):
        fig, ax = plt.subplots(figsize=(12, 12))
        
        # Plot base map
        map_img = np.zeros((self.world.height, self.world.width, 3))
        for y in range(self.world.height):
            for x in range(self.world.width):
                cell = self.world.grid[y][x]
                color = self.colors.get(cell, '#FFFFFF')
                # Convert hex to RGB
                rgb = tuple(int(color.lstrip('#')[i:i+2], 16)/255.0 for i in (0, 2, 4))
                map_img[y][x] = rgb
                
        ax.imshow(map_img, origin='upper', interpolation='nearest')
        
        # Show pheromone overlay
        if show_pheromone and self.world.pheromone is not None:
            pheromone_normalized = self.world.pheromone / (self.world.pheromone.max() + 1e-8)
            ax.imshow(pheromone_normalized, origin='upper', alpha=0.3, cmap='hot')
            
        # Plot drones
        if self.coordinator:
            for drone in self.coordinator.drones:
                y, x = drone.pos
                # Drone marker
                circle = plt.Circle((x, y), 0.3, color='blue', alpha=0.8, zorder=10)
                ax.add_patch(circle)
                # Drone ID
                ax.text(x, y, str(drone.drone_id), 
                       ha='center', va='center', color='white', 
                       fontsize=8, weight='bold', zorder=11)
                
                # Draw path
                if drone.path:
                    path_y = [p[0] for p in drone.path]
                    path_x = [p[1] for p in drone.path]
                    ax.plot(path_x, path_y, 'b--', alpha=0.3, linewidth=1, zorder=5)
                    
            # Plot known survivors
            for survivor in self.coordinator.known_survivors:
                y, x = survivor
                if survivor not in self.coordinator.rescued_survivors:
                    ax.plot(x, y, 'r*', markersize=15, zorder=8)
                    
            # Plot discovered survivors
            for survivor in self.coordinator.discovered_survivors:
                y, x = survivor
                if survivor not in self.coordinator.rescued_survivors:
                    ax.plot(x, y, 'y*', markersize=15, zorder=8)
                    
            # Plot rescued survivors
            for survivor in self.coordinator.rescued_survivors:
                y, x = survivor
                ax.plot(x, y, 'g*', markersize=15, zorder=8)
                
            # Mark spawn point
            sy, sx = self.coordinator.spawn_point
            rect = patches.Rectangle((sx-0.4, sy-0.4), 0.8, 0.8, 
                                     linewidth=2, edgecolor='green', 
                                     facecolor='none', zorder=9)
            ax.add_patch(rect)
        
        # Grid
        if show_grid:
            ax.set_xticks(np.arange(-0.5, self.world.width, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, self.world.height, 1), minor=True)
            ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
            
        ax.set_xlim(-0.5, self.world.width - 0.5)
        ax.set_ylim(self.world.height - 0.5, -0.5)
        ax.set_aspect('equal')
        
        # Legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
                   markersize=10, label='Drone'),
            Line2D([0], [0], marker='*', color='w', markerfacecolor='red', 
                   markersize=15, label='Known Survivor'),
            Line2D([0], [0], marker='*', color='w', markerfacecolor='yellow', 
                   markersize=15, label='Discovered Survivor'),
            Line2D([0], [0], marker='*', color='w', markerfacecolor='green', 
                   markersize=15, label='Rescued'),
            patches.Patch(facecolor='#333333', label='Obstacle'),
            patches.Patch(facecolor='#FFB366', label='Danger Zone'),
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        
        plt.title(f'Rescue Mission Map - Step {self.coordinator.current_time if self.coordinator else 0}')
        plt.tight_layout()
        
        return fig, ax
        
    def save_map(self, filename='rescue_map.png', **kwargs):
        """Save map to file"""
        fig, ax = self.plot_static_map(**kwargs)
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Map saved to {filename}")
        
    def show_map(self, **kwargs):
        """Show map in window"""
        self.plot_static_map(**kwargs)
        plt.show()


# Example usage
if __name__ == "__main__":
    from src.models.map.map_generator import MapGenerator
    from src.models.ai.mission_coordinator import MissionCoordinator
    
    # Generate map
    gen = MapGenerator(width=20, height=20, obstacle_prob=0.15, danger_prob=0.10, seed=42)
    world = gen.generate(survivors=5, drones=0)
    
    # Create coordinator
    coordinator = MissionCoordinator(
        world=world,
        spawn_point=(1, 1),
        detection_radius=2,
        drone_spawn_delay=5
    )
    
    survivors = world.list_survivors()
    coordinator.initialize_mission(survivors[:3])  # รู้แค่ 3 คน
    
    # Spawn some drones
    for i in range(3):
        coordinator.spawn_drone(speed=1.0 + i * 0.2)
    coordinator.assign_tasks()
    
    # Visualize
    viz = MapVisualizer(world, coordinator)
    viz.show_map(show_grid=True)