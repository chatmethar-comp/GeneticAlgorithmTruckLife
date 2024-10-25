num=0
desired_delivery_date = [20240201,20240210,20240211,20240214]
a ={20240201: {'Truck1': {'weight': 1900, 'order': []}, 'Truck2': {'weight': 1500, 'order': [9]}, 'Truck3': {'weight': 1900, 'order': []}, 'Truck4': {'weight': 1100, 'order': []}, 'Outsourcing': []}, 20240202: {'Truck1': {'weight': 600, 'order': [26, 70]}, 'Truck2': {'weight': 1900, 'order': []}, 'Truck3': {'weight': 1900, 'order': []}, 'Truck4': {'weight': 1100, 'order': []}, 'Outsourcing': []}, 20240203: {'Truck1': {'weight': 1900, 'order': []}, 'Truck2': {'weight': 400, 'order': [33, 29, 32, 96]}, 'Truck3': {'weight': 300, 'order': [74, 83]}, 'Truck4': {'weight': 200, 'order': [78]}, 'Outsourcing': []}, 20240204: {'Truck1': {'weight': 700, 'order': [93, 46]}, 'Truck2': {'weight': 0, 'order': [17, 89, 80, 16]}, 'Truck3': {'weight': 0, 'order': [84, 55, 51]}, 'Truck4': {'weight': 1100, 'order': []}, 'Outsourcing': []}, 20240205: {'Truck1': {'weight': 0, 'order': [34, 49, 79]}, 'Truck2': {'weight': 0, 'order': [85, 56, 94]}, 'Truck3': {'weight': 0, 'order': [41, 6]}, 'Truck4': {'weight': 200, 'order': [14]}, 'Outsourcing': []}, 20240206: {'Truck1': {'weight': 0, 'order': [10, 98, 48]}, 'Truck2': {'weight': 100, 'order': [22, 62, 61]}, 'Truck3': {'weight': 0, 'order': [86, 73, 54, 30]}, 'Truck4': {'weight': 0, 'order': [88, 27]}, 'Outsourcing': []}, 20240207: {'Truck1': {'weight': 0, 'order': [68, 53]}, 'Truck2': {'weight': 200, 'order': [92, 91]}, 'Truck3': {'weight': 0, 'order': [57, 60, 2]}, 'Truck4': {'weight': 200, 'order': [13]}, 'Outsourcing': []}, 20240208: {'Truck1': {'weight': 0, 'order': [58, 23, 21]}, 'Truck2': {'weight': 100, 'order': [81, 39]}, 'Truck3': {'weight': 200, 'order': [67, 76]}, 'Truck4': {'weight': 0, 'order': [11, 82, 64]}, 'Outsourcing': []}, 20240209: {'Truck1': {'weight': 200, 'order': [45, 8, 25]}, 'Truck2': {'weight': 0, 'order': [24, 59, 18]}, 'Truck3': {'weight': 100, 'order': [20, 42, 97]}, 'Truck4': {'weight': 
200, 'order': [87]}, 'Outsourcing': []}, 20240210: {'Truck1': {'weight': 0, 'order': [52, 47]}, 'Truck2': {'weight': 0, 'order': [63, 37, 65]}, 'Truck3': {'weight': 200, 'order': [71, 19]}, 'Truck4': {'weight': 100, 'order': [12]}, 'Outsourcing': []}, 
20240211: {'Truck1': {'weight': 400, 'order': [4, 75]}, 'Truck2': {'weight': 100, 'order': [95, 90]}, 'Truck3': {'weight': 100, 'order': [72, 44]}, 'Truck4': {'weight': 100, 'order': [35, 3]}, 'Outsourcing': []}, 20240212: {'Truck1': {'weight': 0, 'order': [1, 5, 31]}, 'Truck2': {'weight': 400, 'order': [38, 99]}, 'Truck3': {'weight': 200, 'order': [77, 36, 43]}, 'Truck4': {'weight': 100, 'order': [7]}, 'Outsourcing': []}, 20240213: {'Truck1': {'weight': 0, 'order': [40, 69, 28]}, 'Truck2': {'weight': 900, 'order': [15]}, 'Truck3': {'weight': 1900, 'order': []}, 'Truck4': {'weight': 1100, 'order': []}, 'Outsourcing': []}, 
20240214: {'Truck1': {'weight': 1400, 'order': [50]}, 'Truck2': {'weight': 1900, 'order': []}, 'Truck3': {'weight': 1900, 'order': []}, 'Truck4': {'weight': 1100, 'order': []}, 'Outsourcing': []}, 20240215: {'Truck1': {'weight': 1900, 'order': []}, 'Truck2': {'weight': 1900, 'order': []}, 'Truck3': {'weight': 1900, 'order': []}, 'Truck4': {'weight': 1100, 'order': []}, 'Outsourcing': []}, 20240216: {'Truck1': {'weight': 1900, 'order': []}, 'Truck2': {'weight': 1900, 'order': []}, 'Truck3': {'weight': 1900, 'order': []}, 'Truck4': {'weight': 300, 'order': [66]}, 'Outsourcing': []}}


# for date in a.keys():
#     for i in range(1, 5):
#         for order in a[date][f"Truck{i}"]["order"]:
#             num+=1
#     for order in a[date]["Outsourcing"]:
#         num+=1
# print(num)

import numpy as np
values = np.array([1,2,3,1,2,4,5,6,3,2,1])
print(values)
searchval = 3
ii = np.where(values == searchval)[0]
print(ii)