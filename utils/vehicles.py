
 # TODO: Tasks 11-13: Vehicle Classes

class Vehicle:
    # P2 Task 11: Base Vehicle class for all transport modes
    def __init__(self, base_speed: float, occupancy: float, name: str = None, 
                 ignores_road_limit: bool = False):
        self._occupancy = occupancy
        self._base_speed = base_speed
        self._name = name             
        self._ignores_road_limit = ignores_road_limit #leave for trip.py use
    
    @property
    def speed(self) -> float:
        return self._base_speed
    
    @property
    def occupancy(self) -> float:
        return self._occupancy
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def ignores_road_limit(self) -> bool:
        # Whether ignores road speed limit (e.g., metro, bike with fixed speed)
        return self._ignores_road_limit
    
    def co2_emission(self, speed: float, distance: float):
        return None

class Bike(Vehicle):
    def __init__(self):
        super().__init__(base_speed=15.0, occupancy=1.0, name='bike', 
                        ignores_road_limit=True)
    
    def co2_emission(self, speed: float, distance: float):
        return 0

    
# P2 Task 12:
class Car(Vehicle):
    def __init__(self):
        super().__init__(base_speed=80.0, occupancy=1.5, name='car')

    def co2_emission(self, speed: float, distance: float):
        emission_factor = 0.002 * (speed**2) + 1200 / (speed + 0.1) + 50
        return round(emission_factor * distance, 2)

class ElectricCar(Car):
    def __init__(self):
        super().__init__()
        self._name = 'electric_car'

    def co2_emission(self, speed: float, distance: float):
        return 0

class HybridCar(Car):
    def __init__(self):
        super().__init__()
        self._name = 'hybrid_car'

    def co2_emission(self, speed: float, distance: float):
        emission_factor = 0.0018 * (speed**2) + 600 / (speed + 0.1) + 30
        return round(emission_factor * distance, 2)

class Bus(Vehicle):
    def __init__(self):
        super().__init__(base_speed=40.0, occupancy=30.0, name='bus')

    def co2_emission(self, speed: float, distance: float):
        emission_factor = 0.004 * (speed**2) + 2500 / (speed + 0.1) + 200
        return round(emission_factor * distance, 2)

class Metro(Vehicle):
    def __init__(self, carts: int = 4):
        self._carts = carts
        occupancy = 100.0 * carts
        super().__init__(base_speed=60.0, occupancy=occupancy, name='metro',
                        ignores_road_limit=True)

    @property
    def carts(self) -> int:
        return self._carts

    def co2_emission(self, speed: float, distance: float):
        # Metro CO2 formula: 2.5 × d × carts × 150
        # Although total emissions high, per-person emissions low (due to high occupancy)
        return round(2.5 * distance * self.carts * 150, 2)

# test code
if __name__ == "__main__":
    
    test_data = [
        ('bike', Bike(), 15, 10),
        ('car', Car(), 80, 10),
        ('electric_car', ElectricCar(), 80, 10),
        ('hybrid_car', HybridCar(), 80, 10),
        ('bus', Bus(), 40, 10),
        ('metro', Metro(), 60, 10),
    ]
    
    for vehicle_type, vehicle, speed, distance in test_data:
        try:
            emission = vehicle.co2_emission(speed, distance)
            if vehicle_type.startswith('metro'):
                print(f"{vehicle_type:15} | Speed: {speed:3} km/h | Distance: {distance} km | CO2: {emission:8.2f} g | Carts: {vehicle.carts}")
            else:
                print(f"{vehicle_type:15} | Speed: {speed:3} km/h | Distance: {distance} km | CO2: {emission:8.2f} g")
        except Exception as e:
            print(f"{vehicle_type}: {e}")
    

