import copy
# num=0
# desired_delivery_date = [20240201,20240210,20240211,20240214]
# a ={20241001: {'Truck1': {'weight': 1000, 'capacity': [0, 200, 1000], 'order': [454, 192, 0, 488, 0]}, 'Truck2': {'weight': 1000, 'capacity': [0, 0, 800, 1000], 'order': [347, 356, 0, 389, 364, 0, 104, 0]}, 'Truck3': {'weight': 1000, 'capacity': [0, 0, 300, 1000], 'order': [136, 431, 0, 67, 545, 0, 231, 177, 0]}, 'Truck4': {'weight': 1000, 'capacity': [0, 200, 1000], 'order': [165, 565, 0, 475, 0]}, 'Truck5': {'weight': 1000, 'capacity': [0, 1000], 'order': [271, 202, 0]}, 'Truck6': {'weight': 1000, 'capacity': [0, 200, 1000], 'order': [280, 355, 0, 518, 0]}, 'Truck7': {'weight': 2000, 'capacity': [300, 1500, 2000], 'order': [325, 172, 6, 593, 0, 252, 0]}, 'Truck8': {'weight': 2000, 'capacity': [0, 2000], 'order': [315, 242, 92, 480, 0]}, 'Truck9': {'weight': 2000, 'capacity': [0, 1000, 2000], 'order': [22, 173, 446, 0, 214, 486, 324, 0]}, 'Truck10': {'weight': 2000, 'capacity': [300, 2000], 'order': [386, 75, 124, 414, 0]}, 'Outsourcing': [352, 441, 540, 283, 483, 97, 294, 455, 589, 548, 549]}, 20241002: {'Truck1': {'weight': 1000, 'capacity': [0, 300, 1000], 'order': [500, 73, 0, 181, 400, 0]}, 'Truck2': {'weight': 1000, 'capacity': [0, 500, 1000], 'order': [228, 249, 0, 360, 0]}, 'Truck3': {'weight': 1000, 'capacity': [0, 1000], 'order': [167, 532, 0]}, 'Truck4': {'weight': 1000, 'capacity': [0, 500, 1000], 'order': [504, 188, 0, 372, 0]}, 'Truck5': {'weight': 1000, 'capacity': [100, 0, 1000], 'order': [90, 48, 270, 0, 560, 84, 0]}, 'Truck6': {'weight': 1000, 
# 'capacity': [100, 1200], 'order': [53, 260, 0]}, 'Truck7': {'weight': 2000, 'capacity': [0, 2000], 'order': [264, 348, 599, 59, 0]}, 'Truck8': {'weight': 2000, 'capacity': [0, 1500, 1500, 2000], 'order': [261, 154, 290, 416, 0, 244, 0, 211, 0]}, 'Truck9': {'weight': 2000, 'capacity': [0, 0, 2000], 'order': [521, 259, 152, 334, 0, 503, 374, 105, 333, 0]}, 'Truck10': {'weight': 2000, 'capacity': [0, 2000], 'order': [159, 522, 393, 351, 0]}, 'Outsourcing': [459, 418, 387, 561, 550, 509, 435, 123, 163, 508, 287, 563, 411, 426, 591, 443, 344, 23, 556, 498, 528, 450, 142, 547, 485, 253]}, 20241003: {'Truck1': {'weight': 1000, 'capacity': [0, 0, 200, 1000], 'order': [536, 115, 0, 232, 320, 0, 538, 0]}, 'Truck2': {'weight': 1000, 'capacity': [100, 
# 200, 1000], 'order': [146, 95, 305, 0, 600, 0]}, 'Truck3': {'weight': 1000, 'capacity': [100, 100, 1000], 'order': [21, 309, 
# 187, 0, 382, 103, 39, 0]}, 'Truck4': {'weight': 1000, 'capacity': [0, 0, 1000], 'order': [531, 110, 0, 361, 335, 0]}, 'Truck5': {'weight': 1000, 'capacity': [0, 100, 300, 1000], 'order': [327, 341, 0, 350, 135, 36, 0, 243, 24, 0]}, 'Truck6': {'weight': 1000, 'capacity': [0, 0, 800, 1000], 'order': [112, 415, 0, 553, 190, 0, 8, 0]}, 'Truck7': {'weight': 2000, 'capacity': [100, 2000], 'order': [28, 47, 96, 544, 371, 0]}, 'Truck8': {'weight': 2000, 'capacity': [100, 2500], 'order': [25, 116, 14, 555, 0]}, 'Truck9': {'weight': 2000, 'capacity': [0, 2000], 'order': [64, 69, 551, 412, 0]}, 'Truck10': {'weight': 2000, 'capacity': [0, 2000], 'order': [492, 107, 298, 269, 0]}, 'Outsourcing': [539, 444, 224, 491, 523, 421, 35, 403, 467, 590, 401, 216, 207, 517, 533, 296, 419, 60, 128, 213, 19, 44, 13, 46, 221, 437, 597, 462, 542, 428, 338, 217]}, 20241004: {'Truck1': {'weight': 1000, 'capacity': [100, 0, 500, 1000], 'order': [55, 394, 175, 0, 495, 61, 0, 201, 0]}, 'Truck2': {'weight': 1000, 'capacity': [100, 0, 800, 1000], 'order': [317, 54, 143, 0, 397, 254, 0, 93, 0]}, 'Truck3': {'weight': 1000, 'capacity': [0, 500, 200, 1000], 'order': [10, 496, 0, 300, 0, 566, 0]}, 'Truck4': {'weight': 1000, 'capacity': [0, 1000], 'order': [138, 487, 0]}, 'Truck5': {'weight': 1000, 'capacity': [100, 0, 0, 1000], 'order': [12, 166, 245, 0, 572, 169, 0, 423, 16, 0]}, 'Truck6': 
# {'weight': 1000, 'capacity': [0, 0, 1000], 'order': [9, 101, 129, 40, 193, 0, 179, 514, 0]}, 'Truck7': {'weight': 2000, 'capacity': [200, 2000, 2000], 'order': [32, 66, 238, 150, 265, 0, 155, 0]}, 'Truck8': {'weight': 2000, 'capacity': [0, 400, 700, 
# 2000], 'order': [383, 390, 222, 385, 0, 478, 457, 0, 376, 583, 0]}, 'Truck9': {'weight': 2000, 'capacity': [100, 2000], 'order': [4, 145, 323, 158, 424, 0]}, 'Truck10': {'weight': 2000, 'capacity': [0, 2000], 'order': [161, 284, 557, 366, 0]}, 'Outsourcing': [578, 468, 223, 268, 367, 330, 535, 422, 170, 98, 137, 391, 429, 577, 473, 195, 427, 481, 507, 513, 438, 552, 176, 407, 285, 109, 395, 465, 203, 484, 464, 236, 520, 493, 204, 365]}, 20241005: {'Truck1': {'weight': 1000, 'capacity': [0, 400, 
# 200, 1000], 'order': [43, 476, 0, 147, 5, 196, 0, 402, 0]}, 'Truck2': {'weight': 1000, 'capacity': [0, 1000], 'order': [113, 
# 117, 183, 168, 106, 0]}, 'Truck3': {'weight': 1000, 'capacity': [0, 0, 1000], 'order': [186, 458, 0, 592, 102, 0]}, 'Truck4': {'weight': 1000, 'capacity': [0, 500, 1000], 'order': [266, 379, 0, 337, 0]}, 'Truck5': {'weight': 1000, 'capacity': [100, 1000], 'order': [17, 392, 118, 0]}, 'Truck6': {'weight': 1000, 'capacity': [0, 0, 1000], 'order': [171, 516, 0, 11, 526, 0]}, 
# 'Truck7': {'weight': 2000, 'capacity': [100, 2000], 'order': [139, 218, 153, 251, 206, 0]}, 'Truck8': {'weight': 2000, 'capacity': [100, 1800, 2000], 'order': [162, 534, 52, 332, 83, 0, 80, 0]}, 'Truck9': {'weight': 2000, 'capacity': [100, 1500, 1200], 'order': [322, 45, 132, 38, 0, 297, 537, 0, 581]}, 'Truck10': {'weight': 2000, 'capacity': [0, 2000], 'order': [489, 248, 
# 99, 354, 0]}, 'Outsourcing': [278, 497, 255, 434, 299, 247, 554, 87, 439, 141, 451, 541, 586, 368, 100, 527, 160, 295, 529, 144, 408, 208, 262, 357, 289, 596, 505, 346, 432, 530, 62]}, 20241006: {'Truck1': {'weight': 1000, 'capacity': [0, 0, 1000], 'order': [377, 0, 49, 570, 353, 0]}, 'Truck2': {'weight': 1000, 'capacity': [100, 1000], 'order': [399, 120, 114, 0]}, 'Truck3': {'weight': 1000, 'capacity': [0, 1500], 'order': [219, 0]}, 'Truck4': {'weight': 1000, 'capacity': [100, 0, 1000], 'order': [174, 329, 29, 0, 227, 286, 0]}, 'Truck5': {'weight': 1000, 'capacity': [0, 1000], 'order': [230, 292, 0]}, 'Truck6': {'weight': 1000, 'capacity': [0, 1000], 'order': [2, 405, 0]}, 'Truck7': {'weight': 2000, 'capacity': [300, 1200, 1300, 2000], 'order': [303, 77, 388, 215, 0, 482, 0, 111, 396, 0]}, 'Truck8': {'weight': 2000, 'capacity': [100, 800, 2000], 'order': [281, 472, 7, 180, 140, 0, 276, 226, 198, 0]}, 'Truck9': {'weight': 2000, 'capacity': [0, 2000], 'order': [209, 587, 182, 373, 0]}, 
# 'Truck10': {'weight': 2000, 'capacity': [100, 1800, 1500, 2000], 'order': [127, 79, 70, 515, 359, 0, 184, 0, 275, 0]}, 'Outsourcing': [588, 452, 582, 293, 318, 94, 326, 564, 420, 316, 85, 189, 197, 20, 307, 273, 562, 380, 524, 42, 342, 71, 436, 205, 
# 543, 306, 410, 558, 469]}, 20241007: {'Truck1': {'weight': 1000, 'capacity': [400, 0, 500, 1000], 'order': [82, 50, 191, 0, 133, 461, 0, 328, 0]}, 'Truck2': {'weight': 1000, 'capacity': [0, 300, 1000], 'order': [362, 358, 0, 199, 369, 0]}, 'Truck3': 
# {'weight': 1000, 'capacity': [100, 1000], 'order': [156, 308, 26, 0]}, 'Truck4': {'weight': 1000, 'capacity': [100, 100, 1000], 'order': [56, 148, 0, 363, 310, 34, 81, 0]}, 'Truck5': {'weight': 1000, 'capacity': [100, 0, 1200], 'order': [274, 30, 0, 
# 126, 506, 0]}, 'Truck6': {'weight': 1000, 'capacity': [100, 500, 1000], 'order': [18, 1, 370, 0, 233, 0]}, 'Truck7': {'weight': 2000, 'capacity': [0, 2000], 'order': [584, 595, 74, 33, 0]}, 'Truck8': {'weight': 2000, 'capacity': [0, 2000], 'order': [466, 339, 272, 76, 0]}, 'Truck9': {'weight': 2000, 'capacity': [200, 200, 2000], 'order': [502, 239, 343, 0, 448, 121, 470, 0]}, 'Truck10': {'weight': 2000, 'capacity': [0, 1300, 2000], 'order': [57, 250, 246, 585, 0, 58, 279, 0]}, 'Outsourcing': [151, 134, 404, 580, 546, 471, 499, 433, 445, 598, 349, 237, 41, 579, 234, 525, 256, 277, 442, 3, 474, 519, 131, 302, 314]}, 20241008: {'Truck1': {'weight': 1000, 'capacity': [100, 1000], 'order': [301, 65, 31, 0]}, 'Truck2': {'weight': 1000, 'capacity': [0, 0, 1500], 'order': [0, 241, 378, 220, 0]}, 'Truck3': {'weight': 1000, 'capacity': [0, 0, 1000], 'order': [185, 479, 0, 
# 413, 91, 0]}, 'Truck4': {'weight': 1000, 'capacity': [100, 300, 1000], 'order': [78, 340, 200, 0, 288, 27, 0]}, 'Truck5': {'weight': 1000, 'capacity': [0, 300, 1000], 'order': [263, 257, 0, 108, 331, 0]}, 'Truck6': {'weight': 1000, 'capacity': [100, 
# 0, 1000], 'order': [130, 149, 0, 571, 225, 51, 0]}, 'Truck7': {'weight': 2000, 'capacity': [0, 2000], 'order': [345, 381, 384, 210, 0]}, 'Truck8': {'weight': 2000, 'capacity': [100, 1500, 2000], 'order': [194, 336, 319, 267, 122, 0, 398, 0]}, 'Truck9': {'weight': 2000, 'capacity': [0, 400, 2000], 'order': [510, 313, 304, 37, 0, 501, 406, 0]}, 'Truck10': {'weight': 2000, 'capacity': [100, 1500], 'order': [68, 291, 86, 594, 178, 0, 235]}, 'Outsourcing': [430, 409, 460, 425, 511, 574]}, 20241009: {'Truck1': {'weight': 1000, 'capacity': [400, 500, 1000], 'order': [72, 157, 15, 0, 311, 0]}, 'Truck2': {'weight': 1000, 'capacity': [0, 200, 1000], 'order': [212, 312, 0, 453, 0]}, 'Truck3': {'weight': 1000, 'capacity': [0, 1000], 'order': [456, 125, 0]}, 'Truck4': {'weight': 1000, 'capacity': [0, 200, 1000], 'order': [258, 375, 0, 567, 0]}, 'Truck5': {'weight': 1000, 'capacity': [0, 200, 800, 1000], 'order': [463, 0, 119, 559, 0, 89, 0]}, 'Truck6': {'weight': 1000, 'capacity': [0, 200, 1000], 'order': [240, 229, 0, 417, 0]}, 'Truck7': {'weight': 2000, 'capacity': [200, 1200, 2000], 'order': [164, 477, 0, 575, 573, 0]}, 'Truck8': {'weight': 2000, 'capacity': [400, 700, 2000], 'order': [440, 0, 447, 0, 576, 282]}, 'Truck9': {'weight': 2000, 
# 'capacity': [700, 200, 2000], 'order': [449, 321, 0, 88, 494, 568, 0]}, 'Truck10': {'weight': 2000, 'capacity': [200, 1200, 2000], 'order': [63, 490, 569, 0, 512, 0]}, 'Outsourcing': []}}      

