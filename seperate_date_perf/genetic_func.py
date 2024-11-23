import copy
import func
import osm
import random
import time
from concurrent.futures import ThreadPoolExecutor

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


def gen_individual(order_data_w, truck_weights):
    global desired_delivery_date

    def make_hashable(item):
        if isinstance(item, (list, tuple)):
            return tuple(
                make_hashable(subitem) for subitem in item
            )  # Recursively convert each subitem to a tuple
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
        individual[date] = {}
        individual[date]["Outsourcing"] = []
        for i in range(truck_num):
            individual[date][f"Truck{i+1}"] = {}
            individual[date][f"Truck{i+1}"]["weight"] = truck_weights[i]
            individual[date][f"Truck{i+1}"]["capacity"] = [truck_weights[i]]
            individual[date][f"Truck{i+1}"]["order"] = []

    shuffle_order_data_w = copy.copy(order_data_w)
    random.shuffle(shuffle_order_data_w)
    for order in shuffle_order_data_w:
        rand_date = random.choice(order_delivery_date_cache[order[0]])
        individual[rand_date]["Outsourcing"].append(order[0])
    return individual

# no use
def initialize_population(pop_size, order_data_w, truck_weights):
    population = []
    while len(population) < pop_size:
        population.append(gen_individual(order_data_w, truck_weights))
    return population


def crossover(individual1, individual2, order_data_w):
    global desired_delivery_date
    individual1_c = func.fast_deepcopy(individual1)
    individual2_c = func.fast_deepcopy(individual2)

    for _ in range(len(individual1_c.keys())):
        date_cross = random.choice(desired_delivery_date)

        if not individual1_c[date_cross]["Outsourcing"]:
            continue  # Skip if there are no items to swap for the chosen date

        outsource_item = random.choice(individual1_c[date_cross]["Outsourcing"])

        for date in order_delivery_date_cache[outsource_item]:
            for truck, truck_data in individual2_c[date].items():
                if truck == "Outsourcing":
                    if outsource_item in truck_data:
                        truck_data.remove(outsource_item)
                        individual2_c[date_cross]["Outsourcing"].append(outsource_item)
                    break  # Move to next item after swapping
                else:
                    if outsource_item in truck_data["order"]:
                        item_index = truck_data["order"].index(outsource_item)
                        capacity_index = truck_data["order"][:item_index].count(0)

                        del truck_data["order"][item_index]
                        truck_data["capacity"][capacity_index] += order_data_w[outsource_item - 1][-1]
                        if (
                            capacity_index > 0
                            and truck_data["capacity"][capacity_index]
                            == truck_data["weight"]
                            and truck_data["order"][item_index - 1] == 0
                        ):
                            del truck_data["capacity"][capacity_index]
                            del truck_data["order"][item_index - 1]

                        individual2_c[date_cross]["Outsourcing"].append(outsource_item)
                        break
    return individual2_c


def assign_to_truck(individual, order_data_w, time_matrix):
    global desired_delivery_date, truck_num
    individual_c = func.fast_deepcopy(individual)

    for _ in range(int(truck_num / 2)):  # Attempt up to four reassignments
        for date in desired_delivery_date:
            # Get random outsourced order, skip if none available
            outsourcing_orders = individual_c[date]["Outsourcing"]
            if not outsourcing_orders:
                continue

            outsourced_order = random.choice(outsourcing_orders)
            order_weight = order_data_w[outsourced_order - 1][-1]

            # Attempt assignment to a truck with two attempts
            for _ in range(2):
                truck_to_assign = random.randint(1, truck_num)
                truck_info = individual_c[date][f"Truck{truck_to_assign}"]
                truck_orders = truck_info["order"]

                # Determine insertion point and capacity index
                insertion_index = random.randint(0, len(truck_orders))

                capacity_index = truck_info["order"][:insertion_index].count(0)

                # Check weight capacity and perform insertion if conditions are met
                if order_weight <= truck_info["capacity"][capacity_index]:
                    if func.check_time_insert_item(
                        outsourced_order,
                        insertion_index,
                        truck_orders,
                        order_data_w,
                        time_matrix,
                    ):
                        truck_orders.insert(insertion_index, outsourced_order)
                        truck_info["capacity"][capacity_index] -= order_weight
                        outsourcing_orders.remove(outsourced_order)
                        break  # Exit after successful assignment
    return individual_c


