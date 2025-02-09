
from utils import save_to_csv, STANDARD_HEADERS
import os

def process_wave_data(wave_data_frames, base_directory):
    """
    Process wave data stored as DataFrames, including wave, wind, surface temperature, and barometer data.

    Args:
        wave_data_frames (dict): Dictionary of DataFrames (e.g., {"waves": df, "wind": df, ...}).
        base_directory (str): Directory to save processed wave data.

    Returns:
        None
    """
    wave_data_directory = os.path.join(base_directory, "spotter_data")
    os.makedirs(wave_data_directory, exist_ok=True)

    # Define CSV file names for each DataFrame
    csv_files = {
        "waves": "waves.csv",
        "wind": "wind.csv",
        "surfaceTemp": "surface_temp.csv",
        "barometerData": "barometer_data.csv",
    }

    for data_type, df in wave_data_frames.items():
        if not df.empty:
            # Add fields to align with the standard header structure
            df["sensor_position"] = 0
            df["bristlemouth_node_id"] = "NULL"
            df["processing_source"] = "bristlemouth_message"

            # Ensure all standard headers are present
            for col in STANDARD_HEADERS:
                if col not in df.columns:
                    df[col] = None

            # Reorder columns to match the standard header structure
            df = df[STANDARD_HEADERS]

            # Save each row using `save_to_csv`
            csv_path = os.path.join(wave_data_directory, csv_files[data_type])
            for index, row in df.iterrows():
                save_to_csv(row.to_dict(), csv_path, header=not os.path.exists(csv_path))

            print(f"DEBUG: Saved {data_type} data to {csv_path}")

    print("Wave data processing complete.")
