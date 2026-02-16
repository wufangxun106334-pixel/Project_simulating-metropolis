import random
from dataclasses import asdict
import networkx as nx
try:
    from .location import Location
    from .city import Road
except (ImportError, ValueError):
    try:
        from utils.location import Location
        from utils.city import Road
    except ImportError:
        from location import Location
        from city import Road

class MovementGenerator:
    # Fallback mode priority: if preferred modes fail, try these in order
    FALLBACK_MODES = ["walk", "car", "bus", "bike"]
    
    def __init__(self, city, population):
        self.city = city
        self.population = population

    @staticmethod
    def _euclidean_heuristic(u, v, graph):
        ux, uy = u
        vx, vy = v
        return ((ux - vx)**2 + (uy - vy)**2)**0.5

    def _get_mode_subgraph(self, modes: list[str]):
        #  Treat electric_car and hybrid_car as car for pathfinding
        if "electric_car" in modes or "hybrid_car" in modes:
            modes = list(set(modes) - {"electric_car", "hybrid_car"})
            modes.append("car")
        # Filter edges that allow at least one of the modes
        valid_edges = [
            (u, v) for u, v, data in self.city.network.edges(data=True)
            if any(m in data["allowed_modes"] for m in modes)
        ]
        return self.city.network.edge_subgraph(valid_edges)

    def _find_nearest_node(self, location, graph):
        """Find the nearest node in the graph to the given location"""
        if not graph.nodes():
            return None
        
        nearest_node = min(
            graph.nodes(),
            key=lambda node: (node[0] - location.x)**2 + (node[1] - location.y)**2
        )
        return nearest_node

    def check_network_connectivity(self, modes: list[str] = None) -> dict:
        """
        Check if the network is connected for given transportation modes.
        Returns a dict with connectivity info and any disconnected components.
        """
        if not self.city.network:
            self.city.build_network()
        
        if modes is None:
            # Check full network
            graph = self.city.network
        else:
            graph = self._get_mode_subgraph(modes)
        
        is_connected = nx.is_connected(graph) if graph.number_of_nodes() > 0 else False
        components = list(nx.connected_components(graph)) if graph.number_of_nodes() > 0 else []
        
        return {
            "is_connected": is_connected,
            "num_components": len(components),
            "num_nodes": graph.number_of_nodes(),
            "num_edges": graph.number_of_edges(),
            "components": components if len(components) <= 5 else components[:5]  # Limit output
        }

    def _try_find_path(self, start, end, modes):
        """
        Internal method to find path with given modes.
        Returns (path, selected_modes) or (None, modes) if no path found.
        """
        G_mode = self._get_mode_subgraph(modes)
        
        if G_mode.number_of_nodes() == 0:
            return None, modes

        try:
            # Find actual nodes to use if start/end are not in the graph
            source_node = (start.x, start.y) if (start.x, start.y) in G_mode else self._find_nearest_node(start, G_mode)
            target_node = (end.x, end.y) if (end.x, end.y) in G_mode else self._find_nearest_node(end, G_mode)
            
            if source_node is None or target_node is None:
                return None, modes
            
            # Check if source and target are in the same connected component
            if not nx.has_path(G_mode, source_node, target_node):
                return None, modes
            
            path = nx.astar_path(
                G_mode,
                source=source_node,
                target=target_node,
                weight="travel_time",
                heuristic=lambda u, v: self._euclidean_heuristic(u, v, G_mode)
            )
            loc_path = [Location(p[0], p[1]) for p in path]
            # Split path into road segments
            road_path = [self.city.find_road(loc_path[i], loc_path[i+1], modes) for i in range(0, len(loc_path)-1)]
            # Check for None in road_path
            if any(r is None for r in road_path):
                return None, modes
            # Union of all allowed modes along the route
            selected_modes = set().union(*(r.allowed_modes for r in road_path if r))
            # Select modes that are also in the person's available modes
            selected_modes = selected_modes.intersection(set(modes))
            return road_path, selected_modes
        
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None, modes

    def find_path(self, start, end, modes):
        """
        A* pathfinding algorithm with fallback mechanism.
        If the preferred modes fail, automatically tries fallback modes.
        """
        if not self.city.network:
            self.city.build_network()
        
        # First, try with the original modes
        path, selected_modes = self._try_find_path(start, end, modes)
        if path is not None:
            return path, selected_modes
        
        # Fallback: try adding walk mode if not present
        modes_with_walk = list(set(modes) | {"walk"})
        if modes_with_walk != list(modes):
            path, selected_modes = self._try_find_path(start, end, modes_with_walk)
            if path is not None:
                return path, selected_modes
        
        # Fallback: try each fallback mode individually
        for fallback_mode in self.FALLBACK_MODES:
            if fallback_mode not in modes:
                fallback_modes = [fallback_mode]
                path, selected_modes = self._try_find_path(start, end, fallback_modes)
                if path is not None:
                    return path, selected_modes
        
        # Last resort: try all non-metro modes
        all_basic_modes = ["walk", "car", "bike", "bus"]
        path, selected_modes = self._try_find_path(start, end, all_basic_modes)
        if path is not None:
            return path, selected_modes
        
        # No path found with any mode
        return None, modes

    def run_day(self, day_type="weekday"):
        movements = []
        for person in self.population.people:
            routine = person.daily_routine.get(day_type, [])
            rec_choice = None
            for i in range(len(routine) - 1):
                start = routine[i]
                end = routine[i + 1]
                
                if start == "home":
                    start_location = person.home_location
                elif start == "work":
                    start_location = person.work_location
                elif start == "rec":
                    start_location = rec_choice if rec_choice else random.choice(person.rec_location)
                    rec_choice = None  # reset after use
                else:
                    raise ValueError(f"Unknown location type: {start}")

                if end == "home":
                    end_location = person.home_location
                elif end == "work":
                    end_location = person.work_location
                elif end == "rec":
                    end_location = rec_choice if rec_choice else random.choice(person.rec_location)
                    rec_choice = end_location  # remember for next trip
                else:
                    continue
                
                # print(f"Person {person.id} from {start_location} to {end_location} by {person.transport_modes}")
                path, modes_selected = self.find_path(start_location, end_location, person.transport_modes)
                if path is None or any(segment is None for segment in path):
                    raise ValueError(f"No road segment found for user {person.id}, Start:{start_location}, End:{end_location}, Modes:{person.transport_modes}")

                movement = {
                    "person_id": person.id,
                    "start": start_location,
                    "end": end_location,
                    "mode": modes_selected,
                    "path": path
                }
                movements.append(movement)
        return movements
    
    @staticmethod
    def save_movements(movements, filename="daily_movements.json", compact=True):
        """
        Save movements to JSON file.
        
        Args:
            movements: List of movement dictionaries
            filename: Output filename
            compact: If True, save only essential data (smaller file size)
                    If False, save full road details (larger file, needed for traffic calc)
        """
        import json
        
        if compact:
            # Compact format: only save path as list of (start, end) coordinates
            # Reduces file size by ~90%
            data = [{
                "person_id": m["person_id"],
                "start": [round(m["start"].x, 2), round(m["start"].y, 2)],
                "end": [round(m["end"].x, 2), round(m["end"].y, 2)],
                "mode": list(m["mode"]),
                "path": [[round(r.start.x, 2), round(r.start.y, 2), 
                          round(r.end.x, 2), round(r.end.y, 2)] for r in m["path"]]
            } for m in movements]
        else:
            # Full format: save complete road details
            data = [{
                "person_id": m["person_id"],
                "start": {"x": m["start"].x, "y": m["start"].y},
                "end": {"x": m["end"].x, "y": m["end"].y},
                "mode": list(m["mode"]),
                "path": [ 
                    {
                        "start": {"x": road.start.x, "y": road.start.y}, 
                        "end": {"x": road.end.x, "y": road.end.y}, 
                        "max_speed_limit": road.max_speed_limit, 
                        "allowed_modes": list(road.allowed_modes),
                        "current_traffic": road.current_traffic
                    } for road in m["path"]
                ]
            } for m in movements]
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_movements(cls, filename="daily_movements.json"):
        import json
        # try to load movements from a file if it exists else return None
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            movements = []
            for m in data:
                path = []
                for road in m["path"]:
                    road_segment = Road(Location(**road["start"]), 
                                        Location(**road["end"]), 
                                        road["max_speed_limit"], 
                                        road["allowed_modes"])
                    road_segment.current_traffic = road["current_traffic"]
                    path.append(road_segment)
                movement = {
                    "person_id": m["person_id"],
                    "start": Location(**m["start"]),
                    "end": Location(**m["end"]),
                    "mode": set(m["mode"]),
                    "path": path
                }
                movements.append(movement)
            return movements
        except FileNotFoundError:
            return None