# orde_list =[]
# for date in a.keys():
#     for i in range(1, 11):
#         for order in a[date][f"Truck{i}"]["order"]:
#             if order:
#                 num+=1
#                 orde_list.append(order)
#     for order in a[date]["Outsourcing"]:
#         num+=1
#         orde_list.append(order)
# print(num)

# my_list = [1,2,3,4,1,5,6,1]
# if 9 in my_list:
#     print("aaaaa")
# indices = [i for i, x in enumerate(my_list) if x == 0]
# print(indices)

a ={20241009: {'Truck1': {'weight': 1000, 'capacity': [500, 200, 200, 1000], 'order': [240, 0, 447, 0, 413, 0]}, 'Truck2': {'weight': 1000, 'capacity': [0, 0, 200, 1000], 'order': [456, 194, 0, 257, 229, 0, 417, 0]}, 'Truck3': {'weight': 1000, 'capacity': [200, 0, 1000], 'order': [440, 0, 375, 398, 0]}, 'Truck4': {'weight': 1000, 'capacity': [200, 200, 200, 1000], 'order': [449, 0, 559, 0, 512, 0]}, 'Truck5': {'weight': 1000, 'capacity': [0, 1000], 'order': [363, 272, 0]}, 'Truck6': {'weight': 1000, 'capacity': [0, 0, 1000], 'order': [584, 88, 0, 573, 122, 0]}, 'Truck7': {'weight': 2000, 'capacity': [0, 2000], 'order': [466, 78, 119, 494, 0]}, 'Truck8': {'weight': 2000, 'capacity': [300, 2000], 'order': [212, 72, 157, 568, 0]}, 'Truck9': {'weight': 2000, 'capacity': [0, 2000], 'order': [63, 576, 490, 89, 0]}, 'Truck10': {'weight': 2000, 'capacity': [400, 2000, 2000, 1000, 1500, 2000], 'order': [463, 477, 0, 0, 0, 258, 246, 0, 311, 0]}, 'Outsourcing': []}}

