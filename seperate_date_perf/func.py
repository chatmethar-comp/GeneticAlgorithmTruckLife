import csv
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


def fast_deepcopy(data):
    copied_data = {}
    for date, trucks in data.items():
        copied_trucks = {}
        
        # Handle outsourcing list separately
        outsourcing_list = trucks.get("Outsourcing", [])
        
        for truck, info in trucks.items():
            # Ensure we only process valid truck data
            if isinstance(info, dict) and "weight" in info and "order" in info:
                copied_trucks[truck] = {
                    "weight": info["weight"],  # Shallow copy of immutable data
                    "order": info["order"][:]  # Deep copy only the list
                }

        # Copy the outsourcing list
        copied_trucks["Outsourcing"] = outsourcing_list[:]  # Shallow copy of the list
        copied_data[date] = copied_trucks

    return copied_data

def make_hashable(item):
        if isinstance(item, (list, tuple)):
            return tuple(make_hashable(subitem) for subitem in item)  # Recursively convert each subitem to a tuple
        return item

def calculate_time(time_matrix,start_orderID,destination_orderID):
    time = time_matrix[start_orderID][destination_orderID]
    return time

def calculate_distance(distance_matrix,start_orderID,destination_orderID):
    distance = distance_matrix[start_orderID][destination_orderID]
    return distance

def correct_time(hour,minute):
    hour_c = hour
    minute_c = minute
    while minute_c>=60:
        minute_c-=60
        hour_c+=1
    while minute_c<0:
        minute_c+=60
        hour_c-=1
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
            minute_t = minute_dt
        else:
            print(f"how tf did we end up here Truck_time{hour_t}:{minute_t} Delivery time {hour_dt}:{minute_dt} adddd")
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

def check_time_insert_item(neworder,insertion_index,truck, order_data_w,time_matrix):
    hour_t = 7
    minute_t = 0
    start_place = 0
    for order in truck[:insertion_index]:
        hour_dt,minute_dt = delivered_time(order,order_data_w)
        hour_t,minute_t = correct_time(hour_t,minute_t+(calculate_time(time_matrix,start_place,order)*60))
        if hour_t<hour_dt:
            hour_t,minute_t = hour_dt,minute_dt
        elif hour_t==hour_dt and minute_t<=minute_dt:
            minute_t = minute_dt
        else:
            print(f"how tf did we end up here Truck_time{hour_t}:{minute_t} Delivery time {hour_dt}:{minute_dt} kkkk")
        start_place = order
    hour_dt,minute_dt = delivered_time(neworder,order_data_w)
    hour_t,minute_t = correct_time(hour_t,minute_t+(calculate_time(time_matrix,start_place,neworder)*60))
    if hour_t<hour_dt:
        hour_t,minute_t = hour_dt,minute_dt
        if insertion_index > len(truck):
            return True
        if len(truck) == 0:
            return True
        hour_dt,minute_dt = delivered_time(truck[insertion_index],order_data_w)
        hour_t,minute_t = correct_time(hour_t,minute_t+(calculate_time(time_matrix,neworder,truck[insertion_index])*60))
        if hour_t<hour_dt:
            return True
        elif hour_t==hour_dt and minute_t<=minute_dt:
            return True
        else:
            return False
    elif hour_t==hour_dt and minute_t<=minute_dt:
        minute_t = minute_dt
        if insertion_index > len(truck):
            return True
        if len(truck) == 0:
            return True
        hour_dt,minute_dt = delivered_time(truck[insertion_index],order_data_w)
        hour_t,minute_t = correct_time(hour_t,minute_t+(calculate_time(time_matrix,neworder,truck[insertion_index])*60))
        if hour_t<hour_dt:
            return True
        elif hour_t==hour_dt and minute_t<=minute_dt:
            return True
        else:
            return False
    else:
        return False

outsource_fee_cache_sum = {}
outsource_fee_cache = {}
def calculate_outsourcing_fee(individual,order_data_w,distance_matrix,desired_delivery_date):
    outsorce_fee = 0;
    for date in desired_delivery_date:
        outsourcing_tuple = make_hashable(individual[date]["Outsourcing"])
        if outsourcing_tuple in outsource_fee_cache_sum:
            outsorce_fee+=outsource_fee_cache_sum[outsourcing_tuple]
            continue
        else:
            for order in individual[date]["Outsourcing"]:
                if order in outsource_fee_cache:
                    outsorce_fee+=outsource_fee_cache[order]
                    continue
                else:
                    dis = calculate_distance(distance_matrix,0,order)
                    if order_data_w[order-1][-1] < 500:
                        if dis < 10:
                            outsorce_fee+=1000
                            outsource_fee_cache[order]=1000
                        elif dis < 20:
                            outsorce_fee+=1100
                            outsource_fee_cache[order]=1100
                        elif dis < 30:
                            outsorce_fee+=1200
                            outsource_fee_cache[order]=1200
                        elif dis < 40:
                            outsorce_fee+=1300
                            outsource_fee_cache[order]=1300
                        else:
                            outsorce_fee+=1400
                    elif order_data_w[order-1][-1] < 1000:
                        if dis < 10:
                            outsorce_fee+=1200
                            outsource_fee_cache[order]=1200
                        elif dis < 20:
                            outsorce_fee+=1400
                            outsource_fee_cache[order]=1400
                        elif dis < 30:
                            outsorce_fee+=1600
                            outsource_fee_cache[order]=1600
                        elif dis < 40:
                            outsorce_fee+=1800
                            outsource_fee_cache[order]=1800
                        else:
                            outsorce_fee+=2000
                            outsource_fee_cache[order]=2000
                    elif order_data_w[order-1][-1] < 1500:
                        if dis < 10:
                            outsorce_fee+=1400
                            outsource_fee_cache[order]=1400
                        elif dis < 20:
                            outsorce_fee+=1700
                            outsource_fee_cache[order]=1700
                        elif dis < 30:
                            outsorce_fee+=2000
                            outsource_fee_cache[order]=2000
                        elif dis < 40:
                            outsorce_fee+=2300
                            outsource_fee_cache[order]=2300
                        else:
                            outsorce_fee+=2600
                            outsource_fee_cache[order]=2600
        # outsource_fee_cache_sum[outsourcing_tuple]=outsorce_fee
    return outsorce_fee

def calculate_wait_time_and_outsourcingscore(individual,order_data_w,time_matrix,desired_delivery_date):
    wait_time=0
    out_score=0
    truck_num1=len(individual[desired_delivery_date[0]].keys())
    for date in desired_delivery_date:
        for truck in range(1,truck_num1):
            hour_t = 7
            minute_t = 0
            start_place = 0
            for order in individual[date][f"Truck{truck}"]["order"]:
                hour_dt,minute_dt = delivered_time(order,order_data_w)
                hour_t,minute_t = correct_time(hour_t,minute_t+(calculate_time(time_matrix,start_place,order)*60))
                hour_w = int(hour_dt)-int(hour_t)
                minute_w = int(minute_dt)-int(minute_t)
                hour_w,minute_w = correct_time(hour_w,minute_w)
                wait_time+=(hour_w+(minute_w/60))
                start_place = order
        out_score+=len(individual[date]["Outsourcing"])**2
    return wait_time,out_score;