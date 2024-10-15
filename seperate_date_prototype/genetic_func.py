import func
import random
import time
import copy
import osm

def validate_individual(individual, order_data_w):
    all_order_ids = {order[0] for order in order_data_w}  # Set of all order IDs
    assigned_orders = set()

    # Go through the trucks and outsourcing lists in each day
    for day in individual:
        for truck in day[1:-1]:  # Skip the date and outsourcing list
            assigned_orders.update(truck)
        assigned_orders.update(day[-1])  # Update from outsourcing list
    
    missing_orders = all_order_ids - assigned_orders
    extra_orders = assigned_orders - all_order_ids

    if missing_orders:
        raise ValueError(f"Missing orders: {missing_orders}")
    if extra_orders:
        raise ValueError(f"Extra orders found: {extra_orders}")
    
    # If all orders are accounted for
    return True


def gen_individual(order_data_w,truck_weights):
    #gen structure
    individual = []
    desired_delivery_date = []
    for order in order_data_w:
        start_date = order[4]
        end_date = order[5]   
        delivery_dates = list(range(start_date, end_date + 1))  # Include end date
        for date in delivery_dates:
            desired_delivery_date.append(date)
    desired_delivery_date = list(dict.fromkeys(desired_delivery_date))
    desired_delivery_date.sort()
    for date in desired_delivery_date:
        individual.append([date])
    for i in range(len(individual)):
        for _ in truck_weights:
            individual[i].append([])
        individual[i].append([]) #append outsorcing list of the day

    #start randomly assign data into outsourcing box
    shuffle_order_data_w = copy.deepcopy(order_data_w)
    random.shuffle(shuffle_order_data_w)
    for data in shuffle_order_data_w:
        random.shuffle(individual)
        for i in range(len(individual)):
            if data[4] <= individual[i][0] <= data[5]:
                individual[i][len(truck_weights)+1].append(data[0])
                break
    individual.sort(key=lambda individual :individual[0])

    try:
        validate_individual(individual,order_data_w)
    except ValueError:
        print("error due to gen_individual")
        raise ValueError(f"Missing orders")
    return individual


def initialize_population(pop_size,order_data_w,truck_weights):
    population = []
    while len(population) < pop_size:
        population.append(gen_individual(order_data_w,truck_weights))
    return population

# def crossover(individual1,individual2,order_data_w,time_matrix,truck_weights,work_time):
#     individual1_c = copy.deepcopy(individual1)
#     individual2_c = copy.deepcopy(individual2)
#     amount_of_order = len(order_data_w)
#     for i in range(random.randint(1,int(amount_of_order/2))): #random amount of time to crossover
#         date_cross=random.randint(0,len(individual1_c)-1)
#         try:
#             item_sw = random.choice(individual1_c[date_cross][-1]) #randomly choose item in outsource truck of random date
#             start_date = order_data_w[item_sw-1][4] #date that item_sw can be deliver
#             end_date = order_data_w[item_sw-1][5]
#             delivery_dates = list(range(start_date, end_date + 1))
#             random.shuffle(individual2_c) 
#             for date in individual2_c: #loop for each date in individual randomly
#                 if set([date[0]]).issubset(delivery_dates): #if that date is in deliverable date
#                     truck_to_assign = random.randint(1,len(individual1_c[0])+1) #randomly choose truck index
#                     for i in range(len(truck_weights)+1):
#                         while truck_to_assign==0:
#                             truck_to_assign+=1
#                         truck_to_assign_weight_capacity = truck_weights[truck_to_assign-1]
#                         truck_work_time,truck_load = func.cal_truck_time_load(date[truck_to_assign],time_matrix,order_data_w)
#                         if truck_to_assign<=len(truck_weights):
#                             if (truck_load+order_data_w[item_sw-1][-1]<=truck_to_assign_weight_capacity) and truck_work_time<=work_time:
#                                 if func.check_time_add_item(item_sw, date[truck_to_assign], order_data_w,time_matrix):
#                                     date[truck_to_assign].append(item_sw)
#                                     break
#                         else:
#                             date[truck_to_assign].append(item_sw)
#                             break
#                         truck_to_assign = (truck_to_assign+1)%(len(truck_weights)+2)
#                     for truck in date[1:]:
#                         try:
#                             truck.remove(item_sw)
#                             break
#                         except ValueError:
#                             continue
#                 else:
#                     continue
#         except IndexError:
#             continue
#     individual2_c.sort(key=lambda individual :individual[0])
#     # try:
#     #     validate_individual(individual2_c,order_data_w)
#     # except ValueError:
#     #     print("error due to crossover")
#     #     raise ValueError(f"Missing orders")
#     return individual2_c


