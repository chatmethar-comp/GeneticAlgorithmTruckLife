import osm
import time

coordinates = [
    (13.7563, 100.5018, 500),   # Bangkok with weight
    (18.7883, 98.9853, 300),    # Chiang Mai with weight
    (13.3611, 100.9847, 400),   # Samut Prakan with weight
    (7.8804, 98.3923, 250),     # Phuket with weight
    (15.8700, 100.9925, 600),   # Nakhon Sawan with weight
    (17.9647, 102.6291, 200),   # Khon Kaen with weight
    (12.5657, 99.9410, 350),    # Hua Hin with weight
    (16.4419, 102.8329, 450),   # Udon Thani with weight
    (16.2534, 103.2497, 150),   # Kalasin with weight
    (13.8251, 100.4357, 550),   # Nonthaburi with weight
    (14.0359, 100.4798, 550),   # Nakhon Ratchasima with weight
    (13.7364, 100.5370, 500),   # Pathum Thani with weight
    (14.8970, 100.8534, 450),   # Suphan Buri with weight
    (17.0169, 99.5228, 250),    # Lampang with weight
    (15.3161, 102.8291, 300),   # Chaiyaphum with weight
    (16.4536, 102.7665, 200),   # Maha Sarakham with weight
    (14.9514, 102.0608, 400),   # Roi Et with weight
    (18.8036, 99.0824, 350),    # Mae Hong Son with weight
    (13.6692, 100.6627, 300) 
]

def create_weight_graph(coor_list):
    weight_graph = []
    for i in range(len(coor_list)):
        weight_graph.append([])
        for j in range(len(coor_list)):
            weight_graph[i].append(osm.get_travel_time(coor_list[i],coor_list[j]))
    return weight_graph


start_time = time.time()
b = create_weight_graph(coordinates)
for i in range(len(b)):
    print(f"{b[i]}\n")

print(f"Time used{time.time()-start_time}")
