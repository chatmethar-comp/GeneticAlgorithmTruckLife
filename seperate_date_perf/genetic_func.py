import copy
import func
import osm
import random
import time
import numpy as np


warehouse_location = [13.7438, 100.5626]
Truck_weights = [1000, 1000, 1000, 1000, 1000, 1000, 2000, 2000, 2000, 2000]
# Truck_weights = [1900, 1900, 1900, 1100]
filepath_order = "order.csv"
filepath_product = "product.csv"
order_delivery_date_cache = {}
global desired_delivery_date
desired_delivery_date = []
global truck_num
truck_num = len(Truck_weights)
ex_data = func.read_csv_to_list(filepath_order)
product_list = func.read_csv_to_list(filepath_product)
new_order = func.product_to_weight(ex_data, product_list)
distance_m = func.create_distance_matrix(warehouse_location, new_order)
time_m = func.create_time_matrix(warehouse_location, new_order)

def gen_individual(order_data_w,truck_weights):
    global desired_delivery_date
    def make_hashable(item):
        if isinstance(item, (list, tuple)):
            return tuple(make_hashable(subitem) for subitem in item)  # Recursively convert each subitem to a tuple
        return item 

    individual = {}
    for order in order_data_w:
        start_date = order[4]
        end_date = order[5]   
        delivery_dates = list(range(start_date, end_date + 1))  # Include end date
        for date in delivery_dates:
            desired_delivery_date.append(date)
            delivery_dates_tuple = make_hashable(delivery_dates)
            order_delivery_date_cache[order[0]] = delivery_dates_tuple
    desired_delivery_date = list(dict.fromkeys(desired_delivery_date))
    desired_delivery_date.sort()

    for date in desired_delivery_date:
        individual[date]={}
        individual[date]["Outsourcing"]=[]
        for i in range(truck_num):
            individual[date][f"Truck{i+1}"] = {}
            individual[date][f"Truck{i+1}"]["weight"] = truck_weights[i] 
            individual[date][f"Truck{i+1}"]["order"] = []

    shuffle_order_data_w = copy.copy(order_data_w)
    random.shuffle(shuffle_order_data_w)
    for order in shuffle_order_data_w:
        rand_date = random.choice(order_delivery_date_cache[order[0]])
        individual[rand_date]["Outsourcing"].append(order[0])
    return individual

def initialize_population(pop_size,order_data_w,truck_weights):
    population = []
    while len(population) < pop_size:
        population.append(gen_individual(order_data_w,truck_weights))
    return population


def crossover(individual1,individual2,order_data_w):
    global desired_delivery_date
    individual1_c = func.fast_deepcopy(individual1)
    individual2_c = func.fast_deepcopy(individual2)
    for i in range(len(individual1_c.keys())):
        date_cross = random.choice(desired_delivery_date)
        try:
            item_sw = random.choice(individual1_c[date_cross]["Outsourcing"])
            for date in order_delivery_date_cache[item_sw]:
                for truck in individual2_c[date].keys():
                    if truck != "Outsourcing":
                        try:
                            individual2_c[date][truck]["order"].remove(item_sw)
                            individual2_c[date][truck]["weight"]+=order_data_w[item_sw-1][-1]
                            individual2_c[date_cross]["Outsourcing"].append(item_sw)
                            break
                        except ValueError:
                            continue
        except IndexError: 
            continue
    return individual2_c

