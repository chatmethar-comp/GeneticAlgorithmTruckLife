import numpy as np
import pandas as pd
from deap import base, creator, tools, algorithms
from geopy.distance import great_circle
import random

# Input data
orderlist = [
    {"orderid": 1, "receptiondate": "2024-06-01", "latitude": 34.05, "longitude": -118.25, "desired_delivery_date": "2024-06-05", "product": 101},
    {"orderid": 2, "receptiondate": "2024-06-02", "latitude": 36.16, "longitude": -115.15, "desired_delivery_date": "2024-06-06", "product": 102},
    {"orderid": 3, "receptiondate": "2024-06-03", "latitude": 40.71, "longitude": -74.01, "desired_delivery_date": "2024-06-07", "product": 103},
    # Add more orders...
]
productlist = [
    {"productid": 101, "productname": "Product A", "weight": 10},
    {"productid": 102, "productname": "Product B", "weight": 20},
    {"productid": 103, "productname": "Product C", "weight": 30},
    # Add more products...
]
trucklist = [
    {"truckid": 1, "truckname": "Truck A", "capacity": 1000},
    {"truckid": 2, "truckname": "Truck B", "capacity": 500},
    {"truckid": 3, "truckname": "Truck C", "capacity": 800},
    # Add more trucks...
]
outsourcingfee = {
    1: 200,  # Example outsourcing fee for orderid 1
    2: 300,  # Example outsourcing fee for orderid 2
    3: 400,  # Example outsourcing fee for orderid 3
    # Add more outsourcing fees...
}

initial_location = (0.0, 0.0)  # Starting location

# Helper functions
def get_product_weight(product_id):
    for product in productlist:
        if product["productid"] == product_id:
            return product["weight"]
    return 0

def calculate_distance(loc1, loc2):
    return great_circle(loc1, loc2).kilometers

def route_distance(route, orders):
    distance = 0
    if route:
        # Distance from initial location to the first order
        distance += calculate_distance(initial_location, (orders[route[0]]["latitude"], orders[route[0]]["longitude"]))
        # Distance between orders
        for i in range(len(route) - 1):
            distance += calculate_distance(
                (orders[route[i]]["latitude"], orders[route[i]]["longitude"]),
                (orders[route[i + 1]]["latitude"], orders[route[i + 1]]["longitude"]),
            )
        # Distance from the last order back to the initial location
        distance += calculate_distance(
            (orders[route[-1]]["latitude"], orders[route[-1]]["longitude"]),
            initial_location
        )
    return distance

def calculate_route_cost(route, orders, truck, outsourcingfee):
    total_distance = route_distance(route, orders)
    total_weight = sum(get_product_weight(orders[i]["product"]) for i in route)

    if total_weight > truck["capacity"]:
        return float('inf')  # Penalty for exceeding truck capacity

    outsourcing_cost = sum(outsourcingfee[orders[i]["orderid"]] for i in route if get_product_weight(orders[i]["product"]) > truck["capacity"])

    return total_distance + outsourcing_cost

# Genetic Algorithm setup
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("indices", random.sample, range(len(orderlist)), len(orderlist))
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
    best_truck = None
    best_cost = float('inf')
    for truck in trucklist:
        cost = calculate_route_cost(individual, orderlist, truck, outsourcingfee)
        if cost < best_cost:
            best_cost = cost
            best_truck = truck
    individual.best_truck = best_truck["truckname"]
    return best_cost,

toolbox.register("mate", tools.cxOrdered)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)

def main():
    random.seed(42)

    population = toolbox.population(n=50)
    hof = tools.HallOfFame(1)

    algorithms.eaSimple(population, toolbox, cxpb=0.7, mutpb=0.2, ngen=100, halloffame=hof, verbose=True)

    best_individual = hof[0]
    best_cost, = evaluate(best_individual)
    best_truck = best_individual.best_truck
    best_route = best_individual

    print("Best Truck:", best_truck)
    print("Best Route:", best_route)
    print("Best Route Cost:", best_cost)

    for index in best_route:
        order = orderlist[index]
        print(f"Order ID: {order['orderid']}, Location: ({order['latitude']}, {order['longitude']}), Product ID: {order['product']}, Desired Delivery Date: {order['desired_delivery_date']}")

if __name__ == "__main__":
    main()
