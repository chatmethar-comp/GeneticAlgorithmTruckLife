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

# def get_travel_time(start_lat, start_lon, end_lat, end_lon):
#     url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=false"
#     response = requests.get(url)
#     data = response.json()
    
#     if "routes" in data:
#         duration = data['routes'][0]['duration']  # Duration in seconds
#         distance = data['routes'][0]['distance'] 
#         return duration / 3600, distance / 1000  
#     else:
#         return None, None

# # Example usage
# start_lat, start_lon = 13.7563, 100.5018
# end_lat, end_lon = 18.7883, 98.9853 

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

def get_route_data(coords):
    coord_pairs = ";".join([f"{lon},{lat}" for lat, lon in coords])
    url = f"http://router.project-osrm.org/route/v1/driving/{coord_pairs}?overview=full&geometries=polyline"
    response = requests.get(url)
    data = response.json()
    
    if "routes" in data:
        route_geometry = data['routes'][0]['geometry']
        return route_geometry
    else:
        return None

def create_map(route_geometries, coords_list, colors):
    # Initialize the map centered at the first point of the first route
    m = folium.Map(location=coords_list[0][0], zoom_start=6)
    
    # Plot each route on the map with a different color
    for route_geometry, coords, color in zip(route_geometries, coords_list, colors):
        if route_geometry:
            route_coords = polyline.decode(route_geometry)
            folium.PolyLine(route_coords, color=color, weight=2.5, opacity=1).add_to(m)
            # Add markers for start and end points of each route
            folium.Marker(coords[0], popup="Start").add_to(m)
            folium.Marker(coords[-1], popup="End").add_to(m)
    
    return m

# Define coordinates for two unconnected routes
coords_route1 = [
    (13.7563, 100.5018),  # Bangkok
    (14.3517, 100.5778)   # Ayutthaya
]

coords_route2 = [
    (17.0076, 99.8233),   # Sukhothai
    (18.7883, 98.9853)    # Chiang Mai
]

# Colors for the routes
colors = ["red", "green"]

# Get route data for both routes
route_geometry1 = get_route_data(coords_route1)
route_geometry2 = get_route_data(coords_route2)

# Create a map with both routes in different colors
route_map = create_map([route_geometry1, route_geometry2], [coords_route1, coords_route2], colors)
route_map.save("unconnected_routes_map_colored.html")
print("Map has been saved as unconnected_routes_map_colored.html")
