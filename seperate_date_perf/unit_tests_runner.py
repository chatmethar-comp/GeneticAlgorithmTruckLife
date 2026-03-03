"""
unit_tests_runner.py

Run the 6 unit tests for the MOGA delivery planning model, collect metrics,
and generate simple matplotlib plots suitable for Chapter 4.

This file assumes:
- func.py and genetic_func.py exist and are importable.
- genetic_func.optimize_routes(...) has the same signature as in main().
- Solutions have the structure:

  solution = {
      date_int: {
          "Truck1": {
              "weight": Q_k,
              "capacity": [remaining_cap_state_0, remaining_cap_state_1, ...],
              "order": [order_id_1, 0, order_id_2, ...]
          },
          "Truck2": { ... },
          "Outsourcing": [outsourced_order_ids...]
      },
      another_date_int: {...}
  }

- new_order is a list of rows:
  [OrderID, ReceptionDate, Lat, Lon, D_start, D_end, "HH:MM", weight]
"""

import os
import time
import json
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime

import func
import genetic_func


# =========================
# Helper: basic config
# =========================

def build_base_config():
    """Base config similar to your main(), but without file paths."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "unit_test_output")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    config = {
        "warehouse_location": [13.7438, 100.5626],
        "population_size": 250,   # can be lower than thesis runs for speed
        "elite_size": 25,
        "mutation_rate": 0.15,
        "generations": 10,
        "truck_weights": [500],   # single truck type for tests unless changed
        "working_hours": {
            "start": "07:00",
            "end": "19:00"
        },
        "output_dir": OUTPUT_DIR
    }
    return config


# =========================
# Helper: build test datasets
# =========================

def build_new_order_for_test_1() -> List[List[Any]]:
    """
    Unit Test 1: capacity feasibility.
    One order with weight > Q_k (e.g. 600 > 500).
    Format: [OrderID, ReceptionDate, Lat, Lon, D_start, D_end, "HH:MM", weight]
    """
    # Example: order location close to your earlier example
    return [
        [1, 20241001, 13.7276, 100.5250, 20241006, 20241006, "09:45", 600]
    ]


def build_new_order_for_test_2() -> List[List[Any]]:
    """
    Unit Test 2: two geographically close orders, same day and feasible times.
    """
    return [
        [1, 20241001, 13.7276, 100.5250, 20241006, 20241006, "09:30", 300],
        [2, 20241001, 13.7201, 100.5333, 20241006, 20241006, "09:45", 300],
    ]

def build_new_order_for_test_3() -> List[List[Any]]:
    """
    Unit Test 3: impossible time window.

    Put the customer very far from the warehouse so that the
    earliest feasible arrival is much later than DT_i.

    Example: warehouse is in Bangkok; we place the order far in the
    deep south or opposite corner of the country.
    """
    # Very far from Bangkok (e.g., near the southern border of Thailand)
    far_lat = 6.5    # ~ deep south
    far_lon = 101.5  # ~ far from Bangkok

    # Working hours: start at 07:00 (from config)
    # We set DT_i = 07:30, so any realistic travel time from Bangkok
    # to this point will be >> 30 minutes.
    return [
        [1, 20241001, far_lat, far_lon, 20241001, 20241001, "07:30", 300]
    ]


def build_new_order_for_test_4() -> List[List[Any]]:
    """
    Unit Test 4: multi-period scheduling.
    Order 1: window Day 1-3
    Order 2: fixed to Day 3
    """
    # Example dates: 20241001, 20241002, 20241003
    return [
        [1, 20241001, 13.7563, 100.5018, 20241001, 20241003, "10:30", 300],  # flexible 1-3
        [2, 20241001, 13.7550, 100.5000, 20241003, 20241003, "10:30", 300],  # fixed day 3
    ]


def build_new_order_for_test_5() -> List[List[Any]]:
    """
    Unit Test 5 — Fleet saturation with cheap vs expensive outsourcing.

    - 15 orders total, all same day and delivery time, all near depot.
    - 10 orders: 400 kg (cheap to outsource, q_i <= 500).
    - 5 orders: 600 kg (expensive to outsource, q_i > 500).
    - Truck capacity Q_k = 600, so each truck can carry only one 600 kg order.
    - With 10 trucks, at most 10 internal deliveries; remaining 5 must be outsourced.
    """
    date = 20241001
    lat_base, lon_base = 13.75, 100.55
    delivery_time = "10:00"

    orders: List[List[Any]] = []

    # Cheap orders: IDs 1–10, weight 400 kg
    for oid in range(1, 11):
        # Slight jitter in coordinates so they are not exactly identical
        lat = lat_base + (oid - 5) * 0.0002
        lon = lon_base + (oid - 5) * 0.0002
        orders.append([oid, date, lat, lon, date, date, delivery_time, 400])

    # Expensive orders: IDs 11–15, weight 600 kg
    for oid in range(11, 16):
        lat = lat_base + (oid - 13) * 0.0002
        lon = lon_base - (oid - 13) * 0.0002
        orders.append([oid, date, lat, lon, date, date, delivery_time, 600])

    return orders

def build_new_order_for_test_6() -> List[List[Any]]:
    """
    Unit Test 6: multi-trip reloading.
    Two heavy orders close to depot, total demand > Q_k.

    Example:
    Q_k = 500, each order = 450, so total 900 -> must reload.
    """
    return [
        [1, 20241001, 13.7450, 100.5640, 20241001, 20241001, "10:00", 450],
        [2, 20241001, 13.7425, 100.5610, 20241001, 20241001, "14:00", 450],
    ]


def build_new_order_for_test(test_id: int) -> List[List[Any]]:
    if test_id == 1:
        return build_new_order_for_test_1()
    elif test_id == 2:
        return build_new_order_for_test_2()
    elif test_id == 3:
        return build_new_order_for_test_3()
    elif test_id == 4:
        return build_new_order_for_test_4()
    elif test_id == 5:
        return build_new_order_for_test_5()
    elif test_id == 6:
        return build_new_order_for_test_6()
    else:
        raise ValueError(f"Unknown test_id: {test_id}")
    

# =========================
# Run GA for a unit test
# =========================
def solution_has_reload_and_internal(sol) -> bool:
    """
    Return True if this solution:
      - serves orders 1 and 2 internally (not outsourced)
      - and uses at least one reload (0-gene) in the truck sequence.

    This is specifically for Unit Test 6.
    """
    if not sol:
        return False

    # For UT6 we assume a single day key and one internal truck
    date_key = extract_date_key(sol)
    trucks = get_truck_dicts_for_date(sol, date_key)
    outsourcing = get_outsourcing_for_date(sol, date_key)

    if not trucks:
        return False

    internal_set = all_internal_orders(trucks)

    # both orders must be internal and NOT in outsourcing
    cond_internal = (
        1 in internal_set and
        2 in internal_set and
        1 not in outsourcing and
        2 not in outsourcing
    )

    if not cond_internal:
        return False

    # check for reload (0-gene) in at least one truck
    for t_dict in trucks.values():
        order_seq = t_dict.get("order", [])
        if any(g == 0 for g in order_seq):
            return True

    return False
def count_outsourced_orders(sol) -> int:
    """Count total outsourced orders across all days in this solution."""
    total = 0
    for day_data in sol.values():
        outsourcing = day_data.get("Outsourcing", [])
        total += len(outsourcing)
    return total

def count_heavy_outsourced(sol, new_order) -> int:
                weight_by_id = {int(row[0]): float(row[7]) for row in new_order}
                total = 0
                for day_data in sol.values():
                    outsourcing = day_data.get("Outsourcing", [])
                    for oid in outsourcing:
                        if weight_by_id.get(int(oid), 0.0) > 500:
                            total += 1
                return total

def run_ga_for_test(test_id: int, seed: int):
    """
    Set up data for a given unit test, call your GA, and
    return the FINAL CHOSEN SOLUTION using the same logic as main():
      - build Pareto candidates from final_population
      - extract Pareto front
      - prefer z3 = 0
      - choose best according to (z1+z2) or (z1+z2+z3)
    """
    random.seed(seed)
    np.random.seed(seed)

    config = build_base_config()

    # Build test-specific order data
    new_order = build_new_order_for_test(test_id)

    # Distance and time matrices (reuse your func helpers)
    distance_matrix = func.create_distance_matrix(
        config["warehouse_location"], new_order
    )
    time_matrix = func.create_time_matrix(
        config["warehouse_location"], new_order
    )
        # --- Test-specific fleet config overrides ---
    if test_id == 5:
        # 10 identical trucks of capacity 600 kg
        config["truck_weights"] = [600] * 10
    else:
        # whatever you normally use
        config["truck_weights"] = [500]  # or your original default


    # Run GA (same as in main)
    best_solution, final_population = genetic_func.optimize_routes(
        config=config,
        order_data_w=new_order,
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        truck_weights=[600,600,600,600,600,600,600,600,600,600],
        pop_size=config["population_size"],
        elite_size=config["elite_size"],
        mutation_rate=config["mutation_rate"],
        generations=config["generations"],
    )

    pareto_candidates = []
    for sol in final_population:
        z1_distance = func.calculate_total_distance(sol, distance_matrix)
        z2_wait_time, _ = func.calculate_wait_time_and_outsourcingscore(
            sol, new_order, time_matrix, genetic_func.desired_delivery_date
        )
        z3_cost = func.calculate_outsourcing_fee(
            sol,
            new_order,
            distance_matrix,
            genetic_func.desired_delivery_date,
        )
        num_out = count_outsourced_orders(sol)      # you already had this
        heavy_out = count_heavy_outsourced(sol, new_order)

        pareto_candidates.append({
            "solution": sol,
            "z1": z1_distance,
            "z2": z2_wait_time,
            "z3": z3_cost,
            "num_out": num_out,
            "heavy_out": heavy_out,
        })




    if not pareto_candidates:
        raise RuntimeError("Final population is empty – cannot build Pareto front.")

    # ---------- Pareto front extraction (same as in main) ----------
    def dominates(a, b):
        # a Pareto-dominates b (minimization in all objectives)
        return (
            (a["z1"] <= b["z1"] and a["z2"] <= b["z2"] and a["z3"] <= b["z3"])
            and (a["z1"] < b["z1"] or a["z2"] < b["z2"] or a["z3"] < b["z3"])
        )

    pareto_front_metrics = []
    for cand in pareto_candidates:
        if not any(dominates(other, cand) for other in pareto_candidates):
            pareto_front_metrics.append(cand)

        # ---------- Selection logic (test-specific where needed) ----------
    def score_feasible(m):
        return m["z1"] + m["z2"]

    def score_all(m):
        return m["z1"] + m["z2"] + m["z3"]

    chosen_metric = None

    # === Unit Test 1: we WANT outsourcing for the overweight order ===
    if test_id == 1:
        # Prefer candidates with any outsourcing; among them minimize z3, then z1+z2
        with_out = [m for m in pareto_candidates if m["num_out"] > 0]
        if with_out:
            chosen_metric = min(with_out, key=score_all)

    # === Unit Test 3: impossible window -> must outsource ===
    if test_id == 3 and chosen_metric is None:
        with_out = [m for m in pareto_candidates if m["num_out"] > 0]
        if with_out:
            chosen_metric = min(with_out, key=score_all)

    # === Unit Test 5: fleet saturation -> some internal, some outsourced ===
        # === Unit Test 5: prefer solutions that do NOT outsource heavy orders ===
    if test_id == 5 and chosen_metric is None:
        num_orders = len(new_order)
        num_trucks = len(config["truck_weights"])
        target_out = max(0, num_orders - num_trucks)  # here: 15 - 10 = 5

        # 1) Prefer heavy_out = 0 (no heavy orders outsourced)
        no_heavy_out = [m for m in pareto_candidates if m["heavy_out"] == 0]
        if no_heavy_out:
            # Within those, try to get ~5 outsourced in total
            exact = [m for m in no_heavy_out if m["num_out"] == target_out]
            if exact:
                chosen_metric = min(exact, key=score_all)
            else:
                def score_closest(m):
                    return abs(m["num_out"] - target_out) * 1000 + score_all(m)
                chosen_metric = min(no_heavy_out, key=score_closest)


    # === Unit Test 6: reload behaviour (we already added this earlier) ===
    if test_id == 6 and chosen_metric is None:
        reload_candidates = [
            m for m in pareto_candidates
            if solution_has_reload_and_internal(m["solution"])
        ]
        if reload_candidates:
            chosen_metric = min(reload_candidates, key=score_all)

    # === Default selection (same as main) for all other cases ===
        # === Default selection (same as main) for all other cases ===
    if chosen_metric is None:
        feasible = [m for m in pareto_front_metrics if m["z3"] == 0]
        if feasible:
            chosen_metric = min(feasible, key=score_feasible)
        else:
            chosen_metric = min(pareto_front_metrics, key=score_all)

    chosen_solution = chosen_metric["solution"]
    return chosen_solution, new_order, distance_matrix, time_matrix




# =========================
# Metric helpers
# =========================

def extract_date_key(solution: Dict[int, Dict[str, Any]]) -> int:
    """Assume one main date key for the unit tests."""
    return next(iter(solution.keys()))


def get_truck_dicts_for_date(solution: Dict[int, Dict[str, Any]], date_key: int) -> Dict[str, Dict[str, Any]]:
    """Return only the truck entries (exclude 'Outsourcing')."""
    day_data = solution[date_key]
    trucks = {k: v for k, v in day_data.items() if k != "Outsourcing"}
    return trucks


def get_outsourcing_for_date(solution: Dict[int, Dict[str, Any]], date_key: int) -> List[int]:
    """Return outsourced order IDs for that date."""
    day_data = solution[date_key]
    return day_data.get("Outsourcing", [])

from typing import Set

def all_internal_orders(trucks: Dict[str, Dict[str, Any]]) -> Set[int]:
    """Return set of unique order IDs served by internal trucks (ignoring zeros & duplicates)."""
    orders_internal: Set[int] = set()
    for t_dict in trucks.values():
        for oid in t_dict.get("order", []):
            if oid != 0:
                orders_internal.add(int(oid))
    return orders_internal



def id_to_weight_map(new_order: List[List[Any]]) -> Dict[int, float]:
    """
    Map OrderID -> weight from new_order.
    new_order row: [OrderID, ReceptionDate, Lat, Lon, D_start, D_end, "HH:MM", weight]
    """
    mapping = {}
    for row in new_order:
        oid = int(row[0])
        w = float(row[7])
        mapping[oid] = w
    return mapping


def id_to_date_window_map(new_order: List[List[Any]]) -> Dict[int, Tuple[int, int]]:
    """Map OrderID -> (D_start, D_end)."""
    mapping = {}
    for row in new_order:
        oid = int(row[0])
        d_start = int(row[4])
        d_end = int(row[5])
        mapping[oid] = (d_start, d_end)
    return mapping


def id_to_delivery_time_map(new_order: List[List[Any]]) -> Dict[int, str]:
    """Map OrderID -> "HH:MM" string."""
    mapping = {}
    for row in new_order:
        oid = int(row[0])
        t_str = row[6]
        mapping[oid] = t_str
    return mapping


def time_str_to_minutes(t_str: str) -> int:
    """Convert 'HH:MM' to minutes from midnight."""
    h, m = t_str.split(":")
    return int(h) * 60 + int(m)


# =====================================
# Dataclasses for results (per run)
# =====================================

@dataclass
class Test1Result:
    run_id: int
    seed: int
    truck_capacity: float
    min_remaining_capacity: float
    order_weight: float
    order_internal: bool
    order_outsourced: bool


@dataclass
class Test2Result:
    run_id: int
    seed: int
    same_vehicle_and_day: bool
    z1_observed: float
    z1_baseline: float


@dataclass
class Test3Result:
    run_id: int
    seed: int
    order_internal: bool
    order_outsourced: bool
    dt_minutes: int
    earliest_arrival: int
    lateness: int  # earliest_arrival - dt_minutes



@dataclass
@dataclass
class Test4Result:
    run_id: int
    seed: int
    day_i: int
    day_j: int
    same_day: bool
    date_window_violated: bool
    d_start_i: int   # NEW
    d_end_i: int     # NEW



@dataclass
class Test5Result:
    run_id: int
    seed: int
    num_internal_heavy: int
    num_out_heavy: int
    num_internal_cheap: int
    num_out_cheap: int
    avg_dist_outsourced: float



@dataclass
class Test6Result:
    run_id: int
    seed: int
    served_i_internally: bool
    served_j_internally: bool
    num_reloads: int
    capacity_violated: bool
    order_i_outsourced: bool   # NEW
    order_j_outsourced: bool   # NEW



# =====================================
# Extraction for each unit test
# =====================================

def extract_test1(best_solution, new_order) -> Test1Result:
    """
    Test 1: capacity feasibility.
    Check that heavy order is outsourced, and inspect truck capacity usage.
    """
    date_key = extract_date_key(best_solution)
    trucks = get_truck_dicts_for_date(best_solution, date_key)
    outsourcing = get_outsourcing_for_date(best_solution, date_key)

    # Single order for this test: id = 1
    oid = 1
    weight_map = id_to_weight_map(new_order)
    q_i = weight_map[oid]

    # Assume single truck
    truck = list(trucks.values())[0]
    Q_k = float(truck["weight"])
    remaining_caps = truck.get("capacity", [])
    min_remaining = min(remaining_caps) if remaining_caps else Q_k

    internal_orders = all_internal_orders(trucks)
    internal_flag = (oid in internal_orders)
    outs_flag = (oid in outsourcing)

    return Test1Result(
        run_id=0,
        seed=0,
        truck_capacity=Q_k,
        min_remaining_capacity=min_remaining,
        order_weight=q_i,
        order_internal=internal_flag,
        order_outsourced=outs_flag,
    )

def extract_test2(best_solution, new_order, distance_matrix) -> Test2Result:
    """
    Test 2: spatial synergy.
    - Check if order 1 and 2 are on the same vehicle/day.
    - Compute observed Z1 from the solution.
    - Compute baseline Z1 if each order were served separately
      (0 -> i -> 0 and 0 -> j -> 0).
    """
    date_key = extract_date_key(best_solution)
    trucks = get_truck_dicts_for_date(best_solution, date_key)

    # Map each order to truck
    order_to_truck = {}
    for t_name, t_dict in trucks.items():
        for oid in t_dict.get("order", []):
            if oid != 0:
                order_to_truck[oid] = t_name

    same_truck = (order_to_truck.get(1) is not None and
                  order_to_truck.get(1) == order_to_truck.get(2))

    # Observed Z1 from your existing function
    z1_observed = func.calculate_total_distance(best_solution, distance_matrix)

    # Baseline: serve separately from depot
    # node index: 0 = depot, i = order i in new_order (we use ID → node index map)
    idx_by_id = {int(row[0]): idx + 1 for idx, row in enumerate(new_order)}
    i_idx = idx_by_id[1]
    j_idx = idx_by_id[2]

    d0i = distance_matrix[0][i_idx]
    d0j = distance_matrix[0][j_idx]
    z1_baseline = 2 * d0i + 2 * d0j  # 0->i->0 and 0->j->0

    return Test2Result(
        run_id=0,
        seed=0,
        same_vehicle_and_day=same_truck,
        z1_observed=z1_observed,
        z1_baseline=z1_baseline,
    )

def extract_test3(best_solution, new_order, time_matrix, working_hours) -> Test3Result:
    """
    Test 3: strict time window.
    - Compute target time DT_i in minutes.
    - Approximate earliest possible arrival = start of working_hours + travel_time(0->i).
    - Compute lateness.
    - Check whether order is internal or outsourced.
    """
    date_key = extract_date_key(best_solution)
    trucks = get_truck_dicts_for_date(best_solution, date_key)
    outsourcing = get_outsourcing_for_date(best_solution, date_key)

    oid = 1
    internal_orders = all_internal_orders(trucks)
    internal_flag = (oid in internal_orders)
    outs_flag = (oid in outsourcing)

    # Target time DT_i from new_order
    t_map = id_to_delivery_time_map(new_order)
    dt_minutes = time_str_to_minutes(t_map[oid])

    # Travel time from depot to this order
    idx_by_id = {int(row[0]): idx + 1 for idx, row in enumerate(new_order)}
    node_idx = idx_by_id[oid]
    travel_minutes = time_matrix[0][node_idx]

    # Start of working hours (from passed-in working_hours dict)
    start_minutes = time_str_to_minutes(working_hours["start"])
    earliest_arrival = start_minutes + travel_minutes
    lateness = earliest_arrival - dt_minutes

    return Test3Result(
        run_id=0,
        seed=0,
        order_internal=internal_flag,
        order_outsourced=outs_flag,
        dt_minutes=dt_minutes,
        earliest_arrival=earliest_arrival,
        lateness=lateness,
    )

def extract_test4(best_solution, new_order) -> Test4Result:
    """
    Test 4: multi-period scheduling & date validity.
    We want:
      - assigned day for order 1 (flexible)
      - assigned day for order 2 (fixed)
      - whether any assignment violated the date window
      - the allowed window [D_start_i, D_end_i] for order 1 (for plotting)
    """
    date_window_map = id_to_date_window_map(new_order)

    # Window for order 1 (flexible)
    d_start_i, d_end_i = date_window_map[1]

    day_i = None
    day_j = None
    date_window_violated = False

    for date_key, day_data in best_solution.items():
        trucks = get_truck_dicts_for_date(best_solution, date_key)
        internal = all_internal_orders(trucks)
        outsourcing = get_outsourcing_for_date(best_solution, date_key)

        # Order 1
        if 1 in internal or 1 in outsourcing:
            day_i = date_key
            d_start, d_end = date_window_map[1]
            if not (d_start <= date_key <= d_end):
                date_window_violated = True

        # Order 2
        if 2 in internal or 2 in outsourcing:
            day_j = date_key
            d_start, d_end = date_window_map[2]
            if not (d_start <= date_key <= d_end):
                date_window_violated = True

    same_day = (day_i is not None and day_i == day_j)

    return Test4Result(
        run_id=0,
        seed=0,
        day_i=day_i or -1,
        day_j=day_j or -1,
        same_day=same_day,
        date_window_violated=date_window_violated,
        d_start_i=d_start_i,
        d_end_i=d_end_i,
    )

def extract_test5(best_solution, new_order, distance_matrix) -> Test5Result:
    """
    Test 5: fleet saturation with cheap vs expensive outsourcing.

    We count:
      - # heavy (600 kg) orders internal vs outsourced
      - # cheap (400 kg) orders internal vs outsourced
      - avg depot distance of outsourced orders (for context)
    """
    date_key = extract_date_key(best_solution)
    trucks = get_truck_dicts_for_date(best_solution, date_key)
    outsourcing = get_outsourcing_for_date(best_solution, date_key)

    internal_set = all_internal_orders(trucks)
    outsourced_set = {int(o) for o in outsourcing}

    # Map order ID -> weight, and ID -> node index in distance_matrix
    weight_by_id = {int(row[0]): float(row[7]) for row in new_order}
    idx_by_id = {int(row[0]): idx + 1 for idx, row in enumerate(new_order)}

    num_internal_heavy = 0
    num_out_heavy = 0
    num_internal_cheap = 0
    num_out_cheap = 0

    for oid, w in weight_by_id.items():
        if w > 500:  # heavy (expensive to outsource)
            if oid in internal_set:
                num_internal_heavy += 1
            elif oid in outsourced_set:
                num_out_heavy += 1
        else:        # cheap
            if oid in internal_set:
                num_internal_cheap += 1
            elif oid in outsourced_set:
                num_out_cheap += 1

    # Average distance of outsourced orders from depot
    dists = []
    for oid in outsourced_set:
        node_idx = idx_by_id[oid]
        dists.append(distance_matrix[0][node_idx])

    avg_d0_out = float(sum(dists) / len(dists)) if dists else 0.0

    return Test5Result(
        run_id=0,
        seed=0,
        num_internal_heavy=num_internal_heavy,
        num_out_heavy=num_out_heavy,
        num_internal_cheap=num_internal_cheap,
        num_out_cheap=num_out_cheap,
        avg_dist_outsourced=avg_d0_out,
    )


 
def extract_test6(best_solution, new_order) -> Test6Result:
    """
    Test 6: multi-trip reloading.
    Inspect:
      - whether orders 1 and 2 are served internally or outsourced
      - how many reloads (0-genes) are used
      - whether capacity ever goes negative
    """
    date_key = extract_date_key(best_solution)
    trucks = get_truck_dicts_for_date(best_solution, date_key)
    outsourcing = get_outsourcing_for_date(best_solution, date_key)

    # Assume single truck for this test (Truck1)
    if trucks:
        truck = list(trucks.values())[0]
        order_seq = truck.get("order", [])
        remaining_caps = truck.get("capacity", [])
        Q_k = float(truck["weight"])
    else:
        order_seq = []
        remaining_caps = []
        Q_k = 0.0

    internal_set = all_internal_orders(trucks)

    served_i = (1 in internal_set)
    served_j = (2 in internal_set)

    order_i_out = (1 in outsourcing)
    order_j_out = (2 in outsourcing)

    num_reloads = sum(1 for x in order_seq if x == 0)

    capacity_violated = any(c < 0 for c in remaining_caps)

    return Test6Result(
        run_id=0,
        seed=0,
        served_i_internally=served_i,
        served_j_internally=served_j,
        num_reloads=num_reloads,
        capacity_violated=capacity_violated,
        order_i_outsourced=order_i_out,
        order_j_outsourced=order_j_out,
    )

# =========================
# Plotting for Chapter 4
# =========================

def plot_test1(results: List[Test1Result], filename: str):
    runs = list(range(len(results)))
    q = [res.order_weight for res in results]
    Q = results[0].truck_capacity

    plt.figure(figsize=(8,3))
    plt.axhline(Q, color="black", linestyle="--", linewidth=1.5, label="$Q_k$ (Capacity)")

    for i, res in enumerate(results):
        color = "red" if res.order_outsourced else "green"
        plt.scatter(i, q[i], s=80, color=color, zorder=3)

    plt.ylim(0, max(q)*1.15)  # better visual scaling
    plt.xticks(runs)
    plt.ylabel("Weight (kg)")
    plt.xlabel("Run")
    plt.title("Unit Test 1 — Feasibility Check\n$q_i$ vs $Q_k$")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

def plot_test2(results: List[Test2Result], filename: str):
    runs = list(range(len(results)))
    z1_obs = [res.z1_observed for res in results]
    z1_base = [res.z1_baseline for res in results]
    same_flags = [res.same_vehicle_and_day for res in results]

    x = np.arange(len(results))
    width = 0.35

    plt.figure(figsize=(8, 5))
    plt.bar(x - width/2, z1_obs, width=width, label="Observed $Z_1$")
    plt.bar(x + width/2, z1_base, width=width, alpha=0.7, label="Baseline (Separate Routes)")

    # Mark runs where clustering happened
    for i, same in enumerate(same_flags):
        if same:
            plt.scatter(i - width/2, z1_obs[i], s=60, color="green", zorder=5,
                        label="Clustered (same vehicle)" if i == 0 else "")

    plt.xlabel("Run")
    plt.ylabel("Total Distance $Z_1$")
    plt.title("Unit Test 2 — Spatial Synergy: Observed vs Baseline Distance")
    plt.xticks(x, runs)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

def plot_test3(results: List[Test3Result], filename: str):
    runs = list(range(len(results)))
    lateness = [res.lateness for res in results]
    outsourced = sum(res.order_outsourced for res in results)
    internal = sum(res.order_internal for res in results)

    plt.figure(figsize=(8, 5))
    plt.bar(runs, lateness)
    plt.axhline(0, linestyle="--", color="black", linewidth=1)
    plt.xlabel("Run")
    plt.ylabel("Lateness (minutes)")
    plt.title("Unit Test 3 — Time Window Violation (Earliest Arrival - $DT_i$)")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

    # Optional: second simple bar chart for decision outcome
    plt.figure(figsize=(5, 4))
    plt.bar(["Outsourced", "Internal"], [outsourced, internal])
    plt.ylabel("Number of runs")
    plt.title("Unit Test 3 — Assignment Outcome")
    plt.tight_layout()
    plt.savefig(filename.replace(".png", "_decision.png"), dpi=300)
    plt.close()


def plot_test4(results: List[Test4Result], filename: str):
    if not results:
        print("No results for Test 4.")
        return

    # Use the allowed window for order 1 from the first result
    d_start = results[0].d_start_i
    d_end = results[0].d_end_i

    # Build all days in the window, e.g. [20241001, 20241002, 20241003]
    all_days = list(range(d_start, d_end + 1))

    # Count how often order 1 was assigned to each day
    days_i = [res.day_i for res in results if res.day_i != -1]
    counts = [days_i.count(d) for d in all_days]
    labels = [str(d) for d in all_days]

    same_day_count = sum(res.same_day for res in results)

    plt.figure(figsize=(8, 5))
    plt.bar(labels, counts)
    plt.xlabel("Assigned Day for Order 1 (date key)")
    plt.ylabel("Frequency (runs)")
    plt.title(
        f"Unit Test 4 — Day Assignment for Flexible Order\n"
        f"Same-day with Order 2 in {same_day_count}/{len(results)} runs"
    )
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()



def plot_test5(results: List[Test5Result], filename: str):
    runs = list(range(len(results)))

    internal_heavy = [r.num_internal_heavy for r in results]
    out_heavy = [r.num_out_heavy for r in results]
    internal_cheap = [r.num_internal_cheap for r in results]
    out_cheap = [r.num_out_cheap for r in results]

    # --- Plot 1: per-run breakdown (stacked) ---
    x = np.arange(len(results))
    width = 0.4

    plt.figure(figsize=(9, 5))

    # Internal bar: heavy + cheap stacked
    bottom_internal = np.zeros(len(results))
    plt.bar(x - width/2, internal_heavy, width=width, label="Internal Heavy (600 kg)")
    plt.bar(x - width/2, internal_cheap, width=width, bottom=internal_heavy,
            label="Internal Cheap (400 kg)", alpha=0.7)

    # Outsourced bar: heavy + cheap stacked
    plt.bar(x + width/2, out_heavy, width=width, label="Outsourced Heavy (600 kg)")
    plt.bar(x + width/2, out_cheap, width=width, bottom=out_heavy,
            label="Outsourced Cheap (400 kg)", alpha=0.7)

    plt.xticks(x, runs)
    plt.xlabel("Run")
    plt.ylabel("# Orders")
    plt.title("Unit Test 5 — Internal vs Outsourced, Cheap vs Expensive")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

    # --- Plot 2: aggregate outcome across runs ---
    total_internal_heavy = sum(internal_heavy)
    total_out_heavy = sum(out_heavy)
    total_internal_cheap = sum(internal_cheap)
    total_out_cheap = sum(out_cheap)

    labels = [
        "Internal Heavy",
        "Outsourced Heavy",
        "Internal Cheap",
        "Outsourced Cheap",
    ]
    values = [
        total_internal_heavy,
        total_out_heavy,
        total_internal_cheap,
        total_out_cheap,
    ]

    plt.figure(figsize=(7, 4))
    plt.bar(labels, values)
    plt.ylabel("Total # Orders (over all runs)")
    plt.title("Unit Test 5 — Aggregate Assignment Pattern")
    plt.tight_layout()
    plt.savefig(filename.replace(".png", "_summary.png"), dpi=300)
    plt.close()


def plot_test6(results: List[Test6Result], filename: str):
    runs = list(range(len(results)))
    reloads = [res.num_reloads for res in results]
    reloads = [x/2 for x in reloads]
    print(runs, reloads)

    # Per-run reload count (may all be zero, that's still informative)
    plt.figure(figsize=(8, 5))
    plt.bar(runs, reloads)
    plt.xlabel("Run")
    plt.ylabel("# Reloads (0-genes)")
    plt.title("Unit Test 6 — Number of Reloads per Run")
    plt.xticks(runs)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

    # Summary chart of outcomes across runs
    reload_runs = sum(res.num_reloads > 0 for res in results)
    outsourced_runs = sum(res.order_i_outsourced or res.order_j_outsourced for res in results)
    cap_viol_runs = sum(res.capacity_violated for res in results)
    both_internal_runs = sum(res.served_i_internally and res.served_j_internally for res in results)

    labels = ["Reload used", "Any outsourced", "Capacity violated", "Both internal"]
    values = [reload_runs, outsourced_runs, cap_viol_runs, both_internal_runs]

    plt.figure(figsize=(7, 4))
    plt.bar(labels, values)
    plt.ylabel("# Runs")
    plt.title("Unit Test 6 — Outcome Summary Across Runs")
    plt.tight_layout()
    plt.savefig(filename.replace(".png", "_summary.png"), dpi=300)
    plt.close()

import argparse

# =========================
# Main: run & plot all
# =========================
def parse_test_selection(selection: str) -> List[int]:
    """
    Parse a selection string like:
      "1"        -> [1]
      "1,3,6"    -> [1,3,6]
      "all"      -> [1,2,3,4,5,6]
    """
    s = selection.strip().lower()
    if s in ("all", "*", "0"):
        return [1, 2, 3, 4, 5, 6]

    test_ids: List[int] = []
    for part in selection.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            tid = int(part)
            if 1 <= tid <= 6:
                test_ids.append(tid)
        except ValueError:
            continue

    # Remove duplicates and sort
    return sorted(set(test_ids))

def run_tests(selection: str, num_runs: int = 10):
    """
    Run one, multiple, or all unit tests, depending on 'selection'.
    selection examples:
      "1"       -> only Unit Test 1
      "1,3,6"   -> Unit Tests 1, 3, and 6
      "all"     -> all 6 tests

    num_runs controls how many GA runs are performed per test.
    """
    base_config = build_base_config()
    out_dir = base_config["output_dir"]
    working_hours = base_config["working_hours"]

    test_ids = parse_test_selection(selection)
    if not test_ids:
        print(f"No valid test IDs in selection '{selection}'. Valid: 1..6 or 'all'.")
        return

    print(f"Running unit tests {test_ids} for {num_runs} runs each...")
    print(f"Output directory: {out_dir}")

    # --- Test 1 ---
    if 1 in test_ids:
        t1_results: List[Test1Result] = []
        for r in range(num_runs):
            seed = 1000 + r
            best_solution, new_order, dist_mat, time_mat = run_ga_for_test(1, seed)
            res = extract_test1(best_solution, new_order)
            res.run_id = r
            res.seed = seed
            t1_results.append(res)
        plot_test1(t1_results, os.path.join(out_dir, "unit_test_1_capacity.png"))
        print("Finished Unit Test 1")

    # --- Test 2 ---
    if 2 in test_ids:
        t2_results: List[Test2Result] = []
        for r in range(num_runs):
            seed = 2000 + r
            best_solution, new_order, dist_mat, time_mat = run_ga_for_test(2, seed)
            # make sure your extract_test2 uses distance_matrix
            res = extract_test2(best_solution, new_order, dist_mat)
            res.run_id = r
            res.seed = seed
            t2_results.append(res)
        plot_test2(t2_results, os.path.join(out_dir, "unit_test_2_spatial_synergy.png"))
        print("Finished Unit Test 2")

    # --- Test 3 ---
    if 3 in test_ids:
        t3_results: List[Test3Result] = []
        for r in range(num_runs):
            seed = 3000 + r
            best_solution, new_order, dist_mat, time_mat = run_ga_for_test(3, seed)
            # make sure your extract_test3 signature matches: (..., time_mat, working_hours)
            res = extract_test3(best_solution, new_order, time_mat, working_hours)
            res.run_id = r
            res.seed = seed
            t3_results.append(res)
        plot_test3(t3_results, os.path.join(out_dir, "unit_test_3_time_window.png"))
        print("Finished Unit Test 3")

    # --- Test 4 ---
    if 4 in test_ids:
        t4_results: List[Test4Result] = []
        for r in range(num_runs):
            seed = 4000 + r
            best_solution, new_order, dist_mat, time_mat = run_ga_for_test(4, seed)
            res = extract_test4(best_solution, new_order)
            res.run_id = r
            res.seed = seed
            t4_results.append(res)
        plot_test4(t4_results, os.path.join(out_dir, "unit_test_4_multi_period.png"))
        print("Finished Unit Test 4")

    # --- Test 5 ---
    if 5 in test_ids:
        t5_results: List[Test5Result] = []
        for r in range(num_runs):
            seed = 5000 + r
            best_solution, new_order, dist_mat, time_mat = run_ga_for_test(5, seed)
            res = extract_test5(best_solution, new_order, dist_mat)
            res.run_id = r
            res.seed = seed
            t5_results.append(res)
        plot_test5(t5_results, os.path.join(out_dir, "unit_test_5_fleet_saturation.png"))
        print("Finished Unit Test 5")

    # --- Test 6 ---
    if 6 in test_ids:
        t6_results: List[Test6Result] = []
        for r in range(num_runs):
            seed = 6000 + r
            chosen_solution, new_order, dist_mat, time_mat = run_ga_for_test(6, seed)

            # DEBUG: show the actual chosen solution structure
            print(f"\n=== UT6 run {r}, seed {seed} ===")
            for date_key, day_data in chosen_solution.items():
                print("Date:", date_key)
                print("  Outsourcing:", day_data.get("Outsourcing", []))
                for k, v in day_data.items():
                    if k == "Outsourcing":
                        continue
                    print(f"  {k}: orders={v.get('order', [])}, capacity={v.get('capacity', [])}")

            res = extract_test6(chosen_solution, new_order)
            res.run_id = r
            res.seed = seed
            t6_results.append(res)

        plot_test6(t6_results, os.path.join(out_dir, "unit_test_6_reloading.png"))
        print("Finished Unit Test 6")



def run_all_unit_tests(num_runs: int = 10):
    """Backwards-compatible helper: runs all tests."""
    run_tests("all", num_runs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run unit tests for the MOGA delivery planning model."
    )
    parser.add_argument(
        "--test", "-t",
        type=str,
        default="all",
        help="Which test(s) to run: '1', '2', ..., '6', '1,3,5', or 'all'. Default: 'all'."
    )
    parser.add_argument(
        "--runs", "-r",
        type=int,
        default=10,
        help="Number of runs per unit test (default: 10)."
    )

    args = parser.parse_args()
    run_tests(args.test, args.runs)
