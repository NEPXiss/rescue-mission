# test_hidden_survivors.py
"""
Test script to verify that hidden survivors work correctly:
1. Hidden survivors are NOT assigned before discovery
2. Discovery triggers re-planning
3. Assignment only happens to known + discovered survivors
"""

import random
from src.models.map.map_generator import MapGenerator
from src.models.ai.mission_coordinator import MissionCoordinator
from src.constants import CellType

def test_hidden_survivor_logic():
    """Test that hidden survivors are handled correctly"""
    
    print("="*70)
    print("TEST: Hidden Survivor Discovery Logic")
    print("="*70)
    
    # Setup
    seed = 123
    generator = MapGenerator(width=20, height=20, obstacle_prob=0.10, danger_prob=0.05, seed=seed)
    world = generator.generate(survivors=5, drones=0)
    
    # Get all survivors
    all_survivors = world.list_survivors()
    random.seed(seed)
    random.shuffle(all_survivors)
    
    # Split: 2 known, 3 hidden
    known_survivors = all_survivors[:2]
    hidden_survivors = all_survivors[2:]
    
    print(f"\nSetup:")
    print(f"  Total survivors: {len(all_survivors)}")
    print(f"  Known survivors: {known_survivors}")
    print(f"  Hidden survivors: {hidden_survivors}")
    
    # Remove hidden survivors from map
    for pos in hidden_survivors:
        world.grid[pos[0]][pos[1]] = CellType.NORMAL
    
    # Create coordinator
    spawn_point = (1, 1)
    coordinator = MissionCoordinator(
        world=world,
        spawn_point=spawn_point,
        detection_radius=2,
        drone_spawn_delay=3
    )
    
    coordinator.initialize_mission(known_survivors)
    
    # Put hidden survivors back (simulating they exist in real world)
    for pos in hidden_survivors:
        world.grid[pos[0]][pos[1]] = CellType.SURVIVOR
    
    coordinator.set_all_survivors(all_survivors)
    
    print("\n" + "-"*70)
    print("TEST 1: Initial assignment should ONLY target known survivors")
    print("-"*70)
    
    # Spawn drones
    for i in range(3):
        coordinator.spawn_drone(speed=1.0)
    
    # Assign tasks
    assignments = coordinator.assign_tasks()
    
    print(f"\nAssignments made: {len(assignments) if assignments else 0}")
    if assignments:
        for drone_id, target, cost in assignments:
            print(f"  Drone {drone_id} -> {target}")
            
            # Verify target is in known_survivors
            if target in hidden_survivors:
                print(f"    ❌ FAIL: Assigned to HIDDEN survivor!")
                return False
            elif target in known_survivors:
                print(f"    ✅ PASS: Assigned to KNOWN survivor")
            else:
                print(f"    ❌ FAIL: Assigned to UNKNOWN survivor!")
                return False
    
    print("\n" + "-"*70)
    print("TEST 2: Simulate discovery and verify re-planning")
    print("-"*70)
    
    # Simulate discovery by manually adding to discovered_survivors
    discovered = hidden_survivors[0]
    print(f"\nSimulating discovery of survivor at {discovered}")
    coordinator.discovered_survivors.add(discovered)
    
    # Check if this triggers re-planning
    coordinator.replan_if_needed()
    
    # Now try to assign again
    print(f"\nAttempting new assignments after discovery...")
    new_assignments = coordinator.assign_tasks()
    
    if new_assignments:
        print(f"New assignments made: {len(new_assignments)}")
        for drone_id, target, cost in new_assignments:
            print(f"  Drone {drone_id} -> {target}")
            
            # Verify target is either known or discovered
            if target in hidden_survivors and target not in coordinator.discovered_survivors:
                print(f"    ❌ FAIL: Assigned to STILL HIDDEN survivor!")
                return False
            else:
                print(f"    ✅ PASS: Assigned to known/discovered survivor")
    else:
        print("No new assignments (all drones busy)")
    
    print("\n" + "-"*70)
    print("TEST 3: Run simulation and verify discoveries happen correctly")
    print("-"*70)
    
    # Run simulation for a few steps
    discoveries_made = []
    
    for step in range(50):
        log = coordinator.step(spawn_new_drone=True, new_drone_speed=1.0)
        
        if log['discovered']:
            discoveries_made.extend(log['discovered'])
            print(f"\nStep {step}: Discovered {log['discovered']}")
            
            # Verify discovered survivors were originally hidden
            for disc in log['discovered']:
                if disc not in hidden_survivors:
                    print(f"  ❌ FAIL: 'Discovered' survivor {disc} was not in hidden list!")
                    return False
                else:
                    print(f"  ✅ PASS: Correctly discovered hidden survivor")
        
        if log['assigned']:
            for drone_id, target, cost in log['assigned']:
                # Verify assignment is valid
                if target in hidden_survivors and target not in coordinator.discovered_survivors:
                    print(f"\nStep {step}:")
                    print(f"  ❌ FAIL: Drone {drone_id} assigned to hidden survivor {target}")
                    print(f"  Known: {coordinator.known_survivors}")
                    print(f"  Discovered: {coordinator.discovered_survivors}")
                    print(f"  Hidden: {set(hidden_survivors)}")
                    return False
        
        # Stop if mission complete
        if coordinator.is_mission_complete():
            break
    
    print(f"\nSimulation completed after {step+1} steps")
    print(f"Total discoveries: {len(discoveries_made)}")
    print(f"Discovered survivors: {discoveries_made}")
    
    status = coordinator.get_status()
    print(f"\nFinal status:")
    print(f"  Known: {status['known_survivors']}")
    print(f"  Discovered: {status['discovered_survivors']}")
    print(f"  Rescued: {status['rescued_survivors']}")
    print(f"  Total: {status['total_survivors']}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    return True

if __name__ == "__main__":
    success = test_hidden_survivor_logic()
    
    if not success:
        print("\n❌ TESTS FAILED!")
        exit(1)
    else:
        print("\n✅ Tests completed successfully!")
        exit(0)