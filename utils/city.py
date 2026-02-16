import json
import networkx as nx
try:
    from .location import Location, Serializable
except (ImportError, ValueError):
    try:
        from utils.location import Location, Serializable
    except ImportError:
        from location import Location
        Serializable = object

# TODO: Tasks 2 & 3: Add Road and Landmark classes
class Landmark(Serializable):
    def __init__(
        self,
        name,
        location: Location,
        local_points: list,
        res_chance: float,
        work_chance: float,
        rec_chance: float,
    ):
        self.__name = name
        self.__location = location
        self.__local_points = local_points
        self.__res_chance = res_chance
        self.__work_chance = work_chance
        self.__rec_chance = rec_chance

    @property
    def name(self):
        return self.__name

    @property
    def location(self):
        return self.__location

    @property
    def local_points(self):
        return self.__local_points

    @property
    def res_chance(self):
        return self.__res_chance

    @res_chance.setter
    def res_chance(self, value):
        self.__res_chance = value

    @property
    def work_chance(self):
        return self.__work_chance

    @work_chance.setter
    def work_chance(self, value):
        self.__work_chance = value

    @property
    def rec_chance(self):
        return self.__rec_chance

    @rec_chance.setter
    def rec_chance(self, value):
        self.__rec_chance = value

    def add_local_point(self, location: Location):
        self.__local_points.append(location)

    def to_dict(self):
        return {
            "name": self.__name,
            "location": self.__location.to_dict(),
            "local_points": [loc.to_dict() for loc in self.__local_points],
            "res_chance": self.__res_chance,
            "work_chance": self.__work_chance,
            "rec_chance": self.__rec_chance,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            location=Location.from_dict(data["location"]),
            local_points=[Location.from_dict(loc) for loc in data["local_points"]],
            res_chance=data["res_chance"],
            work_chance=data["work_chance"],
            rec_chance=data["rec_chance"],
        )

    def __str__(self):
        return f"Landmark: {self.__name}"

# Task 3: Create class Road
class Road:
    def __init__(
        self,
        start: Location,
        end: Location,
        max_speed_limit: int = 50,
        allowed_modes=None,
    ):
        self._start = start
        self._end = end
        self._max_speed_limit = max_speed_limit
        self._current_traffic = 0
        self._allowed_modes = (
            allowed_modes if allowed_modes is not None else []
        )

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def max_speed_limit(self):
        return self._max_speed_limit

    @property
    def current_traffic(self):
        return self._current_traffic

    @current_traffic.setter
    def current_traffic(self, value):
        self._current_traffic = value

    @property
    def allowed_modes(self):
        return self._allowed_modes

    @property
    def length(self):
        distance = (
            (self._end.x - self._start.x) ** 2 + (self._end.y - self._start.y) ** 2
        ) ** 0.5
        return distance

    @property
    def lanes(self):
        if self.length <= 4:
            return 2
        else:
            return 4

    @property
    def capacity(self):
        return self.lanes * self.length * 50000

    @property
    def speed_limit(self):
        half_capacity = self.capacity / 2
        if self.current_traffic < half_capacity:
            return self._max_speed_limit
        else:
            reduction_factor = (self._current_traffic - half_capacity) / half_capacity
            return self._max_speed_limit * (1 - reduction_factor)

    def to_dict(self):
        return {
            "start": self._start.to_dict(),
            "end": self._end.to_dict(),
            "max_speed_limit": self._max_speed_limit,
            "allowed_modes": list(self._allowed_modes),
            "current_traffic": self._current_traffic,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            start=Location.from_dict(data["start"]),
            end=Location.from_dict(data["end"]),
            max_speed_limit=data["max_speed_limit"],
            allowed_modes=data["allowed_modes"],
        )

    def __str__(self):
        return (
            f"Road from ({self._start}) to ({self._end})\n"
            f"Max Speed Limit: {self._max_speed_limit} km/h\n"
            f"Current traffic: {self._current_traffic} vehicles\n"
            f"Allowed Modes: {self._allowed_modes}\n"
            f"Length: {self.length:.2f} km\n"
            f"Lanes: {self.lanes}\n"
            f"Capacity: {self.capacity:.0f} vehicles\n"
            f"Speed limit: {self.speed_limit:.2f} km/h"
        )
    
    def __repr__(self):
        return f"Road({self._start} → {self._end}, {self.length:.1f}km, {self._allowed_modes})"

