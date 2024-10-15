import func
import osm
import genetic_func
import time
# import numpy as np

'''
To Do!
Implement caching  of fitness score 
Test result and plot it on graph maybe using matplotlib
Make the truck can retrieve more item from warehouse if time is appropriate

'''

warehouse_location = [13.7438, 100.5626]
Truck_weights = [1900, 1900, 1900, 1100]
fitness_cache = {}
filepath_order = 'order.csv'
filepath_product = 'product.csv'
ex_data = func.read_csv_to_list(filepath_order)
product_list = func.read_csv_to_list(filepath_product)
new_order = func.product_to_weight(ex_data,product_list)
distance_m = func.create_distance_matrix(warehouse_location, new_order)
time_m = func.create_time_matrix(warehouse_location, new_order)

# print(new_order)
# best_fee_list = []
# sumtime=0
# for i in range(10):
start_time = time.time()
best_solution = genetic_func.optimize_routes(new_order,distance_m, time_m, Truck_weights)
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
        truck_work_time += time_m[start_place][0]
        print(f"Truck{i} load:{truck_load}, work time:{truck_work_time}")
print("best out fee: ",best_out_sourcing_fee)
print(f"Time taken {time.time()-start_time}")
# sumtime+=time.time()-start_time
# to_map = func.to_map_input(best_solution,new_order)
# osm.create_map_tree(warehouse_location,to_map,osm.colors)
# excel_input = func.output_as_excel(best_solution, new_order, time_m)
# func.Excel_writer(excel_input)
#     best_fee_list.append(best_out_sourcing_fee)
# print(f"10 result: {best_fee_list}")
# print(sumtime)
# x = gen_individual(new_order,Truck_weights)
# print(func.cal_route_time(time_m,x,Truck_weights))