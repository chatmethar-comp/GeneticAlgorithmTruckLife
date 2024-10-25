import csv
import osm
import pandas as pd

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
    if len(truck)==0:
        return True
    hour_dt,minute_dt = delivered_time(neworder,order_data_w)
    hour_t,minute_t = delivered_time(truck[-1],order_data_w)
    hour_t,minute_t = correct_time(hour_t,minute_t+(calculate_time(time_matrix,truck[-1],neworder)*60))
    if hour_t<hour_dt or (hour_t==hour_dt and minute_t<=minute_dt):
        return True
    else:
        return False

def check_time_insert_item(neworder, insertion_index, truck, order_data_w, time_matrix):
    # Initialize start time and start place
    hour_t = 7
    minute_t = 0
    start_place = 0

    # Loop through orders in the truck up to the insertion index
    for order in truck[:insertion_index]:
        # Update the time based on the current order
        if order == 0:
            hour_dt, minute_dt = correct_time(hour_t, minute_t + calculate_time(time_matrix, start_place, order) * 60)
        else:
            hour_dt, minute_dt = delivered_time(order, order_data_w)
        hour_t, minute_t = hour_dt, minute_dt

        # Update the start place for the next iteration
        start_place = order

    # Process the new order's delivery time
    hour_dt, minute_dt = delivered_time(neworder, order_data_w)
    hour_t, minute_t = correct_time(hour_t, minute_t + (calculate_time(time_matrix, start_place, neworder) * 60))

    # Check if new order fits in the delivery schedule
    if hour_t < hour_dt or (hour_t == hour_dt and minute_t <= minute_dt):
        hour_t, minute_t = hour_dt, minute_dt
    else:
        return False

    # If there's a next order after the insertion point, validate the time window
    if insertion_index < len(truck):
        next_order = truck[insertion_index]
        hour_dt, minute_dt = delivered_time(next_order, order_data_w)
        hour_t, minute_t = correct_time(hour_t, minute_t + (calculate_time(time_matrix, neworder, next_order) * 60))

        # Final time validation with the next order
        if hour_t > hour_dt or (hour_t == hour_dt and minute_t > minute_dt):
            return False

    return True



outsource_fee_cache_truck = {}
outsource_fee_cache = {}

def calculate_outsourcing_fee(individual, order_data_w, distance_matrix, desired_delivery_date):
    outsorce_fee = 0

    for date in desired_delivery_date:
        outsourcing_tuple = make_hashable(individual[date]["Outsourcing"])

        # Check if the entire outsourcing list for this truck is cached
        if outsourcing_tuple in outsource_fee_cache_truck:
            outsorce_fee += outsource_fee_cache_truck[outsourcing_tuple]
            continue

        # If not, calculate the outsourcing fees for this date
        current_fee = 0
        for order in individual[date]["Outsourcing"]:
            # Check if the fee for this individual order is cached
            if order in outsource_fee_cache:
                current_fee += outsource_fee_cache[order]
                continue

            # Calculate distance and fee
            dis = calculate_distance(distance_matrix, 0, order)
            weight = order_data_w[order - 1][-1]

            # Use a dictionary for fee calculations based on weight and distance ranges
            fee = calculate_fee_by_weight_and_distance(weight, dis)

            current_fee += fee
            outsource_fee_cache[order] = fee  # Cache the result for this order

        outsorce_fee += current_fee
        outsource_fee_cache_truck[outsourcing_tuple] = current_fee  # Cache result for the truck

    return outsorce_fee

def calculate_fee_by_weight_and_distance(weight, dis):
    if weight < 500:
        if dis < 10:
            return 1000
        elif dis < 20:
            return 1100
        elif dis < 30:
            return 1200
        elif dis < 40:
            return 1300
        else:
            return 1400
    elif weight < 1000:
        if dis < 10:
            return 1200
        elif dis < 20:
            return 1400
        elif dis < 30:
            return 1600
        elif dis < 40:
            return 1800
        else:
            return 2000
    elif weight < 1500:
        if dis < 10:
            return 1400
        elif dis < 20:
            return 1700
        elif dis < 30:
            return 2000
        elif dis < 40:
            return 2300
        else:
            return 2600



# Caches for storing previously computed results
time_cache = {}
wait_time_cache = {}

