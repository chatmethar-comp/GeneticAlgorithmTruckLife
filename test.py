import random
Truck_weights = [1900, 1900, 1900, 1000]
individual1 = [[20240201, [], [], [], [], [9]], 
               [20240202, [], [], [], [], [29, 70, 26]], 
               [20240203, [], [], [], [], [74, 33]], 
               [20240204, [], [], [], [], [17, 16, 61, 78]], 
               [20240205, [], [], [], [], [49, 55, 51, 79]], 
               [20240206, [], [], [], [], [2, 41, 52, 58, 6, 30, 54, 32, 46]], 
               [20240207, [], [], [], [], [24, 13, 60, 23, 22, 39, 68, 57, 10, 34, 20]], 
               [20240208, [], [], [], [], [76, 8, 47, 36, 11, 21, 62, 53, 45, 25, 67, 64, 56, 27]], 
               [20240209, [], [], [], [], [12, 15, 38, 71, 42, 14, 1, 44, 59]], 
               [20240210, [], [], [], [], [65, 3, 37, 31, 75, 43, 35, 73, 4, 77, 48, 19, 18]], 
               [20240211, [], [], [], [], [40, 72]], 
               [20240212, [], [], [], [], [7, 63, 69, 5]], 
               [20240213, [], [], [], [], [50, 28]], 
               [20240214, [], [], [], [], []], 
               [20240215, [], [], [], [], []], 
               [20240216, [], [], [], [], [66]]]

[[20240201, [], [], [], [9], []], 
 [20240202, [26, 70], [29], [], [], []], 
 [20240203, [], [33], [74], [], []], 
 [20240204, [61], [17, 78], [16], [], []], 
 [20240205, [51], [49], [55, 79], [], []], 
 [20240206, [46, 52], [32, 58], [2, 30, 41], [54], [6]], 
 [20240207, [23, 24, 57], [68, 10], [60, 13], [34], [22, 39, 20]], 
 [20240208, [53, 11, 8], [64, 62, 67, 27], [21, 56, 25, 36], [45], [76, 47]], 
 [20240209, [38, 14], [44, 12], [42, 1, 71, 59], [15], []], 
 [20240210, [65, 4], [77, 48, 37], [19, 35], [75, 3], [31, 43, 73, 18]], 
 [20240211, [72], [], [40], [], []], 
 [20240212, [69], [63], [5], [7], []], 
 [20240213, [28], [], [], [50], []], 
 [20240214, [], [], [], [], []], 
 [20240215, [], [], [], [], []], 
 [20240216, [], [], [66], [], []]]

[[20240201, [], [9], [], [], []], 
 [20240203, [], [], [], [], []], 
 [20240204, [], [17], [], [], []], 
 [20240205, [], [], [], [16], [14, 6]], 
 [20240206, [2], [], [], [], []], 
 [20240207, [], [], [10], [], [19]], 
 [20240208, [], [], [11], [], [13, 8]], 
 [20240209, [], [18], [], [], []], 
 [20240210, [], [7], [], [], [15]], 
 [20240211, [1], [], [], [], [12, 4, 3]], 
 [20240212, [], [5], [], [], []], 
 [20240213, [], [], [], [], []]]

[[20240201, [], [], [], [9], []], 
 [20240203, [], [], [], [], []], 
 [20240204, [], [17], [], [], []], 
 [20240205, [14], [6], [], [16], []], 
 [20240206, [], [2], [], [], []], 
 [20240207, [], [], [10, 19], [], []], 
 [20240208, [], [13], [8], [11], []], 
 [20240209, [], [], [], [18], []], 
 [20240210, [7], [], [], [15], []], 
 [20240211, [4], [3], [1], [], [12]], 
 [20240212, [], [], [], [5], []], 
 [20240213, [], [], [], [], []]]

individual2 = [[20240201, [], [], [], [], [9]], 
               [20240203, [], [], [], [], []], 
               [20240204, [], [], [], [], [17]], 
               [20240205, [], [], [], [], [16, 14]], 
               [20240206, [], [], [], [], [6, 10]], 
               [20240207, [], [], [], [], []], 
               [20240208, [], [], [], [], [13, 2, 11]], 
               [20240209, [], [], [], [], [1, 18, 4, 7, 8]], 
               [20240210, [], [], [], [], [19]], 
               [20240211, [], [], [], [], [3, 12]], 
               [20240212, [], [], [], [], [15, 5]], 
               [20240213, [], [], [], [], []]]

