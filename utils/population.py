import json
import random
try:
    from .location import Location, Serializable
    from .city import Landmark
    from .trip import Trip
except (ImportError, ValueError):
    try:
        from utils.location import Location, Serializable
        from utils.city import Landmark
        from utils.trip import Trip
    except ImportError:
        from location import Location
        Serializable = object
        from city import Landmark
        from trip import Trip

# TODO: P1 Tasks 6-8: Person and Population Classes
class Person(Serializable):
    def __init__(self, id: int, home_location: Location, work_location: Location,
                 rec_location=None, transport_modes=None, daily_routine=None):
        self._id = id
        self._home_location = home_location
        self._work_location = work_location
        self._rec_location = rec_location if rec_location is not None else []
        self._transport_modes = transport_modes if transport_modes is not None else ["walk", "bike", "car"]
        self._daily_routine = daily_routine if daily_routine is not None else {
            "weekday": ["home", "work", "rec", "home"],
            "weekend": ["home", "rec", "home", "rec", "home"],
        }

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def home_location(self):
        return self._home_location

    @property
    def work_location(self):
        return self._work_location

    @property
    def rec_location(self):
        return self._rec_location

    @property
    def transport_modes(self):
        return self._transport_modes

    @transport_modes.setter
    def transport_modes(self, value):
        self._transport_modes = value

    @property
    def daily_routine(self):
        return self._daily_routine

    @daily_routine.setter
    def daily_routine(self, value):
        self._daily_routine = value

    def to_dict(self):
        return {
            "id": self._id,
            "home_location": self._home_location.to_dict(),
            "work_location": self._work_location.to_dict(),
            "rec_location": [loc.to_dict() for loc in self._rec_location],
            "transport_modes": self._transport_modes,
            "daily_routine": self._daily_routine,
        }

    @classmethod
    def from_dict(cls, data):
        home_loc = Location.from_dict(data["home_location"])
        work_loc = Location.from_dict(data["work_location"])
        rec_locs = [Location.from_dict(loc) for loc in data.get("rec_location", [])]
        person = cls(data["id"], home_loc, work_loc, rec_locs)
        transport_modes = data.get("transport_modes") or data.get("transport_mode")
        if transport_modes:
            person.transport_modes = transport_modes
        person.daily_routine = data.get("daily_routine", person.daily_routine)
        return person

    def __str__(self):
        return f"Person ID: {self._id}, Home: ({self._home_location}), Work: ({self._work_location}), Rec: {len(self._rec_location)}"

    def update_transport_modes(self, chances: dict):
        """Update transport modes based on probability chances."""
        new_modes = []
        for mode, chance in chances.items():
            if random.random() < chance:
                new_modes.append(mode)
        if not new_modes:
            new_modes.append(random.choice(list(chances.keys())))
        self.transport_modes = new_modes


class Population:
    def __init__(self, people=None):
        self._people = people if people is not None else []

    @property
    def people(self):
        return self._people

    def __len__(self):
        return len(self._people)

    def add_person(self, person: Person):
        self._people.append(person)

    def get_all_people(self):
        return self._people

    def save_to_file(self, filename: str):
        data = [person.to_dict() for person in self._people]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filename: str):
        with open(filename, "r", encoding="utf-8") as f:
            people_data = json.load(f)
        population = cls()
        for person_data in people_data:
            person = Person.from_dict(person_data)
            population.add_person(person)
        return population
# task 10
    def change_transport_preferences(self, new_chances=None):
        if new_chances is None:
            new_chances = {"bike": 0.3, "car": 0.5, "electric_car": 0.3, "hybrid_car": 0.2, "bus": 0.5, "metro": 0.8}
        candidates = ["car", "hybrid_car", "electric_car", "bike", "bus", "metro"]
        for person in self._people:
            new_modes = ["walk"]
            for mode in candidates:
                if random.random() < new_chances.get(mode, 0):
                    new_modes.append(mode)
            person.transport_modes = new_modes

    def __str__(self):
        return f"Population with {len(self._people)} people."

