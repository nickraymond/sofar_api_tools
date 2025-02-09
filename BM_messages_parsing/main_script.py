# filename: main_script.py
# description: make multiple API call for wave and sensor data for unit with load cell and current meter, then plot waves, currents, and force
# TODO
# update logic to know difference between data types, and add sensor position, units, and data_type to  JSON parsing for managed sensors
import pytz

import os
import csv
import re
import requests
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Slider
import pandas as pd
from config import API_TOKEN
from spot_config import SPOTTER_CONFIGS

# Conversion factors
meter_to_feet = 3.28084
m_per_s_to_knots = 1.94384
newton_to_lbf = 0.224809


# Ensure the parsed_data directory exists
if not os.path.exists('parsed_data'):
    os.makedirs('parsed_data')

def api_login(api_url):
    """Fetch data from the Sofar API."""
    response = requests.get(api_url)
    if response.status_code == 200:
        print(f"Successfully fetched data from API: {api_url}")
        return response.json()
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        raise Exception("API request failed.")


def fetch_data_in_chunks(start_datetime, end_datetime, spotter_id, chunk_size_days=5, data_type="wave"):
    """Fetch data from the API in chunks of `chunk_size_days` days and combine into a single JSON object."""
    # Initialize combined data structure
    if data_type == "wave":
        combined_data = {"data": {"waves": [], "wind": [], "surfaceTemp": [], "barometerData": []}}
    elif data_type == "sensor":
        combined_data = {"data": []}  # Flat structure for sensor data
    else:
        raise ValueError(f"Invalid data_type: {data_type}")

    current_start = start_datetime

    while current_start < end_datetime:
        current_end = current_start + timedelta(days=chunk_size_days)
        if current_end > end_datetime:
            current_end = end_datetime

        chunk_start = current_start.strftime("%Y-%m-%dT%H:%M:%SZ")
        chunk_end = current_end.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Construct the appropriate API URL
        if data_type == "wave":
            api_url = (
                f"https://api.sofarocean.com/api/wave-data?spotterId={spotter_id}&startDate={chunk_start}"
                f"&endDate={chunk_end}&token={API_TOKEN}&includeWindData=true&includeSurfaceTempData=true"
                f"&includeBarometerData=true&limit=500&processingSources=all"
            )
        elif data_type == "sensor":
            api_url = (
                f"https://api.sofarocean.com/api/sensor-data?spotterId={spotter_id}&startDate={chunk_start}"
                f"&endDate={chunk_end}&token={API_TOKEN}&limit=500"
            )
        else:
            raise ValueError(f"Invalid data_type: {data_type}")

        print(f"Fetching {data_type} data for {chunk_start} to {chunk_end}...")
        chunk_data = api_login(api_url)

        if "data" in chunk_data:
            if data_type == "wave":
                # Combine wave data by appending to corresponding lists
                for key in combined_data["data"]:
                    if key in chunk_data["data"]:
                        combined_data["data"][key].extend(chunk_data["data"][key])
            elif data_type == "sensor":
                # Combine sensor data by appending to the flat list
                combined_data["data"].extend(chunk_data["data"])
        else:
            print(f"No {data_type} data returned for {chunk_start} to {chunk_end}.")

        current_start = current_end

    return combined_data


def decode_hex_to_ascii(hex_string):
    """Decode a hex string to ASCII format, handling non-printable characters."""
    try:
        # Convert hex string to bytes
        byte_value = bytes.fromhex(hex_string)
        # Decode bytes to string, ignoring errors
        decoded_str = byte_value.decode('utf-8', errors='ignore')
        # Remove any trailing non-printable characters or whitespace
        return decoded_str.strip()
    except ValueError:
        return "Invalid hex data"

def extract_force_values(message):
    """Extract min, max, and mean force values from a message string."""
    min_force = max_force = mean_force = None
    min_match = re.search(r"min force:\s*(-?\d+\.\d+)", message)
    max_match = re.search(r"max force:\s*(-?\d+\.\d+)", message)
    mean_match = re.search(r"mean force:\s*(-?\d+\.\d+)", message)
    if min_match:
        min_force = float(min_match.group(1))
    if max_match:
        max_force = float(max_match.group(1))
    if mean_match:
        mean_force = float(mean_match.group(1))
    return min_force, max_force, mean_force