def calculate_wait_time_and_outsourcingscore(individual, order_data_w, time_matrix, desired_delivery_date):
    wait_time = 0
    out_score = 0

    for date in desired_delivery_date:
        truck_num1 = len(individual[date].keys())

        for truck in range(1, truck_num1):
            hour_t, minute_t = 7, 0
            start_place = 0

            # Get the orders for the current truck
            orders = individual[date][f"Truck{truck}"]["order"]

            # Create a cache key using just the sequence of orders
            wait_time_key = tuple(orders)

            # If the wait time for this order sequence has been cached, use it
            if wait_time_key in wait_time_cache:
                wait_time += wait_time_cache[wait_time_key]
                continue

            # Otherwise, calculate the wait time for this order sequence
            current_truck_wait_time = 0

            for order in orders:
                # Cache key for time calculation between start_place and order
                time_cache_key = (start_place, order)

                if time_cache_key in time_cache:
                    travel_time = time_cache[time_cache_key]
                else:
                    travel_time = calculate_time(time_matrix, start_place, order) * 60
                    time_cache[time_cache_key] = travel_time

                # Update current time
                hour_t, minute_t = correct_time(hour_t, minute_t + travel_time)

                # Calculate wait time for the current order
                hour_dt, minute_dt = delivered_time(order, order_data_w)
                hour_w = hour_dt - hour_t
                minute_w = minute_dt - minute_t
                hour_w, minute_w = correct_time(hour_w, minute_w)

                # Add the wait time for this order
                current_truck_wait_time += hour_w + (minute_w / 60)

                # Update start place to the current order for the next iteration
                start_place = order

            # Cache the wait time for this specific order sequence
            wait_time_cache[wait_time_key] = current_truck_wait_time
            wait_time += current_truck_wait_time

        # Calculate outsourcing score for the current date
        outsourcing_len = len(individual[date]["Outsourcing"])
        out_score += outsourcing_len ** 2

    return wait_time, out_score


def to_truck_routes(data_structure, order_data, desired_delivery_dates):
    """
    Transforms the truck and order data into the input format expected for creating routes.
    
    :param data_structure: Dictionary containing dates as keys and truck assignments with orders.
    :param order_data: List of order data with lat/lon and delivery details.
    :param desired_delivery_dates: List of dates to process.
    :return: Dictionary where keys are days and values are lists of truck coordinate routes.
    """
    # Create a dictionary to hold the routes by day
    daily_truck_routes = {}

    # Convert the route data into a dictionary with day as the key
    for day in desired_delivery_dates:
        # Check if the day exists in the data_structure
        if day in data_structure:
            daily_truck_routes[day] = [[] for _ in range(len(data_structure[day].keys()))]  # Assuming 4 trucks

            # Go through each truck's assigned orders
            for truck_num in range(1, len(data_structure[day].keys())):  # Truck1 to Truck4
                truck_orders = data_structure[day][f'Truck{truck_num}']['order']
                truck_coords = []

                # Collect lat/lon data for each order assigned to the truck
                for order_id in truck_orders:
                    if order_id > 0:  # Ensure the order ID is valid
                        # Check if the order_id is within the valid range
                        if 1 <= order_id <= len(order_data):
                            lat, lon = order_data[order_id - 1][2], order_data[order_id - 1][3]
                            truck_coords.append((lat, lon))
                        else:
                            print(f"Warning: Order ID {order_id} is out of range for order_data.")

                # Assign the collected coordinates to the truck's route for the day
                daily_truck_routes[day][truck_num] = truck_coords  # truck_num - 1 for 0-based index

    return daily_truck_routes

