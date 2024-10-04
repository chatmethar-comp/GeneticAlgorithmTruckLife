import func
import random
import csv

warehouse_location = [13.7438, 100.5626]
Truck_weights = [1900, 1900, 1900, 1000]
Truck_Driver_Working_Hour = 12
filepath_order = 'order.csv'
filepath_product = 'product.csv'
ex_data = func.read_csv_to_list(filepath_order)
product_list = func.read_csv_to_list(filepath_product)
new_order = func.product_to_weight(ex_data,product_list)

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
    shuffle_order_data_w = order_data_w[:]
    random.shuffle(shuffle_order_data_w)
    for data in shuffle_order_data_w:
        random.shuffle(individual)
        for i in range(len(individual)):
            if data[4] <= individual[i][0] <= data[5]:
                individual[i][len(truck_weights)+1].append(data[0])
                break
    individual.sort(key=lambda individual :individual[0])
    return individual


def initialize_population(pop_size,order_data_w,truck_weights):
    population = []
    while len(population) < pop_size:
        population.append(gen_individual(order_data_w,truck_weights))
    return population

def crossover(individual1,individual2,order_w):
    individual1_c = individual1.copy()
    individual2_c = individual2.copy()
    amount_of_order = len(order_w)
    for i in range(random.randint(1,int(amount_of_order/2))):
        date_cross=random.randint(0,len(individual1_c))
        try:
            item_sw = random.choice(individual1_c[date_cross][-1])
            individual2_c[date_cross][-1].append(item_sw)
            for i in range(len(individual2_c)):
                try:
                    individual2_c[i][-1].remove(item_sw)
                except ValueError:
                    continue
        except IndexError:
            continue
    return individual2_c

def assign_to_truck(individual,truck_weights,order_data_w):
    individual_c = individual.copy()
    for i in range(10):
        for i in range(len(individual_c)):
            # print(f"date{i}")
            truck_load = 0
            try:
                item_sw = random.choice(individual_c[i][-1])
                # print(f"Order {item_sw}")
                truck_to_assign = random.randint(1,len(individual_c[i])-2)
                truck_to_assign_weight_capacity = truck_weights[truck_to_assign-1]
                for order in individual_c[i][truck_to_assign]:
                    truck_load += order_data_w[order-1][-1]
                # print(f"Truck{truck_to_assign} load now: {truck_load}")
                # print(f"Order detail {order_data_w[item_sw-1]}")
                # print(f"product weight {order_data_w[item_sw-1][-1]}")
                if truck_load+order_data_w[item_sw-1][-1]<=truck_to_assign_weight_capacity:
                    individual_c[i][truck_to_assign].append(item_sw)
                    individual_c[i][-1].remove(item_sw)
                    # print("insert success")
                else:
                    # print("insert fail")
                    continue
            except IndexError:
                continue
    return individual_c

def mutate(individual,truck_weights,order_data_w,mutation_rate):
    mutated_solution = individual.copy()
    for date in mutated_solution:
        if len(date)>3: #check if there are more than 1 truck
            truck_to_assign_load = 0
            if random.random() < mutation_rate:
                if random.random()<=0.9:
                    source_truck = random.randint(1,len(date)-2)
                    item_from_truck_source = random.choice(date[source_truck])
                    truck_to_assign = random.randint(1,len(date)-2)
                    while truck_to_assign==source_truck:
                        truck_to_assign = random.randint(1,len(date)-2)
                    truck_to_assign_weight_capacity = truck_weights[truck_to_assign-1]
                    for order in date[truck_to_assign]:
                        truck_to_assign_load += order_data_w[order-1][-1]
                    if truck_to_assign_load+order_data_w[item_from_truck_source-1][-1]<=truck_to_assign_weight_capacity:
                        date[truck_to_assign].append(item_from_truck_source)
                        date[source_truck].remove(item_from_truck_source)
                    else:
                        continue
                if random.random()<=0.6:
                    print("ac2")
        else:
            break
    return 0

def fitness_score():

    return 0

def rank_solutions(population):
    fitness_results = [(func.calculate_outsourcing_fee(individual), individual) for individual in population]
    fitness_results.sort(key=lambda x: x[0])
    return fitness_results

# x = initialize_population(1,new_order,Truck_weights)
x = gen_individual(new_order,Truck_weights)
# print(f"Exdata: {ex_data}\n")
# print(f"Order with weight: {new_order}\n")
print(x)
print(f"New order: {new_order}")
dis_m = func.create_distance_matrix(warehouse_location,new_order)
y = func.calculate_outsourcing_fee(x,new_order,dis_m)
with open('distance_matrix.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(dis_m)

print(y)