def process_smart_mooring_data(spotter_id, json_data):
    """Process 'sensor-data' JSON and save parsed data by Node ID."""
    grouped_data = defaultdict(list)
    unique_node_ids = set()
    for entry in json_data['data']:
        node_id = entry.get('bristlemouth_node_id', 'Unknown_ID')
        data_type = entry.get("data_type_name", "")
        value = entry.get("value", "")
        timestamp = entry.get("timestamp")

        decoded_value = decode_hex_to_ascii(value) if entry.get("unit_type") == "binary" else value
        min_force, max_force, mean_force = None, None, None
        if data_type == "binary_hex_encoded" and "force" in decoded_value:
            min_force, max_force, mean_force = extract_force_values(decoded_value)

        parsed_entry = {
            "timestamp": timestamp,
            "data_type_name": data_type,
            "latitude": entry.get("latitude"),
            "longitude": entry.get("longitude"),
            "decoded_value": decoded_value,
            "min_force": min_force,
            "max_force": max_force,
            "mean_force": mean_force
        }
        grouped_data[node_id].append(parsed_entry)
        unique_node_ids.add(node_id)

        # Save each node's data to a CSV in a subfolder
        node_directory = os.path.join('parsed_data', node_id)
        if not os.path.exists(node_directory):
            os.makedirs(node_directory)

        # Save the parsed data to CSV
        csv_filename = os.path.join(node_directory, f"{node_id}_smart_mooring.csv")
        save_to_csv(parsed_entry, csv_filename, header=True if not os.path.exists(csv_filename) else False)

    # Print the unique node IDs found
    print("Unique Node IDs found:", unique_node_ids)
    return grouped_data, unique_node_ids

def process_wave_data(spotter_id, api_data_wave):
    """Process wave data, including wave, wind, sea surface temperature, and barometer data."""
    base_directory = "parsed_data/spotter_wave"
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)

    wave_csv = os.path.join(base_directory, "waves.csv")
    wind_csv = os.path.join(base_directory, "wind.csv")
    temp_csv = os.path.join(base_directory, "sea_surface_temp.csv")
    baro_csv = os.path.join(base_directory, "barometer.csv")

    try:
        if "waves" in api_data_wave["data"]:
            for entry in api_data_wave["data"]["waves"]:
                save_to_csv(entry, wave_csv, header=not os.path.exists(wave_csv))

        if "wind" in api_data_wave["data"]:
            for entry in api_data_wave["data"]["wind"]:
                save_to_csv(entry, wind_csv, header=not os.path.exists(wind_csv))

        if "surfaceTemp" in api_data_wave["data"]:
            for entry in api_data_wave["data"]["surfaceTemp"]:
                save_to_csv(entry, temp_csv, header=not os.path.exists(temp_csv))

        if "barometerData" in api_data_wave["data"]:
            for entry in api_data_wave["data"]["barometerData"]:
                save_to_csv(entry, baro_csv, header=not os.path.exists(baro_csv))

    except KeyError as e:
        print(f"Error: Data type {e} not found in wave data response.")

    print("Wave data processing complete. CSV files saved.")

def save_to_csv(data, csv_filename, header=True):
    """Save individual entries to CSV with escape character handling."""
    fieldnames = data.keys()
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
        if header:
            writer.writeheader()
        writer.writerow(data)