def crossover(individual1,individual2,order_data_w):
    individual1_c = copy.deepcopy(individual1)
    individual2_c = copy.deepcopy(individual2)
    amount_of_order = len(order_data_w)
    for i in range(random.randint(int(amount_of_order/4),int(amount_of_order/2))):
        date_cross=random.randint(0,len(individual1_c)-1)
        try:
            item_sw = random.choice(individual1_c[date_cross][-1])
            for i in range(len(individual2_c)):
                for j in range(1,len(individual2_c[i])):
                    try:
                        individual2_c[i][j].remove(item_sw)
                        individual2_c[date_cross][-1].append(item_sw)
                        break
                    except ValueError:
                        continue
        except IndexError: 
            continue
    # try:
    #     validate_individual(individual2_c,order_data_w)
    # except ValueError:
    #     print("error due to crossover")
    #     raise ValueError(f"Missing orders")
    return individual2_c

def assign_to_truck(individual,truck_weights,order_data_w,time_matrix):
    individual_c = copy.deepcopy(individual)
    for i in range(4):
        for date in individual_c:
            # print(f"date{i}")
            truck_load = 0
            try:
                item_sw = random.choice(date[-1])
                # print(f"Order {item_sw}")
                truck_to_assign = random.randint(1,len(date)-2)
                truck_to_assign_weight_capacity = truck_weights[truck_to_assign-1]
                for order in date[truck_to_assign]:
                    truck_load += order_data_w[order-1][-1]
                # print(f"Truck{truck_to_assign} load now: {truck_load}")
                # print(f"Order detail {order_data_w[item_sw-1]}")
                # print(f"product weight {order_data_w[item_sw-1][-1]}")
                if (truck_load+order_data_w[item_sw-1][-1]<=truck_to_assign_weight_capacity):
                    if func.check_time_add_item(item_sw, date[truck_to_assign], order_data_w,time_matrix):
                        date[truck_to_assign].append(item_sw)
                        date[-1].remove(item_sw)
                    else:
                        continue
                else:
                    continue
            except IndexError:
                continue
    # try:
    #     validate_individual(individual_c,order_data_w)
    # except ValueError:
    #     print("error due to assign to truck")
    #     raise ValueError(f"Missing orders")
    return individual_c

def mutate(individual,truck_weights,order_data_w,mutation_rate,time_matrix):
    mutated_solution = copy.deepcopy(individual)
    for date in mutated_solution:
        if random.random() < mutation_rate:
            for order in date[-1]:
                if order:
                    start_date = order_data_w[order-1][4]
                    end_date = order_data_w[order-1][5]
                    delivery_dates = list(range(start_date, end_date + 1))
                    random_date = random.choice(delivery_dates)
                    date[-1].remove(order)
                    for date_in in mutated_solution:
                        if date_in[0] == random_date:
                            date_in[-1].append(order)
            if len(date)>3: #check if there are more than 1 truck
                truck_to_assign_load = 0
                if random.random()<=0.6:
                    source_truck = random.randint(1,len(date)-2)
                    try:
                        item_from_truck_source = random.choice(date[source_truck])
                    except IndexError:
                        break
                    truck_to_assign = random.randint(1,len(date)-2)
                    while truck_to_assign==source_truck:
                        truck_to_assign = random.randint(1,len(date)-2)
                    truck_to_assign_weight_capacity = truck_weights[truck_to_assign-1]
                    for order in date[truck_to_assign]:
                        truck_to_assign_load += order_data_w[order-1][-1]
                    if (truck_to_assign_load+order_data_w[item_from_truck_source-1][-1]<=truck_to_assign_weight_capacity):
                        if func.check_time_add_item(item_from_truck_source, date[truck_to_assign], order_data_w,time_matrix):
                            date[truck_to_assign].append(item_from_truck_source)
                            date[source_truck].remove(item_from_truck_source)
                        else:
                            continue
                    else:
                        continue
                random_truck = random.randint(1,len(date)-2)
                try:
                    random_item = random.choice(date[random_truck])
                except IndexError:
                    break
                # print(f"Truck {random_truck} Item {random_item}")
                date[-1].append(random_item)
                date[random_truck].remove(random_item)
                # for optimize route not work when time is fixed
                # for truck in range(1,len(date)-1):
                #     random.shuffle(date[truck])
            else:
                # for optimize route not work when time is fixed
                # if random.random()<mutation_rate:
                #     for truck in range(1,len(date)-1):
                #         date[truck].shuffle
                break
    # test sent random outsourcing item to other suitable date outsourcing list seem to not have any effect
    # if random.random() < mutation_rate:
    #     try:
    #         random_date = random.choice(mutated_solution)
    #         item_sw = random.choice(random_date[-1])#randomly choose item in outsource truck of random date
    #         random_date = random_date[0] 
    #         start_date = order_data_w[item_sw-1][4] #date that item_sw can be deliver
    #         end_date = order_data_w[item_sw-1][5]
    #         delivery_dates = list(range(start_date, end_date + 1))
    #         lucky_date = random.choice(delivery_dates)
    #         removed = False
    #         added = False
    #         for date in mutated_solution:
    #             if date == random_date:
    #                 date[random_date].remove(item_sw)
    #                 removed = True
    #             if date[0] == lucky_date:
    #                 date[-1].append(item_sw)
    #                 added = True
    #             if removed and added:
    #                 break
    #     except IndexError:
    #         pass
    # try:
    #     validate_individual(mutated_solution,order_data_w)
    # except ValueError:
    #     print("error due to mutate")
    #     raise ValueError(f"Missing orders")
    return mutated_solution


