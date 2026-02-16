from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

try:
    from .population import Population
    from .city import City
except (ImportError, ValueError):
    try:
        from utils.population import Population
        from utils.city import City
    except ImportError:
        from population import Population
        from city import City

# Create N visually distinct colors
def get_colors(n):
    cmap = cm.get_cmap('tab20', n)  # or 'hsv', 'Set3', 'Accent'
    return [cmap(i) for i in range(n)]

def visualize_city(city: City, show_labels=True, show_traffic=False, show_plots=False, name="map"):
    """
    Visualize city roads, landmarks, and neighborhoods
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot roads
    for road in city.roads:
        x_coords = [road.start.x, road.end.x]
        y_coords = [road.start.y, road.end.y]
        if "metro" in road.allowed_modes:
            ax.plot(x_coords, y_coords, color="blue", linewidth=road.lanes/2, linestyle='--', zorder=1)
        else:
            if show_traffic:
                cmap = cm.get_cmap('Reds')
                color = cmap(min(1.0, road.speed_limit/road.max_speed_limit))
                ax.plot(x_coords, y_coords, color=color, linewidth=road.lanes/2, alpha=0.8, zorder=1)
            else:
                ax.plot(x_coords, y_coords, color="gray", linewidth=road.lanes/2, alpha=0.5, zorder=1)
    
    neighborhood_colors = get_colors(len(city.landmarks.values()))
    landmark_neighborhood = {}
    for i, landmark in enumerate(city.landmarks.values()):
        cluster_id = i % len(neighborhood_colors)
        landmark_neighborhood[i] = cluster_id

    # Plot landmarks
    for i, landmark in enumerate(city.landmarks.values()):
        cluster_id = landmark_neighborhood[i]
        x = landmark.location.x
        y = landmark.location.y
        ax.scatter(
            x, y,
            s=100,
            color=neighborhood_colors[cluster_id],
            label=f"{landmark.name}" if show_labels else "",
            edgecolor="black",
            zorder=2
        )
        if show_labels:
            ax.text(x + 1, y + 1, landmark, fontsize=12, ha='left', va='bottom', 
                    bbox=dict(
                        boxstyle='round,pad=0.3',
                        facecolor='white',
                        edgecolor='black',
                        linewidth=1
                    )
                )

    # Customize plot
    ax.set_title(f"City Map: {city.name}", fontsize=16, weight='bold')
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_facecolor("#f3f3f3")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
    ax.set_xticks(range(0, 101, 10))
    ax.set_yticks(range(0, 101, 10))

    # Avoid duplicate labels in legend
    if show_labels:
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys())
    if show_plots:
        plt.show()
    else:
        plt.savefig(f"{city.name}_{name}.png")

def visualize_population(city: City, population: Population, show_plots=False, name="population_map"):
    """
    Visualize population on the map. Overlays people homes as dots on city map.
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot city roads
    for road in city.roads:
        x_coords = [road.start.x, road.end.x]
        y_coords = [road.start.y, road.end.y]
        if "metro" in road.allowed_modes:
            ax.plot(x_coords, y_coords, color="blue", linewidth=road.lanes/2, linestyle='--', zorder=1)
        else:
            ax.plot(x_coords, y_coords, color="gray", linewidth=road.lanes/2, zorder=1)

    neighborhood_colors = get_colors(len(city.landmarks.values()))
    landmark_neighborhood = {}
    for i, landmark in enumerate(city.landmarks.values()):
        cluster_id = i % len(neighborhood_colors)
        landmark_neighborhood[i] = cluster_id

    # Plot landmarks
    for i, landmark in enumerate(city.landmarks.values()):
        cluster_id = landmark_neighborhood[i]
        x = landmark.location.x
        y = landmark.location.y
        ax.scatter(
            x, y,
            s=100,
            color=neighborhood_colors[cluster_id],
            label=f"{landmark.name}",
            edgecolor="black",
            zorder=3
        )
        ax.text(x + 1, y + 1, landmark, fontsize=12, ha='left', va='bottom', 
                bbox=dict(
                    boxstyle='round,pad=0.3',
                    facecolor='white',
                    edgecolor='black',
                    linewidth=1
                )
            )

    # Plot people homes
    for person in population.get_all_people():
        home_location = person.home_location
        ax.scatter(
            home_location.x, home_location.y,
            s=20,
            color="red",
            alpha=0.6,
            zorder=2
        )

    # Customize plot
    ax.set_title(f"City Map with Population: {city.name}", fontsize=16, weight='bold')
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_facecolor("#f3f3f3")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
    ax.set_xticks(range(0, 101, 10))
    ax.set_yticks(range(0, 101, 10))

    # Avoid duplicate labels in legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())
    if show_plots:
        plt.show()
    else:
        plt.savefig(f"{city.name}_{name}.png")

