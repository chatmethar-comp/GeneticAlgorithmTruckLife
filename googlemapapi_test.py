# pip install googlemaps
import googlemaps
from datetime import datetime
import csv

a = [[(0,0),(5,20),(6,20)],
     [(5,20),(0,0),(4,20)],
     [(6,20),(4,20),(0,0)]]

API_KEY = 'AIzaSyC4SRkYCBiobk42kWn-WhhqEYAYUv8_WeI'
gmaps = googlemaps.Client(key=API_KEY)
start_coords = (13.743833, 100.562694)

def get_travel_time_and_distance(start_coords,dest_coords):
    directions_result = gmaps.directions(start_coords,
                                         dest_coords,
                                         mode="driving",
                                         departure_time=datetime.now())
    
    if directions_result:
        leg = directions_result[0]['legs'][0]
        travel_time = leg['duration']['value']  # seconds
        distance = leg['distance']['value']  # meters
        return (distance, travel_time)
    else:
        return (0, 0)

def read_locations_from_csv(file_path):
    locations = []
    locations.append(start_coords)
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            locations.append((float(row['Lat']), float(row['Lon'])))
    return locations

def create_distance_matrix(locations):
    n = len(locations)
    distance_matrix = [[(0, 0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                distance_matrix[i][j] = get_travel_time_and_distance(locations[i], locations[j])
    return distance_matrix

if __name__ == "__main__":
    file_path = 'locations.csv'
    locations = read_locations_from_csv(file_path)
    distance_matrix = create_distance_matrix(locations)
    
    for row in distance_matrix:
        print(row)