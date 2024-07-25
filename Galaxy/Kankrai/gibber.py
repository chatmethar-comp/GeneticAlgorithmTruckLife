from input_data import orderlist, productlist, trucklist, outsourcing_fee_table, start_lat, start_lon
import numpy as np
import random
from math import radians, cos, sin, sqrt, atan2
from datetime import datetime, timedelta

# Calculate the distance between two latitude-longitude points using Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of the Earth in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# Convert order data to include distances from the starting point
for order in orderlist:
    order['distance'] = calculate_distance(start_lat, start_lon, order['latitude'], order['longitude'])

# Helper function to find the earliest start date
def get_earliest_start_date(orderlist):
    return min(datetime.strptime(order['receptiondate'], '%Y-%m-%d') for order in orderlist)

# Genetic Algorithm functions
def initialize_population(pop_size, orderlist, trucklist):
    population = []
    for _ in range(pop_size):
        individual = {'trucks': [], 'outsourced': []}
        for truck in trucklist:
            individual['trucks'].append({
                'truckid': truck['truckid'],
                'route': [],
                'load': 0,
                'current_date': get_earliest_start_date(orderlist),
                'log': [],
                'daily_loads': []  # New field to track daily load
            })
        
        orders = orderlist[:]
        random.shuffle(orders)
        for order in orders:
            assigned = False
            weight = next(p['weight'] for p in productlist if p['productid'] == order['product'])
            reception_date = datetime.strptime(order['receptiondate'], '%Y-%m-%d')
            for truck in individual['trucks']:
                truck_capacity = next(t['capacity'] for t in trucklist if t['truckid'] == truck['truckid'])
                remaining_capacity = truck_capacity - sum(truck['daily_loads'])  # Consider daily load
                if remaining_capacity >= weight:
                    start_date = max(truck['current_date'], reception_date)
                    end_date = datetime.strptime(order['desired_delivery_date_end'], '%Y-%m-%d')
                    if start_date <= end_date:
                        truck['route'].append(order['orderid'])
                        truck['load'] += weight
                        truck['log'].append((start_date.strftime('%Y-%m-%d'), order['orderid']))
                        # Update daily load for the assigned date
                        if truck['current_date'] == start_date:
                            truck['daily_loads'].append(weight)
                        else:
                            truck['daily_loads'].append(0)  # Start a new day with the order's weight
                            truck['current_date'] = start_date
                        assigned = True
                        break
            if not assigned:
                individual['outsourced'].append(order['orderid'])

        population.append(individual)
    return population

def fitness(individual, orderlist, productlist, outsourcing_fee_table, trucklist):
    total_distance = 0
    total_outsource_fee = 0
    
    for truck in individual['trucks']:
        truck_distance = 0
        route_orders = [next(o for o in orderlist if o['orderid'] == order_id) for order_id in truck['route']]
        if route_orders:
            start_order = route_orders[0]
            truck_distance += calculate_distance(start_lat, start_lon, start_order['latitude'], start_order['longitude'])
            for i in range(len(route_orders) - 1):
                order1 = route_orders[i]
                order2 = route_orders[i + 1]
                truck_distance += calculate_distance(order1['latitude'], order1['longitude'], order2['latitude'], order2['longitude'])
            end_order = route_orders[-1]
            truck_distance += calculate_distance(end_order['latitude'], end_order['longitude'], start_lat, start_lon)
        total_distance += truck_distance

    for outsourced_order_id in individual['outsourced']:
        order = next(o for o in orderlist if o['orderid'] == outsourced_order_id)
        weight = next(p['weight'] for p in productlist if p['productid'] == order['product'])
        for (distance_limit, weight_limit), fee in outsourcing_fee_table.items():
            if order['distance'] <= distance_limit and weight <= weight_limit:
                total_outsource_fee += fee
                break

    return total_distance + total_outsource_fee

def selection(population, fitness_scores, num_parents):
    parents = random.choices(population, weights=[1/f for f in fitness_scores], k=num_parents)
    return parents

