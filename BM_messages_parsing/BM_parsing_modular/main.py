
import os
from datetime import datetime, timedelta
from config import SPOTTER_ID, DEPLOYMENT_DATE_STR, DAYS_AFTER, API_TOKEN
from sensor_data_processing import process_smart_mooring_data
from wave_data_processing import process_wave_data
from plotting import plot_data
from api_handler import fetch_sensor_data, fetch_wave_data

# Base directory for saving data (named after Spotter ID)
BASE_DIRECTORY = os.path.join(os.getcwd(), SPOTTER_ID)
os.makedirs(BASE_DIRECTORY, exist_ok=True)

# Deployment and data fetching parameters
START_DATE = datetime.strptime(DEPLOYMENT_DATE_STR, "%Y-%m-%dT%H:%M:%SZ")
END_DATE = START_DATE + timedelta(days=DAYS_AFTER)

# def main():
#
#     # Fetch wave and sensor data from the API
#     wave_data = fetch_data_in_chunks(START_DATE, END_DATE, data_type="wave", spotter_id=SPOTTER_ID, token=API_TOKEN)
#     sensor_data = fetch_data_in_chunks(START_DATE, END_DATE, data_type="sensor", spotter_id=SPOTTER_ID, token=API_TOKEN)
#
#     # Process and save data
#     #grouped_data, unique_node_ids = process_smart_mooring_data(sensor_data, BASE_DIRECTORY)
#     process_wave_data(wave_data, BASE_DIRECTORY)
#
#     # Plot the data
#     #plot_data(grouped_data, unique_node_ids, wave_data["data"], SPOTTER_ID)
def main():
    # Fetch wave and sensor data from the API
    wave_data = fetch_wave_data(START_DATE, END_DATE, token=API_TOKEN, spotter_id=SPOTTER_ID)
    #sensor_data = fetch_sensor_data(START_DATE, END_DATE, data_type="sensor", spotter_id=SPOTTER_ID, token=API_TOKEN)


    #sensor_data = fetch_data_in_chunks(START_DATE, END_DATE, data_type="sensor", spotter_id=SPOTTER_ID, token=API_TOKEN)

    # Process and save data
    process_wave_data(wave_data, BASE_DIRECTORY)
    #grouped_data, unique_node_ids = process_smart_mooring_data(sensor_data, BASE_DIRECTORY)

    # Plot the data
   # plot_data(grouped_data, unique_node_ids, wave_data, SPOTTER_ID)

if __name__ == "__main__":
    main()