def mutate(individual, order_data_w, mutation_rate, time_matrix):
    global desired_delivery_date, truck_num
    mutated_solution = func.fast_deepcopy(individual)
    multiple_trucks = truck_num > 1

    for date in desired_delivery_date:
        if random.random() < mutation_rate:
            # Move orders from Outsourcing to a random date's Outsourcing
            outsourcing_orders = mutated_solution[date]["Outsourcing"]
            for order in outsourcing_orders[:]:  # Copy to avoid mutation during iteration
                if order:
                    random_date = random.choice(order_delivery_date_cache[order])
                    mutated_solution[random_date]["Outsourcing"].append(order)
                    outsourcing_orders.remove(order)

            # Inter-truck order reassignment if there are multiple trucks
            if multiple_trucks and random.random() <= 0.6:
                source_truck_num = random.randint(1, truck_num)
                source_truck = mutated_solution[date][f"Truck{source_truck_num}"]

                if source_truck["order"]:  # Ensure the source truck has orders
                    item_from_truck = random.choice(source_truck["order"])
                    if item_from_truck:
                        target_truck_num = random.choice(
                            [
                                i
                                for i in range(1, truck_num + 1)
                                if i != source_truck_num
                            ]
                        )
                        target_truck = mutated_solution[date][
                            f"Truck{target_truck_num}"
                        ]

                        order_weight = order_data_w[item_from_truck - 1][-1]
                        if order_weight <= target_truck["capacity"][-1]:
                            if func.check_time_add_item(
                                item_from_truck,
                                target_truck["order"],
                                order_data_w,
                                time_matrix,
                            ):
                                target_truck["order"].append(item_from_truck)
                                target_truck["capacity"][-1] -= order_weight
                                item_index = source_truck["order"].index(
                                    item_from_truck
                                )
                                capacity_index = source_truck["order"][
                                    :item_index
                                ].count(0)
                                source_truck["order"].remove(item_from_truck)
                                source_truck["capacity"][capacity_index] += order_weight
                                if (
                                    len(source_truck["capacity"]) > 1
                                    and source_truck["capacity"][capacity_index]
                                    == source_truck["weight"]
                                    and source_truck["order"][item_index - 1] == 0
                                ):
                                    del source_truck["capacity"][capacity_index]
                                    del source_truck["order"][item_index - 1]

            # Randomly move a truck's item to Outsourcing
            random_truck_num = random.randint(1, truck_num)
            random_truck = mutated_solution[date][f"Truck{random_truck_num}"]
            valid_items = [i for i, x in enumerate(random_truck["order"]) if x != 0]

            if valid_items:  # Only proceed if there are non-zero items to choose from
                random_item_index = random.choice(valid_items)
                item_to_move = random_truck["order"][random_item_index]

                capacity_index = random_truck["order"][:random_item_index].count(0)
                # Move order to Outsourcing and adjust capacity
                mutated_solution[date]["Outsourcing"].append(item_to_move)
                random_truck["capacity"][capacity_index] += order_data_w[
                    item_to_move - 1
                ][-1]
                random_truck["order"].remove(item_to_move)

        # Randomly add a (0) to trucks
        for truck_key, truck_data in mutated_solution[date].items():
            if (
                truck_key != "Outsourcing"
            ):
                insertion_index = random.randint(1,len(truck_data["order"])+1)
                if(
                    truck_data["order"]
                    and truck_data["order"][-1]
                    and random.random() < mutation_rate
                ):
                    if func.check_time_insert_item(0,insertion_index,truck_data["order"],order_data_w,time_matrix):
                        truck_data["order"].insert(insertion_index, 0)
                        capacity_index = truck_data["order"][:insertion_index].count(0)
                        truck_data["capacity"].insert(capacity_index+1, truck_data["weight"])
                        for order in truck_data["order"][insertion_index+1:]:
                            if order:
                                truck_data["capacity"][capacity_index+1]-=order_data_w[order-1][-1]
                                truck_data["capacity"][capacity_index]+=order_data_w[order-1][-1]
                            else:
                                break
                elif(
                    truck_data["order"]
                    and truck_data["order"][-1]
                    and random.random() < (2*mutation_rate)
                    ):
                    truck_data["order"].append(0)
                    truck_data["capacity"].append(truck_data["weight"])

    return mutated_solution


