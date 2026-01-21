# main.py

import genetic_func
import func
import osm
import time
import json
import os
from datetime import datetime

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Directory structure
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(BASE_DIR, "input")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output", timestamp)
    CONFIG_DIR = os.path.join(BASE_DIR, "output", timestamp)

    # Create directories if they don't exist
    for directory in [INPUT_DIR, OUTPUT_DIR, CONFIG_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Configuration parameters
    config = {
        # Warehouse location [latitude, longitude]
        "warehouse_location": [13.7438, 100.5626],
        
        # Genetic Algorithm parameters
        "population_size": 1250,
        "elite_size": 125,
        "mutation_rate": 0.05,
        "generations": 150,
        
        # Truck fleet configuration
        # Don't touch it! Truck Weight fiend is not available. This configuration will release soon.
        "truck_weights": [1000, 1000, 1000, 1000, 1000, 1000, 2000, 2000, 2000, 2000],
        
        # Input file paths
        "filepath_order": os.path.join(INPUT_DIR, "order.csv"),
        "filepath_product": os.path.join(INPUT_DIR, "product.csv"),
        
        # Output file configuration
        "output_excel": os.path.join(OUTPUT_DIR, "route_schedule.xlsx"),
        "output_map": os.path.join(OUTPUT_DIR, "route_map.html"),
        "fitness_log": os.path.join(OUTPUT_DIR, "best_fitness_log.txt"),
        
        # Time windows
        "working_hours": {
            "start": "08:00",
            "end": "17:00"
        },
    
    }

    # Save configuration
    config_file = os.path.join(CONFIG_DIR, "config.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)

    try:
        # Load and process input data
        print("Loading input data...")
        ex_data = func.read_csv_to_list(config["filepath_order"])
        product_list = func.read_csv_to_list(config["filepath_product"])
        new_order = func.product_to_weight(ex_data, product_list)
        
        # Create distance and time matrices
        print("Creating distance and time matrices...")
        distance_matrix = func.create_distance_matrix(config["warehouse_location"], new_order)
        time_matrix = func.create_time_matrix(config["warehouse_location"], new_order)
        with open(config["fitness_log"], "a") as f:
            f.write(f"best_outsourcing_fee, wait_time, outsource_score, fitness_score\n")
        # Run optimization
        print(f"Starting optimization with {config['generations']} generations...")
        start_time = time.time()
        
        best_solution = genetic_func.optimize_routes(
            config=config,
            order_data_w=new_order,
            distance_matrix=distance_matrix,
            time_matrix=time_matrix,
            truck_weights=config["truck_weights"],
            pop_size=config["population_size"],
            elite_size=config["elite_size"],
            mutation_rate=config["mutation_rate"],
            generations=config["generations"]
        )
        
        execution_time = time.time() - start_time
        print(f"Optimization completed in {execution_time:.2f} seconds")

        # Calculate metrics
        best_outsourcing_fee = func.calculate_outsourcing_fee(
            best_solution, 
            new_order, 
            distance_matrix, 
            genetic_func.desired_delivery_date
        )
        display_solution  = func.format_solution(
            best_solution,  
            genetic_func.desired_delivery_date
        )

        # Print solution details
        print("\nSolution Summary:")
        print(f"Total Outsourcing Cost: {best_outsourcing_fee}")
        
        for date in genetic_func.desired_delivery_date:
            print(f"\nDate: {date}")

            for truck, trips in display_solution[date]["Trucks"].items():
                print(f"\n{truck}:")
                for i, trip in enumerate(trips, 1):
                    print(f"  Trip {i}: {trip}")

            print(f"\nOutsourced Orders: {display_solution[date]['Outsourcing']}")

        # Generate outputs
        print("\nGenerating outputs...")
        
        # Create route map
        to_map = func.to_truck_routes(
            best_solution,
            new_order,
            genetic_func.desired_delivery_date
        )
        osm.create_map_tree(
            config["warehouse_location"],
            to_map,
            osm.colors,
            output_path=config["output_map"]
        )
        
        # Create Excel schedule
        excel_input = func.output_as_excel(
            best_solution,
            new_order,
            time_matrix,
            genetic_func.desired_delivery_date
        )
        func.Excel_writer(excel_input, output_path=config["output_excel"])
        
        print("\nOptimization completed successfully!")
        print(f"Results saved to {OUTPUT_DIR}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()