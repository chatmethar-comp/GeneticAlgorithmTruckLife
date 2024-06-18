# pip install googlemaps
import googlemaps
from datetime import datetime

API_KEY = 'AIzaSyC4SRkYCBiobk42kWn-WhhqEYAYUv8_WeI'
gmaps = googlemaps.Client(key=API_KEY)

def get_travel_time(start_coords, dest_coords):
    # Get directions
    directions_result = gmaps.directions(start_coords,
                                         dest_coords,
                                         mode="driving",
                                         departure_time=datetime.now())
    
    # Extract travel time from directions_result
    if directions_result:
        travel_time = directions_result[0]['legs'][0]['duration']['text']
        return travel_time
    else:
        return None

if __name__ == "__main__":
    # Input starting location
    start_lat = float(input("Enter the starting latitude: "))
    start_lng = float(input("Enter the starting longitude: "))
    start_coords = (start_lat, start_lng)
    
    # Input destination location
    dest_lat = float(input("Enter the destination latitude: "))
    dest_lng = float(input("Enter the destination longitude: "))
    dest_coords = (dest_lat, dest_lng)
    
    travel_time = get_travel_time(start_coords, dest_coords)
    
    if travel_time:
        print(f"The travel time from {start_coords} to {dest_coords} is {travel_time}.")
    else:
        print("Could not find travel time for the given locations.")