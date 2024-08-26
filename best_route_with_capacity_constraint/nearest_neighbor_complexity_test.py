import time
import tracemalloc
import nearest_neighbor
import matplotlib.pyplot as plt
import pandas as pd

# TODO: create more input case to see the performance of TruckLife v1
optimized_params = [
    {
        "id": 1,
        "coordinates" : [
            (13.7563, 100.5018, 500),  # Bangkok with weight
        ],
        "Truck_weight" : 500,
        "n_coord": 1
    },
    {
        "id": 2,
        "coordinates" : [
            (13.7563, 100.5018, 500), # Bangkok with weight
            (18.7883, 98.9853, 300),    # Chiang Mai with weight
        ],
        "Truck_weight" : 500,
        "n_coord": 2
    },
    {
        "id": 3,
        "coordinates" : [
            (13.7563, 100.5018, 500),  # Bangkok with weight
            (18.7883, 98.9853, 300),    # Chiang Mai with weight
            (13.3611, 100.9847, 400),   # Samut Prakan with weight
        ],
        "Truck_weight" : 500,
        "n_coord": 3
    },
    {
        "id": 4,
        "coordinates": [
            (13.7563, 100.5018, 500),  # Bangkok
            (18.7883, 98.9853, 300),   # Chiang Mai
            (13.3611, 100.9847, 400),  # Samut Prakan
            (7.8804, 98.3923, 250),    # Phuket
            (15.8700, 100.9925, 600),  # Nakhon Sawan
        ],
        "Truck_weight": 900,
        "n_coord": 5
    },
    {
        "id": 5,
        "coordinates": [
            (13.7563, 100.5018, 500),  # Bangkok
            (18.7883, 98.9853, 300),   # Chiang Mai
            (13.3611, 100.9847, 400)  # Samut Prakan
        ],
        "Truck_weight": 900,
        "n_coord": 3
    },
    {
        "id": 6,
        "coordinates": [
            (13.7563, 100.5018, 500),  # Bangkok
            (18.7883, 98.9853, 300),   # Chiang Mai
            (13.3611, 100.9847, 400),  # Samut Prakan
            (7.8804, 98.3923, 250),    # Phuket
        ],
        "Truck_weight": 900,
        "n_coord": 4
    },
    {'id': 7, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200), (12.5657, 99.941, 350)], 'Truck_weight': 2600, 'n_coord': 7}, {'id': 8, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200), (12.5657, 99.941, 350), (16.4419, 102.8329, 450)], 'Truck_weight': 3050, 'n_coord': 8}, {'id': 9, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200), (12.5657, 99.941, 350), (16.4419, 102.8329, 450), (16.2534, 103.2497, 150)], 'Truck_weight': 3200, 'n_coord': 9}, {'id': 10, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200), (12.5657, 99.941, 350), (16.4419, 102.8329, 450), (16.2534, 103.2497, 150), (13.8251, 100.4357, 550)], 'Truck_weight': 3750, 'n_coord': 10}, {'id': 11, 'coordinates': [(13.7563, 100.5018, 500)], 'Truck_weight': 500, 'n_coord': 1}, {'id': 12, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300)], 'Truck_weight': 800, 'n_coord': 2}, {'id': 13, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400)], 'Truck_weight': 1200, 'n_coord': 3}, {'id': 14, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250)], 'Truck_weight': 1450, 'n_coord': 4}, {'id': 15, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600)], 'Truck_weight': 2050, 'n_coord': 5}, {'id': 16, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200)], 'Truck_weight': 2250, 'n_coord': 6}, {'id': 17, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200), (12.5657, 99.941, 350)], 'Truck_weight': 2600, 'n_coord': 7}, {'id': 18, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200), (12.5657, 99.941, 350), (16.4419, 102.8329, 450)], 'Truck_weight': 3050, 'n_coord': 8}, {'id': 19, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200), (12.5657, 99.941, 350), (16.4419, 102.8329, 450), (16.2534, 103.2497, 150)], 'Truck_weight': 3200, 'n_coord': 9}, {'id': 20, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200), (12.5657, 99.941, 350), (16.4419, 102.8329, 450), (16.2534, 103.2497, 150), (13.8251, 100.4357, 550)], 'Truck_weight': 3750, 'n_coord': 10}, {'id': 21, 'coordinates': [(13.7563, 100.5018, 500)], 'Truck_weight': 500, 'n_coord': 1}, {'id': 22, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300)], 'Truck_weight': 800, 'n_coord': 2}, {'id': 23, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400)], 'Truck_weight': 1200, 'n_coord': 3}, {'id': 24, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250)], 'Truck_weight': 1450, 'n_coord': 4}, {'id': 25, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600)], 'Truck_weight': 2050, 'n_coord': 5}, {'id': 26, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200)], 'Truck_weight': 2250, 'n_coord': 6}, {'id': 27, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200), (12.5657, 99.941, 350)], 'Truck_weight': 2600, 'n_coord': 7}, {'id': 28, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200), (12.5657, 99.941, 350), (16.4419, 102.8329, 450)], 'Truck_weight': 3050, 'n_coord': 8},
    {
        "id": 29,
        "coordinates": [
            (13.7563, 100.5018, 500),   # Bangkok
            (18.7883, 98.9853, 300),    # Chiang Mai
            (13.3611, 100.9847, 400),   # Samut Prakan
            (7.8804, 98.3923, 250),     # Phuket
            (15.8700, 100.9925, 600),   # Nakhon Sawan
            (17.9647, 102.6291, 200),   # Khon Kaen
            (12.5657, 99.9410, 350),    # Hua Hin
            (16.4419, 102.8329, 450),   # Udon Thani
            (16.2534, 103.2497, 150),   # Kalasin
        ],
        "Truck_weight": 2800,
        "n_coord": 9
    },
    {
        "id": 30,
        "coordinates" : [
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
        ],
        "Truck_weight" : 3000,
        "n_coord": 10
    },
    {
        "id": 31,
        "coordinates": [
            (13.7563, 100.5018, 500),  # Bangkok
            (18.7883, 98.9853, 300),   # Chiang Mai
            (13.3611, 100.9847, 400),  # Samut Prakan
            (7.8804, 98.3923, 250),    # Phuket
        ],
        "Truck_weight": 3000,
        "n_coord": 4
    },
    {
        "id": 32,
        "coordinates": [
            (13.7563, 100.5018, 500),  # Bangkok
            (18.7883, 98.9853, 300),   # Chiang Mai
            (13.3611, 100.9847, 400),  # Samut Prakan
            (7.8804, 98.3923, 250),    # Phuket
        ],
        "Truck_weight": 3500,
        "n_coord": 4
    },
    {'id': 33, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200)], 'Truck_weight': 900, 'n_coord': 6},
    {'id': 34, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200)], 'Truck_weight': 1500, 'n_coord': 6},
    {'id': 35, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200)], 'Truck_weight': 2000, 'n_coord': 6},
    {'id': 36, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200)], 'Truck_weight': 4500, 'n_coord': 6},
    {'id': 37, 'coordinates': [(13.7563, 100.5018, 500), (18.7883, 98.9853, 300), (13.3611, 100.9847, 400), (7.8804, 98.3923, 250), (15.87, 100.9925, 600), (17.9647, 102.6291, 200)], 'Truck_weight': 2250, 'n_coord': 6},
]

