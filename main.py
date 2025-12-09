# main.py
import random
import numpy as np
from src.models.map.map_generator import MapGenerator
from src.models.ai.mission_coordinator import MissionCoordinator
from src.models.map.map_visualizer import MapVisualizer
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
    save_final_map=True
):
  
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
    
    # Seperate survivors into known and hidden
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
    
    # Run simulation
    print("\n" + "="*60)
    print("STARTING SIMULATION")
    print("="*60)
    
    step = 0
    last_viz_step = -10  # Track last visualization
    
    while step < max_steps:
        # Decide whether to spawn drone
        spawn_new = len(coordinator.drones) < max_drones
        
        # Drone (0.8 - 1.5)
        drone_speed = random.uniform(0.8, 1.5)
        
        # Run 1 step
        log = coordinator.step(spawn_new_drone=spawn_new, new_drone_speed=drone_speed)
        
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
        
        # Visualization
        if visualize and (step - last_viz_step >= 25 or log['discovered'] or log['rescued']):
            if step > 0:
                try:
                    viz = MapVisualizer(world, coordinator)
                    viz.save_map(f'rescue_step_{step:03d}.png', show_grid=False)
                    print(f"  📸 Saved visualization: rescue_step_{step:03d}.png")
                    last_viz_step = step
                except Exception as e:
                    print(f"  ⚠️  Visualization error: {e}")
        
        if coordinator.is_mission_complete():
            print("\n" + "="*60)
            print("🎉 MISSION COMPLETE!")
            print("="*60)
            break
            
        step += 1
    
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
    
    print("\nFinal Map (text):")
    print_map_with_drones(world, coordinator)
    
    if save_final_map:
        try:
            viz = MapVisualizer(world, coordinator)
            viz.save_map('rescue_final.png', show_grid=True)
            print(f"\n📸 Final map saved as: rescue_final.png")
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
    
    return coordinator, world

if __name__ == "__main__":
    # Run simulation
    coordinator, world = run_simulation(
        map_width=25,
        map_height=25,
        num_initial_survivors=8,
        num_hidden_survivors=5,
        detection_radius=3,
        drone_spawn_delay=5,
        max_drones=20,
        max_steps=250,
        seed=42,
        visualize=True,
        save_final_map=True
    )