def plot_data(grouped_data, unique_node_ids, wave_data, spotter_id):
    """Generate time series plots for significant wave height, current speed, sensor tilt, and force."""
    marker_size = 2
    line_alpha = 0.5
    scatter_alpha = 1.0
    plt.rcParams['font.family'] = 'Arial'  # or 'Roboto'

    # Color style guide follow Sofar Dashboard
    color_blue_bright = '#0066FF'
    color_blue_light = '#1ca8dd'
    color_blue_deep = '#0050A0' ##0000CD'
    color_brown_light = '#8B4513'
    color_brown_dark = '#A52A2A'
    color_green_dark = '#228B22'

    data_line_color = color_blue_light  # Soft cyan/blue color
    std_fill_color = color_blue_light   # Using the same color but with alpha for transparency in fill

    fig, axs = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
    fig.suptitle(f"Time Series Data for Spotter ID: {spotter_id}", fontsize=16)

    # Conversion factors
    meter_to_feet = 3.28084
    m_per_s_to_knots = 1.94384
    newton_to_lbf = 0.224809
    rad_to_deg = 57.2958  # Conversion from radians to degrees

    # Plot 1: Significant Wave Height with secondary y-axis in feet
    wave_df = pd.DataFrame(wave_data["waves"])
    wave_df["timestamp"] = pd.to_datetime(wave_df["timestamp"])
    wave_height_m = wave_df["significantWaveHeight"]
    # Plot the line with a lower alpha
    axs[0].plot(wave_df["timestamp"], wave_height_m, color=color_blue_light, linestyle='-', alpha=line_alpha,label="Significant Wave Height (m)")

    # Plot the markers with a higher alpha
    axs[0].scatter(wave_df["timestamp"], wave_height_m, color=color_blue_light, marker='o', s=marker_size ** 2, alpha=scatter_alpha)  # Adjust `s` for marker size
    axs[0].set_ylabel("Wave Height (m)", color='black')
    axs[0].tick_params(axis='y', labelcolor='black')

    ax_wave_feet = axs[0].twinx()
    ax_wave_feet.set_ylabel("Wave Height (ft)", color='black')
    ax_wave_feet.set_ylim(wave_height_m.min() * meter_to_feet, wave_height_m.max() * meter_to_feet)
    ax_wave_feet.tick_params(axis='y', labelcolor='black')
    axs[0].legend(loc="upper left")

    for node_id in unique_node_ids:
        node_data = pd.DataFrame(grouped_data[node_id])
        node_data["timestamp"] = pd.to_datetime(node_data["timestamp"])

        # Plot 2: Current Speed with secondary y-axis in knots, showing standard deviation shading
        speed_data = node_data[node_data["data_type_name"] == "aanderaa_abs_speed_mean_15bits"]
        std_data = node_data[node_data["data_type_name"] == "aanderaa_abs_speed_std_15bits"]
        if not speed_data.empty and not std_data.empty:
            merged_speed_data = pd.merge(speed_data, std_data, on="timestamp", suffixes=('_mean', '_std'))
            speed_mean = merged_speed_data["decoded_value_mean"].astype(float) * 0.01
            speed_std = merged_speed_data["decoded_value_std"].astype(float) * 0.01

            # axs[1].plot(merged_speed_data["timestamp"], speed_mean, color=color_blue_light, marker='o', linestyle='-', markersize=marker_size, label=f"{node_id} - Current Speed (m/s)", alpha=line_alpha)

            axs[1].plot(merged_speed_data["timestamp"], speed_mean, color=color_blue_light, linestyle='-', label=f"{node_id} - Current Speed (m/s)", alpha=line_alpha)
            axs[1].scatter(merged_speed_data["timestamp"], speed_mean, color=color_blue_light, marker='o', s=marker_size ** 2, alpha=scatter_alpha)

            axs[1].fill_between(merged_speed_data["timestamp"], speed_mean - speed_std, speed_mean + speed_std, color=color_blue_light, alpha=0.2, label="Std Dev")
            axs[1].set_ylabel("Current Speed (m/s)", color='black')
            axs[1].tick_params(axis='y', labelcolor='black')

            ax_speed_knots = axs[1].twinx()
            ax_speed_knots.set_ylabel("Current Speed (knots)", color='black')
            ax_speed_knots.set_ylim(axs[1].get_ylim()[0] * m_per_s_to_knots, axs[1].get_ylim()[1] * m_per_s_to_knots)
            ax_speed_knots.tick_params(axis='y', labelcolor='black')
            axs[1].legend(loc="upper left")

        tilt_data = node_data[node_data["data_type_name"] == "aanderaa_abs_tilt_mean_8bits"]
        tilt_std_data = node_data[node_data["data_type_name"] == "aanderaa_std_tilt_mean_8bits"]

        if not tilt_data.empty and not tilt_std_data.empty:
            merged_tilt_data = pd.merge(tilt_data, tilt_std_data, on="timestamp", suffixes=('_mean', '_std'))
            tilt_mean_rad = merged_tilt_data["decoded_value_mean"].astype(float)
            tilt_std_rad = merged_tilt_data["decoded_value_std"].astype(float)

            # Plot the mean tilt in radians
            axs[2].plot(merged_tilt_data["timestamp"], tilt_mean_rad, color=color_blue_light, linestyle='-',
                        label=f"{node_id} - Sensor Tilt (radians)", alpha=line_alpha)
            axs[2].scatter(merged_tilt_data["timestamp"], tilt_mean_rad, color=color_blue_light, marker='o',
                           s=marker_size ** 2, alpha=scatter_alpha)
            axs[2].fill_between(merged_tilt_data["timestamp"], tilt_mean_rad - tilt_std_rad,
                                tilt_mean_rad + tilt_std_rad, color=color_blue_light, alpha=0.2, label="Std Dev")
            axs[2].set_ylabel("Sensor Tilt (radians)", color='black')
            axs[2].tick_params(axis='y', labelcolor='black')

            # Create secondary y-axis for degrees
            ax_tilt_deg = axs[2].twinx()
            ax_tilt_deg.set_ylabel("Sensor Tilt (degrees)", color='black')
            ax_tilt_deg.set_ylim(axs[2].get_ylim()[0] * rad_to_deg, axs[2].get_ylim()[1] * rad_to_deg)
            ax_tilt_deg.tick_params(axis='y', labelcolor='black')
            axs[2].legend(loc="upper left")
            # Plot 3: Sensor Tilt in radians with secondary y-axis in degrees


        # Plot 4: Force with secondary y-axis in pounds-force
        force_data = node_data.dropna(subset=["mean_force", "max_force"])
        if not force_data.empty:
            mean_force = force_data["mean_force"]
            max_force = force_data["max_force"]
            #axs[3].plot(force_data["timestamp"], mean_force, color=color_blue_light, marker='o', linestyle='-', markersize=marker_size, label=f"{node_id} - Mean Force (N)", alpha=line_alpha)
            axs[3].plot(force_data["timestamp"], mean_force, color=color_blue_light, linestyle='-', label=f"{node_id} - Mean Force (N)", alpha=line_alpha)
            axs[3].scatter(force_data["timestamp"], mean_force, color=color_blue_light, marker='o', s=marker_size ** 2, alpha=scatter_alpha)


            #axs[3].plot(force_data["timestamp"], max_force, color=color_blue_bright, marker='o', label=f"{node_id} - Max Force (N)", markersize=marker_size, alpha=line_alpha)
            axs[3].plot(force_data["timestamp"], max_force, color=color_blue_bright, label=f"{node_id} - Max Force (N)", markersize=marker_size, alpha=line_alpha)
            axs[3].scatter(force_data["timestamp"], max_force, color=color_blue_bright, marker='o', s=marker_size ** 2, alpha=scatter_alpha)


            axs[3].set_ylabel("Force (N)", color='black')
            axs[3].tick_params(axis='y', labelcolor='black')

            ax_force_lbf = axs[3].twinx()
            ax_force_lbf.set_ylabel("Force (lbf)", color='black')
            ax_force_lbf.set_ylim(axs[3].get_ylim()[0] * newton_to_lbf, axs[3].get_ylim()[1] * newton_to_lbf)
            ax_force_lbf.tick_params(axis='y', labelcolor='black')
            axs[3].legend(loc="upper left")

    # Set the x-axis label for the last plot
    axs[3].set_xlabel("Time UTC")
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()


