import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

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

def tsp_dp_with_weight_constraint(coordinates, max_weight):
    n = len(coordinates)
    all_distances = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            all_distances[i, j] = haversine_distance(coordinates[i], coordinates[j])
    
    dp = {(frozenset([i]), i): (0, [i]) for i in range(n) if coordinates[i][2] <= max_weight}
    
    for size in range(2, n + 1):
        new_dp = {}
        for subset in combinations(range(n), size):
            subset_set = frozenset(subset)
            for j in subset:
                if sum(coordinates[k][2] for k in subset) > max_weight:
                    continue
                subset_minus_j = subset_set - {j}
                best_distance, best_path = float('inf'), None
                for k in subset_minus_j:
                    current_distance = dp[(subset_minus_j, k)][0] + all_distances[k][j]
                    if current_distance < best_distance:
                        best_distance = current_distance
                        best_path = dp[(subset_minus_j, k)][1] + [j]
                new_dp[(subset_set, j)] = (best_distance, best_path)
        dp = new_dp
    
    # Returning to the start (Bangkok in this case)
    best_distance, best_path = min(
        [(dp[d][0] + all_distances[d[1]][0], dp[d][1]) for d in dp if len(d[0]) == n],
        key=lambda x: x[0]
    )
    best_path.append(0)  # Complete the cycle back to the start
    
    return [coordinates[i] for i in best_path], best_distance

def plot_route(route):
    plt.figure(figsize=(10, 6))
    x = [point[1] for point in route] + [route[0][1]]
    y = [point[0] for point in route] + [route[0][0]]
    plt.plot(x, y, 'o-')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Optimized Delivery Route in Thailand')
    plt.show()

if __name__ == "__main__":
    best_route, best_distance = tsp_dp_with_weight_constraint(coordinates, Truck_weight)
    print("Best route: ", best_route)
    print("Total distance: ", best_distance)
    plot_route(best_route)
