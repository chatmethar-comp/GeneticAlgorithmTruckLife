import copy
from datetime import datetime
import func
import osm
import random
import time
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

warehouse_location = [13.7438, 100.5626]
# Truck_weights = [1000, 1000, 1000, 1000, 1000, 1000, 2000, 2000, 2000, 2000]
Truck_weights = [500, 500, 1000, 1000, 2000]
filepath_order = "order.csv"
filepath_product = "product.csv"
order_delivery_date_cache = {}
global desired_delivery_date
desired_delivery_date = []
global truck_num
truck_num = len(Truck_weights)
# ex_data = func.read_csv_to_list(filepath_order)
# product_list = func.read_csv_to_list(filepath_product)
# new_order = func.product_to_weight(ex_data, product_list)
# print(new_order)
# exit()
# distance_m = func.create_distance_matrix(warehouse_location, new_order)
# time_m = func.create_time_matrix(warehouse_location, new_order)


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
    for _ in range(int(truck_num+1)):  # Attempt up to four reassignments
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
                capable_indices = []
                for insertion_index in range(len(truck_orders) + 1):  # Include the position after the last item
                    capacity_index = truck_orders[:insertion_index].count(0)  # Get the capacity index for this insertion point
                    if order_weight <= truck_info["capacity"][capacity_index]:
                        if func.check_time_insert_item(outsourced_order, insertion_index, truck_orders, order_data_w, time_matrix):
                            capable_indices.append(insertion_index)
                
                if capable_indices:
                    # print(capable_indices)
                    insertion_index = random.choice(capable_indices)
                    capacity_index = truck_orders[:insertion_index].count(0)
                    truck_orders.insert(insertion_index, outsourced_order)
                    truck_info["capacity"][capacity_index] -= order_weight
                    outsourcing_orders.remove(outsourced_order)
                    break
    return individual_c


def mutate(individual, order_data_w, mutation_rate, time_matrix):
    global desired_delivery_date, truck_num
    mutated_solution = func.fast_deepcopy(individual)

    for date in desired_delivery_date:
        if random.random() < mutation_rate:

            # (A) Randomly move outsourcing orders across dates
            outsourcing_orders = mutated_solution[date]["Outsourcing"]
            for order in outsourcing_orders[:]:
                if order:
                    random_date = random.choice(order_delivery_date_cache[order])
                    mutated_solution[random_date]["Outsourcing"].append(order)
                    outsourcing_orders.remove(order)

            # (B) Randomly move ONE truck order to outsourcing
            random_truck_num = random.randint(1, truck_num)
            random_truck = mutated_solution[date][f"Truck{random_truck_num}"]

            valid_items = [i for i, x in enumerate(random_truck["order"]) if x != 0]
            if valid_items:
                random_item_index = random.choice(valid_items)
                item_to_move = random_truck["order"][random_item_index]

                capacity_index = random_truck["order"][:random_item_index].count(0)
                mutated_solution[date]["Outsourcing"].append(item_to_move)

                random_truck["capacity"][capacity_index] += order_data_w[item_to_move - 1][-1]
                random_truck["order"].remove(item_to_move)

        # (C) Random route segmentation (0 insertion)
        for truck_key, truck_data in mutated_solution[date].items():
            if truck_key == "Outsourcing":
                continue

            if (
                truck_data["order"]
                and truck_data["order"][-1]
                and random.random() < mutation_rate
            ):
                insertion_index = random.randint(1, len(truck_data["order"]))
                if func.check_time_insert_item(
                    0,
                    insertion_index,
                    truck_data["order"],
                    order_data_w,
                    time_matrix,
                ):
                    truck_data["order"].insert(insertion_index, 0)
                    capacity_index = truck_data["order"][:insertion_index].count(0)
                    truck_data["capacity"].insert(capacity_index + 1, truck_data["weight"])

    return mutated_solution

