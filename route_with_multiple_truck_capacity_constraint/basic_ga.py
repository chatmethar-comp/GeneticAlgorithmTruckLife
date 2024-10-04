import numpy as np
import random
import matplotlib.pyplot as plt
import osm
import time

# Coordinates with weights
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

# Define the common starting point
starting_point = (13.7438, 100.5626, 0)  # Example: Bangkok without weight

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
    
    routes = [[starting_point] for _ in range(len(truck_weights))]  # Initialize routes with starting point
    truck_loads = [0] * len(truck_weights)
    
    for location in shuffled_locations:
        lat, lon, weight = location
        for i in range(len(truck_weights)):
            if truck_loads[i] + weight <= truck_weights[i]:
                routes[i].append(location)
                truck_loads[i] += weight
                break

    for route in routes:
        route.append(starting_point)  # Ensure each route returns to the starting point
    
    return routes

def route_distance(route):
    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += haversine_distance(route[i], route[i + 1])
    return total_distance

def solution_distance(solution):
    return sum(route_distance(route) for route in solution)

def initial_population(pop_size, coordinates, truck_weights):
    population = []
    while len(population) < pop_size:
        solution = distribute_locations(coordinates, truck_weights)
        if all(sum(coord[2] for coord in route[1:-1]) <= weight for route, weight in zip(solution, truck_weights)):
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
    
    crossover_point1 = random.randint(1, len(parent1) - 2)
    crossover_point2 = random.randint(crossover_point1, len(parent1) - 2)
    
    child_routes = [[starting_point] for _ in range(len(parent1))]

    for i in range(crossover_point1, crossover_point2 + 1):
        child_routes[i].extend(parent1[i][1:-1])

    for i, truck_route in enumerate(parent2):
        for location in truck_route[1:-1]:
            if location not in [loc for sublist in child_routes for loc in sublist]:
                assigned = False
                for j in range(len(child_routes)):
                    if sum([loc[2] for loc in child_routes[j]]) + location[2] <= truck_weights[j]:
                        child_routes[j].append(location)
                        assigned = True
                        break

    for route in child_routes:
        route.append(starting_point)  # Ensure route returns to starting point

    return child_routes

def mutate(solution, mutation_rate, truck_weights):
    mutated_solution = solution.copy()

    for i, truck_route in enumerate(mutated_solution):
        if random.random() < mutation_rate:
            if len(truck_route) > 3:  # More than start, end, and one location
                loc1, loc2 = random.sample(range(1, len(truck_route) - 1), 2)
                truck_route[loc1], truck_route[loc2] = truck_route[loc2], truck_route[loc1]

            if sum([loc[2] for loc in truck_route[1:-1]]) > truck_weights[i]:
                mutated_solution = distribute_locations([loc for truck in solution for loc in truck if loc != starting_point], truck_weights)
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
        x = [point[1] for point in route]
        y = [point[0] for point in route]
        plt.plot(x, y, 'o-', color=colors[i % len(colors)], label=f'Truck {i+1}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Best Delivery Routes in Thailand')
    plt.legend()
    plt.show()

def optimize_routes(coordinates, truck_weights, pop_size=1000, elite_size=100, mutation_rate=0.01, generations=50):
    best_solution = genetic_algorithm(coordinates, truck_weights, pop_size, elite_size, mutation_rate,generations)
    return best_solution

# def create_weight_graph(coor_list):
#     for i in range(len(coor_list)):
#         osm.get_travel_time()
#     return 1

#############################################################################

def remove_third_element(nested_list):
    new_list = []

    for sublist in nested_list:
        modified_sublist = []
        for tpl in sublist:
            modified_tuple = tpl[:2]
            modified_sublist.append(modified_tuple)

        new_list.append(modified_sublist)
    return new_list

def route_data(solution):
    seperate_route_data = []
    for i in range(len(solution)):
        temp_route_data = osm.get_route_data(solution[i])
        seperate_route_data.append(temp_route_data)
    return seperate_route_data

if __name__ == "__main__":
    start_time = time.time()
    best_solution = optimize_routes(coordinates, Truck_weights)
    best_solution_coor_only = remove_third_element(best_solution)
    route_map = osm.create_map(best_solution_coor_only,osm.colors)
    route_map.save("unconnected_routes_map_colored.html")
    print("Map has been saved as unconnected_routes_map_colored.html")
    print("Best solution: ", best_solution)
    print(f"Time taken {time.time()-start_time}")
    plot_solution(best_solution)