for date in a.keys():
    print(date)
    for key in a[date].keys():
        if key == "Outsourcing":
            print(f"Outsourcing: {a[date]["Outsourcing"]}")
        else:
            print(f"{key}: Weight {a[date][key]["capacity"]}")
            print(f"Order {a[date][key]["order"]}")

# Truck6: Weight [0, 0, 1000]
# Order [584, 88, 0, 573, 122, 0]

# Truck6: Weight [0, 0]
# Order [584, 88, 573, 122, 0]


# Truck10: Weight [400, 2000, 2000, 1000, 1500, 2000]
# Order [463, 477, 0, 0, 0, 258, 246, 0, 311, 0]

def clean_solution(best_solution):
    best_solution_c = copy.deepcopy(best_solution)
    for date in best_solution_c.keys():
        for truck_num, truck in best_solution_c[date].items():
            if truck_num!="Outsourcing":
                truck_order = truck["order"]
                truck_capacity = truck["capacity"]
                while truck["weight"] in truck_capacity:
                    for capacity in truck_capacity:
                        print(f"cap {truck_capacity}")
                        capacity_index = truck_capacity.index(capacity)
                        indices = [i for i, x in enumerate(truck["order"]) if x == 0] 
                        print(f"Truck {truck_num} indices{indices} capacity {capacity} capindex {capacity_index}" )
                        if capacity == truck["weight"]:
                            print(f"from {date}:{truck_num} capacity index: {indices[capacity_index-1]}")
                            del truck_order[indices[capacity_index-1]]
                            del truck_capacity[capacity_index]
                            break
    
    return best_solution_c


a = clean_solution(a)

for date in a.keys():
    print(date)
    for key in a[date].keys():
        if key == "Outsourcing":
            print(f"Outsourcing: {a[date]["Outsourcing"]}")
        else:
            print(f"{key}: Weight {a[date][key]["capacity"]}")
            print(f"Order {a[date][key]["order"]}")