def two_opt_star(route1, route2):
    """
    Perform a 2-opt* exchange between two routes.
    Route format: [0, a, b, c, 0, d, e, 0] or similar
    """

    # Remove trailing depot markers for safety
    r1 = route1[:]
    r2 = route2[:]

    # Valid cut positions (cannot cut at depot)
    r1_candidates = [i for i in range(1, len(r1) - 1) if r1[i] != 0]
    r2_candidates = [i for i in range(1, len(r2) - 1) if r2[i] != 0]

    if not r1_candidates or not r2_candidates:
        return route1, route2  # No change possible

    cut1 = random.choice(r1_candidates)
    cut2 = random.choice(r2_candidates)

    # Split routes
    new_r1 = r1[:cut1] + r2[cut2:]
    new_r2 = r2[:cut2] + r1[cut1:]

    return new_r1, new_r2

def local_search(individual, order_data_w, time_matrix, ls_prob=0.3):
    """
    Apply local search (2-opt / 2-opt*) to an individual with probability ls_prob
    """
    if random.random() > ls_prob:
        return individual  # Skip LS

    improved = copy.deepcopy(individual)

    for date, day_plan in improved.items():
        trucks = [k for k in day_plan if k != "Outsourcing"]

        if len(trucks) < 2:
            continue

        # Pick two different trucks
        t1, t2 = random.sample(trucks, 2)
        truck1 = day_plan[t1]
        truck2 = day_plan[t2]

        r1, r2 = two_opt_star(truck1["order"], truck2["order"])

        # Feasibility checks (you already have these)
        if (
            func.check_time_route(r1, order_data_w, time_matrix)
            and func.check_time_route(r2, order_data_w, time_matrix)
            and func.check_capacity(r1, order_data_w, truck1["weight"])
            and func.check_capacity(r2, order_data_w, truck2["weight"])
        ):
            truck1["order"] = r1
            truck1["capacity"] = func.rebuild_capacity(
                r1, order_data_w, truck1["weight"]
            )

            truck2["order"] = r2
            truck2["capacity"] = func.rebuild_capacity(
                r2, order_data_w, truck2["weight"]
            )
    return improved


def calculate_fitness_moga(individual, order_data_w, distance_matrix, time_matrix):
    # z1: Travel Distance
    z1_distance = func.calculate_total_distance(
        individual, distance_matrix
    )

    # z2: Truck Time Efficiency (Waiting Time)
    z2_wait_time, num_outsourced = func.calculate_wait_time_and_outsourcingscore(
        individual, order_data_w, time_matrix, desired_delivery_date
    )

    # z3: Economic Cost
    outsourcing_fee = func.calculate_outsourcing_fee(
        individual, order_data_w, distance_matrix, desired_delivery_date
    )
    z3_cost = outsourcing_fee + (num_outsourced ** 3)

    # MOGA fitness vector
    fitness = (z1_distance, z2_wait_time, z3_cost)

    return fitness, individual

from functools import partial
def rank_solutions(population, order_data_w, distance_matrix, time_matrix):
    partial_fitness = partial(calculate_fitness_moga,
                          order_data_w=order_data_w,
                          distance_matrix=distance_matrix,
                          time_matrix=time_matrix)
    with ThreadPoolExecutor() as executor:
        fitness_results = list(executor.map(partial_fitness, population))

    # fitness_results is already [(fitness_tuple, individual), ...]
    return sorted(fitness_results, key=lambda x: x[0][0])

def dominates(f1, f2):
    return all(a <= b for a, b in zip(f1, f2)) and any(a < b for a, b in zip(f1, f2))

