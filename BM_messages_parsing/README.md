# Wave and Sensor Data Processing

This project fetches wave and sensor data from the Sofar API for units equipped with load cells and current meters. It processes the data to generate plots of wave characteristics, currents, and forces.

## Description

The script performs the following tasks:

- Fetches wave data, including wave height, wind data, surface temperature, and barometer data.
- Fetches sensor data, particularly from smart mooring devices, decoding and processing force measurements.
- Processes and saves the fetched data into organized CSV files.
- Generates time series plots for significant wave height, current speed, sensor tilt, and force.
- Plots GPS coordinates from the wave data to visualize the unit's movement.

## Installation

1. **Clone the repository:**

   ```python
   git clone https://github.com/nickraymond/sofar_api_tools.git
   
2. **Install the required Python packages:**

Ensure you have Python 3.x installed. Then, install the necessary packages:

```python
pip install -r requirements.txt
```
Note: The requirements.txt file should list all dependencies, such as pytz, requests, pandas, matplotlib, and contextily. If this file doesn't exist, you can create it or install the packages individually.

3.**Set up configuration files:**

config.py: Create this file in the root directory and define your Sofar API token:

```python 
API_TOKEN = 'your_api_token_here'
```
spot_config.py: Create this file and define your Spotter configurations:

```python
SPOTTER_CONFIGS = [
    {
        'spotter_id': 'your_spotter_id',
        'start_date': datetime(2025, 1, 1),
        'end_date': datetime(2025, 1, 31)
    },
    # Add more configurations as needed
]
```

Replace 'your_spotter_id' with your actual Spotter ID and adjust the dates as necessary.

# Usage
Run the main script to fetch, process, and plot the data:

```python
python main_script.py
```

The script will:

Fetch data from the Sofar API within the specified date range.
Process and save the data into CSV files organized by sensor node IDs.
Generate and display plots for wave height, current speed, sensor tilt, force, and GPS coordinates.
Note: Ensure that the parsed_data directory exists or will be created in the root directory to store the CSV files.

# License
This project is licensed under the MIT License. See the LICENSE file for details.
