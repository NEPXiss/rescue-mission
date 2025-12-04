from src.models.map.map_generator import MapGenerator

gen = MapGenerator()
world = gen.generate()

world.print_map()
print("Survivors:", world.list_survivors())
print("Drones:", world.list_drones())
