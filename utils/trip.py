from math import ceil
from typing import Optional
import sys
import random
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from .location import Location
    from .city import Road
    from .vehicles import Car, ElectricCar, HybridCar, Bus, Bike, Metro, Vehicle
except (ImportError, ValueError):
    try:
        from utils.location import Location
        from utils.city import Road
        from utils.vehicles import Car, ElectricCar, HybridCar, Bus, Bike, Metro, Vehicle
    except ImportError:
        from location import Location
        from city import Road
        from vehicles import Car, ElectricCar, HybridCar, Bus, Bike, Metro, Vehicle

# TODO: Tasks 14-16: Add Trip classes here
class Trip:
    # P2 Task 14: Base Trip class representing a single trip

    def __init__(
        self,
        pid: str,
        start: Location,
        end: Location,
        path: list,
        vehicle: Vehicle
    ):
        self.id = pid
        self.start = start
        self.end = end
        self.path = path
        self.vehicle = vehicle
        self.vehicle_type = vehicle.name

        # Optimization: Add caching to avoid repeated calculations
        self._distance = None
        self._avg_speed_limit = None
        self._current_speed = None
        self._avg_travel_time = None

    @property
    def distance(self) -> float:
        if self._distance is None:
            self._distance = sum(road.length for road in self.path)
        return self._distance

    @property
    def average_speed_limit(self) -> float:
        if self._avg_speed_limit is None:
            total_distance = self.distance
            weighted_sum = sum(road.max_speed_limit * road.length for road in self.path)
            self._avg_speed_limit = weighted_sum / total_distance
        return self._avg_speed_limit

    @property
    def current_speed(self) -> float:
        if self._current_speed is None:
            if self.vehicle.ignores_road_limit:
                self._current_speed = self.vehicle.speed
            else:
                self._current_speed = min(self.vehicle.speed, self.average_speed_limit)
        return self._current_speed

    @property
    def average_travel_time(self) -> float:
        if self._avg_travel_time is None:
            self._avg_travel_time = 60 * self.distance / self.current_speed
        return self._avg_travel_time

# P2 Task 15: WalkTrip and CarTrip classes
class WalkTrip(Trip):
    def __init__(self, pid: str, start: Location, end: Location, path: list):
        # Create virtual Walk vehicle (fixed 5 km/h, no emissions)
        walk_vehicle = Vehicle(base_speed=5.0, occupancy=1, name="walk", ignores_road_limit=True)
        super().__init__(pid, start, end, path, walk_vehicle)

class CarTrip(Trip):
    def __init__(self, pid: str, start: Location, end: Location, path: list):
        vehicle = Car()
        super().__init__(pid, start, end, path, vehicle)

class ElectricCarTrip(Trip):
    def __init__(self, pid: str, start: Location, end: Location, path: list):
        vehicle = ElectricCar()
        super().__init__(pid, start, end, path, vehicle)


class HybridCarTrip(Trip):
    def __init__(self, pid: str, start: Location, end: Location, path: list):
        vehicle = HybridCar()
        super().__init__(pid, start, end, path, vehicle)

# Task 16: Other trip types
class BikeTrip(Trip):
    def __init__(self, pid: str, start: Location, end: Location, path: list):
        vehicle = Bike()
        super().__init__(pid, start, end, path, vehicle)

class BusTrip(Trip):
    def __init__(self, pid: str, start: Location, end: Location, path: list):
        vehicle = Bus()
        super().__init__(pid, start, end, path, vehicle)

class MetroTrip(Trip):
    def __init__(self, pid: str, start: Location, end: Location, path: list):
        vehicle = Metro()
        super().__init__(pid, start, end, path, vehicle)

def _instantiate_trip(id: str, start: Location, end: Location, mode: str, road_path: list) -> Trip:
    if mode == 'walk':
        return WalkTrip(id, start, end, road_path)
    elif mode == 'car':
        return CarTrip(id, start, end, road_path)
    elif mode == 'electric_car':
        return ElectricCarTrip(id, start, end, road_path)
    elif mode == 'hybrid_car':
        return HybridCarTrip(id, start, end, road_path)
    elif mode == 'bus':
        return BusTrip(id, start, end, road_path)
    elif mode == 'bike':
        return BikeTrip(id, start, end, road_path)
    elif mode == 'metro':
        return MetroTrip(id, start, end, road_path)
    else:
        return CarTrip(id, start, end, road_path)

