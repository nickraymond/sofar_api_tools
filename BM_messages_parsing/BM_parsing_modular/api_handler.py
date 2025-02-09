import requests
from datetime import timedelta
import pandas as pd


def api_login(api_url):
    """Fetch data from the Sofar API."""
    response = requests.get(api_url)
    if response.status_code == 200:
        print(f"Successfully fetched data from API: {api_url}")
        return response.json()
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        raise Exception("API request failed.")

def fetch_wave_data(start_datetime, end_datetime, chunk_size_days=5, token="", spotter_id=""):
    """Fetch wave data from the API in chunks and return DataFrames."""
    wave_data = []
    wind_data = []
    surface_temp_data = []
    barometer_data = []

    current_start = start_datetime

    while current_start < end_datetime:
        current_end = min(current_start + timedelta(days=chunk_size_days), end_datetime)
        chunk_start = current_start.strftime("%Y-%m-%dT%H:%M:%SZ")
        chunk_end = current_end.strftime("%Y-%m-%dT%H:%M:%SZ")

        api_url = (
            f"https://api.sofarocean.com/api/wave-data?spotterId={spotter_id}&startDate={chunk_start}"
            f"&endDate={chunk_end}&token={token}&includeWindData=true&includeSurfaceTempData=true"
            f"&includeBarometerData=true&limit=500&processingSources=all"
        )

        print(f"Fetching wave data for {chunk_start} to {chunk_end}...")
        chunk_data = api_login(api_url)

        if "data" in chunk_data:
            wave_data.extend(chunk_data["data"].get("waves", []))
            wind_data.extend(chunk_data["data"].get("wind", []))
            surface_temp_data.extend(chunk_data["data"].get("surfaceTemp", []))
            barometer_data.extend(chunk_data["data"].get("barometerData", []))

        current_start = current_end

    # Convert lists to DataFrames
    wave_df = pd.DataFrame(wave_data)
    wind_df = pd.DataFrame(wind_data)
    surface_temp_df = pd.DataFrame(surface_temp_data)
    barometer_df = pd.DataFrame(barometer_data)

    return {"waves": wave_df, "wind": wind_df, "surfaceTemp": surface_temp_df, "barometerData": barometer_df}


def fetch_sensor_data(start_datetime, end_datetime, chunk_size_days=5, token="", spotter_id=""):
    """
    Fetch sensor data from the API in chunks and organize it into DataFrames.

    Args:
        start_datetime (datetime): Start date for the API call.
        end_datetime (datetime): End date for the API call.
        chunk_size_days (int): Number of days per API call.
        token (str): API authentication token.
        spotter_id (str): Spotter ID for the API call.

    Returns:
        dict: Dictionary of DataFrames keyed by `data_type_name`.
    """
    # Initialize a dictionary to hold data for each `data_type_name`
    data_by_type = {}

    current_start = start_datetime
    while current_start < end_datetime:
        current_end = min(current_start + timedelta(days=chunk_size_days), end_datetime)
        chunk_start = current_start.strftime("%Y-%m-%dT%H:%M:%SZ")
        chunk_end = current_end.strftime("%Y-%m-%dT%H:%M:%SZ")

        api_url = (
            f"https://api.sofarocean.com/api/sensor-data?spotterId={spotter_id}"
            f"&startDate={chunk_start}&endDate={chunk_end}&token={token}&limit=500"
        )

        print(f"Fetching sensor data for {chunk_start} to {chunk_end}...")
        response = requests.get(api_url)

        if response.status_code == 200:
            print("Successfully fetched sensor data.")
            chunk_data = response.json()

            if "data" in chunk_data:
                # Process each entry in the "data" list
                for entry in chunk_data["data"]:
                    data_type = entry.get("data_type_name", "unknown")

                    # Convert each entry into a DataFrame row
                    entry_df = pd.DataFrame([entry])

                    # Append to the appropriate DataFrame in `data_by_type`
                    if data_type not in data_by_type:
                        data_by_type[data_type] = entry_df
                    else:
                        data_by_type[data_type] = pd.concat([data_by_type[data_type], entry_df], ignore_index=True)
        else:
            print(f"Failed to fetch sensor data: {response.status_code}")
            response.raise_for_status()

        # Advance to the next chunk
        current_start = current_end

    # Ensure all DataFrames have consistent structure
    for key, df in data_by_type.items():
        data_by_type[key] = df.reset_index(drop=True)

    return data_by_type







# TODO, make this output dataframes intead of dict
# def fetch_data_in_chunks(start_datetime, end_datetime, data_type, spotter_id, token):
#     """
#     Fetch data from the API in chunks of days and return combined data.
#
#     Args:
#         start_datetime (datetime): Start date for the API call.
#         end_datetime (datetime): End date for the API call.
#         data_type (str): Type of data to fetch ("wave" or "sensor").
#         spotter_id (str): Spotter ID for the API call.
#         token (str): API authentication token.
#
#     Returns:
#         dict: Combined data fetched from the API.
#     """
#     chunk_size_days = 5  # You can adjust this as needed
#     combined_data = {"data": []}  # Initialize combined data structure
#     current_start = start_datetime
#
#     while current_start < end_datetime:
#         current_end = min(current_start + timedelta(days=chunk_size_days), end_datetime)
#
#         # Construct the appropriate API URL
#         if data_type == "wave":
#             api_url = (
#                 f"https://api.sofarocean.com/api/wave-data?spotterId={spotter_id}"
#                 f"&startDate={current_start.isoformat()}Z"
#                 f"&endDate={current_end.isoformat()}Z"
#                 f"&token={token}&includeWindData=true&includeSurfaceTempData=true"
#                 f"&includeBarometerData=true&limit=500"
#             )
#         elif data_type == "sensor":
#             api_url = (
#                 f"https://api.sofarocean.com/api/sensor-data?spotterId={spotter_id}"
#                 f"&startDate={current_start.isoformat()}Z"
#                 f"&endDate={current_end.isoformat()}Z"
#                 f"&token={token}&limit=500"
#             )
#         else:
#             raise ValueError(f"Invalid data type: {data_type}")
#
#         # Fetch data from the API
#         print(f"Fetching {data_type} data from {current_start} to {current_end}...")
#         response = requests.get(api_url)
#
#         if response.status_code == 200:
#             print(f"Successfully fetched {data_type} data.")
#             data = response.json()
#             if "data" in data:
#                 combined_data["data"].extend(data["data"])
#         else:
#             print(f"Failed to fetch {data_type} data: {response.status_code}")
#             response.raise_for_status()
#
#         # Move to the next chunk
#         current_start = current_end
#
#     return combined_data