def output_as_excel(truck_routes, order_data_w, time_matrix, desired_delivery_dates):
    output = []

    for date in desired_delivery_dates:
        output.append([date])  # Start the output with the date
        
        if date in truck_routes:
            trucks = truck_routes[date].keys()  # Get the list of trucks for the date

            for truck_id in trucks:
                truck_data = truck_routes[date][truck_id]
                
                if truck_id == "Outsourcing":
                    continue
                else:
                    # Ensure truck_data is a dictionary and handle potential outsourcing
                    if isinstance(truck_data, dict):
                        truck_output = []  # Initialize truck output
                        output[-1].append(truck_output)  # Append truck output list

                        # Initialize variables
                        hour_t, minute_t = 7, 0  # Default start time
                        start_place = 0
                        last_order = None
                        delivered = False

                        # Get the first order to determine start time
                        orders = truck_data.get('order', [])  # Get orders list
                        if orders:  # Only proceed if there are orders
                            first_order = orders[0]  # Get first order
                            hour_t, minute_t = delivered_time(first_order, order_data_w)  # Set start time based on first order
                            hour_t, minute_t = correct_time(hour_t,minute_t - (time_matrix[0][first_order])*60)
                            hour_t = int(hour_t)
                            minute_t = int(minute_t)

                        # Process each order in the truck
                        for order in orders:
                            if order:
                                order_time_str = f'{hour_t:02}:{minute_t:02}'  # Current time string
                                
                                # Update time after delivery
                                delivery_duration = int(calculate_time(time_matrix, start_place, order) * 60)
                                hour_t, minute_t = correct_time(hour_t, minute_t + delivery_duration)
                                delivery_time_str = f'{hour_t:02}:{minute_t:02}'  # Delivery time string

                                # Append order delivery information
                                truck_output.append([order, order_time_str, delivery_time_str])  # Order delivery time
                                hour_dt, minute_dt = delivered_time(order, order_data_w)
                                hour_t = hour_dt
                                minute_t = minute_dt
                                delivered_timed = f'{hour_dt:02}:{minute_dt:02}' 
                                truck_output.append([f'wait to deliver {order}', delivery_time_str, delivered_timed])  # Waiting message

                                # Update the last order and start place
                                last_order = order
                                start_place = order
                                delivered = True

                        # Handle return to warehouse if there was a delivery
                        if delivered:
                            return_time_str = f'{hour_t:02}:{minute_t:02}'  # Time back to warehouse
                            # Calculate time at warehouse
                            arrival_at_warehouse_time = correct_time(hour_t, minute_t + int(calculate_time(time_matrix, last_order, 0) * 60))
                            arrival_time_str = f'{arrival_at_warehouse_time[0]:02}:{arrival_at_warehouse_time[1]:02}'
                            truck_output.append(["Go back to warehouse", return_time_str, arrival_time_str])

                    # Add empty lists for trucks with no orders
                    else:
                        output[-1].append([])  # If truck_data is not a dictionary, append empty list

            # Handle outsourcing orders
            if "Outsourcing" in truck_routes[date]:
                outsourcing_orders = truck_routes[date]["Outsourcing"]
                output[-1].append(outsourcing_orders)  # Add outsourcing orders directly

    return output

def Excel_writer(truck_schedule):
    with pd.ExcelWriter('truck_schedule_output.xlsx', engine='xlsxwriter') as writer:
        for day_schedule in truck_schedule:
            # Extract date, truck activities, and outsourcing activities
            date = day_schedule[0]
            trucks = day_schedule[1:-1]  # All lists following the date, except the last, are truck activities
            outsourcing = day_schedule[-1]  # The last element is the outsourcing activities

            # Prepare a list of rows for the DataFrame
            rows = []

            # Find the maximum number of activities among the trucks for this date
            max_activities = max(len(truck) for truck in trucks) if trucks else 0
            max_outsourcing = len(outsourcing)

            # Create rows for each truck's activities
            for i in range(max(max_activities, max_outsourcing)):
                row = {}
                # Fill truck activities
                for truck_index, truck_activities in enumerate(trucks):
                    if i < len(truck_activities):
                        # Convert the activity to a formatted string
                        activity = truck_activities[i]
                        row[f'Truck{truck_index + 1}'] = f"{activity[0]}, {activity[1]} - {activity[2]}"
                    else:
                        row[f'Truck{truck_index + 1}'] = None  # Fill with None if no more activities
                
                # Fill outsourcing activities in the last column, only with order number (no time)
                if i < max_outsourcing:
                    outsourcing_activity = outsourcing[i]
                    row['Outsourcing'] = f"Order: {outsourcing_activity}"
                else:
                    row['Outsourcing'] = None  # Fill with None if no more outsourcing activities

                # Append the row to the list
                rows.append(row)

            # Convert rows to DataFrame
            df = pd.DataFrame(rows)

            # Write each date to a separate sheet named after the date
            df.to_excel(writer, sheet_name=str(date), index=False)

    print("Truck schedule with order numbers has been written to 'truck_schedule_output.xlsx'")
