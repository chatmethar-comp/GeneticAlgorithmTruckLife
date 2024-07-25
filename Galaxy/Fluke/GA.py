import random
import copy

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["distance_matrix"] = [
        # fmt: off
        [0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388, 354, 468, 776, 662],
        [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480, 674, 1016, 868, 1210],
        [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164, 1130, 788, 1552, 754],
        [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628, 822, 1164, 560, 1358],
        [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514, 708, 1050, 674, 1244],
        [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662, 628, 514, 1050, 708],
        [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890, 856, 514, 1278, 480],
        [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354, 320, 662, 742, 856],
        [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696, 662, 320, 1084, 514],
        [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422, 388, 274, 810, 468],
        [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764, 730, 388, 1152, 354],
        [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114, 308, 650, 274, 844],
        [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0, 194, 536, 388, 730],
        [354, 674, 1130, 822, 708, 628, 856, 320, 662, 388, 730, 308, 194, 0, 342, 422, 536],
        [468, 1016, 788, 1164, 1050, 514, 514, 662, 320, 274, 388, 650, 536, 342, 0, 764, 194],
        [776, 868, 1552, 560, 674, 1050, 1278, 742, 1084, 810, 1152, 274, 388, 422, 764, 0, 798],
        [662, 1210, 754, 1358, 1244, 708, 480, 856, 514, 468, 354, 844, 730, 536, 194, 798, 0],
        # fmt: on
    ]
    data["time_matrix"] = [
        [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
        [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
        [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
        [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
        [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
        [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
        [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
        [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
        [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
        [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
        [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
        [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
        [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
        [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
        [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
        [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
        [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],
    ]
    data["time_windows"] = [
        (0, 5),  # depot
        (7, 12),  # 1
        (10, 15),  # 2
        (16, 18),  # 3
        (10, 13),  # 4
        (0, 5),  # 5
        (5, 10),  # 6
        (0, 4),  # 7
        (5, 10),  # 8
        (0, 3),  # 9
        (10, 16),  # 10
        (10, 15),  # 11
        (0, 5),  # 12
        (5, 10),  # 13
        (7, 8),  # 14
        (10, 15),  # 15
        (11, 15),  # 16
    ]
    data["demands"] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    data["vehicle_capacities"] = [15, 15, 15, 15]
    data["num_vehicles"] = 4
    data["depot"] = 0
    return data

# Helper functions
def calculate_route_distance(route, distance_matrix):
    return sum(distance_matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))

def calculate_route_time(route, time_matrix):
    return sum(time_matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))

def is_valid_route(route, time_matrix, time_windows, demands, vehicle_capacity):
    time = 0
    load = 0
    for i in range(len(route)):
        load += demands[route[i]]
        if load > vehicle_capacity:
            return False
        time += time_matrix[route[i - 1]][route[i]] if i > 0 else 0
        if time < time_windows[route[i]][0]:
            time = time_windows[route[i]][0]
        if time > time_windows[route[i]][1]:
            return False
    return True

def split_individual(individual, num_vehicles, depot):
    sublist_size = len(individual) // num_vehicles
    routes = [individual[i * sublist_size:(i + 1) * sublist_size] for i in range(num_vehicles)]
    for route in routes:
        route.insert(0, depot)
        route.append(depot)
    return routes

# Genetic Algorithm Functions
def greedy_initialization(num_customers, distance_matrix, time_matrix, time_windows, demands, vehicle_capacity):
    unassigned = list(range(1, num_customers + 1))
    route = [0]  # Start at the depot
    while unassigned:
        best_next = min(unassigned, key=lambda c: distance_matrix[route[-1]][c])
        if is_valid_route(route + [best_next, 0], time_matrix, time_windows, demands, vehicle_capacity):
            route.append(best_next)
            unassigned.remove(best_next)
        else:
            route.append(0)  # Return to depot
            if len(route) > 2:  # If route is not empty
                yield route[1:-1]  # Yield route without depot
            route = [0]  # Start a new route
    if len(route) > 2:
        yield route[1:-1]

def create_individual(num_customers, distance_matrix, time_matrix, time_windows, demands, vehicle_capacity):
    routes = list(greedy_initialization(num_customers, distance_matrix, time_matrix, time_windows, demands, vehicle_capacity))
    return [customer for route in routes for customer in route]

def create_population(pop_size, num_customers, distance_matrix, time_matrix, time_windows, demands, vehicle_capacity):
    return [create_individual(num_customers, distance_matrix, time_matrix, time_windows, demands, vehicle_capacity) for _ in range(pop_size)]

def calculate_fitness(individual, distance_matrix, time_matrix, time_windows, demands, vehicle_capacities):
    routes = split_individual(individual, len(vehicle_capacities), 0)
    total_distance = sum(calculate_route_distance(route, distance_matrix) for route in routes)
    penalty = sum(1000 for i, route in enumerate(routes) if not is_valid_route(route, time_matrix, time_windows, demands, vehicle_capacities[i]))
    return total_distance + penalty

def tournament_selection(population, fitnesses, tournament_size):
    selected = random.sample(range(len(population)), tournament_size)
    best_individual = min(selected, key=lambda idx: fitnesses[idx])
    return population[best_individual]

def crossover(parent1, parent2):
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child_p1 = parent1[start:end + 1]
    child_p2 = [item for item in parent2 if item not in child_p1]
    return child_p1 + child_p2

def mutate(individual, mutation_rate):
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(individual) - 1)
            individual[i], individual[j] = individual[j], individual[i]
    return individual

# Initialize data model
data = create_data_model()

# Adjusted Parameters
pop_size = 100
num_generations = 500
mutation_rate = 0.02
tournament_size = 5
elite_size = 2

# Initialize population
population = create_population(pop_size, len(data["distance_matrix"]) - 1, data["distance_matrix"], data["time_matrix"], data["time_windows"], data["demands"], data["vehicle_capacities"][0])
fitnesses = [calculate_fitness(ind, data["distance_matrix"], data["time_matrix"], data["time_windows"], data["demands"], data["vehicle_capacities"]) for ind in population]

# Evolution process
for generation in range(num_generations):
    # Elitism
    elite = sorted(zip(population, fitnesses), key=lambda x: x[1])[:elite_size]
    new_population = [ind for ind, _ in elite]
    
    while len(new_population) < pop_size:
        parent1 = tournament_selection(population, fitnesses, tournament_size)
        parent2 = tournament_selection(population, fitnesses, tournament_size)
        child = mutate(crossover(parent1, parent2), mutation_rate)
        new_population.append(child)
    
    population = new_population
    fitnesses = [calculate_fitness(ind, data["distance_matrix"], data["time_matrix"], data["time_windows"], data["demands"], data["vehicle_capacities"]) for ind in population]

    # Determine the best individual in the current generation
    best_individual = min(population, key=lambda ind: calculate_fitness(ind, data["distance_matrix"], data["time_matrix"], data["time_windows"], data["demands"], data["vehicle_capacities"]))
    best_routes = split_individual(best_individual, data["num_vehicles"], data["depot"])
    best_fitness = calculate_fitness(best_individual, data["distance_matrix"], data["time_matrix"], data["time_windows"], data["demands"], data["vehicle_capacities"])
    
    if generation % 50 == 0:
        print(f"Generation {generation + 1} - Best Fitness: {best_fitness}")
        print(f"Best Routes: {best_routes}")

# Best solution
best_individual = min(population, key=lambda ind: calculate_fitness(ind, data["distance_matrix"], data["time_matrix"], data["time_windows"], data["demands"], data["vehicle_capacities"]))
best_routes = split_individual(best_individual, data["num_vehicles"], data["depot"])
best_fitness = calculate_fitness(best_individual, data["distance_matrix"], data["time_matrix"], data["time_windows"], data["demands"], data["vehicle_capacities"])

print("\nFinal Best Routes:", best_routes)
print("Final Best Fitness:", best_fitness)