def crossover(parent1, parent2, orderlist):
    child1, child2 = {'trucks': [], 'outsourced': []}, {'trucks': [], 'outsourced': []}
    crossover_point = random.randint(1, len(parent1['trucks']) - 1)
    
    child1['trucks'] = parent1['trucks'][:crossover_point] + parent2['trucks'][crossover_point:]
    child2['trucks'] = parent2['trucks'][:crossover_point] + parent1['trucks'][crossover_point:]

    def fix_routes(child):
        all_orders = {order['orderid'] for order in orderlist}
        assigned_orders = {order_id for truck in child['trucks'] for order_id in truck['route']}
        missing_orders = all_orders - assigned_orders
        duplicate_orders = assigned_orders - all_orders
        
        for order_id in duplicate_orders:
            for truck in child['trucks']:
                if order_id in truck['route']:
                    truck['route'].remove(order_id)
                    break
        for order_id in missing_orders:
            truck = random.choice(child['trucks'])
            truck['route'].append(order_id)

        # Check for remaining duplicates within a truck's route
        for truck in child['trucks']:
            seen_orders = set()
            new_route = []
            for order_id in truck['route']:
                if order_id not in seen_orders:
                    seen_orders.add(order_id)
                    new_route.append(order_id)
                else:
                    if missing_orders:  # Check if missing_orders is not empty before choosing
                        missing_order = random.choice(list(missing_orders))
                        missing_orders.remove(missing_order)
                        new_route.append(missing_order)
                    else:
                        # Handle the case where no missing orders are available (optional)
                        # You can choose to skip swapping or assign a random order from the route (not recommended)
                        pass
            truck['route'] = new_route

    fix_routes(child1)
    fix_routes(child2)

    return child1, child2

def mutate(individual, mutation_rate, orderlist, trucklist):
    if random.random() < mutation_rate:
        truck1, truck2 = random.sample(individual['trucks'], 2)
        if truck1['route'] and truck2['route']:
            order1 = random.choice(truck1['route'])
            order2 = random.choice(truck2['route'])
            truck1['route'].remove(order1)
            truck2['route'].remove(order2)
            truck1['route'].append(order2)
            truck2['route'].append(order1)

    return individual

def genetic_algorithm(pop_size, num_generations, mutation_rate, orderlist, productlist, trucklist, outsourcing_fee_table):
    population = initialize_population(pop_size, orderlist, trucklist)
    for generation in range(num_generations):
        fitness_scores = [fitness(ind, orderlist, productlist, outsourcing_fee_table, trucklist) for ind in population]
        parents = selection(population, fitness_scores, pop_size // 2)
        offspring = []

        for i in range(0, len(parents), 2):
            parent1, parent2 = parents[i], parents[i + 1]
            child1, child2 = crossover(parent1, parent2, orderlist)
            offspring.append(mutate(child1, mutation_rate, orderlist, trucklist))
            offspring.append(mutate(child2, mutation_rate, orderlist, trucklist))

        population = parents + offspring

    best_solution = min(population, key=lambda ind: fitness(ind, orderlist, productlist, outsourcing_fee_table, trucklist))
    return best_solution

# Parameters
pop_size = 100
num_generations = 500
mutation_rate = 0.1

# Run the genetic algorithm
best_solution = genetic_algorithm(pop_size, num_generations, mutation_rate, orderlist, productlist, trucklist, outsourcing_fee_table)


for truck in best_solution['trucks']:
    route = truck['route']
    load = sum(next(p['weight'] for p in productlist if p['productid'] == next(o['product'] for o in orderlist if o['orderid'] == order_id)) for order_id in route)
    print(f"Delivery log for Truck {truck['truckid']}:")
    daily_logs = {}
    for order_id in route:
        order = next(o for o in orderlist if o['orderid'] == order_id)
        date = order['receptiondate']
        if date not in daily_logs:
            daily_logs[date] = {'orders': [], 'load': 0}
        daily_logs[date]['orders'].append(order_id)
        daily_logs[date]['load'] += next(p['weight'] for p in productlist if p['productid'] == order['product'])
    for date, log in daily_logs.items():
        print(f"\tDate: {date}, Order ID: {', '.join(map(str, log['orders']))}, load: {log['load']}")

print(f"Outsourced orders: {best_solution.get('outsourced', [])}")