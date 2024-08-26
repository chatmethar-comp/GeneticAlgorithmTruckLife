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
    (13.8251, 100.4357, 550),   # Nonthaburi with weight
    (14.0359, 100.4798, 550),   # Nakhon Ratchasima with weight
    (13.7364, 100.5370, 500),   # Pathum Thani with weight
    (14.8970, 100.8534, 450),   # Suphan Buri with weight
    (17.0169, 99.5228, 250),    # Lampang with weight
    (15.3161, 102.8291, 300),   # Chaiyaphum with weight
    (16.4536, 102.7665, 200),   # Maha Sarakham with weight
    (14.9514, 102.0608, 400),   # Roi Et with weight
    (18.8036, 99.0824, 350),    # Mae Hong Son with weight
    (13.6692, 100.6627, 300)    # Samut Songkhram with weight
]
total_weight = sum(coordinates[i][2] for i in range(len(coordinates)))
print(total_weight)

Truck_weights = [1900, 1900, 1900, 1000] 

def haversine_distance(point1, point2):
    lat1, lon1, _ = point1
    lat2, lon2, _ = point2
    R = 6371  # Radius of the Earth in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) * np.sin(dlat / 2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) * np.sin(dlon / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def distribute_locations(locations, truck_weights):
    shuffled_locations = locations[:]
    random.shuffle(shuffled_locations)
    
    routes = [[] for _ in range(len(truck_weights))]
    truck_loads = [0] * len(truck_weights)
    
    for location in shuffled_locations:
        lat, lon, weight = location
        for i in range(len(truck_weights)):
            if truck_loads[i] + weight <= truck_weights[i]:
                routes[i].append(location)
                truck_loads[i] += weight
                break
        
    return routes

def route_distance(route):
    total_distance = 0
    for i in range(len(route)):
        total_distance += haversine_distance(route[i], route[(i + 1) % len(route)])
    return total_distance

def solution_distance(solution):
    return sum(route_distance(route) for route in solution)

def initial_population(pop_size, coordinates, truck_weights):
    population = []
    while len(population) < pop_size:
        solution = distribute_locations(coordinates, truck_weights)
        if all(sum(coord[2] for coord in route) <= weight for route, weight in zip(solution, truck_weights)):
            population.append(solution)
    return population

def rank_solutions(population):
    fitness_results = [(solution_distance(solution), solution) for solution in population]
    fitness_results.sort(key=lambda x: x[0])
    return fitness_results

def selection(fitness_results, elite_size):
    return [fitness_results[i][1] for i in range(elite_size)]

def crossover(parent1, parent2, truck_weights):
    child = []
    
    location_to_truck = {}
    for truck_index, truck_route in enumerate(parent1):
        for location in truck_route:
            location_to_truck[location] = truck_index

    crossover_point1 = random.randint(0, len(parent1) - 1)
    crossover_point2 = random.randint(crossover_point1, len(parent1) - 1)
    
    child_routes = [[] for _ in range(len(parent1))]

    for i in range(crossover_point1, crossover_point2 + 1):
        child_routes[i] = parent1[i]

    for i, truck_route in enumerate(parent2):
        for location in truck_route:
            if location not in [loc for sublist in child_routes for loc in sublist]:
                assigned = False
                for j in range(len(child_routes)):
                    if child_routes[j] == [] or (sum([loc[2] for loc in child_routes[j]]) + location[2]) <= truck_weights[j]:
                        child_routes[j].append(location)
                        assigned = True
                        break

    return child_routes

def mutate(solution, mutation_rate, truck_weights):
    mutated_solution = solution.copy()

    for i, truck_route in enumerate(mutated_solution):
        if random.random() < mutation_rate:
            if len(truck_route) > 1:
                loc1, loc2 = random.sample(range(len(truck_route)), 2)
                truck_route[loc1], truck_route[loc2] = truck_route[loc2], truck_route[loc1]
            else:
                subset_size = random.randint(2, len(truck_route))
                subset_indices = random.sample(range(len(truck_route)), subset_size)
                subset = [truck_route[idx] for idx in subset_indices]
                random.shuffle(subset)
                for idx, loc in zip(subset_indices, subset):
                    truck_route[idx] = loc

            if sum([loc[2] for loc in truck_route]) > truck_weights[i]:
                mutated_solution = distribute_locations([loc for truck in solution for loc in truck], truck_weights)
                break

    return mutated_solution


def next_generation(current_gen, elite_size, mutation_rate, coordinates, truck_weights):
    ranked_solutions = rank_solutions(current_gen)
    selection_results = selection(ranked_solutions, elite_size)
    children = selection_results.copy()
    length = len(current_gen) - elite_size
    while len(children) < len(current_gen):
        parent1, parent2 = random.sample(selection_results, 2)
        child = crossover(parent1, parent2, truck_weights)
        children.append(mutate(child, mutation_rate, truck_weights))
    return children

def genetic_algorithm(coordinates, truck_weights, pop_size, elite_size, mutation_rate, generations):
    population = initial_population(pop_size, coordinates, truck_weights)
    print("Initial distance: " + str(rank_solutions(population)[0][0]))
    
    for _ in range(generations):
        population = next_generation(population, elite_size, mutation_rate, coordinates, truck_weights)
    
    best_solution = rank_solutions(population)[0][1]
    print("Final distance: " + str(rank_solutions(population)[0][0]))
    return best_solution

def plot_solution(solution):
    plt.figure(figsize=(10, 6))
    colors = ['r', 'b', 'g']
    for i, route in enumerate(solution):
        x = [point[1] for point in route] + [route[0][1]]
        y = [point[0] for point in route] + [route[0][0]]
        plt.plot(x, y, 'o-', color=colors[i % len(colors)], label=f'Truck {i+1}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Best Delivery Routes in Thailand')
    plt.legend()
    plt.show()

def optimize_routes(coordinates, truck_weights, pop_size=200, elite_size=40, mutation_rate=0.01, generations=800):
    best_solution = genetic_algorithm(coordinates, truck_weights, pop_size, elite_size, mutation_rate, generations)
    return best_solution

if __name__ == "__main__":
    best_solution = optimize_routes(coordinates, Truck_weights)
    print("Best solution: ", best_solution)
    plot_solution(best_solution)
