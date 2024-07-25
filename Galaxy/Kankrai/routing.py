import numpy as np
import pandas as pd
import random
import copy
from PIL import Image # for visualisation purposes (Optional)
import matplotlib.pyplot as plt # for visualisation purposes (Optional)
import folium # for visualisation purposes (Optional)
from folium import IFrame # for visualisation purposes (Optional)
import os # for visualisation purposes (Optional)
from selenium import webdriver # for visualisation purposes (Optional)
from selenium.webdriver.chrome.service import Service # for visualisation purposes (Optional)
from selenium.webdriver.chrome.options import Options # for visualisation purposes (Optional)
import io # for visualisation purposes (Optional)
import time # for visualisation purposes (Optional)

def get_data():
    """Get the data for the problem"""
    # Define the cost matrix
    connections_cost = np.array([
    # LIS   MAD   PAR   BER   AMS   ROM   ZUR   VIE   POR   BCN   TLS   SXB   GNT   BRU   HAM   FRA   MIL
    [np.inf, 10,   30,   np.inf, 55,   65,   np.inf, 80,   5,    20,   np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],  # LIS
    [10,    np.inf,10,   15,    np.inf,25,   30,    30,   15,   10,   np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],  # MAD
    [30,    15,   np.inf,15,    15,    30,   25,    35,   np.inf,25,   10,    20,    np.inf, np.inf, np.inf, np.inf, np.inf],  # PAR
    [40,    15,   25,   np.inf, 10,    20,   10,    15,   np.inf, np.inf, 15,   15,    np.inf, np.inf, 20,    np.inf, np.inf],  # BER
    [50,    20,   20,   10,    np.inf, 35,   25,    30,   np.inf, np.inf, np.inf, np.inf, 10,    5,     30,    20,    np.inf],  # AMS
    [70,    25,   35,   20,    35,    np.inf,20,    25,   np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 10],  # ROM
    [75,    30,   25,   15,    25,    20,   np.inf, 10,   np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 20],  # ZUR
    [75,    35,   45,   15,    30,    25,   10,    np.inf,np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],  # VIE
    [5,     15,   np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 15,   np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],  # POR
    [20,    10,   25,   np.inf, np.inf, np.inf, np.inf, np.inf, 15,   np.inf, 15,    np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],  # BCN
    [np.inf, np.inf, 10,  15,    np.inf, np.inf, np.inf, np.inf, np.inf, 15,   np.inf, 10,    np.inf, np.inf, np.inf, np.inf, np.inf],  # TLS
    [np.inf, np.inf, 20,  15,    np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 10,    np.inf, 15,    10,    np.inf, np.inf, np.inf],  # SXB
    [np.inf, np.inf, np.inf, np.inf, 10,   np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 15,    np.inf, 5,      25,    np.inf, np.inf],  # GNT
    [np.inf, np.inf, np.inf, np.inf, 5,    np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 10,    5,      np.inf, 20,    15,    np.inf],  # BRU
    [np.inf, np.inf, np.inf, 20,    30,    np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 25,    20,    np.inf, 10,    np.inf],  # HAM
    [np.inf, np.inf, np.inf, np.inf, 20,    np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 15,    10,    np.inf, 30],  # FRA
    [np.inf, np.inf, np.inf, np.inf, np.inf, 10,    20,    np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, 30,    np.inf],  # MIL
])

    # Cities
    cities = ['Lisbon', 'Madrid', 'Paris', 'Berlin', 'Amsterdam', 'Rome', 'Zurich', 'Vienna', 'Porto', 'Barcelona', 'Toulouse', 'Strasbourg', 'Ghent', 'Brussels', 'Hamburg', 'Frankfurt', 'Milan']

    cost_matrix = pd.DataFrame(connections_cost, index=cities, columns=cities)

    # Define the handling costs
    handling_costs = {'Lisbon': 2, 'Madrid': 3, 'Paris': 4, 'Berlin': 5, 'Amsterdam': 5, 'Rome': 4, 'Zurich': 6, 'Vienna': 6, 'Porto': 2, 'Barcelona': 3, 'Toulouse': 4, 'Strasbourg': 5, 'Ghent': 5, 'Brussels': 4, 'Hamburg': 6, 'Frankfurt': 6, 'Milan': 6}

    # Origin
    origin = 'Porto'

    # Destination
    destination = 'Zurich'

    # City coordinates - for visualisation purposes (Optional)
    cities_coords = {
        'Lisbon':{'latitude': 38.722, 'longitude': -9.139},
        'Madrid':{'latitude': 40.416, 'longitude': -3.703},
        'Paris':{'latitude': 48.856, 'longitude': 2.352},
        'Berlin':{'latitude': 52.520, 'longitude': 13.404},
        'Amsterdam':{'latitude': 52.370, 'longitude': 4.895},
        'Rome':{'latitude': 41.902, 'longitude': 12.496},
        'Zurich':{'latitude': 47.376, 'longitude': 8.541},
        'Vienna':{'latitude': 48.208, 'longitude': 16.373},
        'Porto':{'latitude': 41.157, 'longitude': -8.629},
        'Barcelona':{'latitude': 41.385, 'longitude': 2.173},
        'Toulouse':{'latitude': 43.604, 'longitude': 1.444},
        'Strasbourg':{'latitude': 48.583, 'longitude': 7.745},
        'Ghent':{'latitude': 51.054, 'longitude': 3.717},
        'Brussels':{'latitude': 50.850, 'longitude': 4.351},
        'Hamburg':{'latitude': 53.551, 'longitude': 9.993},
        'Frankfurt':{'latitude': 50.110, 'longitude': 8.683},
        'Milan':{'latitude': 45.464, 'longitude': 9.189}
        }

    return cities, origin, destination, handling_costs, cost_matrix, cities_coords

