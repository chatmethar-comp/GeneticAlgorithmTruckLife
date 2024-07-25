import unittest
from random_data_model import random_data_model

class TestCreateDataModel(unittest.TestCase):
    def test_default_parameters(self):
        data = random_data_model()
        self.assertEqual(len(data["distance_matrix"]), 17)
        self.assertEqual(len(data["distance_matrix"][0]), 17)
        self.assertEqual(len(data["time_matrix"]), 17)
        self.assertEqual(len(data["time_matrix"][0]), 17)
        self.assertEqual(len(data["time_windows"]), 17)
        self.assertEqual(len(data["demands"]), 17)
        self.assertEqual(len(data["vehicle_capacities"]), 4)
        self.assertEqual(data["num_vehicles"], 4)
        self.assertEqual(data["depot"], 0)

    def test_custom_parameters(self):
        num_locations = 10
        num_vehicles = 3
        vehicle_capacities = [12, 14, 16]
        max_distance = 500
        max_time = 10
        max_demand = 5

        data = random_data_model(
            num_locations=num_locations,
            num_vehicles=num_vehicles,
            vehicle_capacities=vehicle_capacities,
            max_distance=max_distance,
            max_time=max_time,
            max_demand=max_demand
        )
        self.assertEqual(len(data["distance_matrix"]), num_locations)
        self.assertEqual(len(data["distance_matrix"][0]), num_locations)
        self.assertTrue(all(0 <= dist <= max_distance for row in data["distance_matrix"] for dist in row if dist != 0))

        self.assertEqual(len(data["time_matrix"]), num_locations)
        self.assertEqual(len(data["time_matrix"][0]), num_locations)
        self.assertTrue(all(0 <= time <= max_time for row in data["time_matrix"] for time in row if time != 0))

        self.assertEqual(len(data["time_windows"]), num_locations)
        self.assertEqual(data["time_windows"][0], (0, 5))
        self.assertTrue(all(0 <= window[0] <= 5 and 6 <= window[1] <= 18 for window in data["time_windows"][1:]))

        self.assertEqual(len(data["demands"]), num_locations)
        self.assertTrue(all(0 <= demand <= max_demand for demand in data["demands"]))

        self.assertEqual(len(data["vehicle_capacities"]), num_vehicles)
        self.assertEqual(data["vehicle_capacities"], vehicle_capacities)

        self.assertEqual(data["num_vehicles"], num_vehicles)
        self.assertEqual(data["depot"], 0)

    def test_random_vehicle_capacities(self):
        num_vehicles = 5
        data = random_data_model(num_vehicles=num_vehicles)
        self.assertEqual(len(data["vehicle_capacities"]), num_vehicles)
        self.assertTrue(all(10 <= cap <= 20 for cap in data["vehicle_capacities"]))

if __name__ == '__main__':
    unittest.main()
