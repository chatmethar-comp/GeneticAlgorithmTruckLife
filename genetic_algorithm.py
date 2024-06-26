import random
import math

# Example structures for the input data (unchanged from your provided code)

orderlist = [
    {"orderid": 1, "receptiondate": "2024-02-04", "latitude": 14.0264445, "longitude": 100.691927, "desired_delivery_date_start": "2024-02-09", "desired_delivery_date_end": "2024-02-12", "product": 4},
    {"orderid": 2, "receptiondate": "2024-02-01", "latitude": 13.965548, "longitude": 100.524527, "desired_delivery_date_start": "2024-02-04", "desired_delivery_date_end": "2024-02-08", "product": 1},
    {"orderid": 3, "receptiondate": "2024-02-05", "latitude": 14.1010167, "longitude": 100.555481, "desired_delivery_date_start": "2024-02-10", "desired_delivery_date_end": "2024-02-11", "product": 3},
    {"orderid": 4, "receptiondate": "2024-02-05", "latitude": 14.0236602, "longitude": 100.787754, "desired_delivery_date_start": "2024-02-09", "desired_delivery_date_end": "2024-02-12", "product": 8},
    {"orderid": 5, "receptiondate": "2024-02-06", "latitude": 13.7919807, "longitude": 100.294887, "desired_delivery_date_start": "2024-02-11", "desired_delivery_date_end": "2024-02-12", "product": 2},
    {"orderid": 6, "receptiondate": "2024-02-03", "latitude": 14.0532644, "longitude": 100.764001, "desired_delivery_date_start": "2024-02-04", "desired_delivery_date_end": "2024-02-08", "product": 10},
    {"orderid": 7, "receptiondate": "2024-02-06", "latitude": 13.688546, "longitude": 100.985242, "desired_delivery_date_start": "2024-02-08", "desired_delivery_date_end": "2024-02-12", "product": 9}
]

productlist = [
    {"productid": 1, "productname": "AAA", "weight": 200},
    {"productid": 2, "productname": "BBB", "weight": 300},
    {"productid": 3, "productname": "CCC", "weight": 400},
    {"productid": 4, "productname": "DDD", "weight": 500},
    {"productid": 5, "productname": "EEE", "weight": 600},
    {"productid": 6, "productname": "FFF", "weight": 700},
    {"productid": 7, "productname": "GGG", "weight": 800},
    {"productid": 8, "productname": "HHH", "weight": 900},
    {"productid": 9, "productname": "III", "weight": 1000},
    {"productid": 10, "productname": "JJJ", "weight": 1100}
]

trucklist = [
    {"truckid": 1, "truckname": "Truck A", "capacity": 1000},
    {"truckid": 2, "truckname": "Truck B", "capacity": 500}
]

outsourcing_fee_table = {
    (10, 500): 1000, (10, 1000): 1200, (10, 1500): 1400,
    (20, 500): 1100, (20, 1000): 1400, (20, 1500): 1700,
    (30, 500): 1200, (30, 1000): 1600, (30, 1500): 2000,
    (40, 500): 1300, (40, 1000): 1800, (40, 1500): 2300,
    (float('inf'), 500): 1400, (float('inf'), 1000): 2000, (float('inf'), 1500): 2600
}

# Utility functions (unchanged from your provided code)

def calculate_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def get_product_weight(productid):
    return next(product["weight"] for product in productlist if product["productid"] == productid)

def get_outsourcing_fee(distance, weight):
    for (dist_threshold, capacity_threshold), fee in outsourcing_fee_table.items():
        if distance <= dist_threshold and weight <= capacity_threshold:
            return fee
    return float('inf')


def initialize_population(pop_size, orders):
    population = []
    for _ in range(pop_size):
        chromosome = random.sample(orders, len(orders))
        population.append(chromosome)
    return population

