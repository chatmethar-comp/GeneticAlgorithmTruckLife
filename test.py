# a = [[1,[3,5],[4,3],[555]],[2,[3,5],[4,3],[555]],[3,[3,5],[4,3],[555]],[4,[3,5],[4,3],[555]]]
# for date in a:
#     print(date)
#     for truck in date[1:-1]:
#         print(truck)

# [[20240201, [], [60], [73], [85], []], 
#  [20240202, [], [26, 76, 28], [52, 66], [], []], 
#  [20240203, [82], [83], [97], [75], []], 
#  [20240204, [], [70], [86, 37, 78], [10], []], 
#  [20240205, [], [6], [79], [17, 15], []], 
#  [20240206, [20, 14, 16], [19], [], [30], []], 
#  [20240207, [], [], [56, 47, 61], [48], []], 
#  [20240208, [], [87, 21], [64], [23], []], 
#  [20240209, [22, 55], [93, 71], [95], [18], []], 
#  [20240210, [], [27, 65], [39, 43], [], []], 
#  [20240211, [5, 62], [38, 53], [1], [90], []], 
#  [20240212, [42], [59, 94], [88], [31], []], 
#  [20240213, [], [], [11, 45], [51], []], 
#  [20240214, [72, 34], [89, 98], [50], [33, 25], []], 
#  [20240215, [], [], [32], [8], []], 
#  [20240216, [], [], [12, 58, 96], [7], []]]

# a = [9]
# b = [4,5,6,7]
# print(set(a).issubset(b))



# for truck in date[1:]:
#     if added == False:
#         truck_load=0
#         truck_work_time=0
#         start_place = 0
#         for order in date[truck_to_assign]:
#             truck_load += order_data_w[order-1][-1]
#             truck_work_time += time_matrix[start_place][order]
#             start_place = order
#         truck_work_time += time_matrix[start_place][0]
#         if (truck_load+order_data_w[item_sw-1][-1]<=truck_to_assign_weight_capacity)&(truck_work_time<=work_time):
#             if func.check_time_add_item(item_sw, date[truck_to_assign], order_data_w,time_matrix):
#                 # date[truck_to_assign].append(item_sw)
#                 break
#             else:
#                 continue
#         else:
#             break
#     try:
#         truck.remove(item_sw)
#     except ValueError:
#         continue

a = [5,5,5]
a.remove(3)