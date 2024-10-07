import requests
import folium
import polyline
from itertools import cycle

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

def extract_coordinates(route_data):
    """
    Extract coordinates from the route data structure.
    
    :param route_data: The list containing dates and sets of coordinates.
    :return: A list of lists, where each sublist contains tuples of lat, lon coordinates.
    """
    all_coords = []
    for day_info in route_data:
        day_coords = []
        for coord_list in day_info[1:]:  # Skip the date at index 0
            if coord_list:  # If the coordinate list is not empty
                # Assuming coord_list contains integers which need to be converted
                for coord in coord_list:
                    # Replace this with the actual logic to convert coord to (lat, lon)
                    # Here we will just use placeholders for lat and lon
                    # For example, this can be changed to (coord, coord) if you have a method
                    # to convert these integers into latitude and longitude
                    lat = coord + 10  # Replace with actual lat conversion
                    lon = coord + 20  # Replace with actual lon conversion
                    day_coords.append((lat, lon))  # Add as (lat, lon) tuple
        if day_coords:
            all_coords.append(day_coords)
    return all_coords

def create_map(route_data, colors):
    """
    Create a folium map with multiple routes, each in a different color, with toggle buttons.
    
    :param route_data: The list containing dates and sets of coordinates.
    :param colors: List of colors for the routes.
    :return: Folium Map object.
    """
    # Extract coordinates for all days
    all_routes_coords = extract_coordinates(route_data)

    if not all_routes_coords:
        raise ValueError("No coordinates found in the route data.")

    # Initialize the map centered at the first point of the first route
    m = folium.Map(location=all_routes_coords[0][0], zoom_start=6)

    # Cycle through the colors if there are more routes than colors available
    color_cycle = cycle(colors)

    # Plot each route on the map with a different color
    for idx, route_coords in enumerate(all_routes_coords):
        route_geometry = get_route_data(route_coords)
        color = next(color_cycle)  # Get the next color in the cycle

        # Create a feature group for each route
        feature_group = folium.FeatureGroup(name=f"Route {idx + 1} - Date: {route_data[idx][0]}", show=True)

        if route_geometry:
            decoded_route = polyline.decode(route_geometry)
            folium.PolyLine(decoded_route, color=color, weight=2.5, opacity=1).add_to(feature_group)
            
            # Add markers for each checkpoint in the route
            for i, coord in enumerate(route_coords):
                popup_text = f"Checkpoint {i+1} - Date: {route_data[idx][0]}"
                folium.Marker(coord, popup=popup_text, icon=folium.Icon(color=color)).add_to(feature_group)
        
        # Add the feature group to the map
        feature_group.add_to(m)

    # Add layer control to the map to toggle routes
    folium.LayerControl().add_to(m)

    return m

# Example route data and order_data (simplified for testing purposes)
route = [[20240201, [], [9], [], [], []], [20240202, [], [26], [], [], []], [20240203, [74, 93], [78], [70, 29], [96], []], 
         [20240204, [80, 83], [61, 6, 89], [94, 17], [84], []]]

order_data = [[1, 20240204, 14.02644447, 100.6919272, 20240209, 20240212, 500], 
              [2, 20240201, 13.96554796, 100.5245274, 20240204, 20240208, 200], 
              [3, 20240205, 14.1010167, 100.5554815, 20240210, 20240211, 400]]

# Colors for routes
colors = ["red", "blue", "green"]

# Create the map
m = create_map(route, colors)

# Save the map to an HTML file
m.save("route_map.html")