def visualize_simulation_results(scenarios: dict[str, dict], show_plots=False, name="simulation_comparison"):
    """
    Visualize travel and emission statistics across multiple scenarios.
    """
    # === Overall travel time ===
    names = list(scenarios.keys())
    total_trips = [s["total_trips"] for s in scenarios.values()]
    avg_times = [s["total_average_travel_time"] for s in scenarios.values()]
    total_co2 = [s["total_co2_emissions"] for s in scenarios.values()]

    fig = plt.figure(figsize=(16, 14))
    gs = gridspec.GridSpec(4, 2, width_ratios=[1, 1], height_ratios=[1, 1, 1, 1], wspace=0.1, hspace=0.5)

    ax1 = fig.add_subplot(gs[0, 0])  # row 0, col 0
    ax2 = fig.add_subplot(gs[0, 1])  # row 0, col 1
    ax3 = fig.add_subplot(gs[1, 0])  # row 1, col 0
    ax4 = fig.add_subplot(gs[1, 1])  # row 1, col 1
    ax5 = fig.add_subplot(gs[2, 0])  # row 2, col 0
    ax6 = fig.add_subplot(gs[2, 1])  # row 2, col 1
    ax7 = fig.add_subplot(gs[3, 0])  # row 3, col 0
    ax8 = fig.add_subplot(gs[3, 1])  # row 3, col 1

    # 00. Total Trips
    ax1.bar(names, total_trips, color="salmon", edgecolor="black")
    ax1.set_title("Total Trips per Scenario")
    ax1.set_ylabel("Number of Trips")
    
    # 01. Overall Average Travel Time per Scenario
    ax2.bar(names, avg_times, color="skyblue", edgecolor="black")
    ax2.set_title("Overall Average Travel Time per Scenario")
    ax2.set_ylabel("Average Time (minutes)")
    ax2.set_ylim(0, max(avg_times) * 1.2 if avg_times else 1)
    # 添加数值标签
    for i, v in enumerate(avg_times):
        ax2.text(i, v + max(avg_times)*0.02, f"{v:.1f} min", ha='center', va='bottom', fontsize=9)

    # 11. Total trips per vehicle type
    # Collect all vehicle types from all scenarios
    all_vehicle_types = set()
    for s in scenarios.values():
        all_vehicle_types.update(s["trips_per_vehicle_type"].keys())
    vehicle_types = sorted(list(all_vehicle_types))
    x = np.arange(len(vehicle_types))
    width = 0.2

    for i, (label, s) in enumerate(scenarios.items()):
        offsets = x + (i - len(scenarios)/2) * width
        values = [s["trips_per_vehicle_type"].get(vtype, 0) for vtype in vehicle_types]
        ax3.bar(offsets, values, width, label=label)
    ax3.set_xticks(x)
    ax3.set_xticklabels(vehicle_types)
    ax3.set_title("Total trips per Vehicle Type")
    ax3.legend()

    # 12. Average travel time per vehicle type
    # Collect all vehicle types from all scenarios
    all_vehicle_types = set()
    for s in scenarios.values():
        all_vehicle_types.update(s["travel_time_per_vehicle_type"].keys())
    vehicle_types = sorted(list(all_vehicle_types))
    x = np.arange(len(vehicle_types))
    width = 0.2

    for i, (label, s) in enumerate(scenarios.items()):
        offsets = x + (i - len(scenarios)/2) * width
        values = [s["travel_time_per_vehicle_type"].get(vtype, 0) for vtype in vehicle_types]
        ax4.bar(offsets, values, width, label=label)
    ax4.set_xticks(x)
    ax4.set_xticklabels(vehicle_types)
    ax4.set_title("Average Travel Time per Vehicle Type")
    ax4.legend()

    # 20. Total CO2 emissions
    ax5.bar(names, total_co2, color="lightgreen", edgecolor="black")
    ax5.set_title("Total CO₂ Emissions per Scenario (kg)")
    ax5.set_ylabel("kg")
    
    # 21. CO2 per vehicle type
    # Collect all vehicle types from all scenarios
    all_vehicle_types = set()
    for s in scenarios.values():
        all_vehicle_types.update(s["co2_emissions_per_vehicle"].keys())
    vehicle_types = sorted(list(all_vehicle_types))
    x = np.arange(len(vehicle_types))
    width = 0.2

    for i, (label, s) in enumerate(scenarios.items()):
        offsets = x + (i - len(scenarios)/2) * width
        values = [s["co2_emissions_per_vehicle"].get(vtype, 0) for vtype in vehicle_types]
        ax6.bar(offsets, values, width, label=label)
    ax6.set_xticks(x)
    ax6.set_xticklabels(vehicle_types)
    ax6.set_title(f"CO₂ per Vehicle Type in Each Scenario (g/km or kg/trip)")
    ax6.set_ylabel("g/km or kg/trip")

    # 30. Users per vehicle type
    # Collect all vehicle types from all scenarios
    all_vehicle_types = set()
    for s in scenarios.values():
        all_vehicle_types.update(s["users_per_vehicle_type"].keys())
    vehicle_types = sorted(list(all_vehicle_types))
    x = np.arange(len(vehicle_types))
    width = 0.2

    for i, (label, s) in enumerate(scenarios.items()):
        offsets = x + (i - len(scenarios)/2) * width
        values = [s["users_per_vehicle_type"].get(vtype, 0) for vtype in vehicle_types]
        ax7.bar(offsets, values, width, label=label)
    ax7.set_xticks(x)
    ax7.set_xticklabels(vehicle_types)
    ax7.set_title("Users per transportation mode")
    ax7.legend()

    # 31. Vehicle counts per scenario (drop walking)
    scenarios_no_walk = {
        label: {
            **s,
            "vehicle_counts": {k: v for k, v in s["vehicle_counts"].items() if k != "walk"}
        }
        for label, s in scenarios.items()
    }
    # Collect all vehicle types from all scenarios
    all_vehicle_types = set()
    for s in scenarios_no_walk.values():
        all_vehicle_types.update(s["vehicle_counts"].keys())
    vehicle_types = sorted(list(all_vehicle_types))
    x = np.arange(len(vehicle_types))
    width = 0.2

    for i, (label, s) in enumerate(scenarios_no_walk.items()):
        offsets = x + (i - len(scenarios_no_walk)/2) * width
        values = [s["vehicle_counts"].get(vtype, 0) for vtype in vehicle_types]
        ax8.bar(offsets, values, width, label=label)
    ax8.set_xticks(x)
    ax8.set_xticklabels(vehicle_types)
    ax8.set_title("Number of Vehicles per type")
    ax8.legend()

    plt.tight_layout()
    if show_plots:
        plt.show()
    else:
        filename = f"comparison_{name}.png"
        plt.savefig(filename)
        print(f"✓ Visualization saved to {filename}")
    plt.close()