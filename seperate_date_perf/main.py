# main.py
import numpy as np
import pandas as pd
import genetic_func
import func
import osm
import time
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt

def load_fitness_log(path):
    """
    Load fitness_log written as:
    gen,z1_distance,z2_wait_time,z3_cost
    0, ...
    1, ...
    Returns:
        gens: np.array of ints
        Z:   np.array of shape (G, 3) with columns [z1, z2, z3]
    """
    gens = []
    z1_list, z2_list, z3_list = [], [], []

    if not os.path.exists(path):
        print(f"[WARN] fitness_log not found at {path}")
        return np.array([]), np.empty((0, 3))

    with open(path, "r") as f:
        header = f.readline()  # skip header
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split(",")
            if len(parts) != 4:
                continue
            g, z1, z2, z3 = parts
            gens.append(int(g))
            z1_list.append(float(z1))
            z2_list.append(float(z2))
            z3_list.append(float(z3))

    gens = np.array(gens, dtype=int)
    Z = np.column_stack([z1_list, z2_list, z3_list])
    return gens, Z


def compute_gd_from_best(Z):
    """
    Approximate Generational Distance (GD) using the *best solution per generation*.

    Z: array shape (G, 3), rows = [z1, z2, z3] of the best solution for each generation.

    We take the final generation's best as reference point and compute
    Euclidean distance from each generation's best to that reference.
    """
    if Z.shape[0] == 0:
        return np.array([])

    ref = Z[-1]      # final generation best
    diff = Z - ref
    gd = np.linalg.norm(diff, axis=1)
    return gd


def compute_hv_from_best(Z, ref_factor=1.1):
    """
    Approximate Hypervolume (HV) per generation using the single best point.

    For minimization, with a single point f and reference point r:
        HV = Π_m (r_m - f_m), if f_m <= r_m.

    Z: array shape (G, 3) with [z1, z2, z3] per generation.
    ref_factor: scalar to expand the reference point slightly beyond worst values.
    """
    if Z.shape[0] == 0:
        return np.array([])

    worst = np.max(Z, axis=0)
    ref_point = worst * ref_factor  # r

    hv_values = []
    for f in Z:
        # Ensure f is not worse than ref; if it is, HV becomes 0
        if np.any(f >= ref_point):
            hv_values.append(0.0)
        else:
            hv = np.prod(ref_point - f)
            hv_values.append(float(hv))
    return np.array(hv_values)


def hv_milestone_table(gens, hv_values, milestones=(0, 24, 49, 99, 149)):
    """
    Build a DataFrame summarizing HV at selected generation indices.

    gens: np.array of generation indices (0-based)
    hv_values: np.array of HV values, same length as gens
    milestones: generation indices we care about
                (0,24,49,99,149) = gens 1,25,50,100,150 if you run 150 gens.
    """
    rows = []
    for m in milestones:
        # find index where gens == m
        idx = np.where(gens == m)[0]
        if len(idx) > 0:
            i = idx[0]
            rows.append({"Generation": int(gens[i]), "Hypervolume": hv_values[i]})
    return pd.DataFrame(rows)


def plot_gd_convergence(gens, gd_values, filename):
    """
    Plot GD vs generation and save as PNG.
    """
    if len(gens) == 0:
        print("[WARN] No GD data to plot.")
        return

    plt.figure()
    plt.plot(gens, gd_values, marker="o")
    plt.xlabel("Generation")
    plt.ylabel("Generational Distance (approx.)")
    plt.title("Convergence of MOGA via Generational Distance")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


def plot_3d_pareto_front(pareto_front_metrics, filename):
    """
    3D scatter plot of final Pareto front (z1, z2, z3).
    """
    if not pareto_front_metrics:
        print("[WARN] No Pareto front data for 3D plot.")
        return

    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    z1_list = [m["z1"] for m in pareto_front_metrics]
    z2_list = [m["z2"] for m in pareto_front_metrics]
    z3_list = [m["z3"] for m in pareto_front_metrics]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(z1_list, z2_list, z3_list)

    ax.set_xlabel("Total Distance (z1)")
    ax.set_ylabel("Total Wait Time (z2)")
    ax.set_zlabel("Outsourcing Cost (z3)")
    ax.set_title("3D Pareto Front (Non-dominated Solutions)")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


