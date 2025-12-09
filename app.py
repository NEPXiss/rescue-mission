# main.py
import random
import numpy as np
import os
from src.models.map.map_generator import MapGenerator
from src.models.ai.mission_coordinator import MissionCoordinator
from src.models.map.map_visualizer import MapVisualizer
from src.models.map.animation_recorder import AnimationRecorder
from src.constants import CellType

def print_map_with_drones(world, coordinator):
    display = np.copy(world.grid)
    
    for drone in coordinator.drones:
        y, x = drone.pos
        display[y][x] = 5
        
    symbols = {
        CellType.NORMAL: '.',
        CellType.OBSTACLE: '#',
        CellType.DANGER: '~',
        CellType.SURVIVOR: 'S',
        5: 'D'  # Drone
    }
    
    print("\n" + "="*60)
    for row in display:
        print(' '.join(symbols.get(cell, '?') for cell in row))
    print("="*60)
    
def run_simulation(
    map_width=30,
    map_height=30,
    num_initial_survivors=8,
    num_hidden_survivors=5,
    detection_radius=3,
    drone_spawn_delay=5,
    max_drones=15,
    max_steps=200,
    seed=42,
    visualize=True,
    save_final_map=True,
    create_animation=True,
    output_dir='examples/ex3'
):
    """
    Run rescue mission simulation with visualization and animation
    
    Parameters:
    - create_animation: If True, creates animation video (.mp4 and .gif)
    - output_dir: Directory to save all outputs
    """
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("AI RESCUE MISSION SIMULATION")
    print("="*60)
    
    # Generate a map
    generator = MapGenerator(
        width=map_width,
        height=map_height,
        obstacle_prob=0.15,
        danger_prob=0.40,
        seed=seed
    )
    
    total_survivors = num_initial_survivors + num_hidden_survivors
    world = generator.generate(survivors=total_survivors, drones=0)
    
    # Separate survivors into known and hidden
    all_survivors = world.list_survivors()
    random.seed(seed)
    random.shuffle(all_survivors)
    
    known_survivors = all_survivors[:num_initial_survivors]
    hidden_survivors = all_survivors[num_initial_survivors:]
    
    # Store backup hidden survivors
    hidden_survivors_backup = hidden_survivors.copy()
    
    # Temporarily delete hidden survivors
    for pos in hidden_survivors:
        world.grid[pos[0]][pos[1]] = CellType.NORMAL
        
    # Define spawn point
    spawn_point = (1, 1)
    if world.grid[spawn_point[0]][spawn_point[1]] != CellType.NORMAL:
        for y in range(world.height):
            for x in range(world.width):
                if world.grid[y][x] == CellType.NORMAL:
                    spawn_point = (y, x)
                    break
            else:
                continue
            break
    
    print(f"\nMap Configuration:")
    print(f"  Size: {map_width}x{map_height}")
    print(f"  Spawn point: {spawn_point}")
    print(f"  Known survivors (initial): {len(known_survivors)}")
    print(f"  Hidden survivors: {len(hidden_survivors)}")
    print(f"  Total survivors: {total_survivors}")
    print(f"\nMission Parameters:")
    print(f"  Detection radius: {detection_radius}")
    print(f"  Drone spawn delay: {drone_spawn_delay}")
    print(f"  Max drones: {max_drones}")
    print(f"\nOutput Configuration:")
    print(f"  Output directory: {output_dir}")
    print(f"  Frame-by-frame images: {visualize}")
    print(f"  Animation video: {create_animation}")
    
    # Mission coordinator
    coordinator = MissionCoordinator(
        world=world,
        spawn_point=spawn_point,
        detection_radius=detection_radius,
        drone_spawn_delay=drone_spawn_delay,
        allow_diagonal=True
    )
    
    # Initialize mission with known survivors only
    coordinator.initialize_mission(known_survivors)
    
    # Add hidden survivors back to the world
    # But coordinator doesn't know about them yet
    for pos in hidden_survivors_backup:
        world.grid[pos[0]][pos[1]] = CellType.SURVIVOR
    
    # Tell coordinator about all survivors (for internal tracking)
    # but it won't assign to them until discovered
    coordinator.set_all_survivors(all_survivors)
    
    # Initialize animation recorder
    recorder = None
    if create_animation:
        recorder = AnimationRecorder(world, coordinator)
        recorder.record_snapshot()  # Record initial state
        print("  Animation recorder: Enabled")
    
    # Run simulation
    print("\n" + "="*60)
    print("STARTING SIMULATION")
    print("="*60)
    
    step = 0
    last_viz_step = -10  # Track last visualization
    
    while step < max_steps:
        # Decide whether to spawn drone
        spawn_new = len(coordinator.drones) < max_drones
        
        # Drone speed (0.8 - 1.5)
        drone_speed = random.uniform(0.8, 1.5)
        
        # Run 1 step
        log = coordinator.step(spawn_new_drone=spawn_new, new_drone_speed=drone_speed)
        
        # Record snapshot for animation (every step)
        if recorder:
            recorder.record_snapshot()
        
        # Print log if there is any important event
        important_event = (
            log['spawned'] is not False or 
            log['discovered'] or 
            log['rescued'] or 
            step % 20 == 0
        )
        
        if important_event:
            print(f"\n--- Step {step} ---")
            
            if log['spawned'] is not False:
                print(f"  🚁 Spawned Drone {log['spawned']} (speed: {drone_speed:.2f})")
                
            if log['discovered']:
                print(f"  🔍 Discovered {len(log['discovered'])} survivor(s): {log['discovered']}")
                
            if log['rescued']:
                for drone_id, pos in log['rescued']:
                    print(f"  ✅ Drone {drone_id} rescued survivor at {pos}")
                    
            if log['assigned']:
                for drone_id, target, cost in log['assigned']:
                    print(f"  📍 Drone {drone_id} -> {target} (ETA: {cost:.1f} steps)")
                    
            status = coordinator.get_status()
            print(f"  Status: {status['rescued_survivors']}/{status['total_survivors']} rescued, "
                  f"{status['drones_deployed']} drones deployed, "
                  f"{status['active_assignments']} active assignments")
        
        # Frame-by-frame visualization (save images every 25 steps or on important events)
        if visualize and (step - last_viz_step >= 25 or log['discovered'] or log['rescued']):
            if step > 0:
                try:
                    viz = MapVisualizer(world, coordinator)
                    frame_path = os.path.join(output_dir, f'rescue_step_{step:03d}.png')
                    viz.save_map(frame_path, show_grid=False)
                    print(f"  📸 Saved frame: rescue_step_{step:03d}.png")
                    last_viz_step = step
                except Exception as e:
                    print(f"  ⚠️  Visualization error: {e}")
        
        if coordinator.is_mission_complete():
            print("\n" + "="*60)
            print("🎉 MISSION COMPLETE!")
            print("="*60)
            break
            
        step += 1
    
    # Mission Summary
    print("\n" + "="*60)
    print("MISSION SUMMARY")
    print("="*60)
    
    status = coordinator.get_status()
    print(f"\nPerformance Metrics:")
    print(f"  Total time: {status['time']} steps")
    print(f"  Drones deployed: {status['drones_deployed']}")
    
    print(f"\nSurvivor Statistics:")
    print(f"  Initially known: {len(known_survivors)}")
    print(f"  Discovered during mission: {status['discovered_survivors']}")
    print(f"  Total found: {status['total_survivors']}")
    print(f"  Successfully rescued: {status['rescued_survivors']}")
    print(f"  Remaining: {status['remaining_survivors']}")
    
    success_rate = (status['rescued_survivors'] / status['total_survivors'] * 100 
                   if status['total_survivors'] > 0 else 0)
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    total_distance = sum(d.total_distance_traveled for d in coordinator.drones)
    print(f"\nEfficiency Metrics:")
    print(f"  Total distance traveled: {total_distance:.1f}")
    if total_distance > 0:
        print(f"  Survivors per unit distance: {status['rescued_survivors'] / total_distance:.4f}")
    print(f"  Average time per rescue: {status['time'] / max(status['rescued_survivors'], 1):.1f} steps")
    
    # print("\nFinal Map (text):")
    # print_map_with_drones(world, coordinator)
    
    # Save final map image
    if save_final_map:
        try:
            viz = MapVisualizer(world, coordinator)
            final_map_path = os.path.join(output_dir, 'rescue_final.png')
            viz.save_map(final_map_path, show_grid=True)
            print(f"\n📸 Final map saved as: {final_map_path}")
        except Exception as e:
            print(f"\n⚠️  Could not save final visualization: {e}")
    
    # Show discovered vs initially hidden
    actually_discovered = coordinator.discovered_survivors
    never_found = set(hidden_survivors_backup) - actually_discovered - coordinator.rescued_survivors
    
    print(f"\nDiscovery Analysis:")
    print(f"  Hidden survivors: {len(hidden_survivors_backup)}")
    print(f"  Actually discovered: {len(actually_discovered)}")
    print(f"  Never found: {len(never_found)}")
    if never_found:
        print(f"  Locations not found: {never_found}")
    
    # Create animation videos
    if create_animation and recorder:
        print("\n" + "="*60)
        print("CREATING ANIMATION VIDEOS")
        print("="*60)
        
        try:
            # Create MP4 video (high quality)
            mp4_path = os.path.join(output_dir, 'rescue_mission.mp4')
            print(f"\nGenerating MP4 video: {mp4_path}")
            recorder.create_animation(
                filename=mp4_path,
                fps=3,  # 3 frames per second
                show_pheromone=False,
                show_grid=True,
                dpi=120  # High quality
            )
            print(f"✅ MP4 video saved successfully!")
            
        except Exception as e:
            print(f"⚠️  Could not create MP4 video: {e}")
            print("    Make sure ffmpeg is installed: https://ffmpeg.org/download.html")
        
        try:
            # Create GIF animation (lower quality, smaller file)
            gif_path = os.path.join(output_dir, 'rescue_mission.gif')
            print(f"\nGenerating GIF animation: {gif_path}")
            recorder.create_animation(
                filename=gif_path,
                fps=2,  # 2 frames per second for GIF
                show_pheromone=False,
                show_grid=True,
                dpi=80  # Lower quality for smaller file size
            )
            print(f"✅ GIF animation saved successfully!")
            
        except Exception as e:
            print(f"⚠️  Could not create GIF animation: {e}")
    
    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)
    print(f"\nAll outputs saved to: {output_dir}/")
    print(f"  - Frame images: rescue_step_*.png")
    print(f"  - Final map: rescue_final.png")
    if create_animation:
        print(f"  - MP4 video: rescue_mission.mp4")
        print(f"  - GIF animation: rescue_mission.gif")
    
    return coordinator, world

if __name__ == "__main__":
    # Run simulation with all visualization options
    coordinator, world = run_simulation(
        map_width=30,
        map_height=30,
        num_initial_survivors=10,
        num_hidden_survivors=5,
        detection_radius=4,
        drone_spawn_delay=5,
        max_drones=20,
        max_steps=250,
        seed=42,
        visualize=True,           # Save frame images
        save_final_map=True,      # Save final map
        create_animation=True,    # Create video animations
        output_dir='examples/ex4' # Output directory
    )