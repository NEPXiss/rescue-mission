# main.py
from src.models.map.map_generator import MapGenerator
from src.models.ai.mission_coordinator import MissionCoordinator
from src.models.map.animation_recorder import AnimationRecorder
import random

def run_simulation_with_animation():
    """
    Run rescue mission simulation and create animation video
    """
    # Set seed for reproducibility
    random.seed(42)
    
    # 1. Generate map
    print("=" * 60)
    print("Generating map...")
    gen = MapGenerator(width=25, height=25, obstacle_prob=0.15, danger_prob=0.10, seed=42)
    world = gen.generate(survivors=10, drones=0)
    
    # 2. Create mission coordinator
    print("Initializing mission coordinator...")
    spawn_point = (2, 2)
    coordinator = MissionCoordinator(
        world=world,
        spawn_point=spawn_point,
        detection_radius=3,
        drone_spawn_delay=5,
        allow_diagonal=True
    )
    
    # 3. Setup mission
    all_survivors = world.list_survivors()
    known_survivors = all_survivors[:3]  # Initially know only 3 survivors
    coordinator.set_all_survivors(all_survivors)
    coordinator.initialize_mission(known_survivors)
    
    print(f"Total survivors in map: {len(all_survivors)}")
    print(f"Initially known survivors: {len(known_survivors)}")
    print(f"Hidden survivors: {len(all_survivors) - len(known_survivors)}")
    
    # 4. Create animation recorder
    recorder = AnimationRecorder(world, coordinator)
    
    # 5. Run simulation
    print("\n" + "=" * 60)
    print("Starting rescue mission simulation...")
    print("=" * 60)
    
    max_steps = 200
    step = 0
    
    # Record initial state
    recorder.record_snapshot()
    
    while step < max_steps and not coordinator.is_mission_complete():
        # Spawn new drone with varying speeds
        drone_speed = 1.0 + (step % 3) * 0.3
        
        step_log = coordinator.step(spawn_new_drone=True, new_drone_speed=drone_speed)
        
        # Print important events
        if step_log['spawned'] is not False:
            print(f"[Step {step}] Spawned Drone #{step_log['spawned']}")
            
        if step_log['discovered']:
            print(f"[Step {step}] Discovered {len(step_log['discovered'])} new survivor(s)!")
            
        if step_log['rescued']:
            for drone_id, pos in step_log['rescued']:
                print(f"[Step {step}] Drone #{drone_id} rescued survivor at {pos}")
        
        # Record snapshot for animation
        recorder.record_snapshot()
        
        step += 1
        
        # Print status every 20 steps
        if step % 20 == 0:
            status = coordinator.get_status()
            print(f"\n--- Status at Step {step} ---")
            print(f"  Drones deployed: {status['drones_deployed']}")
            print(f"  Survivors rescued: {status['rescued_survivors']}/{status['total_survivors']}")
            print(f"  Active assignments: {status['active_assignments']}\n")
    
    # 6. Final status
    print("\n" + "=" * 60)
    print("Mission Complete!" if coordinator.is_mission_complete() else "Mission Timeout")
    print("=" * 60)
    
    final_status = coordinator.get_status()
    print(f"Total steps: {coordinator.current_time}")
    print(f"Drones deployed: {final_status['drones_deployed']}")
    print(f"Survivors rescued: {final_status['rescued_survivors']}/{final_status['total_survivors']}")
    print(f"Known survivors: {final_status['known_survivors']}")
    print(f"Discovered survivors: {final_status['discovered_survivors']}")
    
    # 7. Create animation
    print("\n" + "=" * 60)
    print("Creating animation video...")
    print("=" * 60)
    
    # Create MP4 video
    recorder.create_animation(
        filename='rescue_mission.mp4',
        fps=3,  # 3 frames per second
        show_pheromone=False,
        show_grid=True,
        dpi=120  # Higher quality
    )
    
    # Optional: Create GIF (smaller file, lower quality)
    print("\nCreating GIF animation...")
    recorder.create_animation(
        filename='rescue_mission.gif',
        fps=2,
        show_pheromone=False,
        show_grid=True,
        dpi=80
    )
    
    print("\n" + "=" * 60)
    print("All done!")
    print("=" * 60)

if __name__ == "__main__":
    run_simulation_with_animation()