def plot_2d_tradeoff(x, y, xlabel, ylabel, title, filename):
    """
    Generic 2D trade-off plot for Pareto front.
    """
    plt.figure()
    plt.scatter(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


def select_representative_solutions(pareto_front_metrics):
    """
    Select 3 representative solutions from final Pareto front:

    - Least Cost       -> mainly minimize z1 + z3
    - Fastest Delivery -> mainly minimize z2
    - Balanced         -> roughly equal weights z1,z2,z3

    Returns a dict: { "Least Cost": m, "Fastest Delivery": m, "Balanced": m }
    where each m is one of the entries in pareto_front_metrics.
    """
    if not pareto_front_metrics:
        return {}

    import math

    def score(m, w1, w2, w3):
        return w1 * m["z1"] + w2 * m["z2"] + w3 * m["z3"]

    # Least Cost: heavy weight on z1+z3
    least_cost = min(
        pareto_front_metrics,
        key=lambda m: score(m, 0.45, 0.1, 0.45)
    )

    # Fastest Delivery: heavy weight on z2
    fastest = min(
        pareto_front_metrics,
        key=lambda m: score(m, 0.2, 0.6, 0.2)
    )

    # Balanced: roughly equal
    balanced = min(
        pareto_front_metrics,
        key=lambda m: score(m, 1/3, 1/3, 1/3)
    )

    return {
        "Least Cost": least_cost,
        "Fastest Delivery": fastest,
        "Balanced": balanced,
    }


def representative_solution_table(reps):
    """
    Convert representatives dict to a pandas DataFrame.
    """
    rows = []
    for name, m in reps.items():
        rows.append({
            "Solution Type": name,
            "Total Distance (z1)": m["z1"],
            "Total Wait Time (z2)": m["z2"],
            "Outsourcing Cost (z3)": m["z3"],
        })
    return pd.DataFrame(rows)

def run_single_experiment(config):

    """
    Runs one optimization experiment and returns:
    {
        "N": int,
        "final_gd": float,
        "final_hv": float,
        "pareto_size": int,
        "execution_time": float
    }
    """

    ex_data = func.read_csv_to_list(config["filepath_order"])
    product_list = func.read_csv_to_list(config["filepath_product"])
    new_order = func.product_to_weight(ex_data, product_list)

    N = len(new_order)

    distance_matrix = func.create_distance_matrix(
        config["warehouse_location"], new_order
    )
    time_matrix = func.create_time_matrix(
        config["warehouse_location"], new_order
    )

    with open(config["fitness_log"], "w") as f:
        f.write("gen,z1_distance,z2_wait_time,z3_cost\n")

    start_time = time.time()

    best_solution, final_population = genetic_func.optimize_routes(
        config=config,
        order_data_w=new_order,
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        truck_weights=config["truck_weights"],
        pop_size=config["population_size"],
        elite_size=config["elite_size"],
        mutation_rate=config["mutation_rate"],
        generations=config["generations"],
    )
    best_distance = best_solution.fitness[0]
    best_cost = best_solution.fitness[1]

    execution_time = time.time() - start_time

    # Build Pareto
    pareto_candidates = []
    for sol in final_population:
        z1 = func.calculate_total_distance(sol, distance_matrix)
        z2, _ = func.calculate_wait_time_and_outsourcingscore(
            sol, new_order, time_matrix, genetic_func.desired_delivery_date
        )
        z3 = func.calculate_outsourcing_fee(
            sol, new_order, distance_matrix, genetic_func.desired_delivery_date
        )

        pareto_candidates.append({"z1": z1, "z2": z2, "z3": z3})

    def dominates(a, b):
        return (
            (a["z1"] <= b["z1"] and a["z2"] <= b["z2"] and a["z3"] <= b["z3"])
            and (a["z1"] < b["z1"] or a["z2"] < b["z2"] or a["z3"] < b["z3"])
        )

    pareto_front = [
        c for c in pareto_candidates
        if not any(dominates(o, c) for o in pareto_candidates)
    ]

    # Load fitness log
    gens, Z = load_fitness_log(config["fitness_log"])
    gd_values = compute_gd_from_best(Z)
    hv_values = compute_hv_from_best(Z)

    final_gd = float(gd_values[-1]) if len(gd_values) > 0 else None
    final_hv = float(hv_values[-1]) if len(hv_values) > 0 else None

    # For Scailiily test
    # return {
    # "N": N,
    # "Final_GD": final_gd,
    # "Final_HV": final_hv,
    # "Pareto_Size": len(pareto_front),
    # "Execution_Time_sec": execution_time
    # }

    return {
        "Algorithm": "MOGA",
        "N": N,
        "Final_GD": final_gd,
        "Final_HV": final_hv,
        "Pareto_Size": len(pareto_front),
        "Execution_Time_sec": execution_time,
        "Best_Total_Distance": best_distance,
        "Best_Total_Cost": best_cost
    }

def run_moga_comparison(config):

    print("\n===== RUNNING MOGA =====")
    result = run_single_experiment(config)

    print("\nMOGA RESULTS")
    print(f"Final GD: {result['Final_GD']}")
    print(f"Final HV: {result['Final_HV']}")
    print(f"Pareto Size: {result['Pareto_Size']}")
    print(f"Execution Time: {result['Execution_Time_sec']:.2f} sec")
    print(f"Best Distance: {result['Best_Total_Distance']}")
    print(f"Best Cost: {result['Best_Total_Cost']}")

    return result

# def main_scail():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(BASE_DIR, "input")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output", f"scalability_{timestamp}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Base configuration (same for all N)
    base_config = {
        "warehouse_location": [13.7438, 100.5626],
        "population_size": 1250,
        "elite_size": 125,
        "mutation_rate": 0.15,
        "generations": 150,
        "truck_weights": [500, 500, 1000, 1000, 2000],
        "filepath_product": os.path.join(INPUT_DIR, "product.csv"),
        "working_hours": {
            "start": "07:00",
            "end": "19:00"
        },
    }

    order_files = [
        "order100.csv",
        "order200.csv",
        "order350.csv",
        "order500.csv",
    ]

    results = []

    print("\n===== STARTING SCALABILITY EXPERIMENTS =====")

    for file in order_files:

        print(f"\nRunning experiment for: {file}")

        config = base_config.copy()

        config["filepath_order"] = os.path.join(INPUT_DIR, file)
        config["fitness_log"] = os.path.join(OUTPUT_DIR, f"fitness_log_{file}.txt")

        result = run_single_experiment(config)

        print(f"Finished N = {result['N']}")
        print(f"  Final GD: {result['Final_GD']}")
        print(f"  Final HV: {result['Final_HV']}")
        print(f"  Pareto Size: {result['Pareto_Size']}")
        print(f"  Execution Time (sec): {result['Execution_Time_sec']:.2f}")

        results.append(result)

    # ==================================================
    # Save Scalability Table
    # ==================================================

    results_df = pd.DataFrame(results)

    table_path = os.path.join(OUTPUT_DIR, "Table_4_4_Scalability_Results.csv")
    results_df.to_csv(table_path, index=False)

    print("\n===== SCALABILITY SUMMARY =====")
    print(results_df.to_string(index=False))
    print(f"\nSaved scalability table to: {table_path}")

    # ==================================================
    # Plot Execution Time vs N
    # ==================================================

    plt.figure()
    plt.plot(results_df["N"], results_df["Execution_Time_sec"], marker="o")
    plt.xlabel("Number of Orders (N)")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Scalability Analysis: Execution Time vs Problem Size")
    plt.grid(True)
    plt.tight_layout()

    plot_path = os.path.join(OUTPUT_DIR, "Fig_4_4_ExecutionTime_vs_N.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()

    print(f"Saved execution time plot to: {plot_path}")

# def main_old4():
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # # ---------------------------
    # # Directory structure
    # # ---------------------------
    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # INPUT_DIR = os.path.join(BASE_DIR, "input")
    # OUTPUT_DIR = os.path.join(BASE_DIR, "output", timestamp)
    # CONFIG_DIR = os.path.join(BASE_DIR, "output", timestamp)

    # # Create directories if they don't exist
    # for directory in [INPUT_DIR, OUTPUT_DIR, CONFIG_DIR]:
    #     if not os.path.exists(directory):
    #         os.makedirs(directory)

    # # ---------------------------
    # # Configuration parameters
    # # ---------------------------
    # config = {
    #     # Warehouse location [latitude, longitude]
    #     "warehouse_location": [13.7438, 100.5626],

    #     # Genetic Algorithm parameters
    #     "population_size": 1250,
    #     "elite_size": 125,
    #     "mutation_rate": 0.15,
    #     "generations": 150,

    #     # Truck fleet configuration
    #     "truck_weights": [500, 500, 1000, 1000, 2000],

    #     # Input file paths
    #     "filepath_order": os.path.join(INPUT_DIR, "order10.csv"),
    #     "filepath_product": os.path.join(INPUT_DIR, "product.csv"),

    #     # Output file configuration
    #     "output_excel": os.path.join(OUTPUT_DIR, "route_schedule.xlsx"),
    #     "output_map": os.path.join(OUTPUT_DIR, "route_map.html"),
    #     "fitness_log": os.path.join(OUTPUT_DIR, "best_fitness_log.txt"),

    #     # Time windows
    #     "working_hours": {
    #         "start": "07:00",
    #         "end": "19:00"
    #     },
    # }

    # # Save configuration
    # config_file = os.path.join(CONFIG_DIR, "config.json")
    # with open(config_file, "w") as f:
    #     json.dump(config, f, indent=4)

    # try:
    #     # ---------------------------
    #     # Load and process input data
    #     # ---------------------------
    #     print("Loading input data...")
    #     ex_data = func.read_csv_to_list(config["filepath_order"])
    #     product_list = func.read_csv_to_list(config["filepath_product"])
    #     new_order = func.product_to_weight(ex_data, product_list)

    #     # ---------------------------
    #     # Create distance and time matrices
    #     # ---------------------------
    #     print("Creating distance and time matrices...")
    #     distance_matrix = func.create_distance_matrix(
    #         config["warehouse_location"], new_order
    #     )
    #     time_matrix = func.create_time_matrix(
    #         config["warehouse_location"], new_order
    #     )
    #     print("Distance matrix created.")

    #     # Optional: reset fitness log for this run
    #     with open(config["fitness_log"], "w") as f:
    #         f.write("gen,z1_distance,z2_wait_time,z3_cost\n")

    #     # ---------------------------
    #     # Run optimization
    #     # ---------------------------
    #     print(f"Starting optimization with {config['generations']} generations...")
    #     start_time = time.time()

    #     # IMPORTANT:
    #     # optimize_routes MUST return (best_solution, final_population)
    #     best_solution, final_population = genetic_func.optimize_routes(
    #         config=config,
    #         order_data_w=new_order,
    #         distance_matrix=distance_matrix,
    #         time_matrix=time_matrix,
    #         truck_weights=config["truck_weights"],
    #         pop_size=config["population_size"],
    #         elite_size=config["elite_size"],
    #         mutation_rate=config["mutation_rate"],
    #         generations=config["generations"],
    #     )
    #     execution_time = time.time() - start_time
    #     print(f"Optimization completed in {execution_time:.2f} seconds")

        

    # except Exception as e:
    #     print(f"Error occurred: {str(e)}")
    #     raise
def main():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(BASE_DIR, "input")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output", f"comparison_{timestamp}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    config = {
        "warehouse_location": [13.7438, 100.5626],
        "population_size": 1250,
        "elite_size": 125,
        "mutation_rate": 0.15,
        "generations": 150,
        "truck_weights": [500, 500, 1000, 1000, 2000],
        "filepath_product": os.path.join(INPUT_DIR, "product.csv"),
        "filepath_order": os.path.join(INPUT_DIR, "order500.csv"),
        "fitness_log": os.path.join(OUTPUT_DIR, "fitness_log_MOGA.txt"),
        "working_hours": {
            "start": "07:00",
            "end": "19:00"
        }
    }

    print("\n===== RUNNING MOGA =====")

    result = run_single_experiment(config)

    print("\n===== MOGA RESULTS =====")
    print(f"Finished N = {result['N']}")
    print(f"Final GD: {result['Final_GD']}")
    print(f"Final HV: {result['Final_HV']}")
    print(f"Pareto Size: {result['Pareto_Size']}")
    print(f"Execution Time (sec): {result['Execution_Time_sec']:.2f}")

    df = pd.DataFrame([result])
    df.to_csv(os.path.join(OUTPUT_DIR, "MOGA_result.csv"), index=False)

    print("\nSaved MOGA_result.csv")

if __name__ == "__main__":
    main()