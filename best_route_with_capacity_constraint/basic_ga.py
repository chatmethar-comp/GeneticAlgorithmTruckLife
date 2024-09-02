import numpy as np
import random
import matplotlib.pyplot as plt

coordinates = [
    (13.7563, 100.5018, 500),   # Bangkok with weight
    (18.7883, 98.9853, 300),    # Chiang Mai with weight
    (13.3611, 100.9847, 400),   # Samut Prakan with weight
    (7.8804, 98.3923, 250),     # Phuket with weight
    (15.8700, 100.9925, 600),   # Nakhon Sawan with weight
    (17.9647, 102.6291, 200),   # Khon Kaen with weight
    (12.5657, 99.9410, 350),    # Hua Hin with weight
    (16.4419, 102.8329, 450),   # Udon Thani with weight
    (16.2534, 103.2497, 150),   # Kalasin with weight
    (13.8251, 100.4357, 550)    # Nonthaburi with weight
]

Truck_weight = 1900  # Maximum allowable weight for the truck

def haversine_distance(point1, point2):
    lat1, lon1, _ = point1
    lat2, lon2, _ = point2
    R = 6371  # Radius of the Earth in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) * np.sin(dlat / 2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) * np.sin(dlon / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def create_route(coordinates, max_weight):
    route = []
    current_weight = 0
    available_coords = coordinates[:]
    
    while available_coords:
        coord = random.choice(available_coords)
        if current_weight + coord[2] <= max_weight:
            route.append(coord)
            current_weight += coord[2]
        available_coords.remove(coord)
    
    return route

def route_distance(route):
    total_distance = 0
    for i in range(len(route)):
        total_distance += haversine_distance(route[i], route[(i + 1) % len(route)])
    return total_distance

def initial_population(pop_size, coordinates, max_weight):
    population = []
    while len(population) < pop_size:
        route = create_route(coordinates, max_weight)
        if sum([coord[2] for coord in route]) <= max_weight:
            population.append(route)
    return population

def rank_routes(population):
    fitness_results = [(route_distance(route), route) for route in population]
    fitness_results.sort(key=lambda x: x[0])
    return fitness_results

def selection(fitness_results, elite_size):
    return [fitness_results[i][1] for i in range(elite_size)]

def crossover(parent1, parent2, max_weight):
    start = random.randint(0, len(parent1) - 1)
    end = random.randint(start + 1, len(parent1))
    child_p1 = parent1[start:end]
    child_p2 = [item for item in parent2 if item not in child_p1]
    child = child_p1 + child_p2
    
    if sum([coord[2] for coord in child]) <= max_weight:
        return child
    else:
        return create_route(coordinates, max_weight)

def mutate(route, mutation_rate, max_weight):
    for swapped in range(len(route)):
        if random.random() < mutation_rate:
            swap_with = int(random.random() * len(route))
            route[swapped], route[swap_with] = route[swap_with], route[swapped]
    
    if sum([coord[2] for coord in route]) <= max_weight:
        return route
    else:
        return create_route(coordinates, max_weight)

def next_generation(current_gen, elite_size, mutation_rate, max_weight):
    ranked_routes = rank_routes(current_gen)
    selection_results = selection(ranked_routes, elite_size)
    children = selection_results.copy()
    length = len(current_gen) - elite_size
    while len(children) < len(current_gen):
        parent1, parent2 = random.sample(selection_results, 2)
        child = crossover(parent1, parent2, max_weight)
        children.append(mutate(child, mutation_rate, max_weight))
    return children

def genetic_algorithm(coordinates, pop_size, elite_size, mutation_rate, generations, max_weight):
    population = initial_population(pop_size, coordinates, max_weight)
    print("Initial distance: " + str(rank_routes(population)[0][0]))
    
    for _ in range(generations):
        population = next_generation(population, elite_size, mutation_rate, max_weight)
    
    best_route = rank_routes(population)[0][1]
    print("Final distance: " + str(rank_routes(population)[0][0]))
    return best_route

def plot_route(route):
    plt.figure(figsize=(10, 6))
    x = [point[1] for point in route] + [route[0][1]]
    y = [point[0] for point in route] + [route[0][0]]
    plt.plot(x, y, 'o-')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Best Delivery Route in Thailand')
    plt.show()

def optimize_route(coordinates, max_weight, pop_size=100, elite_size=20, mutation_rate=0.01, generations=500):
    best_route = genetic_algorithm(coordinates, pop_size, elite_size, mutation_rate, generations, max_weight)
    return best_route

if __name__ == "__main__":
    best_route = optimize_route(coordinates, Truck_weight)
    print("Best route: ", best_route)
    plot_route(best_route)

