import requests
# import csv
import numpy as np

# Function to generate OSRM distance matrix
def get_osrm_distance_matrix(warehouse_location,order_data_w, mode='driving'):
    """
    Parameters:
    - coordinates: List of (latitude, longitude) tuples.
    - mode: Mode of transportation ('driving', 'walking', 'cycling').
    Returns:
    - distance_matrix: A NumPy array with pairwise distances between locations.
    """
    coordinates=[[item[2], item[3]] for item in order_data_w]
    coordinates.insert(0,warehouse_location)
    # Convert coordinates to a format required by OSRM
    coord_string = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
    # Define the OSRM Table service URL
    url = f"http://router.project-osrm.org/table/v1/{mode}/{coord_string}?annotations=distance"
    # Send the request to OSRM API
    response = requests.get(url)
    # Check if the response is successful
    if response.status_code != 200:
        raise Exception(f"OSRM request failed with status code {response.status_code}: {response.text}")
    # Parse the JSON response
    osrm_data = response.json()
    # Extract the distance matrix
    distance_matrix = np.array(osrm_data['distances'])/1000
    return distance_matrix                  

def get_osrm_travel_time_matrix(warehouse_location,order_data_w, mode='driving'):
    """
    Parameters:
    - coordinates: List of (latitude, longitude) tuples.
    - mode: Mode of transportation ('driving', 'walking', 'cycling').
    Returns:
    - travel_time_matrix: A NumPy array with pairwise travel times between locations.
    """
    coordinates=[[item[2], item[3]] for item in order_data_w]
    coordinates.insert(0,warehouse_location)
    # Convert coordinates to a format required by OSRM
    coord_string = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
    # Define the OSRM Table service URL with annotations=duration for travel time
    url = f"http://router.project-osrm.org/table/v1/{mode}/{coord_string}?annotations=duration"
    # Send the request to OSRM API
    response = requests.get(url)
    # Check if the response is successful
    if response.status_code != 200:
        raise Exception(f"OSRM request failed with status code {response.status_code}: {response.text}")
    # Parse the JSON response
    osrm_data = response.json()
    # Extract the travel time matrix (in seconds)
    travel_time_matrix = np.array(osrm_data['durations'])
    return travel_time_matrix


# Test Here!!!!!!!!
# if __name__ == "__main__":
#     locations = [[1, 20240204, 14.02644447, 100.6919272, 20240209, 20240212, 500], 
#                  [2, 20240201, 13.96554796, 100.5245274, 20240204, 20240208, 200], 
#                  [3, 20240205, 14.1010167, 100.5554815, 20240210, 20240211, 400], 
#                  [4, 20240205, 14.02366024, 100.7877536, 20240209, 20240212, 900], 
#                  [5, 20240206, 13.79198072, 100.2948867, 20240211, 20240212, 300], 
#                  [6, 20240203, 14.05326442, 100.7640006, 20240204, 20240208, 1100], 
#                  [7, 20240206, 13.68854597, 100.9852419, 20240208, 20240212, 1000], 
#                  [8, 20240204, 13.60314233, 100.2348606, 20240207, 20240209, 700], 
#                  [9, 20240201, 14.11163469, 100.689131, 20240201, 20240201, 400], 
#                  [10, 20240204, 13.70892926, 100.9235944, 20240206, 20240207, 300], 
#                  [11, 20240205, 14.0273532, 100.1962857, 20240208, 20240208, 400], 
#                  [12, 20240203, 14.03560299, 100.8545961, 20240208, 20240211, 1000], 
#                  [13, 20240202, 13.58207661, 100.6456153, 20240207, 20240208, 900], 
#                  [14, 20240201, 13.59317788, 100.9298951, 20240205, 20240210, 900], 
#                  [15, 20240206, 13.58328929, 100.8222069, 20240208, 20240213, 1000], 
#                  [16, 20240201, 13.56603353, 100.4366799, 20240203, 20240205, 300], 
#                  [17, 20240202, 14.05955278, 100.461816, 20240204, 20240204, 900], 
#                  [18, 20240204, 13.74508088, 100.4805234, 20240209, 20240210, 1000], 
#                  [19, 20240206, 13.63464473, 100.5075653, 20240206, 20240210, 1100], 
#                  [20, 20240203, 13.56140732, 100.9938387, 20240206, 20240210, 700]]
#     warehouse_location = [13.7438, 100.5626]
#     # Generate distance matrix for driving
#     matrix = get_osrm_distance_matrix(warehouse_location,locations, mode='driving')
    
#     # Print the matrix
#     print("Distance Matrix (in meters):")
#     print(matrix)

#     with open('GFG', 'w') as f:
        
#         # using csv.writer method from CSV package
#         write = csv.writer(f)
        
#         write.writerows(matrix)