order = [[1, 20240204, 14.02644447, 100.6919272, 20240209, 20240212, 500], [2, 20240201, 13.96554796, 100.5245274, 20240204, 20240208, 200], [3, 20240205, 14.1010167, 100.5554815, 20240210, 20240211, 400], [4, 20240205, 14.02366024, 100.7877536, 20240209, 20240212, 900], [5, 20240206, 13.79198072, 100.2948867, 20240211, 20240212, 300], [6, 20240203, 14.05326442, 100.7640006, 
20240204, 20240208, 1100], [7, 20240206, 13.68854597, 100.9852419, 20240208, 20240212, 1000], [8, 20240204, 13.60314233, 100.2348606, 20240207, 20240209, 700], [9, 20240201, 14.11163469, 100.689131, 20240201, 20240201, 400], [10, 20240204, 13.70892926, 100.9235944, 20240206, 20240207, 300], [11, 20240205, 14.0273532, 100.1962857, 20240208, 20240208, 400], [12, 20240203, 14.03560299, 100.8545961, 20240208, 20240211, 1000], [13, 20240202, 13.58207661, 100.6456153, 20240207, 20240208, 900], [14, 20240201, 
13.59317788, 100.9298951, 20240205, 20240210, 900], [15, 20240206, 13.58328929, 100.8222069, 20240208, 20240213, 1000], [16, 20240201, 13.56603353, 100.4366799, 20240203, 20240205, 300], [17, 20240202, 14.05955278, 100.461816, 20240204, 20240204, 900], [18, 20240204, 13.74508088, 100.4805234, 20240209, 20240210, 1000], [19, 20240206, 13.63464473, 100.5075653, 20240206, 20240210, 1100], [20, 20240203, 13.56140732, 100.9938387, 20240206, 20240210, 700], [21, 20240203, 13.69344405, 100.7624837, 20240208, 20240208, 800], [22, 20240202, 13.88725438, 100.1846047, 20240206, 20240207, 1000], [23, 20240203, 13.79272468, 100.2182303, 20240207, 20240211, 400], [24, 20240202, 14.13028772, 100.6687583, 20240206, 20240211, 300], [25, 20240206, 13.78540889, 100.3487762, 20240208, 20240212, 200], [26, 20240201, 13.97242742, 100.2552844, 20240202, 20240202, 700], [27, 20240203, 13.77872208, 100.6054328, 20240205, 20240208, 200], [28, 20240205, 14.11725168, 100.3866821, 20240210, 20240213, 200], [29, 20240202, 13.60727992, 100.6605307, 20240202, 20240203, 200], [30, 20240203, 14.06052021, 100.9611838, 20240206, 20240206, 400], [31, 20240204, 14.15558972, 100.7176285, 20240208, 20240212, 1100], [32, 20240202, 13.58454421, 100.2461556, 20240203, 20240206, 200], [33, 20240203, 14.15495269, 100.1785462, 20240203, 20240205, 900], [34, 20240201, 13.88022347, 100.6454135, 20240205, 20240208, 600], [35, 20240206, 13.91724036, 100.8567787, 20240208, 20240211, 600], [36, 20240202, 13.93579136, 100.591069, 20240207, 20240212, 500], [37, 20240206, 13.8470898, 100.2893438, 20240210, 20240210, 200], [38, 20240203, 14.12250863, 100.4731887, 20240207, 20240212, 800], [39, 20240206, 13.59119256, 100.1985744, 20240206, 20240208, 900], [40, 20240206, 13.72662464, 100.4843515, 20240211, 20240213, 1000], [41, 20240202, 13.87478148, 100.5452835, 20240205, 20240207, 800], [42, 20240206, 13.80348397, 100.4624503, 
20240209, 20240209, 200], [43, 20240205, 13.824066, 100.8623716, 20240209, 20240213, 700], [44, 20240205, 13.83072561, 100.6372509, 20240208, 20240211, 700], [45, 20240205, 14.03745816, 100.2441971, 20240208, 20240209, 800], [46, 20240201, 14.1293833, 100.9554366, 20240204, 20240206, 500], [47, 20240204, 13.98595255, 100.801662, 20240206, 20240210, 900], [48, 20240202, 13.9005856, 100.4622425, 20240206, 20240211, 900], [49, 20240201, 14.11452074, 100.2716631, 20240205, 20240205, 300], [50, 20240206, 13.70041271, 100.4685872, 20240211, 20240214, 500], [51, 20240202, 14.1136999, 100.3662019, 20240203, 20240206, 500], [52, 20240201, 14.06034107, 100.7760415, 20240206, 20240210, 1000], [53, 20240205, 14.02022866, 100.9278432, 20240207, 20240208, 800], [54, 20240205, 14.04856947, 100.308433, 20240206, 20240206, 800], [55, 20240204, 13.78628632, 100.618731, 20240204, 20240206, 500], [56, 20240204, 13.60901137, 100.4855401, 20240205, 20240209, 400], [57, 20240206, 13.80608378, 100.340497, 20240207, 20240207, 1100], [58, 20240204, 13.83983019, 100.6804694, 20240206, 20240209, 700], [59, 20240206, 13.58038851, 100.7270062, 20240209, 20240209, 600], [60, 20240205, 13.65483438, 100.6338541, 20240206, 20240208, 600], [61, 20240201, 13.86797679, 100.5074856, 20240204, 20240207, 300], [62, 20240201, 14.15932179, 100.246802, 20240206, 20240208, 500], [63, 20240204, 14.13712867, 100.8729526, 20240209, 20240214, 700], [64, 20240205, 14.00271258, 100.8567437, 20240208, 20240208, 400], [65, 20240206, 13.96390395, 100.3158028, 20240209, 20240210, 1000], [66, 20240206, 13.66655623, 100.4582506, 20240211, 20240216, 800], [67, 20240204, 13.8963226, 100.2140205, 20240208, 20240208, 700], [68, 20240203, 14.00448326, 100.8972245, 20240206, 20240207, 1100], [69, 20240206, 13.92209629, 100.9613861, 20240209, 20240213, 700], [70, 20240202, 14.13169718, 100.5164467, 20240202, 20240203, 600], [71, 20240201, 13.84733428, 100.8976454, 20240206, 20240210, 600], [72, 20240206, 14.01786852, 100.6804522, 20240211, 20240211, 1100], [73, 20240201, 13.74846408, 100.3786723, 20240206, 20240211, 400], [74, 20240202, 13.80701328, 100.2116569, 20240202, 20240205, 1000], [75, 20240204, 13.95712127, 100.3015606, 20240208, 20240211, 600], [76, 20240204, 14.18298727, 100.3044248, 20240207, 20240208, 1000], [77, 20240204, 13.74729079, 100.8007633, 20240207, 20240212, 500], [78, 20240201, 13.6402236, 100.2843074, 20240203, 20240206, 900], [79, 20240205, 14.05022602, 100.6523458, 20240205, 20240205, 1000]]



