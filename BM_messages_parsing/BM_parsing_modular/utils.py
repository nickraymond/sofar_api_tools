import re
import os
import csv


def decode_hex_to_ascii(hex_string):
    try:
        return bytes.fromhex(hex_string).decode('utf-8', errors='ignore').strip()
    except ValueError:
        return "Invalid hex data"

def extract_force_values(message):
    min_force = max_force = mean_force = None
    min_match = re.search(r"min force:\s*(-?\d+\.\d+)", message)
    if min_match:
        min_force = float(min_match.group(1))
    return min_force, max_force, mean_force

import csv
import pandas as pd

# Centralized header structure
STANDARD_HEADERS = [
    "timestamp",
    "longitude",
    "latitude",
    "sensor_position",
    "bristlemouth_node_id",
    "data_type_name",
    "unit_type",
    "unit",
    "value",
    "processing_source",
]

def save_to_csv(data, csv_filename, header=True):
    """
    Save data to a CSV file with a standardized header structure.

    Args:
        data (dict or pd.DataFrame): Data entry to save.
        csv_filename (str): Path to the CSV file.
        header (bool): Whether to write the header row.

    Returns:
        None
    """
    if isinstance(data, dict):
        # Ensure all headers exist in the dictionary, set defaults for missing keys
        formatted_data = {key: data.get(key, None) for key in STANDARD_HEADERS}
        formatted_data["sensor_position"] = formatted_data.get("sensor_position", 0)
        formatted_data["bristlemouth_node_id"] = formatted_data.get("bristlemouth_node_id", "NULL")
        formatted_data["processing_source"] = formatted_data.get("processing_source", "bristlemouth_message")

        # Save dictionary to CSV
        with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=STANDARD_HEADERS, quoting=csv.QUOTE_MINIMAL, escapechar="\\")
            if header:
                writer.writeheader()
            writer.writerow(formatted_data)

    elif isinstance(data, pd.DataFrame):
        # Ensure all required columns exist in the DataFrame
        for column in STANDARD_HEADERS:
            if column not in data.columns:
                data[column] = None

        # Reorder columns and save to CSV
        data = data[STANDARD_HEADERS]
        data.to_csv(csv_filename, mode="a", index=False, header=header)

    else:
        raise TypeError(f"Unsupported data type for saving to CSV: {type(data)}")

    print(f"DEBUG: Data saved to {csv_filename} with headers: {STANDARD_HEADERS}")