def get_test_people():
    return [
        Person(1, Location(50, 50), Location(60, 60), [Location(55, 45), Location(50, 65)],
               ["walk", "bike", "car"], {"weekday": ["home", "work", "rec", "home"], "weekend": ["home", "rec", "home", "rec", "home"]}),
        Person(2, Location(45, 55), Location(65, 65), [Location(60, 50), Location(55, 60)],
               ["bike", "bus"], {"weekday": ["home", "work", "home"], "weekend": ["home", "rec", "rec", "home"]}),
        Person(3, Location(55, 45), Location(50, 50), [Location(60, 60), Location(45, 50)],
               ["car", "bus", "metro"], {"weekday": ["home", "work", "rec", "work", "home"], "weekend": ["home", "rec", "home"]}),
        Person(4, Location(40, 60), Location(55, 55), [Location(50, 50)],
               ["walk", "bike"], {"weekday": ["home", "work", "home"], "weekend": ["home", "rec", "home", "rec", "home"]}),
        Person(5, Location(60, 40), Location(50, 60), [Location(55, 50), Location(60, 60), Location(50, 45)],
               ["car", "metro"], {"weekday": ["home", "work", "rec", "home"], "weekend": ["home", "rec", "rec", "home"]}),
    ]

def get_test_city():
    try:
        from .city import City, Landmark, Road
        from .location import Location
    except (ImportError, ValueError):
        from city import City, Landmark, Road
        from location import Location

    city = City("PopulationCity")
    # Add landmarks
    city.add_landmark(Landmark("Downtown", Location(50, 50), [], 0.5, 0.8, 0.4))
    city.add_landmark(Landmark("Park", Location(30, 30), [], 0.3, 0.1, 0.9))
    city.add_landmark(Landmark("Mall", Location(70, 70), [], 0.2, 0.2, 0.95))

    # Add roads
    city.add_road(Road(Location(30, 30), Location(50, 50), max_speed_limit=50))
    city.add_road(Road(Location(50, 50), Location(70, 70), max_speed_limit=55))
    city.add_road(Road(Location(30, 30), Location(70, 70), max_speed_limit=60))
    
    city.build_network()
    return city

if __name__ == "__main__":
    people = get_test_people()
    
    print("Creating 5 people...")
    for person in people:
        print(f"  Person {person.id}: {person.home_location} -> {person.work_location}")
    
    population = Population(people)
    print(f"Population: {population}")
    
    population.save_to_file("test_population.json")
    print("Saved to test_population.json")
    
    loaded_population = Population.load_from_file("test_population.json")
    print(f"Loaded: {loaded_population}")
    
    all_match = all(original.id == loaded.id and original.home_location.x == loaded.home_location.x
                    for original, loaded in zip(population.people, loaded_population.people))
    if all_match:
        print("✓ Verification: All data matches")
    #task 7 visualization
    try:
        from city import City
        from visualisation import visualize_population
        try:
            city = City.load_from_data("generated_city.json")
        except FileNotFoundError:
            from city import Landmark, Road
            city = City("TestCity")
            loc1, loc2, loc3 = Location(50, 50), Location(60, 60), Location(55, 45)
            city.add_landmark(Landmark("Downtown", loc1, [Location(49, 51), Location(51, 49)], 0.2, 0.5, 0.3))
            city.add_landmark(Landmark("Park", loc2, [Location(59, 61), Location(61, 59), Location(60, 62)], 0.0, 0.0, 1.0))
            city.add_landmark(Landmark("ResidentialArea", loc3, [Location(54, 46), Location(56, 44)], 0.9, 0.1, 0.0))
            city.add_road(Road(loc1, loc2, 60, ["car", "bus", "bike"]))
            city.add_road(Road(loc2, loc3, 50, ["car", "bus"]))
            city.add_road(Road(loc1, loc3, 70, ["car", "bus", "bike"]))
            city.build_network()
        visualize_population(city, loaded_population, show_plots=True)

    except Exception as e:
        print(f"Error: {e}")
