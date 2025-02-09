import os
import csv
import re
from collections import defaultdict
from utils import decode_hex_to_ascii
import pandas as pd
from utils import save_to_csv


# Predefined managed data types
managed_data_types = {
    "bm_rbr_coda_pressure_mean_21bits": "pressure_mean",
    "bm_rbr_coda_pressure_stdev_15bits": "pressure_stdev",
    "aanderaa_abs_speed_mean_15bits": "speed_mean",
    "aanderaa_abs_speed_std_15bits": "speed_stdev",
    "aanderaa_abs_tilt_mean_8bits": "tilt_mean",
    "aanderaa_direction_circ_mean_13bits": "direction_mean",
    "aanderaa_direction_circ_std_13bits": "direction_stdev",
    "aanderaa_reading_count_10bits": "reading_count",
    "aanderaa_std_tilt_mean_8bits": "tilt_stdev",
    "aanderaa_temperature_mean_13bits": "temperature_mean",
}

def save_to_csv(data, csv_filename, header=True):
    """
    Save individual entries to CSV with escape character handling.

    Args:
        data (dict): Data entry to save.
        csv_filename (str): Path to the CSV file.
        header (bool): Whether to write the header row.

    Returns:
        None
    """
    fieldnames = data.keys()
    with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL, escapechar="\\")
        if header:
            writer.writeheader()
        writer.writerow(data)

def extract_force_values(message):
    """
    Extract min, max, and mean force values from a message string.
    Handles cases with inconsistent separators or non-printable characters.
    """
    #print(f"DEBUG: Raw message to extract forces: {repr(message)}")
    cleaned_message = ''.join(char for char in message if char.isprintable())
    #print(f"DEBUG: Cleaned message: {cleaned_message}")

    mean_match = re.search(r"mean force:\s*([\d\.\-]+)", cleaned_message)
    max_match = re.search(r"max force:\s*([\d\.\-]+)", cleaned_message)
    min_match = re.search(r"min force:\s*([\d\.\-]+)", cleaned_message)

    min_force = float(min_match.group(1)) if min_match else None
    max_force = float(max_match.group(1)) if max_match else None
    mean_force = float(mean_match.group(1)) if mean_match else None

    #print(f"DEBUG: Parsed forces - Min: {min_force}, Max: {max_force}, Mean: {mean_force}")
    return min_force, max_force, mean_force


def parse_managed_data(entry, data_type):
    """
    Parse managed data types.
    """
    return {
        "timestamp": entry.get("timestamp"),
        "latitude": entry.get("latitude"),
        "longitude": entry.get("longitude"),
        "sensorPosition": entry.get("sensorPosition", "Unknown"),
        "data_type_name": data_type,
        "parsed_type": managed_data_types[data_type],
        "value": float(entry.get("value", 0)),
        "units": entry.get("units", ""),
        "unit_type": entry.get("unit_type", ""),
    }


def parse_unmanaged_data(entry):
    """
    Parse unmanaged data types based on keywords in the 'value' field.
    """
    value = entry.get("value", "")
    decoded_value = decode_hex_to_ascii(value) if entry.get("unit_type") == "binary" else value
    #print(f"DEBUG: Decoded unmanaged value: {decoded_value}")

    if "force" in decoded_value:
        min_force, max_force, mean_force = extract_force_values(decoded_value)
        return {
            "timestamp": entry.get("timestamp"),
            "latitude": entry.get("latitude"),
            "longitude": entry.get("longitude"),
            "sensorPosition": entry.get("sensorPosition", "Unknown"),
            "data_type_name": entry.get("data_type_name"),
            "decoded_value": decoded_value,
            "min_force": min_force,
            "max_force": max_force,
            "mean_force": mean_force,
            "units": entry.get("units", ""),
            "unit_type": entry.get("unit_type", ""),
        }

    # Add additional parsing logic for other unmanaged cases
    print(f"Warning: Unmanaged data type with unrecognized value: {decoded_value}")
    return None


def check_unmanaged_pattern(data_type_name, value):
    """
    Check the data_type_name and value for known unmanaged sensor patterns.

    Args:
        data_type_name (str): The data type name from the API.
        value (str): The value field from the API.

    Returns:
        str: The matched pattern type (e.g., "load_cell") or None if no match.
    """
    if data_type_name == "binary_hex_encoded" and "force" in decode_hex_to_ascii(value):
        return "load_cell"
    # Add more patterns here as needed
    return None

