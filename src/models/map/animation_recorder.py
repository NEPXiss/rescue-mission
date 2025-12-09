# src/models/map/animation_recorder.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter
import numpy as np
from src.constants import CellType
from typing import List, Dict, Optional

class AnimationRecorder:
    """
    Records mission simulation and creates animated video with event notifications
    """
    
    def __init__(self, world, coordinator):
        self.world = world
        self.coordinator = coordinator
        self.history_snapshots = []
        
        # Color scheme
        self.colors = {
            CellType.NORMAL: '#FFFFFF',      # White
            CellType.OBSTACLE: '#333333',    # Dark gray
            CellType.DANGER: '#FFB366',      # Orange
            CellType.SURVIVOR: '#FF3333',    # Red
            CellType.DRONE: '#3366FF'        # Blue
        }
        
    def record_snapshot(self):
        """Record current state of mission"""
        snapshot = {
            'time': self.coordinator.current_time,
            'drones': [{
                'id': d.drone_id,
                'pos': d.pos,
                'target': d.target,
                'path': d.path.copy() if d.path else []
            } for d in self.coordinator.drones],
            'known_survivors': self.coordinator.known_survivors.copy(),
            'discovered_survivors': self.coordinator.discovered_survivors.copy(),
            'rescued_survivors': self.coordinator.rescued_survivors.copy(),
            'events': self.coordinator.get_events_at_time(self.coordinator.current_time)
        }
        self.history_snapshots.append(snapshot)
        
    def create_animation(self, filename='rescue_mission.mp4', fps=2, 
                        show_pheromone=False, show_grid=True, dpi=100):
        """
        Create animation video from recorded snapshots
        
        Parameters:
        - filename: output video filename (.mp4 or .gif)
        - fps: frames per second
        - show_pheromone: show pheromone overlay
        - show_grid: show grid lines
        - dpi: video quality (higher = better quality but larger file)
        """
        if not self.history_snapshots:
            print("No snapshots recorded!")
            return
            
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Create base map image (this won't change)
        map_img = self._create_base_map()
        
        def update_frame(frame_idx):
            ax.clear()
            
            snapshot = self.history_snapshots[frame_idx]
            
            # Draw base map
            ax.imshow(map_img, origin='upper', interpolation='nearest')
            
            # Show pheromone overlay
            if show_pheromone and self.world.pheromone is not None:
                pheromone_normalized = self.world.pheromone / (self.world.pheromone.max() + 1e-8)
                ax.imshow(pheromone_normalized, origin='upper', alpha=0.3, cmap='hot')
            
            # Draw survivors
            self._draw_survivors(ax, snapshot)
            
            # Draw drones and their paths
            self._draw_drones(ax, snapshot)
            
            # Draw spawn point
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
            
            # Title with mission status
            status = self._get_status_text(snapshot)
            ax.set_title(status, fontsize=14, pad=20)
            
            # Event notifications (bottom of plot)
            event_text = self._format_events(snapshot['events'])
            if event_text:
                fig.text(0.5, 0.02, event_text, ha='center', fontsize=11,
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            # Legend
            self._add_legend(ax)
            
        # Create animation
        anim = FuncAnimation(fig, update_frame, frames=len(self.history_snapshots),
                           interval=1000/fps, repeat=True)
        
        # Save animation
        print(f"Creating animation with {len(self.history_snapshots)} frames...")
        
        if filename.endswith('.gif'):
            writer = PillowWriter(fps=fps)
        else:
            writer = FFMpegWriter(fps=fps, bitrate=1800)
            
        anim.save(filename, writer=writer, dpi=dpi)
        plt.close()
        
        print(f"Animation saved to {filename}")
        
    def _create_base_map(self):
        """Create base map image"""
        map_img = np.zeros((self.world.height, self.world.width, 3))
        for y in range(self.world.height):
            for x in range(self.world.width):
                cell = self.world.grid[y][x]
                # Don't color survivors/drones in base map
                if cell in (CellType.SURVIVOR, CellType.DRONE):
                    cell = CellType.NORMAL
                color = self.colors.get(cell, '#FFFFFF')
                rgb = tuple(int(color.lstrip('#')[i:i+2], 16)/255.0 for i in (0, 2, 4))
                map_img[y][x] = rgb
        return map_img
        
    def _draw_survivors(self, ax, snapshot):
        """Draw survivors with different colors based on status"""
        # Known survivors (not yet rescued)
        for survivor in snapshot['known_survivors']:
            if survivor not in snapshot['rescued_survivors']:
                y, x = survivor
                ax.plot(x, y, 'r*', markersize=15, zorder=8)
                
        # Discovered survivors (not yet rescued)
        for survivor in snapshot['discovered_survivors']:
            if survivor not in snapshot['rescued_survivors']:
                y, x = survivor
                ax.plot(x, y, 'y*', markersize=15, zorder=8)
                
        # Rescued survivors
        for survivor in snapshot['rescued_survivors']:
            y, x = survivor
            ax.plot(x, y, 'g*', markersize=15, zorder=8)
            
    def _draw_drones(self, ax, snapshot):
        """Draw drones and their paths"""
        for drone_data in snapshot['drones']:
            y, x = drone_data['pos']
            
            # Drone marker
            circle = plt.Circle((x, y), 0.3, color='blue', alpha=0.8, zorder=10)
            ax.add_patch(circle)
            
            # Drone ID
            ax.text(x, y, str(drone_data['id']), 
                   ha='center', va='center', color='white', 
                   fontsize=8, weight='bold', zorder=11)
            
            # Draw path
            if drone_data['path']:
                path_y = [p[0] for p in drone_data['path']]
                path_x = [p[1] for p in drone_data['path']]
                ax.plot(path_x, path_y, 'b--', alpha=0.3, linewidth=1, zorder=5)
                
                # Draw target with arrow
                if drone_data['target']:
                    ty, tx = drone_data['target']
                    ax.annotate('', xy=(tx, ty), xytext=(x, y),
                              arrowprops=dict(arrowstyle='->', color='blue', 
                                            lw=1.5, alpha=0.5), zorder=6)
                    
    def _get_status_text(self, snapshot):
        """Generate status text for title"""
        total_known = len(snapshot['known_survivors'] | snapshot['discovered_survivors'])
        rescued = len(snapshot['rescued_survivors'])
        
        return (f"Rescue Mission - Time: {snapshot['time']} | "
                f"Drones: {len(snapshot['drones'])} | "
                f"Survivors: {rescued}/{total_known} rescued")
        
    def _format_events(self, events):
        """Format events into notification text"""
        if not events:
            return ""
            
        notifications = []
        for event in events:
            if event['type'] == 'spawn':
                notifications.append(f"🚁 Drone #{event['drone_id']} spawned (speed: {event['speed']:.1f})")
                
            elif event['type'] == 'discovery':
                pos = event['survivor_pos']
                notifications.append(f"🔍 Drone #{event['drone_id']} discovered survivor at {pos}!")
                
            elif event['type'] == 'rescue':
                pos = event['survivor_pos']
                notifications.append(f"✅ Drone #{event['drone_id']} rescued survivor at {pos}!")
                
            elif event['type'] == 'reassign':
                old = event['old_target']
                new = event['new_target']
                notifications.append(
                    f"🔄 Drone #{event['drone_id']} reassigned: {old} → {new} "
                    f"(cost: {event['old_cost']:.1f} → {event['new_cost']:.1f})"
                )
                
        return " | ".join(notifications)
        
    def _add_legend(self, ax):
        """Add legend to plot"""
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
        
    def save_all_frames(self, output_dir='frames', prefix='frame'):
        """Save all frames as individual images (useful for debugging)"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(14, 10))
        map_img = self._create_base_map()
        
        for idx, snapshot in enumerate(self.history_snapshots):
            ax.clear()
            ax.imshow(map_img, origin='upper', interpolation='nearest')
            
            self._draw_survivors(ax, snapshot)
            self._draw_drones(ax, snapshot)
            
            status = self._get_status_text(snapshot)
            ax.set_title(status, fontsize=14, pad=20)
            
            event_text = self._format_events(snapshot['events'])
            if event_text:
                fig.text(0.5, 0.02, event_text, ha='center', fontsize=11,
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            self._add_legend(ax)
            
            filename = os.path.join(output_dir, f"{prefix}_{idx:04d}.png")
            plt.savefig(filename, dpi=100, bbox_inches='tight')
            
        plt.close()
        print(f"Saved {len(self.history_snapshots)} frames to {output_dir}/")