def crossover(individual1,individual2,order_w):
    individual1_c = individual1.copy()
    individual2_c = individual2.copy()
    amount_of_order = len(order_w)
    for i in range(random.randint(1,int(amount_of_order/2))):
        date_cross=random.randint(0,len(individual1_c))
        try:
            item_sw = random.choice(individual1_c[date_cross][-1])
            individual2_c[date_cross][-1].append(item_sw)
            for i in range(len(individual2_c)):
                try:
                    individual2_c[i][-1].remove(item_sw)
                except ValueError:
                    continue
        except IndexError:
            continue
    return individual2_c

# child = crossover(individual1,individual2,order)
# print(child)

def assign_to_truck(individual,truck_weights,order_data_w):
    for i in range(30):
        for i in range(len(individual)):
            print(f"date{i}")
            truck_load = 0
            try:
                item_sw = random.choice(individual[i][-1])
                print(f"Order {item_sw}")
                truck_to_assign = random.randint(1,len(individual[i])-2)
                truck_to_assign_weight_capacity = truck_weights[truck_to_assign-1]
                for order in individual[i][truck_to_assign]:
                    truck_load += order_data_w[order-1][-1]
                print(f"Truck{truck_to_assign} load now: {truck_load}")
                print(f"Order detail {order_data_w[item_sw-1]}")
                print(f"product weight {order_data_w[item_sw-1][-1]}")
                if truck_load+order_data_w[item_sw-1][-1]<=truck_to_assign_weight_capacity:
                    individual[i][truck_to_assign].append(item_sw)
                    individual[i][-1].remove(item_sw)
                    print("insert success")
                else:
                    print("insert fail")
                    continue
            except IndexError:
                continue
    return individual

child = assign_to_truck(individual1,Truck_weights,order)
print(child)

