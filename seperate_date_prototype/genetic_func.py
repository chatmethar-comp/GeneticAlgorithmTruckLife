import func
import random
import time
import copy
import osm

start_time = time.time()
warehouse_location = [13.7438, 100.5626]
Truck_weights = [1900, 1900, 1900, 1100]
Truck_Driver_Working_Hour = 12
filepath_order = 'order.csv'
filepath_product = 'product.csv'
ex_data = func.read_csv_to_list(filepath_order)
product_list = func.read_csv_to_list(filepath_product)
new_order = func.product_to_weight(ex_data,product_list)
distance_m = func.create_distance_matrix(warehouse_location, new_order)
time_m = func.create_time_matrix(warehouse_location, new_order)

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

def crossover(individual1,individual2,order_data_w):
    individual1_c = copy.deepcopy(individual1)
    individual2_c = copy.deepcopy(individual2)
    amount_of_order = len(order_data_w)
    for i in range(random.randint(1,int(amount_of_order/2))):
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

def assign_to_truck(individual,truck_weights,order_data_w,work_time,time_matrix):
    individual_c = copy.deepcopy(individual)
    for i in range(1):
        for i in range(len(individual_c)):
            # print(f"date{i}")
            truck_load = 0
            truck_work_time = 0
            try:
                item_sw = random.choice(individual_c[i][-1])
                # print(f"Order {item_sw}")
                truck_to_assign = random.randint(1,len(individual_c[i])-2)
                truck_to_assign_weight_capacity = truck_weights[truck_to_assign-1]
                start_place = 0
                for order in individual_c[i][truck_to_assign]:
                    truck_load += order_data_w[order-1][-1]
                    truck_work_time += time_matrix[start_place][order-1]
                    start_place = order-1
                # print(f"Truck{truck_to_assign} load now: {truck_load}")
                # print(f"Order detail {order_data_w[item_sw-1]}")
                # print(f"product weight {order_data_w[item_sw-1][-1]}")
                if (truck_load+order_data_w[item_sw-1][-1]<=truck_to_assign_weight_capacity)&(truck_work_time<=work_time):
                    individual_c[i][truck_to_assign].append(item_sw)
                    individual_c[i][-1].remove(item_sw)
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

def mutate(individual,truck_weights,order_data_w,mutation_rate,work_time,time_matrix):
    mutated_solution = copy.deepcopy(individual)
    for date in mutated_solution:
        if len(date)>3: #check if there are more than 1 truck
            truck_to_assign_load = 0
            truck_work_time = 0
            start_place = 0
            if random.random() < mutation_rate:
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
                    last_order = 0
                    for order in date[truck_to_assign]:
                        truck_to_assign_load += order_data_w[order-1][-1]
                        truck_work_time += time_matrix[start_place][order]
                        start_place = order
                        last_order = order
                    truck_work_time += time_matrix[last_order][0]
                    if (truck_to_assign_load+order_data_w[item_from_truck_source-1][-1]<=truck_to_assign_weight_capacity)&(truck_work_time<=work_time):
                        date[truck_to_assign].append(item_from_truck_source)
                        date[source_truck].remove(item_from_truck_source)
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
                for truck in range(1,len(date)-1):
                    random.shuffle(date[truck])
        else:
            if random.random()<mutation_rate:
                for truck in range(1,len(date)-1):
                    date[truck].shuffle
    # try:
    #     validate_individual(mutated_solution,order_data_w)
    # except ValueError:
    #     print("error due to mutate")
    #     raise ValueError(f"Missing orders")
    return mutated_solution

def calculate_fitness_score(individual,order_data_w,distance_matrix,time_matrix):
    out_source_fee = func.calculate_outsourcing_fee(individual,order_data_w,distance_matrix)
    fitness_score = out_source_fee+((func.cal_route_time(time_matrix,individual))/1000)
    return fitness_score

def rank_solutions(population,order_data_w,distance_matrix,time_matrix):
    fitness_results = [(calculate_fitness_score(individual,order_data_w,distance_matrix,time_matrix), individual) for individual in population]
    fitness_results.sort(key=lambda x: x[0])
    return fitness_results

def selection(fitness_results, elite_size):
    best_individuals = [fitness_results[i][1] for i in range(elite_size)]
    return best_individuals


def next_generation(current_gen, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix, work_time, truck_weights):
    ranked_solutions = rank_solutions(current_gen, order_data_w, distance_matrix,time_matrix)
    current_best_fitness = ranked_solutions[0][0]  # Lowest outsourcing fee in this generation
    
    print(f"Current gen best fitness score: {current_best_fitness}")
    
    selection_results = selection(ranked_solutions, elite_size)
    children = copy.deepcopy(selection_results)
    while len(children) < len(current_gen):
        parent1, parent2 = random.sample(selection_results, 2)
        child = crossover(parent1, parent2, order_data_w)
        child = mutate(child, truck_weights, order_data_w, mutation_rate, work_time, time_matrix)
        children.append(assign_to_truck(child, truck_weights, order_data_w, work_time, time_matrix))
    
    return children  


def genetic_algorithm(pop_size, generations, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix, work_time, truck_weights):
    population = initialize_population(pop_size, order_data_w, truck_weights)
    
    for gen in range(generations):
        print(f"Generation {gen}")
        population = next_generation(population, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix, work_time, truck_weights)
    
    best_solution = rank_solutions(population, order_data_w, distance_matrix, time_matrix)[0][1]
    return best_solution



def optimize_routes(order_data_w, distance_matrix, time_matrix, work_time, truck_weights, pop_size=1000, elite_size=200, mutation_rate=0.05, generations=60):
    best_solution = genetic_algorithm(pop_size, generations, elite_size, mutation_rate, order_data_w, distance_matrix, time_matrix, work_time, truck_weights)
    return best_solution

if __name__ == "__main__":
    best_solution = optimize_routes(new_order,distance_m, time_m, Truck_Driver_Working_Hour, Truck_weights)
    best_out_sourcing_fee = func.calculate_outsourcing_fee(best_solution,new_order, distance_m)
    print("Best solution: ", best_solution)
    for date in best_solution:
        print(date)
        for i in range(1,len(date)-1):
            truck_load = 0
            truck_work_time = 0
            start_place = 0
            for order in date[i]:
                truck_load += new_order[order-1][-1]
                truck_work_time += time_m[start_place][order]
                start_place = order
            print(f"Truck{i} load:{truck_load}, work time:{truck_work_time}")

    print("best out fee: ",best_out_sourcing_fee)
    print(f"Time taken {time.time()-start_time}")
    to_map = func.to_map_input(best_solution,new_order)
    osm.create_map_tree(warehouse_location,to_map,osm.colors)
    # d = osm.create_map_with_day_truck_routes(warehouse_location,to_map,osm.colors)
    # d.save('map.html')


    # x = gen_individual(new_order,Truck_weights)
    # print(func.cal_route_time(time_m,x,Truck_weights))
