import numpy as np
import matplotlib.pyplot as plt

coordinates = [
    (13.7563, 100.5018, 500),   # Bangkok with weight
    (18.7883, 98.9853, 300),    # Chiang Mai with weight
    (13.3611, 100.9847, 400),   # Samut Prakan with weight
    (7.8804, 98.3923, 250),     # Phuket with weight
    (15.8700, 100.9925, 600),   # Nakhon Sawan with weight
    (17.9647, 102.6291, 200),   # Khon Kaen with weight
    (12.5657, 99.9410, 350),    # Hua Hin with weight
    (16.4419, 102.8329, 450),   # Udon Thani with weight
    (16.2534, 103.2497, 150),   # Kalasin with weight
    (13.8251, 100.4357, 550)    # Nonthaburi with weight
]

Truck_weight = 1900  # Maximum allowable weight for the truck

def haversine_distance(point1, point2):
    lat1, lon1, _ = point1
    lat2, lon2, _ = point2
    R = 6371  # Radius of the Earth in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) * np.sin(dlat / 2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) * np.sin(dlon / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def nearest_neighbor(coordinates, max_weight):
    route = []
    current_weight = 0
    available_coords = coordinates[:]
    
    current_location = available_coords.pop(0)  # Start from the first location (Bangkok in this case)
    route.append(current_location)
    current_weight += current_location[2]
    
    while available_coords:
        next_location = min(available_coords, key=lambda x: haversine_distance(current_location, x))
        if current_weight + next_location[2] <= max_weight:
            route.append(next_location)
            current_weight += next_location[2]
            current_location = next_location
            available_coords.remove(next_location)
        else:
            break  # Stop if adding the next location would exceed the truck's weight limit
    
    return route

def route_distance(route):
    total_distance = 0
    for i in range(len(route)):
        total_distance += haversine_distance(route[i], route[(i + 1) % len(route)])
    return total_distance

def plot_route(route):
    plt.figure(figsize=(10, 6))
    x = [point[1] for point in route] + [route[0][1]]
    y = [point[0] for point in route] + [route[0][0]]
    plt.plot(x, y, 'o-')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Best Delivery Route in Thailand')
    plt.show()

if __name__ == "__main__":
    best_route = nearest_neighbor(coordinates, Truck_weight)
    print("Best route: ", best_route)
    print("Total distance: ", route_distance(best_route))
    plot_route(best_route)
