## Random Data Model Generator

### Overview
This module provides functionality to generate random data models for the Capacitated Vehicle Routing Problem with Time Windows (CVRPTW). The main functions are `random_data_model` and `generate_test_cases`.

### Functions

#### `random_data_model`

Generates a random data model for CVRPTW.

**Parameters:**
- `num_locations` (int): The number of locations, including the depot (default is 17).
- `num_vehicles` (int): The number of vehicles (default is 4).
- `vehicle_capacities` (list of int): The capacities of the vehicles. If `None`, random capacities between 10 and 20 will be generated (default is `None`).
- `max_distance` (int): The maximum distance between locations (default is 1000).
- `max_time` (int): The maximum travel time between locations (default is 15).
- `max_demand` (int): The maximum demand for any location (default is 8).

**Returns:**
- A dictionary containing the random data model with the following keys:
  - `distance_matrix`
  - `time_matrix`
  - `time_windows`
  - `demands`
  - `vehicle_capacities`
  - `num_vehicles`
  - `depot`

**Example Usage:**

```python
import random
from data_model import random_data_model

data_model = random_data_model()
print(data_model)
```


#### `generate_test_cases`

Generates multiple random test cases for CVRPTW.
The size of the data will gradually increase with each test case. Specifically, the number of locations will increase by 1 for each subsequent case, starting from 3. The number of vehicles will match the index of the test case (i.e., for test case 1, there will be 1 vehicles; for test case 2, there will be 2 vehicle, etc.).

**Parameters:**
- `num_cases` (int): The number of test cases to generate (default is 5).

**Returns:**
- A list of dictionaries, each containing a random data model.

**Example Usage:**

```python
import random
from data_model import generate_test_cases

test_cases = generate_test_cases(num_cases=5)
for i, case in enumerate(test_cases):
    print(f"Test Case {i+1}:")
    print(case)
```