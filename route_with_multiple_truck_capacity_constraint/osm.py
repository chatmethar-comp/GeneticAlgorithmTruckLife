# import requests
# import folium
# import polyline
# import numpy as np

# def haversine_distance(point1, point2):
#     lat1, lon1 = point1
#     lat2, lon2 = point2
#     R = 6371  # Radius of the Earth in kilometers
#     dlat = np.radians(lat2 - lat1)
#     dlon = np.radians(lon2 - lon1)
#     a = np.sin(dlat / 2) * np.sin(dlat / 2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) * np.sin(dlon / 2)
#     c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
#     return R * c

# p1 = (start_lat,start_lon)
# p2 = (end_lat,end_lon)
# dis = haversine_distance(p1,p2)
# travel_time_hours, distance_km = get_travel_time(start_lat, start_lon, end_lat, end_lon)
# print(f"Travel Time: {travel_time_hours} hours")
# print(f"Distance: {distance_km} km")
# print(f"Distance hav: {dis}")


##############################################################SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS###############################################


import requests
import folium
import polyline
from itertools import cycle  # Import cycle to handle more routes than colors

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

def create_map(all_routes_coords, colors):
    """
    Create a folium map with multiple routes, each in a different color, with toggle buttons.
    
    :param all_routes_coords: List of lists, where each sublist contains tuples of lat, lon coordinates for a route.
    :param colors: List of colors for the routes.
    :return: Folium Map object.
    """
    # Initialize the map centered at the first point of the first route
    m = folium.Map(location=all_routes_coords[0][0], zoom_start=6)
    
    # Cycle through the colors if there are more routes than colors available
    color_cycle = cycle(colors)
    
    # Plot each route on the map with a different color
    for idx, route_coords in enumerate(all_routes_coords):
        route_geometry = get_route_data(route_coords)
        color = next(color_cycle)  # Get the next color in the cycle
        
        # Create a feature group for each route
        feature_group = folium.FeatureGroup(name=f"Route {idx + 1}", show=True)

        if route_geometry:
            decoded_route = polyline.decode(route_geometry)
            folium.PolyLine(decoded_route, color=color, weight=2.5, opacity=1).add_to(feature_group)
            
            # Add markers for each checkpoint in the route
            for i, coord in enumerate(route_coords):
                popup_text = f"Checkpoint {i+1}"
                folium.Marker(coord, popup=popup_text, icon=folium.Icon(color=color)).add_to(feature_group)
        
        # Add the feature group to the map
        feature_group.add_to(m)
    
    # Add layer control to the map to toggle routes
    folium.LayerControl().add_to(m)

    return m

# Define coordinates for multiple routes with checkpoints
# unconnected_routes = [
#     [
#         (13.7563, 100.5018),  # Bangkok
#         (14.3517, 100.5778),
#         (17.0076, 99.8233)   # Ayutthaya
#     ],
#     [
#         (17.0076, 99.8233),  # Sukhothai
#         (18.7883, 98.9853)   # Chiang Mai
#     ],
#     [
#         (18.7883, 98.9853),  # Chiang Mai
#         (19.8869, 99.0303),  # Chiang Rai
#         (20.2331, 99.7275)   # Mae Sai
#     ],
#     # Additional routes can be added here
# ]

# Colors for the routes
colors = ["red", "blue", "green", "purple", "orange", "darkred", "darkblue", "darkgreen", "cadetblue", "pink"]

# Create a map with all routes, each with multiple checkpoints
# route_map = create_map(unconnected_routes, colors)
# route_map.save("unconnected_routes_map_with_checkpoints.html")
# print("Map has been saved as unconnected_routes_map_with_checkpoints.html")



def get_travel_time(coor_s, coor_e):
    start_lat, start_lon, x = coor_s
    end_lat, end_lon, x = coor_e
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=false"
    response = requests.get(url)
    data = response.json()
    
    if "routes" in data:
        duration = data['routes'][0]['duration']  # Duration in seconds
        distance = data['routes'][0]['distance'] 
        return duration / 3600, distance / 1000  
    else:
        return None, None

t1 = get_travel_time((13.7438, 100.5626, 0),(13.72950272,100.7328243, 0))
print(t1)

