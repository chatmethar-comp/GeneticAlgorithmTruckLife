import random

# Example structures for the input data
orderlist = [
    {"orderid": 1, "receptiondate": "2024-06-01", "latitude": 34.05, "longitude": -118.25, "desired_delivery_date": "2024-06-05", "product": 101},
    {"orderid": 2, "receptiondate": "2024-06-02", "latitude": 36.16, "longitude": -115.15, "desired_delivery_date": "2024-06-06", "product": 102},
    {"orderid": 3, "receptiondate": "2024-06-03", "latitude": 40.71, "longitude": -74.01, "desired_delivery_date": "2024-06-07", "product": 103},
    # Add more orders...
]
productlist = [
    {"productid": 101, "productname": "Product A", "weight": 10},
    {"productid": 102, "productname": "Product B", "weight": 20},
    {"productid": 103, "productname": "Product C", "weight": 30},
    {"productid": 104, "productname": "Product D", "weight": 40},
    # Add more products...
]
trucklist = [
    {"truckid": 1, "truckname": "Truck A", "capacity": 1000},
    {"truckid": 2, "truckname": "Truck B", "capacity": 500},
    {"truckid": 3, "truckname": "Truck C", "capacity": 800},
    # Add more trucks...
]
outsourcingfee = {
    1: 200,  # Example outsourcing fee for orderid 1
    2: 300,  # Example outsourcing fee for orderid 2
    3: 400,  # Example outsourcing fee for orderid 3
    # Add more outsourcing fees...
}

# Utility functions
def calculate_distance(lat1, lon1, lat2, lon2):
    # Simple Euclidean distance for example purposes
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2)**0.5

def get_product_weight(productid):
    return next(product["weight"] for product in productlist if product["productid"] == productid)

def initialize_population(pop_size, orders, trucks):
    population = []
    for _ in range(pop_size):
        chromosome = [(random.choice(trucks), order) for order in orders]
        random.shuffle(chromosome)
        population.append(chromosome)
    return population

def calculate_fitness(chromosome):
    total_cost = 0
    for truck, order in chromosome:
        product_weight = get_product_weight(order["product"])
        if product_weight <= truck["capacity"]:
            route_distance = calculate_distance(order["latitude"], order["longitude"], truck["latitude"], truck["longitude"])
            total_cost += route_distance  # Assume cost per km is 1 unit for simplicity
        else:
            total_cost += outsourcingfee[order["orderid"]]
    return 1 / total_cost  # Fitness is the inverse of cost

def roulette_wheel_selection(population, fitnesses):
    total_fitness = sum(fitnesses)
    probabilities = [f / total_fitness for f in fitnesses]
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

def genetic_algorithm(orders, trucks, pop_size, num_generations):
    population = initialize_population(pop_size, orders, trucks)
    best_chromosome = None
    best_fitness = 0

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

        best_generation_chromosome = population[fitnesses.index(max(fitnesses))]
        best_generation_fitness = max(fitnesses)

        if best_generation_fitness > best_fitness:
            best_fitness = best_generation_fitness
            best_chromosome = best_generation_chromosome

    return best_chromosome, best_fitness

# Run the Algorithm
best_route, best_route_fitness = genetic_algorithm(orderlist, trucklist, pop_size=100, num_generations=1000)
print("Best Route:", best_route)
print("Best Route Fitness:", best_route_fitness)
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⣀⠤⠔⠂⠈⠉⠁⠒⠤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡔⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠓⠦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⣔⠑⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⢕⠉⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⢨⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ⢸⢎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣶⣿⣿⣷⣦⣄⡀⠀⢀⣀⣀⣤⣤⡄⠀⠀⠀⠀⠀⠀⠀⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⣿⣿⣿⣿⣿⣿⣿⣿⢽⣿⣿⣿⣿⣿⣾⣾⣄⢀⣠⡴⢞⠟⣿⡵⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⢾⡟⠛⠿⠿⣿⣿⠁⠸⣿⣿⣿⣿⣿⣿⣿⡷⠚⠉⢠⢎⣎⠀⣇⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⢹⡇⠉⠒⠒⢺⠃⠀⠀⠱⣌⣉⠉⠙⠋⣡⠅⠀⠀⣼⢀⣋⣔⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ⢸⣇⡀⣀⣀⣾⣄⣀⣦⣀⠄⢈⡉⠉⠉⢀⠀⢀⣾⣯⠈⢀⡝⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ⣿⣇⡿⣿⣿⠿⣽⣿⣧⣦⣤⣹⣶⢦⢁⣤⣾⣻⣏⠏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⢿⣾⢨⠛⠿⣾⣲⡾⠿⠟⠛⣟⣾⣿⣽⣿⡿⠈⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠻⣬⢷⣦⣤⣄⣱⡜⠀⣵⡿⣿⣿⣿⠟⠁⠀⣷⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠈⢿⣶⡉⢹⣏⣁⣤⣿⣿⣿⡿⠟⠁⠀⠀⢸⣿⣿⣿⣿⣿⡿⣲⠶⣤⣤⣀⡀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⠀⠀⠀⠀⣴⣾⣿⣿⣿⡆⠀⠀⢔⣿⡿⠻⢿⣿⣿⣿⣿⡿⠋⠁⠈⠀⠀⢀⣿⣿⣿⣽⣿⣿⣿⣾⠞⠿⢽⣺⣾⣿⡷⣶⢤⣄
# ⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⠀⢠⣷⣿⣧⠀⠀⠈⠙⠉⠁⠀⠀⠀⠀⠀⠀⠀⣿⣿⢿⣿⣿⣿⣿⣿⠅⠠⡪⣿⣽⣿⣿⡛⠉⢻
# ⡄⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣋⢸⣿⣿⣿⡀⠀⠘⡀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣫⣿⣿⣿⣿⣿⡷⢾⣷⣿⣿⣿⣿⣿⣄⣾
# ⣿⣆⠀⣀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡷⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⣿⣋⠿⣿⣿⣿⣃⣤⣿⣿⣿⣿⣿⣿⣿⣟
# ⣿⣿⣷⣿⣿⣿⣿⣿⣿⡏⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣬⣄⠀⠀⠀⠀⠀⣀⣀⣤⣾⣿⣿⣿⣿⣏⣤⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣻⣿
# ⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⡼⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣟
# ⣿⣿⣿⣿⣿⣿⣿⡟⠀⢘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣽⣿⣿⣿
# ⣿⣿⣿⣿⣿⣿⣿⠁⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣼
# ⣿⣿⣿⣿⣿⡿⠋⢳⣾⣿⣿⣿⣿⣿⣿⣿⣿⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿
# ⣿⣿⣿⣿⣿⠁⡄⣾⣿⣿⣿⣿⣿⣿⣿⣿⡯⢺⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢰⣿⣿⣿⣿⣿
# ⡿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⡷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⢿⣿⣿⣿⢴⣿⣿⣿⣿⣿⣿
# ⣦⣤⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⡟⣺⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
# ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣵⣿⣿⣿⣿⡟⣰⣿⣿⣿⣿⣿⣿⣿⣿⣫⣵⣖
# ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣛⣉⠁
# ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾
# ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣆
# ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣻⠚