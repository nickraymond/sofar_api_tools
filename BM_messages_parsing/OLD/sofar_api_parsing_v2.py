# filename: sofar_api_parsin_v2.py
# description: read API for wave and sensor data for unit with load cell and current meter, then plot waves, currents, and force
# TODO
# update logic to know difference between data types, and add sensor position, units, and data_type to  JSON parsing for managed sensors
import os
import csv
import re
import requests
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict


# Conversion factors
meter_to_feet = 3.28084
m_per_s_to_knots = 1.94384
newton_to_lbf = 0.224809

# Define Spotter ID, token, and date range
spotterId = "SPOT-31088C"
token = "90bda8b0a39b9570b548ab6f7a1aea"
start_date = "2024-10-31T00:00:00Z"
end_date = "2024-11-05T00:00:00Z"

# Set up API URLs
api_url_smart_mooring = f"https://api.sofarocean.com/api/sensor-data?spotterId={spotterId}&startDate={start_date}&endDate={end_date}&token={token}&limit=500"
api_url_spotter_waves = (
    f"https://api.sofarocean.com/api/wave-data?spotterId={spotterId}&startDate={start_date}"
    f"&endDate={end_date}&token={token}&includeWindData=true&includeSurfaceTempData=true&includeBarometerData=true&limit=500"
)

# Base directory for saving CSVs
base_directory = 'parsed_data'
if not os.path.exists(base_directory):
    os.makedirs(base_directory)

def api_login(api_url):
    """Fetch data from the Sofar API."""
    response = requests.get(api_url)
    if response.status_code == 200:
        print("Successfully fetched data from Sofar API.")
        return response.json()
    else:
        print(f"Failed to fetch data from Sofar API. Status code: {response.status_code}")
        raise Exception("API request failed.")

# def decode_hex_to_ascii(hex_string):
#     """Decode a hex string to ASCII format."""
#     try:
#         byte_value = bytes.fromhex(hex_string)
#         return byte_value.decode('utf-8', errors='replace')
#     except ValueError:
#         return "Invalid hex data"

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

def process_smart_mooring_data(json_data):
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
        node_directory = os.path.join(base_directory, node_id)
        if not os.path.exists(node_directory):
            os.makedirs(node_directory)

        # Save the parsed data to CSV
        csv_filename = os.path.join(node_directory, f"{node_id}_smart_mooring.csv")
        save_to_csv(parsed_entry, csv_filename, header=True if not os.path.exists(csv_filename) else False)

    # Print the unique node IDs found
    print("Unique Node IDs found:", unique_node_ids)
    return grouped_data, unique_node_ids

def process_wave_data(api_data_wave):
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
    axs[3].set_xlabel("Time")
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()

def plot_gps_coordinates(wave_data, spotter_id):
    """Plot GPS coordinates from Spotter wave data with specific formatting."""

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

    # Create the figure and plot
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_facecolor('#0077B6')  # Set plot area background to blue to match reference

    # Plot GPS points with white dotted lines between them
    ax.plot(longitudes, latitudes, color='white', linestyle=':', marker='o', markerfacecolor='#FFB000',
            markeredgewidth=0.5, markersize=5, label="GPS Path", alpha=0.7)

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

    # Set background color to vibrant blue
    plt.gca().set_facecolor("#007FFF")

    # Show legend
    ax.legend(loc="upper right", frameon=False, fontsize=8) # facecolor='#0077B6')

    # Show grid for easier geographic reference
    plt.grid(True, linestyle="--", color="white", alpha=0.4)
    plt.show()


def main():
    # Fetch data from the API
    api_data_smart_mooring = api_login(api_url_smart_mooring)
    api_data_waves = api_login(api_url_spotter_waves)

    # Process the smart mooring data and wave data
    smart_mooring_data, unique_node_ids = process_smart_mooring_data(api_data_smart_mooring)
    process_wave_data(api_data_waves)

    # Plot data for all unique Node IDs found
    #plot_data(smart_mooring_data, unique_node_ids, api_data_waves["data"], spotterId)

    # Plot the GPS coordiantes from wave data
    plot_gps_coordinates(api_data_waves["data"],spotterId)


if __name__ == "__main__":
    main()