# P2 Task 16: Split path into multiple trips based on allowed modes
def split_path_to_trips(id: str, start: Location, end: Location, path: list['Road'], transportation_modes: list[str]) -> list[Trip]:
    if not transportation_modes:
        transportation_modes = ["walk"]
    if not path:
        raise ValueError("Path cannot be empty")

    transportation_modes_set = set(transportation_modes)
    first_allowed_modes_set = set(path[0].allowed_modes) if path[0].allowed_modes else set()

    # Select initial mode: randomly choose from valid intersection of person's modes and road's allowed modes
    current_mode_set = transportation_modes_set.intersection(first_allowed_modes_set)
    if not current_mode_set:
        raise ValueError(f"No valid mode found for Person {id} with allowed modes {path[0].allowed_modes} and transportation modes {transportation_modes}")
    
    # Randomly select from available modes (respects individual preferences)
    current_mode = random.choice(list(current_mode_set))

    trips = []
    current_path = []

    for road in path:
        road_allowed_modes_set = set(road.allowed_modes)
        allowed = road_allowed_modes_set.intersection(transportation_modes_set)
        if not allowed:
            raise ValueError(f"No allowed modes for road {road}")

        if current_mode in road_allowed_modes_set and current_mode not in ["bike", "walk"]:
            current_path.append(road)
        else:
            if current_path:
                trips.append(_instantiate_trip(id, start, end, current_mode, current_path))
            # For next road, randomly select from available modes (respects individual preferences)
            current_mode_set = road_allowed_modes_set.intersection(transportation_modes_set)
            assert current_mode_set != set(), f"No valid mode found for road {road} with allowed modes {road.allowed_modes} and transportation modes {transportation_modes}"
            current_mode = random.choice(list(current_mode_set))
            current_path = [road]

    if current_path:
        trips.append(_instantiate_trip(id, start, end, current_mode, current_path))

    return trips

def generate_trips(movements):  # Task 16
    trips = []
    for movement in movements:
        trips.extend(split_path_to_trips(movement["person_id"], movement["start"], movement["end"], movement["path"], movement["mode"]))
    return trips

# TODO:Tasks 17-19: Statistics and Simulation
def count_vehicle_stats(trips: list) -> dict:  # Task 18
    from collections import defaultdict
    vehicle_map = {
        "car": Car(),              # Car: occupancy 1.5 people
        "electric_car": ElectricCar(),  # Electric car: occupancy 1.5 people
        "hybrid_car": HybridCar(),      # Hybrid car: occupancy 1.5 people
        "bus": Bus(),                   # Bus: occupancy 30 people
        "bike": Bike(),                 # Bike: occupancy 1 person
        "metro": Metro(),               # Metro: occupancy 100 people/cart
    }

    travel_time_per_vehicle_type = defaultdict(float)
    co2_emissions_per_vehicle = defaultdict(float)
    users_per_vehicle_type = defaultdict(int)
    vehicle_counts = defaultdict(int)
    total_trips = 0

    for trip in trips:
        vtype = trip.vehicle_type
        total_trips += 1
        travel_time_per_vehicle_type[vtype] += trip.average_travel_time
        trip_co2 = 0.0
        for road in trip.path:
            road_limit = road.max_speed_limit
            if trip.vehicle_type == "metro":
                actual_speed = trip.vehicle.speed
            else:
                actual_speed = min(trip.vehicle.speed, road_limit)
            emission = trip.vehicle.co2_emission(actual_speed, road.length)

            if emission is None:
                emission = 0.0

            if trip.vehicle_type in ["bus", "metro"]:
                occupancy = trip.vehicle.occupancy
                if occupancy is not None and occupancy > 0:
                    emission = emission / occupancy
            trip_co2 += emission

        co2_emissions_per_vehicle[vtype] += trip_co2
        users_per_vehicle_type[vtype] += 1

    total_co2_emissions = sum(co2_emissions_per_vehicle.values())
    total_time = sum(travel_time_per_vehicle_type.values())
    average_travel_time = total_time / total_trips if total_trips > 0 else 0

    # Calculate average travel time per vehicle type
    average_travel_time_per_vehicle_type = {}
    for vtype, total_time_for_type in travel_time_per_vehicle_type.items():
        users_for_type = users_per_vehicle_type.get(vtype, 1)
        average_travel_time_per_vehicle_type[vtype] = total_time_for_type / users_for_type if users_for_type > 0 else 0

    for vtype, users in users_per_vehicle_type.items():
        if users > 0:
            if vtype == "walk":
                vehicle_counts[vtype] = 0
            elif vtype in vehicle_map:
                occupancy = vehicle_map[vtype].occupancy
                vehicle_counts[vtype] = ceil(users / occupancy) if occupancy > 0 else users
            else:
                vehicle_counts[vtype] = users

    return {
        "total_trips": total_trips,
        "travel_time_per_vehicle_type": dict(travel_time_per_vehicle_type),
        "average_travel_time_per_vehicle_type": average_travel_time_per_vehicle_type,
        "average_travel_time": average_travel_time,
        "co2_emissions_per_vehicle": dict(co2_emissions_per_vehicle),
        "total_co2_emissions": total_co2_emissions,
        "users_per_vehicle_type": dict(users_per_vehicle_type),
        "vehicle_counts": dict(vehicle_counts),
    }