def assign_to_truck(individual, order_data_w, time_matrix):
    global desired_delivery_date
    individual_c = func.fast_deepcopy(individual)

    for i in range(4):
        for date in desired_delivery_date:
            try:
                # Get random outsourced order
                outsourcing_orders = individual_c[date]["Outsourcing"]
                if not outsourcing_orders:
                    continue  # Skip if no orders left in outsourcing

                item_sw = random.choice(outsourcing_orders)

                # Precompute order weight
                order_weight = order_data_w[item_sw-1][-1]

                # Try to assign to a truck
                for _ in range(2):  # Max two attempts to assign to a truck
                    truck_to_assign = random.randint(1, truck_num)
                    truck_info = individual_c[date][f"Truck{truck_to_assign}"]
                    truck_weight_capacity = truck_info["weight"]

                    if order_weight <= truck_weight_capacity:
                        # Generate random insertion index only once
                        truck_orders = truck_info["order"]
                        insertion_index = random.randint(0, len(truck_orders))

                        if func.check_time_insert_item(item_sw, insertion_index, truck_orders, order_data_w, time_matrix):
                            # Perform the insertion and update weight
                            truck_orders.insert(insertion_index, item_sw)
                            truck_info["weight"] -= order_weight
                            outsourcing_orders.remove(item_sw)
                            break  # Exit loop after successful assignment

            except IndexError:
                continue  # Skip if any indexing error occurs (e.g., empty outsourcing)

    return individual_c


def mutate(individual, order_data_w, mutation_rate, time_matrix):
    global desired_delivery_date
    mutated_solution = func.fast_deepcopy(individual)
    truck_more_than_one = truck_num > 1  # Boolean flag for truck count

    for date in desired_delivery_date:
        if random.random() < mutation_rate:
            # Move order from Outsourcing to a random date
            for order in mutated_solution[date]["Outsourcing"]:
                if order:
                    random_date = random.choice(order_delivery_date_cache[order])
                    mutated_solution[random_date]["Outsourcing"].append(order)
                    mutated_solution[date]["Outsourcing"].remove(order)

            if truck_more_than_one:
                if random.random() <= 0.6:
                    source_truck = random.randint(1, truck_num)

                    # Get a random order from the source truck
                    source_order_list = mutated_solution[date][f"Truck{source_truck}"]["order"]
                    if not source_order_list:
                        continue  # Skip if the truck is empty

                    item_from_truck_source = random.choice(source_order_list)

                    # Find a truck to assign this order
                    truck_to_assign = random.randint(1, truck_num)
                    while truck_to_assign == source_truck:
                        truck_to_assign = random.randint(1, truck_num)

                    # Check weight capacity and time constraints
                    if (order_data_w[item_from_truck_source - 1][-1] <= mutated_solution[date][f"Truck{truck_to_assign}"]["weight"]):
                        if func.check_time_add_item(item_from_truck_source, mutated_solution[date][f"Truck{truck_to_assign}"]["order"], order_data_w, time_matrix):
                            mutated_solution[date][f"Truck{truck_to_assign}"]["order"].append(item_from_truck_source)
                            mutated_solution[date][f"Truck{truck_to_assign}"]["weight"] -= order_data_w[item_from_truck_source - 1][-1]
                            mutated_solution[date][f"Truck{source_truck}"]["order"].remove(item_from_truck_source)
                            mutated_solution[date][f"Truck{source_truck}"]["weight"] += order_data_w[item_from_truck_source - 1][-1]

            # Handle moving a random item from a random truck to Outsourcing
            random_truck = random.randint(1, truck_num)
            random_order_list = mutated_solution[date][f"Truck{random_truck}"]["order"]
            if random_order_list:  # Only proceed if the truck is not empty
                random_item = random.choice(random_order_list)
                mutated_solution[date]["Outsourcing"].append(random_item)
                mutated_solution[date][f"Truck{random_truck}"]["order"].remove(random_item)
                mutated_solution[date][f"Truck{random_truck}"]["weight"] += order_data_w[random_item - 1][-1]

    return mutated_solution


def calculate_fitness_score(individual,order_data_w,distance_matrix,time_matrix):
    out_source_fee = func.calculate_outsourcing_fee(individual,order_data_w,distance_matrix,desired_delivery_date)
    wait_time,outsource_score = func.calculate_wait_time_and_outsourcingscore(individual,order_data_w,time_matrix,desired_delivery_date)
    fitness_score = out_source_fee+wait_time+outsource_score
    return fitness_score