def calculate_fitness_score(individual,order_data_w,distance_matrix,time_matrix):
    out_source_fee = func.calculate_outsourcing_fee(individual,order_data_w,distance_matrix)
    wait_time,outsource_score = func.calculate_wait_time_and_outsourcingscore(individual,order_data_w,time_matrix)
    fitness_score = out_source_fee+wait_time+outsource_score
    return fitness_score

fitness_cache = {}
def evaluate_fitness(individual, order_data_w, distance_matrix, time_matrix):
    # Helper function to convert individual into a hashable tuple
    def make_hashable(item):
        if isinstance(item, (list, tuple)):
            return tuple(make_hashable(subitem) for subitem in item)  # Recursively convert each subitem to a tuple
        return item  # Return the item itself if it's not a list or tuple (e.g., int)

    # Convert individual to a hashable tuple
    individual_tuple = make_hashable(individual)

    # Check if the individual's fitness is already cached
    if individual_tuple in fitness_cache:
        return fitness_cache[individual_tuple]

    # Compute the fitness using the existing function
    fitness_value = calculate_fitness_score(individual, order_data_w, distance_matrix, time_matrix)
    
    # Cache the computed fitness
    fitness_cache[individual_tuple] = fitness_value

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


def next_generation(current_gen, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix, truck_weights):
    ranked_solutions = rank_solutions(current_gen, order_data_w, distance_matrix, time_matrix)
    current_best_fitness = ranked_solutions[0][0]  # Lowest outsourcing fee in this generation
    
    print(f"Current gen best fitness score: {current_best_fitness}")
    
    selection_results = selection(ranked_solutions, elite_size)
    children = copy.deepcopy(selection_results)
    while len(children) < len(current_gen):
        parent1, parent2 = random.sample(selection_results, 2)
        parent1 = mutate(parent1, truck_weights, order_data_w, mutation_rate, time_matrix)
        parent2 = mutate(parent2, truck_weights, order_data_w, mutation_rate, time_matrix)
        # child = crossover(parent1, parent2, order_data_w,time_matrix,truck_weights,work_time)
        child = crossover(parent1, parent2, order_data_w)
        # child = mutate(child, truck_weights, order_data_w, mutation_rate, work_time, time_matrix)
        children.append(assign_to_truck(child, truck_weights, order_data_w, time_matrix))
    
    return children  


def genetic_algorithm(pop_size, generations, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix, truck_weights):
    population = [gen_individual(order_data_w, truck_weights) for _ in range(pop_size)]
    
    for gen in range(generations):
        print(f"Gen {gen}")
        population = next_generation(population, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix, truck_weights)

    best_solution = rank_solutions(population, order_data_w, distance_matrix, time_matrix)[0][1]
    return best_solution

def optimize_routes(order_data_w, distance_matrix, time_matrix, truck_weights, pop_size=1250, elite_size=200, mutation_rate=0.4, generations=70):
    best_solution = genetic_algorithm(pop_size, generations, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix, truck_weights)
    return best_solution