# TODO: Task 4: Implement the City class
class City:
    def __init__(self, name: str):
        self.name = name
        self.roads = []
        self.landmarks = {}
        self.network = None
        self.node_lookup: dict[str, Location] = {}
        self.road_index = {}

    def build_network(self):
        G = nx.Graph()
        self.node_lookup = {}

        for road in self.roads:
            for loc in (road.start, road.end):
                key = str(loc)
                if key not in self.node_lookup:
                    self.node_lookup[key] = loc
                    G.add_node((loc.x, loc.y))

            speed_kmh = road.speed_limit
            travel_time_minutes = (road.length / speed_kmh) * 60

            G.add_edge(
                (road.start.x, road.start.y),
                (road.end.x, road.end.y),
                length=road.length,
                speed_limit=speed_kmh,
                allowed_modes=road.allowed_modes,
                travel_time=travel_time_minutes,
            )
        self.network = G

    def find_road(self, start: Location, end: Location, allowed_modes: list):
        if start is None or end is None or not isinstance(start, Location) or not isinstance(end, Location):
            return None

        key = ((start.x, start.y), (end.x, end.y))
        road = self.road_index.get(key)

        if road and any(mode in road.allowed_modes for mode in allowed_modes):
            return road
        return None

    def find_landmark(self, name: str):
        return self.landmarks[name]

    def add_traffic(self, start: Location, end: Location, mode: str, count: int):
        road = self.find_road(start, end, [mode])
        if road is not None:
            road.current_traffic += count

    def clear_traffic(self):
        for road in self.roads:
            road.current_traffic = 0

    def add_road(self, road):
        self.roads.append(road)
        key = ((road.start.x, road.start.y), (road.end.x, road.end.y))
        self.road_index[key] = road
        key_rev = ((road.end.x, road.end.y), (road.start.x, road.start.y))
        self.road_index[key_rev] = road

    def add_landmark(self, landmark):
        self.landmarks[landmark.name] = landmark

