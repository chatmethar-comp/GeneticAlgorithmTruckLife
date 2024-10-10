import csv
import numpy as np
import time
import osm
import copy

filepath_outsourcing = 'outsourcing.csv'

start_time = time.time()

def read_csv_to_list(file_path):
    data_list = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader)
        for row in csv_reader:
            float_row = []
            for value in row:
                if len(value) == 10 and value[4] == '/' and value[7] == '/':
                    year, month, day = value.split('/')
                    date_int = int(year + month + day)  # Combine and convert to int   
                    float_row.append(date_int) 
                # elif len(value) == 5 and value[2] == ':':
                #     hour, minute = value.split(':')
                #     time = int(hour+minute)
                #     float_row.append(time)                 
                else:
                    try:
                        float_row.append(int(value))  # Convert to int if it's not a date
                    except ValueError:
                        try:
                            float_row.append(float(value)) 
                        except ValueError:
                            float_row.append(value) 
            data_list.append(float_row)
    return data_list

def product_to_weight(order_data,product_list):
    for order in order_data:
        for i in range(len(product_list)):
            if order[-1] == product_list[i][0]:
                order[-1] = product_list[i][2]
    return order_data

def create_distance_matrix(warehouse_location,order_data_w):
    distance_matrix = osm.get_osrm_distance_matrix(warehouse_location,order_data_w, mode='driving')
    return distance_matrix

def create_time_matrix(warehouse_location,order_data_w):
    time_matrix = osm.get_osrm_travel_time_matrix(warehouse_location,order_data_w, mode='driving')
    return time_matrix

def calculate_distance(distance_matrix,start_orderID,destination_orderID):
    distance = distance_matrix[start_orderID][destination_orderID]
    return distance

def calculate_time(time_matrix,start_orderID,destination_orderID):
    time = time_matrix[start_orderID][destination_orderID]
    return time

def cal_route_time(time_matrix,individual):
    sum_time = 0
    for date in individual:
        start_place = 0
        for truck in range(1,len(date)-1):
            for coord in date[truck]:
                time = time_matrix[start_place][coord]
                sum_time+=time
                start_place=coord
            sum_time+=time_matrix[start_place][0]
    return sum_time

def cal_truck_time_load(truck,time_matrix,order_data_w):
    truck_work_time = 0
    start_place = 0
    truck_load = 0
    for order in truck:
        truck_load += order_data_w[order-1][-1]
        truck_work_time += time_matrix[start_place][order]
        start_place = order
    truck_work_time += time_matrix[start_place][0]
    return truck_work_time,truck_load
                    

def calculate_outsourcing_fee(individual,order_data_w,distance_matrix):
    outsorce_fee = 0;
    for i in range(len(individual)):
        for j in range(len(individual[i][len(individual[0])-1])):
            outsourcce_item = individual[i][len(individual[0])-1][j]
            dis = calculate_distance(distance_matrix,0,outsourcce_item)
            if order_data_w[outsourcce_item-1][-1] < 500:
                if dis < 10:
                    outsorce_fee+=1000
                elif dis < 20:
                    outsorce_fee+=1100
                elif dis < 30:
                    outsorce_fee+=1200
                elif dis < 40:
                    outsorce_fee+=1300
                else:
                    outsorce_fee+=1400
            elif order_data_w[outsourcce_item-1][-1] < 1000:
                if dis < 10:
                    outsorce_fee+=1200
                elif dis < 20:
                    outsorce_fee+=1400
                elif dis < 30:
                    outsorce_fee+=1600
                elif dis < 40:
                    outsorce_fee+=1800
                else:
                    outsorce_fee+=2000
            elif order_data_w[outsourcce_item-1][-1] < 1500:
                if dis < 10:
                    outsorce_fee+=1400
                elif dis < 20:
                    outsorce_fee+=1700
                elif dis < 30:
                    outsorce_fee+=2000
                elif dis < 40:
                    outsorce_fee+=2300
                else:
                    outsorce_fee+=2600
    return outsorce_fee

def to_map_input(route_data, order_data):
    """
    Transforms route and order data into the input format expected by the create_map_with_day_truck_routes function.
    
    :param route_data: List of routes containing day and truck assignment information.
    :param order_data: List of order data with lat/lon and delivery dates.
    :return: Dictionary where keys are days and values are lists of truck routes (each list contains truck coordinate routes).
    """
    # Create a dictionary to hold the routes by day
    daily_truck_routes = {}

    # Convert the route data into a dictionary with day as the key
    for day_entry in route_data:
        day = day_entry[0]
        daily_truck_routes[day] = [[] for _ in range(len(day_entry[1:]))]  # Initialize empty lists for each truck

        # Go through each truck's assigned orders
        for truck_idx, order_indices in enumerate(day_entry[1:]):
            truck_coords = []
            
            # Collect lat/lon data for each order assigned to the truck
            for order_idx in order_indices:
                for order in order_data:
                    if order[0] == order_idx:
                        lat, lon = order[2], order[3]
                        truck_coords.append((lat, lon))
                        break  # Stop after finding the order

            # Assign the collected coordinates to the truck's route for the day
            daily_truck_routes[day][truck_idx] = truck_coords

    return daily_truck_routes

def correct_time(hour,minute):
    hour_c = copy.deepcopy(hour)
    minute_c = copy.deepcopy(minute)
    while minute_c>=60:
        minute_c-=60
        hour_c+=1
    return(hour_c,minute_c)

def delivered_time(order, order_data_w):
    time = order_data_w[order-1][-2]
    hour, minute = time.split(':')
    hour = int(hour)
    minute = int(minute)
    time = correct_time(hour,minute)
    return time

def check_time_add_item(neworder,truck, order_data_w,time_matrix):
    hour_t = 7
    minute_t = 0
    start_place = 0
    for order in truck:
        hour_dt,minute_dt = delivered_time(order,order_data_w)
        hour_t,minute_t = correct_time(hour_t,minute_t+(calculate_time(time_matrix,start_place,order)*60))
        if hour_t<hour_dt:
            hour_t,minute_t = hour_dt,minute_dt
        elif hour_t==hour_dt and minute_t<=minute_dt:
            hour_t,minute_t = hour_dt,minute_dt
        else:
            print(f"how tf did we end up here Truck_time{hour_t}:{minute_t} Delivery time {hour_dt}:{minute_dt}")
        start_place = order
    hour_dt,minute_dt = delivered_time(neworder,order_data_w)
    hour_t,minute_t = correct_time(hour_t,minute_t+(calculate_time(time_matrix,start_place,neworder)*60))
    if hour_t<hour_dt:
        # print("successful")
        return True
    elif hour_t==hour_dt and minute_t<=minute_dt:
        # print("successful")
        return True
    else:
        # print(f"Ahhh Truck_time{hour_t}:{minute_t} Delivery time {hour_dt}:{minute_dt}")
        return False
                


# outsourcing = read_csv_to_list(filepath_outsourcing)
# print(outsourcing)
# print(f"time taken {start_time - time.time()}")