log_file = "best_route_with_capacity_constraint/complexity/nearest_v1.log"

def log_performance():
    for param in optimized_params:
        
        start_time = time.time()

        tracemalloc.start()
        best_route = nearest_neighbor.nearest_neighbor(param["coordinates"], param["Truck_weight"])

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        end_time = time.time()
        execution_time = end_time - start_time
        print("id: ", param["id"])
        print(f"n_coord: {param['n_coord']}")
        print(f"Truck_weight: {param['Truck_weight']}")
        print(f"Execution time: {execution_time:.4f} seconds")
        print(f"Peak memory usage: {peak / 10**6:.4f} MB")
        
        with open(log_file, "a") as log:
            log.write(f"id: {param['id']}\n")
            log.write(f"n_coord: {param['n_coord']}\n")
            log.write(f"Truck_weight: {param['Truck_weight']}\n")
            log.write(f"Execution time(seconds): {execution_time:.4f}\n")
            log.write(f"Peak memory usage(MB): {peak / 10**6:.4f}\n")
            log.write("\n")

def extract_data(log_file):
    data = []
    with open(log_file, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines), 6):
            entry = {}
            entry['id'] = int(lines[i].strip().split(': ')[1])
            entry['n_coord'] = int(lines[i+1].strip().split(': ')[1])
            entry['truck_weight'] = float(lines[i+2].strip().split(': ')[1])
            entry['execution_time'] = float(lines[i+3].strip().split(': ')[1])
            entry['peak_memory'] = float(lines[i+4].strip().split(': ')[1])
            data.append(entry)
    return data

def plot_data(data):
    # TODO: make more plot to see the relation of number of location and truck capacity to Execution time and memory usage in TruckLife v1 
    df = pd.DataFrame(data)

    plt.figure(figsize=(10, 6))
    plt.scatter(df['n_coord'], df['execution_time'], c=df['truck_weight'], cmap='viridis')
    plt.colorbar(label='Truck Weight')
    
    plt.xlabel('Number of Coordinates')
    plt.ylabel('Execution Time')
    plt.title('Execution Time vs Number of Coordinates (Colored by Truck Weight)')
    plt.show()

if __name__ == "__main__":
    log_performance()
    data = extract_data(log_file)
    plot_data(data)