def create_network_map(cities, cost_matrix, cities_coords):
    """Create a visual representation of the network"""

    # Calculate average latitude and longitude for the initial map center
    avg_lat = sum(coord['latitude'] for coord in cities_coords.values()) / len(cities_coords)
    avg_lon = sum(coord['longitude'] for coord in cities_coords.values()) / len(cities_coords)

    # Create a map centered around the average location
    map = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)

    # Add markers for each city
    for city, coords in cities_coords.items():
        folium.Marker([coords['latitude'], coords['longitude']], popup=city).add_to(map)

    # Determine min and max costs for normalization
    min_cost = np.min(cost_matrix[cost_matrix != np.inf])
    max_cost = np.max(cost_matrix[cost_matrix != np.inf])

    # Function to normalize costs to a range for line widths
    def normalize_cost(cost, min_cost, max_cost, min_width=1, max_width=5):
        # Inverse normalization to make cheaper routes thicker
        return max_width - (cost - min_cost) * (max_width - min_width) / (max_cost - min_cost)

    line_color = '#69b8d6' # Color for the lines

    # Draw connections with varying line widths
    for i, city1 in enumerate(cities):
        for j, city2 in enumerate(cities):
            if i != j and cost_matrix.iloc[i, j] != np.inf:
                cost = cost_matrix.iloc[i, j]
                line_width = normalize_cost(cost, min_cost, max_cost)
                location1 = [cities_coords[city1]['latitude'], cities_coords[city1]['longitude']]
                location2 = [cities_coords[city2]['latitude'], cities_coords[city2]['longitude']]
                line = folium.PolyLine(locations=[location1, location2], weight=line_width, color=line_color)
                map.add_child(line)

    return map

def get_ga_config():
    """Get the configuration for the genetic algorithm"""
    population_size = 20 # Number of individuals in the population
    elitism_percentage = 0.2 # Percentage of the population to be selected for elitism
    tournament_size = 5 # Number of chromosomes to select for tournament
    max_generations = 100 # Number of generations to run the algorithm for
    max_stagnation = 20 # Number of generations to wait before terminating due to stagnation

    return population_size, elitism_percentage, tournament_size, max_generations, max_stagnation

def initialise_population(pop_size, cities, origin, destination):
    """Create a population of chromosomes"""
    population = []
    shortest_path_chromosome = {}
    longest_path_chromosome = {}

    # List all other cities besides the origin and destination
    connection_cities = [city for city in cities if city not in [origin, destination]]  # exclude origin and destination

    # Add a cromosome with the shortest path
    shortest_path_chromosome['route'] = [origin] + [destination]
    population.append(shortest_path_chromosome)

    # Add a chromosome with the longest path (going through all cities)
    longest_path_chromosome['route'] = [origin] + connection_cities + [destination]
    population.append(longest_path_chromosome)

    # Add chromosomes with random paths between origin and destination until we reach the total number of individuals in the population
    for _ in range(pop_size - 2):
        random_chromosome = {}
        # Randomly decide how many intermediate cities to include
        num_intermediate = random.randint(0, len(connection_cities) - 2)
        # Randomly select the intermediate cities
        intermediate_cities = random.sample(connection_cities, num_intermediate)
        # Build the chromosome
        random_chromosome['route'] = [origin] + intermediate_cities + [destination]
        # Add chromosome to population
        population.append(random_chromosome)

    return population

