# main.py
import random
import numpy as np
from src.models.map.map_generator import MapGenerator
from src.models.ai.mission_coordinator import MissionCoordinator
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
    seed=42
):
    print("\n" + "="*60)
    print("AI RESCUE MISSION SIMULATION")
    print("="*60)
    
    generator = MapGenerator(
        width=map_width,
        height=map_height,
        obstacle_prob=0.15,
        danger_prob=0.10,
        seed=seed
    )
    
    total_survivors = num_initial_survivors + num_hidden_survivors
    world = generator.generate(survivors=total_survivors, drones=0)
    
    all_survivors = world.list_survivors()
    random.shuffle(all_survivors)
    
    known_survivors = all_survivors[:num_initial_survivors]
    hidden_survivors = all_survivors[num_initial_survivors:]
    
    for pos in hidden_survivors:
        world.grid[pos[0]][pos[1]] = CellType.NORMAL

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
    
    print(f"\nMap size: {map_width}x{map_height}")
    print(f"Spawn point: {spawn_point}")
    print(f"Known survivors: {len(known_survivors)}")
    print(f"Hidden survivors: {len(hidden_survivors)}")
    print(f"Detection radius: {detection_radius}")
    print(f"Drone spawn delay: {drone_spawn_delay}")
    
    coordinator = MissionCoordinator(
        world=world,
        spawn_point=spawn_point,
        detection_radius=detection_radius,
        drone_spawn_delay=drone_spawn_delay,
        allow_diagonal=True
    )
    
    # Initialize mission
    coordinator.initialize_mission(known_survivors)

    # Add hidden survivors back to the map (coordinator is unaware)
    for pos in hidden_survivors:
        world.grid[pos[0]][pos[1]] = CellType.SURVIVOR
    
    # Start simulation loop
    print("\n" + "="*60)
    print("STARTING SIMULATION")
    print("="*60)
    
    step = 0
    while step < max_steps:
        # Check if we should spawn drone
        spawn_new = len(coordinator.drones) < max_drones
        
        drone_speed = random.uniform(0.8, 1.5)
        
        # Execute step
        log = coordinator.step(spawn_new_drone=spawn_new, new_drone_speed=drone_speed)
        
        # Print log if there are significant events
        if (log['spawned'] is not False or 
            log['discovered'] or 
            log['rescued'] or 
            step % 20 == 0):
            
            print(f"\n--- Step {step} ---")
            
            if log['spawned'] is not False:
                print(f"  🚁 Spawned Drone {log['spawned']} (speed: {drone_speed:.2f})")
                
            if log['discovered']:
                print(f"  🔍 Discovered survivors: {log['discovered']}")
                
            if log['rescued']:
                for drone_id, pos in log['rescued']:
                    print(f"  ✅ Drone {drone_id} rescued survivor at {pos}")
                    
            if log['assigned']:
                for drone_id, target, cost in log['assigned']:
                    print(f"  📍 Drone {drone_id} assigned to {target} (ETA: {cost:.1f})")
                    
            status = coordinator.get_status()
            print(f"  Status: {status['rescued_survivors']}/{status['total_survivors']} rescued, "
                  f"{status['drones_deployed']} drones, "
                  f"{status['active_assignments']} active")
        

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
    print(f"Total time: {status['time']} steps")
    print(f"Drones deployed: {status['drones_deployed']}")
    print(f"Known survivors (initial): {len(known_survivors)}")
    print(f"Discovered survivors: {status['discovered_survivors']}")
    print(f"Total survivors: {status['total_survivors']}")
    print(f"Rescued: {status['rescued_survivors']}/{status['total_survivors']}")
    
    success_rate = (status['rescued_survivors'] / status['total_survivors'] * 100 
                   if status['total_survivors'] > 0 else 0)
    print(f"Success rate: {success_rate:.1f}%")
    
    # print("\nFinal map:")
    # print_map_with_drones(world, coordinator)
    
    return coordinator, world

if __name__ == "__main__":
    coordinator, world = run_simulation(
        map_width=25,
        map_height=25,
        num_initial_survivors=7,
        num_hidden_survivors=3,
        detection_radius=3,
        drone_spawn_delay=5,
        max_drones=10,
        max_steps=100,
        seed=42
    )