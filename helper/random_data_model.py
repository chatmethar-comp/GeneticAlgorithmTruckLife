import random

def random_data_model(
    num_locations=17,
    num_vehicles=4,
    vehicle_capacities=None,
    max_distance=1000,
    max_time=15,
    max_demand=8
):
    if vehicle_capacities is None:
        vehicle_capacities = [random.randint(10, 20) for _ in range(num_vehicles)]
    
    data = {}
    data["distance_matrix"] = [
        [0 if i == j else random.randint(1, max_distance) for j in range(num_locations)]
        for i in range(num_locations)
    ]
    data["time_matrix"] = [
        [0 if i == j else random.randint(1, max_time) for j in range(num_locations)]
        for i in range(num_locations)
    ]
    data["time_windows"] = [
        (random.randint(0, 5), random.randint(6, 18)) for _ in range(num_locations)
    ]
    data["time_windows"][0] = (0, 5)  # Depot
    data["demands"] = [0] + [random.randint(1, max_demand) for _ in range(num_locations - 1)]
    data["vehicle_capacities"] = vehicle_capacities
    data["num_vehicles"] = num_vehicles
    data["depot"] = 0
    return data

"""
random_data_model(num_locations=5, num_vehicles=2)

result: 
{
    'distance_matrix': [[0, 24, 936, 861, 107], 
                        [729, 0, 882, 786, 557], 
                        [611, 272, 0, 641, 114], 
                        [786, 562, 166, 0, 584], 
                        [83, 354, 751, 142, 0]], 
    'time_matrix': [[0, 4, 15, 5, 9], 
                    [14, 0, 15, 4, 4], 
                    [1, 11, 0, 8, 4], 
                    [14, 14, 9, 0, 4], 
                    [1, 2, 15, 2, 0]], 
    'time_windows': [(0, 5), 
                    (2, 13), 
                    (0, 8), 
                    (5, 12), 
                    (4, 10)], 
    'demands': [0, 3, 6, 1, 6], 
    'vehicle_capacities': [15, 10], 
    'num_vehicles': 2, 
    'depot': 0
}
"""
    
def generate_test_cases(num_cases=5):
    test_cases = []
    for i in range(num_cases):
        num_vehicles = i
        vehicle_capacities = [random.randint(10, 20) for _ in range(num_vehicles)]
        test_case = random_data_model(num_locations=i+3, num_vehicles=num_vehicles, vehicle_capacities=vehicle_capacities)
        test_cases.append(test_case)
    return test_cases


"""
generate_test_cases(3)

[
    {
        'distance_matrix': [[0, 495, 367], 
                         [538, 0, 987], 
                         [434, 625, 0]], 
        'time_matrix': [[0, 7, 9], 
                        [8, 0, 8], 
                        [14, 8, 0]], 
        'time_windows': [
            (0, 5), 
            (1, 12), 
            (5, 11)
        ], 
        'demands': [0, 7, 6], 
        'vehicle_capacities': [15, 19, 20, 13], 
        'num_vehicles': 4, 
        'depot': 0
     }, 
    {
        'distance_matrix': [[0, 143, 967, 505], 
                            [836, 0, 648, 905], 
                            [660, 184, 0, 352], 
                            [571, 548, 815, 0]], 
        'time_matrix': [[0, 15, 11, 5], 
                        [8, 0, 12, 4], 
                        [12, 9, 0, 2], 
                        [12, 1, 4, 0]], 
        'time_windows': [(0, 5), (5, 18), (3, 16), (3, 6)], 
        'demands': [0, 7, 4, 6], 
        'vehicle_capacities': [10, 19, 15], 
        'num_vehicles': 3, 
        'depot': 0
    }, 
    {
        'distance_matrix': [[0, 358, 690, 859, 120], 
                            [797, 0, 418, 51, 283], 
                            [260, 231, 0, 741, 398], 
                            [586, 790, 749, 0, 820], 
                            [102, 441, 951, 725, 0]], 
        'time_matrix': [[0, 7, 7, 12, 10], 
                        [6, 0, 13, 5, 5], 
                        [2, 3, 0, 3, 15], 
                        [14, 14, 13, 0, 6], 
                        [7, 11, 15, 9, 0]], 
        'time_windows': [(0, 5), (2, 18), (5, 16), (1, 8), (4, 7)], 
        'demands': [0, 5, 8, 7, 3], 
        'vehicle_capacities': [12, 17, 13, 17, 19, 10], 
        'num_vehicles': 6, 
        'depot': 0
    }
]
"""