def calculate_fitness(chromosome):
    start_lat, start_lon = 0, 0
    total_cost = 0
    total_distance = 0
    total_weight = 0

    for order in chromosome:
        product_weight = get_product_weight(order["product"])
        distance = calculate_distance(start_lat, start_lon, order["latitude"], order["longitude"])

        if product_weight <= trucklist[0]["capacity"]:
            total_cost += distance  # Assume cost per km is 1 unit for simplicity
            total_distance += distance
        else:
            outsourcing_fee = get_outsourcing_fee(distance, product_weight)
            total_cost += outsourcing_fee
            total_distance += distance
        total_weight += product_weight
        start_lat, start_lon = order["latitude"], order["longitude"]

    fitness_score = 1 / total_cost if total_cost > 0 else float('inf')
    return fitness_score, total_cost, total_distance, total_weight


def roulette_wheel_selection(population, fitnesses):
    total_fitness = sum(f[0] for f in fitnesses)  # Summing only the fitness scores
    probabilities = [f[0] / total_fitness for f in fitnesses]
    selected_index = random.choices(range(len(population)), probabilities)[0]
    return population[selected_index]

def order_crossover(parent1, parent2):
    start, end = sorted(random.sample(range(len(parent1)), 2))
    child = [None] * len(parent1)
    child[start:end] = parent1[start:end]
    fill_position = end
    for gene in parent2:
        if gene not in child:
            if fill_position == len(parent1):
                fill_position = 0
            child[fill_position] = gene
            fill_position += 1
    return child

def swap_mutation(chromosome):
    i, j = random.sample(range(len(chromosome)), 2)
    chromosome[i], chromosome[j] = chromosome[j], chromosome[i]

def determine_truck_usage(total_weight):
    truck_a_capacity = trucklist[0]["capacity"]
    truck_b_capacity = trucklist[1]["capacity"]

    if total_weight <= truck_b_capacity:
        return 1, "Truck B"
    elif total_weight <= truck_a_capacity:
        return 1, "Truck A"
    else:
        num_truck_a = math.ceil(total_weight / truck_a_capacity)
        num_truck_b = math.ceil(total_weight / truck_b_capacity)
        return num_truck_a, "Truck A", num_truck_b, "Truck B"

def genetic_algorithm(orders, pop_size, num_generations):
    population = initialize_population(pop_size, orders)
    best_chromosome = None
    best_fitness = 0
    best_route_cost = float('inf')
    best_route_distance = 0
    best_route_weight = 0

    for generation in range(num_generations):
        fitnesses = [calculate_fitness(chrom) for chrom in population]
        new_population = []

        for _ in range(pop_size):
            parent1 = roulette_wheel_selection(population, fitnesses)
            parent2 = roulette_wheel_selection(population, fitnesses)
            child = order_crossover(parent1, parent2)
            if random.random() < 0.1:  # Mutation probability
                swap_mutation(child)
            new_population.append(child)

        population = new_population

        for chrom in population:
            fitness, cost, distance, weight = calculate_fitness(chrom)
            if fitness > best_fitness:
                best_fitness = fitness
                best_chromosome = chrom
                best_route_cost = cost
                best_route_distance = distance
                best_route_weight = weight

    if best_chromosome:
        num_trucks_a, truck_a_name, num_trucks_b, truck_b_name = determine_truck_usage(best_route_weight)
        return best_chromosome, best_fitness, best_route_cost, best_route_distance, best_route_weight, num_trucks_a, truck_a_name, num_trucks_b, truck_b_name
    else:
        return None, 0, 0, 0, 0, 0, "", 0, ""

# Run the Algorithm
best_route, best_fitness, best_route_cost, best_route_distance, best_route_weight, num_trucks_a, truck_a_name, num_trucks_b, truck_b_name = genetic_algorithm(orderlist, pop_size=100, num_generations=1000)

best_route_order_ids = [order["orderid"] for order in best_route]
print("Best Route Order IDs:", best_route_order_ids)
print("Best Fitness Score:", best_fitness)
print("Overall Cost:", best_route_cost)
print("Overall Distance:", best_route_distance)
print("Overall Weight:", best_route_weight)
print("Number of Truck A:", num_trucks_a, ", Type:", truck_a_name)
print("Number of Truck B:", num_trucks_b, ", Type:", truck_b_name)

