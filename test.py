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

# my_list = [1,2,3,4,1,5,6,1]
# if 9 in my_list:
#     print("aaaaa")
# indices = [i for i, x in enumerate(my_list) if x == 0]
# print(indices)



{20240201: {'Truck1': {'weight': 1900, 'capacity': [1900], 'order': []}, 
            'Truck2': {'weight': 1900, 'capacity': [1200], 'order': [0]}, 
            'Truck3': {'weight': 1900, 'capacity': [1100, 3000], 'order': [9]}, 
            'Truck4': {'weight': 1100, 'capacity': [1100], 'order': []}, 
            'Outsourcing': []}, 
 20240202: {'Truck1': {'weight': 1900, 'capacity': [1900, 2600], 'order': []}, 
            'Truck2': {'weight': 1900, 'capacity': [900, 1200], 'order': [0, 74, 0]}, 
            'Truck3': {'weight': 1900, 'capacity': [600, 1000], 'order': [26, 70, 0, 0, 29]}, 
            'Truck4': {'weight': 1100, 'capacity': [700, 2200], 'order': []}, 
            'Outsourcing': []}, 
 20240203: {'Truck1': {'weight': 1900, 'capacity': [500], 'order': [93, 96, 51]}, 
            'Truck2': {'weight': 1900, 'capacity': [1300], 'order': [83]}, 
            'Truck3': {'weight': 1900, 'capacity': [1900], 'order': []}, 
            'Truck4': {'weight': 1100, 'capacity': [1100], 'order': []}, 
            'Outsourcing': []}, 
 20240204: {'Truck1': {'weight': 1900, 'capacity': [0, 2400, 1500, 1900], 'order': [17, 0, 46, 0, 80, 0]}, 
            'Truck2': {'weight': 1900, 'capacity': [500, 1900, 1900], 'order': [89, 32, 0, 78, 0]}, 
            'Truck3': {'weight': 1900, 'capacity': [100, 1000, 1900], 'order': [33, 84, 0, 0, 2, 0]}, 
            'Truck4': {'weight': 1100, 'capacity': [500, 2400], 'order': []}, 
            'Outsourcing': []}, 
 20240205: {'Truck1': {'weight': 1900, 'capacity': [200, 1900], 'order': [41, 94, 0]}, 
            'Truck2': {'weight': 1900, 'capacity': [500, 2300], 'order': [0, 79]}, 
            'Truck3': {'weight': 1900, 'capacity': [200, 800], 'order': [6, 49, 16, 0, 0, 56]}, 
            'Truck4': {'weight': 1100, 'capacity': [1100, 1800], 'order': []}, 
            'Outsourcing': []}, 
 20240206: {'Truck1': {'weight': 1900, 'capacity': [0], 'order': [60, 47, 30]}, 'Truck2': {'weight': 1900, 'capacity': [0], 'order': [10, 14, 98]}, 'Truck3': {'weight': 1900, 'capacity': [300], 'order': [68, 55]}, 'Truck4': {'weight': 1100, 'capacity': [0], 'order': [86, 54]}, 'Outsourcing': []}, 
 20240207: {'Truck1': {'weight': 1900, 'capacity': [0, 2700], 'order': [88, 27, 0]}, 'Truck2': {'weight': 1900, 'capacity': [0, 1900], 'order': [57, 62, 61, 0]}, 'Truck3': {'weight': 1900, 'capacity': [200, 1100], 'order': [22, 8, 0, 53]}, 'Truck4': {'weight': 1100, 'capacity': [100, 1100], 'order': [76, 0]}, 'Outsourcing': [81, 19]}, 
 20240208: {'Truck1': {'weight': 1900, 'capacity': [0, 2300], 'order': [13, 34, 0]}, 'Truck2': {'weight': 1900, 'capacity': [100, 1900], 'order': [11, 45, 0, 91]}, 'Truck3': {'weight': 1900, 'capacity': [100, 1900], 'order': [67, 82, 21, 0]}, 'Truck4': {'weight': 1100, 'capacity': [200, 700, 1100], 'order': [39, 0, 64, 0]}, 'Outsourcing': []},
 20240209: {'Truck1': {'weight': 1900, 'capacity': [200], 'order': [85, 42, 97]}, 'Truck2': {'weight': 1900, 'capacity': [200], 'order': [92, 59]}, 'Truck3': {'weight': 1900, 'capacity': [300], 'order': [52, 35]}, 'Truck4': {'weight': 1100, 'capacity': [0], 'order': [58, 23]}, 'Outsourcing': [18]}, 
 20240210: {'Truck1': {'weight': 1900, 'capacity': [0, 0, 1700, 500, 1300, 1300, 1700, 1900], 'order': [24, 20, 87, 0, 4, 65, 0, 25, 0, 0, 44, 0, 75, 0, 71, 0, 37, 0]}, 'Truck2': {'weight': 1900, 'capacity': [300, 4200], 'order': []}, 'Truck3': {'weight': 1900, 'capacity': [100, 2300, 2100], 'order': [90, 3, 0, 0]}, 'Truck4': {'weight': 1100, 'capacity': [0, 2200], 'order': [0]}, 'Outsourcing': []}, 
 20240211: {'Truck1': {'weight': 1900, 'capacity': [0, 1900, 1900], 'order': [95, 36, 0, 73, 0]}, 
            'Truck2': {'weight': 1900, 'capacity': [0, 1200], 'order': [1, 99, 69, 0, 0]}, 
            'Truck3': {'weight': 1900, 'capacity': [300, 1600], 'order': [12, 0]}, 
            'Truck4': {'weight': 1100, 'capacity': [0, 1800], 'order': [72]}, 
            'Outsourcing': []}, 
 20240212: {'Truck1': {'weight': 1900, 'capacity': [300, 900, 1900], 'order': [77, 31, 0, 7, 0]}, 'Truck2': {'weight': 1900, 'capacity': [0, 3800], 'order': [0]}, 'Truck3': {'weight': 1900, 'capacity': [100, 1000, 3500], 'order': [40, 5, 50, 0]}, 'Truck4': {'weight': 1100, 'capacity': [300, 400], 'order': [38, 0, 0]}, 'Outsourcing': []}, 
 20240213: {'Truck1': {'weight': 1900, 'capacity': [1900], 'order': []}, 'Truck2': {'weight': 1900, 'capacity': [700, 1900], 'order': [15, 28, 0]}, 'Truck3': {'weight': 1900, 'capacity': [1900], 'order': []}, 'Truck4': {'weight': 1100, 'capacity': [400, 1100], 'order': [43, 0]}, 'Outsourcing': []}, 
 20240214: {'Truck1': {'weight': 1900, 'capacity': [1200, 1900], 'order': [63, 0]}, 'Truck2': {'weight': 1900, 'capacity': [1900], 'order': []}, 'Truck3': {'weight': 1900, 'capacity': [1900], 'order': []}, 'Truck4': {'weight': 1100, 'capacity': [300, 1100], 'order': [66, 0]}, 'Outsourcing': []}, 
 20240215: {'Truck1': {'weight': 1900, 'capacity': [1900], 'order': []}, 'Truck2': {'weight': 1900, 'capacity': [1900], 'order': []}, 'Truck3': {'weight': 1900, 'capacity': [1900], 'order': []}, 'Truck4': {'weight': 1100, 'capacity': [1100], 'order': []}, 'Outsourcing': []}, 
 20240216: {'Truck1': {'weight': 1900, 'capacity': [1900], 'order': []}, 'Truck2': {'weight': 1900, 'capacity': [1900], 'order': []}, 'Truck3': {'weight': 1900, 'capacity': [1900], 'order': []}, 'Truck4': {'weight': 1100, 'capacity': [1100], 'order': []}, 'Outsourcing': []}}

a = [5,3,2,1]
del a[0]
print(a)