# Task 19
def run_simulation(city, population, filename, day_type, load_data):
    import os
    try:
        from .generate_movement import MovementGenerator
    except (ImportError, ValueError):
        try:
            from utils.generate_movement import MovementGenerator
        except ImportError:
            from generate_movement import MovementGenerator
    
    if load_data and os.path.exists(filename):
        movements = MovementGenerator.load_movements(filename)
    else:
        generator = MovementGenerator(city, population)
        movements = generator.run_day(day_type)

    trips = generate_trips(movements)
    stats = count_vehicle_stats(trips)

    # Optimization: Avoid unnecessary dictionary copying and multiple iterations
    travel_time_per_vehicle_type = {
        vtype: (stats['travel_time_per_vehicle_type'][vtype] / count 
                if count > 0 else 0.0)
        for vtype, count in stats['users_per_vehicle_type'].items()
    }
    
    co2_emissions_per_vehicle = {
        vtype: co2_grams / 1000
        for vtype, co2_grams in stats['co2_emissions_per_vehicle'].items()
    }
    
    total_co2_emissions = stats['total_co2_emissions'] / 1000
    
    # Return data dictionary for visualization
    return {   
        "total_trips": stats['total_trips'],
        "trips_per_vehicle_type": stats['users_per_vehicle_type'],
        "travel_time_per_vehicle_type": travel_time_per_vehicle_type,
        "total_average_travel_time": stats['average_travel_time'],
        "co2_emissions_per_vehicle": co2_emissions_per_vehicle,
        "total_co2_emissions": total_co2_emissions,
        "users_per_vehicle_type": stats['users_per_vehicle_type'],
        "vehicle_counts": stats['vehicle_counts'],
    }

# Task 19: Simulation Test code:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

class SimulationTest:  # JSON file paths as default arguments
    def __init__(self, city_file: str = "utils/generated_city.json", 
                 population_file: str = "utils/generated_population.json"):
        self.city_file = city_file
        self.population_file = population_file
        self.city = None
        self.population = None
    
    @staticmethod
    def _import_classes():
        try:
            from .city import City
            from .population import Population
        except (ImportError, ValueError):
            try:
                from utils.city import City
                from utils.population import Population
            except ImportError:
                from city import City
                from population import Population
        return City, Population
        
    def load_data(self):
        City, Population = self._import_classes()
        
        self.city = City.load_from_data(self.city_file)
        self.population = Population.load_from_file(self.population_file)
        print(f"Loaded: City ({len(self.city.roads)} roads), Population ({len(self.population)} people)\n", flush=True)
    
    def run_scenario(self, scenario_name: str, day_type: str, 
                     enable_metro: bool, movements_file: Optional[str] = None) -> dict:
        # Update population's allowed transportation modes based on metro availability
        if enable_metro:
            for person in self.population.get_all_people():  # type: ignore
                if "metro" not in person.transport_modes:
                    person.transport_modes.append("metro")
        else:
            for person in self.population.get_all_people():  # type: ignore
                if "metro" in person.transport_modes:
                    person.transport_modes.remove("metro")
        
        # Clear traffic before running simulation
        self.city.clear_traffic()  # type: ignore
        
        # Run simulation
        stats = run_simulation(
            city=self.city,
            population=self.population,
            filename=movements_file,
            day_type=day_type,
            load_data=False
        )
        
        return stats
    
    def run_all_scenarios(self) -> dict:  # Run all 4 scenarios
        scenarios = {}
        # Scenario 1: Weekday without metro
        print(f"  [1/4] Weekday (No Metro)")
        scenarios["Weekday (No Metro)"] = self.run_scenario(
            scenario_name="Weekday in City (No Metro)",
            day_type="weekday",
            enable_metro=False
        )

        # Scenario 2: Weekend without metro
        print(f"  [2/4] Weekend (No Metro)")
        scenarios["Weekend (No Metro)"] = self.run_scenario(
            scenario_name="Weekend in City (No Metro)",
            day_type="weekend",
            enable_metro=False
        )

        # Scenario 3: Weekday with metro
        print(f"  [3/4] Weekday (With Metro)")
        scenarios["Weekday (With Metro)"] = self.run_scenario(
            scenario_name="Weekday in City (With Metro)",
            day_type="weekday",
            enable_metro=True
        )

        # Scenario 4: Weekend with metro
        print(f"  [4/4] Weekend (With Metro)")
        scenarios["Weekend (With Metro)"] = self.run_scenario(
            scenario_name="Weekend in City (With Metro)",
            day_type="weekend",
            enable_metro=True
        )
        
        return scenarios
    
    def execute(self):

        try:
            from .visualisation import visualize_simulation_results
        except (ImportError, ValueError):
            try:
                from utils.visualisation import visualize_simulation_results
            except ImportError:
                from visualisation import visualize_simulation_results

        try:
            print(f"\n[1/4] Loading data")
            self.load_data()

            print(f"[2/4] Running scenarios")
            scenarios = self.run_all_scenarios()

            print(f"\n[3/4] Generating visualization")
            visualize_simulation_results(scenarios, show_plots=False, name="p2_task19")
            print(f" Visualization generated")

            print(f"\n[4/4] Complete")           
            return scenarios
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            return None
 # test code to run the simulation       
if __name__ == "__main__":
    test = SimulationTest(
        city_file="utils/generated_city.json",
        population_file="utils/generated_population.json"
    )

    scenarios = test.execute()