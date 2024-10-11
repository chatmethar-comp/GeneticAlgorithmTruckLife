import requests
import csv
import numpy as np
import folium
from itertools import cycle
from folium.plugins.treelayercontrol import TreeLayerControl
import polyline

colors = ["red", "blue", "green", "purple", "orange", "darkred", "darkblue", "darkgreen", "cadetblue"]
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
    return travel_time_matrix/3600

def get_route_data(coords):
    """
    Fetch route data from OSRM for a set of coordinates.
    
    :param coords: List of tuples representing lat, lon coordinates for the route.
    :return: Encoded polyline geometry of the route or None if an error occurs.
    """
    coord_pairs = ";".join([f"{lon},{lat}" for lat, lon in coords])
    url = f"http://router.project-osrm.org/route/v1/driving/{coord_pairs}?overview=full&geometries=polyline"
    response = requests.get(url)
    data = response.json()
    
    if "routes" in data and data["routes"]:
        route_geometry = data['routes'][0]['geometry']
        return route_geometry
    else:
        return None

def create_map_with_day_truck_routes(warehouse_location, daily_truck_routes, colors):
    """
    Create a folium map with routes filtered by day and truck, each with toggle buttons.
    
    :param daily_truck_routes: Dictionary where keys are days and values are lists of truck routes (each route is a list of coordinates).
    :param colors: List of colors for the routes.
    :return: Folium Map object.
    """
    # Find the first non-empty truck route to initialize the map
    first_route_coords = None
    for day, truck_routes in daily_truck_routes.items():
        for truck_route in truck_routes:
            if truck_route:  # Check if the truck has a non-empty route
                first_route_coords = truck_route[0]  # Get the first coordinate of the first non-empty route
                break
        if first_route_coords:
            break

    if not first_route_coords:
        raise ValueError("No valid truck routes found to initialize the map.")

    # Initialize the map centered at the first valid truck route's first location
    m = folium.Map(location=first_route_coords, zoom_start=6)

    # Cycle through the colors if there are more trucks than colors available
    color_cycle = cycle(colors)

    # Loop through each day and each truck's route
    for day, truck_routes in daily_truck_routes.items():
        for truck_idx, truck_route_coords in enumerate(truck_routes):
            if truck_route_coords:  # Check if the truck has a route for the day
                # Fetch the route data using the get_route_data function
                truck_route_coords.append(warehouse_location)
                truck_route_coords.insert(0,warehouse_location)
                route_data = get_route_data(truck_route_coords)
                
                if route_data:  # If route data is successfully retrieved
                    color = next(color_cycle)  # Get the next color in the cycle

                    # Create a feature group for each truck's route for each day
                    feature_group = folium.FeatureGroup(name=f"Truck {truck_idx + 1}", show=True)

                    # Decode the polyline returned from get_route_data
                    decoded_route = polyline.decode(route_data)  # Use polyline package to decode

                    # Plot the truck's route using the decoded coordinates
                    folium.PolyLine(decoded_route, color=color, weight=2.5, opacity=1).add_to(feature_group)

                    # Add markers for the start and end points of the route
                    if decoded_route:
                        # Marker for the start point
                        for i, coord in enumerate(truck_route_coords):
                            popup_text = f"Checkpoint {i+1}"
                            folium.Marker(coord, popup=popup_text, icon=folium.Icon(color=color)).add_to(feature_group)
                        # Marker for the end point
                    # Add the feature group to the map
                    feature_group.add_to(m)

    # Add layer control to the map to toggle routes
    folium.LayerControl().add_to(m)

    return m

def create_map_tree(warehouse_location,daily_routes,colors):
    m = folium.Map(location=warehouse_location, zoom_start=5)
    color_cycle = cycle(colors)
    ovt = {
        "label": "All Date Route",
        "select_all_check_box": True,
        "children": []
    }
    x = 0
    for date in list(daily_routes.keys()):
        ovt["children"].append({ 
                "label": date,
                "select_all_checkbox": True, 
                "children": []
            })
        a=0
        for i in range(1,len(daily_routes[date])):
            color = next(color_cycle)
            if daily_routes[date][i]:
                ovt["children"][x]["children"].append({ 
                    "label": f"Truck {i}",
                    "select_all_checkbox": True, 
                    "children": []
                })
                daily_routes[date][i].append(warehouse_location)
                daily_routes[date][i].insert(0,warehouse_location)
                route_data = get_route_data(daily_routes[date][i])
                decoded_route = polyline.decode(route_data)
                ovt["children"][x]["children"][a]["children"].append(
                    { "label": f"Route", "layer": folium.PolyLine(decoded_route, color=color, weight=2.5, opacity=1).add_to(m) }
                )
                for j, coord in enumerate(daily_routes[date][i]):
                    popup_text = f"Checkpoint {j+1}"
                    ovt["children"][x]["children"][a]["children"].append(
                    { "label": f"CheckPoint {j}", "layer": folium.Marker(coord, popup=popup_text, icon=folium.Icon(color=color)).add_to(m) }
                    )
                a+=1
        x+=1
    TreeLayerControl(overlay_tree=ovt).add_to(m)
    m.save('m.html')
    return 0

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
#     matrix = get_osrm_travel_time_matrix(warehouse_location,locations, mode='driving')
#     print("Distance Matrix (in meters):")
#     print(matrix)
#     with open('GFG', 'w') as f:
        
#         write = csv.writer(f)
#         write.writerows(matrix)