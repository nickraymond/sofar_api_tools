
# Replace with your Mapbox Access Token
mapbox_access_token = 'pk.eyJ1Ijoibmlja3JheW1vbmQ5OSIsImEiOiJjbHlrdDYzMmExM3psMm1vam92c2c4NjB3In0.1KVs_Kh_128z249Iqz5g0Q'


import pandas as pd
import numpy as np
import plotly.graph_objects as go


def plot_gps_with_dynamic_currents(wave_data, spotter_id, mapbox_token, current_speed, current_direction):
    """Interactive map with GPS data and dynamically updated uniform ocean current vector overlay."""

    # Validate wave_data structure
    if "waves" not in wave_data:
        print("Error: 'waves' key not found in wave_data.")
        return

    # Extract GPS data
    gps_entries = [entry for entry in wave_data["waves"] if "latitude" in entry and "longitude" in entry]
    if not gps_entries:
        print("No GPS data available in the wave data.")
        return

    # Create DataFrame for GPS
    gps_df = pd.DataFrame(gps_entries)
    gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp']).dt.tz_convert('UTC')
    gps_df = gps_df.sort_values(by="timestamp")

    # Compute vector components for uniform currents
    u = current_speed * np.cos(np.radians(current_direction))
    v = current_speed * np.sin(np.radians(current_direction))

    # Function to generate dynamic vectors for the visible map region
    def generate_vectors(lat_min, lat_max, lon_min, lon_max, num_points=10):
        latitudes = np.linspace(lat_min, lat_max, num_points)
        longitudes = np.linspace(lon_min, lon_max, num_points)
        grid_lat, grid_lon = np.meshgrid(latitudes, longitudes)

        arrow_traces = []
        for lat, lon in zip(grid_lat.flatten(), grid_lon.flatten()):
            end_lat = lat + (v * 0.01)  # Scale for visualization
            end_lon = lon + (u * 0.01)
            # Draw arrow line
            arrow_traces.append(
                go.Scattermapbox(
                    lat=[lat, end_lat],
                    lon=[lon, end_lon],
                    mode="lines",
                    line=dict(color="blue", width=2),
                    showlegend=False  # Hide legend for individual arrows
                )
            )
            # Add arrowhead
            arrow_traces.append(
                go.Scattermapbox(
                    lat=[end_lat],
                    lon=[end_lon],
                    mode="markers",
                    marker=dict(size=6, color="blue", symbol="triangle-up"),
                    showlegend=False
                )
            )
        return arrow_traces

    # Define initial bounds for the map region
    lat_min = gps_df['latitude'].min() - 0.02
    lat_max = gps_df['latitude'].max() + 0.02
    lon_min = gps_df['longitude'].min() - 0.02
    lon_max = gps_df['longitude'].max() + 0.02

    # Generate initial vector field
    vector_traces = generate_vectors(lat_min, lat_max, lon_min, lon_max)

    # Create the figure
    fig = go.Figure()

    # Add GPS path trace
    fig.add_trace(
        go.Scattermapbox(
            lat=gps_df["latitude"],
            lon=gps_df["longitude"],
            mode="lines+markers",
            marker=dict(color="orange", size=8),
            line=dict(color="white", width=2),
            name="GPS Path",
        )
    )

    # Add the vector field
    fig.add_traces(vector_traces)

    # Configure the map
    fig.update_layout(
        mapbox=dict(
            style="mapbox://styles/mapbox/streets-v11",
            accesstoken=mapbox_token,
            center=dict(lat=gps_df['latitude'].mean(), lon=gps_df['longitude'].mean()),
            zoom=12
        ),
        legend=dict(
            orientation="h",
            y=-0.2,  # Move legend below the map
            x=0.5,
            xanchor="center"
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 50},
        title=f"GPS Path and Dynamic Ocean Currents for Spotter ID: {spotter_id}"
    )

    # Save the interactive map to an HTML file
    html_file = "gps_map_with_dynamic_currents.html"
    fig.write_html(html_file)
    print(f"Interactive map with dynamic currents saved to {html_file}. Open it in your browser to view.")


# Example wave_data
wave_data = {
    "waves": [
        {"latitude": 37.8199, "longitude": -122.4783, "timestamp": "2024-11-19T12:00:00Z"},
        {"latitude": 37.8210, "longitude": -122.4700, "timestamp": "2024-11-19T12:10:00Z"},
        {"latitude": 37.8221, "longitude": -122.4600, "timestamp": "2024-11-19T12:20:00Z"},
        {"latitude": 37.8250, "longitude": -122.4500, "timestamp": "2024-11-19T12:30:00Z"},
        {"latitude": 37.8265, "longitude": -122.4230, "timestamp": "2024-11-19T12:40:00Z"}
    ]
}

# Call the function with uniform current parameters
plot_gps_with_dynamic_currents(
    wave_data=wave_data,
    spotter_id="SPOT-001",
    mapbox_token=mapbox_access_token,
    current_speed=0.5,  # Uniform speed in m/s
    current_direction=45  # Uniform direction in degrees (e.g., 45° = NE)
)



