from src.models.map import Map

def simulate():
    world = Map(20,20)
    world.randomize(obstacle_prob=0.1, danger_prob=0.2, seed=42)
    world.add_survivors([(2, 3), (7, 8), (5, 1)])
    world.add_drones([(0, 0), (9, 9)])

    print(world)
    world.display()

    x, y = 2, 3
    print(f"\nNeighbors of ({x}, {y}):")
    for (nx, ny), cost in world.get_neighbors(x, y):
        print(f"  -> ({nx}, {ny}) cost={cost}")
    
    # decay test
    print("\nAfter danger decay:")
    world.decay_danger(decay_rate=0.5)
    world.display()

if __name__ == "__main__":
    simulate()