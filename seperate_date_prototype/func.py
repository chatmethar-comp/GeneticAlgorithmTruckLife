import csv
import numpy as np
import osm

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
                else:
                    try:
                        float_row.append(float(value))  # Convert to int if it's not a date
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

def create_weight_graph(coor_list):
    weight_graph = []
    for i in range(len(coor_list)):
        weight_graph.append([])
        for j in range(len(coor_list)):
            weight_graph[i].append(osm.get_travel_time(coor_list[i],coor_list[j]))
    return weight_graph

def calculate_distance_and_travel_time():
    distance = 0
    travel_time = 0
    return (distance,travel_time)
