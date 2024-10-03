import requests
import folium
import polyline
from itertools import cycle 

colors = ["red", "blue", "green", "purple", "orange", "darkred", "darkblue", "darkgreen", "cadetblue", "pink"]

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