def process_smart_mooring_data(sensor_data, base_directory):
    """
    Process sensor data JSON, distinguishing between managed and unmanaged data types,
    delegating processing to modular helper functions.

    Args:
        sensor_data (dict): Sensor data fetched from the API.
        base_directory (str): Directory to save processed data.

    Returns:
        grouped_data (dict): Parsed data grouped by Node ID or sensor position.
        unique_node_ids (set): Unique Node IDs found in the data.
    """
    import pandas as pd
    from collections import defaultdict

    grouped_data = defaultdict(pd.DataFrame)
    unique_node_ids = set()

    # Define managed data types
    managed_data_types = {
        "bm_rbr_coda_pressure_mean_21bits",
        "bm_rbr_coda_pressure_stdev_15bits",
        "aanderaa_abs_speed_mean_15bits",
        "aanderaa_abs_speed_std_15bits",
        "aanderaa_abs_tilt_mean_8bits",
        "aanderaa_direction_circ_mean_13bits",
        "aanderaa_direction_circ_std_13bits",
        "aanderaa_reading_count_10bits",
        "aanderaa_std_tilt_mean_8bits",
        "aanderaa_temperature_mean_13bits",
    }

    for entry in sensor_data.get("data", []):
        data_type_name = entry.get("data_type_name", "unknown")

        if data_type_name in managed_data_types:
            process_managed_data(entry, grouped_data, base_directory)
        elif data_type_name == "binary_hex_encoded":
            process_unmanaged_data(entry, grouped_data, unique_node_ids, base_directory)
        else:
            print(f"DEBUG: Unrecognized data_type_name '{data_type_name}'. Skipping entry.")

    return grouped_data, unique_node_ids


def process_managed_data(entry, grouped_data, base_directory):
    """
    Process managed sensor data based on pre-defined data_type_name.

    Args:
        entry (dict): Single entry from sensor data.
        grouped_data (dict): Dictionary of grouped dataframes for saving.
        base_directory (str): Directory to save processed data.

    Returns:
        None
    """
    import pandas as pd
    import os

    timestamp = entry.get("timestamp")
    latitude = entry.get("latitude")
    longitude = entry.get("longitude")
    sensor_position = entry.get("sensorPosition", "unknown")
    data_type_name = entry.get("data_type_name", "unknown")
    units = entry.get("units", "")
    unit_type = entry.get("unit_type", "unknown")
    value = entry.get("value", None)

    parsed_entry = {
        "timestamp": timestamp,
        "latitude": latitude,
        "longitude": longitude,
        "sensorPosition": sensor_position,
        "data_type_name": data_type_name,
        "unit_type": unit_type,
        "value": float(value) if value is not None else None,
        "units": units,
    }

    save_group = f"position_{sensor_position}"
    if save_group not in grouped_data:
        grouped_data[save_group] = pd.DataFrame(columns=parsed_entry.keys())
    grouped_data[save_group] = pd.concat([grouped_data[save_group], pd.DataFrame([parsed_entry])], ignore_index=True)

    save_directory = os.path.join(base_directory, "smart_mooring_data", save_group)
    os.makedirs(save_directory, exist_ok=True)
    csv_filename = os.path.join(save_directory, f"{save_group}.csv")
    grouped_data[save_group].to_csv(csv_filename, index=False, escapechar="\\")


def process_unmanaged_data(entry, grouped_data, unique_node_ids, base_directory):
    """
    Process unmanaged sensor data using pattern recognition for specific types.

    Args:
        entry (dict): Single entry from sensor data.
        grouped_data (dict): Dictionary of grouped dataframes for saving.
        unique_node_ids (set): Set of unique node IDs found.
        base_directory (str): Directory to save processed data.

    Returns:
        None
    """
    import pandas as pd
    import os
    import re

    timestamp = entry.get("timestamp")
    latitude = entry.get("latitude")
    longitude = entry.get("longitude")
    node_id = entry.get("bristlemouth_node_id", "unknown_node")
    data_type_name = entry.get("data_type_name", "unknown")
    value = entry.get("value", "")
    unit_type = entry.get("unit_type", "unknown")

    if unit_type == "binary" and "load cell" in data_type_name.lower():
        decoded_value = decode_hex_to_ascii(value)

        # Trim non-standard ASCII characters from the decoded value
        valid_value_match = re.match(r'^[\x20-\x7E]+', decoded_value)
        if valid_value_match:
            decoded_value = valid_value_match.group(0)  # Keep only valid portion
        else:
            print(f"DEBUG: Skipping invalid decoded value for Node ID {node_id}: {decoded_value}")
            return

        # Parse forces from the cleaned decoded value
        min_force, max_force, mean_force = extract_force_values(decoded_value)

        parsed_entry = {
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "node_id": node_id,
            "data_type_name": data_type_name,
            "unit_type": unit_type,
            "decoded_value": decoded_value,
            "min_force": min_force,
            "max_force": max_force,
            "mean_force": mean_force,
            "units": "newtons",
        }

        if node_id not in grouped_data:
            grouped_data[node_id] = pd.DataFrame(columns=parsed_entry.keys())
        grouped_data[node_id] = pd.concat([grouped_data[node_id], pd.DataFrame([parsed_entry])], ignore_index=True)

        save_directory = os.path.join(base_directory, "smart_mooring_data", node_id)
        os.makedirs(save_directory, exist_ok=True)
        csv_filename = os.path.join(save_directory, f"{node_id}.csv")
        grouped_data[node_id].to_csv(csv_filename, index=False, escapechar="\\")

        unique_node_ids.add(node_id)
        print(f"DEBUG: Processed unmanaged data for Node ID: {node_id}")