def fast_non_dominated_sort(fitness_results):
    fronts = [[]]
    domination_count = {}
    dominated_solutions = {}

    for i, (fit_i, ind_i) in enumerate(fitness_results):
        domination_count[i] = 0
        dominated_solutions[i] = []

        for j, (fit_j, _) in enumerate(fitness_results):
            if i == j:
                continue
            if dominates(fit_i, fit_j):
                dominated_solutions[i].append(j)
            elif dominates(fit_j, fit_i):
                domination_count[i] += 1

        if domination_count[i] == 0:
            fronts[0].append(i)

    current_front = 0
    while fronts[current_front]:
        next_front = []
        for i in fronts[current_front]:
            for j in dominated_solutions[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)
        current_front += 1
        fronts.append(next_front)

    return fronts[:-1]

def crowding_distance(front, fitness_results):
    distance = {i: 0 for i in front}
    num_objectives = len(fitness_results[0][0])

    for m in range(num_objectives):
        front.sort(key=lambda i: fitness_results[i][0][m])
        distance[front[0]] = distance[front[-1]] = float("inf")

        min_val = fitness_results[front[0]][0][m]
        max_val = fitness_results[front[-1]][0][m]
        if max_val == min_val:
            continue

        for k in range(1, len(front) - 1):
            prev_val = fitness_results[front[k - 1]][0][m]
            next_val = fitness_results[front[k + 1]][0][m]
            distance[front[k]] += (next_val - prev_val) / (max_val - min_val)

    return distance

def selection_nsga2(fitness_results, population_size):
    fronts = fast_non_dominated_sort(fitness_results)
    selected = []

    for front in fronts:
        if len(selected) + len(front) <= population_size:
            selected.extend(front)
        else:
            distances = crowding_distance(front, fitness_results)
            sorted_front = sorted(front, key=lambda i: distances[i], reverse=True)
            selected.extend(sorted_front[:population_size - len(selected)])
            break

    return [fitness_results[i][1] for i in selected]

def get_pareto_front(fitness_results):
    pareto = []
    for i, (fit_i, ind_i) in enumerate(fitness_results):
        dominated = False
        for j, (fit_j, _) in enumerate(fitness_results):
            if i != j and dominates(fit_j, fit_i):
                dominated = True
                break
        if not dominated:
            pareto.append((fit_i, ind_i))
    return pareto


def next_generation(
    config, current_gen, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix
):
    ranked_solutions = rank_solutions(
        current_gen, order_data_w, distance_matrix, time_matrix
    )

    current_best_fitness = ranked_solutions[0][0]
    print(f"Current gen best fitness score: {current_best_fitness}")

    # NSGA-II selection
    selection_results = selection_nsga2(ranked_solutions, elite_size)

    # Keep elite copies
    children = copy.deepcopy(selection_results)

    def mutate_and_ls(individual):
        mutated = mutate(
            copy.deepcopy(individual), order_data_w, mutation_rate, time_matrix
        )
        return local_search(mutated, order_data_w, time_matrix)

    # Parallel mutation + local search
    with ThreadPoolExecutor() as executor:
        improved_parents = list(executor.map(mutate_and_ls, selection_results))

    children.extend(improved_parents)

    # Crossover if population is still short
    while len(children) < len(current_gen):
        parent1, parent2 = random.sample(improved_parents, 2)
        child = crossover(parent1, parent2, order_data_w)
        children.append(assign_to_truck(child, order_data_w, time_matrix))
    return children



