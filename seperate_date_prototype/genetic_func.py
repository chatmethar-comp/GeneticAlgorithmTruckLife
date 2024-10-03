import func
import random

Truck_weights = [1900, 1900, 1900, 1000]
Truck_Driver_Working_Hour = 12
ex_data=[[1.0, 20240204, 14.02644447, 100.6919272, 20240209, 20240212, 4.0], 
         [2.0, 20240201, 13.96554796, 100.5245274, 20240204, 20240208, 1.0], 
         [3.0, 20240205, 14.1010167, 100.5554815, 20240210, 20240211, 3.0], 
         [4.0, 20240205, 14.02366024, 100.7877536, 20240209, 20240212, 8.0], 
         [5.0, 20240206, 13.79198072, 100.2948867, 20240211, 20240212, 2.0]]

def gen_individual(order_data,truck_weights):
    #gen structure
    individual = []
    desired_delivery_date = []
    for order in order_data:
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
    shuffle_order_data = order_data[:]
    random.shuffle(shuffle_order_data)
    for data in shuffle_order_data:
        random.shuffle(individual)
        for i in range(len(individual)):
            if data[4] <= individual[i][0] <= data[5]:
                individual[i][len(truck_weights)+1].append(data[0])
                break
    individual.sort(key=lambda individual :individual[0])
    return individual


def initialize_population(pop_size,order_data,truck_weights):
    population = []
    while len(population) < pop_size:
        population.append(gen_individual(order_data,truck_weights))

    return population


x = initialize_population(1000,ex_data,Truck_weights)
print(x)

# print(ex_data)