def plot_gps_coordinates(wave_data, spotter_id):
    """Plot GPS coordinates from Spotter wave data with specific formatting and dual scrubbers."""

    # Check if wave_data contains the expected structure
    if "waves" not in wave_data:
        print("Error: 'waves' key not found in wave_data.")
        return

    # Extract latitude, longitude, and timestamp values
    gps_entries = [entry for entry in wave_data["waves"] if "latitude" in entry and "longitude" in entry]
    latitudes = [entry["latitude"] for entry in gps_entries]
    longitudes = [entry["longitude"] for entry in gps_entries]
    timestamps = [entry["timestamp"] for entry in gps_entries]

    # Check if we have any valid GPS entries
    if not gps_entries:
        print("No GPS data available in the wave data.")
        return
    elif not latitudes or not longitudes or not timestamps:
        print("Error: GPS data found, but some entries are missing latitude or longitude.")
        return

    # Convert timestamps to datetime objects
    times = pd.to_datetime(timestamps)
    start_time = times.min().strftime("%Y-%m-%d %H:%M:%S")
    end_time = times.max().strftime("%Y-%m-%d %H:%M:%S")

    # Set font to Arial
    plt.rcParams['font.family'] = 'Arial'

    # Create the figure and main plot
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_facecolor('#0077B6')  # Set plot area background to blue to match reference

    # Set grid spacing approximately to 10 meters (around 0.0001 degrees)
    ax.xaxis.set_major_locator(plt.MultipleLocator(0.0001))
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.0001))

    # Initial plot of GPS points with white dotted lines between them
    plot, = ax.plot(longitudes, latitudes, color='white', linestyle=':', marker='o',
                    markerfacecolor='#FFB000', markeredgewidth=0.5, markersize=5,
                    label="GPS Path", alpha=0.7)

    # Mark the start and end points with different colors
    ax.scatter(longitudes[0], latitudes[0], color="green", marker="o", s=100, label="Start")
    ax.scatter(longitudes[-1], latitudes[-1], color="red", marker="o", s=100, label="End")

    # Add title and time span subtitle without overlap
    plt.title(f"GPS Plot of Latitude and Longitude for SPOT ID: {spotter_id}", fontsize=14, color='black', pad=20)
    plt.figtext(0.5, 0.88, f"Time Span: {start_time} to {end_time}", fontsize=10, ha='center', color='black')

    # Add labels for axes with black text color
    ax.set_xlabel("Longitude", color='black')
    ax.set_ylabel("Latitude", color='black')

    # Set axis to have equal scaling and a square aspect ratio
    ax.set_aspect('equal', 'box')

    # Show legend
    ax.legend(loc="upper right", frameon=False, fontsize=8)

    # Show grid for easier geographic reference
    ax.grid(True, linestyle="--", color="white", alpha=0.4)

    # Adjust layout to make space for the sliders
    plt.subplots_adjust(bottom=0.25)

    # Create sliders for controlling the start and end points of the visible GPS data
    ax_slider_start = plt.axes([0.2, 0.1, 0.6, 0.03], facecolor="lightgrey")
    ax_slider_end = plt.axes([0.2, 0.05, 0.6, 0.03], facecolor="lightgrey")

    slider_start = Slider(ax_slider_start, "Start", 0, len(latitudes) - 1, valinit=0, valstep=1)
    slider_end = Slider(ax_slider_end, "End", 0, len(latitudes) - 1, valinit=len(latitudes) - 1, valstep=1)

    # Update function for sliders
    def update(val):
        start_index = int(slider_start.val)
        end_index = int(slider_end.val)

        # Ensure start_index is always less than end_index
        if start_index >= end_index:
            end_index = start_index + 1 if start_index + 1 < len(latitudes) else start_index

        # Update the plotted data
        plot.set_data(longitudes[start_index:end_index + 1], latitudes[start_index:end_index + 1])
        fig.canvas.draw_idle()

    # Link the sliders to the update function
    slider_start.on_changed(update)
    slider_end.on_changed(update)

    plt.show()

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import pandas as pd
import contextily as ctx
import contextily as ctx
print(ctx.providers)