def evaluate_and_sort_population(population, cost_matrix, handling_costs):
    """Evaluate the population and sort it in ascending order of cost"""
    for chromosome in population:
        if 'cost' not in chromosome.keys():
            total_cost = 0
            for i in range(len(chromosome['route'])-1):
                city1 = chromosome['route'][i]
                city2 = chromosome['route'][i + 1]
                total_cost += cost_matrix.loc[city1, city2] + handling_costs[city1]
            chromosome['cost'] = total_cost
    return sorted(population, key=lambda x: x['cost'])

def tournament_selection(population, tournament_size):
    """Select two parents from the population using tournament selection"""
    selected_parents = []
    for _ in range(2): # Select two parents
        # Randomly select tournament_size chromosomes for the tournament
        tournament = random.sample(population, tournament_size)
        # Select the best chromosome from the tournament
        winner = min(tournament, key=lambda x: x['cost'])
        selected_parents.append(winner)
    return selected_parents

def crossover(parent1, parent2, origin, destination):
    """Create two new chromosomes by applying crossover to two parent chromosomes"""
    route1 = copy.deepcopy(parent1['route'])
    route2 = copy.deepcopy(parent2['route'])

    #Proceed to crossover if both parents have more than two cities and if parents are different
    if min(len(route1), len(route2)) > 2 and route1 != route2:
        # If one of the parents has only 3 cities, then add the other parent's cities to the offspring (otherwise we end up with offsprings which are the same as the parents)
        if min(len(route1), len(route2)) == 3:
            # Randomly select a crossover point
            crossover_point = random.randint(1, min(len(route1), len(route2))-1)
            # Perform crossover
            offspring1_route = route1 + route2[crossover_point:]
            offspring2_route = route2 + route1[crossover_point:]
        
        else: 
            # Randomly select a crossover point (between 2 and the minimum length of the two routes -2, to maximise odds of having offsprings different from parents)
            crossover_point = random.randint(2, min(len(route1), len(route2)) - 2)

            # Perform crossover
            offspring1_route = route1[:crossover_point] + route2[crossover_point:]
            offspring2_route = route2[:crossover_point] + route1[crossover_point:]

        # Repair the offsprings routes to avoid repeating cities 
        offspring1_route = repair_route(offspring1_route, origin, destination)
        offspring2_route = repair_route(offspring2_route, origin, destination)

        # Create offsprings
        offspring1 = {"route": offspring1_route}
        offspring2 = {"route": offspring2_route}

        return offspring1, offspring2
    
    # If one or both parents have only one leg, return the parents since offsprings would be the same as parents
    else:
        return parent1, parent2


def repair_route(route, origin, destination):
    """Repair a route by ensuring it starts and ends at the origin and destination, respectively, and by removing repeated cities"""
    # Ensure first city is origin and last city is destination and remove intermediate cities if they are origin or destination
    if route[0] != origin:
        route[0] = origin
    if route[-1] != destination:
        route[-1] = destination
    route = [route[0]] + [city for city in route[1:-1] if city != origin and city != destination] + [route[-1]]

    # Remove repeated cities
    seen = set()
    repaired_route = [seen.add(city) or city for city in route if city not in seen] # adds city to seen if not already there and, in that case, adds city to fixed_route

    return repaired_route

# Mutation Function
def mutation(chromosome, cities, origin, destination):
    """Create two new chromosomes by applying mutations to a chromosome"""
    route1 = copy.deepcopy(chromosome['route'])
    route2 = copy.deepcopy(chromosome['route'])

    # Ensure we only add cities that are not the origin, destination, or already in the route
    possible_cities_to_add = [city for city in cities if city not in chromosome['route']]

    # If chromosome has only 2 cities, create two new chromosomes by adding a city between the origin and destination (position 1):
    if len(chromosome['route']) == 2:
        route1.insert(1, random.choice(possible_cities_to_add))
        route2.insert(1, random.choice(possible_cities_to_add))

    # If chromosome has 3 or more cities, create a new chromosome by removing a city
    elif len(chromosome['route']) >= 3:
        route1.pop(random.randint(1, len(chromosome['route'])-1))

        # If chromosome has 3 cities, create a new chromosome by adding a city between the origin and destination (position 1):
        if len(chromosome['route']) == 3:
            route2.insert(1, random.choice(possible_cities_to_add))

        # If chromosome has 4 or more cities, create a new chromosome by swapping two cities
        elif len(chromosome['route']) >= 4:
            idx1, idx2 = random.sample(range(1, len(chromosome['route'])-1), 2)  # Get two distinct indices
            # Perform the swap
            route2[idx1], route2[idx2] = route2[idx2], route2[idx1]
    
    # Repair routes if necessary
    route1 = repair_route(route1, origin, destination)
    route2 = repair_route(route2, origin, destination)

    # Create offsprings
    mutated_chromosome1 = {"route": route1}
    mutated_chromosome2 = {"route": route2}

    return mutated_chromosome1, mutated_chromosome2