# TODO: Task 5: Save and load cities in json files.
    def save_to_file(self, filename: str):
        data = {
            "name": self.name,
            "roads": [road.to_dict() for road in self.roads],
            "landmarks": [landmark.to_dict() for landmark in self.landmarks.values()]
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_from_data(cls, filename: str):
        with open(filename, "r") as f:
            data = json.load(f)

        city = cls(data["name"])

        for landmark_data in data["landmarks"]:
            landmark = cls._landmark_from_data(landmark_data)
            city.add_landmark(landmark)

        for road_data in data["roads"]:
            road = cls._road_from_data(road_data)
            city.add_road(road)

        city.build_network()
        return city

    @staticmethod
    def _parse_location(loc_data):
        """Parse Location from dict, handling both old and new formats."""
        if "_Location__x" in loc_data:
            return Location(loc_data["_Location__x"], loc_data["_Location__y"])
        return Location(loc_data["x"], loc_data["y"])

    @classmethod
    def _landmark_from_data(cls, data):
        location = cls._parse_location(data["location"])
        local_points = [cls._parse_location(loc) for loc in data["local_points"]]
        return Landmark(
            data["name"], location, local_points,
            data["res_chance"], data["work_chance"], data["rec_chance"]
        )

    @classmethod
    def _road_from_data(cls, data):
        start = cls._parse_location(data["start"])
        end = cls._parse_location(data["end"])
        road = Road(start, end, data["max_speed_limit"], data["allowed_modes"])
        road.current_traffic = data.get("current_traffic", 0)
        return road

# TODO: Task 9: NEW function for metro lines and traffic calculation
    def add_metro_lines(self, lines: dict):
        landmark_map = {landmark.name: landmark for landmark in self.landmarks.values()}
        for line_name, stops in lines.items():
            for i in range(len(stops) - 1):
                start_name = stops[i]
                end_name = stops[i + 1]
                start_landmark = landmark_map[start_name]
                end_landmark = landmark_map[end_name]
                metro_road = Road(
                    start=start_landmark.location,
                    end=end_landmark.location,
                    max_speed_limit=80,
                    allowed_modes=["metro"],
                )
                metro_road.current_traffic = 0
                self.add_road(metro_road)
        self.build_network()

    # Task 17 Add the calculate_traffic(trips) method in the class City
    def calculate_traffic(self, trips) -> None:
        for road in self.roads:
            road.current_traffic = 0

        car_types = {"car", "electric_car", "hybrid_car"}

        for trip in trips:
            if trip.vehicle_type in car_types:
                for road in trip.path:
                    road.current_traffic += 1

        self.build_network()

        for trip in trips:
            for road in trip.path:
                city_road = self.find_road(road.start, road.end, [trip.vehicle_type])
                if city_road is not None:
                    road.current_traffic = city_road.current_traffic

    # Task 10: Get information about all metro lines in the city
    def get_metro_info(self):
        metro_roads = [road for road in self.roads if "metro" in road.allowed_modes]

        if not metro_roads:
            return

        return {
            "total_roads": len(metro_roads),
            "total_distance": sum(road.length for road in metro_roads),
            "roads": metro_roads
        }

    def visualize_city(self, show_labels: bool = True, show_traffic: bool = False,
                      show_plots: bool = False, name: str = "map"):
        try:
            from .visualisation import visualize_city as viz_city
        except ImportError:
            from visualisation import visualize_city as viz_city

        viz_city(self, show_labels=show_labels, show_traffic=show_traffic,
                show_plots=show_plots, name=name)


# Test code
if __name__ == "__main__":
    # Create a small city with 2-3 landmarks, 2-3 local points per landmark, and a few roads
    city = City("TestCity")
    
    # Create Landmark items
    loc1 = Location(50, 50)
    landmark1 = Landmark("Downtown", loc1, 
                        [Location(49, 51), Location(51, 49)],
                        res_chance=0.2, work_chance=0.5, rec_chance=0.3)
    city.add_landmark(landmark1)

    loc2 = Location(60, 60)
    landmark2 = Landmark("Park", loc2,
                        [Location(59, 61), Location(61, 59), Location(60, 62)],
                        res_chance=0.0, work_chance=0.0, rec_chance=1.0)
    city.add_landmark(landmark2)
    
    loc3 = Location(55, 45)
    landmark3 = Landmark("ResidentialArea", loc3,
                        [Location(54, 46), Location(56, 44)],
                        res_chance=0.9, work_chance=0.1, rec_chance=0.0)
    city.add_landmark(landmark3)
    
    # Create roads connecting the landmarks
    road1 = Road(loc1, loc2, max_speed_limit=60, allowed_modes=["car", "bus", "bike"])
    road2 = Road(loc2, loc3, max_speed_limit=50, allowed_modes=["car", "bus"])
    road3 = Road(loc1, loc3, max_speed_limit=70, allowed_modes=["car", "bus", "bike"])
    road4 = Road(loc1, Location(49, 51), max_speed_limit=30, allowed_modes=["walk", "bike"])
    
    city.add_road(road1)
    city.add_road(road2)
    city.add_road(road3)
    city.add_road(road4)
    
    # Build the network
    city.build_network()
    
    # Save the city to file
    city.save_to_file("test_city.json")
    print("City saved to test_city.json")
    
    # Load the city from file
    loaded_city = City.load_from_data("test_city.json")
    print(f"City loaded from file: {loaded_city.name}")
    
    # Task 9: Add two metro lines
    metro_lines = {
        "Line1": ["Downtown", "Park", "ResidentialArea"],
        "Line2": ["Park", "Downtown", "ResidentialArea"]
    }
    loaded_city.add_metro_lines(metro_lines)
    print("Metro lines added:")
    print("Line1: Downtown -> Park -> ResidentialArea")
    print("Line2: Park -> Downtown -> ResidentialArea")
    
    # Display metro information
    print(f"Total roads before metro: 4")
    print(f"Total roads after metro: {len(loaded_city.roads)}")
    metro_count = sum(1 for road in loaded_city.roads if "metro" in road.allowed_modes)
    print(f"Metro roads: {metro_count}")
    
    # Visualize to verify metro lines (blue dashed lines represent metro)
    from visualisation import visualize_city
    visualize_city(loaded_city, show_plots=True)
    



def get_small_test_city():
    # Create a small test city with 2-3 landmarks and 2-3 local points per landmark
    viz_test_city = City("SmallTestCity")

    # Define landmarks and their local points
    landmarks_with_points = {
        "School": {
            "location": Location(20, 30),
            "local_points": [Location(18, 28), Location(22, 32)],  # 2 local points near school
            "res_chance": 0.8, "work_chance": 0.1, "rec_chance": 0.6
        },
        "Shopping Mall": {
            "location": Location(50, 50),
            "local_points": [Location(48, 48), Location(52, 50), Location(50, 52)],  # 3 local points
            "res_chance": 0.3, "work_chance": 0.2, "rec_chance": 0.9
        },
        "Hospital": {
            "location": Location(70, 40),
            "local_points": [Location(68, 38), Location(72, 42)],  # 2 local points
            "res_chance": 0.7, "work_chance": 0.8, "rec_chance": 0.1
        }
    }

    # Add landmarks to city
    for landmark_name, data in landmarks_with_points.items():
        viz_test_city.add_landmark(Landmark(
            landmark_name, 
            data["location"], 
            data["local_points"],
            data["res_chance"], 
            data["work_chance"], 
            data["rec_chance"]
        ))

    # Add roads connecting the points
    roads_config = [
        # School connections
        (Location(18, 28), Location(22, 32), 50),
        (Location(20, 30), Location(48, 48), 60),
        # Shopping Mall internal connections
        (Location(48, 48), Location(52, 50), 40),
        (Location(52, 50), Location(50, 52), 40),
        # Connections to Hospital
        (Location(50, 50), Location(68, 38), 55),
        (Location(68, 38), Location(72, 42), 50),
        # Additional cross connections
        (Location(22, 32), Location(50, 52), 65),
        (Location(52, 50), Location(72, 42), 60),
    ]

    for start, end, speed in roads_config:
        viz_test_city.add_road(Road(start, end, max_speed_limit=speed))
    viz_test_city.build_network()
    
    return viz_test_city

def get_city_test_data():
    """
    Returns test data for Task 4: (landmark1, landmark2, road1, road2)
    """
    landmark1 = Landmark("School", Location(20, 30), [], 0.8, 0.1, 0.6)
    landmark2 = Landmark("Hospital", Location(40, 50), [], 0.7, 0.8, 0.2)
    
    test_road1 = Road(Location(0, 0), Location(10, 10), max_speed_limit=50)
    test_road2 = Road(Location(10, 10), Location(20, 20), max_speed_limit=60)
    
    return landmark1, landmark2, test_road1, test_road2