def process_and_plot_data(spotter_id, start_date, end_date):
    """Fetch, process, and plot data for a given SPOT ID."""
    print(f"Processing data for SPOT ID: {spotter_id}")

    print("Data fetching, processing, and plotting complete.")
    print("Start date:", start_date.strftime("%m/%d/%Y"))
    print("End date:", end_date.strftime("%m/%d"))
    print("Number of days between the start and end date:", end_date - start_date)

    # Fetch wave data and smart mooring data as combined JSON objects
    api_data_waves = fetch_data_in_chunks(start_date, end_date,spotter_id, chunk_size_days=5, data_type="wave")
    api_data_smart_mooring = fetch_data_in_chunks(start_date, end_date, spotter_id, chunk_size_days=5, data_type="sensor")

    # Process the smart mooring data and wave data
    smart_mooring_data, unique_node_ids = process_smart_mooring_data(spotter_id, api_data_smart_mooring)
    process_wave_data(spotter_id, api_data_waves)

    # Plot data for all unique Node IDs found
    plot_data(smart_mooring_data, unique_node_ids, api_data_waves["data"], spotter_id)

    # Plot the GPS coordiantes from wave data
    plot_gps_coordinates(api_data_waves["data"],spotter_id)


    print("Data fetching, processing, and plotting complete.")
    print("Start date:", start_date.strftime("%m/%d/%Y"))
    print("End date:", end_date.strftime("%m/%d"))
    print("Number of days between the start and end date:", end_date - start_date)


def main():
    for config in SPOTTER_CONFIGS:
        process_and_plot_data(config['spotter_id'], config['start_date'], config['end_date'])

if __name__ == "__main__":
    main()