fitness_cache = {}
def evaluate_fitness(individual, order_data_w, distance_matrix, time_matrix):
    # Helper function to convert individual into a hashable tuple
    # def make_hashable(item):
    #     if isinstance(item, (list, tuple)):
    #         return tuple(make_hashable(subitem) for subitem in item)  # Recursively convert each subitem to a tuple
    #     return item  # Return the item itself if it's not a list or tuple (e.g., int)

    # # Convert individual to a hashable tuple
    # individual_tuple = make_hashable(individual)

    # # Check if the individual's fitness is already cached
    # if individual_tuple in fitness_cache:
    #     return fitness_cache[individual_tuple]

    # Compute the fitness using the existing function
    fitness_value = calculate_fitness_score(individual, order_data_w, distance_matrix, time_matrix)
    
    # Cache the computed fitness
    # fitness_cache[individual_tuple] = fitness_value

    return fitness_value

def rank_solutions(population, order_data_w, distance_matrix, time_matrix):
    fitness_results = [
        (evaluate_fitness(individual, order_data_w, distance_matrix, time_matrix), individual)
        for individual in population
    ]
    
    # Sort population by fitness (lower fitness is better)
    return sorted(fitness_results, key=lambda x: x[0])

def selection(fitness_results, elite_size):
    best_individuals = [fitness_results[i][1] for i in range(elite_size-50)]
    for _ in range(50):
        a=random.choice(fitness_results)
        best_individuals.append(a[1])
    return best_individuals


def next_generation(current_gen, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix):
    ranked_solutions = rank_solutions(current_gen, order_data_w, distance_matrix, time_matrix)
    current_best_fitness = ranked_solutions[0][0]  # Lowest outsourcing fee in this generation
    
    print(f"Current gen best fitness score: {current_best_fitness}")
    
    selection_results = selection(ranked_solutions, elite_size)
    children = copy.deepcopy(selection_results)
    while len(children) < len(current_gen):
        parent1, parent2 = random.sample(selection_results, 2)
        parent1 = mutate(parent1, order_data_w, mutation_rate, time_matrix)
        parent2 = mutate(parent2, order_data_w, mutation_rate, time_matrix)
        # child = crossover(parent1, parent2, order_data_w,time_matrix,truck_weights,work_time)
        child = crossover(parent1, parent2,order_data_w)
        # child = mutate(child, truck_weights, order_data_w, mutation_rate, work_time, time_matrix)
        children.append(assign_to_truck(child, order_data_w, time_matrix))
    
    return children  


def genetic_algorithm(pop_size, generations, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix, truck_weights):
    population = [gen_individual(order_data_w, truck_weights) for _ in range(pop_size)]
    
    for gen in range(generations):
        print(f"Gen {gen}")
        population = next_generation(population, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix)

    best_solution = rank_solutions(population, order_data_w, distance_matrix, time_matrix)[0][1]
    return best_solution

def optimize_routes(order_data_w, distance_matrix, time_matrix, truck_weights, pop_size=1250, elite_size=125, mutation_rate=0.1, generations=50):
    best_solution = genetic_algorithm(pop_size, generations, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix, truck_weights)
    return best_solution




# print(new_order)
# best_fee_list = []
# sumtime=0
# mut_rate = 0.00
# score_list = []
# for _ in range(5):
#     genetic_func.fitness_cache = {}
#     for _ in range(5):
start_time = time.time()
best_solution = optimize_routes(
    new_order, distance_m, time_m, Truck_weights, generations=70
)
best_out_sourcing_fee = func.calculate_outsourcing_fee(
    best_solution, new_order, distance_m,desired_delivery_date
)
print("Best solution: ", best_solution)
for date in desired_delivery_date:
    print(date)
    for key in best_solution[date].keys():
        if key == 'Outsourcing':
            print(f"Outsourcing: {best_solution[date]["Outsourcing"]}")
        else:
            print(f"{key}: Weight {best_solution[date][key]["weight"]}")
            print(f"Order {best_solution[date][key]["order"]}")
print("best out fee: ", best_out_sourcing_fee)
print(f"Time taken {time.time()-start_time}")

to_map = func.to_truck_routes(best_solution, new_order, desired_delivery_date)
osm.create_map_tree(warehouse_location, to_map, osm.colors)

excel_input = func.output_as_excel(best_solution, new_order, time_m, desired_delivery_date)
func.Excel_writer(excel_input)