def genetic_algorithm(
    config,
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
        # === at the end of each generation, AFTER you have population ===
        log_generation_fitness(
            gen=gen,
            population=population,        # current generation’s population
            config=config,
            order_data_w=order_data_w,
            distance_matrix=distance_matrix,
            time_matrix=time_matrix,
            desired_delivery_date=desired_delivery_date  # or genetic_func.desired_delivery_date
        )

        population = next_generation(
            config,
            population,
            elite_size,
            mutation_rate,
            order_data_w,
            distance_matrix,
            time_matrix,
        )

    ranked = rank_solutions(population, order_data_w, distance_matrix, time_matrix)
    best_solution = ranked[0][1]

    # ⬇️ return best_solution AND final population
    return best_solution, population

def optimize_routes(
    config,
    order_data_w,
    distance_matrix,
    time_matrix,
    truck_weights,
    pop_size=1250,
    elite_size=125,
    mutation_rate=0.05,
    generations=50,
):
    global truck_num
    truck_num = len(Truck_weights)
    best_solution, final_population = genetic_algorithm(
        config,
        pop_size,
        generations,
        elite_size,
        mutation_rate,
        order_data_w,
        distance_matrix,
        time_matrix,
        truck_weights,
    )
    # pass both out
    return best_solution, final_population

def log_generation_fitness(gen,
                           population,
                           config,
                           order_data_w,
                           distance_matrix,
                           time_matrix,
                           desired_delivery_date):
    """
    Log the best fitness of the current generation to fitness_log.

    Parameters
    ----------
    gen : int
        Current generation index (0-based).
    population : iterable
        List (or other iterable) of solutions (same type as in final_population).
    config : dict
        The config dict passed from main.py. Must contain 'fitness_log'.
    order_data_w : list
        Order list with weights (your `new_order`).
    distance_matrix : 2D list/array
        Distance matrix used by the GA.
    time_matrix : 2D list/array
        Time matrix used by the GA.
    desired_delivery_date : list
        Your `genetic_func.desired_delivery_date`.
    """

    log_path = config["fitness_log"]

    if not population:
        # nothing to log
        return

    best_sol = None
    best_z1 = None
    best_z2 = None
    best_z3 = None
    best_score = None

    for sol in population:
        # === compute objectives for this solution ===
        z1 = func.calculate_total_distance(sol, distance_matrix)
        z2, _ = func.calculate_wait_time_and_outsourcingscore(
            sol,
            order_data_w,
            time_matrix,
            desired_delivery_date
        )
        z3 = func.calculate_outsourcing_fee(
            sol,
            order_data_w,
            distance_matrix,
            desired_delivery_date
        )

        # === scoring rule for "best" of this generation ===
        # Here we minimise the sum z1 + z2 + z3.
        score = z1 + z2 + z3

        if (best_score is None) or (score < best_score):
            best_score = score
            best_z1 = z1
            best_z2 = z2
            best_z3 = z3
            best_sol = sol

    # Append best of this generation to the log file
    with open(log_path, "a") as f:
        f.write(f"{gen},{best_z1},{best_z2},{best_z3}\n")
# print(new_order)
# best_fee_list = []
# sumtime=0
# mut_rate = 0.00
# score_list = []
# for _ in range(5):
#     genetic_func.fitness_cache = {}
#     for _ in range(5):
# start_time = time.time()
# best_solution = optimize_routes(
#     new_order, distance_m, time_m, Truck_weights, generations=30
# )
# best_out_sourcing_fee = func.calculate_outsourcing_fee(
#     best_solution, new_order, distance_m, desired_delivery_date
# )
# print("Best solution: ", best_solution)
# for date in desired_delivery_date:
#     print(date)
#     for key in best_solution[date].keys():
#         if key == "Outsourcing":
#             print(f"Outsourcing: {best_solution[date]['Outsourcing']}")
#         else:
#             print(f"{key}: Weight {best_solution[date][key]['capacity']}")
#             print(f"Order {best_solution[date][key]['order']}")
#             hour, minute = func.out_put_time_show(
#                 best_solution[date][key]["order"], new_order, time_m
#             )
#             print(f"Time end: {hour}:{minute}")
# print("best out fee: ", best_out_sourcing_fee)
# print(f"Time taken {time.time()-start_time}")

# to_map = func.to_truck_routes(best_solution, new_order, desired_delivery_date)
# osm.create_map_tree(warehouse_location, to_map, osm.colors)

# excel_input = func.output_as_excel(
#     best_solution, new_order, time_m, desired_delivery_date
# )
# func.Excel_writer(excel_input)

# print(f"Time taken {time.time()-start_time}")

