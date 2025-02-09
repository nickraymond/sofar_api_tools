# Sofar API Data Parsing and Visualization Tool

## Overview

This Python script is designed to make multiple API calls to the Sofar Spotter API to fetch wave, sensor, and GPS data from Spotter units. It processes the data, saves it in a structured format, and visualizes it using various plots, including time series and GPS tracks.

The script can be configured for different Spotter deployments by adjusting parameters for `spotterId` and date ranges.

---

## Requirements

### Libraries Used

- **pytz**: Handles timezone conversions for accurate date and time management.
- **os**: Used to create directories for saving data.
- **csv**: Enables data to be written to CSV files.
- **re**: For parsing specific patterns in sensor data.
- **requests**: Facilitates API calls to fetch data from the Sofar Spotter API.
- **pandas**: For handling and processing tabular data efficiently.
- **matplotlib**: For plotting time series data, including wave heights, currents, forces, and GPS tracks.
- **collections (defaultdict)**: Simplifies the storage of grouped data.
- **datetime**: Handles date and time manipulations.
- **matplotlib.widgets (Slider)**: Provides interactive sliders for user-friendly navigation of GPS plots.
- **contextily**: Used for overlaying maps (if required).

---

## How It Works

1. **Fetch Data from API**:
   - The script interacts with the Sofar Spotter API using the `spotterId` and date range specified by the user.
   - Data is fetched in chunks to handle large datasets efficiently.
   - Both wave and sensor data are fetched using the API.

2. **Process Data**:
   - The data is parsed and saved in structured CSV files in directories named after the `spotterId`.
   - Each unique node ID in the sensor data is saved separately for better organization.

3. **Generate Plots**:
   - Time series plots are created for:
     - Significant wave height.
     - Current speed (with standard deviation).
     - Sensor tilt (in radians and degrees).
     - Force (in Newtons and pounds-force).
   - GPS tracks are plotted with start and end points highlighted.

4. **Save and Manipulate Data**:
   - Data is saved in directories named after the `spotterId`.
   - CSV files are created for wave data (e.g., wave heights, wind, surface temperature, and barometer) and sensor data (grouped by node ID).

---

## User Inputs

### Customizable Parameters

1. **Spotter ID**:
   - Change the `spotterId` to specify the Spotter unit for which you want to fetch data.
   - Example: 
     ```python
     spotterId = "SPOT-31088C"
     ```

2. **Date Range**:
   - Update `start_date` and `end_date` to specify the time period for data retrieval.
   - Example:
     ```python
     start_date = datetime.strptime("2024-10-31T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
     end_date = datetime.utcnow()
     ```

3. **Chunk Size**:
   - Adjust the chunk size for API calls in `fetch_data_in_chunks`.
   - Example:
     ```python
     chunk_size_days = 5
     ```

---

## How to Run

1. **Install Dependencies**:
   Ensure all required libraries are installed. You can use the following command:
   ```bash
   pip install pytz requests pandas matplotlib contextily
   ```

2. **Configure Parameters**:
   Open the script and update the following variables as needed:
   - `spotterId`: The ID of the Spotter unit.
   - `start_date` and `end_date`: The time range for fetching data.

3. **Run the Script**:
   Execute the script using Python:
   ```bash
   python sofar_api_parsin_v4.py
   ```

4. **View Outputs**:
   - Time series plots for wave, current, and force data will be displayed.
   - GPS tracks will be plotted interactively.
   - CSV files will be saved in a directory named after the `spotterId`.

---

## Outputs

1. **Plots**:
   - Significant wave height (with secondary y-axis in feet).
   - Current speed (with standard deviation shading and secondary y-axis in knots).
   - Sensor tilt (with secondary y-axis in degrees).
   - Force (with secondary y-axis in pounds-force).
   - GPS tracks with start and end markers.

2. **Saved Data**:
   - CSV files for wave and sensor data in directories named after the `spotterId`.

---

## Example Configuration

### Spotter for Half Moon Bay Deployment
```python
spotterId = "SPOT-31088C"
start_date = datetime.strptime("2024-10-31T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
end_date = datetime.utcnow()
```

### Example Run Command
```bash
python sofar_api_parsin_v4.py
```

---

## Notes

1. Ensure the `token` variable is set correctly to authenticate with the API.
2. Make sure the date range is within the deployment period for the selected `spotterId`.
3. Use interactive sliders to explore GPS tracks effectively.
4. All data is saved locally in a structured directory for easy access and further analysis.

For additional support or questions, please refer to the Sofar API documentation or contact the author.