def calculate_fitness_score(individual, order_data_w, distance_matrix, time_matrix):
    out_source_fee = func.calculate_outsourcing_fee(
        individual, order_data_w, distance_matrix, desired_delivery_date
    )
    wait_time, outsource_score = func.calculate_wait_time_and_outsourcingscore(
        individual, order_data_w, time_matrix, desired_delivery_date
    )
    fitness_score = out_source_fee + wait_time + outsource_score
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
    fitness_value = calculate_fitness_score(
        individual, order_data_w, distance_matrix, time_matrix
    )

    # Cache the computed fitness
    # fitness_cache[individual_tuple] = fitness_value

    return fitness_value


def rank_solutions(population, order_data_w, distance_matrix, time_matrix):
    fitness_results = [
        (
            evaluate_fitness(individual, order_data_w, distance_matrix, time_matrix),
            individual,
        )
        for individual in population
    ]

    # Sort population by fitness (lower fitness is better)
    return sorted(fitness_results, key=lambda x: x[0])


def selection(fitness_results, elite_size):
    best_individuals = [fitness_results[i][1] for i in range(elite_size - 50)]
    for _ in range(50):
        a = random.choice(fitness_results)
        best_individuals.append(a[1])
    return best_individuals


def next_generation(
    current_gen, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix
):
    ranked_solutions = rank_solutions(
        current_gen, order_data_w, distance_matrix, time_matrix
    )
    current_best_fitness = ranked_solutions[0][0]  # Best score in this generation

    print(f"Current gen best fitness score: {current_best_fitness}")

    # Selection and cloning elite individuals
    selection_results = selection(ranked_solutions, elite_size)
    children = copy.deepcopy(selection_results)

    # Parallel mutation for each parent in the selection
    def mutate_individual(individual):
        # Perform mutation on a deep copy of the individual to avoid shared state issues
        return mutate(
            copy.deepcopy(individual), order_data_w, mutation_rate, time_matrix
        )

    # Use ThreadPoolExecutor to parallelize mutation
    with ThreadPoolExecutor() as executor:
        # Apply mutation to selected individuals
        mutated_parents = list(executor.map(mutate_individual, selection_results))

    # Add mutated individuals as children, along with original elite copies
    children.extend(mutated_parents)

    # If more children are needed, perform additional crossovers
    while len(children) < len(current_gen):
        parent1, parent2 = random.sample(mutated_parents, 2)
        child = crossover(parent1, parent2, order_data_w)
        children.append(assign_to_truck(child, order_data_w, time_matrix))

    return children


def genetic_algorithm(
    pop_size,
    generations,
    elite_size,
    mutation_rate,
    order_data_w,
    distance_matrix,
    time_matrix,
    truck_weights,
):
    population = [gen_individual(order_data_w, truck_weights) for _ in range(pop_size)]

    for gen in range(generations):
        print(f"Gen {gen}")
        population = next_generation(
            population,
            elite_size,
            mutation_rate,
            order_data_w,
            distance_matrix,
            time_matrix,
        )

    best_solution = rank_solutions(
        population, order_data_w, distance_matrix, time_matrix
    )[0][1]
    return best_solution


def optimize_routes(
    order_data_w,
    distance_matrix,
    time_matrix,
    truck_weights,
    pop_size=1250,
    elite_size=125,
    mutation_rate=0.05,
    generations=50,
):
    best_solution = genetic_algorithm(
        pop_size,
        generations,
        elite_size,
        mutation_rate,
        order_data_w,
        distance_matrix,
        time_matrix,
        truck_weights,
    )
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
    new_order, distance_m, time_m, Truck_weights, generations=150
)
best_out_sourcing_fee = func.calculate_outsourcing_fee(
    best_solution, new_order, distance_m, desired_delivery_date
)
print("Best solution: ", best_solution)
for date in desired_delivery_date:
    print(date)
    for key in best_solution[date].keys():
        if key == "Outsourcing":
            print(f"Outsourcing: {best_solution[date]['Outsourcing']}")
        else:
            print(f"{key}: Weight {best_solution[date][key]['capacity']}")
            print(f"Order {best_solution[date][key]['order']}")
            hour, minute = func.out_put_time_show(
                best_solution[date][key]["order"], new_order, time_m
            )
            print(f"Time end: {hour}:{minute}")
print("best out fee: ", best_out_sourcing_fee)
print(f"Time taken {time.time()-start_time}")

to_map = func.to_truck_routes(best_solution, new_order, desired_delivery_date)
osm.create_map_tree(warehouse_location, to_map, osm.colors)

excel_input = func.output_as_excel(
    best_solution, new_order, time_m, desired_delivery_date
)
func.Excel_writer(excel_input)

print(f"Time taken {time.time()-start_time}")